# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Tests for :mod:`~exa.management.editor`
#############################################
Test the functionality of the :class:`~exa.management.editor.Editor` class and
related functions.
"""
import shutil
import os, gzip, bz2
from io import StringIO
from uuid import uuid4
from exa._config import config
from exa.tester import UnitTester
from exa.cms.editors.editor import Editor


editor_string = """This string is used as the test for the editor class.

It contains templates: {template}
and constants: {{constant}}
"""


class TestEditor(UnitTester):
    """
    The tester reads in a contrived example in the root "tests" directory and
    proceeds to test the various functions provided by
    :class:`~exa.management.editor.Editor`.
    """
    def setUp(self):
        """
        A :class:`~exa.management.editor.Editor` can be create in three ways,
        from a file, from a stream, and from a string.
        """
        self.path = os.path.join(config['paths']['tmp'], uuid4().hex)
        with open(self.path, 'w', newline='') as f:
            f.write(editor_string)
        with open(self.path, "rb") as f_in:
            with gzip.open(self.path + ".gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        with open(self.path, "rb") as f_in:
            with bz2.open(self.path + ".bz2", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        with open(self.path + '.iso-8859-1', 'w', newline='', encoding='iso-8859-1') as f:
            f.write(editor_string)
        self.from_file = Editor(self.path)
        self.from_file_enc = Editor(self.path, encoding='iso-8859-1')
        self.from_gzip = Editor(self.path + ".gz")
        self.from_bz2 = Editor(self.path + ".bz2")
        self.from_stream = Editor(StringIO(editor_string))
        self.from_string = Editor(editor_string)

    def tearDown(self):
        """
        Remove the temporary files generated by the test.
        """
        os.remove(self.path)
        os.remove(self.path + ".gz")
        os.remove(self.path + ".bz2")
        os.remove(self.path + ".iso-8859-1")

    def test_editor_input_methods(self):
        """
        Test to make sure all the support input (**read_\***) were read in
        correctly. This function actually tests
        :func:`~exa.management.editor.Editor.__eq__`.
        """
        self.assertEqual(self.from_file, self.from_file_enc)
        self.assertEqual(self.from_file, self.from_gzip)
        self.assertEqual(self.from_file, self.from_bz2)
        self.assertEqual(self.from_file, self.from_stream)
        self.assertEqual(self.from_file, self.from_string)

    def test_tmpl_cnst(self):
        """
        Test :func:`~exa.management.editor.Editor.templates` and
        :func:`~exa.management.editor.Editor.constants`.
        """
        self.assertEqual(self.from_file.templates, ['template'])
        self.assertEqual(self.from_file.constants, ['constant'])

    def test_head_tail(self):
        """
        Test :func:`~exa.management.editor.Editor.head` and
        :func:`~exa.management.editor.Editor.tail`.
        """
        self.assertEqual(self.from_file.head(1), self.from_file._lines[0])
        self.assertEqual(self.from_file.tail(1), self.from_file._lines[-1])

    def test_insert(self):
        """
        Test :func:`~exa.management.editor.Editor.append`,
        Test :func:`~exa.management.editor.Editor.prepend`, and
        :func:`~exa.management.editor.Editor.insert`.
        """
        test = "new\nlines"
        self.from_file.append(test)
        self.assertEqual(str(self.from_file[-1]), "lines")
        self.from_file.prepend(test)
        self.assertEqual(str(self.from_file[1]), "lines")
        del self.from_file[0]
        del self.from_file[0]
        del self.from_file[-1]
        del self.from_file[-1]
        self.from_file.insert(-1, test)
        self.assertEqual(str(self.from_file[-2]), "lines")
        del self.from_file[-2]
        del self.from_file[-2]

    def test_replace(self):
        """
        Test :func:`~exa.management.editors.editor.Editor.replace`.
        """
        rp0 = "This string is used as the test for the editor class."
        rp1 = "replacement"
        self.from_file.replace(rp0, rp1)
        self.assertEqual(str(self.from_file[0]), rp1)
        self.from_file.replace(rp1, rp0)