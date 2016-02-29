# -*- coding: utf-8 -*-
'''
Indexing Recipes
=====================
Functions related to generating indexes
'''
from exa import _np as np


def idxs_from_starts_and_counts(starts, counts):
    '''
    Generates flat indexes from starting points (starts) and counts
    with incrementing by 1.
    '''
    n = np.sum(counts)
    i_idx = np.empty((n, ), dtype='i8')
    j_idx = i_idx.copy()
    values = j_idx.copy()
    h = 0
    for i, start in enumerate(starts):
        stop = start + counts[i]
        for j, value in enumerate(range(start, stop)):
            i_idx[h] = i
            j_idx[h] = j
            values[h] = value
            h += 1
    return (i_idx, j_idx, values)


def idxs_from_starts_and_count(starts, count):
    '''
    '''
    n = len(starts)
    i_idx = np.empty((n * count, ), dtype='i8')
    j_idx = i_idx.copy()
    values = j_idx.copy()
    h = 0
    for i, start in enumerate(starts):
        stop = start + count
        for j, value in enumerate(range(start, stop)):
            i_idx[h] = i
            j_idx[h] = j
            values[h] = value
            h += 1
    return (i_idx, j_idx, values)


def _unordered_pairing_function(x, y):
    '''
    http://www.mattdipasquale.com/blog/2014/03/09/unique-unordered-pairing-function/
    '''
    return np.int64(x * y + np.trunc((np.abs(x - y) - 1)**2 / 4))

unordered_pairing_function = np.vectorize(_unordered_pairing_function)
