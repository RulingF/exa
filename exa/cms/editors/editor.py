# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Editor
####################################
The :class:`~exa.management.editor.Editor` class is a way for programmatic text-
editor-like manipulation of files on disk. It does not strive to be a full
featured text editor. A large number of Pythonic operations can be performed on
editors:

.. code-block:: Python

    editor = Editor(file.txt)       # Create an editor from a file
    editor = Editor(file.txt.gz)    # Automatically decompress
    editor = Editor(file.txt.bz2)
    for line in editor:             # Iterate over lines in the file
        pass
    if 'text' in editor:            # True if "text" appears on any line
        True

Text lines are stored in memory; file handles are only open during reading and
writing. For large repetitive files, memoization can reduce the memory footprint
(see the **as_interned** kwarg).
"""
import os
import re
import sys
import bz2
import six
import gzip
import pandas as pd
from copy import copy, deepcopy
from operator import add
from collections import Counter
from io import StringIO, TextIOWrapper


class Editor(object):
    """
    An in memory copy of a file on disk that can be programmatically manipulated.

    Editor line numbers use a 0 base index. To increase the number of lines
    displayed by the repr, increase the value of the **nprint** attribute.
    For large text with repeating strings be sure to use the **as_interned**
    argument.

    Args:
        name (str): Data/file/misc name
        description (str): Data/file/misc description
        meta (dict): Additional metadata as key, value pairs
        nrpint (int): Number of lines to display when printing
        cursor (int): Line number position of the cusor (see :func:`~exa.editor.Editor.find_next_any` and :func:`~exa.editor.Editor.find_next_string`)
    """
    _getter_prefix = 'parse'     # See :class:`~exa.typed.Typed`
    _fmt = '{0}: {1}\n'.format   # Format for printing lines (see __repr__)

    @property
    def templates(self):
        """
        Display a list of templatable variables present in the file.

        .. code-block:: text

            tmpl = "this is a {template}"
            tmpl.format(template="other text")    # prints "this is a other text"

        See Also:
            Python string formatting is very powerful. See the `docs`_ for more
            information and usage examples.

        .. _docs: https://docs.python.org/3.6/library/string.html
        """
        csnt = r"{{[\w\d]*}}"
        tmpl = r"{[\w\d]*}"
        constants = [match[2:-2] for match in self.regex(csnt, which='values')[csnt]]
        templates = [match[1:-1] for match in self.regex(tmpl, which='values')[tmpl]]
        return sorted(set(templates).difference(constants))

    @property
    def constants(self):
        """
        Display a list of constants within the file. Constants are literal
        templates constructed using double curly braces.

        .. code-block:: text

            cnst = "this is a {{constant}}"   # Cannot be "formatted"

        See Also:
            `String formatting`_.

        .. _String formatting: https://docs.python.org/3.6/library/string.html
        """
        csnt = r"{{[\w\d]*}}"
        constants = [match[2:-2] for match in self.regex(csnt, which='values')[csnt]]
        return sorted(constants)

    def regex(self, *patterns, **kwargs):
        """
        Match a line or lines by the specified regular expression(s).

        Args:
            \*patterns: Regular expressions to search each line for
            which (str): If none, return values as (lineno, match), if "keys" return lineno only, if "values" return lines only
            flags: Python re flags (e.g. re.MULTILINE)

        Returns:
            results (dict): Dictionary with pattern keys and list of (lineno, match) values

        See Also:
            `Regular expressions`_ are a complex but powerful way to search
            and match text text.

        .. _Regular expressions: https://en.wikipedia.org/wiki/Regular_expression
        """
        which = kwargs.pop('which', None)
        flags = kwargs.pop('flags', re.MULTILINE|re.DOTALL)
        results = {}
        self_str = str(self)
        for pattern in patterns:
            match = pattern
            if not type(pattern).__name__ == "SRE_Pattern":
                match = re.compile(pattern, flags)
            if which == "keys":
                pattern_results = [self_str.count("\n", 0, m.start()) + 1 for m in match.finditer(self_str)]
            elif which == "values":
                pattern_results = [m.group() for m in match.finditer(self_str)]
            else:
                pattern_results = [(self_str.count("\n", 0, m.start()) + 1, m.group()) for m in match.finditer(self_str)]
            results[match.pattern] = pattern_results
        return results

    def find(self, *patterns, **kwargs):
        """
        Search each line for a specified pattern(s).

        Args:
            \*strings (str): Any number of strings to search for
            which (str): If none, return values as (lineno, match), if "keys" return lineno only, if "values" return lines only

        Returns:
            results (dict): Dictionary with pattern keys and list of (lineno, line) values
        """
        which = kwargs.pop('which', None)
        results = {pattern: [] for pattern in patterns}
        for i, line in enumerate(self):
            for pattern in patterns:
                if pattern in line:
                    if which == "keys":
                        results[pattern].append(i)
                    elif which == "values":
                        results[pattern].append(line)
                    else:
                        results[pattern].append((i, line))
        return results

    def find_next(self, pattern, which=None, reverse=False):
        """
        From the current cursor position, find the next occurrence of the pattern.

        Args:
            pattern (str): String to search for from the current cursor position
            which (str): If none, return values as (lineno, match), if "keys" return lineno only, if "values" return lines only
            reverse (bool): Find next in reverse

        Returns:
            tup (tuple): Tuple of line number and line of next occurrence

        Note:
            Searching will cycle the file and continue if an occurrence is not
            found.
        """
        n = len(self)
        n1 = n - 1
        if reverse:
            self.cursor = 0 if self.cursor == 0 else self.cursor - 1
            positions = [(self.cursor - 1, 0, -1), (n1, self.cursor, -1)]
        else:
            self.cursor = 0 if self.cursor == n1 else self.cursor + 1
            positions = [(self.cursor, n, 1), (0, self.cursor, 1)]
        for start, stop, inc in positions:
            for i in range(start, stop, inc):
                if pattern in str(self[i]):
                    self.cursor = i
                    if which == "keys":
                        return i
                    elif which == "values":
                        return str(self[i])
                    else:
                        return (i, str(self[i]))

    def copy(self):
        """
        Create a copy of the current editor.
        """
        cls = self.__class__
        lines = self._lines[:]
        as_interned = copy(self.as_interned)
        nprint = copy(self.nprint)
        name = copy(self.name)
        description = copy(self.description)
        meta = deepcopy(self.meta)
        enc = copy(self.encoding)
        return cls(lines, as_interned, nprint, name, description, meta, enc)

    def format(self, *args, **kwargs):
        """
        Populate the editors templates.

        Args:
            \*args: Args for formatting
            \*\*kwargs: Kwargs for formatting
            inplace (bool): If True, overwrite editor's contents with formatted contents (default False)

        Returns:
            formatted: Returns the formatted editor (if inplace is False)
        """
        inplace = kwargs.pop('inplace', False)
        if inplace:
            self._lines = str(self).format(*args, **kwargs).splitlines()
        else:
            cp = self.copy()
            cp._lines = str(cp).format(*args, **kwargs).splitlines()
            return cp

    def write(self, path, *args, **kwargs):
        """
        Write the editor contents to a file.

        Args:
            path (str): Full file path (default None, prints to stdout)
            *args: Positional arguments to format the editor with
            **kwargs: Keyword arguments to format the editor with
        """
        with open(path, "wb") as f:
            if len(args) > 0 or len(kwargs) > 0:
                f.write(six.b(str(self.format(*args, **kwargs))))
            else:
                f.write(six.b(str(self)))

    def head(self, n=10):
        """
        Display the top of the file.
        """
        return "\n".join(self._lines[:n])

    def tail(self, n=10):
        """
        Display the bottom of the file.
        """
        return "\n".join(self._lines[-n:])

    def append(self, lines):
        """
        Append lines to the editor (inplace).

        Args:
            lines (list, str): List of lines or str text to append to the editor
        """
        if isinstance(lines, list):
            self._lines += lines
        elif isinstance(lines, six.string_types):
            self._lines += lines.splitlines()
        else:
            raise TypeError("Unsupported type {} for lines.".format(type(lines)))

    def prepend(self, lines):
        """
        Prepend lines to the editor (inplace).

        Args:
            lines (list, str): List of lines or str text to append to the editor
        """
        if isinstance(lines, list):
            self._lines = lines + self._lines
        elif isinstance(lines, six.string_types):
            self._lines = lines.splitlines() + self._lines
        else:
            raise TypeError("Unsupported type {} for lines.".format(type(lines)))

    def insert(self, no, lines):
        """
        Insert lines into the editor (inplace).

        Args:
            no (int): Line number after which to insert lines
            lines (list, str): List of lines or str text to append to the editor
        """
        if isinstance(lines, six.string_types):
            lines = lines.splitlines()
        elif not isinstance(lines, list):
            raise TypeError("Unsupported type {} for lines.".format(type(lines)))
        self._lines = self._lines[:no] + lines + self._lines[no:]

    def replace(self, pattern, replacement):
        """
        Replace all instances of a pattern with a replacement.

        Args:
            pattern (str): Pattern to replace
            replacement (str): Text to insert
        """
        for i, line in enumerate(self):
            while pattern in line:
                line = line.replace(pattern, replacement)
            self[i] = line

    def remove_blank_lines(self):
        """Remove all blank lines (blank lines are those with zero characters)."""
        to_remove = []
        for i, line in enumerate(self):
            ln = line.strip()
            if ln == '':
                to_remove.append(i)
        self.delete_lines(to_remove)

#    def _data(self, copy=False):
#        """
#        Get all data associated with the container as key value pairs.
#        """
#        data = {}
#        for key, obj in self.__dict__.items():
#            if isinstance(obj, (pd.Series, pd.DataFrame, pd.SparseSeries, pd.SparseDataFrame)):
#                if copy:
#                    data[key] = obj.copy()
#                else:
#                    data[key] = obj
#        return data
#
    def delete_lines(self, lines):
        """
        Delete all lines with given line numbers.

        Args:
            lines (list): List of integers corresponding to line numbers to delete
        """
        for k, i in enumerate(lines):
            del self[i-k]    # Accounts for the fact that len(self) decrease upon deletion


#    def pandas_dataframe(self, start, stop, ncol, **kwargs):
#        """
#        Returns the result of tab-separated pandas.read_csv on
#        a subset of the file.
#
#        Args:
#            start (int): line number where structured data starts
#            stop (int): line number where structured data stops
#            ncol (int or list): the number of columns in the structured
#                data or a list of that length with column names
#
#        Returns:
#            pd.DataFrame: structured data
#        """
#        try:
#            ncol = int(ncol)
#            return pd.read_csv(StringIO('\n'.join(self[start:stop])), delim_whitespace=True, names=range(ncol), **kwargs)
#        except TypeError:
#            try:
#                ncol = list(ncol)
#                return pd.read_csv(StringIO('\n'.join(self[start:stop])), delim_whitespace=True, names=ncol, **kwargs)
#            except TypeError:
#                print('Cannot pandas_dataframe if ncol is {}, must be int or list'.format(type(ncol)))
#
#

#    @classmethod
#    def from_file(cls, path, **kwargs):
#        """Create an editor instance from a file on disk."""
#        lines = lines_from_file(path)
#        if 'meta' not in kwargs:
#            kwargs['meta'] = {'from': 'file'}
#        kwargs['meta']['filepath'] = path
#        return cls(lines, **kwargs)
#
#    @classmethod
#    def from_stream(cls, f, **kwargs):
#        """Create an editor instance from a file stream."""
#        lines = lines_from_stream(f)
#        if 'meta' not in kwargs:
#            kwargs['meta'] = {'from': 'stream'}
#        kwargs['meta']['filepath'] = f.name if hasattr(f, 'name') else None
#        return cls(lines, **kwargs)
#
#    @classmethod
#    def from_string(cls, string, **kwargs):
#        """Create an editor instance from a string template."""
#        return cls(lines_from_string(string), **kwargs)

    def __eq__(self, other):
        if isinstance(other, Editor) and self._lines == other._lines:
            return True
        return False

    def __len__(self):
        return len(self._lines)

    def __iter__(self):
        for line in self._lines:
            yield line

    def __str__(self):
        return '\n'.join(self._lines)

    def __contains__(self, item):
        for obj in self:
            if item in obj:
                return True

    def __delitem__(self, line):
        del self._lines[line]     # "line" is the line number minus one

    def __getitem__(self, key):
        if isinstance(key, six.string_types):
            return getattr(self, key)
        return self.__class__(self._lines[key])

    def __setitem__(self, line, value):
        self._lines[line] = value

    def __init__(self, data, as_interned=False, nprint=30, name=None,
                 description=None, meta=None, encoding='utf-8'):
        filepath = None
        if isinstance(data, six.string_types) and os.path.exists(data):
            self._lines = read_file(data, as_interned, encoding)
            filepath = data
        elif isinstance(data, six.string_types):
            self._lines = read_string(data, as_interned)
        elif isinstance(data, (TextIOWrapper, StringIO)):
            self._lines = read_stream(data, as_interned)
        elif isinstance(data, list) and all(isinstance(dat, six.string_types) for dat in data):
            self._lines = data
        else:
            raise TypeError('Unknown type for arg data: {}'.format(type(data)))
        self.name = name
        self.description = description
        self.meta = meta
        self.nprint = 30
        self.as_interned = as_interned
        self.encoding = encoding
        self.cursor = 0
        if self.meta is None and filepath is not None:
            self.meta = {'filepath': filepath}
        elif filepath is not None and 'filepath' not in self.meta:
            self.meta['filepath'] = filepath

    def __repr__(self):
        r = ''
        nn = len(self)
        n = len(str(nn))
        if nn > self.nprint * 2:
            for i in range(self.nprint):
                ln = str(i).rjust(n, ' ')
                r += self._fmt(ln, self._lines[i])
            r += '...\n'.rjust(n, ' ')
            for i in range(nn - self.nprint, nn):
                ln = str(i).rjust(n, ' ')
                r += self._fmt(ln, self._lines[i])
        else:
            for i, line in enumerate(self):
                ln = str(i).rjust(n, ' ')
                r += self._fmt(ln, line)
        return r


def read_file(path, as_interned=False, encoding='utf-8'):
    """
    Create a list of file lines from a given filepath.

    Args:
        path (str): File path
        as_interned (bool): List of "interned" strings (default False)

    Returns:
        strings (list): File line list
    """
    lines = None
    if path.endswith(".gz"):
        f = gzip.open(path, 'rb')
    elif path.endswith(".bz2"):
        f = bz2.open(path, 'rb')
    else:
        f = open(path, 'rb')
    read = f.read()
    try:
        read = read.decode(encoding)    # For .gz and .bz2 files
    except AttributeError:
        pass
    if as_interned:
        lines = [sys.intern(line) for line in read.splitlines()]
    else:
        lines = read.splitlines()
    f.close()
    return lines


def read_stream(f, as_interned=False):
    """
    Create a list of file lines from a given file stream.

    Args:
        f (:class:`~io.TextIOWrapper`): File stream
        as_interned (bool): List of "interned" strings (default False)

    Returns:
        strings (list): File line list
    """
    if as_interned:
        return [sys.intern(line) for line in f.read().splitlines()]
    return f.read().splitlines()


def read_string(string, as_interned=False):
    """
    Create a list of file lines from a given string.

    Args:
        string (str): File string
        as_interned (bool): List of "interned" strings (default False)

    Returns:
        strings (list): File line list
    """
    if as_interned:
        return [sys.intern(line) for line in string.splitlines()]
    return string.splitlines()


def concat(*editors, **kwargs):
    """
    Concatenate a collection of editors into a single editor.

    Args:
        \*editors: Collection of editors (in order) to be concatenated
        \*\*kwargs: Arguments for editor creation

    Returns:
        editor: An instance of an editor
    """
    classes = [ed.__class__ for ed in editors]
    cls = Counter(classes).most_common(1)[0][0]
    lines = []
    for ed in editors:
        lines += ed._lines
    return cls(lines, **kwargs)
