BASH_RAND_MAX = 0x7fff  # 15 bits

class BashRandom:
    def __init__(self, seed: int, is_old: bool):
        self.seed = seed
        self.last = 0
        self.is_old = is_old
        self.a = 16807
        self.m = 0x7fffffff  # 2^31 - 1

    def next_16(self) -> int:
        self.next_seed()

        if self.is_old:
            # Bash 5.0 and earlier
            result = self.seed & BASH_RAND_MAX
        else:
            # Bash 5.1 and later
            result = ((self.seed >> 16) ^ (self.seed & 0xffff)) & BASH_RAND_MAX

        # Skip if same as last
        if result == self.last:
            return self.next_16()
        self.last = result
        return result

    def next_16_n(self, n: int) -> list:
        return [self.next_16() for _ in range(n)]

    def skip(self, n: int) -> None:
        for _ in range(n):
            self.next_16()

    def next_seed(self) -> int:
        if self.seed == 0:
            self.seed = 123459876

        self.seed = (self.seed * self.a) % self.m
        return self.seed

    def next_seed_n(self, n: int) -> list:
        return [self.next_seed() for _ in range(n)]

# Tests
if __name__ == "__main__":
    def test_bash_52_zero():
        rng = BashRandom(0, False)
        assert rng.next_16_n(3) == [20814, 24386, 149], "bash_52_zero test failed"

    def test_bash_52_n():
        rng = BashRandom(1337, False)
        assert rng.next_16_n(3) == [24697, 15233, 8710], "bash_52_n test failed"

    def test_bash_52_big():
        rng = BashRandom(2147483646, False)
        assert rng.next_16_n(3) == [16807, 10791, 19566], "bash_52_big test failed"

    def test_bash_50_zero():
        rng = BashRandom(0, True)
        assert rng.next_16_n(3) == [20034, 24315, 12703], "bash_50_zero test failed"

    def test_bash_50_n():
        rng = BashRandom(1337, True)
        assert rng.next_16_n(3) == [24879, 21848, 15683], "bash_50_n test failed"

    def test_bash_50_big():
        rng = BashRandom(2147483646, True)
        assert rng.next_16_n(3) == [15960, 17678, 21286], "bash_50_big test failed"

    # Run tests
    test_bash_52_zero()
    test_bash_52_n()
    test_bash_52_big()
    test_bash_50_zero()
    test_bash_50_n()
    test_bash_50_big()
    print("All tests passed!")