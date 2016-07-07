# -*- coding: utf-8 -*-
'''
Table of Isotopes
###########################################
This module provides an interface for interacting with isotopes of atoms; the
extended periodic table. For convenience, functions are provided for obtaining
traditionally used elements. This module also provides mappers for commonly
used dataframe manipulations.
'''
import numpy as np
import pandas as pd
from itertools import product
from sqlalchemy import String, Float
from sqlalchemy import Column, Integer, String
from exa._config import config
from exa.relational.base import BaseMeta, Base, SessionFactory
from exa.iterative import product_sum_2f, product_add_2


class Meta(BaseMeta):
    '''
    Provides lookup methods for :class:`~exa.relational.isotope.Isotope`.

    .. code-block:: Python

        Isotope['1H']     # Returns
    '''
    def get_by_strid(cls, strid):
        '''
        Get an isotope using a string id.
        '''
        return SessionFactory().query(cls).filter(cls.strid == strid).one()

    def get_by_symbol(cls, symbol):
        '''
        Get an isotope using a string id.
        '''
        return SessionFactory().query(cls).filter(cls.symbol == symbol).all()

    def get_element(cls, name_or_symbol):
        '''
        Get (i.e. compute) the element with the given name or symbol (an
        element's data is given as an average over isotopic composition).
        '''
        raise NotImplementedError()

    def _getitem(cls, key):
        if isinstance(key, str):
            if key[0].isdigit():
                return cls.get_by_strid(key)
            elif len(key) <= 3:
                return cls.get_by_symbol(key)
            return cls.get_by_name(key)


class Isotope(Base, metaclass=Meta):
    '''
    A variant of a chemical element with a specific proton and neutron count.

    >>> h = Isotope['1H']
    >>> h.A
    1
    >>> h.Z
    1
    >>> h.mass
    1.0078250321
    >>> Isotope['C']
    [8C, 9C, 10C, 11C, 12C, 13C, 14C, 15C, 16C, 17C, 18C, 19C, 20C, 21C, 22C]
    >>> Isotope['13C'].szuid
    175
    >>> c = Isotope[57]
    >>> c.A
    13
    >>> c.Z
    6
    >>> c.strid
    '13C'
    '''
    A = Column(Integer, nullable=False)
    Z = Column(Integer, nullable=False)
    af = Column(Float)
    eaf = Column(Float)
    color = Column(Integer)
    radius = Column(Float)
    gfactor = Column(Float)
    mass = Column(Float)
    emass = Column(Float)
    name = Column(String(length=16))
    eneg = Column(Float)
    quadmom = Column(Float)
    spin = Column(Float)
    symbol = Column(String(length=3))
    szuid = Column(Integer)
    strid = Column(Integer)

    def __repr__(self):
        return '{0}{1}'.format(self.A, self.symbol)


def symbol_to_z():
    '''
    Create a "mapper" (:class:`~pandas.Series`) from element symbol to proton
    number ("Z"). This object can be used to quickly transform element symbols
    to proton number via:

    .. code-block:: Python

        mapper = symbol_to_z()
        z_series = symbol_series.map(mapper)
    '''
    df = Isotope.to_frame().drop_duplicates('symbol').sort_values('symbol')
    return df.set_index('symbol')['Z']


def z_to_symbol():
    '''
    Create a mapper from proton number to element symbol.

    See Also:
        Opposite mapper of :func:`~exa.relational.isotope.symbol_to_z`.
    '''
    df = Isotope.to_frame().drop_duplicates('Z').sort_values('Z')
    return df.set_index('Z')['symbol']


def symbols_to_radii():
    '''Mapper from symbol pairs to sum of covalent radii.'''
    df = Isotope.to_frame().drop_duplicates('symbol')
    symbol = df['symbol'].values
    radius = df['radius'].values
    symbols = [x + y for x, y in product(symbol, symbol)]
    s = pd.Series(sum_product_pair_f8(radius, radius))
    s.index = symbols
    return s


def symbol_to_element_mass():
    '''Mapper from symbol to element mass.'''
    isotopedf['fmass'] = isotopedf['mass'] * isotopedf['af']
    topes = isotopedf.groupby('name')
    n = topes.ngroups
    masses = np.empty((n, ), dtype=np.float64)
    symbols = np.empty((n, ), dtype='O')
    for i, (name, element) in enumerate(topes):
        symbols[i] = element['symbol'].values[-1]
        masses[i] = element['fmass'].sum()
    symbol_to_element_mass = pd.Series(masses)
    symbol_to_element_mass.index = symbols


def init_symbol_to_radius(isotopedf):
    '''
    Initialize the **symbol_to_radius** mapper.
    '''
    global symbol_to_radius
    symbol_to_radius = isotopedf.drop_duplicates('symbol')
    symbol_to_radius = symbol_to_radius.set_index('symbol')['radius']


def init_symbol_to_color(isotopedf):
    '''
    Initialize the **symbol_to_color** mapper.
    '''
    global symbol_to_color
    symbol_to_color = isotopedf.drop_duplicates('symbol')
    symbol_to_color = symbol_to_color.set_index('symbol')['color']
