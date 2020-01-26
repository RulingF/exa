# -*- coding: utf-8 -*-
# Copyright (c) 2015-2020, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0

#import pytest

import exa

def test_init():
    assert exa.cfg.logdir
    assert exa.cfg.logname
    assert hasattr(exa.cfg, 'log')
    assert hasattr(exa.cfg.log, 'info')
