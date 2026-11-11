"""Render the frozen confirmation figure with unclipped export boundaries."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent/'sac_confirm'))
import matplotlib.pyplot as plt
import confirmation as C
import plot_confirmation as F


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True)
    args=parser.parse_args()
    # Export styling only: statistical sources and figure data stay unchanged.
    plt.rcParams['savefig.bbox']='tight'
    F.plot(args.input)
    path=args.input/'plot_provenance.json'
    record=json.loads(path.read_text(encoding='utf-8'))
    record['render_configuration']={'savefig.bbox':'tight'}
    record['export_wrapper_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    C.save_json(path,record)


if __name__=='__main__':main()
