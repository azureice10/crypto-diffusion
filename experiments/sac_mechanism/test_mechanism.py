"""Exact identities and synthetic-only smoke tests for mechanism diagnostics."""
import hashlib
import itertools
import json
import unittest

import numpy as np
from scipy.stats import binom

import mechanism as M


class MechanismTests(unittest.TestCase):
    def test_pearson_shape_scatter_identity(self):
        hist=np.array([[6,4],[8,2],[5,5]])
        _,shape,scatter,total=M.parts(hist,np.array([5.,5.]))
        np.testing.assert_allclose(shape+scatter,total)
        self.assertAlmostEqual(float(total.sum()),float(np.mean(np.sum((hist-5)**2/5,axis=1))))
        self.assertAlmostEqual(float(scatter.sum()),float(np.sum(hist.var(axis=0,ddof=0)/5)))

    def test_product_marginal_expectation_and_signed_covariance(self):
        probabilities=np.array([[.2,.8],[.7,.3]])
        expectation=0.
        for state in itertools.product((0,1),repeat=2):
            mass=np.prod([probabilities[i,x] for i,x in enumerate(state)])
            hist=np.bincount(state,minlength=2)
            expectation+=mass*np.sum((hist-1)**2)
        shape=np.sum((probabilities.sum(axis=0)-1)**2)
        scatter=np.sum(probabilities*(1-probabilities))
        self.assertAlmostEqual(expectation,shape+scatter)
        # Perfect positive or negative dependence, same fair marginals.
        for hist,expected_cov in ((np.array([[2,0],[0,2]]),1.),(np.array([[1,1],[1,1]]),-1.)):
            _,_,actual,_=M.parts(hist,np.ones(2))
            self.assertAlmostEqual(float(actual.sum()-1),expected_cov)

    def test_squared_bias_unbiased_even_when_estimate_negative(self):
        support=np.arange(11)
        for p in (.2,.5,.8):
            estimate=M.squared_bias_unbiased(support,10)
            self.assertAlmostEqual(float(np.dot(binom.pmf(support,10,p),estimate)),(p-.5)**2,places=13)
        self.assertLess(M.squared_bias_unbiased(5,10),0.)

    def test_layout_invariance_and_axis_response(self):
        generator=np.random.default_rng(991161)
        p=np.full((64,64),.5);p[:16]=.55
        counts=generator.binomial(256,p).astype(np.uint16)
        actual=M.C.SAC.statistics(counts[None],256)[0]
        shuffled=np.array([generator.permutation(counts.ravel()).reshape(64,64) for _ in range(8)])
        stats=M.C.SAC.statistics(shuffled,256)
        np.testing.assert_array_equal(stats[:,:2],np.broadcast_to(actual[:2],(8,2)))
        self.assertTrue(np.any(np.abs(stats[:,2:]-actual[2:])>1e-6))
        transposed=M.C.SAC.statistics(counts.T[None],256)[0]
        np.testing.assert_allclose(actual[[2,3]],transposed[[3,2]])

    def test_synthetic_surrogate_layout_pipeline(self):
        tag=hashlib.sha256(json.dumps(M.source_hashes(),sort_keys=True).encode()).hexdigest()[:12]
        folder=M.ROOT/'results'/('mechanism-smoke-'+tag);folder.mkdir(parents=True,exist_ok=True)
        if (folder/'execution_layouts.json').exists():self.skipTest('Existing synthetic smoke evidence retained')
        original=dict(M.P)
        try:
            M.P.update(base_seed=991161,replications=8,training_replicates=4,holdout_replicates=4,
                       surrogate_draws=64,layout_permutations_per_parent=4,bootstrap_draws=100,chunk=16)
            generator=np.random.default_rng(991161);counts={}
            for case in M.P['default_cases']:
                probability=.506 if case['round']==7 else .5
                counts[M.case_name(case)]=generator.binomial(case['N'],probability,size=(8,64,64)).astype(np.uint16)
            np.savez_compressed(folder/'default_replayed_counts.npz',**counts)
            M.surrogates(folder);M.layouts(folder)
            rows=M.C.read_csv(folder/'surrogate_summary.csv');self.assertEqual(len(rows),60)
            for row in M.C.read_csv(folder/'layout_summary.csv'):
                if row['method'] in ('basic','count'):self.assertEqual(float(row['permuted_minus_original_rate']),0.)
            with np.load(folder/'surrogate_statistics.npz',allow_pickle=False) as archive:
                self.assertEqual(len(archive.files),9)
                for name in archive.files:self.assertEqual(archive[name].shape,(64,4))
        finally:M.P.clear();M.P.update(original)


if __name__=='__main__':unittest.main(verbosity=2)
