"""Generate fresh explicit-key RECTANGLE SAC matrices and sufficient records."""
import argparse
import json
import platform
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import scipy

import confirmation as C


def run_key(index,folder):
    started=time.perf_counter();key=C.KEYS[index];reps=C.P['replications_per_key']
    prefix=folder/key['key_id']
    for suffix in ('_raw.csv','_inputs.csv','_arrays.npz','_metadata.json'):
        if Path(str(prefix)+suffix).exists():raise FileExistsError(str(prefix)+suffix)
    raw=[];inputs=[];arrays={};bases=[]
    selected=np.array(C.P['analysis_rounds'])-1
    snapshots=sorted({0,1,2,reps-1}&set(range(reps)))
    for N in C.P['sample_sizes']:
        arrays[f'value_hist_N{N}']=np.zeros((reps,len(selected),N+1),dtype=np.uint16)
        for direction in ('row','col'):arrays[f'{direction}_hist_N{N}']=np.zeros((reps,len(selected),64,8),dtype=np.uint8)
        arrays[f'sum_counts_N{N}']=np.zeros((len(selected),64,64),dtype=np.uint64)
        arrays[f'sum_squared_counts_N{N}']=np.zeros((len(selected),64,64),dtype=np.uint64)
    for replicate in range(reps):
        seed=C.input_seed(index,replicate)
        matrices,values=C.keyed_counts(int(key['key_hex'],16),seed)
        bases.append(values.view('<u8').reshape(-1))
        for N,full in matrices.items():
            counts=full[selected];stats=C.SAC.statistics(counts,N)
            inputs.append({'key_id':key['key_id'],'key_index':index,'key_hex':key['key_hex'],
                           'replicate':replicate,'N':N,'seed_entropy':json.dumps(seed.entropy),
                           'input_sha256':C.array_digest(values[:N]),'query_budget':N*65})
            for ri,native in enumerate(C.P['analysis_rounds']):
                row={'key_id':key['key_id'],'key_index':index,'key_type':key['key_type'],
                     'key_hex':key['key_hex'],'replicate':replicate,'N':N,'native_round':native,
                     'count_matrix_sha256':C.array_digest(counts[ri])}
                row.update({'stat_'+m:float(stats[ri,j]) for j,m in enumerate(C.METHODS)})
                raw.append(row)
                arrays[f'value_hist_N{N}'][replicate,ri]=np.bincount(counts[ri].ravel(),minlength=N+1)
            _,_,labels=C.SAC.bin_description(N);categories=labels[counts]
            arrays[f'row_hist_N{N}'][replicate]=np.stack([(categories==j).sum(axis=-1) for j in range(8)],axis=-1)
            arrays[f'col_hist_N{N}'][replicate]=np.stack([(categories==j).sum(axis=-2) for j in range(8)],axis=-1)
            numeric=counts.astype(np.uint64)
            arrays[f'sum_counts_N{N}']+=numeric
            arrays[f'sum_squared_counts_N{N}']+=numeric**2
            if replicate in snapshots:arrays[f'snapshot_rep{replicate}_N{N}']=full
        if (replicate+1)%100==0:
            print(json.dumps({'key':key['key_id'],'replications':replicate+1,
                              'elapsed_seconds':time.perf_counter()-started}),flush=True)
    C.write_csv(Path(str(prefix)+'_raw.csv'),raw)
    C.write_csv(Path(str(prefix)+'_inputs.csv'),inputs)
    array_path=Path(str(prefix)+'_arrays.npz');np.savez_compressed(array_path,**arrays)
    all_bases=np.concatenate(bases);unique=np.unique(all_bases)
    overlap=np.intersect1d(unique,C.discovery_bases(),assume_unique=True)
    commit=subprocess.run(['git','rev-parse','HEAD'],cwd=C.ROOT,check=True,capture_output=True,text=True).stdout.strip()
    record={'schema':'sac-key-confirmation-execution/1','key':key,'execution_commit':commit,
            'source_sha256':C.source_hashes(),'replications':reps,'sample_sizes':C.P['sample_sizes'],
            'analysis_rounds':C.P['analysis_rounds'],'snapshot_replicates':snapshots,
            'input_bases':len(all_bases),'unique_input_bases':len(unique),
            'duplicate_input_bases':len(all_bases)-len(unique),'discovery_base_intersection':len(overlap),
            'sorted_unique_base_sha256':C.array_digest(unique),
            'freshness_scope':'Base inputs only; does not exhaustively compare every one-bit-neighbor query',
            'scheduled_trace_inputs':reps*max(C.P['sample_sizes'])*65,
            'raw_rows':len(raw),'input_prefix_rows':len(inputs),
            'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
            'platform':platform.platform(),'elapsed_seconds':time.perf_counter()-started,
            'output_sha256':{p.name:C.digest(p) for p in (array_path,Path(str(prefix)+'_raw.csv'),Path(str(prefix)+'_inputs.csv'))}}
    C.save_json(Path(str(prefix)+'_metadata.json'),record)
    print(json.dumps({'status':'completed','key':key['key_id'],'elapsed_seconds':record['elapsed_seconds'],
                      'duplicate_bases':record['duplicate_input_bases'],'old_base_overlap':record['discovery_base_intersection']}),flush=True)
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--key-indices',type=int,nargs='+',required=True,choices=range(len(C.KEYS)))
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    for index in args.key_indices:run_key(index,args.output)


if __name__=='__main__':main()
