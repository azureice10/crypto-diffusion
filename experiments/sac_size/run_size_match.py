"""Run frozen, separate null banks and held-out validation; no cipher calls."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import scipy

import size_statistics as S

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P = S.PROTOCOL


def hashes():
    paths = sorted(HERE.glob('*.py'))+[HERE/'protocol.json', HERE/'requirements.txt',
                                    HERE.parent/'sac/sac_statistics.py']
    paths += [ROOT/P['source_data_folder']/name for name in
              ('cipher_raw_rectangle.csv','detection_rates.csv')]
    paths += [HERE.parent/'sac/protocol.json']
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def metadata(started, **fields):
    commit = subprocess.run(['git','rev-parse','HEAD'], cwd=ROOT, check=True,
                            capture_output=True,text=True).stdout.strip()
    return {'schema':'sac-size-execution/1','execution_commit':commit,
            'source_data_commit':P['source_data_commit'], 'source_sha256':hashes(),
            'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
            'platform':platform.platform(),'elapsed_seconds':time.perf_counter()-started,
            **fields}


def finish_metadata(path, value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:value[k] for k in ('stage','N','elapsed_seconds')},ensure_ascii=False),flush=True)


def run_train(args):
    started=time.perf_counter(); N=args.samples; bank=args.bank
    file=args.output/f'calibration_N{N}_bank{bank}.npz'
    if file.exists():
        raise FileExistsError(file)
    B=P['training_draws_per_bank_and_design']; keep=P['retained_upper_tail']
    full=S.SAC.sample_null_statistics(P['state_bits'],N,B,S.rng(401,N,bank))
    saved={}; checks=0
    for index,key in ((1,'basic'),(2,'max_axis')):
        entire=np.sort(full[:,index]); saved[key]=entire[-keep:]
        # Check tail compression against the full reference at all retained
        # values, body quantiles and independent probes; include random ties.
        probes=np.r_[saved[key],entire[::max(1,B//1000)],np.nextafter(saved[key][0],-np.inf)]
        u=S.rng(499,N,bank,index).random(len(probes))
        for policy in S.POLICIES:
            uniforms=None if policy==S.POLICIES[0] else u
            level=S.target(N,policy)
            assert np.array_equal(S.hist_reject(entire,probes,B,level,uniforms),
                                  S.hist_reject(saved[key],probes,B,level,uniforms))
            checks+=len(probes)
    np.savez_compressed(file,**saved)
    spec=S.count_spec(N)
    value=metadata(started,stage='calibration',N=N,bank=bank,draws=B,
                   seed_entropy=[P['base_seed'],401,P['state_bits'],N,bank],
                   complete_array_sha256=S.array_sha256(full), retained_upper_tail=keep,
                   compression_probe_decisions_checked=checks,
                   count_reference={k:v for k,v in spec.items() if k not in ('greater','mass','inclusive')},
                   archive_sha256=hashlib.sha256(file.read_bytes()).hexdigest())
    finish_metadata(file.with_suffix('.json'),value)


def load_calibration(output,N,bank):
    with np.load(output/f'calibration_N{N}_bank{bank}.npz',allow_pickle=False) as data:
        return {key:data[key] for key in data.files}


def run_validate(args):
    started=time.perf_counter();N=args.samples
    file=args.output/f'validation_N{N}.npz'
    if file.exists():
        raise FileExistsError(file)
    V=P['validation_draws_per_design'];keep=P['retained_upper_tail']
    full=S.SAC.sample_null_statistics(P['state_bits'],N,V,S.rng(402,N))
    saved={};summary=[];checks=0;uniform_hashes={}
    values=full[:,0].astype(np.int64)
    saved['count_histogram']=np.bincount(values,minlength=int(values.max())+1)
    minimum=min(S.count_spec(N)['critical'],S.count_spec(N)['randomized_boundary'])
    index=np.flatnonzero(values>=minimum)
    saved['count_values']=values[index];saved['count_indices']=index
    for j,key in ((1,'basic'),(2,'max_axis')):
        saved[key],saved[key+'_indices']=S.upper_tail(full[:,j],keep)
    for method_index,key in ((0,'count'),(1,'basic'),(2,'max_axis')):
        u=S.rng(404,N,method_index).random(V)
        uniform_hashes[key]=S.array_sha256(u)
        for bank in range(P['calibration_banks']):
            cal=load_calibration(args.output,N,bank)
            for policy in S.POLICIES:
                uniform=None if policy==S.POLICIES[0] else u
                if key=='count':
                    decision=S.count_reject(values,N,policy,uniform)
                    compressed=S.count_reject(saved['count_values'],N,policy,
                                              None if uniform is None else u[index])
                else:
                    j=1 if key=='basic' else 2
                    decision=S.hist_reject(cal[key],full[:,j],P['training_draws_per_bank_and_design'],S.target(N,policy),uniform)
                    selected=saved[key+'_indices']
                    compressed=S.hist_reject(cal[key],saved[key],P['training_draws_per_bank_and_design'],S.target(N,policy),
                                             None if uniform is None else u[selected])
                successes=int(decision.sum())
                assert successes==int(compressed.sum())
                selected_indices=index if key=='count' else selected
                assert np.array_equal(decision[selected_indices],compressed)
                # All discarded values are non-rejections; counts agree above.
                checks+=V
                low,high=S.SAC.wilson(successes,V)
                summary.append({'N':N,'bank':bank,'policy':policy,'method':key,
                                'target_iid_size':S.target(N,policy),
                                'reference_ceiling_with_coupling':S.target(N,policy)+S.count_spec(N)['delta'],
                                'validation_draws':V,'rejections':successes,'rate':successes/V,
                                'wilson95_low':low,'wilson95_high':high,
                                'rate_to_target':successes/V/S.target(N,policy)})
    np.savez_compressed(file,**saved)
    value=metadata(started,stage='validation',N=N,draws=V,
                   seed_entropy=[P['base_seed'],402,P['state_bits'],N],
                   complete_array_sha256=S.array_sha256(full),uniform_array_sha256=uniform_hashes,
                   compression_full_decisions_checked=checks,
                   count_candidates_minimum=minimum,retained_upper_tail=keep,
                   archive_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
                   held_out_results=summary,
                   caveat='Shared validation sample across banks. Maximum-axis law represents Row/Column marginals; count is independently generated, so there is no joint-detector null claim.')
    finish_metadata(file.with_suffix('.json'),value)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('train','validate','all'))
    parser.add_argument('--samples',type=int,choices=P['sample_sizes'],required=True)
    parser.add_argument('--bank',type=int,choices=range(P['calibration_banks']))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    if args.stage=='all':
        for bank in range(P['calibration_banks']):
            args.bank=bank
            run_train(args)
        run_validate(args)
    elif args.stage=='train':
        if args.bank is None: parser.error('--bank required for train')
        run_train(args)
    else: run_validate(args)


if __name__=='__main__':main()
