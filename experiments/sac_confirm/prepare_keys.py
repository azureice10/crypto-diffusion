"""Freeze a seed-defined key list without evaluating any cipher outcome."""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def create():
    protocol=json.loads((HERE/'protocol.json').read_text(encoding='utf-8'))
    source=ROOT/'data/reference/utama_seed2026/kunci_horizon.csv'
    with source.open(encoding='utf-8-sig',newline='') as stream:
        excluded={int(r['kunci_hex'],16) for r in csv.DictReader(stream) if r['primitif']=='RECTANGLE-80'}
    default=protocol['default_key_hex']
    used=set(excluded)|{int(default,16)}
    generator=np.random.default_rng(np.random.SeedSequence([protocol['base_seed'],501]))
    keys=[{'key_index':0,'key_id':'default','key_type':'default_control','key_hex':default}]
    rejected=0
    while len(keys)<=protocol['random_keys']:
        value=int.from_bytes(generator.bytes(10),'big')
        if value in used:
            rejected+=1
            continue
        used.add(value);index=len(keys)
        keys.append({'key_index':index,'key_id':f'random_{index:02d}',
                     'key_type':'random','key_hex':f'{value:020x}'})
    record={'schema':'sac-confirmation-keys/1','seed_entropy':[protocol['base_seed'],501],
            'historical_keys_source':source.relative_to(ROOT).as_posix(),
            'historical_keys_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'duplicate_or_historical_draws_rejected':rejected,'keys':keys}
    target=HERE/'keys.json'
    text=json.dumps(record,indent=2)+'\n'
    if target.exists():
        assert json.loads(target.read_text(encoding='utf-8'))==record
    else:target.write_text(text,encoding='utf-8')
    print(json.dumps(record,indent=2))


if __name__=='__main__':create()
