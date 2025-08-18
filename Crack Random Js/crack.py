import sys
from implement import MathRandom
from gf2bv import LinearSystem, BitVec
import struct

def v8_from_double(double):
    """
    Convert a double back to a 64-bit integer.
    The 12 least significant bits of the result cannot be recovered.
    """
    if double == 1.0:
        return 0xffffffffffffffff
    return (struct.unpack('<Q', struct.pack('d', double + 1.0))[0] & 0xfffffffffffff)

numbers = [
    0.20850633840727073,
    0.28382289045651743,
    0.4071416957057805,
    0.3101367279739642,
    0.6813711566813534,
    0.8365880507655776,
    0.2238039081275922,
    0.014754643967695324,
    0.44290438850282876,
    0.5473214381957232,
    0.40023560591139606,
    0.14837298522461473,
    0.12321774476187275,
    0.8501766788936596,
    0.9212308144118708,
    0.8099337802981195,
    0.06047989985671265,
    0.6552969701254443,
    0.5803218168252511,
    0.41915921494443964,
    0.9153038363744563,
    0.7403989120318095,
    0.6630141727527132,
    0.5230661117641415
]

lin = LinearSystem([64] * 2)
state0, state1 = lin.gens()

Random = MathRandom(state0, state1, True)

out = [Random.next() for _ in range(len(numbers))]

zeros = [(v8_from_double(numbers[i]) | 0x3ff0000000000000) ^ out[i] for i in range(len(numbers))]

print("solving...")
sol = lin.solve_one(zeros)

print(sol)