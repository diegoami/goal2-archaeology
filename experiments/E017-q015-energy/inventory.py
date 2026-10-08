"""All direct DI + C/D/E listing accesses, without a player-pointer filter.

Printed references are instruction listing lines, not decompiler line numbers.
Classification and pointer provenance are in notes.md: a pitch access in a
routine that also loads players is not a player-field access. Removing the
old player-load filter also exposes the unrelated runtime and manager records.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def candidates():
    for path in sorted((ROOT / 'static/goal-exe/code').glob('seg_*.asm')):
        chunks = re.split(r'(?=; ---- routine )', path.read_text())
        line = 1
        for chunk in chunks:
            heading = re.match(r'; ---- routine ([0-9A-F]+:[0-9A-F]+)', chunk)
            if heading:
                refs = []
                for n, text in enumerate(chunk.splitlines(), line):
                    if re.search(r'es:\[di \+ 0x[cde]\]|add di, 0x[cde]$', text):
                        refs.append((n, text))
                if refs:
                    yield heading[1], path.name, refs
            line += chunk.count('\n')


if __name__ == '__main__':
    for routine, file, refs in candidates():
        print(routine, file)
        for line, text in refs:
            print(f'  {line}: {text}')
