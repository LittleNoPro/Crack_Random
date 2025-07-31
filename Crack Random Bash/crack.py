import multiprocessing
from multiprocessing import Pool, Manager
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from functools import partial

from implement import BashRandom

class OneResultCracker(ABC):
    @abstractmethod
    def find(self) -> Optional[int]:
        pass


def chunked_range(start, end, chunk_size):
    while start < end:
        yield range(start, min(start + chunk_size, end))
        start += chunk_size


def check_seed_range(seed_range, target, old):
    for i in seed_range:
        rng = BashRandom(i, old)
        if all(rng.next_16() == t for t in target):
            return i
    return None


class New3Cracker(OneResultCracker):
    def __init__(self, target: List[int]):
        self.target = target

    def find(self):
        max_seed = 2 ** 30
        chunk_size = 100000

        with Pool() as pool:
            for seed_range in chunked_range(0, max_seed, chunk_size):
                results = pool.starmap(
                    check_seed_range, [(seed_range, self.target, False)]
                )
                for res in results:
                    if res is not None:
                        pool.terminate()
                        return res
        return None


class Old3Cracker(OneResultCracker):
    def __init__(self, target: List[int]):
        self.target = target

    def find(self):
        max_seed = 2 ** 31
        chunk_size = 100000

        with Pool() as pool:
            for seed_range in chunked_range(0, max_seed, chunk_size):
                results = pool.starmap(
                    check_seed_range, [(seed_range, self.target, True)]
                )
                for res in results:
                    if res is not None:
                        pool.terminate()
                        return res
        return None


class MultiResultCracker(ABC):
    @abstractmethod
    def find(self, tx: multiprocessing.Queue):
        pass

class New2Cracker(MultiResultCracker):
    def __init__(self, target: List[int]):
        self.target = target

    def _check_seed(self, i: int, tx: multiprocessing.Queue):
        rng = BashRandom(i, False)
        if rng.next_16() == self.target[0] and rng.next_16() == self.target[1]:
            tx.put((i, False))

    def find(self, tx: multiprocessing.Queue):
        max_seed = 2**30  # Equivalent to u32::MAX / 4
        with Pool() as pool:
            pool.starmap(self._check_seed, [(i, tx) for i in range(max_seed)])
            pool.close()
            pool.join()

class Old2Cracker(MultiResultCracker):
    def __init__(self, target: List[int]):
        self.target = target

    def _check_seed(self, i: int, tx: multiprocessing.Queue):
        rng = BashRandom(i, True)
        if rng.next_16() == self.target[0] and rng.next_16() == self.target[1]:
            tx.put((i, True))

    def find(self, tx: multiprocessing.Queue):
        max_seed = 2**31  # Equivalent to u32::MAX / 2
        with Pool() as pool:
            pool.starmap(self._check_seed, [(i, tx) for i in range(max_seed)])
            pool.close()
            pool.join()

class MultiResultVersionCracker(ABC):
    @abstractmethod
    def find(self, tx: multiprocessing.Queue):
        pass

class CollisionCracker(MultiResultVersionCracker):
    def __init__(self, target: int):
        self.target = target

    def _check_seed(self, i: int, tx: multiprocessing.Queue):
        rng_old = BashRandom(i, True)
        rng_old.next_16()  # Setting RANDOM= iterates once
        if rng_old.next_16() == self.target:
            rng_new = BashRandom(i, False)
            rng_new.next_16()
            if rng_new.next_16() == self.target:
                tx.put(i)

    def find(self, tx: multiprocessing.Queue):
        max_seed = 2**30  # Equivalent to u32::MAX / 4
        with Pool() as pool:
            pool.starmap(self._check_seed, [(i, tx) for i in range(max_seed)])
            pool.close()
            pool.join()

class New1Cracker(MultiResultVersionCracker):
    def __init__(self, target: int):
        self.target = target

    def _check_seed(self, i: int, tx: multiprocessing.Queue):
        rng = BashRandom(i, False)
        rng.next_16()  # Setting RANDOM= iterates once
        if rng.next_16() == self.target:
            tx.put(i)

    def find(self, tx: multiprocessing.Queue):
        max_seed = 2**30  # Equivalent to u32::MAX / 4
        with Pool() as pool:
            pool.starmap(self._check_seed, [(i, tx) for i in range(max_seed)])
            pool.close()
            pool.join()

class Old1Cracker(MultiResultVersionCracker):
    def __init__(self, target: int):
        self.target = target

    def _check_seed(self, i: int, tx: multiprocessing.Queue):
        rng = BashRandom(i, True)
        rng.next_16()  # Setting RANDOM= iterates once
        if rng.next_16() == self.target:
            tx.put(i)

    def find(self, tx: multiprocessing.Queue):
        max_seed = 2**31  # Equivalent to u32::MAX / 2
        with Pool() as pool:
            pool.starmap(self._check_seed, [(i, tx) for i in range(max_seed)])
            pool.close()
            pool.join()

if __name__ == "__main__":
    import unittest

    class TestCrackers(unittest.TestCase):
        def test_find_new(self):
            cracker = New3Cracker([24697, 15233, 8710])
            self.assertEqual(cracker.find(), 1337)

        def test_find_old(self):
            cracker = Old3Cracker([24879, 21848, 15683])
            self.assertEqual(cracker.find(), 1337)

    unittest.main()