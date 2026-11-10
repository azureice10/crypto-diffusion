#!/usr/bin/env python3
"""
Metrics computed identically for every primitive, per round.

All per-round metrics take traces (state after round 1..R). Corrected p-values
use an ideal random-permutation null, coupled to fresh independent random
labels. The collision correction bounds the finite-domain approximation;
this does not assert equal test power across state sizes or metric families.
"""

import math
import random
from collections import Counter
from functools import lru_cache
from typing import Dict, List, Optional

import numpy as np

from primitif import Primitive


# ---------------- helpers ----------------
def to_bits(values: List[int], n: int) -> np.ndarray:
    """ints -> (len, n) uint8 array, column j = bit j."""
    nb = n // 8
    buf = b"".join(v.to_bytes(nb, "little") for v in values)
    arr = np.frombuffer(buf, dtype=np.uint8).reshape(len(values), nb)
    return np.unpackbits(arr, axis=1, bitorder="little")


def z_crit(p: float) -> float:
    """two-sided normal quantile: P(|Z| > z) = p."""
    lo, hi = 0.0, 40.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if math.erfc(mid / math.sqrt(2)) > p:
            lo = mid
        else:
            hi = mid
    return hi


def popcount(x: int) -> int:
    return bin(x).count("1")


# ---------------- nonlinear unit (S-box) ----------------
def sbox_properties(name: str, S: List[int], n: int) -> Dict:
    N = 1 << n
    ddt_max = 0
    for dx in range(1, N):
        cnt = Counter(S[x] ^ S[x ^ dx] for x in range(N))
        ddt_max = max(ddt_max, max(cnt.values()))
    # linear approximation table: W[a, b] = sum over x of (-1)^(a.x + b.S(x)), for b != 0
    sign = np.array([1 - 2 * (popcount(v) & 1) for v in range(N)], dtype=np.int64)
    idx = np.arange(N)
    input_chars = sign[np.bitwise_and.outer(idx, idx)]            # [a, x]
    output_chars = sign[np.bitwise_and.outer(idx, np.array(S))]   # [b, x]
    lat_max = int(np.abs(input_chars @ output_chars[1:].T).max())
    # algebraic degree via Moebius transform of each coordinate
    degree = 0
    for bit in range(n):
        f = [(S[x] >> bit) & 1 for x in range(N)]
        for i in range(n):
            for x in range(N):
                if x & (1 << i):
                    f[x] ^= f[x ^ (1 << i)]
        degree = max(degree, max((popcount(x) for x in range(N) if f[x]), default=0))
    return {
        "sbox": name, "bits": n,
        "bijective": sorted(S) == list(range(N)),
        "differential_uniformity": ddt_max,
        "max_dp_log2": round(math.log2(ddt_max / N), 3),
        "linearity": lat_max,
        "nonlinearity": (N - lat_max) // 2,
        "max_correlation_log2": round(math.log2(lat_max / N), 3),
        "algebraic_degree": degree,
        "fixed_points": sum(S[x] == x for x in range(N)),
    }


# ---------------- avalanche / SAC / diffusion completeness ----------------
@lru_cache(maxsize=32)
def binomial_mass(samples: int) -> np.ndarray:
    if samples < 1:
        raise ValueError("samples must be positive")
    logmass = [math.lgamma(samples + 1) - math.lgamma(k + 1)
               - math.lgamma(samples - k + 1) - samples * math.log(2)
               for k in range(samples + 1)]
    mass = np.exp(logmass)
    return mass / mass.sum()


@lru_cache(maxsize=32)
def binomial_pvalues(samples: int) -> np.ndarray:
    """exact two-sided binomial p-value of every possible flip count under SAC (p = 1/2)."""
    cdf = np.cumsum(binomial_mass(samples))
    # Symmetry avoids cancellation in the upper tail and overflow at N >= 1024.
    return np.minimum(1.0, 2 * cdf[np.minimum(np.arange(samples + 1),
                                             samples - np.arange(samples + 1))])


def null_coupling_bound(n: int, queries: int) -> float:
    """Conservative sum of input-overlap and output-collision union bounds.

    For avalanche stars, overlaps within a star are impossible and between
    stars have probability <= (n+1)^2/2^n. Q^2/2^n covers that union plus
    the random-function/random-permutation switching bound. Used only where
    the sampling geometry satisfies this argument, not as a generic theorem.
    """
    return min(1.0, math.ldexp(float(queries * queries), -n))


def avalanche(p: Primitive, samples: int, rng: random.Random, alpha: float = 1e-3) -> List[Dict]:
    n, R = p.n, p.rounds
    flips = np.zeros((R, n, n), dtype=np.int32)   # [round, input bit, output bit]
    for _ in range(samples):
        x = rng.getrandbits(n)
        traces = p.trace_many([x] + [x ^ (1 << i) for i in range(n)])
        base = traces[0]
        diffs = [[] for _ in range(R)]
        for i in range(n):
            t = traces[i + 1]
            for r in range(R):
                diffs[r].append(base[r] ^ t[r])
        for r in range(R):
            flips[r] += to_bits(diffs[r], n)
    pval = binomial_pvalues(samples)
    pairs = n * n
    q_effective = float(binomial_mass(samples)[pval < alpha].sum())
    coupling = null_coupling_bound(n, samples * (n + 1))
    rows = []
    for r in range(R):
        f = flips[r] / samples
        viol = int((pval[flips[r]] < alpha).sum())
        rows.append({
            "round": r + 1,
            "avalanche_mean": float(f.mean()),                  # ideal 0.5
            "avalanche_min_input_bit": float(f.mean(axis=1).min()),
            "completeness": float((flips[r] > 0).mean()),       # fraction of (in,out) bit pairs that ever flip
            "sac_max_dev": float(np.abs(f - 0.5).max()),
            "sac_violation_frac": viol / pairs,                 # pairs with p < alpha (chance level = alpha)
            "sac_violations": viol,
            "sac_effective_alpha": q_effective,
            "sac_null_coupling_bound": coupling,
            "sac_p_value_legacy": binom_tail(pairs, alpha, viol),
            "sac_p_value": min(1.0, binom_tail(pairs, q_effective, viol) + coupling),
            "sac_bonferroni_p": min(1.0, pairs * float(pval[flips[r]].min()) + coupling),
        })
    return rows


def key_avalanche(p: Primitive, samples: int, rng: random.Random, alpha: float = 1e-3) -> List[Dict]:
    """Avalanche of the key: flip one key bit at a time, random key and plaintext per sample."""
    n, R, kb = p.n, p.rounds, p.key_bits
    flips = np.zeros((R, kb, n), dtype=np.int32)   # [round, key bit, output bit]
    for _ in range(samples):
        key, x = rng.getrandbits(kb), rng.getrandbits(n)
        base = p.with_key(key)(x)
        diffs = [[] for _ in range(R)]
        for i in range(kb):
            t = p.with_key(key ^ (1 << i))(x)
            for r in range(R):
                diffs[r].append(base[r] ^ t[r])
        for r in range(R):
            flips[r] += to_bits(diffs[r], n)
    pval = binomial_pvalues(samples)
    pairs = kb * n
    q_effective = float(binomial_mass(samples)[pval < alpha].sum())
    rows = []
    for r in range(R):
        viol = int((pval[flips[r]] < alpha).sum())
        rows.append({
            "round": r + 1,
            "key_avalanche_mean": float((flips[r] / samples).mean()),
            "key_completeness": float((flips[r] > 0).mean()),
            "key_sac_violation_frac": viol / pairs,
            "key_sac_p_value_legacy": binom_tail(pairs, alpha, viol),
            # Ideal independent keyed-permutation family; this is a related-key
            # trace statistic, not a claim about a standardized key schedule.
            "key_sac_p_value": min(1.0, binom_tail(pairs, q_effective, viol)
                                    + null_coupling_bound(min(n, kb), samples * (kb + 1))),
        })
    return rows


# ---------------- single-bit linear correlation ----------------
def linear_single_bit(p: Primitive, samples: int, rng: random.Random, alpha: float = 1e-3,
                      keep_rounds=()):
    """Returns (rows per round, {round: +-1 output matrix}) for the last round and keep_rounds."""
    n, R = p.n, p.rounds
    xs = [rng.getrandbits(n) for _ in range(samples)]
    traces = p.trace_many(xs)
    X = to_bits(xs, n).astype(np.float64) * 2 - 1
    zc = z_crit(alpha / (n * n))
    exact_p = binomial_pvalues(samples)
    coupling = null_coupling_bound(n, samples)
    keep = set(keep_rounds) | {R}
    rows, kept = [], {}
    for r in range(R):
        Y = to_bits([t[r] for t in traces], n).astype(np.float64) * 2 - 1
        corr = X.T @ Y / samples
        z = np.abs(corr) * math.sqrt(samples)
        counts = np.rint((corr + 1) * samples / 2).astype(int)
        adjusted = np.minimum(1.0, n * n * exact_p[counts] + coupling)
        sig = adjusted < alpha
        mx = float(np.abs(corr).max())
        rows.append({
            "round": r + 1,
            "lin_max_abs_corr": mx,
            "lin_max_corr_log2": round(math.log2(mx), 3) if mx > 0 else None,
            "lin_sig_pairs": int(sig.sum()),
            "lin_sig_pairs_legacy": int((z > zc).sum()),
            "lin_bonferroni_p": float(adjusted.min()),
            "lin_sig_frac": float(sig.mean()),
            "lin_noise_level": zc / math.sqrt(samples),
        })
        if r + 1 in keep:
            kept[r + 1] = Y
    return rows, kept


# ---------------- empirical differential ----------------
def input_differences(p: Primitive) -> Dict[str, int]:
    """single-bit difference at bit 0, one active nonlinear unit (4 bits), and 8 aligned bits."""
    return {
        "1 bit": 1 << p.active4[0],
        "1 unit (4 bit)": sum(1 << b for b in p.active4),
        "8 bit selaras": sum(1 << b for b in p.active8),
    }


def differential(p: Primitive, pairs: int, rng: random.Random) -> List[Dict]:
    """per round and input difference: multiplicity of the most frequent output difference.
    A random n-bit map repeats a fixed output difference with prob ~2^-n, so >= 3 hits is a bias."""
    R = p.rounds
    rows = []
    per_round_best = [None] * R
    for label, dx in input_differences(p).items():
        counters = [Counter() for _ in range(R)]
        xs = [rng.getrandbits(p.n) for _ in range(pairs)]
        traces = p.trace_many([v for x in xs for v in (x,x^dx)])
        for index in range(pairs):
            a, b = traces[2*index:2*index+2]
            for r in range(R):
                counters[r][a[r] ^ b[r]] += 1
        for r in range(R):
            dy, cnt = counters[r].most_common(1)[0]
            rows.append({
                "round": r + 1, "input_diff": label, "dx_hex": hex(dx),
                "top_dy_count": cnt, "distinct_dy_frac": len(counters[r]) / pairs,
                "dp_log2": round(math.log2(cnt / pairs), 3) if cnt >= 3 else None,
                "top_dy_hw": popcount(dy),
                # Each triple of distinct unordered dx pairs can share dy
                # with probability <= 1/((2^n-3)(2^n-5)). Union over triples
                # and the three predefined dx patterns, plus input reuse.
                "diff_null_p_bound": min(1.0, len(input_differences(p)) *
                    (math.comb(pairs, 3) / ((2 ** p.n - 3) * (2 ** p.n - 5))
                     + math.comb(pairs, 2) * 2 / 2 ** p.n)) if cnt >= 3 else 1.0,
            })
            best = per_round_best[r]
            if best is None or cnt > best["top_dy_count"]:
                per_round_best[r] = rows[-1]
    return rows, per_round_best


# ---------------- zero-sum (integral) ----------------
def zero_sum(p: Primitive, active: List[int], cosets: int, rng: random.Random) -> List[Dict]:
    n, R = p.n, p.rounds
    amask = sum(1 << b for b in active)
    full = (1 << n) - 1
    balanced = [full] * R
    zero_counts = np.zeros((R, n), dtype=np.int64)   # per output bit: cosets with XOR-sum 0
    for _ in range(cosets):
        base = rng.getrandbits(n) & ~amask
        acc = [0] * R
        inputs = []
        for i in range(1 << len(active)):
            x = base
            for j, b in enumerate(active):
                if (i >> j) & 1:
                    x |= 1 << b
            inputs.append(x)
        for t in p.trace_many(inputs):
            for r in range(R):
                acc[r] ^= t[r]
        for r in range(R):
            balanced[r] &= ~acc[r] & full
            zero_counts[r] += 1 - to_bits([acc[r]], n)[0].astype(np.int64)
    q = 2.0 ** -cosets    # a random bit is zero-sum in every coset with prob 2^-cosets
    # Distinct cosets have distinct inputs. Duplicate cosets are covered by
    # this union bound; iid-output/permutation switching contributes the rest.
    coupling = min(1.0, math.comb(cosets, 2) / 2 ** (n - len(active))
                   + math.comb(cosets * (1 << len(active)), 2) / 2 ** n)
    rows = []
    for r in range(R):
        m = popcount(balanced[r])
        rows.append({"round": r + 1, "active_bits": len(active), "balanced_bits": m,
                     "balanced_frac": m / n, "expected_false_pos": n * q,
                     "p_value_legacy": binom_tail(n, q, m),
                     "p_value": min(1.0, binom_tail(n, q, m) + coupling),
                     "markov_p_bound": min(1.0, n * q / m + coupling) if m else 1.0,
                     "null_coupling_bound": coupling,
                     # a bit can be zero-sum in nearly all cosets without being a certainty
                     "zero_rate_max": float(zero_counts[r].max() / cosets),
                     "zero_rates": zero_counts[r] / cosets,
                     "balanced_positions": [i for i in range(n) if (balanced[r] >> i) & 1]})
    return rows


def binom_tail(n: int, q: float, m: int) -> float:
    """P[Binomial(n, q) >= m]."""
    if m <= 0:
        return 1.0
    if q <= 0:
        return 0.0
    lq, l1q, lnf = math.log(q), math.log1p(-q), math.lgamma(n + 1)

    def term(i):
        return math.exp(lnf - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lq + (n - i) * l1q)

    if m <= n * q:   # body of the distribution: 1 - lower tail is cheaper
        return max(0.0, 1.0 - sum(term(i) for i in range(m)))
    total, i = 0.0, m
    while i <= n:    # terms shrink geometrically past the mean
        t = term(i)
        total += t
        if t == 0.0 or t < total * 1e-16:
            break
        i += 1
    return min(1.0, total)


# ---------------- randomness at full rounds ----------------
def full_round_randomness(Y: np.ndarray, alpha: float = 1e-3) -> Dict:
    """Y: (N, n) +-1 matrix of full-round outputs for random inputs."""
    N, n = Y.shape
    bits = (Y > 0).astype(np.uint8)
    ones = bits.sum(axis=0)
    z_bal = np.abs(ones - N / 2) / (math.sqrt(N) / 2)
    corr = np.corrcoef(Y, rowvar=False)
    np.fill_diagonal(corr, 0)
    m = n * (n - 1) // 2
    byte_vals = np.packbits(bits, axis=1, bitorder="little").ravel()
    hist = np.bincount(byte_vals, minlength=256) / byte_vals.size
    ent = float(-(hist[hist > 0] * np.log2(hist[hist > 0])).sum())
    hw = bits.sum(axis=1)
    return {
        "bit_balance_max_z": float(z_bal.max()),
        "bit_balance_z_crit": z_crit(alpha / n),
        "bit_corr_max_abs": float(np.abs(corr).max()),
        "bit_corr_z_crit_level": z_crit(alpha / m) / math.sqrt(N),
        "byte_entropy": ent,
        "byte_observations": int(byte_vals.size),
        "byte_entropy_by_position_mean": float(np.mean([
            -(lambda h: (h[h > 0] * np.log2(h[h > 0])).sum())(
                np.bincount(col, minlength=256) / N)
            for col in np.packbits(bits, axis=1, bitorder="little").T])),
        "byte_entropy_max_possible": math.log2(min(256, byte_vals.size)),
        "hw_mean": float(hw.mean()), "hw_ideal": n / 2,
        "hw_std": float(hw.std()), "hw_std_ideal": math.sqrt(n) / 2,
    }


# ---------------- horizons and relationships ----------------
def horizon(rows: List[Dict], detected) -> Optional[int]:
    """Last round of the unbroken run of detections from round 1 (None = round 1 not detected).
    These properties fade with the rounds, and with many tests a few false positives are
    expected, so a detection after a gap must not extend the horizon; see isolated()."""
    last = None
    for row in rows:
        if not detected(row):
            break
        last = row["round"]
    return last


def isolated(rows: List[Dict], detected) -> List[int]:
    """Rounds detected beyond the horizon: candidates for false positives, to be checked separately."""
    h = horizon(rows, detected) or 0
    return [row["round"] for row in rows if row["round"] > h and detected(row)]


def first_round(rows: List[Dict], cond) -> Optional[int]:
    for row in rows:
        if cond(row):
            return row["round"]
    return None


def resample_with_start(curve: List[float], start: float, points: int) -> np.ndarray:
    """curve over rounds 1..R -> values on the normalized grid r/R in [0, 1];
    round 0 takes `start`, the value of the untouched input."""
    R = len(curve)
    xs = np.arange(0, R + 1) / R
    return np.interp(np.linspace(0, 1, points), xs, np.asarray([start] + curve, dtype=float))


def curve_similarity(curves: Dict[str, List[float]], starts: Dict[str, float], points: int = 21) -> Dict:
    """pairwise Pearson correlation and RMS distance of curves on the normalized round axis."""
    names = list(curves)
    res = {nm: resample_with_start(c, starts[nm], points) for nm, c in curves.items()}
    pear, rms = {}, {}
    for a in names:
        for b in names:
            va, vb = res[a], res[b]
            if np.std(va) == 0 or np.std(vb) == 0:
                pear[(a, b)] = None
            else:
                pear[(a, b)] = float(np.corrcoef(va, vb)[0, 1])
            rms[(a, b)] = float(np.sqrt(np.mean((va - vb) ** 2)))
    return {"names": names, "pearson": pear, "rms": rms, "grid": res}


def average_ranks(values) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = (start + end - 1) / 2 + 1
        start = end
    return ranks


def spearman(a: List[float], b: List[float]) -> Optional[float]:
    if len(a) != len(b):
        raise ValueError("ranked arrays must have the same length")
    if len(a) < 3 or not np.isfinite(a).all() or not np.isfinite(b).all():
        return None
    ra = average_ranks(a)
    rb = average_ranks(b)
    if ra.std() == 0 or rb.std() == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])
