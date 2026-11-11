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
    evidence=ROOT/"data/validation/sparkle_c_2026-11-10"
    summary=load_json(evidence/"execution_summary.json")
    assert summary["status"]=="all passed" and summary["mismatches"]==0
    assert len(summary["reports"])==4
    assert len(summary["workflow_jobs"])==6 and all(j["conclusion"]=="success" for j in summary["workflow_jobs"])
    output_hashes=set()
    input_hashes=set()
    combinations=set()
    for item in summary["reports"]:
        path=evidence/item["file"]
        assert digest(path)==item["sha256"]
        report=load_json(path)
        assert report["status"]=="all passed" and report["mismatches"]==0
        assert report["git_commit"]==summary["source_commit"]
        assert report["github_run_url"]==summary["workflow_url"]
        assert report["total_inputs_across_widths"]==5394
        assert report["C_state_comparisons"]==59846
        assert report["python_state_checks"]==199316
        assert report["numpy"]=="2.2.6"
        assert sum(g["input_count"] for g in report["groups"])==5394
        assert sum(g["C_state_comparisons"] for g in report["groups"])==59846
        for group in report["groups"]:
            n=group["state_bits"]
            assert group["input_count"]==1030+2*n
            assert group["input_categories"]["single_bit"]==n
            assert group["input_categories"]["single_zero"]==n
            assert group["input_categories"]["random"]==1024
            for config in group["configurations"]:
                assert config["scalar_states_matched"]==group["input_count"]*config["steps"]
                assert config["batch_states_matched"]==config["scalar_states_matched"]
        for relative,expected in report["source_sha256"].items():
            assert digest(ROOT/relative)==expected,relative
        combinations.add((item["python"].rsplit(".",1)[0],item["optimization"]))
        output_hashes.add(report["C_output_transcript_sha256"])
        input_hashes.add(report["C_input_transcript_sha256"])
    assert combinations=={("3.12","O0"),("3.12","O2"),("3.13","O0"),("3.13","O2")}
    assert len(output_hashes)==len(input_hashes)==1
    followup=ROOT/"data/followup/sac_directed_2026-11-10"
    sac_audit=load_json(followup/"verification.json")
    assert sac_audit["status"]=="PASS" and sac_audit["raw_cipher_condition_rows"]==15000
    assert sac_audit["source_commit"]=="b36f15ed785755be8068b898b59dc0aea8747b2a"
    sac_summary=load_json(followup/"analysis_summary.json")
    assert sac_summary["primary_paired_contrasts"]==90
    assert digest(ROOT/"experiments/sac/analyze_comparison.py")==sac_summary["analysis_source_sha256"]
    with (followup/"paired_comparisons.csv").open(encoding="utf-8",newline="") as stream:
        paired=list(csv.DictReader(stream))
    primary=[r for r in paired if r["interpretation"]=="primary"]
    assert len(paired)==360 and len(primary)==90
    significant=[r for r in primary if float(r["holm_adjusted_p"])<0.05]
    assert len(significant)==sac_summary["primary_holm_significant_contrasts"]==7
    assert sum(float(r["comparator_minus_count_rate"])>0 for r in significant)==6
    assert sum(float(r["comparator_minus_count_rate"])<0 for r in significant)==1
    size_folder=ROOT/'data/followup/sac_size_matched_2026-11-11'
    size_summary=load_json(size_folder/'analysis_summary.json')
    size_audit=load_json(size_folder/'verification.json')
    assert size_audit['status']=='PASS'
    assert size_summary['new_cipher_evaluations']==0
    assert size_summary['total_calibration_statistic_draws']==9000000
    assert size_summary['total_held_out_statistic_draws']==3000000
    assert size_summary['primary_tested_contrasts']==45 and size_summary['holm_family_slots']==90
    assert size_summary['rate_rows']==360 and size_summary['paired_comparison_rows']==270
    assert size_audit['execution_commits']==['1e3b424da936cb148dc7b536c990cdfb36a36e4f']
    for relative,expected in size_summary['source_sha256'].items():
        assert digest(ROOT/relative)==expected,relative
    key_folder=ROOT/'data/followup/sac_fresh_keys_2026-11-11'
    key_summary=load_json(key_folder/'analysis_summary.json')
    key_audit=load_json(key_folder/'verification.json')
    assert key_audit['status']=='PASS'
    assert key_summary['execution_commits']==['71853e7dbf0a1dfccb4d80146f29a824ead217a4']
    assert key_summary['new_cipher_replications']==4500 and key_summary['new_null_draws']==0
    assert key_summary['new_keys_random']==8 and key_summary['default_controls']==1
    assert key_summary['raw_rows']==27000 and key_summary['input_prefix_rows']==9000
    assert key_summary['rate_rows']==1296 and key_summary['paired_rows']==972
    assert key_summary['primary_family_size']==18
    assert key_audit['regenerated_native_snapshot_matrices']==72
    for relative,expected in key_summary['source_sha256'].items():
        assert digest(ROOT/relative)==expected,relative
    mechanism_folder=ROOT/'data/followup/sac_mechanism_2026-11-11'
    mechanism_summary=load_json(mechanism_folder/'analysis_summary.json')
    mechanism_audit=load_json(mechanism_folder/'verification.json')
    assert mechanism_audit['status']=='PASS'
    assert mechanism_summary['execution_commits']==['6d60cfb6c84a4cc02717e1896ec0d19671f08693']
    assert mechanism_summary['new_cipher_input_replications']==0
    assert mechanism_summary['replayed_cipher_input_replications']==500
    assert mechanism_summary['surrogate_matrix_draws']==90000 and mechanism_summary['layout_matrix_draws']==30000
    assert mechanism_audit['coordinate_tests']==221184 and mechanism_audit['retained_original_matrix_hashes']==1500
    for relative,expected in mechanism_summary['source_sha256'].items():
        assert digest(ROOT/relative)==expected,relative
    print(f"PASS: {len(manifest['files'])} checksummed files; 6 frozen runs; 52 checkpoints; 4 Linux C reports; directed SAC, size matching, fresh keys and mechanism diagnostics.")


if __name__=="__main__":
    try:
        main()
    except (AssertionError,ValueError,KeyError,OSError,zipfile.BadZipFile) as error:
        print("FAIL:",error,file=sys.stderr)
        sys.exit(1)
