# -*- coding: utf-8 -*-
from exa import _conf

if _conf['pkg_numba']:
    from exa.algorithms.jitted import vmag3, vdist3
    from exa.algorithms.jitted import (arange1, arange2, unordered_pairing,
                                       indexes_sc1, indexes_sc2)
    from exa.algorithms.jitted import pdist, supercell3d, meshgrid3d
else:
    from exa.algorithms.broadcasting import vmag3, vdist3
    from exa.algorithms.indexing import (arange1, arange2, unordered_pairing,
                                         indexes_sc1, indexes_sc2)
    from exa.algorithms.iteration import pdist, supercell3d, meshgrid3d
