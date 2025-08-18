from abc import ABC, abstractmethod
from rng import RngSource
from typing import Callable, List

class Source(ABC):
    @abstractmethod
    def int63(self) -> int:
        pass

    @abstractmethod
    def seed(self, seed: int) -> None:
        pass

class Source64(Source):
    @abstractmethod
    def uint64(self) -> int:
        pass

def new_source(seed: int) -> Source64:
    rng = RngSource()
    rng.seed(seed)
    return rng

def read(p: bytearray, src: Source, read_val: int, read_pos: int) -> tuple[int, None]:
    pos = read_pos
    val = read_val
    n = 0
    for n in range(len(p)):
        if pos == 0:
            val = src.int63()
            pos = 7
        p[n] = val & 0xFF
        val >>= 8
        pos -= 1
    return n, read_val, read_pos

class Rand:
    def __init__(self, src: Source):
        self.src = src
        self.s64 = src if isinstance(src, Source64) else None
        self.read_val = 0
        self.read_pos = 0

    def seed(self, seed: int) -> None:
        self.src.seed(seed)
        self.read_pos = 0

    def int63(self) -> int:
        return self.src.int63()

    def uint32(self) -> int:
        return self.int63() >> 31

    def uint64(self) -> int:
        if self.s64 is not None:
            return self.s64.uint64()
        return (self.int63() >> 31) | (self.int63() << 32)

    def int31(self) -> int:
        return self.int63() >> 32

    def int(self) -> int:
        u = self.int63()
        return u << 1 >> 1

    def int63n(self, n: int) -> int:
        if n <= 0:
            raise ValueError("invalid argument to int63n")
        if n & (n - 1) == 0:
            return self.int63() & (n - 1)
        max_val = (1 << 63) - 1 - ((1 << 63) % n)
        v = self.int63()
        while v > max_val:
            v = self.int63()
        return v % n

    def int31n(self, n: int) -> int:
        if n <= 0:
            raise ValueError("invalid argument to int31n")
        if n & (n - 1) == 0:
            return self.int31() & (n - 1)
        max_val = (1 << 31) - 1 - ((1 << 31) % n)
        v = self.int31()
        while v > max_val:
            v = self.int31()
        return v % n

    def _int31n_internal(self, n: int) -> int:
        v = self.uint32()
        prod = v * n
        low = prod & 0xFFFFFFFF
        if low < n:
            thresh = (-n) % n
            while low < thresh:
                v = self.uint32()
                prod = v * n
                low = prod & 0xFFFFFFFF
        return prod >> 32

    def intn(self, n: int) -> int:
        if n <= 0:
            raise ValueError("invalid argument to intn")
        if n <= (1 << 31) - 1:
            return self.int31n(n)
        return self.int63n(n)

    def float64(self) -> float:
        while True:
            f = self.int63() / (1 << 63)
            if f != 1.0:
                return f

    def float32(self) -> float:
        while True:
            f = float(self.float64())
            if f != 1.0:
                return f

    def perm(self, n: int) -> List[int]:
        m = list(range(n))
        for i in range(n):
            j = self.intn(i + 1)
            m[i], m[j] = m[j], m[i]
        return m

    def shuffle(self, n: int, swap: Callable[[int, int], None]) -> None:
        if n < 0:
            raise ValueError("invalid argument to shuffle")
        i = n - 1
        while i > (1 << 31) - 1 - 1:
            j = int(self.int63n(i + 1))
            swap(i, j)
            i -= 1
        while i > 0:
            j = int(self._int31n_internal(i + 1))
            swap(i, j)
            i -= 1

    def read(self, p: bytearray) -> tuple[int, None]:
        n, self.read_val, self.read_pos = read(p, self.src, self.read_val, self.read_pos)
        return n, None

def new(src: Source) -> 'Rand':
    return Rand(src)