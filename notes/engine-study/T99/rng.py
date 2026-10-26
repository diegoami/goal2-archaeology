"""Source-derived word LCG; every draw advances, including bounds zero and one."""
MOD=65536
MULTIPLIER=0x7ABD
INCREMENT=0x1B0F


def step(seed):return (seed*MULTIPLIER+INCREMENT)&65535


def draw(seed,bound):
    seed=step(seed)
    return seed,((seed*(bound&65535))>>16)+1


def s16(x):
    x&=65535
    return x-65536 if x>=32768 else x
