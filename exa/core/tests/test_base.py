# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Tests for :mod:`~exa.core.base`
#############################################
Tests for abstract base classes of data, editor, and container objects.
This module also tests some advanced usages of the abstract base class
in combination with the :class:`~exa.special.Typed` metaclass.
"""
from unittest import TestCase
from exa.core import Base
from exa.special import Typed


class Concrete(Base):
    """Example concrete implementation of the abstract base class."""
    def info(self):
        pass

    def _html_repr_(self):
        pass


class FooMeta(Typed):
    """Metaclass that defines typed attributes for class Foo."""
    foo = dict
    bar = list
    baz = str


class Foo(six.with_metaclass(FooMeta, Concrete)):
    """Example of strongly typed objects on a concrete implementation."""
    def _get_foo(self):
        """Test automatic (lazy) getter with prefix _get."""
        self.foo = {'value': "foo"}

    def compute_bar(self):
        """Test automatic (lazy) getter with prefix compute."""
        self.bar = ["bar"]

    def parse_baz(self):
        """Test automatic (lazy) getter with prefix parse."""
        self.baz = "baz"


class TestBase(TestCase):
    """Test the abstract base class."""
    def test_abstract(self):
        """Test that we require a concrete implementation."""
        with self.assertRaises(TypeError):
            Base()

    def test_concrete(self):
        """Test the concrete implementation."""
        c = Concrete()
        self.assertIsInstance(c, Base)
        self.assertTrue(hasattr(c, "info"))

    def test_kwargs(self):
        c = Concrete(brick=0, slab=1)
        self.assertTrue(hasattr(c, "brick"))
        self.assertIsInstance(c.brick, int)
