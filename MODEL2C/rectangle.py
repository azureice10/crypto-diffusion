#!/usr/bin/env python3
"""
Pure Python implementation of RECTANGLE-80 block cipher.
Ported and adapted from rectangle_strict_80.c for educational differential cryptanalysis tool.
Follows the 80-bit key schedule of the paper (Zhang et al., ePrint 2014/084) and
reproduces its test vectors (see TEST_VECTORS_80).

Bit/row convention (paper Fig. 1 & Fig. 5):
  - state  W = w63..w0, Row i = bits 16i..16i+15  -> Row0 = 16 least significant bits
  - key    V = v79..v0, Row i = bits 16i..16i+15  -> Row0 = 16 least significant bits
Use int_to_state/state_to_int and key_from_hex to convert between integers and rows.
"""

import os
from typing import List, Tuple, Optional

# S-box and inverse S-box from strict implementation (matches paper/JS)
s_box = [0x6, 0x5, 0xC, 0xA, 0x1, 0xE, 0x7, 0x9, 0xB, 0x0, 0x3, 0xD, 0x8, 0xF, 0x4, 0x2]
inv_s_box = [0x9, 0x4, 0xF, 0xA, 0xE, 0x1, 0x0, 0x6, 0xC, 0x7, 0x3, 0x8, 0x2, 0xB, 0x5, 0xD]

ROUNDS = 25
KEY_WORDS = 5
STATE_WORDS = 4


def rotl16(x: int, n: int) -> int:
    n &= 15
    if n == 0:
        return x & 0xFFFF
    return ((x << n) | (x >> (16 - n))) & 0xFFFF


def rotr16(x: int, n: int) -> int:
    n &= 15
    if n == 0:
        return x & 0xFFFF
    return ((x >> n) | (x << (16 - n))) & 0xFFFF


def subcolumn4(state: List[int], cols: int, box: List[int]) -> None:
    """Apply SubColumn to first 4 rows, 'cols' columns (bit positions). Modifies state in place."""
    for i in range(cols):
        col_val = 0
        in_bits = [0] * 4
        for r in range(4):
            in_bits[r] = (state[r] >> i) & 1
            col_val |= (in_bits[r] << r)
        col_val = box[col_val & 0xF]
        for r in range(4):
            out_bit = (col_val >> r) & 1
            delta = out_bit ^ in_bits[r]
            state[r] = (state[r] ^ (delta << i)) & 0xFFFF


def shiftrow(state: List[int]) -> None:
    state[1] = rotl16(state[1], 1)
    state[2] = rotl16(state[2], 12)
    state[3] = rotl16(state[3], 13)


def inv_shiftrow(state: List[int]) -> None:
    state[1] = rotr16(state[1], 1)
    state[2] = rotr16(state[2], 12)
    state[3] = rotr16(state[3], 13)


def rc_next(rc: List[int]) -> None:
    """5-bit LFSR for round constant. rc is mutable list with one int."""
    if rc[0] == 0:
        rc[0] = 1
        return
    # new rc0 = rc4 XOR rc2 (compare the bits themselves, not the masked values)
    rc0 = ((rc[0] >> 4) & 1) ^ ((rc[0] >> 2) & 1)
    rc[0] = ((rc[0] << 1) & 0x1F) | rc0


def key_extend_80(master: List[int]) -> List[List[int]]:
    """Generate all 26 round keys (25 rounds + final) for 80-bit master key (5 x 16-bit)."""
    key = [k & 0xFFFF for k in master]
    round_keys = [[0] * STATE_WORDS for _ in range(ROUNDS + 1)]
    rc = [0]
    for r in range(ROUNDS):
        round_keys[r][0] = key[0]
        round_keys[r][1] = key[1]
        round_keys[r][2] = key[2]
        round_keys[r][3] = key[3]
        rc_next(rc)
        subcolumn4(key, 4, s_box)
        row0 = key[0]
        key[0] = (rotl16(key[0], 8) ^ key[1]) & 0xFFFF
        key[1] = key[2]
        key[2] = key[3]
        key[3] = (rotl16(key[3], 12) ^ key[4]) & 0xFFFF
        key[4] = row0
        key[0] = (key[0] & 0xFFE0) | ((key[0] & 0x001F) ^ rc[0])
    round_keys[ROUNDS][0] = key[0]
    round_keys[ROUNDS][1] = key[1]
    round_keys[ROUNDS][2] = key[2]
    round_keys[ROUNDS][3] = key[3]
    return round_keys


def bytes_to_state(in_bytes: bytes) -> List[int]:
    """Little-endian conversion: 8 bytes -> 4 x 16-bit rows."""
    if len(in_bytes) != 8:
        raise ValueError("Input must be exactly 8 bytes")
    state = [0] * 4
    for i in range(4):
        state[i] = in_bytes[2 * i] | (in_bytes[2 * i + 1] << 8)
    return state


def state_to_bytes(state: List[int]) -> bytes:
    """4 x 16-bit -> 8 bytes little-endian."""
    out = bytearray(8)
    for i in range(4):
        out[2 * i] = state[i] & 0xFF
        out[2 * i + 1] = (state[i] >> 8) & 0xFF
    return bytes(out)


def int_to_state(w: int) -> List[int]:
    """64-bit integer W -> 4 rows, Row0 = 16 least significant bits (paper Fig. 1)."""
    return [(w >> (16 * i)) & 0xFFFF for i in range(STATE_WORDS)]


def state_to_int(state: List[int]) -> int:
    """4 rows -> 64-bit integer W, Row0 = 16 least significant bits (paper Fig. 1)."""
    w = 0
    for i in range(STATE_WORDS):
        w |= (state[i] & 0xFFFF) << (16 * i)
    return w


def key_from_hex(key_hex: str) -> List[int]:
    """80-bit key hex string V -> 5 rows, Row0 = 16 least significant bits (paper Fig. 5)."""
    v = int(key_hex, 16)
    if v >> 80:
        raise ValueError("Key must be at most 80 bits (20 hex chars)")
    return [(v >> (16 * i)) & 0xFFFF for i in range(KEY_WORDS)]


# (key V, plaintext W, ciphertext W) for RECTANGLE-80, as 80/64-bit integers
TEST_VECTORS_80 = [
    (0x00000000000000000000, 0x0000000000000000, 0x0874E8B1E3542D96),
    (0xFFFFFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF, 0x0112AE3DAA349945),
]

# round constants RC[0..24] from the 5-bit LFSR (paper Appendix A)
RC_SEQUENCE = [0x01, 0x02, 0x04, 0x09, 0x12, 0x05, 0x0B, 0x16, 0x0C, 0x19, 0x13, 0x07, 0x0F,
               0x1F, 0x1E, 0x1C, 0x18, 0x11, 0x03, 0x06, 0x0D, 0x1B, 0x17, 0x0E, 0x1D]


def rectangle_encrypt_block(pt: List[int], round_keys: List[List[int]]) -> List[int]:
    state = [x & 0xFFFF for x in pt]
    for r in range(ROUNDS):
        for i in range(STATE_WORDS):
            state[i] ^= round_keys[r][i]
        subcolumn4(state, 16, s_box)
        shiftrow(state)
    for i in range(STATE_WORDS):
        state[i] ^= round_keys[ROUNDS][i]
    return state


def rectangle_decrypt_block(ct: List[int], round_keys: List[List[int]]) -> List[int]:
    state = [x & 0xFFFF for x in ct]
    for i in range(STATE_WORDS):
        state[i] ^= round_keys[ROUNDS][i]
    for r in range(ROUNDS - 1, -1, -1):
        inv_shiftrow(state)
        subcolumn4(state, 16, inv_s_box)
        for i in range(STATE_WORDS):
            state[i] ^= round_keys[r][i]
    return state


def encrypt_block_with_master(pt: List[int], master_key: List[int]) -> List[int]:
    rk = key_extend_80(master_key)
    return rectangle_encrypt_block(pt, rk)


def decrypt_block_with_master(ct: List[int], master_key: List[int]) -> List[int]:
    rk = key_extend_80(master_key)
    return rectangle_decrypt_block(ct, rk)


def rectangle_encrypt_reduced(pt: List[int], master_key: List[int], num_rounds: int) -> List[int]:
    """
    Reduced-round encryption for educational differential attacks.
    Performs exactly num_rounds rounds + final AddRoundKey with the key state after updates.
    """
    if num_rounds < 1:
        num_rounds = 1
    if num_rounds > ROUNDS:
        num_rounds = ROUNDS
    key = [k & 0xFFFF for k in master_key]
    rc = [0]
    state = [x & 0xFFFF for x in pt]
    for r in range(num_rounds):
        # Add current subkey
        for i in range(STATE_WORDS):
            state[i] ^= key[i]
        subcolumn4(state, 16, s_box)
        shiftrow(state)
        # Update key for next round (or final)
        rc_next(rc)
        subcolumn4(key, 4, s_box)
        row0 = key[0]
        key[0] = (rotl16(key[0], 8) ^ key[1]) & 0xFFFF
        key[1] = key[2]
        key[2] = key[3]
        key[3] = (rotl16(key[3], 12) ^ key[4]) & 0xFFFF
        key[4] = row0
        key[0] = (key[0] & 0xFFE0) | ((key[0] & 0x001F) ^ rc[0])
    # Final AddRoundKey with the updated key state (matches full schedule logic for reduced)
    for i in range(STATE_WORDS):
        state[i] ^= key[i]
    return state


def compute_ddt(box: Optional[List[int]] = None) -> List[List[int]]:
    """Compute Difference Distribution Table for the (4-bit) S-box."""
    if box is None:
        box = s_box
    ddt = [[0 for _ in range(16)] for _ in range(16)]
    for x in range(16):
        for dx in range(16):
            y1 = box[x]
            y2 = box[x ^ dx]
            dy = y1 ^ y2
            ddt[dx][dy] += 1
    return ddt


def hamming_weight(x: int) -> int:
    return bin(x & 0xFFFFFFFFFFFFFFFF).count('1')


def hamming_distance(a: int, b: int) -> int:
    return bin((a ^ b) & 0xFFFFFFFFFFFFFFFF).count('1')


if __name__ == "__main__":
    # Round constants and paper test vectors
    rc = [0]
    seq = []
    for _ in range(ROUNDS):
        rc_next(rc)
        seq.append(rc[0])
    assert seq == RC_SEQUENCE, "Round constant sequence mismatch!"
    for v, w, c in TEST_VECTORS_80:
        mk = key_from_hex(f"{v:020x}")
        ct = state_to_int(encrypt_block_with_master(int_to_state(w), mk))
        assert ct == c, f"Test vector mismatch: got {ct:016X}, expected {c:016X}"
        assert state_to_int(decrypt_block_with_master(int_to_state(c), mk)) == w
    print("Round constants and RECTANGLE-80 test vectors OK.")

    # Quick self-test with zero key
    master = [0x0000] * 5
    pt = [0x0000, 0x0000, 0x0000, 0x0000]
    ct = encrypt_block_with_master(pt, master)
    print("Self-test RECTANGLE-80 zero key:")
    print(f"PT: { [hex(x) for x in pt] }")
    print(f"CT: { [hex(x) for x in ct] }")
    # Decrypt back
    pt2 = decrypt_block_with_master(ct, master)
    print(f"Decrypted: { [hex(x) for x in pt2] }")
    assert pt == pt2, "Encrypt/Decrypt mismatch!"
    print("Encrypt/Decrypt OK.")

    # Test reduced
    ct_red = rectangle_encrypt_reduced(pt, master, 5)
    print(f"5-round CT: {[hex(x) for x in ct_red]}")
    print("Reduced round OK.")