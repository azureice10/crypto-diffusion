#!/usr/bin/env python3
"""Reproduce the complete rerun, retaining logs, checkpoints and provenance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent.parent / "eksperimen_ulang")
    args = ap.parse_args()
    root = args.output_dir.resolve()
    root.mkdir(parents=True, exist_ok=True)
    here = Path(__file__).resolve().parent
    env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", PYTHONUTF8="1")
    validation = root / "validasi"
    validation.mkdir(exist_ok=True)
    with (validation / "test_primitif.log").open("w",encoding="utf-8") as log:
        subprocess.run([sys.executable,"-B",str(here/"test_primitif.py")],env=env,
                       stdout=log,stderr=subprocess.STDOUT,check=True)
    configurations = [(f"utama_seed{seed}", ["--seed", str(seed), "--kunci", "8" if seed == 2026 else "0"])
                      for seed in range(2026, 2031)]
    configurations += [("sampel_besar_seed2026", ["--seed", "2026", "--kunci", "0",
        "--sampel-avalanche", "256", "--sampel-linear", "8192", "--pasangan-diff", "4096", "--koset", "32"])]
    for label, options in configurations:
        output = root / label
        if (output / "ringkasan.json").is_file():
            print(f"Sudah lengkap: {label}", flush=True)
            continue
        command = [sys.executable, "-u", "-B", str(here / "bandingkan.py"), *options, "--output-dir", str(output)]
        print(f"Mulai: {label}", flush=True)
        with (root / f"{label}.log").open("w", encoding="utf-8") as log:
            subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        print(f"Selesai: {label}", flush=True)
    subprocess.run([sys.executable, "-B", str(here / "audit_eksperimen.py"), "--data-dir", str(root)],
                   env=env, check=True)
    for folder in (root / "utama_seed2026", root / "sampel_besar_seed2026"):
        subprocess.run([sys.executable, "-B", str(here / "buat_grafik.py"), "--data-dir", str(folder),
                        "--output-dir", str(folder / "grafik"), "--format", "png", "pdf"], env=env, check=True)
    with zipfile.ZipFile(root/"kode_eksperimen_terkoreksi.zip","w",zipfile.ZIP_DEFLATED) as archive:
        for source in sorted(here.iterdir()):
            if source.is_file():
                archive.write(source,arcname=source.name)
    manifest = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(root.rglob("*")) if p.is_file() and p.name != "manifest_sha256.json"}
    (root / "manifest_sha256.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
