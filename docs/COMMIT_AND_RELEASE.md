# Local commit and public release

The initial packaging prepared a local Git repository on branch `main`, with
files staged for review. The repository designated by the authors is now
https://github.com/azureice10/crypto-diffusion. Commit and push use the owner's
authenticated GitHub account; credentials are not stored in this package.

The separately provided ZIP excludes `.git`, caches and generated smoke
outputs. If starting from the ZIP rather than the prepared folder, run
`git init --initial-branch=main` and `git add --all` first.

Before making the local commit:

```bash
python scripts/verify_package.py
git status --short
git diff --cached --stat
git commit -m "Add reproducible cryptographic diffusion research supplement"
```

Use the research team's own configured Git identity; no identity is embedded
or configured by the package. The author list in CITATION.cff is bibliographic
metadata, not the Git commit author.

For subsequent tracked changes, rebuild the checksum inventory deliberately:

```bash
python scripts/update_manifest.py
python scripts/verify_package.py
git add --all
```

Before a public release, resolve the component-specific rights recorded in
LICENSE.md, choose grants for author-owned code/data/docs, review author names
and contributions, and replace/add repository and final article identifiers
when they actually exist. The local commit can preserve this rights review
without silently granting rights that were never supplied.

The journal draft and template are excluded. Data sharing statements should
cite the actual repository URL or deposited DOI once created, rather than a
local Windows path. The intended remote is
`https://github.com/azureice10/crypto-diffusion.git`; this package does not
contain an access token.
