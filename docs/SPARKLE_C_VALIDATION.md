# Independent SPARKLE C execution validation

This follow-up addresses the Windows execution block recorded in the frozen
`data/reference/validasi/hasil_referensi_c.json`. Historical measurements and
their status are retained unchanged. New reports are generated on Linux by
the `sparkle-c` job in `.github/workflows/validate.yml`.

## Protocol

- Retained official SPARKLE C v1.2.1, compiled using GCC at `-O0` and `-O2`.
- Python 3.12 and 3.13, NumPy 2.2.6; four environment/build combinations.
- For each of 256, 384 and 512 bits: zero, all ones, alternating 0x55/0xaa,
  ascending/descending bytes, every one-bit input, every one-zero input, and
  1,024 distinct pseudorandom inputs. The base seed is 752026; each width uses
  Python `random.Random(base_seed + width)`.
- Each C invocation starts with the original input and computes steps 1..R,
  yielding an independent implementation's reference for every native step.
- Compare the production scalar and uint32 batch trace adapters, for both
  big and slim configurations, to those C states. Explicit slim comparisons
  reuse the corresponding big-prefix reference and are not independent data.
- State words use the adapter's little-endian word order, bit zero integer
  LSB. Reports contain input/output transcript hashes, source and executable
  hashes, compiler/Python/NumPy versions, source commit and workflow URL.

Expected counts per environment/build: 5,394 distinct-width input cases;
59,846 C state references; 199,316 Python state comparisons when scalar,
batch, big and slim are counted. These are deterministic conformance checks,
not independent statistical replications or a probability-of-correctness proof.

## Reproduce on Linux

```bash
mkdir -p results/sparkle-c
python -m pip install numpy==2.2.6
gcc -std=c99 -Wall -Wextra -Werror -O2 third_party/sparkle/sparkle_ref.c third_party/sparkle/driver.c -o results/sparkle-c/sparkle_ref
python -B MODEL2C/validasi_referensi_linux.py --executable results/sparkle-c/sparkle_ref --output results/sparkle-c/validation.json --compiler gcc --build-command "gcc -std=c99 -Wall -Wextra -Werror -O2 third_party/sparkle/sparkle_ref.c third_party/sparkle/driver.c -o results/sparkle-c/sparkle_ref"
```

## Interpretation

A passing report establishes exact agreement on the documented inputs and
steps with an independently executed official C implementation. It does not
establish cryptographic security, validate Schwaemm/Esch modes, or separately
validate every standalone Alzette round. No cipher algorithm, detector or
frozen result is changed by this validation.

## Completed execution: 10 November 2026

[GitHub Actions run 42790712675](https://github.com/azureice10/crypto-diffusion/actions/runs/42790712675)
passed all six jobs: the four C validation combinations plus the two existing
research-package validation jobs. The tested source commit is
`88ef6a22417e67f508c72652e347e7747c4775e6`.

All four C combinations report **zero mismatches**. Their input and C-output
transcript hashes agree exactly. GCC was 13.3.0; Python versions were 3.12.16
and 3.13.18; NumPy was 2.2.6. The C validation jobs took 13-15 seconds each
on GitHub-hosted Ubuntu 24.04 runners, including job setup and dependency
installation; this is not a cipher-performance benchmark.

| State | Inputs | Big steps | Slim steps | C states | Python scalar/batch states, including slim |
|---|---:|---:|---:|---:|---:|
| 256 bits | 1,542 | 10 | 7 | 15,420 | 52,428 |
| 384 bits | 1,798 | 11 | 7 | 19,778 | 64,728 |
| 512 bits | 2,054 | 12 | 8 | 24,648 | 82,160 |
| Total per build | 5,394 | | | 59,846 | 199,316 |

Permanent evidence in this repository (independent of artifact expiration):

- [Execution summary](../data/validation/sparkle_c_2026-11-10/execution_summary.json)
- [Python 3.12, -O0](../data/validation/sparkle_c_2026-11-10/sparkle-c-py3.12-O0.json)
- [Python 3.12, -O2](../data/validation/sparkle_c_2026-11-10/sparkle-c-py3.12-O2.json)
- [Python 3.13, -O0](../data/validation/sparkle_c_2026-11-10/sparkle-c-py3.13-O0.json)
- [Python 3.13, -O2](../data/validation/sparkle_c_2026-11-10/sparkle-c-py3.13-O2.json)

The archived Windows failure remains a historical fact; it is superseded as
the current conformance status by this successful Linux follow-up. Existing
cipher measurements do not require rerunning on the basis of this check:
no implementation discrepancy was found, and none of the measured algorithm
or metric source files was changed.

## Suggested manuscript replacement

"The SPARKLE scalar and uint32 batch traces were compared with the retained
official C reference v1.2.1 on Ubuntu 24.04 using GCC 13.3.0 at -O0 and -O2
and Python 3.12/3.13. For each build, 5,394 structured and seeded random input
cases produced 59,846 native-step reference states; all 199,316 scalar/batch
comparisons, including explicit slim-prefix checks, matched exactly. The four
builds used the same input suite and are not independent statistical
replications. Source hashes and execution reports are archived in the
supplement."

The earlier sentence that independent SPARKLE C execution remains incomplete
can be removed from the manuscript after incorporating this result. The
separate absence of a direct detector-power comparison remains unchanged.
