"""Compare every SPARKLE step with the compiled official C implementation."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import subprocess
import primitif as P

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--executable",type=Path,required=True)
    args=parser.parse_args()
    rng=random.Random(752026)
    cases=[]
    for name in ("sparkle256","sparkle384","sparkle512"):
        p=P.PRIMITIVES[name]
        inputs=[0,(1<<p.n)-1]+[rng.getrandbits(p.n) for _ in range(18)]
        for x in inputs:
            trace=p.trace(x)
            words=[(x>>(32*i))&0xffffffff for i in range(p.n//32)]
            for step in range(1,p.rounds+1):
                line=f"{p.n//64} {step} "+" ".join(f"{w:08x}" for w in words)
                expected="".join(f"{(trace[step-1]>>(32*i))&0xffffffff:08x}" for i in range(p.n//32))
                cases.append((line,expected))
    proc=subprocess.run([str(args.executable.resolve())],input="\n".join(c[0] for c in cases)+"\n",
                        text=True,capture_output=True,check=True)
    answers=proc.stdout.splitlines()
    assert len(answers)==len(cases)
    for index,(actual,(_,expected)) in enumerate(zip(answers,cases)):
        assert actual==expected,(index,actual,expected)
    folder=args.executable.resolve().parent
    result={"cases":len(cases),"status":"all passed","seed":752026,
        "scope":"20 inputs (zero, ones, 18 random), every step of SPARKLE256/384/512 big; includes slim prefixes",
        "source":"https://github.com/cryptolu/sparkle/tree/master/software/sparkle",
        "source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in folder.glob('*') if p.suffix in ('.c','.h')},
        "compiler":"zig cc 0.13.0, -O2"}
    (folder/"hasil_referensi_c.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
