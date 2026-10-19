"""T60 fuzz: the random inputs of each routine (fuzz.py). A generator fills a Trial: the stack words (arg 0 first), memory
writes (linear addresses; the scratch segment 0x9000 is linear 0x90000) and register overrides. Inputs are valid for the
routine (a screen stream whose rows fill their width, a Pascal string whose length byte is its length) and also reach its
edges (equal bounds, a zero count, an offset at the top of the segment, strings that overlap)."""
DATA = 0x9000
D = DATA * 16
M16 = 0xFFFF


def regs(tr, **fixed):
    for r in ("ax", "bx", "cx", "dx", "si", "di", "bp"):
        tr.regs[r] = tr.rnd.randrange(0x10000)
    tr.regs["es"] = DATA
    tr.regs.update(fixed)


def small_or_big(rnd, small=40, big=600, p_big=0.1):
    return rnd.randrange(big) if rnd.random() < p_big else rnd.randrange(small)


def words(rnd, n):
    return bytes(rnd.randrange(256) for _ in range(n))


def pascal(rnd, length=None, alphabet=None, maxlen=255):
    n = rnd.randrange(0, maxlen + 1) if length is None else length
    if alphabet is None:
        body = bytes(rnd.randrange(256) for _ in range(n))
    else:
        body = bytes(rnd.choice(alphabet) for _ in range(n))
    return bytes([n]) + body


# ---- 214B ---------------------------------------------------------------------------------------------------
def fill_words(tr, img):
    regs(tr)
    off = tr.rnd.choice([tr.rnd.randrange(0x10000), 0xFFFE, 0xFFFF, 0, 0x1000])
    tr.args = [tr.rnd.randrange(0x10000), small_or_big(tr.rnd), off, DATA]
    tr.random_bytes(D + 0xFF00, 0x100)


def fill_bytes(tr, img):
    regs(tr)
    off = tr.rnd.choice([tr.rnd.randrange(0x10000), 0xFFFE, 0xFFFF, 0, 0x1000])
    tr.args = [tr.rnd.randrange(0x10000), small_or_big(tr.rnd), off, DATA]


def move_bytes(tr, img):
    regs(tr)
    rnd = tr.rnd
    tr.random_bytes(D, 0x600)
    n = rnd.choice([0, 1, 2, 3, 4, 5, 7, 8, 9, rnd.randrange(300)])
    soff = rnd.randrange(0, 0x200)
    doff = soff + rnd.choice([-3, -2, -1, 0, 1, 2, 3, 5, rnd.randrange(-100, 100), 0x100, -0x100])
    doff = max(0, doff)
    tr.args = [n, doff & M16, DATA, soff, DATA]
    tr.note = f"n={n} s={soff:X} d={doff:X}"


def swap_bytes(tr, img):
    regs(tr)
    rnd = tr.rnd
    tr.random_bytes(D, 0x600)
    n = rnd.choice([1, 1, 2, 3, 7, rnd.randrange(1, 100)] + ([0] if rnd.random() < 0.03 else []))
    a = rnd.randrange(0, 0x100)
    b = a + rnd.choice([0, 1, 5, 0x40, 0x100, 0x200])
    tr.args = [n, b, DATA, a, DATA]
    tr.note = f"n={n}"


def upcase_string(tr, img):
    regs(tr)
    rnd = tr.rnd
    alphabet = bytes(range(0x30, 0x7F)) + bytes([0x40, 0x5B, 0x60, 0x7B, 0x61, 0x7A])
    s = pascal(rnd, rnd.choice([0, 1, 2, 10, 0x4F, 0x50, 0x51, 0x60, rnd.randrange(0, 256)]), alphabet)
    soff, doff = 0x100, 0x500
    tr.poke(D + soff, s)
    tr.args = [soff, DATA, doff, DATA]


def screen_stream(rnd, rows=None, cols=None, first_cell=None):
    rows = rows or rnd.randrange(1, 6)
    cols = cols or rnd.randrange(1, 30)
    first = first_cell or rnd.randrange(1, 100)
    body = bytearray()
    have_literal = False
    for _ in range(rows):
        remaining = cols
        while remaining > 0:
            op = rnd.random()
            if op < 0.2:
                body += bytes([0xFF, rnd.randrange(1, 256)])            # an attribute for the next characters
            elif op < 0.45 and remaining >= 1:
                run = rnd.randrange(1, remaining + 1)
                body += bytes([0, run])
                remaining -= run
            else:
                body += bytes([rnd.choice([rnd.randrange(1, 255), 0x20, 0x41, 0xFE])])
                remaining -= 1
                have_literal = True
    return bytes([first & 0xFF, first >> 8, rows, cols]) + bytes(body), rows, cols


def unpack_screen_rle(tr, img):
    regs(tr)
    stream, rows, cols = screen_stream(tr.rnd)
    tr.poke(D + 0x100, stream)
    tr.args = [0x100, DATA, 0x2000 + tr.rnd.randrange(0x40), DATA]
    tr.note = f"{rows}x{cols}"


def unpack_screen_to_buffer(tr, img):
    regs(tr)
    stream, rows, cols = screen_stream(tr.rnd)
    tr.poke(D + 0x100, stream)
    dest = 0x2000 + tr.rnd.randrange(0x40)
    tr.poke(D + 0x80, bytes([dest & 0xFF, dest >> 8, DATA & 0xFF, DATA >> 8]))      # the far pointer variable
    tr.args = [0x80, DATA, 0x100, DATA]


def unpack_screen_796a_to_back(tr, img):
    regs(tr)
    ds = img.DS * 16
    stream, rows, cols = screen_stream(tr.rnd)
    tr.poke(ds + 0x796A, stream)
    dest = 0x2000 + tr.rnd.randrange(0x40)
    tr.poke(ds + 0xA96E, bytes([dest & 0xFF, dest >> 8, DATA & 0xFF, DATA >> 8]))


def unpack_screen_row_record(tr, img):
    regs(tr)
    ds = img.DS * 16
    rnd = tr.rnd
    row = rnd.randrange(1, 26)
    rows, cols = rnd.randrange(1, 6), rnd.randrange(1, 30)
    stream, rows, cols = screen_stream(rnd, rows, cols, 1)
    tr.poke(ds + 0x79A6, stream[2:])                                      # the word at 79A4 is written by the routine
    dest = 0x2000 + rnd.randrange(0x40)
    tr.poke(ds + 0xA96E, bytes([dest & 0xFF, dest >> 8, DATA & 0xFF, DATA >> 8]))
    tr.args = [row]


def random_is_one(tr, img):
    regs(tr)
    tr.args = [tr.rnd.choice([1, 2, 3, 5, 10, 33, tr.rnd.randrange(0x10000), 0, 0xFFFF])]


def number_to_string(tr, img):
    regs(tr)
    rnd = tr.rnd
    value = rnd.choice([0, 1, -1, 9, 10, 99, 100, 2 ** 31 - 1, -2 ** 31, rnd.randrange(-2 ** 31, 2 ** 31),
                        rnd.randrange(-1000, 1000)]) & 0xFFFFFFFF
    tr.args = [value & M16, value >> 16, 0x300, DATA]
    tr.note = str(value)


def set_test_bit(tr, img):
    regs(tr)
    tr.args = [tr.rnd.randrange(0x10000), tr.rnd.choice([0, 1, 2, 8, 9, 16, 17, 31, 32, 33, tr.rnd.randrange(0x10000)])]


def _set_args(tr, extra=()):
    regs(tr)
    tr.random_bytes(D + 0x100, 8)
    k = tr.rnd.choice([0, 1, 2, 3, 8, 9, 15, 16, 17, 31, 32, 33, 0x100, 0x101, tr.rnd.randrange(0x10000)])
    return [0x103, DATA, k]


def set_include_bit(tr, img):
    tr.args = _set_args(tr)


def set_exclude_bit(tr, img):
    tr.args = _set_args(tr)


def set_toggle_bit(tr, img):
    tr.args = _set_args(tr)


def set_assign_bit(tr, img):
    a = _set_args(tr)
    tr.args = [tr.rnd.choice([0, 1, 2, 0x100, 0x1FF]), a[0], a[1], a[2]]


def _long_pair(rnd):
    pick = rnd.random()
    a = rnd.randrange(2 ** 32)
    if pick < 0.2:
        b = a
    elif pick < 0.4:
        b = (a & 0xFFFF0000) | rnd.randrange(0x10000)
    elif pick < 0.5:
        b = (a + rnd.choice([1, -1])) & 0xFFFFFFFF
    else:
        b = rnd.randrange(2 ** 32)
    return a, b


def longs(tr, img):
    regs(tr)
    a, b = _long_pair(tr.rnd)
    tr.args = [b & M16, b >> 16, a & M16, a >> 16]


def wrap_add(tr, img):
    regs(tr)
    rnd = tr.rnd
    lo = rnd.choice([0, 1, 5, rnd.randrange(0, 300)])
    hi = lo + rnd.choice([0, 1, 2, 10, 199, rnd.randrange(0, 400)])
    v = rnd.choice([lo, hi, lo + 1, hi - 1, rnd.randrange(0, 600)]) & M16
    delta = rnd.choice([0, 1, -1, 2, -2, 5, -5, 199, -199, rnd.randrange(-700, 700), 0x7FFF, -0x8000]) & M16
    tr.poke(D + 0x100, v.to_bytes(2, "little") + bytes([0xAA]))
    tr.args = [delta, hi & M16, lo & M16, 0x100, DATA]
    tr.note = f"v={v} lo={lo} hi={hi} d={delta:04X}"


def wrap_add_byte(tr, img):
    regs(tr)
    rnd = tr.rnd
    lo = rnd.choice([0, 1, 5, rnd.randrange(0, 100)])
    hi = lo + rnd.choice([0, 1, 2, 10, rnd.randrange(0, 150)])
    v = rnd.choice([lo, hi, lo + 1, hi - 1, rnd.randrange(0, 256)]) & 0xFF
    delta = rnd.choice([0, 1, -1, 2, -2, 5, -5, rnd.randrange(-300, 300)]) & M16
    tr.poke(D + 0x100, bytes([v, 0xAA, 0xBB]))
    tr.args = [delta, hi & M16, lo & M16, 0x100, DATA]
    tr.note = f"v={v} lo={lo} hi={hi} d={delta:04X}"


def clamp_int(tr, img):
    regs(tr)
    rnd = tr.rnd
    lo = rnd.choice([0, -5, 5, rnd.randrange(-300, 300)])
    hi = lo + rnd.choice([0, 1, 10, rnd.randrange(0, 600)])
    v = rnd.choice([lo, hi, lo - 1, hi + 1, rnd.randrange(-1000, 1000), -0x8000, 0x7FFF])
    tr.poke(D + 0x100, (v & M16).to_bytes(2, "little") + bytes([0xAA]))
    tr.args = [hi & M16, lo & M16, 0x100, DATA]


def clamp_byte(tr, img):
    regs(tr)
    rnd = tr.rnd
    lo = rnd.choice([0, -5, 5, rnd.randrange(-100, 100)])
    hi = lo + rnd.choice([0, 1, 10, rnd.randrange(0, 100)])
    hi = min(hi, 127)
    v = rnd.choice([lo, hi, lo - 1, hi + 1, rnd.randrange(-128, 128), -128, 127])
    tr.poke(D + 0x100, bytes([v & 0xFF, 0xAA]))
    tr.args = [hi & M16, lo & M16, 0x100, DATA]


# ---- 23E4 ---------------------------------------------------------------------------------------------------
def sys_move(tr, img):
    regs(tr)
    rnd = tr.rnd
    tr.random_bytes(D, 0x600)
    n = rnd.choice([0, 1, 2, 3, 9, rnd.randrange(300)])
    soff = rnd.randrange(0, 0x200)
    doff = max(0, soff + rnd.choice([-3, -1, 0, 1, 3, rnd.randrange(-50, 50), 0x100]))
    tr.args = [n, doff, DATA, soff, DATA]


def sys_long_mul(tr, img):
    rnd = tr.rnd
    regs(tr)
    for r in ("ax", "dx", "bx", "cx"):
        tr.regs[r] = rnd.choice([0, 1, 0xFFFF, 0x8000, rnd.randrange(0x10000)])


def sys_long_div(tr, img):
    rnd = tr.rnd
    regs(tr)
    for r in ("ax", "dx", "bx", "cx"):
        tr.regs[r] = rnd.choice([0, 1, 0xFFFF, 0x8000, 0x7FFF, rnd.randrange(0x10000)])
    if rnd.random() < 0.5:
        tr.regs["bx"] = rnd.choice([0, 0, 0xFFFF])
    if tr.regs["bx"] == 0 and tr.regs["cx"] == 0:       # a zero divisor is the original's runtime error 200: not run
        tr.regs["cx"] = 1
    tr.note = " ".join(f"{r}={tr.regs[r]:04X}" for r in ("dx", "ax", "bx", "cx"))


def _two_strings(tr, alphabet=None, a_max=255, b_max=255):
    rnd = tr.rnd
    a = pascal(rnd, rnd.choice([0, 1, 2, 5, rnd.randrange(0, a_max + 1)]), alphabet, a_max)
    b = pascal(rnd, rnd.choice([0, 1, 2, 5, rnd.randrange(0, b_max + 1)]), alphabet, b_max)
    return a, b


def sys_str_store(tr, img):
    regs(tr)
    a, _ = _two_strings(tr)
    tr.poke(D + 0x100, a)
    tr.args = [0x100, DATA, 0x400 + tr.rnd.choice([0, 0, 1, -40]) + 40, DATA]


def sys_str_store_max(tr, img):
    regs(tr)
    a, _ = _two_strings(tr)
    tr.poke(D + 0x100, a)
    tr.args = [tr.rnd.choice([0, 1, 5, 0x50, 0xFF, tr.rnd.randrange(0x10000)]), 0x400, DATA, 0x100, DATA]


def sys_str_copy(tr, img):
    regs(tr)
    rnd = tr.rnd
    a, _ = _two_strings(tr, a_max=30)
    tr.poke(D + 0x100, a)
    tr.args = [rnd.choice([0, 1, 5, 40, -1 & M16, 0x8000, rnd.randrange(0x10000)]),
               rnd.choice([0, 1, 2, 5, 31, -1 & M16, 0x8000, rnd.randrange(0x10000), rnd.randrange(1, 35)]),
               0x100, DATA, 0x400, DATA]


def sys_str_concat(tr, img):
    regs(tr)
    a, b = _two_strings(tr)
    tr.poke(D + 0x100, b)           # source
    tr.poke(D + 0x400, a)           # destination (the first string)
    tr.args = [0x100, DATA, 0x400, DATA]


def sys_str_pos(tr, img):
    regs(tr)
    rnd = tr.rnd
    alphabet = b"abc"
    s = pascal(rnd, rnd.choice([0, 1, 2, 5, rnd.randrange(0, 40)]), alphabet, 40)
    sub = pascal(rnd, rnd.choice([0, 1, 2, 3, rnd.randrange(0, 6)]), alphabet, 6)
    tr.poke(D + 0x100, s)
    tr.poke(D + 0x400, sub)
    tr.args = [0x100, DATA, 0x400, DATA]


def sys_str_compare(tr, img):
    regs(tr)
    rnd = tr.rnd
    a, b = _two_strings(tr, b"ab", 6, 6)
    if rnd.random() < 0.3:
        b = bytes([b[0]]) + a[1:1 + b[0]] + bytes(rnd.choice(b"ab") for _ in range(max(0, b[0] - (len(a) - 1))))
        b = bytes([len(b) - 1]) + b[1:]
    tr.poke(D + 0x100, a)
    tr.poke(D + 0x400, b)
    tr.args = [0x400, DATA, 0x100, DATA]


def sys_char_to_str(tr, img):
    regs(tr)
    tr.args = [tr.rnd.randrange(0x10000), 0x400, DATA]


def sys_str_insert(tr, img):
    regs(tr)
    rnd = tr.rnd
    s = pascal(rnd, rnd.choice([0, 1, 5, 20, rnd.randrange(0, 256)]), b"abcdef")
    src = pascal(rnd, rnd.choice([0, 1, 5, 20, rnd.randrange(0, 256)]), b"UVW")
    tr.poke(D + 0x100, s)
    tr.poke(D + 0x400, src)
    tr.args = [rnd.choice([0, 1, 2, 5, 19, 20, 21, 200, 255, 256, 0x8000, -1 & M16, rnd.randrange(0x10000)]),
               rnd.choice([0, 1, 20, 40, 0xFF, 0x100, 0x1FF, rnd.randrange(0x10000)]),
               0x100, DATA, 0x400, DATA]


def sys_str_delete(tr, img):
    regs(tr)
    rnd = tr.rnd
    s = pascal(rnd, rnd.choice([0, 1, 5, 20, rnd.randrange(0, 256)]), b"abcdef")
    tr.poke(D + 0x100, s)
    tr.args = [rnd.choice([0, 1, 2, 5, 100, 255, 0x7FFF, 0x8000, -1 & M16, rnd.randrange(0x10000)]),
               rnd.choice([0, 1, 2, 5, 19, 20, 21, 255, 0x7FFF, 0x8000, -1 & M16, rnd.randrange(0x10000)]),
               0x100, DATA]


def sys_set_compact(tr, img):
    regs(tr)
    rnd = tr.rnd
    tr.random_bytes(D + 0x100, 64)
    tr.args = [(rnd.randrange(0, 32) << 8) | rnd.randrange(0, 33), 0x400, DATA, 0x100, DATA]


def sys_long_to_digits(tr, img):
    regs(tr)
    rnd = tr.rnd
    value = rnd.choice([0, 1, -1, 9, 10, 99, 100, 2 ** 31 - 1, -2 ** 31, rnd.randrange(-2 ** 31, 2 ** 31)]) & 0xFFFFFFFF
    tr.regs["ax"], tr.regs["dx"] = value & M16, value >> 16
    tr.regs["di"], tr.regs["es"] = 0x400, DATA
    tr.note = str(value)


def sys_str_of_long(tr, img):
    regs(tr)
    rnd = tr.rnd
    value = rnd.choice([0, 1, -1, 12345, -987654321, 2 ** 31 - 1, -2 ** 31, rnd.randrange(-2 ** 31, 2 ** 31),
                        rnd.randrange(-1000, 1000)]) & 0xFFFFFFFF
    tr.args = [rnd.choice([0x14, 0x20, 3, 1, 0xFF, rnd.randrange(0, 40)]), 0x400, DATA,
               rnd.choice([0, 1, 5, 10, 11, 0x14, 0x30, -1 & M16, rnd.randrange(0, 40)]), value & M16, value >> 16]
    tr.note = str(value)


def sys_upcase(tr, img):
    regs(tr)
    tr.args = [tr.rnd.choice([0x61, 0x7A, 0x60, 0x7B, 0x41, tr.rnd.randrange(0x10000)])]


GENERATORS = {
    "214B:0000": fill_words, "214B:0018": fill_bytes, "214B:003C": move_bytes, "214B:007B": swap_bytes,
    "214B:009C": upcase_string, "214B:0147": unpack_screen_rle, "214B:0329": unpack_screen_to_buffer,
    "214B:05DB": unpack_screen_796a_to_back, "214B:05F0": unpack_screen_row_record, "214B:06D0": random_is_one,
    "214B:09DA": number_to_string, "214B:0C57": set_test_bit, "214B:0C79": set_include_bit,
    "214B:0CA1": set_exclude_bit, "214B:0CCB": set_assign_bit, "214B:0CF4": set_toggle_bit,
    "214B:0D1C": longs, "214B:0D56": longs, "214B:1C86": wrap_add, "214B:1D6F": wrap_add_byte,
    "214B:2000": clamp_int, "214B:2031": clamp_byte,
    "23E4:025D": sys_move, "23E4:0279": sys_long_mul, "23E4:0294": sys_long_div, "23E4:062A": sys_str_store,
    "23E4:0644": sys_str_store_max, "23E4:0676": sys_str_copy, "23E4:06B7": sys_str_concat,
    "23E4:06E3": sys_str_pos, "23E4:072F": sys_str_compare, "23E4:075A": sys_char_to_str,
    "23E4:0787": sys_str_insert, "23E4:07DB": sys_str_delete, "23E4:08BF": sys_set_compact,
    "23E4:11E4": sys_long_to_digits, "23E4:12F6": sys_str_of_long, "23E4:19B2": sys_upcase,
}
