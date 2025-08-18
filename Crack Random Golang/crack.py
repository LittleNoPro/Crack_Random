from rng import *
from z3 import *

s = Solver()
NUM_TEST = 700

vec = [BitVec(f'vec_{i}', 64) for i in range(RNG_LEN)]
rng_test = RngSource(vec)
test = [rng_test.uint64() for _ in range(NUM_TEST)]

rng_real = RngSource()
rng_real.seed(0)
real = [rng_real.uint64() for _ in range(NUM_TEST)]

for i in range(NUM_TEST):
    s.add(test[i] == real[i])

print("Solving ...")

if s.check() == sat:
    m = s.model()
    model = s.model()
    array_values = [model.evaluate(vec[i]).as_long() for i in range(RNG_LEN)]
    rng = RngSource(array_values)

    for _ in range(NUM_TEST):
        cur = rng.uint64()

    for _ in range(10):
        print(rng.uint64(), rng_real.uint64())

