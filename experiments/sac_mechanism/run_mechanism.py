"""Run the frozen mechanism stages; old data are never overwritten."""
import argparse
from pathlib import Path
import mechanism as M


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('all','descriptive','replay','surrogates','layouts','finalize'))
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    stages=('descriptive','replay','surrogates','layouts','finalize') if args.stage=='all' else (args.stage,)
    for stage in stages:
        checkpoint=args.output/('analysis_summary.json' if stage=='finalize' else f'execution_{stage}.json')
        if checkpoint.exists():raise FileExistsError(checkpoint)
        getattr(M,stage)(args.output)
