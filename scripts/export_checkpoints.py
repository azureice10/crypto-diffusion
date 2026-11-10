#!/usr/bin/env python3
"""Export trusted local measurement pickles as JSON + numeric NPZ files.

Pickle is loaded only by explicit invocation of this exporter. To read the
published portable data, use read_checkpoint.py instead (allow_pickle=False).
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import pickle
import numpy as np


def export_one(source, directory):
    with gzip.open(source,"rb") as stream:
        measurement=pickle.load(stream)
    arrays={}
    def encode(value):
        if isinstance(value,np.ndarray):
            if value.dtype.hasobject:
                raise ValueError("Object arrays cannot be exported")
            name=f"array_{len(arrays):04d}"
            arrays[name]=value
            return {"$array":name}
        if isinstance(value,np.generic):
            return value.item()
        if isinstance(value,dict):
            return {str(key):encode(item) for key,item in value.items()}
        if isinstance(value,(tuple,list)):
            return [encode(item) for item in value]
        return value
    payload=encode(measurement)
    directory.mkdir(parents=True,exist_ok=True)
    stem=source.name.removesuffix(".pkl.gz")
    npz=directory/(stem+".npz")
    np.savez_compressed(npz,**arrays)
    metadata={"schema":"measurement-checkpoint/1","source_file":"../medicoes/"+source.name,
              "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
              "arrays_file":npz.name,"arrays_sha256":hashlib.sha256(npz.read_bytes()).hexdigest(),
              "arrays":{name:{"shape":list(a.shape),"dtype":a.dtype.str} for name,a in arrays.items()},
              "measurement":payload}
    target=directory/(stem+".json")
    target.write_text(json.dumps(metadata,ensure_ascii=False,allow_nan=False,indent=2)+"\n",encoding="utf-8")
    # Verify every exported numeric array immediately without using pickle.
    with np.load(npz,allow_pickle=False) as saved:
        for name,value in arrays.items():
            np.testing.assert_array_equal(value,saved[name])
    return target


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir",type=Path,default=Path(__file__).resolve().parents[1]/"data/reference")
    args=parser.parse_args()
    sources=sorted(args.reference_dir.glob("*/medicoes/*.pkl.gz"))
    if not sources:
        parser.error("No measurement checkpoints found")
    for source in sources:
        export_one(source,source.parent.parent/"medicoes_portable")
    print(f"Exported and verified {len(sources)} checkpoints (JSON + NPZ).")


if __name__=="__main__":
    main()
