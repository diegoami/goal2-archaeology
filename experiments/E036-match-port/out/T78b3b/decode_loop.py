"""Decode the source listing's db-marked loop target; reads no game asset."""
from pathlib import Path
import re
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
root=Path(__file__).resolve().parents[4]
source=(root/'static/goal-exe/code/seg_23E4_02.asm').read_text()
line=next(s for s in source.splitlines() if re.match(r'^111F\s+db ',s))
raw=bytes.fromhex(line.split('db ',1)[1].split(';',1)[0])
for instruction in Cs(CS_ARCH_X86,CS_MODE_16).disasm(raw,0x111F):
    print(f'{instruction.address:04X} {instruction.mnemonic} {instruction.op_str}')
