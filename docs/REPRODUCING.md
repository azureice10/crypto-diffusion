# Reproducing the supplement

Run commands from the repository root. Do not overwrite `data/reference/`.

## Environment

Recorded environment: Windows 11, 12 logical CPUs, Python 3.13.14,
NumPy 2.2.6; Matplotlib 3.11.2 was used to generate the figures. CPU details
are retained in each run's `ambiente.json`. Python 3.12 is also targeted by
the regression tests and CI; the numerical results recorded here came from
the recorded environment, not from an unexecuted cross-platform assertion.

```bash
python -m venv .venv
```

Activate on Linux/macOS:

```bash
source .venv/bin/activate
```

Activate in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install and check:

```bash
python -m pip install -r MODEL2C/requirements.txt
python -B scripts/verify_package.py
python -B MODEL2C/test_primitif.py
```

The verifier is dependency-free and never loads pickle. Regression tests
include known RECTANGLE/CLEFIA vectors, all primitive adapters, slim prefixes,
native CLEFIA units, rank ties, constant correlations, and scalar/batch traces.

## Workflows

| Purpose | Command |
|---|---|
| Full six-run study, audit, held-out check, figures | `python -B MODEL2C/ulang_eksperimen.py --output-dir results/reproduced` |
| Single full main run, including eight keys | `python -B MODEL2C/bandingkan.py --seed 2026 --output-dir results/main` |
| Fast pipeline exercise, not a paper result | `python -B MODEL2C/bandingkan.py --cepat --primitif rectangle alzette --kunci 0 --output-dir results/smoke` |
| Figures for a new run | `python -B MODEL2C/buat_grafik.py --data-dir results/main --output-dir results/main/grafik --format png pdf` |
| Audit a newly reproduced complete six-run study | `python -B MODEL2C/audit_eksperimen.py --data-dir results/reproduced` |
| Read a portable reference checkpoint | `python -B scripts/read_checkpoint.py data/reference/utama_seed2026/medicoes_portable/clefia.json` |

The full runner uses seeds 2026–2030. Only seed 2026 performs the eight-key
analysis; other seed runs use the default key. The larger-sample run uses seed
2026 and no additional-key analysis. Main parameters are avalanche=64,
linear/output=2048, differential=1024 pairs per pattern, zero-sum=16 cosets,
key avalanche=32. Larger-sample parameters are 256, 8192, 4096, and 32 cosets.

The runner passes `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1` to its child
processes. It skips directories containing a completed `ringkasan.json`.
Use a fresh `results/` path for a genuinely new execution, rather than treating
an existing completed directory as a new replication.

`audit_eksperimen.py` expects all six run directories. It repeats null
calibration with fixed calibration seeds, inspects late CLEFIA correlations,
and performs the pre-specified held-out check with 65,536 inputs and seed
20261110. Re-running the same seeds is reproducibility, not a new independent
experiment. Its five benchmark repetitions occur after the numerical runs.

## Reading original and portable checkpoints

The original audit reads trusted `.pkl.gz` files produced by the study. For
ordinary data inspection, prefer JSON/NPZ and `read_checkpoint.py`, which
does not use pickle. Portable JSON dictionary keys are strings, including the
retained-round keys under `ys`. Conversion preserves every numeric array's
dtype, shape, and values. The exporter records the original checkpoint hash
and the NPZ hash in the paired JSON file.

To export **newly generated trusted checkpoints**:

```bash
python -B scripts/export_checkpoints.py --reference-dir results/reproduced
```

## Official C comparison and successful Linux follow-up

The official C source and local driver are provided in `third_party/sparkle/`.
In an environment with an authorized C compiler, a typical build is:

```bash
mkdir -p results/sparkle-c
gcc -std=c99 -Wall -Wextra -Werror -O2 third_party/sparkle/sparkle_ref.c third_party/sparkle/driver.c -o results/sparkle-c/sparkle_ref
python -B MODEL2C/validasi_referensi_linux.py --executable results/sparkle-c/sparkle_ref --output results/sparkle-c/validation.json --compiler gcc --build-command "gcc -std=c99 -Wall -Wextra -Werror -O2 third_party/sparkle/sparkle_ref.c third_party/sparkle/driver.c -o results/sparkle-c/sparkle_ref"
```

The Windows execution originally attempted for this supplement was blocked
by Application Control. The frozen JSON records that block. A subsequent
Linux execution passed all four Python/compiler combinations; see
[SPARKLE_C_VALIDATION.md](SPARKLE_C_VALIDATION.md) for the protocol, counts,
workflow and permanent evidence. The workflow reruns this check on pushes
and pull requests. No executable is shipped.

## Expected agreement

The frozen six runs share the combined horizons listed in the README. Exact
benchmark timings are not expected to reproduce on different hardware.
Floating-point correlations may differ slightly between numerical-library
builds. The scalar-to-batch validation in the recorded environment compared
all six base seed-2026 measurements and found all saved values exactly equal.

The manuscript and journal template are separate from the research artifact. The verification scope is defined by the recorded finite conformance checks and the frozen protocols.
