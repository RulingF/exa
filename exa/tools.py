'''
Tools
====================
Require internal (exa) imports.
'''
import shutil
from itertools import product
from notebook import install_nbextension
from exa import Config
from exa import _re as re
from exa import _os as os
from exa import _np as np
from exa import _json as json
from exa.utils import mkpath
from exa.relational.isotope import Isotope
from exa.relational.units import Dimension
from exa.relational.constans import Constant


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
    for i, r in enumerate([Config.templates, Config.static]):
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
    constants = None
    units = None
    isotopes = None    # Load only if needed
    with open(mkpath(Config.static, 'constants.json')) as f:
        constants = json.load(f)
    with open(mkpath(Config.static, 'units.json')) as f:
        units = json.load(f)
    for tbl in Dimension.__subclasses__() + [Isotope, Constant]:
        count = 0
        name = tbl.__tablename__
        try:
            count = tbl.count()
        except:
            pass
        if count == 0:
            print('Loading {0} data'.format(name))
            if name == 'isotope':
                data = None
                with open(mkpath(Config.static, 'isotopes.json')) as f:
                    data = json.load(f)
            elif name == 'constants':
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
