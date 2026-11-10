"""Vector scheduling of unchanged RECTANGLE/CLEFIA native trace operations.

Used only by the targeted SAC follow-up; production measurement code remains
unchanged. Inputs/outputs are arrays of four words, least-significant first.
"""
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'MODEL2C'))
import primitif as P


def anf_masks(box, output_bit):
    values = np.array([(x >> output_bit) & 1 for x in box], dtype=np.uint8)
    for bit in range(4):
        for mask in range(16):
            if mask & (1 << bit):
                values[mask] ^= values[mask ^ (1 << bit)]
    return [int(i) for i in np.flatnonzero(values)]


ANF = [anf_masks(P.R.s_box, bit) for bit in range(4)]


def rectangle_words(values, rounds=8, key=None):
    key = int(P.RECT_KEY, 16) if key is None else key
    keys = P.R.key_extend_80(P.R.key_from_hex(f'{key:020x}'))
    state = np.asarray(values, dtype=np.uint16).copy()
    for index in range(rounds):
        state ^= np.asarray(keys[index], dtype=np.uint16)
        terms = {0: np.full(len(state), 65535, dtype=np.uint16)}
        for mask in range(1, 16):
            low = mask & -mask
            bit = low.bit_length() - 1
            terms[mask] = terms[mask ^ low] & state[:, bit]
        output = np.zeros_like(state)
        for bit in range(4):
            for mask in ANF[bit]:
                output[:, bit] ^= terms[mask]
        for bit, shift in ((1,1), (2,12), (3,13)):
            output[:, bit] = (output[:, bit] << shift) | (output[:, bit] >> (16-shift))
        state = output
        yield state


def f_tables(function):
    constant = function(0, 0)
    tables = [np.array([function(0, x << shift) ^ constant for x in range(256)], dtype=np.uint32)
              for shift in (24,16,8,0)]
    return np.uint32(constant), tables


F0 = f_tables(P.C.f0)
F1 = f_tables(P.C.f1)


def f_vector(values, key, description):
    constant, tables = description
    values = values ^ np.uint32(key)
    result = np.full(len(values), constant, dtype=np.uint32)
    for table, shift in zip(tables, (24,16,8,0)):
        result ^= table[(values >> shift) & 255]
    return result


def clefia_words(values, rounds=7, key=None):
    key = P.CLEFIA_KEY if key is None else int(key).to_bytes(16,'big')
    wk, rk = P.C.key_schedule_128(key)
    state = np.asarray(values, dtype=np.uint32)[:, ::-1].copy()
    state[:,1] ^= np.uint32(wk[0])
    state[:,3] ^= np.uint32(wk[1])
    for index in range(rounds):
        state = np.stack((state[:,1] ^ f_vector(state[:,0],rk[2*index],F0),
                          state[:,2],
                          state[:,3] ^ f_vector(state[:,2],rk[2*index+1],F1),
                          state[:,0]), axis=1)
        yield state[:, ::-1].copy()


CONFIG = {
    'rectangle': {'bits':64, 'word_bits':16, 'rounds':8,
                  'analysis_rounds':[4,5,6,7,8], 'function':rectangle_words,
                  'key_hex':P.RECT_KEY, 'source_key':'rectangle'},
    'clefia': {'bits':128, 'word_bits':32, 'rounds':7,
               'analysis_rounds':[3,4,5,6,7], 'function':clefia_words,
               'key_hex':P.CLEFIA_KEY.hex(), 'source_key':'clefia'},
}


def avalanche_counts(name, seed, sample_sizes=(64,256,1024), batch_size=32):
    """Paired/nested samples, same full SAC matrix for every compared detector."""
    cfg = CONFIG[name]
    n, word_bits, rounds = cfg['bits'], cfg['word_bits'], cfg['rounds']
    dtype = np.dtype('<u2' if word_bits == 16 else '<u4')
    rng = np.random.default_rng(seed)
    values = np.frombuffer(rng.bytes(max(sample_sizes)*n//8), dtype=dtype).reshape(-1,4)
    flips = np.zeros((rounds,n,n), dtype=np.uint16)
    stored = {}
    for start in range(0,len(values),batch_size):
        bases = values[start:start+batch_size]
        stars = np.repeat(bases[:,None,:], n+1, axis=1)
        for bit in range(n):
            stars[:,bit+1,bit//word_bits] ^= np.array(1 << (bit % word_bits), dtype=dtype)
        for r, output in enumerate(cfg['function'](stars.reshape(-1,4),rounds)):
            output = output.reshape(len(bases),n+1,4)
            differences = output[:,1:,:] ^ output[:,:1,:]
            raw = differences.astype(dtype,copy=False).reshape(-1,4).view(np.uint8)
            bits = np.unpackbits(raw, axis=1, bitorder='little').reshape(len(bases),n,n)
            flips[r] += bits.sum(axis=0,dtype=np.uint16)
        stop = start + len(bases)
        if stop in sample_sizes:
            stored[stop] = flips.copy()
    if set(stored) != set(sample_sizes):
        raise ValueError('Sample sizes must coincide with batch boundaries')
    return stored, values
