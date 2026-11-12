# Licenses and component scope

The authors confirmed the following grants on 12 November 2026:

- **MIT** for code owned by the manuscript authors. The full grant and copyright
  notice are in [LICENSES/MIT.txt](LICENSES/MIT.txt).
- **CC BY 4.0** for data, figures and documentation owned by the manuscript
  authors. The full text is in [LICENSES/CC-BY-4.0.txt](LICENSES/CC-BY-4.0.txt).
  Attribute Hermawan Setiawan, Raden Budiarto Hadiprakoso and Sri Rosdiana,
  identify the repository version and indicate changes. Cite the associated
  article separately when its publication details become available.

These grants apply only to rights the authors hold. They do not relicense
third-party material, algorithms' upstream source code or runtime dependencies.

## Exclusions and retained notices

| Material | Applicable status |
| --- | --- |
| `third_party/sparkle/sparkle_ref.c`, `sparkle.h` | Retained upstream GPL-3.0-or-later notices; full license in `LICENSES/GPL-3.0.txt` |
| `MODEL2C/sparkle.py` | Declared upstream port; excluded from the new MIT grant and must be considered with the upstream terms |
| `MODEL2C/rectangle.py`, `MODEL2C/clefia.py` | Historical source permission remains unresolved; excluded from the new MIT grant |
| Other upstream-derived portions or dependencies | Original terms apply; the authors grant only their own original contributions |

`MODEL2C/primitif.py` and experiment-local evaluators combine study-specific
wrappers with primitive operations. A grant for the authors' original
contributions does not override terms applicable to incorporated or derived
upstream material. The MIT notice is not a repository-wide assertion that
every file or combined program is available under MIT alone.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for evidence and exclusions.
No permission from the RECTANGLE/CLEFIA upstream rights holders is asserted.
The fixed historical sources remain unchanged for reproducibility; an
authorized-source replacement or explicit upstream grant is still needed to
resolve their distribution and reuse status. Public access alone does not
establish that permission.
