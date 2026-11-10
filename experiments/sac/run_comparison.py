"""Execute the frozen directed-SAC protocol; see protocol.json before running."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
import scipy

import batch_ciphers as B
import sac_statistics as S

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROTOCOL=json.loads((HERE/'protocol.json').read_text(encoding='utf-8'))
SIZES=tuple(PROTOCOL['sample_sizes'])
BASE_SEED=PROTOCOL['base_seed']


def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def source_record():
    paths=list(HERE.glob('*.py'))+[HERE/'protocol.json',HERE/'requirements.txt']
    paths += [ROOT/'MODEL2C'/name for name in ('primitif.py','rectangle.py','clefia.py','metrik.py')]
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def metadata(args,started,extra=None):
    try:
        commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
    except (OSError,subprocess.CalledProcessError):
        commit=None
    return {'schema':'directed-sac-execution/1','stage':args.stage,'cipher':args.cipher,'bits':args.bits,
            'git_commit':commit,'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
            'platform':platform.platform(),'elapsed_seconds':time.perf_counter()-started,
            'source_sha256':source_record(),**(extra or {})}


def run_null(args):
    started=time.perf_counter();n=args.bits
    report=[]
    for samples in SIZES:
        tick=time.perf_counter()
        cal=S.sample_null_statistics(n,samples,PROTOCOL['null_calibration_repetitions'],
                                    np.random.default_rng(np.random.SeedSequence([BASE_SEED,101,n,samples])))
        calibration={'basic':np.sort(cal[:,1]),'max_axis':np.sort(cal[:,2])}
        np.savez_compressed(args.output/f'calibration_n{n}_N{samples}.npz',**calibration)
        print(json.dumps({'stage':'calibration','bits':n,'N':samples,'seconds':time.perf_counter()-tick}),flush=True)
        validation=S.sample_null_statistics(n,samples,PROTOCOL['null_validation_repetitions'],
                                           np.random.default_rng(np.random.SeedSequence([BASE_SEED,102,n,samples])))
        stats=np.c_[validation,validation[:,2]]
        policies={'nominal':S.nominal_pvalues(stats,n,samples),
                  'MC_calibrated':S.monte_carlo_pvalues(stats,n,samples,calibration)}
        cuts,probabilities,_=S.bin_description(samples)
        for policy,pvalues in policies.items():
            for alpha in (PROTOCOL['primary_alpha'],PROTOCOL['sensitivity_alpha']):
                for index,method in enumerate(S.METHODS):
                    successes=int((pvalues[:,index]<alpha).sum())
                    low,high=S.wilson(successes,len(stats))
                    report.append({'state_bits':n,'N':samples,'policy':policy,'alpha':alpha,'method':method,
                                   'validation_repetitions':len(stats),'rejections':successes,
                                   'rate':successes/len(stats),'wilson95_low':low,'wilson95_high':high,
                                   'coupling_bound':S.coupling(n,samples),
                                   'minimum_row_bin_expectation':n*float(probabilities.min()),
                                   'bin_cuts':json.dumps(cuts.tolist()),
                                   'null_law_note':'row and column share marginal simulation; not separate independent trials'})
        print(json.dumps({'stage':'null_validation','bits':n,'N':samples,'seconds':time.perf_counter()-tick}),flush=True)
    write_csv(args.output/f'null_validation_n{n}.csv',report)
    (args.output/f'null_metadata_n{n}.json').write_text(json.dumps(metadata(args,started),indent=2)+'\n',encoding='utf-8')


def run_cipher(args):
    started=time.perf_counter();name=args.cipher;cfg=B.CONFIG[name];n=cfg['bits']
    rows=[];input_rows=[];snapshots={}
    repetitions=PROTOCOL['replications_per_cipher'] if args.replicates is None else args.replicates
    snapshots_to_keep=set(PROTOCOL['snapshot_replicates'])
    for replicate in range(repetitions):
        seed=np.random.SeedSequence([BASE_SEED,201,n,replicate])
        matrices,values=B.avalanche_counts(name,seed,SIZES)
        for samples,counts in matrices.items():
            input_rows.append({'cipher':name,'replicate':replicate,'N':samples,
                               'seed_entropy':json.dumps(seed.entropy),
                               'input_sha256':hashlib.sha256(values[:samples].tobytes()).hexdigest(),
                               'query_budget':samples*(n+1)})
            stats=S.statistics(counts,samples)
            nominal=S.nominal_pvalues(stats,n,samples)
            for r in cfg['analysis_rounds']:
                row={'cipher':name,'state_bits':n,'key_hex':cfg['key_hex'],'replicate':replicate,'N':samples,'native_round':r,
                     'query_budget':samples*(n+1),'count_matrix_sha256':hashlib.sha256(counts[r-1].tobytes()).hexdigest()}
                for index,method in enumerate(S.METHODS):
                    row['stat_'+method]=float(stats[r-1,index])
                    row['nominal_p_'+method]=float(nominal[r-1,index])
                rows.append(row)
            if replicate in snapshots_to_keep:
                snapshots[f'rep{replicate}_N{samples}']=counts
        if (replicate+1)%25==0 or replicate==0:
            print(json.dumps({'stage':'cipher','cipher':name,'completed_replicates':replicate+1,
                              'total_replicates':repetitions,'seconds':time.perf_counter()-started}),flush=True)
    write_csv(args.output/f'cipher_raw_{name}.csv',rows)
    write_csv(args.output/f'inputs_{name}.csv',input_rows)
    np.savez_compressed(args.output/f'count_snapshots_{name}.npz',**snapshots)
    (args.output/f'cipher_metadata_{name}.json').write_text(json.dumps(metadata(args,started,{'replicates':repetitions}),indent=2)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['null','cipher'])
    parser.add_argument('--bits',type=int,choices=[64,128])
    parser.add_argument('--cipher',choices=list(B.CONFIG))
    parser.add_argument('--replicates',type=int,help='Optional pilot size; main run must use protocol default')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    if args.stage=='null':
        if args.bits is None:parser.error('--bits required for null stage')
        run_null(args)
    else:
        if args.cipher is None:parser.error('--cipher required for cipher stage')
        run_cipher(args)


if __name__=='__main__':main()
