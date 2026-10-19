"""T60 fuzz: the random inputs of the 0791 geometry routines (fuzz.py; generators.py has the runtime's). They fill DS with
a random match state (the 22 pitch records, the ball, the two slots, the direction tables, the draw table, the players'
and countries' bytes the routines read) and give the routine a record and a word that reach its edges."""
from generators import GENERATORS, regs

PITCH = 0x80E8
SLOT = 0x16


def pitch_state(tr, img, players=True):
    rnd = tr.rnd
    ds = img.DS * 16
    for slot in range(1, 23):
        rec = bytearray(rnd.randrange(256) for _ in range(SLOT))
        rec[0] = rnd.choice([0, 1, 5, 0xFF, 0xFB, 0x80, rnd.randrange(256)])                  # x
        rec[1] = rnd.choice([0, 3, 0x20, 0x21, 0x25, 0x1C, 0x1D, 0xE0, 0xDB, 0x80, rnd.randrange(256)])    # y
        rec[6] = rnd.choice([slot, slot, rnd.randrange(0, 24), 0xB, 0xC, 0xD, 0x16])          # the slot
        idx = rnd.randrange(0, 600)
        rec[0xD], rec[0xE] = idx & 0xFF, idx >> 8
        rec[0x12] = rnd.choice([0, 1, 2, 5, 0x0B, rnd.randrange(256)])
        tr.poke(ds + PITCH + SLOT * slot, bytes(rec))
        if players:
            far = img.far(0xA91B)
            tr.poke(far + 0x14 * idx, bytes(rnd.choice([0, 1, 0x1F, 0x20, 0x21, 0x80, 0xE0, rnd.randrange(256)])
                                             for _ in range(0x14)))
    tr.poke(ds + 0x830B, bytes([rnd.choice([0, 1, 5, 0xB, 0xC, 0xD, 0x16, rnd.randrange(0, 24)]),
                                rnd.choice([0, 1, 5, 0xB, 0xC, 0xD, 0x16, rnd.randrange(0, 24)])]))
    tr.poke(ds + 0x8302, bytes([rnd.choice([0, 0, 1, 2])]))
    tr.poke(ds + 0x8319, bytes([rnd.choice([0, 1, 0xFF, 0x80, 0x7F, rnd.randrange(256)])]))
    tr.poke(ds + 0x831B, rnd.choice([0, 1, 2, 0x7F, 0x80, 0xFF, 0x100, rnd.randrange(0x10000)]).to_bytes(2, "little"))
    tr.poke(ds + 0x82F6, bytes([rnd.choice([0, 1, 5, 0xFF, rnd.randrange(256)]),
                                rnd.choice([0, 3, 0x20, 0x21, 0xE0, 0xFF, rnd.randrange(256)])]))
    tr.poke(ds + 0x7920, bytes(rnd.choice([(0xFF, 1), (1, 0xFF), (1, 1), (0xFF, 0xFF)])))
    tr.poke(ds + 0x9B34, bytes([rnd.randrange(0, 4), 0, rnd.randrange(0, 4), 0]))
    tr.poke(ds + 0x668, bytes([0, 11]) if rnd.random() < 0.8 else bytes([rnd.randrange(256), rnd.randrange(256)]))
    tr.poke(ds + 0x80FC, bytes([rnd.choice([0, 1])]))
    tr.poke(ds + 0x8327, bytes([rnd.choice([0, 1, 2, 3, 4, 5, 7, 8, 0x18, rnd.randrange(256)])]))
    tr.poke(ds + 0x8437, rnd.choice([0, 1, 0xFE, 0xFF, 0x100, rnd.randrange(0x10000)]).to_bytes(2, "little"))
    tr.poke(ds + 0x8337, bytes(rnd.randrange(16) for _ in range(256)))
    tr.poke(ds + 0x769, bytes(rnd.choice([0, 0, 1]) for _ in range(40)))
    tr.poke(ds + 0x776, bytes([rnd.choice([3, 5, 8, 0x0A]), rnd.choice([3, 5, 8, 0x0A])]))
    if players:
        cfar = img.far(0xA917)
        for c in range(4):
            tr.poke(cfar + 0xBF * c + 0x2D, bytes([rnd.randrange(256)]))


def rec_arg(tr, img):
    slot = tr.rnd.randrange(1, 23)
    return [PITCH + SLOT * slot, img.DS]


def g_draw_table_byte(tr, img):
    regs(tr)
    pitch_state(tr, img, players=False)


def g_set_message_word(tr, img):
    regs(tr)
    tr.args = [tr.rnd.choice([0, 1, 2, 0x100, 0x1FF, tr.rnd.randrange(0x10000)])]


def g_noargs(tr, img):
    regs(tr)
    pitch_state(tr, img, players=True)


def g_with_rec(tr, img):
    regs(tr)
    pitch_state(tr, img)
    tr.args = rec_arg(tr, img)


def g_with_rec_word(tr, img):
    regs(tr)
    pitch_state(tr, img)
    rnd = tr.rnd
    tr.args = rec_arg(tr, img) + [rnd.choice([rnd.randrange(0x10000), 0x2100, 0x1900, 0x0525, 0x2702, 0x2A03, 0x25FF,
                                              0xFFFF, 0x0000, 0xDF03, 0xE0FE, 0x2102, 0x2103, 0xDF02, 0x2505, 0x2504, 0x1905])]


def g_with_rec_n(tr, img):
    regs(tr)
    pitch_state(tr, img)
    tr.args = rec_arg(tr, img) + [tr.rnd.choice([0, 1, 2, 3, 5, 8, 0x10, 0x7F, 0x80, 0xFF, 0x100, 0xFFFF,
                                                 tr.rnd.randrange(0x10000)])]


def g_26d7(tr, img):
    regs(tr)
    pitch_state(tr, img)
    tr.args = rec_arg(tr, img) + [tr.rnd.choice([0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11])]


def g_278a(tr, img):
    regs(tr)
    pitch_state(tr, img)
    tr.args = rec_arg(tr, img) + [tr.rnd.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])]


def g_byte_arg(tr, img):
    regs(tr)
    pitch_state(tr, img, players=True)
    tr.args = [tr.rnd.choice([0, 1, 2, 5, 0x0B, 0x100, 0x1FF, tr.rnd.randrange(0x10000)])]


def g_word_arg(tr, img):
    regs(tr)
    rnd = tr.rnd
    tr.args = [rnd.choice([rnd.randrange(0x10000), 0x2100, 0x1900, 0x0525, 0x2702, 0x2A03, 0x25FF, 0xFFFF, 0x0000,
                           0x0800, 0x0900, 0x0A00, 0x2700, 0x2800, 0x1800, 0x1A00, 0x0600, 0x0500, 0x2505, 0x1905, 0x1904, 0xE705,
                           0x2504, 0x2506, 0x2102, 0x2103, 0xDF02, 0xDF03])]


GENERATORS.update({
    "0791:261A": g_draw_table_byte, "0791:26A0": g_set_message_word, "0791:26C2": g_noargs, "0791:26D7": g_26d7,
    "0791:278A": g_278a, "0791:287C": g_278a, "0791:28B2": g_byte_arg, "0791:2929": g_byte_arg,
    "0791:2956": g_with_rec, "0791:2996": g_noargs, "0791:29B3": g_noargs, "0791:2A15": g_noargs,
    "0791:2A6D": g_noargs, "0791:2AA3": g_byte_arg, "0791:2AD4": g_byte_arg, "0791:2B0F": g_byte_arg,
    "0791:2B28": g_with_rec_n, "0791:2B51": g_with_rec, "0791:2B7B": g_with_rec, "0791:2BB1": g_with_rec,
    "0791:2C29": g_with_rec, "0791:2C54": g_with_rec, "0791:2C86": g_with_rec_word, "0791:2CEC": g_with_rec,
    "0791:2D10": g_with_rec_n, "0791:2D6D": g_with_rec_n, "0791:2E00": g_word_arg, "0791:2E36": g_with_rec_word,
    "0791:2E82": g_word_arg, "0791:2EB8": g_with_rec_word, "0791:2EF0": g_with_rec_word, "0791:2F28": g_with_rec,
})
