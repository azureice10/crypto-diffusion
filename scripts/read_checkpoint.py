#!/usr/bin/env python3
"""Read a portable checkpoint without importing or loading pickle."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np


def load_checkpoint(path):
    metadata=json.loads(path.read_text(encoding="utf-8"))
    if metadata["schema"]!="measurement-checkpoint/1":
        raise ValueError("Unsupported schema")
    arrays_path=path.parent/metadata["arrays_file"]
    if arrays_path.parent.resolve()!=path.parent.resolve():
        raise ValueError("Array file must be alongside the metadata")
    if hashlib.sha256(arrays_path.read_bytes()).hexdigest()!=metadata["arrays_sha256"]:
        raise ValueError("NPZ checksum mismatch")
    with np.load(arrays_path,allow_pickle=False) as saved:
        arrays={key:saved[key] for key in saved.files}
    for name,description in metadata["arrays"].items():
        if arrays[name].shape!=tuple(description["shape"]) or arrays[name].dtype.str!=description["dtype"]:
            raise ValueError("Array schema mismatch: "+name)
    def decode(value):
        if isinstance(value,dict):
            if set(value)=={"$array"}:
                return arrays[value["$array"]]
            return {key:decode(item) for key,item in value.items()}
        if isinstance(value,list):
            return [decode(item) for item in value]
        return value
    return decode(metadata["measurement"])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("metadata",type=Path)
    args=parser.parse_args()
    result=load_checkpoint(args.metadata)
    print("Measurement fields:",", ".join(result))
    print("Avalanche rounds:",len(result["ava"]))
    print("Retained output rounds:",", ".join(result["ys"]))


if __name__=="__main__":
    main()
