from rngcook import rng_cooked

RNG_LEN = 607
RNG_TAP = 273
RNG_MAX = 1 << 63
RNG_MASK = RNG_MAX - 1
INT32_MAX = (1 << 31) - 1


def seedrand(x):
    """Seed function for rng: x[n+1] = 48271 * x[n] mod (2**31 - 1)"""
    A = 48271
    Q = 44488
    R = 3399

    hi = x // Q
    lo = x % Q
    x = A * lo - R * hi
    if x < 0:
        x += INT32_MAX
    return x


class RngSource:
    def __init__(self, mt = None):
        self.tap = 0
        self.feed = RNG_LEN - RNG_TAP
        if mt is not None:
            self.vec = list(mt)
        else:
            self.vec = [0] * RNG_LEN

    def seed(self, seed):
        self.tap = 0
        self.feed = RNG_LEN - RNG_TAP

        seed %= INT32_MAX
        if seed < 0:
            seed += INT32_MAX
        if seed == 0:
            seed = 89482311

        x = int(seed)
        for i in range(-20, RNG_LEN):
            x = seedrand(x)
            if i >= 0:
                u = (int(x) << 40) & 0xFFFFFFFFFFFFFFFF
                x = seedrand(x)
                u ^= (int(x) << 20) & 0xFFFFFFFFFFFFFFFF
                x = seedrand(x)
                u ^= int(x)
                u ^= rng_cooked[i]
                self.vec[i] = u

    def int63(self):
        """Returns a non-negative pseudo-random 63-bit integer"""
        return self.uint64() & RNG_MASK

    def uint64(self):
        """Returns a non-negative pseudo-random 64-bit integer"""
        self.tap -= 1
        if self.tap < 0:
            self.tap += RNG_LEN

        self.feed -= 1
        if self.feed < 0:
            self.feed += RNG_LEN

        x = (self.vec[self.feed] + self.vec[self.tap]) & 0xFFFFFFFFFFFFFFFF
        self.vec[self.feed] = x
        return x