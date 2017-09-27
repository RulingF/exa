# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Tests for :mod:`~exa.core.parser`
#############################################
Parsing is tested on static data provided in the included data directory.
"""
import os, re
from unittest import TestCase
from exa.core.parser import Parser, Sections
from exa.typed import Typed
from exa.static import datadir


name = "parser.bz2"


# Simple test parsers
class SCF(Parser):
    _start = "Self-consistent Calculation"
    _stop = re.compile("^\s*End of self-consistent calculation$", re.MULTILINE)


class XYZ(Parser):
    _start = re.compile("^ATOMIC_POSITIONS", re.MULTILINE)
    _stop = 0


class Output(Parser):
    pass


Output.add_parsers(SCF, XYZ)


# Testing begins here
class TestSections(TestCase):
    """Test the sections dataframe works correctly."""
    def test_create(self):
        sec = Sections.from_lists([0], [0], [None], None)
        self.assertIsInstance(sec['start'].tolist()[0], int)
        self.assertIsNone(sec._ed)
        self.assertEqual(len(sec), 1)

    def test_false_create(self):
        with self.assertRaises(TypeError):
            Sections.from_lists([0.0], [0], [None], None)


class TestParser(TestCase):
    """Check basic parsing functionality on a test file."""
    def setUp(self):
        self.ed = Output(os.path.join(datadir(), name))

    def test_basic(self):
        self.assertEqual(len(self.ed), 2002)

    def test_sections(self):
        sec = self.ed.sections
        self.assertEqual(len(sec), 10)
