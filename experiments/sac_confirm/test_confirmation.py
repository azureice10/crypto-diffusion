"""Explicit random-key scalar conformance and an unrelated-seed smoke run."""
import hashlib
import json
import unittest

import numpy as np

import confirmation as C


class ConfirmationTests(unittest.TestCase):
    def test_all_keys_full_native_scalar_traces(self):
        rng=np.random.default_rng(991151)
        values=[0,(1<<64)-1]+[1<<i for i in range(64)]+[int(x) for x in rng.integers(0,2**64,size=32,dtype=np.uint64)]
        words=np.array([[(x>>(16*j))&65535 for j in range(4)] for x in values],dtype='<u2')
        comparisons=0
        for key in C.KEYS:
            scalar=C.B.P.PRIMITIVES['rectangle'].with_key(int(key['key_hex'],16))
            expected=[scalar(x) for x in values]
            for r,state in enumerate(C.B.rectangle_words(words,25,int(key['key_hex'],16))):
                actual=[sum(int(w)<<(16*j) for j,w in enumerate(row)) for row in state]
                self.assertEqual(actual,[x[r] for x in expected]);comparisons+=len(values)
        self.assertEqual(comparisons,22050)
        print(json.dumps({'full_native_scalar_states':comparisons,'keys':9}),flush=True)

    def test_all_keys_scalar_full_count_matrices(self):
        for key in C.KEYS:
            seed=np.random.SeedSequence([991151,599,key['key_index']])
            matrices,values=C.keyed_counts(int(key['key_hex'],16),seed,(2,),batch_size=2)
            scalar=C.B.P.PRIMITIVES['rectangle'].with_key(int(key['key_hex'],16))
            oracle=np.zeros((8,64,64),dtype=np.uint16)
            for row in values:
                x=sum(int(w)<<(16*j) for j,w in enumerate(row));base=scalar(x)
                for bit in range(64):
                    trace=scalar(x^(1<<bit))
                    for r in range(8):oracle[r,bit]+=np.array([((base[r]^trace[r])>>j)&1 for j in range(64)],dtype=np.uint16)
            np.testing.assert_array_equal(matrices[2],oracle)

    def test_pipeline_unrelated_smoke_inputs(self):
        import run_confirmation as R
        import analyze_confirmation as A
        import verify_confirmation as V
        import plot_confirmation as F
        tag=hashlib.sha256(json.dumps(C.source_hashes(),sort_keys=True).encode()).hexdigest()[:12]
        folder=C.ROOT/'results'/('sac-key-smoke-'+tag);folder.mkdir(parents=True,exist_ok=True)
        if list(folder.glob('*_metadata.json')):self.skipTest('Existing smoke evidence retained')
        old=dict(C.P)
        try:
            C.P.update(base_seed=991151,replications_per_key=3)
            for key in C.KEYS:R.run_key(key['key_index'],folder)
            A.analyze(folder);report=V.verify(folder,True);F.plot(folder)
            self.assertEqual(report['status'],'PASS');self.assertEqual(report['new_cipher_replications'],27)
        finally:C.P.clear();C.P.update(old)


if __name__=='__main__':unittest.main(verbosity=2)
