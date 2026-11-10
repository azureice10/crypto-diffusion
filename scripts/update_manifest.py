#!/usr/bin/env python3
"""Explicitly rebuild the inventory of intended Git-tracked files."""
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    root=Path(__file__).resolve().parents[1]
    # Include staged/untracked, non-ignored files; do not hash .git or outputs.
    proc=subprocess.run(["git","ls-files","--cached","--others","--exclude-standard","-z"],
                        cwd=root,capture_output=True,check=True)
    entries={}
    for raw in sorted(set(proc.stdout.split(b"\0"))):
        if not raw:
            continue
        name=raw.decode("utf-8")
        if name=="provenance/SHA256SUMS.json":
            continue
        path=root/name
        if path.is_file():
            entries[name]={"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    value={"schema":"research-supplement-sha256/1","algorithm":"sha256","files":entries}
    (root/"provenance/SHA256SUMS.json").write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Updated manifest for {len(entries)} files. Review and stage it explicitly.")


if __name__=="__main__":
    main()
