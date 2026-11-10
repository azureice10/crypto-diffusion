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

Completed execution evidence will be linked here after the Linux run has
finished and its machine-readable reports have been checked.
