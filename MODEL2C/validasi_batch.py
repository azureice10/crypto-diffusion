"""Check full measurements against saved pre-vectorization seed-2026 data."""
import argparse
import gzip
import json
from pathlib import Path
import pickle
import time
from types import SimpleNamespace
import numpy as np
import bandingkan as B
import primitif as P


def equal(a,b,path="root"):
    if isinstance(a,np.ndarray):
        np.testing.assert_array_equal(a,b,err_msg=path)
    elif isinstance(a,dict):
        assert a.keys()==b.keys(),path
        for key in a:
            equal(a[key],b[key],path+"."+str(key))
    elif isinstance(a,(tuple,list)):
        assert len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):
            equal(x,y,path+f"[{i}]")
    else:
        assert a==b,(path,a,b)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--run-dir",type=Path,required=True)
    args=ap.parse_args()
    params=json.loads((args.run_dir/"ringkasan.json").read_text(encoding="utf-8"))["parameter"]
    params=SimpleNamespace(**params)
    records=[]
    for key in ("rectangle","clefia","sparkle256","sparkle384","sparkle512","alzette"):
        p=P.PRIMITIVES[key]
        with gzip.open(args.run_dir/"medicoes"/f"{key}.pkl.gz","rb") as f:
            old=pickle.load(f)
        keep=[q.rounds for q in P.PRIMITIVES.values() if q.derived_from==key]
        start=time.perf_counter()
        current=B.measure(p,params,params.seed+p.seed_id,keep_rounds=keep)
        equal(old,current)
        records.append(dict(primitif=p.name,status="all saved values exactly equal",seconds=time.perf_counter()-start))
        print(records[-1],flush=True)
    path=args.run_dir.parent/"validasi"/"kesetaraan_batch.json"
    path.write_text(json.dumps(records,indent=2),encoding="utf-8")


if __name__=="__main__":
    main()
