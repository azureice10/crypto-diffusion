#!/usr/bin/env python3
"""Buat grafik publikasi dari keluaran perbandingan_algoritma.

Secara default, data dibaca dari ../perbandingan_algoritma/hasil dan grafik
ditulis ke ./grafik. Memerlukan matplotlib; CSV dibaca dengan pustaka standar.

Contoh:
    python buat_grafik.py
    python buat_grafik.py --format png pdf svg
    python buat_grafik.py --data-dir ../perbandingan_algoritma/hasil --output-dir grafik
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "hasil"
DEFAULT_OUTPUT = HERE / "grafik"

PRIMITIVE_ORDER = [
    "RECTANGLE-80", "CLEFIA-128", "Sparkle256", "Sparkle256-slim",
    "Sparkle384", "Sparkle384-slim", "Sparkle512", "Sparkle512-slim", "Alzette",
]
COLORS = {
    "RECTANGLE-80": "#4C78A8",
    "CLEFIA-128": "#F58518",
    "Sparkle256": "#54A24B",
    "Sparkle256-slim": "#9ACD8A",
    "Sparkle384": "#E45756",
    "Sparkle384-slim": "#F2A09F",
    "Sparkle512": "#7A5195",
    "Sparkle512-slim": "#B59AC8",
    "Alzette": "#72B7B2",
}
LINESTYLES = {name: ("--" if "slim" in name else "-") for name in PRIMITIVE_ORDER}


def read_csv(data_dir: Path, filename: str) -> list[dict[str, str]]:
    path = data_dir / filename
    if not path.is_file():
        print(f"Lewati {filename}: berkas tidak ditemukan")
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def number(row: dict[str, str], key: str) -> float | None:
    value = row.get(key, "")
    if value is None or value == "":
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def ordered(names: Iterable[str]) -> list[str]:
    names = set(names)
    return [name for name in PRIMITIVE_ORDER if name in names] + sorted(names - set(PRIMITIVE_ORDER))


def save_figure(fig: plt.Figure, output_dir: Path, stem: str, formats: list[str], dpi: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for ext in formats:
        fig.savefig(output_dir / f"{stem}.{ext}", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Grafik dibuat: {stem} ({', '.join(formats)})")


def base_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.labelsize": 9,
        "legend.fontsize": 8,
        "figure.titlesize": 14,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": ":",
        "savefig.facecolor": "white",
    })


def plot_round_metrics(data_dir: Path, output_dir: Path, formats: list[str], dpi: int) -> int:
    rows = read_csv(data_dir, "per_ronde.csv")
    if not rows:
        return 0
    metrics = [
        ("avalanche_mean", "Avalanche rata-rata", "Proporsi bit keluaran berubah", 0.5),
        ("completeness", "Kelengkapan difusi", "Proporsi pasangan bit yang berubah", 1.0),
        ("sac_violation_frac", "Pelanggaran SAC", "Proporsi pasangan bit signifikan", None),
        ("lin_max_abs_corr", "Korelasi linear maksimum", "Korelasi absolut maksimum", None),
        ("diff_top_frac", "Frekuensi beda keluaran teratas", "Fraksi pasangan pada dy teratas", None),
        ("zs8_balanced_frac", "Bit zero-sum (8 bit aktif)", "Fraksi bit keluaran seimbang", None),
    ]
    names = ordered(row["primitif"] for row in rows if row.get("primitif"))
    count = 0
    for key, title, ylabel, reference in metrics:
        fig, ax = plt.subplots(figsize=(8.4, 4.8))
        for name in names:
            series = sorted((r for r in rows if r.get("primitif") == name), key=lambda r: int(r["round"]))
            xs = [int(r["round"]) for r in series]
            ys = [number(r, key) for r in series]
            pairs = [(x, y) for x, y in zip(xs, ys) if y is not None]
            if not pairs:
                continue
            ax.plot([p[0] for p in pairs], [p[1] for p in pairs], marker="o", ms=3,
                    lw=1.8, color=COLORS.get(name), linestyle=LINESTYLES.get(name, "-"), label=name)
        if reference is not None:
            ax.axhline(reference, color="#333333", lw=1, ls="--", alpha=0.7,
                       label=f"Acuan {reference:g}")
        ax.set(title=title, xlabel="Ronde / step", ylabel=ylabel, ylim=(-0.03, 1.05))
        ax.set_xticks(sorted({int(r["round"]) for r in rows if r.get("round", "").isdigit()}))
        ax.legend(ncol=2, frameon=False, loc="best")
        save_figure(fig, output_dir, f"kurva_{key}", formats, dpi)
        count += 1
    return count


def plot_horizons(data_dir: Path, output_dir: Path, formats: list[str], dpi: int) -> int:
    rows = read_csv(data_dir, "horizon.csv")
    if not rows:
        return 0
    rows.sort(key=lambda r: PRIMITIVE_ORDER.index(r["primitif"]) if r["primitif"] in PRIMITIVE_ORDER else 99)
    names = [r["primitif"] for r in rows]
    y = np.arange(len(rows))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), gridspec_kw={"width_ratios": [1.25, 1]})
    horizons = [number(r, "distinguisher_horizon") or 0 for r in rows]
    totals = [number(r, "R") or 0 for r in rows]
    margins = [number(r, "margin_frac") or 0 for r in rows]
    bar_colors = [COLORS.get(name, "#777777") for name in names]
    ax1.barh(y, horizons, color=bar_colors, label="Horizon empiris")
    ax1.barh(y, [max(0, t - h) for t, h in zip(totals, horizons)], left=horizons,
             color="#E6E6E6", edgecolor="white", label="Sisa ronde/step")
    for i, (h, total) in enumerate(zip(horizons, totals)):
        ax1.text(total + max(totals) * 0.012, i, f"{int(h)}/{int(total)}", va="center", fontsize=8)
    ax1.set_yticks(y, names)
    ax1.invert_yaxis()
    ax1.set(xlabel="Ronde / step", title="Horizon empiris dari total ronde/step")
    ax1.set_xlim(0, max(totals) * 1.18)
    ax1.legend(frameon=False, loc="lower right")

    ax2.barh(y, margins, color=bar_colors)
    ax2.set_yticks(y, names)
    ax2.invert_yaxis()
    ax2.set(xlabel="Margin relatif (1 − H/R)", title="Sisa panjang relatif", xlim=(0, 1))
    for i, value in enumerate(margins):
        ax2.text(min(value + 0.025, 0.91), i, f"{value:.3f}", va="center", fontsize=8)
    fig.suptitle("Horizon deteksi dan margin")
    fig.tight_layout()
    save_figure(fig, output_dir, "horizon_margin", formats, dpi)

    fields = [
        ("sac_horizon", "SAC"), ("linear_horizon", "Linear"),
        ("diferensial_horizon", "Diferensial"),
        ("zero_sum4_horizon", "Zero-sum 4 bit"), ("zero_sum8_horizon", "Zero-sum 8 bit"),
    ]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    width = 0.14
    offsets = (np.arange(len(fields)) - (len(fields) - 1) / 2) * width
    for j, (field, label) in enumerate(fields):
        vals = [number(r, field) for r in rows]
        plotted = [0 if v is None else v for v in vals]
        bars = ax.bar(y + offsets[j], plotted, width=width, label=label)
        for bar, value in zip(bars, vals):
            if value is None:
                ax.text(bar.get_x() + bar.get_width()/2, 0.08, "—", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(y, names, rotation=25, ha="right")
    ax.set_ylabel("Horizon (ronde / step)")
    ax.set_title("Horizon per jenis pengujian")
    ax.legend(ncol=3, frameon=False)
    fig.tight_layout()
    save_figure(fig, output_dir, "horizon_per_metrik", formats, dpi)
    return 2


def plot_output_statistics(data_dir: Path, output_dir: Path, formats: list[str], dpi: int) -> int:
    rows = read_csv(data_dir, "keacakan_dan_kecepatan.csv")
    if not rows:
        return 0
    rows.sort(key=lambda r: PRIMITIVE_ORDER.index(r["primitif"]) if r["primitif"] in PRIMITIVE_ORDER else 99)
    names = [r["primitif"] for r in rows]
    ratios = [
        ("byte_entropy", "byte_entropy_max_possible", "Entropi byte / maksimum", "Entropi (bit per byte)"),
        ("hw_mean", "hw_ideal", "Rata-rata bobot Hamming / ideal", "Rasio terhadap n/2"),
        ("hw_std", "hw_std_ideal", "Simpangan baku Hamming / ideal", "Rasio terhadap √n/2"),
        ("bit_balance_max_z", "bit_balance_z_crit", "Penyimpangan keseimbangan bit", "z maksimum / batas"),
        ("bit_corr_max_abs", "bit_corr_z_crit_level", "Korelasi antar-bit maksimum", "Korelasi / batas"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.3))
    for ax, (numkey, denkey, title, ylabel) in zip(axes.flat, ratios):
        vals = []
        for row in rows:
            num, den = number(row, numkey), number(row, denkey)
            vals.append(num / den if num is not None and den not in (None, 0) else np.nan)
        x = np.arange(len(names))
        ax.bar(x, vals, color=[COLORS.get(n, "#777777") for n in names])
        ax.axhline(1, color="#333333", ls="--", lw=1)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xticks(x, names, rotation=50, ha="right", fontsize=7)
    axes.flat[-1].axis("off")
    fig.suptitle("Statistik keluaran ronde penuh dibandingkan dengan nilai acuan")
    fig.tight_layout()
    save_figure(fig, output_dir, "statistik_keluaran", formats, dpi)
    return 1


def plot_performance(data_dir: Path, output_dir: Path, formats: list[str], dpi: int) -> int:
    rows = read_csv(data_dir, "keacakan_dan_kecepatan.csv")
    valid = [(r["primitif"], number(r, "bits_per_us")) for r in rows]
    valid = [(name, val) for name, val in valid if val is not None]
    if not valid:
        return 0
    valid.sort(key=lambda p: PRIMITIVE_ORDER.index(p[0]) if p[0] in PRIMITIVE_ORDER else 99)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    names = [p[0] for p in valid]
    values = [p[1] for p in valid]
    y = np.arange(len(names))
    ax.barh(y, values, color=[COLORS.get(n, "#777777") for n in names])
    ax.set_yticks(y, names)
    ax.invert_yaxis()
    ax.set_xlabel("bit/µs (implementasi Python yang diukur)")
    ax.set_title("Throughput implementasi pada eksperimen")
    for i, value in enumerate(values):
        ax.text(value + max(values) * 0.012, i, f"{value:.3f}", va="center", fontsize=8)
    ax.set_xlim(0, max(values) * 1.2)
    save_figure(fig, output_dir, "throughput_python", formats, dpi)
    return 1


def plot_similarity(data_dir: Path, output_dir: Path, formats: list[str], dpi: int) -> int:
    rows = read_csv(data_dir, "kemiripan_kurva.csv")
    if not rows:
        return 0
    names = ordered({r["a"] for r in rows} | {r["b"] for r in rows})
    scores: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        value = number(row, "pearson")
        if value is not None:
            scores[(row["a"], row["b"])].append(value)
    matrix = np.full((len(names), len(names)), np.nan)
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            vals = scores.get((a, b), []) + scores.get((b, a), [])
            if vals:
                matrix[i, j] = float(np.mean(vals))
    fig, ax = plt.subplots(figsize=(8.5, 7.2))
    image = ax.imshow(matrix, vmin=-1, vmax=1, cmap="RdYlBu_r", aspect="auto")
    ax.set_xticks(np.arange(len(names)), names, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(names)), names)
    ax.set_title("Rata-rata Pearson antar-kurva ternormalisasi")
    fig.colorbar(image, ax=ax, label="Pearson rata-rata")
    if len(names) <= 12:
        for i in range(len(names)):
            for j in range(len(names)):
                if np.isfinite(matrix[i, j]):
                    ax.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", fontsize=7,
                            color="black" if abs(matrix[i, j]) < 0.65 else "white")
    fig.tight_layout()
    save_figure(fig, output_dir, "kemiripan_kurva_pearson", formats, dpi)
    return 1


def plot_metric_correlation(data_dir: Path, output_dir: Path, formats: list[str], dpi: int) -> int:
    rows = read_csv(data_dir, "korelasi_metrik.csv")
    if not rows:
        return 0
    labels = [key for key in rows[0] if key != "metrik"]
    matrix = np.array([[number(row, key) if number(row, key) is not None else np.nan for key in labels]
                       for row in rows])
    fig, ax = plt.subplots(figsize=(8.5, 7.0))
    image = ax.imshow(matrix, vmin=-1, vmax=1, cmap="RdBu_r", aspect="auto")
    ax.set_xticks(np.arange(len(labels)), labels, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(rows)), [r["metrik"] for r in rows])
    ax.set_title("Korelasi Spearman antar-metrik")
    fig.colorbar(image, ax=ax, label="Spearman ρ")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if np.isfinite(matrix[i, j]):
                ax.text(j, i, f"{matrix[i,j]:.2f}", ha="center", va="center", fontsize=7,
                        color="white" if abs(matrix[i, j]) > 0.55 else "black")
    fig.tight_layout()
    save_figure(fig, output_dir, "korelasi_metrik_spearman", formats, dpi)
    return 1


def plot_key_results(data_dir: Path, output_dir: Path, formats: list[str], dpi: int) -> int:
    summary = read_csv(data_dir, "kunci_horizon_ringkas.csv")
    avalanche = read_csv(data_dir, "avalanche_kunci.csv")
    count = 0
    horizon = [r for r in summary if r.get("metrik") == "distinguisher_horizon"]
    if horizon:
        fig, ax = plt.subplots(figsize=(7.5, 3.8))
        names = [r["primitif"] for r in horizon]
        y = np.arange(len(names))
        low = np.array([number(r, "min") or 0 for r in horizon])
        high = np.array([number(r, "max") or 0 for r in horizon])
        ax.hlines(y, low, high, color=[COLORS.get(n, "#777777") for n in names], lw=5)
        ax.scatter((low + high) / 2, y, color="black", s=20, zorder=3)
        for i, row in enumerate(horizon):
            ax.text(high[i] + 0.15, i, f"{int(low[i])}–{int(high[i])}", va="center", fontsize=8)
        ax.set_yticks(y, names)
        ax.invert_yaxis()
        ax.set_xlabel("Horizon gabungan (ronde)")
        ax.set_title("Rentang horizon pada delapan kunci uji")
        ax.set_xlim(0, max(high) + 1.8)
        save_figure(fig, output_dir, "horizon_lintas_kunci", formats, dpi)
        count += 1
    if avalanche:
        names = ordered(r["primitif"] for r in avalanche)
        fig, ax = plt.subplots(figsize=(8, 4.8))
        for name in names:
            series = sorted((r for r in avalanche if r.get("primitif") == name), key=lambda r: int(r["round"]))
            ax.plot([int(r["round"]) for r in series], [number(r, "key_avalanche_mean") for r in series],
                    marker="o", ms=3, lw=1.8, label=name, color=COLORS.get(name))
        ax.axhline(0.5, color="#333333", ls="--", lw=1, label="Acuan 0,5")
        ax.set(xlabel="Ronde", ylabel="Avalanche kunci rata-rata", ylim=(-0.03, 1.05),
               title="Difusi akibat pembalikan satu bit kunci")
        ax.legend(frameon=False)
        save_figure(fig, output_dir, "avalanche_kunci", formats, dpi)
        count += 1
    return count


def plot_differential(data_dir: Path, output_dir: Path, formats: list[str], dpi: int) -> int:
    rows = read_csv(data_dir, "per_ronde.csv")
    if not rows:
        return 0
    names = ordered(r["primitif"] for r in rows)
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for name in names:
        series = sorted((r for r in rows if r.get("primitif") == name), key=lambda r: int(r["round"]))
        vals = [(int(r["round"]), number(r, "diff_top_count")) for r in series]
        vals = [(x, y) for x, y in vals if y is not None]
        ax.plot([p[0] for p in vals], [p[1] for p in vals], marker="o", ms=3, lw=1.6,
                label=name, color=COLORS.get(name), linestyle=LINESTYLES.get(name, "-"))
    ax.axhline(3, color="#333333", ls="--", lw=1, label="Ambang deteksi (3)")
    ax.set_yscale("log")
    ax.set(xlabel="Ronde / step", ylabel="Frekuensi dy teratas (skala log)",
           title="Frekuensi beda keluaran teratas")
    ax.legend(ncol=2, frameon=False)
    save_figure(fig, output_dir, "diferensial_dy_teratas", formats, dpi)
    return 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA,
                        help=f"folder data CSV (default: {DEFAULT_DATA})")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT,
                        help=f"folder tujuan grafik (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--format", nargs="+", choices=("png", "pdf", "svg"), default=["png", "pdf"],
                        help="format berkas grafik; default: png pdf")
    parser.add_argument("--dpi", type=int, default=300, help="resolusi PNG (default: 300 dpi)")
    args = parser.parse_args()

    if not args.data_dir.is_dir():
        parser.error(f"folder data tidak ditemukan: {args.data_dir}")
    base_style()
    generated = 0
    builders = [plot_round_metrics, plot_horizons, plot_output_statistics, plot_performance,
                plot_similarity, plot_metric_correlation, plot_key_results, plot_differential]
    for builder in builders:
        generated += builder(args.data_dir, args.output_dir, args.format, args.dpi)
    if generated == 0:
        raise SystemExit("Tidak ada grafik dibuat; periksa nama dan skema CSV sumber.")
    print(f"Selesai: {generated} grafik di {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
