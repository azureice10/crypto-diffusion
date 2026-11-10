#!/usr/bin/env python3
"""
Uniform adapters for the primitives compared in this folder.

Every primitive maps an n-bit integer to n bits and exposes trace(x): the state
after round 1..R as integers. One trace therefore feeds the metrics of every
round at once. The adapters call the round functions of the existing tools
(rectangle.py, clefia.py, sparkle.py); test_primitif.py checks that the last
trace state reproduces each tool's own encrypt/permute output.

Final key additions / whitening are omitted from the round trace. This is exact
for differential and avalanche metrics; it preserves linear-correlation
magnitudes (but may flip signs) and cancels in even-sized zero-sum sets. It can
change Hamming-weight statistics, so those are not invariant to whitening.
"""

import copy
import importlib.util
import random
import sys
import numpy as np
from pathlib import Path
from typing import Callable, Dict, List, Optional

HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.pop(0)
    return mod


R = _load("rectangle_core", HERE / "rectangle.py")
C = _load("clefia_core", HERE / "clefia.py")
SP = _load("sparkle_core", HERE / "sparkle.py")


class Primitive:
    """n-bit primitive with R rounds and a per-round trace."""

    def __init__(self, name: str, family: str, n: int, rounds: int, round_unit: str,
                 trace: Callable[[int], List[int]], active4: List[int], active8: List[int],
                 note: str, seed_id: int = 0, derived_from: Optional[str] = None,
                 with_key: Optional[Callable[[int], Callable[[int], List[int]]]] = None,
                 key_bits: int = 0, default_key: int = 0):
        self.name = name
        self.family = family          # structure: SPN, GFN, ARX ...
        self.n = n
        self.rounds = rounds
        self.round_unit = round_unit  # what one "round" means for this primitive
        self.trace = trace
        self.active4 = active4        # 4 input bits aligned to one nonlinear unit
        self.active8 = active8        # 8 input bits aligned to the nonlinear layer
        self.note = note
        self.seed_id = seed_id        # stable seed offset, independent of which primitives are selected
        self.derived_from = derived_from  # id of the big variant whose first steps this slim variant is
        self.with_key = with_key      # key (int) -> trace function, for keyed primitives
        self.key_bits = key_bits
        self.default_key = default_key
        self.batch_trace = None

    def trace_many(self, values):
        """Exact optional batch evaluator; speed benchmarks still use trace()."""
        return self.batch_trace(values) if self.batch_trace else [self.trace(x) for x in values]

    def keyed(self, key: int) -> "Primitive":
        """Copy of this primitive that traces under another key."""
        other = copy.copy(self)
        other.trace = self.with_key(key)
        return other

    def info(self) -> Dict:
        return {"name": self.name, "family": self.family, "n_bits": self.n, "rounds": self.rounds,
                "round_unit": self.round_unit, "note": self.note, "key_bits": self.key_bits}


# ---------------- RECTANGLE-80 ----------------
RECT_KEY = "00010203040506070809"


def make_rectangle_trace(key_hex: str) -> Callable[[int], List[int]]:
    rk = R.key_extend_80(R.key_from_hex(key_hex))

    def trace(x: int) -> List[int]:
        state = R.int_to_state(x)
        out = []
        for r in range(R.ROUNDS):
            for i in range(4):
                state[i] ^= rk[r][i]
            R.subcolumn4(state, 16, R.s_box)
            R.shiftrow(state)
            out.append(R.state_to_int(state))
        return out
    return trace


_rect_rk = R.key_extend_80(R.key_from_hex(RECT_KEY))
rectangle_trace = make_rectangle_trace(RECT_KEY)


# ---------------- CLEFIA-128 ----------------
CLEFIA_KEY = bytes.fromhex("ffeeddccbbaa99887766554433221100")
_clefia_wk, _clefia_rk = C.key_schedule_128(CLEFIA_KEY)


def _words_to_int(w: List[int]) -> int:
    return (w[0] << 96) | (w[1] << 64) | (w[2] << 32) | w[3]


def make_clefia_trace(key: bytes) -> Callable[[int], List[int]]:
    wk, rk = C.key_schedule_128(key)

    def trace(x: int) -> List[int]:
        t = [(x >> s) & 0xFFFFFFFF for s in (96, 64, 32, 0)]   # big-endian words, as clefia.py
        t[1] ^= wk[0]
        t[3] ^= wk[1]
        out = []
        for i in range(C.ROUNDS128):
            t[1] ^= C.f0(rk[2 * i], t[0])
            t[3] ^= C.f1(rk[2 * i + 1], t[2])
            t = [t[1], t[2], t[3], t[0]]
            out.append(_words_to_int(t))
        return out
    return trace


clefia_trace = make_clefia_trace(CLEFIA_KEY)  # native 18-round trace, used for conformance checks


def make_clefia_full_state_trace(key: bytes) -> Callable[[int], List[int]]:
    """Analysis trace sampled every two native CLEFIA rounds (9 full-state units)."""
    native = make_clefia_trace(key)
    return lambda x: native(x)[1::2]


def clefia_byte_bits(b: int) -> List[int]:
    """int bit positions of plaintext byte b (byte 0 = most significant)."""
    lo = 8 * (15 - b)
    return list(range(lo, lo + 8))


# ---------------- Sparkle256 / 384 / 512 ----------------
def make_sparkle_trace(brans: int, steps: int) -> Callable[[int], List[int]]:
    perm = SP.SparklePerm(brans, steps)
    words = 2 * brans

    def trace(x: int) -> List[int]:
        state = [(x >> (32 * i)) & 0xFFFFFFFF for i in range(words)]
        out = []
        for i in range(steps):
            perm._add_round_constants(state, i)
            perm._arxbox_layer(state)
            perm._linear_layer(state)
            out.append(sum(w << (32 * k) for k, w in enumerate(state)))
        return out
    return trace


def make_arx_batch(brans, steps, standalone=False):
    """uint32 vectorization of the unchanged reference operations.

    This changes evaluation scheduling only; it never draws random inputs.
    Inputs and per-round integer states retain the same little-endian layout.
    """
    def rotate(x, count):
        return (x >> count) | (x << (32 - count))

    def evaluate(values):
        values = list(values)
        if not values:
            return []
        width = 2 * brans
        states = np.frombuffer(b"".join(v.to_bytes(width*4,"little") for v in values),
                               dtype="<u4").reshape(len(values),width).copy()
        result = [[] for _ in values]
        def record():
            raw = states.astype("<u4",copy=False).tobytes()
            size=width*4
            for index, trace in enumerate(result):
                trace.append(int.from_bytes(raw[index*size:(index+1)*size],"little"))
        if standalone:
            for r,s in SP.ALZETTE_ROT:
                states[:,0] += rotate(states[:,1],r)
                states[:,1] ^= rotate(states[:,0],s)
                states[:,0] ^= np.uint32(SP.RCON[0])
                record()
            return result
        for step in range(steps):
            states[:,1] ^= np.uint32(SP.RCON[step%8])
            states[:,3] ^= np.uint32(step)
            for j in range(0,width,2):
                for r,s in SP.ALZETTE_ROT:
                    states[:,j] += rotate(states[:,j+1],r)
                    states[:,j+1] ^= rotate(states[:,j],s)
                    states[:,j] ^= np.uint32(SP.RCON[j//2])
            x0,y0 = states[:,0].copy(),states[:,1].copy()
            tx,ty = x0.copy(),y0.copy()
            for j in range(2,brans,2):
                tx ^= states[:,j]
                ty ^= states[:,j+1]
            tx = rotate(tx ^ (tx << 16),16)
            ty = rotate(ty ^ (ty << 16),16)
            for j in range(2,brans,2):
                states[:,j-2] = states[:,j+brans] ^ states[:,j] ^ ty
                states[:,j+brans] = states[:,j]
                states[:,j-1] = states[:,j+brans+1] ^ states[:,j+1] ^ tx
                states[:,j+brans+1] = states[:,j+1]
            states[:,brans-2] = states[:,brans] ^ x0 ^ ty
            states[:,brans] = x0
            states[:,brans-1] = states[:,brans+1] ^ y0 ^ tx
            states[:,brans+1] = y0
            record()
        return result
    return evaluate


SPARKLE_STEPS = SP.OFFICIAL_STEPS[4][1]   # big variant of Sparkle256
sparkle256_trace = make_sparkle_trace(4, SPARKLE_STEPS)


def _xor_whitened_trace(base_trace: Callable[[int], List[int]], n: int, key: int) -> Callable[[int], List[int]]:
    """Experimental keyed wrapper: XOR key before and after the full primitive."""
    mask = (1 << n) - 1
    key &= mask

    def trace(x: int) -> List[int]:
        states = base_trace((x ^ key) & mask)
        if states:
            states[-1] ^= key
        return states
    return trace


def _sparkle(bits: int, slim: bool, seed_id: int = 0) -> Primitive:
    brans = bits // 64
    steps = SP.OFFICIAL_STEPS[brans][0 if slim else 1]
    return Primitive(
        f"Sparkle{bits}" + ("-slim" if slim else ""), "ARX-SPN (permutasi)", bits, steps, "step",
        make_sparkle_trace(brans, steps),
        active4=[0, 1, 2, 3],                          # low bits of x0 (one Alzette)
        active8=list(range(8)),
        note=(f"permutasi Sparkle {'slim' if slim else 'big'} ({steps} step), tanpa kunci"
              + ("; step-nya sama persis dengan awal varian big" if slim else "")),
        seed_id=seed_id, derived_from=f"sparkle{bits}" if slim else None)


# ---------------- Alzette (64-bit ARX-box of Sparkle) ----------------
ALZETTE_C = SP.RCON[0]


def alzette_trace(v: int) -> List[int]:
    x, y = v & 0xFFFFFFFF, v >> 32
    out = []
    for r, s in SP.ALZETTE_ROT:
        x = (x + SP.rot32(y, r)) & 0xFFFFFFFF
        y = (y ^ SP.rot32(x, s)) & 0xFFFFFFFF
        x ^= ALZETTE_C
        out.append((y << 32) | x)
    return out


# seed_id keeps each primitive's random stream stable when others are added or left out
PRIMITIVES = {
    "rectangle": Primitive(
        "RECTANGLE-80", "SPN (bitslice)", 64, R.ROUNDS, "ronde",
        rectangle_trace,
        active4=[0, 16, 32, 48],                      # column 0 = input of one S-box
        active8=[0, 16, 32, 48, 1, 17, 33, 49],       # columns 0 and 1
        note=f"kunci {RECT_KEY}; S-box 4-bit per kolom",
        seed_id=0, with_key=lambda k: make_rectangle_trace(f"{k:020x}"),
        key_bits=80, default_key=int(RECT_KEY, 16)),
    "clefia": Primitive(
        "CLEFIA-128", "GFN 4-cabang", 128, C.ROUNDS128, "ronde asli CLEFIA",
        clefia_trace,
        active4=clefia_byte_bits(4)[:4],               # low nibble of byte 4
        active8=clefia_byte_bits(4),                   # byte 4 = input of one S-box (word 1)
        note="kunci uji resmi ffeedd..00; S-box 8-bit S0/S1",
        seed_id=1, with_key=lambda k: make_clefia_trace(k.to_bytes(16, "big")),
        key_bits=128, default_key=int.from_bytes(CLEFIA_KEY, "big")),
    "sparkle256": _sparkle(256, False, seed_id=2),
    "sparkle256s": _sparkle(256, True),
    "sparkle384": _sparkle(384, False, seed_id=4),
    "sparkle384s": _sparkle(384, True),
    "sparkle512": _sparkle(512, False, seed_id=5),
    "sparkle512s": _sparkle(512, True),
    "alzette": Primitive(
        "Alzette", "ARX-box", 64, 4, "ronde ARX",
        alzette_trace,
        active4=[0, 1, 2, 3],
        active8=list(range(8)),
        note=f"Alzette dengan konstanta tetap c={ALZETTE_C:08x}, tanpa kunci tambahan",
        seed_id=3),
}
for _id, _p in PRIMITIVES.items():
    _p.key = _id
    if _id.startswith("sparkle"):
        _p.batch_trace = make_arx_batch(_p.n // 64, _p.rounds)
    elif _id == "alzette":
        _p.batch_trace = make_arx_batch(1, 4, standalone=True)


def get(names: List[str]) -> List[Primitive]:
    unknown = [n for n in names if n not in PRIMITIVES]
    if unknown:
        raise ValueError(f"primitif tidak dikenal: {unknown}; pilihan: {list(PRIMITIVES)}")
    return [PRIMITIVES[n] for n in names]


def random_input(p: Primitive, rng: random.Random) -> int:
    return rng.getrandbits(p.n)
