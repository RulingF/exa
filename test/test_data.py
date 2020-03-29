# -*- coding: utf-8 -*-
# Copyright (c) 2015-2020, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Tests for :mod:`~exa.core.data`
#######################################
"""
import pytest
import pandas as pd
from traitlets import TraitError
import exa
from exa.core.error import RequiredColumnError


@pytest.fixture(scope='module')
def data():
    return exa.Data()

def test_data_simple(data):
    assert data.data() is None
    fun = lambda: 42
    data.source = fun
    assert data.data() == 42
    data.source = None
    assert data.data() is None
    with pytest.raises(TraitError):
        data.source = ''

def test_new_data_call_params():
    d = exa.Data(call_args=['a', 'b'],
                 call_kws={'a': 'b'})
    assert d.call_args == ['a', 'b']
    assert d.call_kws == {'a': 'b'}
    assert d.data() is None
    fun = lambda *a, **kws: a
    d.source = fun
    assert d.data() == tuple(d.call_args)
    fun = lambda *a, **kws: kws
    d.source = fun
    assert d.data(cache=False) == d.call_kws

def test_data_setting_source(data):
    fun = lambda *a: a[0] if a else None
    data.source = fun
    data.call_args = ['a', 'b']
    assert data.data() == 'a'
    data.source = None

def test_data_slice(data):
    assert data.slice(None) is None

def test_data_groupby(data):
    df = pd.DataFrame.from_dict(
        {'a': [1, 2], 'b': [3, 4]}
    )
    data.data(df=df)
    data.indexes = []
    assert data.groupby() is None
    data.indexes = ['a']
    grps = data.groupby()
    assert grps.ngroups == 2
    data.indexes = ['a', 'b']
    grps = data.groupby()
    assert grps.ngroups == 2
    data.indexes = []
    df[['a', 'b']] = 1
    data.data(df=df)
    grps = data.groupby(columns=['a', 'b'])
    assert grps.ngroups == 1

def test_data_memory(data):
    data.data(cache=False)
    assert not data.memory()
    df = pd.DataFrame.from_dict(
        {'a': [1, 2], 'b': [3, 4]}
    )
    data.data(df=df)
    assert data.memory().sum()

def test_data_validation(data):
    df = pd.DataFrame.from_dict(
        {'a': [1, 2], 'b': [3, 4]}
    )
    data.data(df=df)
    assert data.data().equals(df)
    data.columns = ['c']
    with pytest.raises(RequiredColumnError):
        data.data(df=df)
    data.columns = []
    data.categories = {'a': str, 'b': int, 'c': int}
    df = data.data(df=df)
    assert df['a'].dtype == 'category'
    df['d'] = 1
    data.indexes = ['d']
    with pytest.raises(TraitError):
        data.data(df=df)
    data.indexes = []

def test_from_yml(isotopes):
    d = exa.Data.from_yml(exa.cfg.resource('isotopes.yml'))
    df = d.data()
    assert df.index.name == 'isotope'
    assert df['symbol'].dtype == 'category'
    assert df['Z'].dtype == 'category'
    assert not df.columns.difference(d.columns).any()
    assert df.shape == isotopes.data().shape

def test_from_yml_fail(tmp_path):
    f = tmp_path / "cfg.yml"
    f.write_text("""\
name: test
source: os.path.isfile
""")
    dum = exa.Data.from_yml(f)
    with pytest.raises(Exception):
        dum.data()
    f = tmp_path / "oth.yml"
    f.write_text("""\
name: test
source: os.path.dne
""")
    with pytest.raises(TraitError):
        dum = exa.Data.from_yml(f)

def test_copy(data):
    data._data = None
    n = data.copy()
    assert id(n) != id(data)
    df = pd.DataFrame()
    n.data(df=df)
    nn = n.copy()
    assert id(nn) != id(n)

def test_isotopes():
    assert not exa.Isotopes.data().empty

def test_constants():
    assert not exa.Constants.data().empty

def test_units():
    assert not exa.core.data.Units.data().empty
