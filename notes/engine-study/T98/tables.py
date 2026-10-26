"""Read the complete committed DS hex extract, expanding its repeated rows."""
from pathlib import Path
import re
from functools import lru_cache

ROOT=Path(__file__).resolve().parents[3]


@lru_cache(maxsize=1)
def load_ds():
    data=bytearray(65536)
    known=bytearray(65536)
    previous=None
    repeat=False
    sources=[]
    for path in sorted((ROOT/'static/goal-exe/data').glob('ds_2581_*.hex')):
        sources.append(path.relative_to(ROOT).as_posix())
        for line in path.read_text().splitlines():
            if not line or line.startswith(';'):continue
            if line.strip()=='*':repeat=True;continue
            if re.fullmatch(r'[0-9A-Fa-f]{4}',line.strip()):
                end=int(line.strip(),16)
                if repeat and previous is not None:
                    start,old=previous
                    for p in range(start+32,end,32):
                        data[p:p+32]=old;known[p:p+32]=b'\x01'*32
                    repeat=False
                elif previous is not None and end!=previous[0]+len(previous[1]):
                    raise ValueError('hex end marker does not match last row')
                continue
            if not re.match(r'^[0-9A-Fa-f]{4}  ',line):raise ValueError(f'unknown hex row: {line}')
            offset=int(line[:4],16)
            raw=bytes.fromhex(line[6:].split('|',1)[0])
            if repeat:
                if previous is None:raise ValueError('repeat without preceding row')
                start,old=previous
                if len(old)!=32:raise ValueError('repeat of partial row')
                for p in range(start+32,offset,32):
                    data[p:p+32]=old;known[p:p+32]=b'\x01'*32
                repeat=False
            data[offset:offset+len(raw)]=raw
            known[offset:offset+len(raw)]=b'\x01'*len(raw)
            previous=offset,raw
    def read(offset):
        if not 0<=offset<65536 or not known[offset]:raise ValueError(f'DS byte not in static extract: {offset:04X}')
        return data[offset]
    return read,bytes(data),sources


def s8(x):return x-256 if x>=128 else x
def s16(x):return x-65536 if x>=32768 else x
