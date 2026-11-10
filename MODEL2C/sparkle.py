#!/usr/bin/env python3
"""
Pure Python implementation of the SPARKLE permutation family.
Ported from the reference C implementation in cryptolu/sparkle; verified
against itzmeanjan/sparkle (see test_sparkle.py).
Supports Sparkle256 (brans=4), Sparkle384 (brans=6), Sparkle512 (brans=8).
State is represented as list of 2*brans 32-bit integers (little-endian words).
"""

import struct
from typing import List, Tuple, Optional

# Round constants (same as C)
RCON = [
    0xB7E15162, 0xBF715880, 0x38B4DA56, 0x324E7738,
    0xBB1185EB, 0x4F7C7B57, 0xCFBFA1C8, 0xC2B3293D
]

MAX_BRANCHES = 8

# Official (slim, big) step counts per branch count, table 2.1 of the spec
OFFICIAL_STEPS = {4: (7, 10), 6: (7, 11), 8: (8, 12)}

def rot32(x: int, n: int) -> int:
    """32-bit right rotation."""
    x &= 0xFFFFFFFF
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

def ell32(x: int) -> int:
    """ELL linear function."""
    x &= 0xFFFFFFFF
    return rot32((x ^ ((x << 16) & 0xFFFFFFFF)), 16)

# (r, s) rotation pairs of the four ARX rounds of Alzette
ALZETTE_ROT = ((31, 24), (17, 17), (0, 31), (24, 16))

def alzette(x: int, y: int, c: int, rounds: int = 4) -> Tuple[int, int]:
    """
    Alzette ARX-box (64-bit, constant c), optionally reduced to 1..4 rounds.
    rounds=4 is the full Alzette used in each branch of the ARXBOX layer.
    """
    if not 1 <= rounds <= 4:
        raise ValueError("Alzette rounds must be 1..4")
    for r, s in ALZETTE_ROT[:rounds]:
        x = (x + rot32(y, r)) & 0xFFFFFFFF
        y = (y ^ rot32(x, s)) & 0xFFFFFFFF
        x ^= c
    return x, y

class SparklePerm:
    """
    Sparkle Permutation.
    Args:
        brans: number of branches (4 for 256-bit, 6 for 384-bit, 8 for 512-bit)
        steps: number of steps (official slim/big: Sparkle256 7/10,
               Sparkle384 7/11, Sparkle512 8/12; any steps >= 1 is allowed
               for reduced-round analysis)
    """
    def __init__(self, brans: int = 4, steps: int = 10):
        if brans not in OFFICIAL_STEPS:
            raise ValueError("brans must be 4, 6 or 8")
        if not (isinstance(steps, int) and steps >= 1):
            raise ValueError("steps must be an integer >= 1")
        self.brans = brans
        self.steps = steps
        self.state_size_bits = 32 * 2 * brans  # e.g. 256 for brans=4

    def _add_round_constants(self, state: List[int], step_idx: int):
        state[1] = (state[1] ^ RCON[step_idx % MAX_BRANCHES]) & 0xFFFFFFFF
        state[3] = (state[3] ^ step_idx) & 0xFFFFFFFF

    def _arxbox_layer(self, state: List[int]):
        for j in range(0, 2 * self.brans, 2):
            rc = RCON[j >> 1]
            # 4 ARX sub-steps (ported exactly from C)
            state[j] = (state[j] + rot32(state[j+1], 31)) & 0xFFFFFFFF
            state[j+1] = (state[j+1] ^ rot32(state[j], 24)) & 0xFFFFFFFF
            state[j] = (state[j] ^ rc) & 0xFFFFFFFF

            state[j] = (state[j] + rot32(state[j+1], 17)) & 0xFFFFFFFF
            state[j+1] = (state[j+1] ^ rot32(state[j], 17)) & 0xFFFFFFFF
            state[j] = (state[j] ^ rc) & 0xFFFFFFFF

            state[j] = (state[j] + state[j+1]) & 0xFFFFFFFF
            state[j+1] = (state[j+1] ^ rot32(state[j], 31)) & 0xFFFFFFFF
            state[j] = (state[j] ^ rc) & 0xFFFFFFFF

            state[j] = (state[j] + rot32(state[j+1], 24)) & 0xFFFFFFFF
            state[j+1] = (state[j+1] ^ rot32(state[j], 16)) & 0xFFFFFFFF
            state[j] = (state[j] ^ rc) & 0xFFFFFFFF

    def _linear_layer(self, state: List[int]):
        tmpx = x0 = state[0]
        tmpy = y0 = state[1]
        for j in range(2, self.brans, 2):
            tmpx ^= state[j]
            tmpy ^= state[j + 1]
        tmpx = ell32(tmpx)
        tmpy = ell32(tmpy)

        for j in range(2, self.brans, 2):
            state[j-2] = (state[j + self.brans] ^ state[j] ^ tmpy) & 0xFFFFFFFF
            state[j + self.brans] = state[j]
            state[j-1] = (state[j + self.brans + 1] ^ state[j + 1] ^ tmpx) & 0xFFFFFFFF
            state[j + self.brans + 1] = state[j + 1]

        state[self.brans - 2] = (state[self.brans] ^ x0 ^ tmpy) & 0xFFFFFFFF
        state[self.brans] = x0
        state[self.brans - 1] = (state[self.brans + 1] ^ y0 ^ tmpx) & 0xFFFFFFFF
        state[self.brans + 1] = y0

    def permute(self, state: List[int]) -> List[int]:
        """
        Apply the Sparkle permutation to the state (in-place modification, returns it too).
        state: list of 2*brans uint32 values.
        """
        if len(state) != 2 * self.brans:
            raise ValueError(f"State must have {2*self.brans} words for brans={self.brans}")
        for i in range(len(state)):
            state[i] &= 0xFFFFFFFF  # ensure 32-bit, keep the same list object

        for i in range(self.steps):
            self._add_round_constants(state, i)
            self._arxbox_layer(state)
            self._linear_layer(state)
        return state

    def permute_bytes(self, data: bytes) -> bytes:
        """Convenience: input/output as bytes (little-endian 32-bit words)."""
        if len(data) != (2 * self.brans * 4):
            raise ValueError(f"Input must be exactly {2*self.brans*4} bytes for this variant")
        state = self.permute(list(struct.unpack('<' + 'I' * (2 * self.brans), data)))
        return struct.pack('<' + 'I' * (2 * self.brans), *state)

    def __call__(self, state: List[int]) -> List[int]:
        return self.permute(state)

    def is_official(self) -> bool:
        return self.steps in OFFICIAL_STEPS[self.brans]

    def get_info(self) -> str:
        return f"SparklePerm(brans={self.brans}, steps={self.steps}, state_bits={self.state_size_bits})"

# Example usage / test
if __name__ == "__main__":
    # Test with Sparkle256 slim-ish (small steps for demo)
    perm = SparklePerm(brans=4, steps=4)  # reduced for quick test
    state = [0x12345678, 0x9abcdef0, 0x11223344, 0x55667788,
             0xaabbccdd, 0xeeff0011, 0x22334455, 0x66778899]
    print("Initial state:", [hex(x) for x in state])
    out = perm.permute(state[:])  # copy
    print("After permute:", [hex(x) for x in out])
    print(perm.get_info())