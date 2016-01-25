# -*- coding: utf-8 -*-
'''
Container
===============================================
'''
from ipywidgets import DOMWidget
from traitlets import Unicode
from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from exa import _pd as pd
from exa import _np as np
from exa.frames import DataFrame
from exa.relational.base import Column, Integer, Base, Name, HexUID, Time, Disk


ContainerFile = Table(
    'containerfile',
    Base.metadata,
    Column('container_pkid', Integer, ForeignKey('container.pkid', onupdate='CASCADE', ondelete='CASCADE')),
    Column('file_pkid', Integer, ForeignKey('file.pkid', onupdate='CASCADE', ondelete='CASCADE'))
)


class Container(DOMWidget, Name, HexUID, Time, Disk, Base):
    '''
    Containers control data manipulation, processing, and provide convenient
    visualizations.

    This class defines a table schema for storing metadata about data
    processing and provides some convience methods for visualization. The
    latter feature is especially relevant for data specific containers where,
    knowledge about the structure of the data can provide useful, interactive,
    2D/3D visualizations.

    Warning:
        The correct way to set DataFrame object is as follows:

        .. code-block:: Python

            c = exa.Container()
            df = pd.DataFrame()
            c['name'] = df
            # or
            setattr(c, 'name', df)

        Avoid setting objects using the **__dict__** attribute as follows:

        .. code-block:: Python

            universe = atomic.Universe()
            c = exa.Container()
            df = pd.DataFrame()
            c.name = df

        (This is used in **__init__** where type control is enforced.)

    See Also:
        :class:`~exa.session.Session`
    '''
    container_type = Column(String(16))
    files = relationship('File', secondary=ContainerFile, backref='containers', cascade='all, delete')
    __mapper_args__ = {
        'polymorphic_identity': 'container',   # This allows the container to
        'polymorphic_on': container_type,      # be inherited.
        'with_polymorphic': '*'
    }
    __dfclasses__ = {}
    _ipy_disp = DOMWidget._ipython_display_

    def to_archive(self, path):
        '''
        Export this container to an archive that can be imported elsewhere.
        '''
        raise NotImplementedError()

    @classmethod
    def from_archive(cls, path):
        '''
        Import a container from an archive into the current active session.

        Note:
            This function will also create file entries and objects
            corresponding to the data provided in the archive.
        '''
        raise NotImplementedError()

    @property
    def get_df_dict(self):
        '''
        Return:
            dfs (dict): Dictionary of dataframes (key is the dataframe name)
        '''
        return {n: v for n, v in vars(self).items() if isinstance(v, pd.DataFrame)}

    def copy(self):
        '''
        Create a copy of the current object
        '''
        cls = self.__class__
        kwargs = {name: df.copy() for name, df in self.dataframes}
        obj = cls(name=self.name, description=self.description, meta=self.meta, **kwargs)
        return obj

    def _get_by_index(self, index):
        '''
        '''
        obj = self.copy()
        for name, df in obj.dataframes.items():
            if len(df) > 0:
                index_name = df.index.names[0]
                obj[name] = df.ix[df.index.isin([index], index_name), :]
        return obj

    def _get_by_indices(self, indices):
        '''
        '''
        obj = self.copy()
        for name, df in obj.dataframes.items():
            if len(df) > 0:
                index_name = df.index.names[0]
                obj[name] = df.ix[df.index.isin(indices, index_name), :]
        return obj

    def _get_by_slice(self, key):
        '''
        '''
        obj = self.copy()
        for name, df in obj.dataframes.items():
            if len(df) > 0:
                index_name = df.index.names[0]
                index_values = df.index.get_level_values(index_name).unique()
                start = index_values[0] if key.start is None else key.start
                stop = index_values[-1] if key.stop is None else key.stop
                step = index_values[1] - index_values[0] if key.step is None else key.step
                stop += step            # To ensure we get the endpoint
                indices = np.arange(start, stop, step, dtype=np.int64)
                obj[name] = df.ix[df.index.isin(indices, index_name), :]
        return obj

    def __getitem__(self, key):
        '''
        Integers, slices, and lists are assumed to be values in the index (
        for multi-indexed dataframes, corresponding to level 0).
        '''
        if isinstance(key, int):
            return self._get_single(key)
        elif isinstance(key, list):
            return self._get_by_indices(key)
        elif isinstance(key, slice):
            return self._get_by_slice(key)
        else:
            raise NotImplementedError()

    def __setitem__(self, key, value):
        '''
        Custom set calls __setattr__ to enforce certain types.
        '''
        setattr(self, key, value)

    def __setattr__(self, key, value):
        '''
        Custom attribute setting to enforce custom dataframe types.
        '''
        if isinstance(value, pd.DataFrame):
            for name, cls in self.__dfclasses__.items():
                if key == name:
                    self.__dict__[key] = cls(value)
                    return
            self.__dict__[key] = DataFrame(value)
            return
        self.__dict__[key] = value

    def __iter__(self):
        raise NotImplementedError()

    def __len__(self):
        raise NotImplementedError()

    def __init__(self, name=None, description=None, meta=None, **kwargs):
        super().__init__(name=name, description=description)
        self.meta = meta
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _ipython_display_(self):
        '''
        Custom HTML representation
        '''
        self._ipy_disp()
        print(repr(self))

    def _repr_html_(self):
        return self._ipython_display_()

    def __repr__(self):
        c = self.__class__.__name__
        p = self.pkid
        n = self.name
        u = self.uid
        return '{0}({1}: {2}[{3}])'.format(c, p, n, u)

    def __str__(self):
        return repr(self)


def concat(containers, axis=0, join='inner'):
    '''
    Concatenate a collection of containers.
    '''
    raise NotImplementedError()
