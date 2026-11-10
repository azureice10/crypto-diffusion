"""Compare scalar/batch SPARKLE traces to the retained official C reference.

Run separately from the frozen historical measurements. Slim prefixes are
checked explicitly but are not independent observations of the big traces.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys

import numpy as np
import primitif as P

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_SOURCE = "https://github.com/cryptolu/sparkle/tree/master/software/sparkle"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_suite(bits, random_inputs, seed):
    """Distinct structured and seeded random inputs in integer-LSB bit order."""
    mask = (1 << bits) - 1
    entries = [("zero", 0), ("ones", mask),
               ("alternating_55", int.from_bytes(b"\x55" * (bits // 8), "little")),
               ("alternating_aa", int.from_bytes(b"\xaa" * (bits // 8), "little")),
               ("ascending_bytes", int.from_bytes(bytes(range(bits // 8)), "little")),
               ("descending_bytes", int.from_bytes(bytes(reversed(range(bits // 8))), "little"))]
    entries += [("single_bit", 1 << bit) for bit in range(bits)]
    entries += [("single_zero", mask ^ (1 << bit)) for bit in range(bits)]
    rng = random.Random(seed + bits)
    seen = {value for _, value in entries}
    for _ in range(random_inputs):
        value = rng.getrandbits(bits)
        while value in seen:
            value = rng.getrandbits(bits)
        seen.add(value)
        entries.append(("random", value))
    if len(seen) != len(entries):
        raise ValueError("Structured inputs unexpectedly overlap")
    return entries


def compare_trace(actual, expected, label):
    if len(actual) != len(expected):
        raise AssertionError(f"Trace length mismatch: {label}")
    for step, (value, reference) in enumerate(zip(actual, expected), 1):
        if value != reference:
            raise AssertionError(f"C mismatch: {label}, step={step}, python={value:x}, C={reference:x}")
    return len(expected)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "results/sparkle-c/validation.json")
    parser.add_argument("--random-inputs", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=752026)
    parser.add_argument("--compiler", default="cc")
    parser.add_argument("--build-command", default="not recorded")
    args = parser.parse_args()
    if args.random_inputs < 1:
        parser.error("--random-inputs must be positive")
    executable = args.executable.resolve()
    compiler = subprocess.run([args.compiler, "--version"], capture_output=True,
                              text=True, check=True).stdout.splitlines()[0]
    all_inputs, requests, slices = {}, [], {}
    for bits in (256, 384, 512):
        primitive = P.PRIMITIVES[f"sparkle{bits}"]
        entries = input_suite(bits, args.random_inputs, args.seed)
        all_inputs[bits] = entries
        start = len(requests)
        for _, value in entries:
            words = " ".join(f"{(value >> (32*i)) & 0xffffffff:08x}" for i in range(bits // 32))
            for step in range(1, primitive.rounds + 1):
                requests.append(f"{bits // 64} {step} {words}")
        slices[bits] = (start, len(requests))
    transcript = "\n".join(requests) + "\n"
    proc = subprocess.run([str(executable)], input=transcript, capture_output=True,
                          text=True, check=True, timeout=180)
    answers = proc.stdout.splitlines()
    if len(answers) != len(requests):
        raise AssertionError(f"C returned {len(answers)} lines for {len(requests)} requests")
    groups = []
    checks = 0
    for bits, entries in all_inputs.items():
        big = P.PRIMITIVES[f"sparkle{bits}"]
        lines = answers[slices[bits][0]:slices[bits][1]]
        reference = []
        for index, (_, value) in enumerate(entries):
            states = []
            for line in lines[index*big.rounds:(index+1)*big.rounds]:
                if len(line) != bits // 4 or any(c not in "0123456789abcdef" for c in line):
                    raise ValueError("Malformed C state")
                states.append(sum(int(line[i:i+8], 16) << (4*i) for i in range(0, len(line), 8)))
            reference.append(states)
        group = {"state_bits": bits, "input_count": len(entries),
                 "input_categories": dict(Counter(kind for kind, _ in entries)),
                 "C_step_count": big.rounds, "C_state_comparisons": len(lines),
                 "input_sha256": hashlib.sha256(b"".join(v.to_bytes(bits//8, "little") for _, v in entries)).hexdigest(),
                 "configurations": []}
        for key in (f"sparkle{bits}", f"sparkle{bits}s"):
            primitive = P.PRIMITIVES[key]
            scalar_count = batch_count = 0
            values = [value for _, value in entries]
            batch = primitive.batch_trace(values)
            if len(batch) != len(values):
                raise AssertionError("Batch input count mismatch")
            for index, value in enumerate(values):
                expected = reference[index][:primitive.rounds]
                label = f"{key}, input_index={index}, input={value:x}"
                scalar_count += compare_trace(primitive.trace(value), expected, label + ", scalar")
                batch_count += compare_trace(batch[index], expected, label + ", batch")
            checks += scalar_count + batch_count
            group["configurations"].append({"primitive": key, "steps": primitive.rounds,
                                             "scalar_states_matched": scalar_count,
                                             "batch_states_matched": batch_count})
        groups.append(group)
    source_files = [ROOT / "third_party/sparkle" / name for name in ("sparkle_ref.c", "sparkle.h", "driver.c")]
    python_files = [Path(__file__).resolve(), ROOT / "MODEL2C/primitif.py", ROOT / "MODEL2C/sparkle.py"]
    run_id, repository = os.environ.get("GITHUB_RUN_ID"), os.environ.get("GITHUB_REPOSITORY")
    result = {
        "schema": "sparkle-c-conformance/1", "status": "all passed",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(), "seed": args.seed,
        "random_seed_rule": "base seed + state bits, Python random.Random",
        "random_inputs_per_width": args.random_inputs,
        "total_inputs_across_widths": sum(len(x) for x in all_inputs.values()),
        "C_state_comparisons": len(requests), "python_state_checks": checks,
        "mismatches": 0, "groups": groups,
        "scope": "Every big step; explicit slim-prefix checks; Python scalar and uint32 batch against retained official C v1.2.1. Shared prefixes are not independent replications. No exhaustive proof, Schwaemm/Esch validation or standalone Alzette validation is claimed.",
        "source": OFFICIAL_SOURCE,
        "source_sha256": {p.relative_to(ROOT).as_posix(): sha256(p) for p in source_files + python_files},
        "C_executable_sha256": sha256(executable),
        "C_input_transcript_sha256": hashlib.sha256(transcript.encode()).hexdigest(),
        "C_output_transcript_sha256": hashlib.sha256(proc.stdout.encode()).hexdigest(),
        "compiler": compiler, "build_command": args.build_command,
        "platform": platform.platform(), "machine": platform.machine(),
        "python": sys.version, "numpy": np.__version__,
        "git_commit": os.environ.get("GITHUB_SHA"),
        "github_run_url": f"https://github.com/{repository}/actions/runs/{run_id}" if run_id and repository else None,
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "C_state_comparisons": len(requests),
                      "python_state_checks": checks, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
