# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Tests for :mod:`~exa.typed`
#############################################
There are a large number of test implementations in the source code of these
tests, which may be helpful for developers.
"""
#import six
#import pytest
#import numpy as np
#from exa.typed import Typed, typed, TypedClass, TypedMeta, yield_typed
#
#
## The following are objects used in testing
#class _Foo(object):
#    def __init__(self, bar):
#        self.bar = bar
#
#class _TFoo(TypedClass, _Foo):
#    pass
#
#
#@typed
#class Foo0(_Foo):
#    bar = Typed(int)
#
#
#class Foo1(six.with_metaclass(TypedMeta, _Foo)):
#    bar = Typed(int)
#
#
#class Foo2(_TFoo):
#    bar = Typed(int)
#
#
#@typed
#class Foo3(_Foo):
#    bar = Typed(int, autoconv=False)
#
#
#class Foo4(_TFoo):
#    bar = Typed(int, allow_none=False)
#
#
#class Foo5(_TFoo):
#    bar = Typed(int, pre_set="pre_set")
#
#    def pre_set(self):
#        self.pre_set_called = True
#        self.pre_set_bar_value = self.bar
#
#    def __init__(self):
#        self.pre_set_called = False
#
#
#def external_pre_set(foo):
#    """Test external functions (see Foo6)."""
#    foo.pre_set_called = True
#    foo.pre_set_bar_value = foo.bar
#
#
#class Foo6(_TFoo):
#    bar = Typed(int, pre_set=external_pre_set)
#
#    def __init__(self, *args, **kwargs):
#        super(Foo6, self).__init__(*args, **kwargs)
#        self.pre_set_called = False
#
#
#class Foo7(_TFoo):
#    bar = Typed(int, post_set="post_set")
#
#    def post_set(self):
#        self.post_set_bar_value = self.bar
#        self.post_set_called = True
#
#    def __init__(self, *args, **kwargs):
#        super(Foo7, self).__init__(*args, **kwargs)
#        self.post_set_called = False
#
#
#def external_post_set(foo):
#    """See external_pre_set."""
#    foo.post_set_called = True
#    foo.post_set_bar_value = foo.bar
#
#
#class Foo8(TypedClass):
#    bar = Typed(int, post_set=external_post_set)
#
#    def __init__(self):
#        self.post_set_called = False
#
#
#class Foo9(TypedClass):
#    bar = Typed(int, pre_get="pre_get")
#
#    def pre_get(self):
#        self.pre_get_called = True
#
#    def __init__(self, bar):
#        self.bar = bar
#        self.pre_get_called = False
#
#
#def external_pre_get(foo):
#    """See external_pre_set."""
#    foo.pre_get_called = True
#
#
#class Foo10(TypedClass):
#    bar = Typed(int, pre_get=external_pre_get)
#
#    def __init__(self, bar):
#        self.bar = bar
#        self.pre_get_called = False
#
#
#class Foo11(TypedClass):
#    """Testing auto-setting."""
#    _setters = ("compute", )
#    bar = Typed(int)
#
#    def compute_bar(self):
#        self.bar = 42
#
#
#class Foo12(TypedClass):
#    """Testing deletion functions."""
#    bar = Typed(int, pre_del="pre_del")
#
#    def pre_del(self):
#        self.pre_del_called = True
#
#    def __init__(self):
#        self.bar = 42
#        self.pre_del_called = False
#
#
#def external_pre_del(foo):
#    """See external_pre_set."""
#    foo.pre_del_called = True
#
#
#class Foo13(TypedClass):
#    """Testing deletion functions."""
#    bar = Typed(int, pre_del=external_pre_del)
#
#    def __init__(self):
#        self.bar = 42
#        self.pre_del_called = False
#
#
#class Foo14(TypedClass):
#    """Testing deletion functions."""
#    bar = Typed(int, post_del="pre_del")
#
#    def pre_del(self):
#        self.post_del_called = True
#
#    def __init__(self):
#        self.bar = 42
#        self.post_del_called = False
#
#
#def external_post_del(foo):
#    """See external_pre_set."""
#    foo.post_del_called = True
#
#
#class Foo15(TypedClass):
#    """Testing deletion functions."""
#    bar = Typed(int, post_del=external_post_del)
#
#    def __init__(self):
#        self.bar = 42
#        self.post_del_called = False
#
#
#class Foo16(TypedClass):
#    bar = Typed(int)
#
#    @property
#    def foo(self):
#        return 42
#
#
#class Foo17(TypedClass):
#    _setters = ("compute", )
#    bar = Typed(np.ndarray)
#
#    def compute_bar(self):
#        self.bar = np.random.rand(10)
#
#    def __init__(self, bar):
#        self.bar = bar
#
#
## Fixtures
#@pytest.fixture
#def foo0():
#    return Foo0(42)
#
#
#@pytest.fixture
#def foo1():
#    return Foo1
#
## Testing begins here.
#def test_basic(foo0)
#class TestTyped(TestCase):
#    """
#    Test the strongly typed infrastructure provided by :mod:`~exa.typed`.
#    """
#    def test_basic(self):
#        """
#        Test that the three methods of typed class creation work.
#        """
#        obj = Foo0(42)
#        self.assertIsInstance(obj.bar, int)
#        self.assertEqual(obj.bar, 42)
#        obj = Foo1(42)
#        self.assertIsInstance(obj.bar, int)
#        self.assertEqual(obj.bar, 42)
#        obj = Foo2(42)
#        self.assertIsInstance(obj.bar, int)
#        self.assertEqual(obj.bar, 42)
#
#    def test_autoconv(self):
#        """Test auto type conversion."""
#        obj = Foo0(42.0)
#        self.assertIsInstance(obj.bar, int)
#        self.assertEqual(obj.bar, 42)
#        with self.assertRaises(TypeError):
#            Foo0("failure")
#        with self.assertRaises(TypeError):
#            Foo3("failure")
#
#    def test_setting_none(self):
#        """Test that None is always an acceptable typed value."""
#        obj = Foo3(None)
#        self.assertIsNone(obj.bar)
#        with self.assertRaises(TypeError):
#            Foo4(None)
#
#    def test_pre_set(self):
#        """Test calling functions prior to set."""
#        # Internal pre_set call
#        obj = Foo5()
#        self.assertFalse(obj.pre_set_called)
#        self.assertFalse(hasattr(obj, "pre_set_bar_value"))
#        obj.bar = 42
#        self.assertTrue(obj.pre_set_called)
#        self.assertIsNone(obj.pre_set_bar_value)
#        self.assertEqual(obj.bar, 42)
#        # External pre_set call
#        obj = Foo6()
#        self.assertFalse(obj.pre_set_called)
#        self.assertFalse(hasattr(obj, "pre_set_bar_value"))
#        obj.bar = 42
#        self.assertTrue(obj.pre_set_called)
#        self.assertIsNone(obj.pre_set_bar_value)
#        self.assertEqual(obj.bar, 42)
#
#    def test_post_set(self):
#        """Test calling post_set functions."""
#        obj = Foo7()
#        self.assertFalse(obj.post_set_called)
#        self.assertFalse(hasattr(obj, "post_set_bar_value"))
#        obj.bar = 42
#        self.assertIs(obj.post_set_bar_value, obj.bar)
#        self.assertTrue(obj.post_set_called)
#        obj = Foo8()
#        self.assertFalse(obj.post_set_called)
#        self.assertFalse(hasattr(obj, "post_set_bar_value"))
#        obj.bar = 42
#        self.assertIs(obj.post_set_bar_value, obj.bar)
#        self.assertTrue(obj.post_set_called)
#
#    def test_pre_get(self):
#        """Test calling pre_get functions."""
#        obj = Foo9(42)
#        self.assertFalse(obj.pre_get_called)
#        self.assertEqual(obj.bar, 42)
#        self.assertTrue(obj.pre_get_called)
#        obj = Foo10(42)
#        self.assertFalse(obj.pre_get_called)
#        self.assertEqual(obj.bar, 42)
#        self.assertTrue(obj.pre_get_called)
#
#    def test_setters(self):
#        """Test _setters works correctly."""
#        obj = Foo11()
#        self.assertFalse(hasattr(obj, "_bar"))
#        self.assertEqual(obj.bar, 42)
#
#    def test_pre_del(self):
#        """Test pre_del functions."""
#        obj = Foo12()
#        self.assertFalse(obj.pre_del_called)
#        self.assertEqual(obj.bar, 42)
#        del obj.bar
#        self.assertTrue(obj.pre_del_called)
#        self.assertIsNone(obj.bar)
#        obj = Foo13()
#        self.assertFalse(obj.pre_del_called)
#        self.assertEqual(obj.bar, 42)
#        del obj.bar
#        self.assertTrue(obj.pre_del_called)
#        self.assertIsNone(obj.bar)
#
#
#    def test_post_del(self):
#        """Test post_del functions."""
#        obj = Foo14()
#        self.assertFalse(obj.post_del_called)
#        self.assertEqual(obj.bar, 42)
#        del obj.bar
#        self.assertTrue(obj.post_del_called)
#        self.assertIsNone(obj.bar)
#        obj = Foo15()
#        self.assertFalse(obj.post_del_called)
#        self.assertEqual(obj.bar, 42)
#        del obj.bar
#        self.assertTrue(obj.post_del_called)
#        self.assertIsNone(obj.bar)
#
#    def test_yield_typed(self):
#        """Test :func:`~exa.typed.yield_typed`."""
#        names = list(yield_typed(Foo16))
#        self.assertIsInstance(Foo16.foo, property)
#        self.assertEqual(Foo16().foo, 42)
#        self.assertListEqual(names, ["bar"])
#
#    def test_foo17(self):
#        """
#        Test array attribute types (includes series, dataframe objects)
#        since their truth value is determined by not being None.
#        """
#        obj = Foo17(None)
#        self.assertIsNotNone(obj.bar)
#        a = np.random.rand(10)
#        obj = Foo17(a)
#        self.assertTrue(np.allclose(obj.bar, a))
