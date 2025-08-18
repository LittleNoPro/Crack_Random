from rand import new_source, new
from rng import RngSource, RNG_LEN
from tqdm import trange
from z3 import *

s = Solver()
NUM_TEST = 700

vec = [BitVec(f'vec_{i}', 64) for i in range(RNG_LEN)]
rng = RngSource(vec)
psudo_rand = new(rng)
test = [psudo_rand.uint64() for _ in range(NUM_TEST)]

src = new_source(123843)
hehe = list(src.vec)
rand = new(src)
real = [rand.uint64() for _ in range(NUM_TEST)]

for i in trange(NUM_TEST):
    s.add(real[i] == test[i])

print("solve......")
if s.check() == sat:
    model = s.model()
    array_values = [model.evaluate(vec[i]).as_long() for i in range(RNG_LEN)]
    rng = RngSource(array_values)
    print(f"{hehe[:10] = }")
    print(f"{rng.vec[:10] = }")

    test_rand = new(rng)
    test = [test_rand.uint64() for _ in range(NUM_TEST)]
    for i in range(20):
        print(test_rand.uint64(), rand.uint64())