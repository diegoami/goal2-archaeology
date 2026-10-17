"""Rule 9 check for test_cases.py: change one row of cases.tsv at a time and show the test fails.

usage (from the repository root): python3 -B experiments/E037-exchange-windows/mutate.py > experiments/E037-exchange-windows/out/mutation.txt

For each row: (1) its verdict is replaced by another one and only the verdict test runs (the hash pin is not
involved); (2) its finals_flag is flipped (0 <-> 1, '?' -> 0) and the whole Cases class runs. cases.tsv is read
first and written back in a finally block (CLAUDE.md rule 9a).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, 'cases.tsv')
OTHER = {'allowed': 'tour', 'finals': 'allowed', 'tour': 'allowed', 'in_match': 'allowed', 'sacked': 'allowed',
         'unknown': 'allowed'}


def run(test):
    r = subprocess.run([sys.executable, '-B', '-m', 'unittest', test], cwd=HERE,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return 'FAILS' if r.returncode else 'passes'


def main():
    with open(CASES, 'rb') as f:
        original = f.read()
    lines = original.decode().split('\n')
    header = lines[0].split('\t')
    ie, ifl = header.index('expected'), header.index('finals_flag')
    print('# E037 mutate.py: one row changed at a time; baseline verdict test %s, Cases %s' % (
        run('test_cases.Cases.test_every_row_matches_the_predicate'), run('test_cases.Cases')))
    try:
        for k in range(1, len(lines)):
            if not lines[k]:
                continue
            f = lines[k].split('\t')
            m1 = list(f)
            m1[ie] = OTHER[f[ie]]
            m2 = list(f)
            m2[ifl] = {'0': '1', '1': '0', '?': '0'}[f[ifl]]
            out = []
            for m, test in ((m1, 'test_cases.Cases.test_every_row_matches_the_predicate'), (m2, 'test_cases.Cases')):
                mutated = lines[:k] + ['\t'.join(m)] + lines[k + 1:]
                with open(CASES, 'w') as fh:
                    fh.write('\n'.join(mutated))
                out.append(run(test))
            print('%s verdict %s -> %s: verdict test %s | finals_flag %s -> %s: Cases %s' % (
                f[0], f[ie], m1[ie], out[0], f[ifl], m2[ifl], out[1]))
    finally:
        with open(CASES, 'wb') as fh:
            fh.write(original)
    print('# restored; final Cases %s' % run('test_cases.Cases'))


if __name__ == '__main__':
    main()
