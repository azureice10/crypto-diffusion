# Directed SAC comparison: protocol and execution

Read `protocol.json` for the fixed design, seeds, adaptation decisions and
inferential scope. This is a query-matched, sample-adapted comparison with
Aslan et al. (IEEE Access 2026, DOI 10.1109/ACCESS.2026.3659273), not a full
replication of their 2^20-input cipher experiments. No upstream code is copied.
The targeted ciphers are RECTANGLE-80 and CLEFIA-128 with their recorded
default keys. Existing cipher sources and frozen measurements are unchanged.

Install the pinned dependencies from `requirements.txt` into an isolated
environment. Execute from the repository root:

```bash
python experiments/sac/run_comparison.py null --bits 64 --output results/sac-directed
python experiments/sac/run_comparison.py null --bits 128 --output results/sac-directed
python experiments/sac/run_comparison.py cipher --cipher rectangle --output results/sac-directed
python experiments/sac/run_comparison.py cipher --cipher clefia --output results/sac-directed
```

The four commands are independent and can run concurrently. Null calibration
and validation seeds are independent of the cipher seeds. Sample prefixes
within a cipher replicate are nested, and all compared detectors receive the
same SAC matrix. `--replicates` is for labeled pilot runs only; the main run
uses the 500-replicate protocol default. Each output contains source hashes,
environment metadata, individual test statistics, input/matrix checksums,
selected count-matrix snapshots and independent null-calibration arrays.

The corrected-count test is the manuscript's existing rule. The histogram
tests use exact discrete bin masses at the selected smaller sample sizes.
Both nominal chi-square/Sidak p-values and independent Monte Carlo calibrated
variants are retained. Calibration does not imply equal realized null size
for discrete tests; held-out null rates and uncertainty must accompany power
comparisons. Row and column null laws coincide under the independent-label
reference, and their shared calibration is not independent evidence.
