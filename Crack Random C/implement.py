class RandomC:
    def __init__(self, seed, max_val):
        self.seed = seed
        self.max_val = max_val
        self.r = [0] * self.max_val
        self.r[0] = seed
        for i in range(1, 31):
            self.r[i] = (16807 * self.r[i - 1]) % 2147483647
            if self.r[i] < 0:
                self.r[i] += 2147483647
        for i in range(31, 34):
            self.r[i] = self.r[i - 31]
        for i in range(34, 344):
            self.r[i] = (self.r[i - 31] + self.r[i - 3]) % 2**32
        for i in range(344, self.max_val):
            self.r[i] = (self.r[i - 31] + self.r[i - 3]) % 2**32

    def random(self):
        return [((self.r[i] >> 1) & 0xFFFFFFFF) for i in range(344, self.max_val)]

if __name__ == "__main__":
    rand_gen = RandomC(seed = 100, max_val = 344 + 50)
    print(rand_gen.random())