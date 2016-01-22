# -*- coding: utf-8 -*-
'''
Tools
====================
Require internal (exa) imports.
'''
import shutil
from itertools import product
from notebook import install_nbextension
from exa import _re as re
from exa import _os as os
from exa import _np as np
from exa import _pd as pd
from exa import _json as json
from exa.config import Config
from exa.utils import mkpath
from exa.relational.base import Base, engine
from exa.relational.isotopes import Isotope
from exa.relational.constants import Constant
from exa.relational.units import Dimension


def install_notebook_widgets(path=None, verbose=False):
    '''
    Installs custom :py:mod:`ipywidgets` JavaScript into the Jupyter
    nbextensions directory to allow use of exa's JavaScript frontend
    within the Jupyter notebook GUI.
    '''
    try:
        shutil.rmtree(Config.extensions)
    except:
        pass
    for i, r in enumerate([Config.nbext]):
        for root, subdirs, files in os.walk(r):
            for filename in files:
                low = filename.lower()
                if not low.endswith('json'):
                    subdir = root.split('exa')[-1]
                    orig = mkpath(root, filename)
                    dest = mkpath(Config.extensions, subdir, mkdir=True)
                    install_nbextension(
                        orig,
                        verbose=verbose,
                        overwrite=True,
                        nbextensions_dir=dest
                    )


def initialize_database(force=False):
    '''
    Generates the static relational database tables for isotopes, constants,
    and unit conversions.
    '''
    Base.metadata.create_all(engine)     # Create the database and tables
    constants = None
    units = None
    isotopes = None                      # Load only if needed
    with open(mkpath(Config.static, 'constants.json')) as f:
        constants = json.load(f)
    with open(mkpath(Config.static, 'units.json')) as f:
        units = json.load(f)
    for tbl in Dimension.__subclasses__() + [Isotope, Constant]:
        count = 0
        name = tbl.__tablename__
        try:
            count = len(tbl)
        except:
            pass
        if count == 0:
            print('Loading {0} data'.format(name))
            if name == 'isotope':
                data = pd.read_json(mkpath(Config.static, 'isotopes.json'))
                data.sort_values(['Z', 'A'], inplace=True)
                data.reset_index(drop=True, inplace=True)
                data = data.to_dict(orient='records')
            elif name == 'constant':
                data = [{'symbol': k, 'value': v} for k, v in constants[name].items()]
            else:
                data = units[name]
                labels = list(data.keys())
                values = np.array(list(data.values()))
                cols = list(product(labels, labels))
                values_t = values.reshape(len(values), 1)
                fac = (values / values_t).ravel()
                data = [{'from_unit': cols[i][0], 'to_unit': cols[i][1], 'factor': v} for i, v in enumerate(fac)]
            tbl._bulk_insert(data)
        elif force:
            raise NotImplementedError('Updating constants, isotopes, and unit conversions is not yet available')
