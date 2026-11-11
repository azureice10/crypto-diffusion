"""Nontrivial checks of random-rank validity, exact count size and truncation."""
import itertools
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

import numpy as np

import size_statistics as S


class SizeMatchingTests(unittest.TestCase):
    def test_randomized_rank_uniform_even_with_ties(self):
        # Exhaust all IID Bernoulli statistic samples (three calibration +
        # one observation), integrating the tie uniform analytically.
        for mass in (.2,.5,.8):
            for alpha in (.01,.13,.4,.9):
                rejection=0.;nonrandom=0.
                for sample in itertools.product((0,1),repeat=4):
                    probability=np.prod([mass if v else 1-mass for v in sample])
                    cal=np.array(sample[:3]);obs=sample[3]
                    greater=int((cal>obs).sum());equal=int((cal==obs).sum())
                    fraction=np.clip((alpha*4-greater)/(equal+1),0,1)
                    rejection+=probability*fraction
                    nonrandom+=probability*((1+greater+equal)/4 < alpha)
                self.assertAlmostEqual(rejection,alpha,places=13)
                self.assertLessEqual(nonrandom,alpha+1e-14)

    def test_exact_count_randomization_and_historical_rule(self):
        for samples in S.PROTOCOL['sample_sizes']:
            spec=S.count_spec(samples);a=spec['randomized_label_target']
            # Divide only the unique partial-rejection boundary; no huge
            # ratios on numerically negligible, already certain tail events.
            probability=np.where(spec['greater']+spec['mass']<=a,1.,0.)
            partial=(spec['greater']<a)&(spec['greater']+spec['mass']>a)
            probability[partial]=(a-spec['greater'][partial])/spec['mass'][partial]
            exact=np.dot(spec['mass'],np.clip(probability,0,1))
            self.assertAlmostEqual(exact,a,places=13)
            self.assertLess(spec['iid_size']+spec['delta'],.001)
            self.assertGreaterEqual(spec['inclusive'][spec['critical']-1]+spec['delta'],.001)
            vals=np.arange(4097)
            self.assertTrue(np.array_equal(S.count_reject(vals,samples,S.POLICIES[0]),
                                            spec['inclusive']+spec['delta']<.001))

    def test_compressed_tail_including_cut_ties(self):
        full=np.repeat(np.arange(20),10).astype(float)
        tail=full[-37:]  # Cuts through the tie at value 16.
        probes=np.r_[np.arange(-1,22),np.nextafter(19.,np.inf)]
        for u in (0.,.1,.5,.999):
            uniform=np.full(len(probes),u)
            for randomness in (None,uniform):
                self.assertTrue(np.array_equal(S.hist_reject(full,probes,len(full),.08,randomness),
                                               S.hist_reject(tail,probes,len(full),.08,randomness)))

    def test_padded_holm(self):
        values=S.holm90([.0001,.001,.1])
        np.testing.assert_allclose(values,[.009,.089,1.])

    def test_reject_inadequate_tail_with_large_tie_group(self):
        with self.assertRaises(AssertionError):
            S.hist_reject(np.ones(40),np.array([1.]),200,.08,np.array([.01]))

    def test_end_to_end_with_separate_smoke_seed(self):
        import run_size_match as R
        import analyze_size_match as A
        import verify_size_match as V
        # Deliberately unrelated seeds and small banks: no inspection of
        # the main experiment's fresh calibration/validation draws.
        old=dict(S.PROTOCOL)
        tag=hashlib.sha256(json.dumps(R.hashes(),sort_keys=True).encode()).hexdigest()[:12]
        output=R.ROOT/'results'/('sac-size-smoke-'+tag)
        output.mkdir(parents=True,exist_ok=True)
        if list(output.glob('*.npz')):
            self.skipTest('Existing smoke records retained; use a fresh output for another pipeline run')
        try:
            S.PROTOCOL.update(base_seed=991199,training_draws_per_bank_and_design=2500,
                              validation_draws_per_design=3000,retained_upper_tail=500)
            for N in S.PROTOCOL['sample_sizes']:
                args=SimpleNamespace(samples=N,output=output)
                for bank in range(3):
                    args.bank=bank;R.run_train(args)
                R.run_validate(args)
            A.analyze(output)
            report=V.verify(output)
            self.assertEqual(report['status'],'PASS')
            self.assertEqual(report['calibration_draws'],22500)
            self.assertEqual(report['held_out_draws'],9000)
        finally:
            S.PROTOCOL.clear();S.PROTOCOL.update(old)


if __name__=='__main__':unittest.main(verbosity=2)
