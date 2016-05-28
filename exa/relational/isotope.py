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
from exa.relational.base import BaseMeta, Base, SessionFactory
from exa.iterative import product_sum_2f, product_add_2


# Mappers are series objects that appear in commonly used dataframe manipulations
symbol_to_radius = None
symbol_to_color = None
symbols_to_radii = None
symbol_to_element_mass = None


class Meta(BaseMeta):
    '''
    This class provides methods available to the :class:`~exa.relational.isotope.Isotope`
    class object used to efficiently look up data stored in the database.
    '''
    def get_by_strid(cls, strid):
        '''
        Get an isotope using a string id.
        '''
        s = SessionFactory()
        return s.query(cls).filter(cls.strid == strid).one()

    def get_by_symbol(cls, symbol):
        '''
        Get an isotope using a string id.
        '''
        s = SessionFactory()
        return s.query(cls).filter(cls.symbol == symbol).all()

    def get_element(cls, name_or_symbol):
        '''
        Get a
        '''
        pass

    def _getitem(cls, key):
        if isinstance(key, str):
            if key[0].isdigit():
                return cls.get_by_strid(key)
            elif len(key) <= 3:
                return cls.get_by_symbol(key)
            return cls.get_by_name(key)

#    _symbols_to_radii_map = None    # {'HH': 1.21, ...}
#    _element_mass_map = None        # See the properties below: this pattern is
#    _Z_to_symbol_map = None         # used so that we cache the result once computed.
#    _symbol_to_Z_map = None         # {'H': 1, ...}
#    _symbol_to_radius_map = None
#    _symbol_to_color_map = None
#    _symbols_to_Z_map = None
#
#    @property
#    def symbols_to_Z_map(self):
#        '''
#        Generate (and store in memory) a quick mapping between symbol pairs
#        (e.g OH) and multiplied Z values (8*1=8).
#        '''
#        if self._symbols_to_Z_map is None:
#            df = atomic.Isotope.table()[['symbol', 'Z']].drop_duplicates('symbol').dropna()
#            s = df['symbol'].values
#            z = df['Z'].values
#            sym_pairs = pd.Series([''.join(pair) for pair in product(s, s)])
#            Z_product = pd.Series([a*b for a, b in product(z, z)])
#            df = pd.DataFrame.from_dict({'symbols': sym_pairs, 'Z_product': Z_product}).set_index('symbols')['Z_product'].astype(np.int64)
#            self._symbols_to_Z_map = df
#        return self._symbols_to_Z_map
#
#
#    @property
#    def element_mass_map(self):
#        '''
#        Dictionary of element keys and element mass values.
#        '''
#        if self._element_mass_map is None:
#            df = self.table()[['symbol', 'mass', 'af']].dropna()
#            df['fmass'] = df['mass'] * df['af']
#            self._element_mass_map = df.groupby('symbol')['fmass'].sum()
#        return self._element_mass_map
#
#    @property
#    def Z_to_symbol_map(self):
#        '''
#        Dictionary of proton number (Z) keys and symbol values.
#        '''
#        if self._Z_to_symbol_map is None:
#            mapper = self.table()[['symbol', 'Z']].drop_duplicates('Z', keep='first').set_index('Z')['symbol']
#            self._Z_to_symbol_map = mapper
#        return self._Z_to_symbol_map
#
#    @property
#    def symbol_to_Z_map(self):
#        '''
#        Dictionary of symbol keys and proton number (Z) values.
#        '''
#        if self._symbol_to_Z_map is None:
#            self._symbol_to_Z_map = self.table()[['symbol', 'Z']].drop_duplicates().set_index('symbol')['Z']
#        return self._symbol_to_Z_map
#
#    @property
#
#    def get_by_strid(self, strid):
#        '''
#        Get stope by string of format 'ZA' (e.g. '1H').
#
#        Args:
#            strid (str): Standard isotope string
#
#        Returns:
#            isotope (:class:`~exa.relational.isotopes.Isotope`): Isotope object
#        '''
#        with scoped_session() as s:
#            obj = s.query(self).filter(self.strid == strid).one()
#        return obj
#
#    def get_by_symbol(self, symbol):
#        '''
#        Get all isotopes with a given symbol.
#
#        Args:
#            symbol (str): Isotope or element 0, 1, or 2 character symbol
#
#        Returns:
#            isotopes (list): List of isotope with the given symbol
#        '''
#        with scoped_session() as s:
#            obj = s.query(self).filter(self.symbol == symbol).all()
#        return obj
#
#    def get_by_szuid(self, szuid):
#        '''
#        Get isotope with a given Szudzik id.
#
#        Args:
#            szuid (int): Szudzik id for a given isotope
#
#        Returns:
#            isotope (:class:`~exa.relational.isotopes.Isotope`): Isotope object
#        '''
#        with scoped_session() as s:
#            obj = s.query(self).filter(self.szuid == szuid).one()
#        return obj
#
#    def get_by_pkid(self, pkid):
#        '''
#        Get isotope with a given primary key (pkid).
#
#        Args:
#            pkid (int): Isotope primary key
#
#        Returns:
#            isotope (:class:`~exa.relational.isotopes.Isotope`): Isotope object
#        '''
#        return SessionFactory().query(self).filter(self.pkid == pkid).one()
#
#    def __getitem__(self, key):
#        '''
#        Custom lookup for isotopes: if string with leading digit, get by
#        istope string id, else get by symbol. If integer, try first to get by
#        Szudzik id, then try to get by primary key id.
#        '''
#        if isinstance(key, str):
#            if key[0].isdigit():
#                return self.get_by_strid(key)
#            else:
#                return self.get_by_symbol(key)
#        elif isinstance(key, int):
#            try:
#                return self.get_by_szuid(key)
#            except:
#                return self.get_by_pkid(key)
#        else:
#            raise TypeError('Key type {0} not supported.'.format(type(key)))


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
    >>> Isotope.symbol_to_mass()['H']
    1.0076788974703454
    >>> Isotope['C']
    [8C, 9C, 10C, 11C, 12C, 13C, 14C, 15C, 16C, 17C, 18C, 19C, 20C, 21C, 22C]
    >>> Isotope['13C'].szuid
    175
    >>> c = Isotope[175]
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
#
#    @classmethod
#    def symbol_to_mass(cls):
#        '''
#        Series containing element symbols and their respective mass (in a.u.).
#
#        >>> Isotope.symbol_to_mass().head()    # .head() used to truncate the full series
#        symbol
#        Ac    227.027752
#        Ag    107.869877
#        Al     26.981539
#        Am    240.630767
#        Ar     39.947843
#        Name: fmass, dtype: float64
#
#        Note:
#            The resulting mass the isotope abundance fraction averaged "element"
#            mass.
#        '''
#        return cls.element_mass_map
#
#    @classmethod
#    def symbol_to_radius(cls):
#        '''
#        Series containing the element symbol and its respective covalent radius.
#
#        >>> Isotope.symbol_to_radius().head()
#        symbol
#        Dga    0.300000
#        H      0.604712
#        D      0.604712
#        T      0.604712
#        He     0.869274
#        Name: radius, dtype: float64
#
#        Note:
#            The covalent radii data are taken from `this reference`_.
#
#            .. _this reference: http://doi.org/10.1039/b801115j
#        '''
#        return cls.symbol_to_radius_map
#
#    @classmethod
#    def symbols_to_radii(cls):
#        '''
#        Series containing element symbol pairs and their respective sum of
#        covalent radii (in a.u.).
#
#        >>> Isotope.symbols_to_radii().head()    # Try without .head()
#        DgaDga    0.600000
#        DgaH      0.904712
#        DgaD      0.904712
#        DgaT      0.904712
#        DgaHe     1.169274
#        Name: radius, dtype: float64
#        '''
#        return cls.symbols_to_radii_map
#
#    @classmethod
#    def symbol_to_color(cls):
#        '''
#        Series containing the element symbol and its color
#
#        >>> Isotope.symbol_to_color().head()
#        symbol
#        Dga    16711935
#        H      10197915
#        D       5263440
#        T       4210752
#        He     14286847
#        Name: color, dtype: int64
#        '''
#        return cls.symbol_to_color_map
#
#    @classmethod
#    def Z_to_symbol(cls):
#        '''
#        Series containing Z number (proton number) and the corresponding symbol.
#
#        >>> Isotope.Z_to_symbol().head()
#        Z
#        0    Dga
#        1      H
#        2     He
#        3     Li
#        4     Be
#        Name: symbol, dtype: object
#        '''
#        return cls.Z_to_symbol_map
#
#    @classmethod
#    def symbol_to_Z(cls):
#        return cls.symbol_to_Z_map
#
#    @classmethod
#    def symbols_to_Z(cls):
#        return cls.symbols_to_Z_map
#
#    def __repr__(self):
#        return '{0}{1}'.format(self.A, self.symbol)
#

# Dynamically create a number of commonly used dataframe mappings after
# static data has been loaded
def init_mappers():
    '''
    Initialize commonly used dataframe mappers (in memory).
    '''
    isotopedf = Isotope.to_frame()
    init_symbols_to_radii(isotopedf)
    init_symbol_to_element_mass(isotopedf)
    init_symbol_to_radius(isotopedf)
    init_symbol_to_color(isotopedf)


def init_symbols_to_radii(isotopedf):
    '''
    Initialize the **symbols_to_radii** mapper
    '''
    global symbols_to_radii
    df = isotopedf.drop_duplicates('symbol')
    symbol = df['symbol'].values
    radius = df['radius'].values
    symbols = product_add_2(symbol, symbol)
    radii = product_sum_2f(radius, radius)
    symbols_to_radii = pd.Series(radii)
    symbols_to_radii.index = symbols


def init_symbol_to_element_mass(isotopedf):
    '''
    Initialize the **symbol_to_element_mass** mapper.
    '''
    global symbol_to_element_mass
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
