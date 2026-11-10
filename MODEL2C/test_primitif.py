#!/usr/bin/env python3
"""
The adapters must reproduce the original tools exactly.
Run: python test_primitif.py   (or: python -m pytest test_primitif.py)
"""

import random
import metrik as M
import primitif as P


def test_rectangle_matches_tool():
    rng = random.Random(1)
    mk = P.R.key_from_hex(P.RECT_KEY)
    for _ in range(20):
        x = rng.getrandbits(64)
        last = P.rectangle_trace(x)[-1]
        k25 = P.R.state_to_int(P._rect_rk[P.R.ROUNDS])
        assert last ^ k25 == P.R.state_to_int(P.R.encrypt_block_with_master(P.R.int_to_state(x), mk))
        # reduced rounds of the tool use the same round function
        for r in (1, 3, 6):
            red = P.R.state_to_int(P.R.rectangle_encrypt_reduced(P.R.int_to_state(x), mk, r))
            assert P.rectangle_trace(x)[r - 1] ^ P.R.state_to_int(P._rect_rk[r]) == red


def test_clefia_matches_tool():
    rng = random.Random(2)
    for _ in range(20):
        x = rng.getrandbits(128)
        tr = P.clefia_trace(x)
        for r in (1, 5, 18):
            w = [(tr[r - 1] >> s) & 0xFFFFFFFF for s in (96, 64, 32, 0)]
            y = [w[3], w[0], w[1], w[2]]          # undo last rotation, as gfn4
            y[1] ^= P._clefia_wk[2]
            y[3] ^= P._clefia_wk[3]
            ct = P.C.encrypt_block(x.to_bytes(16, "big"), P.CLEFIA_KEY, r)
            assert P._words_to_int(y) == int.from_bytes(ct, "big")


def test_sparkle_matches_tool():
    rng = random.Random(3)
    for _ in range(10):
        x = rng.getrandbits(256)
        state = [(x >> (32 * i)) & 0xFFFFFFFF for i in range(8)]
        for steps in (1, 4, 10):
            ref = P.SP.SparklePerm(4, steps).permute(state[:])
            assert P.sparkle256_trace(x)[steps - 1] == sum(w << (32 * k) for k, w in enumerate(ref))


def test_alzette_matches_tool():
    rng = random.Random(4)
    for _ in range(50):
        v = rng.getrandbits(64)
        for r in range(1, 5):
            x, y = P.SP.alzette(v & 0xFFFFFFFF, v >> 32, P.ALZETTE_C, r)
            assert P.alzette_trace(v)[r - 1] == (y << 32) | x


def test_other_keys_match_tools():
    rng = random.Random(5)
    for _ in range(10):
        k80, k128, x64, x128 = rng.getrandbits(80), rng.getrandbits(128), rng.getrandbits(64), rng.getrandbits(128)
        rect = P.PRIMITIVES["rectangle"].keyed(k80)
        rows = P.R.key_from_hex(f"{k80:020x}")
        rk = P.R.key_extend_80(rows)
        ct = P.R.state_to_int(P.R.encrypt_block_with_master(P.R.int_to_state(x64), rows))
        assert rect.trace(x64)[-1] ^ P.R.state_to_int(rk[P.R.ROUNDS]) == ct
        clefia = P.PRIMITIVES["clefia"].keyed(k128)
        key = k128.to_bytes(16, "big")
        wk, _ = P.C.key_schedule_128(key)
        w = [(clefia.trace(x128)[-1] >> s) & 0xFFFFFFFF for s in (96, 64, 32, 0)]
        y = [w[3], w[0] ^ wk[2], w[1], w[2] ^ wk[3]]
        assert P._words_to_int(y) == int.from_bytes(P.C.encrypt_block(x128.to_bytes(16, "big"), key), "big")


def test_sparkle_family_matches_tool():
    rng = random.Random(6)
    for key, brans in (("sparkle384", 6), ("sparkle512", 8)):
        p = P.PRIMITIVES[key]
        for _ in range(5):
            x = rng.getrandbits(p.n)
            state = [(x >> (32 * i)) & 0xFFFFFFFF for i in range(2 * brans)]
            ref = P.SP.SparklePerm(brans, p.rounds).permute(state[:])
            assert p.trace(x)[-1] == sum(w << (32 * i) for i, w in enumerate(ref))


def test_slim_is_prefix_of_big():
    rng = random.Random(7)
    for p in P.PRIMITIVES.values():
        if p.derived_from:
            big = P.PRIMITIVES[p.derived_from]
            assert p.n == big.n and p.rounds < big.rounds
            x = rng.getrandbits(p.n)
            assert p.trace(x) == big.trace(x)[:p.rounds]


def test_horizon_ignores_isolated_detections():
    rows = [{"round": r, "hit": r in (1, 2, 11)} for r in range(1, 26)]
    detected = lambda row: row["hit"]
    assert M.horizon(rows, detected) == 2
    assert M.isolated(rows, detected) == [11]
    assert M.horizon([{"round": 1, "hit": False}, {"round": 2, "hit": True}], detected) is None


def test_zero_rate_of_a_known_map():
    # identity map: every bit is zero-sum in every coset of 2^k texts
    identity = P.Primitive("id", "-", 64, 1, "-", lambda x: [x], [0, 1], [0, 1], "-")
    rows = M.zero_sum(identity, [0, 1], 4, random.Random(1))
    assert rows[0]["balanced_bits"] == 64 and rows[0]["zero_rate_max"] == 1.0
    assert (rows[0]["zero_rates"] == 1.0).all()


def test_corrected_statistics():
    import math
    import statistics
    import numpy as np
    a, b = [0, 0, 1, 2, 2, 2], [4, 3, 3, 1, 1, 0]
    assert math.isclose(M.spearman(a, b), statistics.correlation(a, b, method="ranked"))
    assert M.spearman([0, 0, 0], [1, 2, 3]) is None
    assert M.spearman(a[::-1], b[::-1]) == M.spearman(a, b)
    pv = M.binomial_pvalues(64)
    exact_q = sum(math.comb(64, k) / 2**64 for k in range(65) if pv[k] < .001)
    assert math.isclose(exact_q, 0.0006173782640671298)
    # Large sample sizes must not overflow or lose the two-sided symmetry.
    big = M.binomial_pvalues(8192)
    assert np.isfinite(big).all() and np.allclose(big, big[::-1]) and big[4096] == 1


def test_official_vectors_and_scope():
    for key, pt, ct in P.R.TEST_VECTORS_80:
        rows = P.R.key_from_hex(f"{key:020x}")
        assert P.R.state_to_int(P.R.encrypt_block_with_master(P.R.int_to_state(pt), rows)) == ct
    pt = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    assert P.C.encrypt_block(pt, P.CLEFIA_KEY).hex() == "de2bf2fd9b74aacdf1298555459494fd"
    assert P.PRIMITIVES["clefia"].rounds == 18
    assert len(P.PRIMITIVES["clefia"].trace(0)) == 18
    assert P.make_clefia_full_state_trace(P.CLEFIA_KEY)(0) == P.clefia_trace(0)[1::2]
    assert {key for key, p in P.PRIMITIVES.items() if p.with_key} == {"rectangle", "clefia"}


def test_batch_traces_match_scalar_reference():
    rng = random.Random(99)
    for p in P.PRIMITIVES.values():
        inputs = [0, (1 << p.n) - 1] + [rng.getrandbits(p.n) for _ in range(10)]
        assert p.trace_many([]) == []
        assert p.trace_many(inputs) == [p.trace(x) for x in inputs]
        assert p.trace_many([inputs[0], inputs[0]]) == [p.trace(inputs[0])] * 2


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"{name}: OK")
    print("All tests passed.")
