# -*- coding: utf-8 -*-
'''
Loop Intensive Jitted Algorithms
==================================
'''
from exa import _np as np
from exa.jitted import jit, float64


@jit(nopython=True, cache=True)
def periodic_supercell(ijk, ei, ej, ek):
    '''
    '''
    multipliers = [-1, 0, 1]
    n = len(ijk)
    periodic = np.empty((n * 27, 3), dtype=float64)
    h = 0
    for i in multipliers:
        for j in multipliers:
            for k in multipliers:
                for l in range(n):
                    periodic[h, 0] = ijk[l, 0] + i * ei
                    periodic[h, 1] = ijk[l, 1] + j * ej
                    periodic[h, 2] = ijk[l, 2] + k * ek
                    h += 1
    return periodic
