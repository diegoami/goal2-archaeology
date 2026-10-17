"""runtime/original_match/port (T58): the port mode, on synthetic programs (no byte of the original).

- PortMachineTests (unicorn): a port's write fires the kit's watch (and the draw record's write listener) as the
  original's instruction it names, before it lands, the routine's own code never run; a site inside a ported routine
  fires the kit's hook there once, at the listing's point; a stub returns its value in AX with its `ret n`; a hook at
  a port's entry that stops is replayed on resume and the port then runs once, never twice; a stop made by a site
  inside a port resumes at the port's return as a fresh start (no replay there) without running the port again; a
  decision inside a port is refused (PortError); a saved match names its ports and a loaded one has them again.
- RegistryTests (no emulator): the per-module registries, their variants, the listing's return forms, and a port run
  on PlainMem with its writes reaching its listeners.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import port  # noqa: E402
from original_match.port import Registry, PortError  # noqa: E402
from original_match.port.mem import PlainMem  # noqa: E402
from original_match.machine import Machine, MEM_SIZE  # noqa: E402
try:
    import unicorn  # noqa: F401
except ImportError:                    # CI does not install python3-unicorn
    Machine = None

# 0100:0000  E8 0D 00         call 0x0010
# 0100:0003  90               nop          (the return address)
# 0100:0004  90               nop          (the end of the run)
# 0100:0010  C6 06 00 50 07   mov byte ptr [0x5000], 7
# 0100:0015  B8 34 12         mov ax, 0x1234
# 0100:0018  C3               ret
PROGRAM = {0x0000: bytes([0xE8, 0x0D, 0x00, 0x90, 0x90]),
           0x0010: bytes([0xC6, 0x06, 0x00, 0x50, 0x07, 0xB8, 0x34, 0x12, 0xC3])}
CODE = 0x0100
END = CODE * 16 + 4
TARGET = 0x5000                        # DS:5000


@unittest.skipIf(Machine is None, "unicorn not installed")
class PortMachineTests(unittest.TestCase):
    def machine(self):
        memory = bytearray(MEM_SIZE)
        for off, code in PROGRAM.items():
            memory[CODE * 16 + off:CODE * 16 + off + len(code)] = code
        m = Machine(memory, load=0)
        for reg, v in (("cs", CODE), ("eip", 0), ("ss", 0x0800), ("sp", 0x0400), ("ds", m.DS), ("es", m.DS)):
            m.set_reg(reg, v)
        self.target = m.DS * 16 + TARGET
        return m

    def registry(self, fn=None, address="0100:0010", ret="ret"):
        reg = Registry("test")
        reg.port(address, ret=ret)(fn or (lambda mem, variant: mem.wds8(TARGET, 9, "0100:0010")))
        return reg

    def test_unported_routine_runs(self):
        m = self.machine()
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual(m.read(self.target, 1), b"\x07")
        self.assertEqual(m.reg("ax"), 0x1234)

    def test_a_ports_write_fires_the_kits_watch(self):
        m = self.machine()
        seen, raw = [], []
        m.watch(self.target, 1, lambda old, new: seen.append((old, new, m.pc(), m.read(self.target, 1))))
        m.on_write(self.target, self.target, lambda a, n, v: raw.append((a, n, v)))
        inst = port.install(m, [(self.registry(), None)])
        self.assertIsNone(m.run(END, 5, fresh=True))
        # the watch saw the port's write as 0100:0010's, before it landed; the original's 7 was never written
        self.assertEqual(seen, [(b"\x00", b"\x09", m.lin("0100:0010"), b"\x00")])
        self.assertEqual(raw, [(self.target, 1, 9)])
        self.assertEqual(m.read(self.target, 1), b"\x09")
        self.assertEqual(inst.calls, {"0100:0010": 1})
        self.assertEqual((m.reg("ip"), m.reg("sp")), (4, 0x0400))      # returned as `ret`

    def test_a_watch_refusing_a_ports_write_stops_the_run(self):
        m = self.machine()

        def refuse(old, new):
            raise RuntimeError("an undeclared writer")
        m.watch(self.target, 1, refuse)
        port.install(m, [(self.registry(), None)])
        with self.assertRaisesRegex(RuntimeError, "an undeclared writer"):
            m.run(END, 5, fresh=True)
        self.assertEqual(m.read(self.target, 1), b"\x00")               # it never landed

    def test_a_site_inside_a_ported_routine_fires(self):
        m = self.machine()
        calls = []
        m.at("0100:0015", lambda replay: calls.append((replay, m.pc())))

        def fn(mem, variant):
            mem.wds8(TARGET, 9, "0100:0010")
            mem.site("0100:0015")
        port.install(m, [(self.registry(fn), None)])
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual(calls, [(False, m.lin("0100:0015"))])
        self.assertEqual(m.pc(), END)                                   # pc() is the guest's again

    def test_a_stub_returns_its_value(self):
        m = self.machine()
        reg = Registry("test")
        reg.stub("0100:0010", ret="ret", value=0x4321, why="a synthetic routine")
        inst = port.install(m, [(reg, None)])
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual(m.reg("ax"), 0x4321)
        self.assertEqual(m.read(self.target, 1), b"\x00")               # the routine's code never ran
        self.assertEqual(inst.calls, {"0100:0010": 1})

    def test_a_stub_returns_as_retf_n(self):
        # 0100:0000 push 0x7777; call far 0100:0010; nop; nop (the routine pops its argument: retf 2)
        memory = bytearray(MEM_SIZE)
        memory[0x1000:0x1000 + 10] = bytes([0x68, 0x77, 0x77, 0x9A, 0x10, 0x00, 0x00, 0x01, 0x90, 0x90])
        m = Machine(memory, load=0)
        for r, v in (("cs", CODE), ("eip", 0), ("ss", 0x0800), ("sp", 0x0400), ("ds", m.DS)):
            m.set_reg(r, v)
        reg = Registry("test")
        args = []
        reg.port("0100:0010", ret="retf 2")(lambda mem, variant: args.append(mem.arg(0)) or 0x55)
        port.install(m, [(reg, None)])
        self.assertIsNone(m.run(0x1009, 5, fresh=True))
        self.assertEqual((args, m.reg("ax"), m.reg("sp")), ([0x7777], 0x55, 0x0400))

    def test_a_replayed_hook_runs_no_port_twice(self):
        m = self.machine()
        flags = []

        def kit_hook(replay):          # a kit hook at the ported routine's entry that stops once (a tick's events)
            flags.append(replay)
            if len(flags) == 1:
                m.stop("events")
        m.at("0100:0010", kit_hook)
        inst = port.install(m, [(self.registry(), None)])
        self.assertEqual(m.run(END, 5, fresh=True), "events")
        self.assertEqual(inst.calls["0100:0010"], 0)                    # stopped before the port
        self.assertIsNone(m.run(END, 5))
        self.assertEqual(flags, [False, True])
        self.assertEqual(inst.calls["0100:0010"], 1)

    def test_a_stop_inside_a_port_resumes_at_its_return(self):
        m = self.machine()
        at_return = []
        m.at("0100:0015", lambda replay: m.stop("events"))
        m.at("0100:0003", lambda replay: at_return.append(replay))

        def fn(mem, variant):
            mem.site("0100:0015")
            mem.wds8(TARGET, 9, "0100:0010")                           # the port goes on to its return
        inst = port.install(m, [(self.registry(fn), None)])
        self.assertEqual(m.run(END, 5, fresh=True), "events")
        self.assertEqual((m.pc(), m.read(self.target, 1)), (CODE * 16 + 3, b"\x09"))
        self.assertIsNone(m.run(END, 5))
        self.assertEqual(at_return, [False])                            # its first visit, not a replay
        self.assertEqual(inst.calls["0100:0010"], 1)

    def test_a_decision_inside_a_port_is_refused(self):
        m = self.machine()
        m.at("0100:0015", lambda replay: m.stop("decision"))
        port.install(m, [(self.registry(lambda mem, variant: mem.site("0100:0015")), None)])
        with self.assertRaises(PortError):
            m.run(END, 5, fresh=True)

    def test_a_saved_match_names_its_ports(self):
        from original_match.match import Match, fresh_state
        mt = Match.__new__(Match)
        mt.m = Machine(bytearray(MEM_SIZE), load=0)
        mt.st, mt.opts, mt.inputs, mt.side = fresh_state({}), {"record_draws": False}, [], 0
        mt.image_sha256, mt.end_lin, mt.fixture_ptr, mt.timeout_s = "x", 0, (0, 0), 5
        mt._queue, mt._result, mt._menu, mt.image_header, mt.image_tail = [], None, None, b"", b""
        mt._install_ports(["pilot.no-picture"])
        mt.ports.calls["0791:8889"] = 3
        loaded = Match.load(mt.save())
        self.assertEqual(loaded.opts["ports"], ["pilot.no-picture"])
        self.assertEqual(loaded.ports.names, ["pilot.no-picture"])
        self.assertEqual(loaded.ports.calls, {"0791:8889": 3})
        self.assertIn(loaded.m.lin("0791:8889"), loaded.m._ports)


class RegistryTests(unittest.TestCase):
    def test_pilot_registers_itself(self):
        self.assertIn("pilot", port.available())
        (reg, variant), = port.load(["pilot"])
        self.assertIsNone(variant)
        e = reg.entries["0791:8889"]
        self.assertEqual((e.far, e.pop), (False, 2))
        self.assertEqual(sorted(reg.variants), ["bound-36", "coin-swapped", "no-picture"])
        self.assertEqual(port.spec_names(port.load(["pilot", "pilot.bound-36"])), ["pilot.bound-36"])

    def test_unknown_modules_and_variants_are_refused(self):
        with self.assertRaises(ValueError):
            port.load(["nosuch"])
        with self.assertRaises(ValueError):
            port.load(["pilot.nosuch"])
        with self.assertRaises(ValueError):
            port.load(["pilot.coin-swapped", "pilot.bound-36"])
        with self.assertRaises(ValueError):
            Registry("x").port("0791:0000", ret="jmp")(lambda mem, v: None)

    def test_a_port_on_plain_memory(self):
        mem = PlainMem(bytearray(0x110000), load=0)
        seen = []
        ds = mem.DS * 16
        mem.listeners.append((ds + 0x7B62, ds + 0x7B63, lambda a, n, v, at: seen.append((a - ds, n, v, at))))
        mem.memory[ds + 0xA978:ds + 0xA97C] = bytes([0x62, 0x7B]) + mem.DS.to_bytes(2, "little")   # -> DS:7B62
        from original_match.port import pilot
        r = pilot.rand(mem, 5)
        new = (0 * 0x7ABD + 0x1B0F) & 0xFFFF
        self.assertEqual(seen, [(0x7B62, 2, new, mem.lin("214B:069F"))])
        self.assertEqual(mem.ds16(0x7B62), new)
        self.assertEqual(r, ((new * 5) >> 16) + 1)


if __name__ == "__main__":
    unittest.main()
