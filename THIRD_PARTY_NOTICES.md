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

## Provenance recheck — 12 November 2026

The fedescarpa/clefia repository root, README and C header were inspected
again through the GitHub connector. The root contains README.md, clefia.c,
encript.c and decript.c, with no LICENSE file; the inspected header and README
contain no explicit source-code license grant. The inspected clefia.c blob is
`9ee52be938203c3619c59f4b9fa56f655a8f6ec5`. This recheck does not establish
permission. The supplied RECTANGLE module identifies rectangle_strict_80.c,
but that source and an explicit grant were not supplied. Citation of an
algorithm specification alone does not license a previously ported source.

The author-confirmed MIT and CC BY 4.0 grants cover their rights only. The
historical cipher modules and upstream-derived portions are excluded as
described in LICENSE.md. No permissions have been requested from upstream
authors in this workflow. Historical measured sources remain byte-identical;
an authorized-source replacement is separate implementation work.
