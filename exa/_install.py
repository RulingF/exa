# -*- coding: utf-8 -*-
'''
Installer
########################
This module allows a user to install exa in a persistent manner enabling some
advanced content management features. Installation will create a permanent
directory where exa's relational database will be housed (default ~/.exa).
All container creation, logging, and static data is housed in this directory.
'''
import os
import shutil
import platform
import pandas as pd
from itertools import product
from notebook import install_nbextension
from exa import global_config
from exa._config import update_config, save_config
from exa._config import cleanup as config_cleanup
from exa.log import setup_loggers
from exa.relational.base import cleanup as rel_cleanup
from exa.relational.base import create_tables, init_db, engine
from exa.relational.update import drop_all_static_tables
from exa.utility import mkp


def install(persist=False):
    '''
    Initializes exa's database and notebook widget features.

    By default, exa runs in memory. To take full advantage of exa's content
    management features this function should be run. It will create a storage
    location in **~/.exa** where all configuration, log, and data are housed.

    Args:
        exa_root (str): If None assumes temporary session, otherwise directory path where the package will be installed
    '''
    if persist:
        rel_cleanup()
        config_cleanup()
        if platform.system().lower() == 'windows':
            dot_exa = mkp(os.getenv('USERPROFILE'), '.exa')
        else:
            dot_exa = mkp(os.getenv('HOME'), '.exa')
        mkp(dot_exa, mk=True)
        update_config()
        save_config()
        init_db()
        global engine
        from exa.relational.base import engine
        setup_loggers()
    update()


def update():
    '''
    If upgrading to a new version of exa, update static databases as needed.
    '''
    try:
        drop_all_static_tables()
    except:
        pass
    create_tables()
    load_isotope_data()
    load_unit_data()
    load_constant_data()
    install_notebook_widgets(global_config['nbext_localdir'], global_config['nbext_sysdir'])


def load_isotope_data():
    '''
    Load isotope data (from isotopes.json) into the database.
    '''
    df = pd.read_json(global_config['static_isotopes.json'], orient='values')
    df.columns = ('A', 'Z', 'af', 'eaf', 'color', 'radius', 'gfactor', 'mass', 'emass',
                  'name', 'eneg', 'quadmom', 'spin', 'symbol', 'szuid', 'strid')
    df.index.names = ['pkid']
    df.reset_index(inplace=True)
    df.to_sql(name='isotope', con=engine, index=False, if_exists='replace')


def load_unit_data():
    '''
    Load unit conversions (from units.json) into the database.
    '''
    df = pd.read_json(global_config['static_units.json'])
    for column in df.columns:
        series = df[column].copy().dropna()
        values = series.values
        labels = series.index
        n = len(values)
        factor = (values.reshape(1, n) / values.reshape(n, 1)).ravel()
        from_unit, to_unit = list(zip(*product(labels, labels)))
        df_to_save = pd.DataFrame.from_dict({'from_unit': from_unit, 'to_unit': to_unit, 'factor': factor})
        df_to_save['pkid'] = df_to_save.index
        df_to_save.to_sql(name=column, con=engine, index=False, if_exists='replace')


def load_constant_data():
    '''
    Load constants (from constants.json) into the database.
    '''
    df = pd.read_json(global_config['static_constants.json'])
    df.reset_index(inplace=True)
    df.columns = ['symbol', 'value']
    df['pkid'] = df.index
    df.to_sql(name='constant', con=engine, index=False, if_exists='replace')


def install_notebook_widgets(origin_base, dest_base, verbose=False):
    '''
    Convenience wrapper around :py:func:`~notebook.install_nbextension` that
    installs Jupyter notebook extensions using a systematic naming convention (
    mimics the source directory and file name structure rather than installing
    as a flat file set).

    This function will read the special file "__paths__" to collect dependencies
    not present in the nbextensions directory.

    Args:
        origin_base (str): Location of extension source code
        dest_base (str): Destination location (system and/or user specific)
        verbose (bool): Verbose installation (default False)

    See Also:
        The configuration module :mod:`~exa._config` describes the default
        arguments used by :func:`~exa._install.install` during installation.
    '''
    try:
        shutil.rmtree(dest_base)
    except:
        pass
    for root, subdirs, files in os.walk(origin_base):
        for filename in files:
            subdir = root.split('nbextensions')[-1]
            orig = mkp(root, filename)
            dest = mkp(dest_base, subdir, mk=True)
            install_nbextension(orig, verbose=verbose, overwrite=True, nbextensions_dir=dest)
