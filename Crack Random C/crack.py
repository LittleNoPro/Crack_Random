from implement import RandomC

def self_recover(states):
    MOD = 2 ** 32
    length = len(states)

    while True:
        updated = False

        for i in range(34, length):
            s_i = states[i]
            s_31 = states[i - 31]
            s_3 = states[i - 3]

            if s_i is not None and s_3 is not None and s_31 is None:
                states[i - 31] = (s_i - s_3) % MOD
                updated = True

            elif s_i is not None and s_31 is not None and s_3 is None:
                states[i - 3] = (s_i - s_31) % MOD
                updated = True

            elif s_i is None and s_3 is not None and s_31 is not None:
                states[i] = (s_3 + s_31) % MOD
                updated = True

        if not updated:
            break

def crack(outputs):
    states = []

    for i in range(len(outputs)):
        if (i >= 31 and
            outputs[i]      != None and
            outputs[i - 31] != None and
            outputs[i - 3]  != None and
            outputs[i] != (outputs[i - 31] + outputs[i - 3]) & 0x7fffffff
        ):
            states[i - 31] = (outputs[i - 31] << 1) + 1
            states[i - 3]  = (outputs[i - 3]  << 1) + 1
            states.append((outputs[i] << 1) + 0)
        else:
            states.append(None)

    return states

def recover_seed(outputs):
    states = crack(outputs)

    init = [None] * 344

    for i in range(343, 2, -1):
        s31 = states[i + 31 - 344] if i + 31 >= 344 else init[i + 31]
        s28 = states[i + 28 - 344] if i + 28 >= 344 else init[i + 28]
        if s31 is not None and s28 is not None:
            init[i] = (s31 - s28) % 2**32

    for i in range(3):
        init[i] = init[i + 31]

    base_idx = next((i for i in range(31) if init[i] is not None), None)

    if base_idx is not None:
        for i in range(31):
            if init[i] is None:
                init[i] = pow(16807, i - base_idx, 2147483647) * init[base_idx] % 2147483647

    all_states = init + states
    self_recover(all_states)

    print(all_states[:40])

    assert all(s is None or s < 2147483647 for s in all_states[1:31]), "Invalid states"

    return all_states[0] if all_states[0] is not None else None


if __name__ == "__main__":
    rand_gen = RandomC(seed = 1, max_val = 2000)
    outputs = rand_gen.random()
    cracked_seed = recover_seed(outputs)
    print(f"Cracked seed: {cracked_seed}")