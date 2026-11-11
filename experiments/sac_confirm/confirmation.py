"""Shared, explicit-key evaluator and frozen confirmation bookkeeping."""
import csv
import hashlib
import json
from functools import lru_cache
from pathlib import Path
import sys

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/'sac'))
sys.path.insert(0,str(HERE.parent/'sac_size'))
import batch_ciphers as B
import sac_statistics as SAC
import size_statistics as SIZE

P=json.loads((HERE/'protocol.json').read_text(encoding='utf-8'))
KEY_RECORD=json.loads((HERE/'keys.json').read_text(encoding='utf-8'))
KEYS=KEY_RECORD['keys']
POLICIES=SIZE.POLICIES
METHODS=SAC.METHODS


def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))


def write_csv(path,rows):
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(rows)


def save_json(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def array_digest(values):return hashlib.sha256(np.ascontiguousarray(values).tobytes()).hexdigest()


def input_seed(key_index,replicate):
    return np.random.SeedSequence([P['base_seed'],502,64,key_index,replicate])


def input_words(seed,maximum):
    return np.frombuffer(np.random.default_rng(seed).bytes(maximum*8),dtype='<u2').reshape(-1,4)


def keyed_counts(key,seed,sizes=None,batch_size=None):
    sizes=tuple(P['sample_sizes'] if sizes is None else sizes)
    batch_size=P['batch_size'] if batch_size is None else batch_size
    values=input_words(seed,max(sizes));flips=np.zeros((P['native_rounds_computed'],64,64),dtype=np.uint16)
    stored={}
    for start in range(0,len(values),batch_size):
        bases=values[start:start+batch_size]
        stars=np.repeat(bases[:,None,:],65,axis=1)
        for bit in range(64):stars[:,bit+1,bit//16]^=np.uint16(1<<(bit%16))
        # Pass the key explicitly; never mutate the historical global config.
        for r,output in enumerate(B.rectangle_words(stars.reshape(-1,4),P['native_rounds_computed'],key)):
            output=output.reshape(len(bases),65,4)
            differences=output[:,1:,:]^output[:,:1,:]
            raw=differences.astype('<u2',copy=False).reshape(-1,4).view(np.uint8)
            bits=np.unpackbits(raw,axis=1,bitorder='little').reshape(len(bases),64,64)
            flips[r]+=bits.sum(axis=0,dtype=np.uint16)
        if start+len(bases) in sizes:stored[start+len(bases)]=flips.copy()
    assert set(stored)==set(sizes),'Sample sizes must end at batch boundaries'
    return stored,values


@lru_cache(maxsize=1)
def discovery_bases():
    rows=read_csv(ROOT/P['discovery_folder']/'inputs_rectangle.csv')
    hashes={int(r['replicate']):r['input_sha256'] for r in rows if int(r['N'])==1024}
    assert set(hashes)==set(range(500))
    arrays=[]
    for replicate in range(500):
        values=input_words(np.random.SeedSequence([20261110,201,64,replicate]),1024)
        assert array_digest(values)==hashes[replicate]
        arrays.append(values.view('<u8').reshape(-1))
    return np.unique(np.concatenate(arrays))


def source_hashes():
    paths=list(HERE.glob('*.py'))+[HERE/'protocol.json',HERE/'keys.json',HERE/'requirements.txt']
    paths += [HERE.parent/'sac'/name for name in ('batch_ciphers.py','sac_statistics.py')]
    paths += [HERE.parent/'sac_size'/name for name in ('size_statistics.py','protocol.json')]
    paths += [ROOT/'MODEL2C'/name for name in ('primitif.py','rectangle.py','clefia.py')]
    paths += [ROOT/P['discovery_folder']/'inputs_rectangle.csv',ROOT/KEY_RECORD['historical_keys_source']]
    paths += [ROOT/P['calibration_folder']/f'calibration_N{N}_bank{bank}.{ext}'
              for N in P['sample_sizes'] for bank in P['calibration_banks'] for ext in ('npz','json')]
    return {p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)}


@lru_cache(maxsize=None)
def calibration(N,bank):
    path=ROOT/P['calibration_folder']/f'calibration_N{N}_bank{bank}.npz'
    with np.load(path,allow_pickle=False) as archive:return {k:archive[k] for k in archive.files}


def decisions(stats,key_index,N,bank,policy):
    cal=calibration(N,bank);columns=[];reps=P['replications_per_key']
    for j,method in enumerate(METHODS):
        uniform=None
        if policy==POLICIES[1]:
            uniform=np.random.default_rng(np.random.SeedSequence([P['base_seed'],503,64,key_index,N,j])).random(reps)
        if j==0:result=SIZE.count_reject(stats[:,j],N,policy,uniform)
        else:result=SIZE.hist_reject(cal['basic' if j==1 else 'max_axis'],stats[:,j],1000000,SIZE.target(N,policy),uniform)
        columns.append(result)
    return np.stack(columns,axis=1)


def holm(values):
    p=np.asarray(values,dtype=float);order=np.argsort(p,kind='stable')
    corrected=np.maximum.accumulate(np.minimum(1.,p[order]*(len(p)-np.arange(len(p)))))
    result=np.empty(len(p));result[order]=corrected
    return result


def planned(N,native,method):
    return any((N,native,method)==(x['N'],x['round'],x['comparator']) for x in P['primary_contrasts_per_key'])
