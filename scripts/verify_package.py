#!/usr/bin/env python3
"""Verify file integrity and the frozen research results; standard library only."""
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={"RECTANGLE-80":(25,6),"CLEFIA-128":(18,5),"Sparkle256":(10,2),
          "Sparkle256-slim":(7,2),"Sparkle384":(11,2),"Sparkle384-slim":(7,2),
          "Sparkle512":(12,2),"Sparkle512-slim":(8,2),"Alzette":(4,4)}


def reject_constant(value):
    raise ValueError("Nonfinite JSON constant: "+value)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"),parse_constant=reject_constant)


def digest(path):
    result=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):
            result.update(block)
    return result.hexdigest()


def main():
    manifest=load_json(ROOT/"provenance/SHA256SUMS.json")
    for relative,entry in manifest["files"].items():
        path=ROOT/relative
        if ROOT not in path.resolve().parents or not path.is_file():
            raise ValueError("Missing or invalid path: "+relative)
        if path.stat().st_size!=entry["bytes"] or digest(path)!=entry["sha256"]:
            raise ValueError("Checksum mismatch: "+relative)
    reference=ROOT/"data/reference"
    names=[f"utama_seed{seed}" for seed in range(2026,2031)]+["sampel_besar_seed2026"]
    for name in names:
        folder=reference/name
        data=load_json(folder/"ringkasan.json")
        assert set(data["per_ronde"])==set(EXPECTED),name
        for primitive,(rounds,horizon) in EXPECTED.items():
            points=data["per_ronde"][primitive]
            assert len(points)==rounds,(name,primitive)
            assert [point["round"] for point in points]==list(range(1,rounds+1))
            assert data["horizon"][primitive]["distinguisher_horizon"]==horizon
        assert set(data["antar_kunci"])==({"RECTANGLE-80","CLEFIA-128"} if name=="utama_seed2026" else set())
        with (folder/"per_ronde.csv").open(encoding="utf-8",newline="") as stream:
            rows=list(csv.DictReader(stream))
        assert len(rows)==sum(pair[0] for pair in EXPECTED.values())
        for row in rows:
            point=data["per_ronde"][row["primitif"]][int(row["round"])-1]
            for field in ("avalanche_mean","completeness","lin_sig_frac","diff_top_frac"):
                assert math.isclose(float(row[field]),point[field],rel_tol=0,abs_tol=1e-12)
    portable=sorted(reference.glob("*/medicoes_portable/*.json"))
    assert len(portable)==52,len(portable)
    for path in portable:
        metadata=load_json(path)
        assert metadata["schema"]=="measurement-checkpoint/1"
        assert digest(path.parent/metadata["arrays_file"])==metadata["arrays_sha256"]
        assert digest(path.parent/metadata["source_file"])==metadata["source_sha256"]
        with zipfile.ZipFile(path.parent/metadata["arrays_file"]) as archive:
            assert set(archive.namelist())=={key+".npy" for key in metadata["arrays"]}
    with (reference/"audit/linear_deteksi_terisolasi_konfirmasi.csv").open(encoding="utf-8",newline="") as stream:
        checks=list(csv.DictReader(stream))
    assert len(checks)==2 and all(r["confirmed_at_001"]=="False" and int(r["holdout_n"])==65536 for r in checks)
    print(f"PASS: {len(manifest['files'])} checksummed files; 6 runs; 54 configurations; 52 portable checkpoints; held-out results.")


if __name__=="__main__":
    try:
        main()
    except (AssertionError,ValueError,KeyError,OSError,zipfile.BadZipFile) as error:
        print("FAIL:",error,file=sys.stderr)
        sys.exit(1)
