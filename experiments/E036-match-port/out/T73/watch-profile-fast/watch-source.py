"""T73 independent UNHOOKED DS access evidence, before any candidate or mask.

Each guest access is attributed to its instruction and static routine. An additional
active T73 caller identifies shared-library writes made on behalf of a display
routine, but does not erase the actual instruction owner. Kit reads are separate:
semantic reads are retained, only the explicit memory-digest/footprint snapshots
and screen hashing are labelled measurement. No value or original byte is output.

Usage: python3.12 -B .../watch_accesses.py --only O8/c1-c2-friendly --out-dir <new dir>
The directory is immutable: an existing per-match output is refused, not overwritten.
"""
import argparse
import bisect
from collections import Counter
import json
from pathlib import Path
import sys
import time
import resource

ROOT = Path(__file__).resolve().parents[4]
E036 = ROOT / 'experiments/E036-match-port'
sys.path.insert(0, str(ROOT / 'runtime'))
sys.path.insert(0, str(E036))
import families
import family
import records
import sizes
from original_match import Image
from original_match.assets import reference_image
from original_match.match import SS_PARAGRAPH
from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, UC_HOOK_CODE
from unicorn import x86_const as X

DISPLAY = set(sizes.TASKS['T73'][3])
ROUTINES = []
for line in (ROOT / 'static/goal-exe/routines.tsv').read_text().splitlines():
    if not line or line.startswith(';') or line.startswith('segment:offset'):
        continue
    cells = line.split('\t')
    seg, off = (int(x, 16) for x in cells[0].split(':'))
    ROUTINES.append((seg * 16 + off, seg * 16 + off + int(cells[1]), cells[0]))
ROUTINES.sort()
STARTS = [a for a, b, r in ROUTINES]


def owner(relative):
    i = bisect.bisect_right(STARTS, relative) - 1
    if i >= 0 and relative < ROUTINES[i][1]:
        return ROUTINES[i][2]
    return 'UNKNOWN'


class Watch:
    def __init__(self, mode='all', fast_pc=False):
        self.mode = mode
        self.fast_pc = fast_pc
        self.current_pc = None
        self.accesses = Counter()
        self.host_reads = Counter()
        self.host_writes = Counter()
        self.frames = []
        self.m = None
        self.calls = Counter()
        self.current = ('UNKNOWN', '-', 'UNKNOWN')
        self.instruction_cache = {}
        self.watched_spans = ()

    def install(self, match):
        m = self.m = match.m
        assert not m._ports
        ds = m.DS * 16
        load = m.load * 16
        for address in (sorted(DISPLAY) if self.mode in ('all', 'entries') else []):
            def entered(replay, address=address):
                if replay:
                    return
                ss, sp = m.reg('ss'), m.reg('sp')
                while self.frames and (self.frames[-1][1] != ss or sp > self.frames[-1][2]):
                    self.frames.pop()
                self.frames.append((address, ss, sp))
                self.calls[address] += 1
            m.at(address, entered)
            # Observe entry SP before a kit service can return immediately (e.g. delay).
            # This is read-only instrumentation order, not a port or a new runtime API.
            handlers = m._handlers[m.lin(address)]
            handlers.insert(0, handlers.pop())

        # Raw MEM_READ observers of the kit's live return stack perturb this Unicorn build,
        # even a no-op observer (probe-hooks-none); the same observer excluding the stack is exact.
        # Excluded bytes are NEVER mask candidates. SS's DS-relative base is from match.py;
        # the text-buffer boundary is the actual initial A96E/A972 pointer, not a guessed mask.
        stack_begin = m.seg(SS_PARAGRAPH) * 16 - ds
        screen_begin = min(m.far(0xA96E), m.far(0xA972)) - ds
        assert 0 < stack_begin < screen_begin < 0x10000
        self.watched_spans = ((0, stack_begin), (screen_begin, 0x10000))

        def code(uc, address, size, data):
            relative = address - load
            placed = self.instruction_cache.get(relative)
            if placed is None:
                routine = owner(relative)
                if routine == 'UNKNOWN':
                    at = 'P+' + format(relative, 'X')
                else:
                    seg = int(routine[:4], 16)
                    at = f'{seg:04X}:{relative - seg * 16:04X}'
                placed = routine, at
                self.instruction_cache[relative] = placed
            if self.fast_pc:
                self.current = placed[0], '-', placed[1]
                return
            sp = uc.reg_read(X.UC_X86_REG_ESP) & 65535
            ss = uc.reg_read(X.UC_X86_REG_SS) & 65535
            while self.frames and (self.frames[-1][1] != ss or sp > self.frames[-1][2]):
                self.frames.pop()
            self.current = placed[0], self.frames[-1][0] if self.frames else '-', placed[1]

        def accessed(uc, access, address, size, value, data, kind):
            # No VM register read occurs in a memory callback: the instruction observer supplies context.
            start, end = max(address, ds), min(address + size, ds + 0x10000)
            if start >= end:
                return
            routine, context, at = self.current
            self.accesses[(kind, routine, context, at, start - ds, end - start)] += 1

        if self.mode in ('all', 'guest'):
            m.uc.hook_add(UC_HOOK_CODE, code)
            for begin, end in self.watched_spans:
                m.uc.hook_add(UC_HOOK_MEM_READ, lambda *args: accessed(*args, 'read'),
                              begin=ds + begin, end=ds + end - 1)
                m.uc.hook_add(UC_HOOK_MEM_WRITE, lambda *args: accessed(*args, 'write'),
                              begin=ds + begin, end=ds + end - 1)
        assert m.io_tap is None and m.write_tap is None

        def host_read(kind, address, value):
            if kind != 'r':
                return
            start, end = max(address, ds), min(address + len(value), ds + 0x10000)
            if start >= end:
                return
            frame = sys._getframe(1)
            stack = []
            while frame is not None:
                stack.append(frame.f_code.co_name)
                frame = frame.f_back
            # These exact paths read whole memory/digests, or pixels for a hash. Other kit reads remain protected.
            measurement = 'digest_memory' in stack or '_screen_raw' in stack
            if not measurement and not m.running and len(value) == 0x110000 and 'run_match' in stack:
                measurement = True
            category = 'measurement' if measurement else 'semantic'
            origin = next((f for f in stack if f not in ('read', 'rd', 'word_at', 'host_read')), '?')
            self.host_reads[(category, origin, start - ds, end - start)] += 1

        def host_write(address, value):
            start, end = max(address, ds), min(address + len(value), ds + 0x10000)
            if start < end:
                self.host_writes[(start - ds, end - start)] += 1
        if self.mode in ('all', 'kit'):
            m.io_tap = host_read
            m.write_tap = host_write

    def report(self, mid):
        return {
            'schema': 1, 'match': mid, 'ports': [], 'fast_pc': self.fast_pc,
            'watched_ds_spans': [list(s) for s in self.watched_spans],
            'excluded_ds_spans_are_unmaskable': True,
            'display_entries': dict(sorted(self.calls.items())),
            'guest_accesses': [dict(kind=k, routine=r, display_context=c, instruction=a,
                                    ds_offset=o, size=n, count=count)
                               for (k, r, c, a, o, n), count in sorted(self.accesses.items())],
            'kit_reads': [dict(category=k, origin=origin, ds_offset=o, size=n, count=count)
                          for (k, origin, o, n), count in sorted(self.host_reads.items())],
            'kit_writes': [dict(ds_offset=o, size=n, count=count)
                           for (o, n), count in sorted(self.host_writes.items())],
        }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--only', required=True)
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--fast-pc', action='store_true', help='actual instruction owner only; no optional caller context')
    ap.add_argument('--mode', choices=('all', 'entries', 'guest', 'kit'), default='all')
    ap.add_argument('--time-limit', type=float, default=6000)
    args = ap.parse_args()
    want = args.only.split(',')
    all_specs = {m.id: m for f in families.discover().values() for m in f.matches}
    assert set(want) <= set(all_specs)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    image = Image.from_bytes(reference_image(family.DEFAULT_CACHE))
    for mid in want:
        name = mid.replace('/', '__')
        accesses, record = out / (name + '-accesses.json'), out / (name + '-record.jsonl')
        if accesses.exists() or record.exists():
            raise SystemExit(f'refusing to overwrite evidence for {mid}')
        watcher = Watch(args.mode, args.fast_pc)
        t0 = time.monotonic()
        rec = family.run_match(image, all_specs[mid], time_limit=args.time_limit,
                               stretch_limit=args.time_limit, watch=watcher.install)
        record.write_text(records.dumps(rec) + '\n')
        report = watcher.report(mid)
        report['profile'] = {'elapsed_s': time.monotonic() - t0,
                             'max_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                             'unique_guest_accesses': len(watcher.accesses)}
        accesses.write_text(json.dumps(report, indent=2) + '\n')
        print(mid, 'completed' if rec['error'] is None else rec['error'],
              f'{len(watcher.accesses)} attributed DS access sites/ranges', flush=True)
        if rec['error']:
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
