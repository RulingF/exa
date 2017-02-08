# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Tests for :mod:`~exa.compute.dispatch`
##########################################
Test the (multiple) dispatch like functionality provided by
:mod:`~exa.compute.dispatch`.
"""
#import numpy as np
#from exa.compute.dispatch import dispatch
#from exa.tester import UnitTester
#
#
#class TestDispatcher(UnitTester):
#    """
#    In order to test the dispatching functionality, we generate a dummy multiply
#    dispatched function "fn".
#    """
#    def setUp(self):
#        """Generate the dummy function "fn"."""
#        try:
#            @dispatch(str)
#            def fn(arg):
#                return arg + "!"
#
#            @dispatch(bool)
#            def fn(arg):
#                return str(arg) + "?"
#
#            @dispatch((int, np.int64))
#            def fn(arg):
#                return str(arg) + "*"
#
#            @dispatch(str, bool)
#            def fn(arg0, arg1):
#                return arg0 + str(arg1) + "!"
#
#            @dispatch((str, int), (bool, int))
#            def fn(arg0, arg1):
#                return str(arg0) + str(arg1) + "!"
#        except Exception as e:
#            self.fail(str(e))
#        self.fn = fn
#
#    def test_single_dispatch(self):
#        """Test the singly dispatched methods."""
#        self.assertTrue(self.fn("Foo").endswith("!"))
#        self.assertTrue(self.fn(True).endswith("?"))
#        self.assertTrue(self.fn(42).endswith("*"))
#        self.assertTrue(self.fn(np.int64(42)).endswith("*"))
#        with self.assertRaises(KeyError):
#            self.fn(np.int32(42))
#
#    def test_multiple_dispatch(self):
#        """Test multiply dispatched arguments."""
#        self.assertTrue(self.fn("Bar", True).endswith("!"))
#        self.assertTrue(self.fn(42, 42).endswith("!"))
