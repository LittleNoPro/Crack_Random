
class MT19937:
    """Classical Mersenne Twister Implementation."""

    w, n, m, r = 32, 624, 397, 31
    a = 0x9908b0df
    u, d = 11, 0xffffffff
    s, b = 7, 0x9d2c5680
    t, c = 15, 0xefc60000
    l = 18
    f = 0x6C078965

    def __init__(self, seed=None):
        self.mt = [0 for i in range(624)]
        self.index = 624
        if seed is not None:
            self.seed(seed)

    def seed(self, seed):
        self.mt[0] = seed
        for i in range(1, 624):
            self.mt[i] = self._int32(self.f *
                                (self.mt[i - 1] ^ (self.mt[i - 1] >> (self.w - 2))) + i)

    def extract(self):
        """ Extracts a 32bit word """
        if self.index >= 624:
            self.twist()

        x = self.mt[self.index]
        x ^= x >> self.u
        x ^= (x << self.s) & self.b
        x ^= (x << self.t) & self.c
        x ^= x >> self.l
        x &= self.d

        self.index += 1
        return self._int32(x)

    def twist(self):
        """ The twist operation. Advances the internal state """
        for i in range(624):
            upper = 1 << (self.w - 1)
            lower = (1 << (self.w - 1)) - 1

            x = self._int32((self.mt[i] & upper) +
                            (self.mt[(i + 1) % 624] & lower))
            self.mt[i] = self.mt[(i + self.m) % 624] ^ (x >> 1)

            if x & 1 != 0:
                self.mt[i] ^= self.a

        self.index = 0

    def _int32(self, x):
        return x & 0xffffffff


class PythonMT19937(MT19937):
    """Minimalistic Mersenne Twister implementation with python's custom seed,
        which allows for the seed to be larger than 32 bit.

        Returns 32bit values via extract().
    """
    def __init__(self, seed=None):
        MT19937.__init__(self)
        if seed is not None:
            self.seed(seed)

    def seed(self, n):
        lower = 0xffffffff
        keys = []

        while n:
            keys.append(n & lower)
            n >>= 32

        if len(keys) == 0:
            keys.append(0)

        self.init_by_array(keys)

    def init_by_array(self, keys):
        MT19937.seed(self, 0x12bd6aa)
        i, j = 1, 0
        for _ in range(max(624, len(keys))):
            self.mt[i] = self._int32((self.mt[i] ^ ((self.mt[i-1] ^
                            (self.mt[i-1] >> (self.w - 2))) * 0x19660d)) + keys[j] + j)
            i += 1
            j += 1
            if i >= 624:
                self.mt[0] = self.mt[623]
                i = 1
            j %= len(keys)

        for _ in range(623):
            self.mt[i] = self._int32((self.mt[i] ^ ((self.mt[i-1] ^
                            (self.mt[i-1] >> (self.w - 2))) * 0x5d588b65)) - i)
            i += 1
            if i >= 624:
                self.mt[0] = self.mt[623]
                i = 1

        self.mt[0] = 0x80000000


def test_PythonMT19937():
    import random
    seed = 0

    mtorig = random.Random(seed)
    mt = PythonMT19937(seed)

    for i in range(10):
        r1 = mtorig.getrandbits(32)
        r2 = mt.extract()

        print(r1, r2)

        assert r1 == r2

test_PythonMT19937()