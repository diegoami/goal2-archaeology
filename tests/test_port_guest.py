"""runtime/original_match/port (T59): guest calls, a decision under a port, the proof mode and the divergence locator,
on synthetic programs (no byte of the original).

- GuestCallTests (unicorn): a port that calls a routine still the original's gets the callee's registers back, the
  callee's writes reach the kit's watch and write listeners as a guest's and its kit hooks fire, and the state at the
  return equals the unported routine's; a far call pushes the segment, and a caller-pops call has its arguments
  dropped at the return; a guest call's return address in code Unicorn has already translated is still reached (the
  cache is dropped); a decision a kit hook makes inside the callee stops the run with the port's frame live, the port
  not going on, and the run resumes exactly (the hook replayed, then the port); Match.save refuses while a port's
  frame is live; a frame resumes only at its own return address, and a reach of it with another SP is not the call's
  return.
- ProofTests (unicorn): a faithful port is proved and the muted original reaches no kit listener; a port writing one
  byte differently, or returning another AX from a function, raises ProofError naming the routine, the call and the
  byte or register; a procedure's port (it returns None) has AX counted as scratch; a call whose original reaches a
  kit site gives way to the port (counted as not proved); a proof not armed runs the port as is.
- LocatorTests: the first differing per-minute row of two records, a one-byte divergence located to its call, and
  the grammar and comparison of ported records (records.py, compare.py, family.py --ports/--variant).
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import port  # noqa: E402
from original_match.port import Registry  # noqa: E402
from original_match.port.guest import call, PortFrame  # noqa: E402
from original_match.port.prove import Prover, ProofError  # noqa: E402
from original_match.machine import Machine, MEM_SIZE  # noqa: E402
try:
    import unicorn  # noqa: F401
except ImportError:                    # CI does not install python3-unicorn
    Machine = None

E036 = ROOT / "experiments/E036-match-port"


def load_scripts(names):
    """E036's scripts under the names e036t59_<name> (the suite is one process; other tests have their own `records`
    and `compare`), each finding its siblings while it executes."""
    path, saved = list(sys.path), {n: sys.modules.pop(n) for n in names if n in sys.modules}
    sys.path.insert(0, str(E036))
    out = []
    try:
        for n in names:
            spec = importlib.util.spec_from_file_location("e036t59_" + n, E036 / f"{n}.py")
            module = importlib.util.module_from_spec(spec)
            sys.modules["e036t59_" + n] = sys.modules[n] = module
            spec.loader.exec_module(module)
            out.append(module)
    finally:
        for n in names:
            sys.modules.pop(n, None)
            if n in saved:
                sys.modules[n] = saved[n]
        sys.path[:] = path + [str(E036)]
    return out


records, families, compare, family, locate = load_scripts(("records", "families", "compare", "family", "locate"))

# 0100:0000  E8 0D 00         call 0x0010                 (P)
# 0100:0003  90               nop                         (P's return)
# 0100:0004  90               nop                         (the end of the run)
# 0100:0010  55               push bp                     P: the routine a port replaces
# 0100:0011  89 E5            mov bp, sp
# 0100:0013  B8 05 00         mov ax, 5
# 0100:0016  50               push ax
# 0100:0017  E8 16 00         call 0x0030                 (G, still the original's)
# 0100:001A  A2 02 50         mov [0x5002], al            (G's return address)
# 0100:001D  5D               pop bp
# 0100:001E  C3               ret
# 0100:0030  55               push bp                     G(arg): [5000] := 7, [5001] := arg, AX 0x1234, DX 0x5678
# 0100:0031  89 E5            mov bp, sp
# 0100:0033  C6 06 00 50 07   mov byte ptr [0x5000], 7
# 0100:0038  8A 46 04         mov al, [bp + 4]
# 0100:003B  A2 01 50         mov [0x5001], al
# 0100:003E  B8 34 12         mov ax, 0x1234
# 0100:0041  BA 78 56         mov dx, 0x5678
# 0100:0044  5D               pop bp
# 0100:0045  C2 02 00         ret 2
# 0100:0050  55 89 E5 8A 46 06 A2 03 50 B8 21 43 5D CA 02 00   F(arg), far: [5003] := arg, AX 0x4321, retf 2
# 0100:0070  55 89 E5 8A 46 04 A2 03 50 5D C3                  H(arg), the caller pops: [5003] := arg, ret
PROGRAM = {0x0000: bytes([0xE8, 0x0D, 0x00, 0x90, 0x90]),
           0x0010: bytes([0x55, 0x89, 0xE5, 0xB8, 0x05, 0x00, 0x50, 0xE8, 0x16, 0x00, 0xA2, 0x02, 0x50, 0x5D, 0xC3]),
           0x0030: bytes([0x55, 0x89, 0xE5, 0xC6, 0x06, 0x00, 0x50, 0x07, 0x8A, 0x46, 0x04, 0xA2, 0x01, 0x50,
                          0xB8, 0x34, 0x12, 0xBA, 0x78, 0x56, 0x5D, 0xC2, 0x02, 0x00]),
           0x0050: bytes([0x55, 0x89, 0xE5, 0x8A, 0x46, 0x06, 0xA2, 0x03, 0x50, 0xB8, 0x21, 0x43, 0x5D, 0xCA, 0x02, 0x00]),
           0x0070: bytes([0x55, 0x89, 0xE5, 0x8A, 0x46, 0x04, 0xA2, 0x03, 0x50, 0x5D, 0xC3])}
CODE = 0x0100
END = CODE * 16 + 4
P, G, G_RETURN, INSIDE_G = "0100:0010", "0100:0030", "0100:001A", "0100:0038"
TARGET = 0x5000                        # DS:5000..5002


def faithful(mem, variant):
    """P as the listing writes it, with G called as the original's."""
    mem.enter(0, P)                                       # 0010-0011
    mem.set_reg("ax", 5)                                  # 0013
    ax = yield call(G, 5, ret_to=G_RETURN, far=False)     # 0016-0017
    mem.wds8(TARGET + 2, ax & 0xFF, G_RETURN)             # 001A


def registry(fn=faithful, address=P, ret="ret"):
    reg = Registry("test")
    reg.port(address, ret=ret)(fn)
    return reg


class Synthetic:
    """The synthetic program in a machine, and P's port with the proof."""

    def machine(self):
        memory = bytearray(MEM_SIZE)
        for off, code in PROGRAM.items():
            memory[CODE * 16 + off:CODE * 16 + off + len(code)] = code
        m = Machine(memory, load=0)
        self.start(m)
        self.target = m.DS * 16 + TARGET
        return m

    def start(self, m):
        for reg, v in (("cs", CODE), ("eip", 0), ("ss", 0x0800), ("sp", 0x0400), ("bp", 0x0123), ("ds", m.DS),
                       ("es", m.DS), ("ax", 0), ("dx", 0)):
            m.set_reg(reg, v)

    def outcome(self, m):
        return (m.read(self.target, 3), {r: m.reg(r) for r in ("ax", "dx", "sp", "bp", "ip", "cs")},
                m.read(0x8000 + 0x400 - 8, 8))                       # the stack below the start, written by P and G

    def prove(self, fn=faithful, armed=lambda: True, address=P, ret="ret", kit_site=False):
        m = self.machine()
        writes = []
        m.watch(self.target, 3, lambda old, new: writes.append((old, new)))
        hits = []
        if kit_site:
            m.at(INSIDE_G, lambda replay: hits.append(replay))
        inst = port.install(m, [(registry(fn, address, ret), None)])
        prover = Prover(m, inst, armed=armed, where=lambda: "minute 7")
        return m, prover, writes, hits


@unittest.skipIf(Machine is None, "unicorn not installed")
class GuestCallTests(Synthetic, unittest.TestCase):
    def test_a_guest_call_returns_the_originals_registers_and_writes(self):
        plain = self.machine()
        self.assertIsNone(plain.run(END, 5, fresh=True))
        m = self.machine()
        seen, raw, inside = [], [], []
        m.watch(self.target, 1, lambda old, new: seen.append((old, new, m.pc())))
        m.on_write(self.target + 1, self.target + 2, lambda a, n, v: raw.append((a - self.target, v, m.pc())))
        m.at(INSIDE_G, lambda replay: inside.append((replay, len(m.frames))))
        got = []

        def fn(mem, variant):
            mem.enter(0, P)
            mem.set_reg("ax", 5)
            ax = yield call(G, 5, ret_to=G_RETURN, far=False)
            got.append((ax, mem.reg("dx")))
            mem.wds8(TARGET + 2, ax & 0xFF, G_RETURN)
        inst = port.install(m, [(registry(fn), None)])
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual(got, [(0x1234, 0x5678)])                       # the callee's AX and DX
        self.assertEqual(seen, [(b"\x00", b"\x07", m.lin("0100:0033"))])  # G's write, seen as the guest's
        self.assertEqual(raw, [(1, 5, m.lin("0100:003B")), (2, 0x34, m.lin(G_RETURN))])
        self.assertEqual(inside, [(False, 1)])                          # the kit's hook in G, the port's frame live
        self.assertEqual(self.outcome(m), self.outcome(plain))          # memory, registers and stack as unported
        self.assertEqual((inst.calls, m.frames), ({P: 1}, []))

    def test_a_far_call_pushes_the_segment_and_the_callee_pops_its_argument(self):
        m = self.machine()
        got = []

        def fn(mem, variant):
            sp = mem.reg("sp")
            ax = yield call("0100:0050", 0x11, ret_to=G_RETURN, far=True)
            got.append((ax, (sp - mem.reg("sp")) & 0xFFFF, mem.u16(mem.ss_lin(sp - 2)), mem.u16(mem.ss_lin(sp - 4)),
                        mem.u16(mem.ss_lin(sp - 6))))
        port.install(m, [(registry(fn), None)])
        self.assertIsNone(m.run(END, 5, fresh=True))
        # AX, SP back where the call left it, and the stack: the argument, CS, the return offset (as call far does)
        self.assertEqual(got, [(0x4321, 0, 0x11, CODE, 0x001A)])
        self.assertEqual(m.read(self.target + 3, 1), b"\x11")

    def test_a_caller_pops_call_drops_its_arguments(self):
        m = self.machine()
        got = []

        def fn(mem, variant):
            sp = mem.reg("sp")
            yield call("0100:0070", 0x22, ret_to=G_RETURN, far=False, caller_pops=True)
            got.append((sp - mem.reg("sp")) & 0xFFFF)                 # the listing's `add sp, 2` after the call
        port.install(m, [(registry(fn), None)])
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual((got, m.read(self.target + 3, 1), m.frames), ([0], b"\x22", []))

    def test_a_return_address_in_code_already_translated_is_reached(self):
        m = self.machine()
        self.assertIsNone(m.run(END, 5, fresh=True))                    # P's body (001A included) translated
        m.write(self.target, bytes(4))
        self.start(m)
        marks = []

        def fn(mem, variant):
            ax = yield call(G, 5, ret_to=G_RETURN, far=False)
            marks.append(ax)
            mem.wds8(TARGET + 3, 1, G_RETURN)                           # a byte only the port writes
        port.install(m, [(registry(fn), None)])
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual((marks, m.read(self.target + 3, 1), m.frames), ([0x1234], b"\x01", []))

    def test_a_decision_under_a_port_stops_and_resumes_exactly(self):
        plain = self.machine()
        self.assertIsNone(plain.run(END, 5, fresh=True))
        m = self.machine()
        visits = []

        def decide(replay):            # the kit's notice: a decision, the original stopped before the instruction
            visits.append((replay, [f.describe() for f in m.frames]))
            if len(visits) == 1:
                m.stop("decision")
        m.at(INSIDE_G, decide)
        inst = port.install(m, [(registry(), None)])
        self.assertEqual(m.run(END, 5, fresh=True), "decision")
        self.assertEqual(m.pc(), m.lin(INSIDE_G))
        self.assertEqual(m.read(self.target, 3), b"\x07\x00\x00")       # the port did not go on after the stop
        self.assertEqual([f.describe() for f in m.frames],
                         [f"{P} waiting on its call of {G} (returning to {G_RETURN})"])
        self.assertIsNone(m.run(END, 5))                                # answered: the match goes on
        self.assertEqual([v[0] for v in visits], [False, True])         # the hook replayed, once
        self.assertEqual(self.outcome(m), self.outcome(plain))
        self.assertEqual((inst.calls, m.frames), ({P: 1}, []))

    def test_save_refuses_while_a_ports_frame_is_live(self):
        from original_match.match import Match, MatchError, fresh_state
        m = self.machine()
        m.at(INSIDE_G, lambda replay: replay or m.stop("decision"))
        port.install(m, [(registry(), None)])
        self.assertEqual(m.run(END, 5, fresh=True), "decision")
        mt = Match.__new__(Match)
        mt.m, mt.ports, mt.prover = m, None, None
        mt.st, mt.opts, mt.inputs, mt.side = fresh_state({}), {"record_draws": False}, [], 0
        mt.image_sha256, mt.end_lin, mt.fixture_ptr, mt.timeout_s = "x", END, (0, 0), 5
        mt._queue, mt._result, mt._menu, mt.image_header, mt.image_tail = [], None, None, b"", b""
        with self.assertRaisesRegex(MatchError, f"a port's frame is live \\({P} waiting on its call of {G}"):
            mt.save()
        self.assertIsNone(m.run(END, 5))
        self.assertTrue(mt.save().startswith(b"OMK1"))                  # the frame gone, the match saves

    def test_a_frame_resumes_only_at_its_return_address(self):
        m = self.machine()
        resumed = []

        class Waiting:                 # a frame whose stack test always holds: only the address may hold it back
            ret_lin = m.lin("0100:0060")

            def returned(self, machine):
                return True

            def resume(self, machine):
                resumed.append(machine.pc())
        m.at("0100:0003", lambda replay: None)                          # a kit hook the guest reaches
        m.expect_return(Waiting())
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual((resumed, len(m.frames)), ([], 1))

    def test_the_return_address_with_another_sp_is_not_the_calls_return(self):
        m = self.machine()
        reg = registry()
        frame = PortFrame(m, port.mem.MachineMem(m), reg.entries[P], None)
        frame.expect_sp, frame.ss = 0x0300, m.reg("ss")
        m.set_reg("sp", 0x02FE)                                         # deeper: a recursive reach
        self.assertFalse(frame.returned(m))
        m.set_reg("sp", 0x0300)
        self.assertTrue(frame.returned(m))
        m.set_reg("ss", 0x0801)                                         # another stack
        self.assertFalse(frame.returned(m))


@unittest.skipIf(Machine is None, "unicorn not installed")
class ProofTests(Synthetic, unittest.TestCase):
    """The proof of P's port against P (G stays the original's), or of G's against G."""

    def test_a_faithful_port_is_proved(self):
        m, prover, writes, _ = self.prove()
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual(prover.summary(), {P: {"proved": 1, "unproved": {}, "scratch": {}}})
        self.assertEqual(m.read(self.target, 3), b"\x07\x05\x34")
        # the port's run only, on memory the original's run left as it was: the muted original reached no listener
        self.assertEqual(writes, [(b"\x00\x00\x00", b"\x07\x00\x00"), (b"\x07\x00\x00", b"\x07\x05\x00"),
                                  (b"\x07\x05\x00", b"\x07\x05\x34")])
        self.assertEqual((m.reg("ip"), m.reg("sp"), m.frames, m.muted), (4, 0x0400, [], False))

    def test_a_one_byte_divergence_is_named(self):
        def off_by_one(mem, variant):
            mem.enter(0, P)
            mem.set_reg("ax", 5)
            ax = yield call(G, 5, ret_to=G_RETURN, far=False)
            mem.wds8(TARGET + 2, (ax & 0xFF) ^ 1, G_RETURN)
        m, prover, _, _ = self.prove(off_by_one)
        with self.assertRaises(ProofError) as e:
            m.run(END, 5, fresh=True)
        self.assertEqual(str(e.exception),
                         f"{P} (test), call #1 from 0100:0003, minute 7: written byte #2 differs: the original wrote "
                         f"0x34 at linear 0x{m.DS * 16 + TARGET + 2:05X} (DS:5002), the port wrote 0x35 at linear "
                         f"0x{m.DS * 16 + TARGET + 2:05X} (DS:5002)")

    def test_a_functions_other_result_is_named(self):
        m, prover, _, _ = self.prove(lambda mem, variant: (mem.wds8(TARGET, 7, "0100:0033"),
                                                           mem.wds8(TARGET + 1, mem.arg(0), "0100:003B"),
                                                           0x1235)[-1], address=G, ret="ret 2")
        with self.assertRaisesRegex(ProofError, f"^{G} \\(test\\), call #1 from 0100:001A, minute 7: register AX at "
                                                "the return: the original 0x1234, the port 0x1235$"):
            m.run(END, 5, fresh=True)

    def test_a_procedures_ax_is_scratch(self):
        def no_result(mem, variant):                # P's port that leaves AX as G left it, then clears it: a procedure
            yield from faithful(mem, variant)
            mem.set_reg("ax", 0)
        m, prover, _, _ = self.prove(no_result)
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual(prover.summary()[P], {"proved": 1, "unproved": {}, "scratch": {"AX": 1}})

    def test_a_call_whose_original_reaches_a_kit_site_gives_way(self):
        m, prover, writes, hits = self.prove(kit_site=True)
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual(prover.summary()[P], {"proved": 0, "unproved": {INSIDE_G: 1}, "scratch": {}})
        self.assertEqual(hits, [False])             # once: the port's run, not the muted original's
        self.assertEqual((m.read(self.target, 3), len(writes)), (b"\x07\x05\x34", 3))

    def test_a_proof_not_armed_runs_the_port(self):
        m, prover, writes, _ = self.prove(armed=lambda: False)
        self.assertIsNone(m.run(END, 5, fresh=True))
        self.assertEqual(prover.summary()[P]["proved"], 0)
        self.assertEqual((m.read(self.target, 3), len(writes)), (b"\x07\x05\x34", 3))


def rows(*digests):
    return [[m, 10, d] for m, d in enumerate(digests)]


class LocatorTests(unittest.TestCase):
    def test_the_first_differing_row(self):
        ref = {"draws": {"per_minute": rows("a" * 64, "b" * 64, "c" * 64)}}
        self.assertEqual(locate.first_differing_row(ref, {"draws": {"per_minute": rows("a" * 64, "x" * 64, "c" * 64)}}),
                         (1, 1, 10))
        self.assertEqual(locate.first_differing_row(ref, {"draws": {"per_minute": rows("a" * 64, "b" * 64)}}),
                         (2, 2, 20))                                     # a row missing at the end
        self.assertEqual(locate.first_differing_row(ref, {"draws": None}), (0, 0, 0))   # no draws: from the start
        self.assertIsNone(locate.first_differing_row(ref, ref))

    @unittest.skipIf(Machine is None, "unicorn not installed")
    def test_a_one_byte_divergence_is_located_to_its_call(self):
        """The locator's second step on a synthetic divergence: the run proved from the start names the call."""
        def diverges_second_time(mem, variant):
            calls.append(1)
            yield from faithful(mem, variant)
            if len(calls) == 2:
                mem.wds8(TARGET + 1, 6, "0100:003B")
        calls = []
        t = Synthetic()
        m, prover, _, _ = t.prove(diverges_second_time)
        self.assertIsNone(m.run(END, 5, fresh=True))
        t.start(m)
        with self.assertRaisesRegex(ProofError, f"^{P} \\(test\\), call #2 from 0100:0003, minute 7: the port writes "
                                                "more: byte #3, 0x06 at linear 0x[0-9A-F]{5} \\(DS:5001\\)"):
            m.run(END, 5, fresh=True)

    def reference_record(self):
        with open(ROOT / "experiments/E036-match-port/out/T57/reference.jsonl") as f:
            return json.loads(f.readline())

    def test_the_grammar_of_a_ported_record(self):
        r = self.reference_record()
        records.validate(r)
        ported = dict(r, ports=["pilot", "restarts"], variant="restarts.side-swapped",
                      port_calls={"0791:8889": 5, "0791:6E11": 0})
        records.validate(ported)
        for bad in ({"variant": None}, {"ports": ["pilot"]}):           # partial keys
            with self.assertRaises(records.SchemaError):
                records.validate(dict(r, **bad))
        for key, value in (("ports", []), ("ports", ["restarts", "pilot"]), ("ports", ["pilot", "pilot"]),
                           ("variant", "other.coin-swapped"), ("variant", "restarts"), ("port_calls", {}),
                           ("port_calls", {"0791:8889": -1}), ("port_calls", {"8889": 1})):
            with self.assertRaises(records.SchemaError, msg=f"{key}={value}"):
                records.validate(dict(ported, **{key: value}))

    def test_a_ported_reference_is_refused(self):
        r = self.reference_record()
        ported = dict(r, ports=["pilot"], variant=None, port_calls={"0791:8889": 5})
        expected = {r["id"]: r["spec_sha256"]}
        lines, ok = compare.check({r["id"]: r}, {r["id"]: ported}, expected)
        self.assertTrue(ok, lines)                  # a ported candidate compares with the unhooked reference
        with self.assertRaisesRegex(compare.Malformed, "was run with ports"):
            compare.check({r["id"]: ported}, {r["id"]: r}, expected)

    def test_the_ports_options(self):
        self.assertEqual(family.port_specs(None, None), ([], [], None))
        self.assertEqual(family.port_specs("pilot,restarts", "restarts.side-swapped"),
                         (["pilot", "restarts.side-swapped"], ["pilot", "restarts"], "restarts.side-swapped"))
        self.assertEqual(family.port_specs(None, "pilot.bound-36")[0], ["pilot.bound-36"])
        for ports, variant in (("nosuch", None), (None, "pilot.nosuch"), (None, "pilot"), ("guest", None)):
            with self.assertRaises(family.Refused, msg=f"{ports} {variant}"):
                family.port_specs(ports, variant)
        self.assertEqual(port.available(), ["pilot", "restarts"])        # the machinery is no port module

    def test_a_log_of_other_ports_is_refused(self):
        import tempfile
        r = self.reference_record()
        spec = next(m for fam in families.discover().values() for m in fam.matches if m.id == r["id"])
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "log.jsonl"
            out.write_text(records.dumps(dict(r, ports=["pilot"], variant=None, port_calls={"0791:8889": 1})) + "\n")
            self.assertIn(r["id"], family.existing_records(out, [spec], [], ["pilot"]))
            for ports in ([], ["pilot.coin-swapped"], ["pilot", "restarts"]):
                with self.assertRaises(family.Refused, msg=str(ports)):
                    family.existing_records(out, [spec], [], ports)


if __name__ == "__main__":
    unittest.main()
