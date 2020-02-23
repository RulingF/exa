# Copyright (c) 2015-2020, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Exa
#########
"""
import os
import sys
import datetime as dt
import logging.config
import yaml
from traitlets import HasTraits, Unicode, default, validate


_base = os.path.abspath(os.path.dirname(__file__))


class Base(HasTraits):
    """A traitlets base class that provides configuration
    and logging utilities. Subclasses define respective
    traits and trait-based logic.
    """

    @staticmethod
    def right_now():
        """Returns the current datetime"""
        return dt.datetime.now()

    @staticmethod
    def time_diff(start):
        """Returns a formatted string of the time difference
        between right now and the passed in datetime"""
        stop = dt.datetime.now()
        return '{:.2f}s'.format((stop - start).total_seconds())

    @property
    def log(self):
        """A configured `logger` object"""
        name = '.'.join([
            self.__module__, self.__class__.__name__
        ])
        return logging.getLogger(name)

    @classmethod
    def from_yml(cls, path):
        """Load an object from a configuration file"""
        return cls(**cls._from_yml(path))

    @staticmethod
    def _from_yml(path):
        """Load a configuration file"""
        with open(path, 'r') as f:
            cfg = yaml.safe_load(f.read())
        return cfg

    def traits(self, *args, **kws):
        # inherit super.__doc__?
        # inherent to traitlets API and
        # of little concern to us here.
        skipme = ['parent', 'config']
        traits = super().traits(*args, **kws)
        return {k: v for k, v in traits.items()
                if k not in skipme}

    def trait_values(self):
        """Return a dictionary of trait names and values"""
        return {k: getattr(self, k) for k in self.traits()}


class Cfg(Base):
    """Exa library configuration object. Manages logging
    configuration and the static asset resource API.
    """
    logdir = Unicode()
    logname = Unicode()
    staticdir = Unicode()

    @property
    def db_conn(self):
        return os.environ.get('EXA_DB_CONN', '')

    @validate('logdir')
    def _validate_logdir(self, prop):
        logdir = prop['value']
        os.makedirs(logdir, exist_ok=True)
        return prop['value']

    @default('logdir')
    def _default_logdir(self):
        base = os.path.expanduser('~')
        return os.path.join(base, '.exa')

    @default('staticdir')
    def _default_staticdir(self):
        return os.path.join(_base, "static")

    def resource(self, name):
        """Return the full path of a named resource
        in the static directory.

        If multiple files with the same name exist,
        **name** should contain the first directory
        as well.

        .. code-block:: python

            import exa
            exa.cfg.resource("myfile")
            exa.cfg.resource("test01/test.txt")
            exa.cfg.resource("test02/test.txt")
        """
        for path, _, files in os.walk(self.staticdir):
            if name in files:
                return os.path.abspath(os.path.join(path, name))


_path = os.path.join(_base, 'conf', 'config.yml')
cfg = Cfg.from_yml(_path)
_path = os.path.join(_base, 'conf', 'logging.yml')
_log = Cfg._from_yml(_path)
_path = os.path.join(cfg.logdir, cfg.logname)
_log['handlers']['file']['filename'] = _path
logging.config.dictConfig(_log)

from ._version import __version__
from .core import (DataFrame, Series, Field3D, Field, Editor, Container,
                   SparseDataFrame)

from .core import Data, Isotopes, Constants, Units
