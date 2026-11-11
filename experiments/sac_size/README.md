This follow-up addresses unequal null sizes in the directed SAC comparison.
The analysis plan in `protocol.json` is frozen before new null simulations,
after inspection of the existing cipher data. It is a post hoc reanalysis,
not an independent cipher replication.

The primary policy preserves the archived count decision and brings histogram
sizes toward its exact discrete size. A secondary, explicitly randomized policy
targets 0.001 for every method. Bank zero is primary; banks one and two assess
retraining sensitivity. The same validation sample is reused across banks.

Install the versions in `requirements.txt`, then run from the repository root:

```text
python -B experiments/sac_size/test_size_match.py
python -B experiments/sac_size/run_size_match.py all --samples 64 --output results/sac-size
python -B experiments/sac_size/run_size_match.py all --samples 256 --output results/sac-size
python -B experiments/sac_size/run_size_match.py all --samples 1024 --output results/sac-size
python -B experiments/sac_size/analyze_size_match.py --input results/sac-size
python -B experiments/sac_size/verify_size_match.py --input results/sac-size
python -B experiments/plot_sac_size.py --input results/sac-size
```

The three `all` commands are independent and may run concurrently. Each runs
three independent million-draw calibration banks, then a separate million-draw
held-out validation. Existing stage outputs are never overwritten. Individual
`train --bank 0/1/2` and `validate` stages support interrupted-run recovery.

The small end-to-end test uses unrelated smoke seeds and retained, ignored
`results/sac-size-smoke-<source-hash>` records. Existing smoke records cause that one test to
skip; the mathematical tests still execute. Scientific inference uses the full
frozen protocol, not smoke results.

Only upper-tail sufficient records are archived, including validation indices
for deterministic reproduction of randomizers. SHA256 fingerprints of full
draw arrays are retained. Cutoff-tail coverage, including potentially truncated
tie groups, is checked; no clipped rank is reported as an exact p-value.
The verifier recomputes every archived decision count and paired statistic from
the retained sufficient records and unchanged archived cipher statistics.

There are 45 tested RECTANGLE contrasts per bank/policy. Holm retains 90 slots,
with 45 untested CLEFIA contrasts assigned p=1. Only bank zero and the nonrandom
policy constitute the primary reanalysis; other combinations are sensitivity
analyses. Conditional null intervals do not include retraining uncertainty;
three banks characterize an observed range rather than a precise uncertainty
distribution. No original measurements or detector implementation in
`experiments/sac/` are modified.

Use the separate post-generation renderer shown above. The frozen analyzer's
optional `--plots` path encounters microscopic negative errorbar extents from
floating-point Wilson endpoints at a zero rate. The separate renderer clamps
only these plot extents, preserves recorded intervals, and records its own
source/input/output hashes. Frozen statistical sources remain byte-identical.

Archive verification (a full-history Git clone is required for comparing the
original raw-statistic bytes with their source commit):

```text
python -B experiments/sac_size/verify_size_match.py --input data/followup/sac_size_matched_2026-11-11
```
