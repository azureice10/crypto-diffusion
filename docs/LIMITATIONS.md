# Validation scope and limitations

## Recorded checks that passed

- Twelve regression tests in the final measurement workspace, including
  adapter consistency, official RECTANGLE/CLEFIA vectors, rank ties, constant
  arrays, native CLEFIA round units, slim prefixes, and batch/scalar traces.
- All six base seed-2026 measurement structures compared with the saved
  pre-vectorization checkpoints: every saved scalar and array was equal.
- Ciphertext finalization checked against native RECTANGLE/CLEFIA encryption
  on 20 additional inputs.
- Six complete runs, 54 primitive configurations, finite summary JSON, and
  expected per-round row counts.
- Conversion of 52 original checkpoints into numeric JSON/NPZ exports with
  equality checks for every exported array.

## Independent C execution: historical block and successful follow-up

Official SPARKLE C code was downloaded, retained with its license, and compiled
using Zig 0.13.0. Windows Application Control blocked execution with WinError
4551. The corresponding JSON status records zero successful comparisons.
This historical attempt has been followed by successful Linux execution on
10 November 2026. All scalar/batch big/slim trace comparisons passed against
the retained official C v1.2.1 under Python 3.12/3.13 and GCC -O0/-O2.
The [protocol and permanent reports](SPARKLE_C_VALIDATION.md) document 59,846
C reference states and 199,316 Python state comparisons per build, with zero
mismatches. Shared prefixes and repeated builds are not independent statistical
replications. This is finite conformance evidence, not an exhaustive proof or
validation of Schwaemm/Esch and all standalone Alzette rounds.

## Scientific interpretation

The [directed SAC follow-up](SAC_COMPARISON.md) now supplies a direct,
query-matched comparison against sample-adapted Basic/Row/Column histogram
tests on two default keys and selected round windows. It does not establish
behavior over all keys, replicate the source paper's full 2^20-input protocol,
or compare SAC-2/neural/exhaustive methods. Histogram calibration uses finite
independent simulation; realized null sizes are not exactly identical to the
discrete count test. Conditional validation intervals exclude retraining
uncertainty. These limits must accompany conditional detection-rate claims.

- Failure to detect a property does not establish cryptographic security.
- Round/step counts have different meanings and costs across constructions.
- The combined horizon is an operational summary of five selected tests,
  not a practical attack limit or a universal security margin.
- Linear testing uses single-bit masks; differential testing uses three fixed
  patterns; zero-sum uses two fixed active-set layouts.
- Default-key seed replication and eight-key analysis have different scopes.
  Different key runs also use different input samples; differences cannot
  automatically be assigned purely to the key.
- Full-output statistics are sanity checks under synthetic random input, not
  evidence of strong mixing on their own. Even identity preserves a uniform
  input distribution.
- Pooled byte entropy uses different numbers of byte observations across state
  sizes. Per-position entropy is supplied as an additional comparison.
- Slim/big data share measurements. Pooled correlations also contain repeated
  rounds within each primitive and should not be treated as independent data.
- The held-out CLEFIA findings were not confirmed. This is not a mathematical
  proof that the discovery detections were false.
- Type-I calibration under an ideal model does not measure power against all
  alternative ciphers, keys, masks, differences, or integral structures.
- Benchmark values describe a Python trace implementation and a particular
  environment; use the repeated benchmark table rather than a production
  performance claim.

## Archive versus new executions

The reference package preserves source hashes from more than one evaluator
version. Byte identity to every historical source hash is not claimed for the
single current code snapshot; measured scalar/batch equality is documented.
Packaging normalizes only portable paths and text encoding where recorded in
the inventory. It does not revise numeric measurements.

CI performs integrity/regression checks and a small pipeline smoke run. It
does not rerun every expensive study, the million-statistic calibration, all
eight-key experiments, or the independently blocked C test on each commit.

The draft paper still requires author review and journal formatting. No
journal acceptance, public-repository publication, or blanket reuse license
is implied by this local supplementary package.
