"""T117: plain dispatch got faster without changing what it does.

The register path is compared with a verbatim copy of the code it replaced (values, the base
registers, what an io_tap is told, and the error type and message of every unsupported name);
the write listeners are still the ones present when a write starts; call addresses parse as
before; and E034-03's straight drive still gives the events, result and full memory recorded
before the change (experiments/E036-match-port/out/T117/taps-before-v1.json)."""
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "runtime")]
from original_match.machine import MEM_SIZE  # noqa: E402
from original_match.port.engine import PortMachine  # noqa: E402
from original_match.port.mem import PortError  # noqa: E402
from original_match.port import guest  # noqa: E402
from original_match.port.runtime import Regs  # noqa: E402

RECEIPT = ROOT / "experiments/E036-match-port/out/T117/taps-before-v1.json"


class Before:
    """port/engine.py's register path before T117, verbatim but for `self`."""
    def __init__(self, registers):
        self._registers, self.io_tap = registers, None

    @staticmethod
    def _alias(name):
        name = name.lower()
        if name in ('eax','ebx','ecx','edx','esi','edi','ebp','esp','eip','eflags'):
            return name, 0, 32
        if name in ('cs','ds','es','ss','fs','gs'):
            return name, 0, 16
        if name in ('ax','bx','cx','dx','si','di','bp','sp','ip','flags'):
            return 'e'+name, 0, 16
        if len(name)==2 and name[0] in 'abcd' and name[1] in 'lh':
            return 'e'+name[0]+'x', 8 if name[1]=='h' else 0, 8
        raise PortError(f'unsupported plain register {name!r}')

    def reg(self, name):
        base, shift, bits = self._alias(name)
        value = self._registers[base] >> shift & ((1 << bits)-1)
        if self.io_tap is not None:self.io_tap('g', name.lower(), value)
        return value

    def set_reg(self, name, value):
        base, shift, bits = self._alias(name)
        if name.lower() in ('ip','flags'):self._registers[base] = 0
        mask = ((1 << bits)-1) << shift
        self._registers[base] = ((self._registers[base] & ~mask) | ((value << shift) & mask)) & 0xFFFFFFFF
        if base=='eflags':self._registers[base] |= 2
        if self.io_tap is not None:self.io_tap('s', name.lower(), value)


def Before_bounds(linear, n):
    """PortMachine._bounds before T117, verbatim."""
    if (not isinstance(linear, int) or not isinstance(n, int)
            or linear < 0 or n < 0 or linear+n > MEM_SIZE):
        raise PortError(f'plain-memory read/write outside mapped range: {linear}+{n}')


NAMES = ['eax','ebx','ecx','edx','esi','edi','ebp','esp','eip','eflags','cs','ds','es','ss','fs','gs',
         'ax','bx','cx','dx','si','di','bp','sp','ip','flags','al','ah','bl','bh','cl','ch','dl','dh']
NAMES += [n.upper() for n in NAMES] + ['Ax', 'eFlags', 'Ip', 'aH']
BAD = ['xx', 'r8', 'e', '', 'al ', 'ahh', 'el', 'AXX', 5, None, 1.5, ('ax',), ['ax'], b'ax']


def outcome(call):
    try:
        return ('value', call())
    except Exception as error:  # the type and message are what must not change
        return ('error', type(error).__name__, str(error))


class Registers(unittest.TestCase):
    def pair(self):
        new = PortMachine(bytes(MEM_SIZE), 0x1000)
        old = Before(dict(new._registers))
        new_taps, old_taps = [], []
        new.io_tap = lambda *a: new_taps.append(a)
        old.io_tap = lambda *a: old_taps.append(a)
        return new, old, new_taps, old_taps

    def test_every_name_reads_and_writes_as_before_with_the_same_taps(self):
        new, old, new_taps, old_taps = self.pair()
        rng = random.Random(117)
        for _ in range(4000):
            name = rng.choice(NAMES)
            if rng.random() < 0.5:
                value = rng.choice([0, 1, 0xFF, 0x100, 0xFFFF, 0x10000, 0xFFFFFFFF, 0x1FFFFFFFF, -1,
                                    rng.getrandbits(40)])
                self.assertEqual(outcome(lambda: new.set_reg(name, value)), outcome(lambda: old.set_reg(name, value)))
            else:
                self.assertEqual(outcome(lambda: new.reg(name)), outcome(lambda: old.reg(name)), name)
            self.assertEqual(new._registers, old._registers)
        self.assertEqual(new_taps, old_taps)
        self.assertGreater(len(new_taps), 3000)

    def test_with_no_tap_the_machine_and_the_port_view_read_and_write_as_before(self):
        rng = random.Random(1170)
        for via in ("machine", "view"):
            new = PortMachine(bytes(MEM_SIZE), 0x1000)
            old = Before(dict(new._registers))
            target = new if via == "machine" else new.port_memory()
            for _ in range(4000):
                name = rng.choice(NAMES + BAD)
                if rng.random() < 0.5:
                    value = rng.choice([0, 1, True, 0xFF, 0xFFFF, 0x10000, 0xFFFFFFFF, -1, rng.getrandbits(40)])
                    self.assertEqual(outcome(lambda: target.set_reg(name, value)), outcome(lambda: old.set_reg(name, value)),
                                     (via, name))
                else:
                    self.assertEqual(outcome(lambda: target.reg(name)), outcome(lambda: old.reg(name)), (via, name))
                self.assertEqual(new._registers, old._registers, via)
            if via == "view":
                for off in (0, 1, 0xFFFF, 0x10000, -1):
                    self.assertEqual(target.ss_lin(off), old.reg("ss") * 16 + (off & 0xFFFF))

    def test_bounds_and_word_reads_as_before(self):
        m = PortMachine(bytes(range(256)) * (MEM_SIZE // 256), 0x1000)
        view = m.port_memory()
        for linear, n in ((0, 1), (MEM_SIZE - 2, 2), (MEM_SIZE - 1, 2), (-1, 1), (True, 1), (0, True), (1.0, 1), ("1", 1),
                          (MEM_SIZE, 0), (0, -1)):
            self.assertEqual(outcome(lambda: PortMachine._bounds(linear, n)), outcome(lambda: Before_bounds(linear, n)),
                             (linear, n))
        for linear in (0, 7, 0x1234, MEM_SIZE - 2, MEM_SIZE - 1, -1, True):
            self.assertEqual(outcome(lambda: view.u16(linear)),
                             outcome(lambda: (Before_bounds(linear, 2), int.from_bytes(bytes(m._memory[linear:linear + 2]), "little"))[1]),
                             linear)
            self.assertEqual(outcome(lambda: view.u8(linear)),
                             outcome(lambda: (Before_bounds(linear, 1), bytes(m._memory[linear:linear + 1])[0])[1]), linear)

    def test_unsupported_names_fail_with_the_same_error(self):
        new, old, new_taps, old_taps = self.pair()
        for name in BAD:
            with self.subTest(name=name):
                self.assertEqual(outcome(lambda: new.reg(name)), outcome(lambda: old.reg(name)))
                self.assertEqual(outcome(lambda: new.set_reg(name, 1)), outcome(lambda: old.set_reg(name, 1)))
                self.assertEqual(outcome(lambda: PortMachine._alias(name)), outcome(lambda: Before._alias(name)))
                self.assertEqual(outcome(lambda: new.reg(name))[0], 'error')
        self.assertEqual((new_taps, new._registers), (old_taps, old._registers))

    def test_alias_answers_as_before(self):
        for name in NAMES:
            self.assertEqual(PortMachine._alias(name), Before._alias(name), name)

    def test_regs_names_are_unchanged(self):
        self.assertEqual(Regs._NAME_SET, frozenset(Regs._NAMES))
        self.assertEqual(Regs._NAMES, ("ax", "bx", "cx", "dx", "si", "di", "es", "sp", "bp"))


class Listeners(unittest.TestCase):
    def test_a_listener_added_during_a_write_waits_for_the_next_write(self):
        m = PortMachine(bytes(MEM_SIZE), 0x1000)
        calls = []

        def late(address, size, value):
            calls.append(('late', address, value))

        def first(address, size, value):
            calls.append(('first', address, value))
            if len(calls) == 1:
                m.on_write(0x500, 0x50F, late)

        m.on_write(0x500, 0x50F, first)
        m.write_as(0x504, 2, 0x1234, 0x10)
        self.assertEqual(calls, [('first', 0x504, 0x1234)])
        m.write_as(0x506, 1, 0x1FF, 0x10)
        self.assertEqual(calls[1:], [('first', 0x506, 0xFF), ('late', 0x506, 0xFF)])
        self.assertEqual(m.read(0x504, 3), bytes((0x34, 0x12, 0xFF)))
        self.assertEqual(m._writes_now, tuple(m._writes))

    def test_listeners_outside_the_range_are_not_called_and_order_is_kept(self):
        m = PortMachine(bytes(MEM_SIZE), 0x1000)
        calls = []
        for name, begin, end in (('a', 0x600, 0x600), ('b', 0x500, 0x5FF), ('c', 0x5FE, 0x700), ('d', 0x400, 0x4FF)):
            m.on_write(begin, end, lambda address, size, value, name=name: calls.append(name))
        m.write_as(0x5FE, 2, 7, 0x10)
        self.assertEqual(calls, ['b', 'c'])


class Addresses(unittest.TestCase):
    def test_call_addresses_parse_as_before(self):
        for address in ('0791:1F3C', '214B:0000', '0:0', 'ffff:FFFF'):
            self.assertEqual(guest._parsed(address), tuple(int(x, 16) for x in address.split(':')))
            self.assertIs(guest._parsed(address), guest._parsed(address))

        def old(address):
            seg, off = (int(x, 16) for x in address.split(':'))
            return seg, off

        def new(address):
            seg, off = guest._parsed(address)
            return seg, off

        for address in ('0791', '1:2:3', 'zz:00', ''):
            self.assertEqual(outcome(lambda: new(address))[:2], outcome(lambda: old(address))[:2], address)


class Drive(unittest.TestCase):
    """E034-03's first straight drive, as recorded before T117 (events, result, full memory)."""

    def test_e034_03_drive_equals_the_recorded_before_receipt(self):
        before = json.loads(RECEIPT.read_text())
        spec = importlib.util.spec_from_file_location("boundaries", ROOT / "experiments/E033-original-match-kit/save_boundaries.py")
        harness = importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
        from original_match import Image, Match, Fixture
        from original_match.assets import reference_image
        m = Match(Image.from_savestate(reference_image(ROOT / ".cache/dl")), Fixture(7, 19, index=9, kind=200), managed=7,
                  substitutions=None, engine="port", record_draws=True)
        self.assertEqual(m.timeout_s, 60)

        def policy(match, data):
            match.answer(quick=True) if data["context"] == "half_time" else match.answer()

        events = harness.drive(m, policy, ())
        digest = lambda value: hashlib.sha256(json.dumps(value, sort_keys=True, default=repr).encode()).hexdigest()
        self.assertEqual(len(events), before["events"])
        self.assertEqual(digest(events), before["events_sha256"])
        self.assertEqual(digest(m.result()), before["result_sha256"])
        self.assertEqual(hashlib.sha256(m.m.read(0, 0x110000)).hexdigest(), before["memory_sha256"])


if __name__ == "__main__":
    unittest.main()
