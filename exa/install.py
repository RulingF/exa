# -*- coding: utf-8 -*-
'''
DB Initialization
====================
'''
from itertools import product
from notebook import install_nbextension
from exa import _re as re
from exa import _os as os
from exa import _np as np
from exa import _pd as pd
from exa import _json as json
from exa.config import Config
from exa.relational.base import Base, engine
from exa.relational.isotope import Isotope
from exa.relational.constant import Constant
from exa.relational.unit import Dimension
from exa.relational.container import Container
from exa.utility import mkpath


def install_notebook_widgets(origin_base=Config.nbext, dest_base=Config.extensions,
                             verbose=False):
    '''
    Installs custom :py:mod:`ipywidgets` JavaScript into the Jupyter
    nbextensions directory to allow use of exa's JavaScript frontend
    within the Jupyter notebook GUI.
    '''
    for root, subdirs, files in os.walk(origin_base):
        for filename in files:
            subdir = root.split('nbextensions')[-1]
            orig = mkpath(root, filename)
            dest = mkpath(dest_base, subdir, mkdir=True)
            install_nbextension(orig, verbose=verbose, overwrite=True, nbextensions_dir=dest)


def initialize_database(verbose=False):
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
            if verbose:
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
            tbl.bulk_insert(data)
        else:
            raise NotImplementedError('Updating existing databases not implemented')
    obj = Container(name='test', description='created during install...')    # This prevents FlushError for inherited containers...


def finalize_install(path=None, verbose=False):
    '''
    This function is run after successfully installing this package to install
    some extensions and initialize the database.
    '''
    if path:
        Config['exa'] = path
    else:
        Config['exa'] = mkpath(Config.home, '.exa')
    Config.relational['database'] = 'exa.sqlite'
    initialize_database(verbose=verbose)         # Create the database and tables
    install_notebook_widgets(verbose=verbose)    # Copy widget JS to the Jupyter notebook
