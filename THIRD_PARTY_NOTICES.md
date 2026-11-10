# Source attribution and license evidence

| Component | Evidence retained | Status |
|---|---|---|
| Official SPARKLE C | https://github.com/cryptolu/sparkle/tree/master/software/sparkle; original headers and `LICENSES/GPL-3.0.txt` | GPL-3.0-or-later as stated in source headers |
| Python SPARKLE | Supplied file says it is ported from `cryptolu/sparkle` | Preserve attribution and consider the upstream GPL; not independently relicensed here |
| Python RECTANGLE | Supplied header names `rectangle_strict_80.c` and Zhang et al., ePrint 2014/084 | Original C source and explicit license grant were not provided |
| Python CLEFIA | Supplied header names the official specification and `fedescarpa/clefia` | No license in supplied file; the cited GitHub license endpoint returned 404 during preparation |
| NumPy / Matplotlib | Runtime dependencies installed separately through pip | Their distributions are not vendored; their own license terms apply |

Official SPARKLE C version in the retained header: 1.2.1, 18 October 2021.
Copyright is attributed there to the SPARKLE Group and University of Luxembourg.
The comparison driver in `third_party/sparkle/driver.c` is a local test harness.
File hashes identify the downloaded bytes in the original validation record.

Algorithm references include [RFC 6114](https://www.rfc-editor.org/rfc/rfc6114.html),
the [SPARKLE specification site](https://sparkle-lwc.github.io/sparkle), and
[RECTANGLE ePrint 2014/084](https://eprint.iacr.org/2014/084).
An algorithm specification citation is not being substituted for a source-code
license grant.

Historical headers mention earlier C/random-vector checks and a
`test_sparkle.py` file that was not supplied. Those headers are kept unchanged
for byte-level provenance; they are not evidence that those checks were run
for this supplement. The current recorded validation scope is described in
`docs/LIMITATIONS.md`.
