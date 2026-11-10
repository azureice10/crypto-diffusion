#!/usr/bin/env python3
"""
Compare RECTANGLE-80, CLEFIA-128, the Sparkle family (256/384/512, big and slim)
and Alzette with the same metrics.

Per primitive and per round: avalanche / SAC / diffusion completeness,
single-bit linear correlation, empirical differential, zero-sum (integral).
Once per primitive: S-box properties, randomness at full rounds, speed.
Across primitives: distinguisher horizons (absolute and as a fraction of R),
pairwise curve similarity on the normalized round axis r/R, pairwise
combination table, and the correlation between metrics.
Across keys (RECTANGLE, CLEFIA): the same metrics repeated per key, which zero-sum
bits hold for every key, and the avalanche of the key itself. CLEFIA uses its
18 native rounds. The paired-round view is a separate sensitivity analysis.

Slim Sparkle variants are the first steps of the big variant, so they are derived
from its measurement: any difference between them comes from the step count alone.

Usage:
    python bandingkan.py                    # all primitives, default sample sizes
    python bandingkan.py --cepat            # quick run (smaller samples)
    python bandingkan.py --primitif rectangle alzette --kunci 0
"""

import argparse
import csv
import json
import gzip
import hashlib
import os
import pickle
import platform
import random
import time
from itertools import combinations
from pathlib import Path

import numpy as np

import metrik as M
import primitif as P


def checkpoint(args, name, measurement):
    """Retain raw per-round measurements for audit and post-hoc sensitivity."""
    path = Path(args.output_dir) / "medicoes" / (name + ".pkl.gz")
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb") as f:
        pickle.dump(measurement, f, protocol=pickle.HIGHEST_PROTOCOL)

CURVES = {
    # key: (label, value at round 0 (identity map) as a function of n)
    "avalanche_mean": ("Avalanche rata-rata", lambda n: 1 / n),
    "completeness": ("Kelengkapan difusi", lambda n: 1 / n),
    "sac_violation_frac": ("Pelanggaran SAC", lambda n: 1.0),
    "lin_sig_frac": ("Korelasi linear signifikan", lambda n: 1 / n),
    "diff_top_frac": ("Frekuensi dy teratas", lambda n: 1.0),
    "zs8_balanced_frac": ("Bit zero-sum (8 bit aktif)", lambda n: 1.0),
}

HORIZON_KEYS = ["difusi_lengkap_ronde", "sac_horizon", "linear_horizon", "diferensial_horizon",
                "zero_sum4_horizon", "zero_sum8_horizon", "distinguisher_horizon"]

KEY_ROUND_METRICS = ["avalanche_mean", "completeness", "sac_violation_frac", "lin_sig_pairs",
                     "lin_max_abs_corr", "diff_top_count", "zs4_balanced_bits", "zs8_balanced_bits"]


def write_csv(path: Path, rows, fields=None):
    rows = list(rows)
    if not rows:
        return
    fields = fields or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})


def fmt(v, nd=3):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def measure(p: P.Primitive, args, seed: int, keep_rounds=()):
    """All per-round metrics of one primitive under one key."""
    rng = random.Random(seed)
    ava = M.avalanche(p, args.sampel_avalanche, rng)
    lin, ys = M.linear_single_bit(p, args.sampel_linear, rng, keep_rounds=keep_rounds)
    diff_rows, diff_best = M.differential(p, args.pasangan_diff, rng)
    zs4 = M.zero_sum(p, p.active4, args.koset, rng)
    zs8 = M.zero_sum(p, p.active8, args.koset, rng)
    return {"ava": ava, "lin": lin, "ys": ys, "diff_rows": diff_rows, "diff_best": diff_best,
            "zs4": zs4, "zs8": zs8}


def per_round_rows(p: P.Primitive, m, pairs: int):
    rows = []
    for r in range(p.rounds):
        b = m["diff_best"][r]
        rows.append({
            "primitif": p.name, "round": r + 1, "r_norm": round((r + 1) / p.rounds, 4),
            **{k: v for k, v in m["ava"][r].items() if k != "round"},
            **{k: v for k, v in m["lin"][r].items() if k != "round"},
            "diff_top_count": b["top_dy_count"], "diff_top_frac": b["top_dy_count"] / pairs,
            "diff_best_input": b["input_diff"], "diff_dp_log2": b["dp_log2"],
            "diff_null_p_bound": b["diff_null_p_bound"],
            "zs4_balanced_bits": m["zs4"][r]["balanced_bits"], "zs8_balanced_bits": m["zs8"][r]["balanced_bits"],
            "zs8_balanced_frac": m["zs8"][r]["balanced_frac"],
            "zs4_p_value": m["zs4"][r]["p_value"],
            "zs8_p_value": m["zs8"][r]["p_value"],
            "zs4_markov_p_bound": m["zs4"][r]["markov_p_bound"],
            "zs8_markov_p_bound": m["zs8"][r]["markov_p_bound"],
        })
    return rows


def horizons(p: P.Primitive, m, per_round):
    R = p.rounds
    # zero-sum counts only when that many balanced bits is unlikely by chance
    zs_ok = lambda row: row["p_value"] < 1e-3
    tests = {
        "sac": (m["ava"][:R], lambda r: r["sac_p_value"] < 1e-3),
        "linear": (m["lin"][:R], lambda r: r["lin_sig_pairs"] > 0),
        "diferensial": (per_round, lambda r: r["diff_top_count"] >= 3 and r["diff_null_p_bound"] < 1e-3),
        "zero_sum4": (m["zs4"][:R], zs_ok),
        "zero_sum8": (m["zs8"][:R], zs_ok),
    }
    hz = {"difusi_lengkap_ronde": M.first_round(m["ava"][:R], lambda r: r["completeness"] == 1.0)}
    for name, (rows, detected) in tests.items():
        hz[f"{name}_horizon"] = M.horizon(rows, detected)
    found = [v for k, v in hz.items() if k.endswith("horizon") and v is not None]
    hz["deteksi_terisolasi"] = " ".join(
        f"{name}:{r}" for name, (rows, detected) in tests.items() for r in M.isolated(rows, detected))
    combined = max(found) if found else 0
    hz.update({
        "distinguisher_horizon": combined,
        "horizon_frac": round(combined / R, 3),
        "margin_ronde": R - combined,
        "margin_frac": round(1 - combined / R, 3),
    })
    return hz


def measure_speed(prims, seed: int, cpu_seconds: float = 1.0, turn_seconds: float = 0.05):
    """CPU time per evaluation, taken in turns between the primitives. CPU time rather than
    wall-clock time, because a busy machine stretches wall-clock time by very uneven amounts."""
    rng = random.Random(seed)
    inputs = {p.name: [rng.getrandbits(p.n) for _ in range(50)] for p in prims}
    spent = {p.name: 0.0 for p in prims}
    evals = {p.name: 0 for p in prims}
    while min(spent.values()) < cpu_seconds:
        for p in prims:
            start = time.process_time()
            while time.process_time() - start < turn_seconds:
                for x in inputs[p.name]:
                    p.trace(x)
                evals[p.name] += len(inputs[p.name])
            spent[p.name] += time.process_time() - start
    speeds = {}
    for p in prims:
        us = spent[p.name] / evals[p.name] * 1e6
        speeds[p.name] = {"us_per_eval": us, "us_per_round": us / p.rounds, "bits_per_us": p.n / us}
    return speeds


def assemble(p: P.Primitive, m, args):
    """Result of p from a measurement of p, or of the big variant it is a prefix of."""
    R = p.rounds
    per_round = per_round_rows(p, m, args.pasangan_diff)
    zs4, zs8 = m["zs4"][:R], m["zs8"][:R]
    return {
        "info": p.info(), "per_round": per_round,
        "diff_detail": [r for r in m["diff_rows"] if r["round"] <= R],
        "zs_detail": [dict(z, primitif=p.name, set="4 bit") for z in zs4] +
                     [dict(z, primitif=p.name, set="8 bit") for z in zs8],
        "horizon": horizons(p, m, per_round),
        "randomness": M.full_round_randomness(m["ys"][R]),
    }


def analyse_all(prims, args):
    """Measure each big/standalone primitive once; slim variants reuse the big variant's measurement."""
    needed = {}
    for p in prims:
        base = P.PRIMITIVES[p.derived_from] if p.derived_from else p
        needed.setdefault(base.key, base)
    measured = {}
    for key, base in needed.items():
        keep = [q.rounds for q in P.PRIMITIVES.values() if q.derived_from == key]
        t0 = time.perf_counter()
        print(f"\n== {base.name} ({base.n} bit, {base.rounds} {base.round_unit}) ==", flush=True)
        measured[key] = measure(base, args, args.seed + base.seed_id, keep_rounds=keep)
        checkpoint(args, key, measured[key])
        print(f"  selesai dalam {time.perf_counter() - t0:.1f} s", flush=True)
    results = {}
    for p in prims:
        results[p.name] = assemble(p, measured[p.derived_from or p.key], args)
        h = results[p.name]["horizon"]
        print(f"  {p.name}: horizon distinguisher = {h['distinguisher_horizon']}/{p.rounds}")
    for name, speed in measure_speed(prims, args.seed).items():
        results[name]["speed"] = speed
    return results


# ---------------- across keys ----------------
def key_set(p: P.Primitive, count: int, seed: int):
    """(label, key): the tool's default key, two structured keys, then random keys."""
    rng = random.Random(seed)
    keys = [("default", p.default_key), ("semua 0", 0), ("semua 1", (1 << p.key_bits) - 1)]
    i = 1
    while len(keys) < count:
        keys.append((f"acak {i}", rng.getrandbits(p.key_bits)))
        i += 1
    return keys[:count]


def analyse_keys(p: P.Primitive, args):
    runs = []
    t0 = time.perf_counter()
    print(f"\n== {p.name}: {args.kunci} kunci ==", flush=True)
    for i, (label, key) in enumerate(key_set(p, args.kunci, args.seed + 77 + p.seed_id)):
        kp = p.keyed(key)
        m = measure(kp, args, args.seed + 1000 * (p.seed_id + 1) + i)
        checkpoint(args, f"{p.key}_kunci_{i}", m)
        rows = per_round_rows(kp, m, args.pasangan_diff)
        runs.append({"label": label, "key": key, "rows": rows, "zs4": m["zs4"], "zs8": m["zs8"],
                     "horizon": horizons(kp, m, rows)})
        print(f"  {label}: horizon {runs[-1]['horizon']['distinguisher_horizon']}/{p.rounds}", flush=True)

    per_key = [dict(primitif=p.name, kunci=r["label"], kunci_hex=f"{r['key']:x}", **r["horizon"]) for r in runs]

    summary = []
    for k in HORIZON_KEYS:
        vals = [r["horizon"][k] for r in runs]
        known = [v for v in vals if v is not None]
        summary.append({
            "primitif": p.name, "metrik": k,
            "min": min(known) if known else None, "max": max(known) if known else None,
            "tidak_terdeteksi": len(vals) - len(known),
            "stabil": len(known) == len(vals) and min(known) == max(known) if known else len(vals) == 0,
            "nilai": " ".join("-" if v is None else str(v) for v in vals),
        })

    per_round = []
    for r in range(p.rounds):
        row = {"primitif": p.name, "round": r + 1}
        for k in KEY_ROUND_METRICS:
            vals = [run["rows"][r][k] for run in runs]
            row.update({f"{k}_min": min(vals), f"{k}_mean": float(np.mean(vals)), f"{k}_max": max(vals)})
        per_round.append(row)

    zero_sum = []
    for set_name, field in (("4 bit", "zs4"), ("8 bit", "zs8")):
        for r in range(p.rounds):
            sets = [set(run[field][r]["balanced_positions"]) for run in runs]
            both, either = set.intersection(*sets), set.union(*sets)
            partial_hits = sum(len(q - both) for q in sets)
            rates = np.array([run[field][r]["zero_rates"] for run in runs])
            mean_rate = rates.mean(axis=0)
            top = np.argsort(-mean_rate)[:5]
            zero_sum.append({
                "primitif": p.name, "set": set_name, "round": r + 1,
                "bit_per_kunci": " ".join(str(len(s)) for s in sets),
                "semua_kunci": len(both), "sebagian_kunci": len(either - both),
                "posisi_semua_kunci": " ".join(map(str, sorted(both))),
                "posisi_sebagian_kunci": " ".join(map(str, sorted(either - both))),
                "positif_palsu_per_kunci": runs[0][field][r]["expected_false_pos"],
                # chance of this many key-dependent hits if they were all false positives
                "sebagian_p_value": M.binom_tail(p.n * len(sets), 2.0 ** -args.koset, partial_hits),
                "laju_nol_tertinggi": " ".join(f"{b}={mean_rate[b]:.3f}" for b in top),
                "kemiripan_laju_antar_kunci": _mean_pairwise_corr(rates),
            })

    ka = M.key_avalanche(p, args.sampel_kunci_avalanche, random.Random(args.seed + 500 + p.seed_id))
    ka_rows = [dict(primitif=p.name, r_norm=round(r["round"] / p.rounds, 4), **r) for r in ka]
    ka_summary = {
        "primitif": p.name, "key_bits": p.key_bits, "R": p.rounds,
        "kelengkapan_penuh_ronde": M.first_round(ka, lambda r: r["key_completeness"] == 1.0),
        "avalanche_ideal_ronde": M.first_round(ka, lambda r: abs(r["key_avalanche_mean"] - 0.5) < 0.01),
        "sac_kunci_horizon": M.horizon(ka, lambda r: r["key_sac_p_value"] < 1e-3),
    }
    print(f"  selesai dalam {time.perf_counter() - t0:.1f} s", flush=True)
    return {"per_key": per_key, "summary": summary, "per_round": per_round, "zero_sum": zero_sum,
            "key_avalanche": ka_rows, "key_avalanche_summary": ka_summary}


def _mean_pairwise_corr(rates: np.ndarray):
    """Do the keys agree on which bits are biased towards zero-sum? Near 1 = key-independent, near 0 = noise."""
    usable = rates[rates.std(axis=1) > 0]
    if len(usable) < 2:
        return None
    c = np.corrcoef(usable)
    return round(float(c[np.triu_indices(len(usable), 1)].mean()), 3)


# ---------------- relationships ----------------
def relationships(results, prims):
    names = [p.name for p in prims]
    ns = {p.name: p.n for p in prims}
    sims = {}
    for key, (label, start) in CURVES.items():
        curves = {nm: [row[key] for row in results[nm]["per_round"]] for nm in names}
        starts = {nm: start(ns[nm]) for nm in names}
        sims[key] = M.curve_similarity(curves, starts)

    pairs = []
    for a, b in combinations(names, 2):
        ha, hb = results[a]["horizon"], results[b]["horizon"]
        row = {"pasangan": f"{a} vs {b}", "a": a, "b": b,
               "R_a": results[a]["info"]["rounds"], "R_b": results[b]["info"]["rounds"],
               "horizon_frac_a": ha["horizon_frac"], "horizon_frac_b": hb["horizon_frac"],
               "selisih_margin_frac": round(ha["margin_frac"] - hb["margin_frac"], 3),
               "difusi_lengkap_frac_a": _frac(ha["difusi_lengkap_ronde"], results[a]),
               "difusi_lengkap_frac_b": _frac(hb["difusi_lengkap_ronde"], results[b])}
        ps, rs = [], []
        for key in CURVES:
            pv = sims[key]["pearson"][(a, b)]
            rv = sims[key]["rms"][(a, b)]
            row[f"pearson_{key}"] = None if pv is None else round(pv, 3)
            row[f"rms_{key}"] = round(rv, 4)
            if pv is not None:
                ps.append(pv)
            rs.append(rv)
        row["pearson_rata2"] = round(float(np.mean(ps)), 3) if ps else None
        row["rms_rata2"] = round(float(np.mean(rs)), 4)
        speed_a, speed_b = results[a]["speed"]["bits_per_us"], results[b]["speed"]["bits_per_us"]
        row["rasio_kecepatan_bit_a_per_b"] = round(speed_a / speed_b, 3)
        pairs.append(row)

    # correlation between metrics over all (primitive, round) points
    keys = ["r_norm", "avalanche_mean", "completeness", "sac_violation_frac", "lin_sig_frac",
            "lin_max_abs_corr", "diff_top_frac", "zs8_balanced_frac"]
    pts = [row for nm in names for row in results[nm]["per_round"]]
    corr = []
    for k1 in keys:
        row = {"metrik": k1}
        for k2 in keys:
            v = M.spearman([p[k1] for p in pts], [p[k2] for p in pts])
            row[k2] = None if v is None else round(v, 3)
        corr.append(row)
    return sims, pairs, corr


def _frac(r, res):
    return None if r is None else round(r / res["info"]["rounds"], 3)


def sbox_table():
    rows = [M.sbox_properties("RECTANGLE S", P.R.s_box, 4),
            M.sbox_properties("CLEFIA S0", P.C.S0, 8),
            M.sbox_properties("CLEFIA S1", P.C.S1, 8)]
    rows.append({"sbox": "Alzette (ARX, bukan tabel)", "bits": 64, "bijective": True,
                 "differential_uniformity": None, "max_dp_log2": None, "linearity": None,
                 "nonlinearity": None, "max_correlation_log2": None, "algebraic_degree": None,
                 "fixed_points": None})
    return rows


# ---------------- report ----------------
def report(out: Path, prims, results, sims, pairs, corr, sboxes, params, keys):
    L = []
    L.append("# Perbandingan RECTANGLE-80, CLEFIA-128, keluarga Sparkle, dan Alzette\n")
    L.append("Dibuat oleh `bandingkan.py`. Semua metrik dihitung dengan cara yang sama untuk setiap primitif.\n")
    L.append(f"Parameter: `{json.dumps(params)}`\n")
    L.append("## 1. Profil primitif\n")
    L.append("| Primitif | Struktur | Bit | Ronde (R) | Satuan | Catatan |\n|---|---|---|---|---|---|")
    for p in prims:
        L.append(f"| {p.name} | {p.family} | {p.n} | {p.rounds} | {p.round_unit} | {p.note} |")
    L.append("\n## 2. Unit nonlinear (S-box)\n")
    L.append("| S-box | Bit | Bijektif | Uniformitas diff. | log2 DP maks | Linearitas | Nonlinearitas | log2 korelasi maks | Derajat aljabar | Titik tetap |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for s in sboxes:
        L.append("| " + " | ".join(fmt(s[k]) for k in ("sbox", "bits", "bijective", "differential_uniformity",
                 "max_dp_log2", "linearity", "nonlinearity", "max_correlation_log2", "algebraic_degree",
                 "fixed_points")) + " |")
    L.append("\n## 3. Horizon distinguisher (ronde terakhir sifat masih terdeteksi)\n")
    L.append("Horizon gabungan = maksimum dari semua horizon. Margin = R − horizon gabungan. "
             "Pecahan (`/R`) membuat primitif dengan definisi ronde berbeda bisa dibandingkan.\n")
    L.append("| Primitif | Difusi lengkap | SAC | Linear | Diferensial | Zero-sum 4 bit | Zero-sum 8 bit | Gabungan | Gabungan/R | Margin | Margin/R |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for p in prims:
        h = results[p.name]["horizon"]
        L.append(f"| {p.name} | " + " | ".join(fmt(h[k]) for k in (
            "difusi_lengkap_ronde", "sac_horizon", "linear_horizon", "diferensial_horizon",
            "zero_sum4_horizon", "zero_sum8_horizon", "distinguisher_horizon", "horizon_frac",
            "margin_ronde", "margin_frac")) + " |")
    L.append("\nHorizon adalah akhir deretan deteksi yang bersambung dari ronde 1. Deteksi setelah jeda tidak "
             "menaikkan horizon menurut definisi operasional ini; deteksi itu bukan otomatis positif palsu dan "
             "dicatat di kolom `deteksi_terisolasi` pada `horizon.csv`. Ini horizon eksperimen, bukan batas "
             "serangan atau klaim keamanan. Angka serangan literatur harus dibaca terpisah karena model, "
             "data, kompleksitas, dan jenis serangannya berbeda.\n")
    L.append("Varian slim Sparkle memakai pengukuran varian big-nya, karena step-nya sama persis. "
             "Selisih margin big dan slim karena itu murni datang dari jumlah step.\n")
    L.append("## 4. Kurva per ronde\n")
    for p in prims:
        L.append(f"### {p.name}\n")
        L.append("| Ronde | r/R | Avalanche | Kelengkapan | Pelanggaran SAC | Korelasi linear maks | Pasangan linear signifikan | dy teratas | log2 DP | Zero-sum 4 | Zero-sum 8 |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for r in results[p.name]["per_round"]:
            L.append("| " + " | ".join(fmt(r[k]) for k in ("round", "r_norm", "avalanche_mean", "completeness",
                     "sac_violation_frac", "lin_max_abs_corr", "lin_sig_pairs", "diff_top_count",
                     "diff_dp_log2", "zs4_balanced_bits", "zs8_balanced_bits")) + " |")
        L.append("")
    L.append("## 5. Keacakan pada ronde penuh dan kecepatan\n")
    L.append("| Primitif | z maks keseimbangan bit (batas) | Korelasi antar-bit maks (batas) | Entropi byte | HW rata-rata (ideal) | Simpangan HW (ideal) | µs/evaluasi | µs/ronde | bit/µs |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for p in prims:
        x, s = results[p.name]["randomness"], results[p.name]["speed"]
        L.append(f"| {p.name} | {x['bit_balance_max_z']:.2f} ({x['bit_balance_z_crit']:.2f}) | "
                 f"{x['bit_corr_max_abs']:.3f} ({x['bit_corr_z_crit_level']:.3f}) | "
                 f"{x['byte_entropy']:.3f}/{x['byte_entropy_max_possible']:.3f} | "
                 f"{x['hw_mean']:.2f} ({x['hw_ideal']:.0f}) | {x['hw_std']:.2f} ({x['hw_std_ideal']:.2f}) | "
                 f"{s['us_per_eval']:.0f} | {s['us_per_round']:.1f} | {s['bits_per_us']:.3f} |")
    L.append("\n## 6. Kombinasi antar-pasangan\n")
    L.append("Kemiripan kurva diukur pada sumbu ronde ternormalisasi r/R (0 = input, 1 = ronde penuh). "
             "Pearson mendekati 1 = bentuk kurva mirip; RMS kecil = nilainya juga dekat.\n")
    L.append("| Pasangan | Horizon/R | Margin/R a − b | Difusi lengkap/R | Pearson rata-rata | RMS rata-rata | Rasio kecepatan (bit/µs) |")
    L.append("|---|---|---|---|---|---|---|")
    for r in pairs:
        L.append(f"| {r['pasangan']} | {fmt(r['horizon_frac_a'])} vs {fmt(r['horizon_frac_b'])} | "
                 f"{fmt(r['selisih_margin_frac'])} | {fmt(r['difusi_lengkap_frac_a'])} vs {fmt(r['difusi_lengkap_frac_b'])} | "
                 f"{fmt(r['pearson_rata2'])} | {fmt(r['rms_rata2'], 4)} | {fmt(r['rasio_kecepatan_bit_a_per_b'])} |")
    L.append("\n### Kemiripan per kurva (Pearson)\n")
    names = [p.name for p in prims]
    for key, (label, _) in CURVES.items():
        L.append(f"**{label}** (`{key}`)\n")
        L.append("| | " + " | ".join(names) + " |\n|---|" + "---|" * len(names))
        for a in names:
            L.append(f"| {a} | " + " | ".join(fmt(sims[key]["pearson"][(a, b)]) for b in names) + " |")
        L.append("")
    L.append("## 7. Korelasi antar-metrik (Spearman, semua titik primitif × ronde)\n")
    corr_keys = [k for k in corr[0] if k != "metrik"]
    L.append("| | " + " | ".join(corr_keys) + " |\n|---|" + "---|" * len(corr_keys))
    for row in corr:
        L.append(f"| {row['metrik']} | " + " | ".join(fmt(row[k]) for k in corr_keys) + " |")
    if keys:
        L.append("\n## 8. Perbandingan antar-kunci\n")
        L.append("Metrik yang sama diulang untuk kunci default, kunci semua 0, kunci semua 1, dan kunci acak. "
                 "Metrik \"stabil\" jika horizonnya sama untuk semua kunci. Selisih satu ronde di tepi horizon "
                 "biasanya efek sampel, bukan bukti ketergantungan pada kunci.\n")
        L.append("| Primitif | Metrik | Min | Maks | Kunci tanpa deteksi | Stabil | Nilai per kunci |")
        L.append("|---|---|---|---|---|---|---|")
        for k in keys.values():
            for s in k["summary"]:
                L.append(f"| {s['primitif']} | {s['metrik']} | {fmt(s['min'])} | {fmt(s['max'])} | "
                         f"{s['tidak_terdeteksi']} | {'ya' if s['stabil'] else 'tidak'} | {s['nilai']} |")
        L.append("\n### Bit zero-sum antar-kunci\n")
        L.append("\"Seimbang\" di sini berarti jumlah XOR-nya nol di **setiap** koset yang diuji. Bit yang seimbang di "
                 "semua kunci belum tentu sifat pasti, dan bit yang seimbang hanya di sebagian kunci belum tentu "
                 "bergantung pada kunci: bit dengan laju nol tinggi tetapi di bawah 100% bisa lolos di satu kunci dan "
                 "gagal di kunci lain hanya karena sampel. Karena itu lihat juga laju nol per koset (rata-rata semua "
                 "kunci) dan kemiripan laju antar-kunci: mendekati 1 berarti semua kunci sepakat bit mana yang bias, "
                 "jadi biasnya tidak bergantung pada kunci; mendekati 0 berarti noise.\n")
        L.append("Baris ditampilkan bila sebagian bit sudah hilang dan masih ada bit seimbang di semua kunci, atau bila "
                 "bit di sebagian kunci terlalu banyak untuk disebut kebetulan (p < 0,001). Semua baris ada di "
                 "`kunci_zero_sum.csv`.\n")
        L.append("| Primitif | Bit aktif | Ronde | Bit seimbang per kunci | Semua kunci | Sebagian kunci | Posisi di semua kunci | Laju nol tertinggi (bit=laju) | Kemiripan laju antar-kunci |")
        L.append("|---|---|---|---|---|---|---|---|---|")
        for pid, k in keys.items():
            n = P.PRIMITIVES[pid].n
            for z in k["zero_sum"]:
                if z["semua_kunci"] < n and (z["semua_kunci"] > 0 or z["sebagian_p_value"] < 1e-3):
                    L.append(f"| {z['primitif']} | {z['set']} | {z['round']} | {z['bit_per_kunci']} | "
                             f"{z['semua_kunci']} | {z['sebagian_kunci']} | {_cut(z['posisi_semua_kunci'])} | "
                             f"{z['laju_nol_tertinggi']} | {fmt(z['kemiripan_laju_antar_kunci'])} |")
        L.append("\n### Avalanche kunci\n")
        L.append("Satu bit kunci dibalik, dengan kunci dan plaintext acak di tiap sampel. "
                 "Avalanche ideal = ronde pertama rata-ratanya dalam 0,01 dari 0,5.\n")
        L.append("| Primitif | Bit kunci | R | Kelengkapan penuh | Avalanche ideal | Horizon SAC kunci |")
        L.append("|---|---|---|---|---|---|")
        for k in keys.values():
            s = k["key_avalanche_summary"]
            L.append(f"| {s['primitif']} | {s['key_bits']} | {s['R']} | {fmt(s['kelengkapan_penuh_ronde'])} | "
                     f"{fmt(s['avalanche_ideal_ronde'])} | {fmt(s['sac_kunci_horizon'])} |")
    L.append("\n## Catatan cara membaca\n")
    L.append("- Unit analisis utama CLEFIA adalah satu ronde asli (18 ronde total). "
             "Satu step Sparkle berisi 4 ronde ARX per cabang. Satuan ini masih berbeda, jadi bandingkan "
             "juga kolom `/R`.")
    L.append("- \"Tidak terdeteksi\" berarti tidak melewati ambang uji dengan jumlah sampel ini, bukan terbukti aman. "
             "Untuk membaca daya deteksi, lihat jumlah sampel pada Parameter, `lin_noise_level`, ambang uji SAC, "
             "jumlah pasangan diferensial, dan jumlah koset. Menaikkan sampel memperkecil noise; hasil nol tetap "
             "tidak membuktikan tidak adanya distinguisher.")
    L.append("- Bagian 1–7 memakai kunci tetap untuk RECTANGLE dan CLEFIA; analisis antar-kunci disajikan terpisah. "
             "Sparkle dan Alzette memakai spesifikasi tanpa pembungkus kunci tambahan.")
    L.append("- Trace merekam state setelah unit analisis. Whitening XOR tidak mengubah avalanche/diferensial, "
             "hanya dapat membalik tanda korelasi linear, dan saling meniadakan pada zero-sum berukuran genap. "
             "Whitening dapat mengubah statistik Hamming-weight, jadi metrik itu tidak invariant.")
    (out / "laporan.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def _cut(text: str, limit: int = 24) -> str:
    parts = text.split()
    return text if len(parts) <= limit else " ".join(parts[:limit]) + f" … (+{len(parts) - limit})"


def update_speed_only(out: Path, seed: int):
    """Re-measure speed and rebuild what depends on it, reusing the saved measurements of ringkasan.json."""
    summary = json.loads((out / "ringkasan.json").read_text(encoding="utf-8"))
    by_name = {p.name: p for p in P.PRIMITIVES.values()}
    prims = [by_name[i["name"]] for i in summary["primitif"]]
    names = [p.name for p in prims]
    speeds = measure_speed(prims, seed)
    results = {nm: {"info": by_name[nm].info(), "per_round": summary["per_ronde"][nm],
                    "horizon": summary["horizon"][nm], "randomness": summary["keacakan"][nm],
                    "speed": speeds[nm]} for nm in names}
    sims, pairs, corr = relationships(results, prims)
    keys = {by_name[nm].key: {"summary": k["ringkas"], "zero_sum": k["zero_sum"],
                              "key_avalanche_summary": k["avalanche_kunci"]}
            for nm, k in summary["antar_kunci"].items()}
    write_csv(out / "keacakan_dan_kecepatan.csv",
              [dict(primitif=nm, **results[nm]["randomness"], **speeds[nm]) for nm in names])
    write_csv(out / "kombinasi_pasangan.csv", pairs)
    summary["kecepatan"] = speeds
    summary["kombinasi_pasangan"] = pairs
    (out / "ringkasan.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    report(out, prims, results, sims, pairs, corr, summary["sbox"], summary["parameter"], keys)
    for nm in names:
        print(f"  {nm}: {speeds[nm]['us_per_eval']:.1f} µs/evaluasi, {speeds[nm]['bits_per_us']:.3f} bit/µs")


def main():
    ap = argparse.ArgumentParser(description="Perbandingan metrik RECTANGLE, CLEFIA, keluarga Sparkle, Alzette.")
    ap.add_argument("--primitif", nargs="+", default=list(P.PRIMITIVES), choices=list(P.PRIMITIVES))
    ap.add_argument("--sampel-avalanche", type=int, default=64, help="input acak untuk matriks avalanche")
    ap.add_argument("--sampel-linear", type=int, default=2048, help="input acak untuk korelasi linear")
    ap.add_argument("--pasangan-diff", type=int, default=1024, help="pasangan per beda input")
    ap.add_argument("--koset", type=int, default=16, help="koset per uji zero-sum")
    ap.add_argument("--kunci", type=int, default=8, help="jumlah kunci untuk primitif berkunci; 0 = lewati")
    ap.add_argument("--sampel-kunci-avalanche", type=int, default=32, help="sampel untuk avalanche kunci")
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--cepat", action="store_true", help="sampel kecil untuk uji cepat")
    ap.add_argument("--output-dir", "-o", default="hasil")
    ap.add_argument("--perbarui-kecepatan", action="store_true",
                    help="ukur ulang kecepatan saja, memakai ringkasan.json yang sudah ada di output-dir")
    args = ap.parse_args()
    for field in ("sampel_avalanche", "sampel_linear", "pasangan_diff", "koset", "sampel_kunci_avalanche"):
        if getattr(args, field) < 1:
            ap.error(f"{field} harus positif")
    if args.kunci < 0:
        ap.error("kunci tidak boleh negatif")
    if args.perbarui_kecepatan:
        update_speed_only(Path(args.output_dir), args.seed)
        return
    if args.cepat:
        args.sampel_avalanche, args.sampel_linear, args.pasangan_diff, args.koset = 16, 512, 256, 8
        args.kunci, args.sampel_kunci_avalanche = min(args.kunci, 3), 8

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    metadata = {
        "python": platform.python_version(), "numpy": np.__version__,
        "platform": platform.platform(), "cpu": os.environ.get("PROCESSOR_IDENTIFIER", platform.processor()),
        "logical_cpus": os.cpu_count(), "parameters": vars(args),
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(Path(__file__).parent.glob("*.py"))},
        "rules": "SAC actual discrete size + coupling; linear exact Bonferroni; ZS binomial + coupling; differential triple bound",
        "scope": "per metric per round; no global experiment-wise error control in main table",
        "trace": "round functions retain round keys and input whitening; final output whitening omitted",
    }
    (out / "ambiente.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    prims = P.get(args.primitif)
    params = {k: v for k, v in vars(args).items() if k != "output_dir"}

    results = analyse_all(prims, args)
    sims, pairs, corr = relationships(results, prims)
    sboxes = sbox_table()
    keys = {p.key: analyse_keys(p, args) for p in prims if p.with_key} if args.kunci > 0 else {}

    write_csv(out / "per_ronde.csv", [r for p in prims for r in results[p.name]["per_round"]])
    write_csv(out / "diferensial_detail.csv",
              [dict(r, primitif=p.name) for p in prims for r in results[p.name]["diff_detail"]])
    write_csv(out / "zero_sum_detail.csv",
              [{**{k: v for k, v in r.items() if k != "zero_rates"},
                "balanced_positions": " ".join(map(str, r["balanced_positions"]))}
               for p in prims for r in results[p.name]["zs_detail"]])
    write_csv(out / "horizon.csv", [dict(primitif=p.name, R=p.rounds, **results[p.name]["horizon"]) for p in prims])
    write_csv(out / "keacakan_dan_kecepatan.csv",
              [dict(primitif=p.name, **results[p.name]["randomness"], **results[p.name]["speed"]) for p in prims])
    write_csv(out / "sbox.csv", sboxes)
    write_csv(out / "kombinasi_pasangan.csv", pairs)
    write_csv(out / "korelasi_metrik.csv", corr)
    names = [p.name for p in prims]
    sim_rows = []
    for key in CURVES:
        for a in names:
            for b in names:
                sim_rows.append({"kurva": key, "a": a, "b": b,
                                 "pearson": sims[key]["pearson"][(a, b)], "rms": sims[key]["rms"][(a, b)]})
    write_csv(out / "kemiripan_kurva.csv", sim_rows)
    grid_rows = []
    for key in CURVES:
        for nm in names:
            for i, v in enumerate(sims[key]["grid"][nm]):
                grid_rows.append({"kurva": key, "primitif": nm, "r_norm": round(i / (len(sims[key]["grid"][nm]) - 1), 3),
                                  "nilai": float(v)})
    write_csv(out / "kurva_ternormalisasi.csv", grid_rows)
    if keys:
        write_csv(out / "kunci_horizon.csv", [r for k in keys.values() for r in k["per_key"]])
        write_csv(out / "kunci_horizon_ringkas.csv", [r for k in keys.values() for r in k["summary"]])
        write_csv(out / "kunci_per_ronde.csv", [r for k in keys.values() for r in k["per_round"]])
        write_csv(out / "kunci_zero_sum.csv", [r for k in keys.values() for r in k["zero_sum"]])
        write_csv(out / "avalanche_kunci.csv", [r for k in keys.values() for r in k["key_avalanche"]])
        write_csv(out / "avalanche_kunci_ringkas.csv", [k["key_avalanche_summary"] for k in keys.values()])

    summary = {
        "parameter": params,
        "primitif": [p.info() for p in prims],
        "horizon": {nm: results[nm]["horizon"] for nm in names},
        "keacakan": {nm: results[nm]["randomness"] for nm in names},
        "kecepatan": {nm: results[nm]["speed"] for nm in names},
        "sbox": sboxes,
        "kombinasi_pasangan": pairs,
        "korelasi_metrik": corr,
        "per_ronde": {nm: results[nm]["per_round"] for nm in names},
        "antar_kunci": {P.PRIMITIVES[pid].name: {
            "horizon_per_kunci": k["per_key"], "ringkas": k["summary"],
            "zero_sum": k["zero_sum"], "avalanche_kunci": k["key_avalanche_summary"],
        } for pid, k in keys.items()},
    }
    (out / "ringkasan.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    report(out, prims, results, sims, pairs, corr, sboxes, params, keys)
    print(f"\nHasil tersimpan di {out.resolve()} (laporan.md, ringkasan.json, *.csv)")


if __name__ == "__main__":
    main()
