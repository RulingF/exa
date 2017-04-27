# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Abstract Editors, Containers, and Data
#######################################
This module provides abstract base classes for editor, container, and data
objects.
"""
import six, sys
from uuid import UUID, uuid4
from abc import abstractmethod
from exa.special import Typed


class ABCBaseMeta(Typed):
    """Strongly typed static attributes."""
    uid = UUID
    meta = dict
    name = str


class ABCBase(six.with_metaclass(ABCBaseMeta, object)):
    """
    Abstract base class for composite data representations such as editors,
    containers, and higher level data objects.
    """
    _getters = ('_get', )

    @abstractmethod
    def copy(self):
        """At a bare minimum a data object must define a copy method."""
        pass

    def _get_uid(self):
        """Generate a new uid for this object."""
        object.__setattr__(self, "uid", uuid4())

    def __init__(self, name=None, uid=None, meta=None):
        if name is not None:
            self.name = name
        if uid is not None:
            self.uid = uid
        if meta is not None:
            self.meta = meta


class ABCContainer(ABCBase):
    """
    An abstract base class for container objects.

    Given a collection of data of some (at least moderately) known structure,
    this object can facilitate computation, analytics, and visualization. All
    container objects share a basic API defined by this class.
    """
    _getters = ("_get", "parse", "compute")

    @abstractmethod
    def describe(self):
        """Display a frame containing information about this object."""
        pass

    def _data(self):
        """Helper method for introspectively obtaining data objects."""
        return {n: v for n, v in vars(self).items() if not n.startswith("_")}

    def _data_properties(self):     # To be used by the ``describe`` method
        """Helper method to estimate data sizes (in MiB)."""
        data = {}
        for name, v in self._data().items():
            if hasattr(v, "memory_usage"):
                size = v.memory_usage()
                size = size.sum() if not isinstance(size, int) else size
            elif hasattr(v, "nbytes"):
                size = v.nbytes
            else:
                size = sys.getsizeof(v)
            data[name] = (type(v), size)
        return data

    @abstractmethod
    def _html_repr_(self):    # Jupyter notebook visualization
        """Jupyter notebook representation."""
        pass

    def __init__(self, **kwargs):
        uid = kwargs.pop("uid", None)
        meta = kwargs.pop("meta", None)
        name = kwargs.pop("name", None)
        super(ABCContainer, self).__init__(name=name, meta=meta, uid=uid)
        # Sets arbitrary objects via kwargs
        for name, data in kwargs.items():
            setattr(self, name, data)
