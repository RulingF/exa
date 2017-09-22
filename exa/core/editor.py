# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Editor
####################################
This module provides the :class:`~exa.editor.Editor`, a text manipulation
engine for small/medium sized text files. This class is not a fully fledged
text editor. It provides basic features for searching text (including
regular expressions). This module additionally provides convenience methods
for reading and writing text.
"""
import io
import os
import bz2
import six
import gzip
from io import StringIO, TextIOWrapper
from exa.typed import Typed, typed
# Python 2 compatibility
if not hasattr(bz2, "open"):
    bz2.open = bz2.BZ2File


def read_file(path, encoding=None):
    """
    Read in a text file (including compressed text files) to a list of lines.

    .. code-block:: Python

        lines = read_file("myfile.gz")
        lines = read_file("myfile.bz2")
        lines = read_file("myfile.txt")

    Args:
        path (str): File path
        encoding (str): Text encoding

    Returns:
        lines (list): Text lines as list of strings
    """
    if path.endswith(".gz"):
        f = gzip.open(path, "rb")
    elif path.endswith(".bz2"):
        f = bz2.open(path, "rb")
    else:
        f = io.open(path, "rb")
    read = f.read()
    if encoding is not None:
        read = read.decode(encoding)
    else:
        read = read.decode("utf-8", "ignore")
    f.close()
    return read.splitlines()


def write_file(text, path, encoding="utf-8", newline=""):
    """
    Write an editor to a file on disk.

    Args:
        text (str): Text to write
        path (str): Full file path
        encoding (str): File encoding (default utf-8)
        newline (str): Newline delimiter
    """
    with io.open(path, "w", newline=newline, encoding=encoding) as f:
        try:
            f.write(text)
        except TypeError:
            f.write(unicode(text))


@typed
class Match(object):
    """A key/value pair containing line number and line text."""
    num = Typed(int)
    text = Typed(str)
    rep = Typed(int)

    def __init__(self, num, text, rep=20):
        self.num = num
        self.text = text
        self.rep = rep

    def __repr__(self):
        if len(self.text) > self.rep:
            text = self.text[:self.rep] + "..."
        else:
            text = self.text
        return "{}: {}".format(self.num, text)


@typed
class Matches(object):
    """A Dictionary like object for storing matches of text searches."""
    _matches = Typed(list)
    _pattern = Typed(str)

    def numpairs(self):
        """Yield sequential line numbers of matches."""
        n = len(self._matches)//2
        for i in range(n):
            yield self._matches[i].num, self._matches[i+1].num

    def items(self):
        """Iterator that yields individual matches as tuples."""
        for match in self._matches:
            yield match.num, match.text

    def add(self, *matches):
        self._matches = sorted(self._matches+list(matches), key=lambda m: m.num)

    def __getitem__(self, num):
        return self._matches[num]

    def __len__(self):
        return len(self._matches)

    def __init__(self, pattern, *matches):
        self._matches = []
        self._pattern = pattern
        self.add(*matches)

    def __repr__(self):
        return "Matches({}, matches={})".format(self._pattern, len(self._matches))


class Found(object):
    """Result of an editor search."""
    def all(self):
        matches = [m for match in self._patterns.values() for m in match._matches]
        return Matches(None, *matches)

    def __iter__(self):
        for i, pattern in self._patterns.items():
            yield i, pattern

    def __getitem__(self, key):
        if isinstance(key, str):
            for i in self._patterns.keys():
                if key == self._patterns[i]._pattern:
                    return self._patterns[i]
        else:
            return self._patterns[key]

    def __len__(self):
        return len(self._patterns)

    def __init__(self, *patterns):
        self._patterns = {i: Matches(pattern) for i, pattern in enumerate(patterns)}

    def __repr__(self):
        return "Found(n={})".format(len(self._patterns))


@typed
class Editor(object):
    """
    Args:
        data: File path, text, stream, or archived text file
        nprint (int): Number of lines shown by the 'repr'
        encoding (str): File encoding

    Attributes:
        lines (list):
    """
    meta = Typed(dict, doc="Document metadata")

    def copy(self):
        """
        Create a copy of the current editor's text.

        Note that this function accepts the same arguments as accepted by the
        :class:`~exa.editor.Editor` object.
        """
        cls = self.__class__
        lines = self.lines[:]
        return cls(lines)

    def format(self, *args, **kwargs):
        """
        Populate the editors templates.

        Templating uses Python's string formatting system.

        Args:
            args: Args for formatting
            kwargs: Kwargs for formatting
            inplace (bool): If True, overwrite editor's contents (default False)

        Returns:
            formatted: Returns the formatted editor (if inplace is False)
        """
        inplace = kwargs.pop("inplace", False)
        if len(args) == len(kwargs) == 0:
            return self
        if inplace:
            self.lines = str(self).format(*args, **kwargs).splitlines()
        else:
            cp = self.copy()
            cp.lines = str(cp).format(*args, **kwargs).splitlines()
            return cp

    def write(self, path, encoding="utf-8", newline="", *args, **kwargs):
        """
        Write editor contents to file.

        Args:
            path (str): Full file path
            args: Positional arguments for formatting
            kwargs: Keyword arguments for formatting

        """
        if len(args) > 0 or len(kwargs) > 0:
            text = str(self.format(*args, **kwargs))
        else:
            text = str(self)
        return write_file(text, path, encoding, newline)

    def find(self, *patterns, **kwargs):
        """
        Search line by line for given patterns.

        Args:
            patterns: String text to search for
            case (bool): Consider character case (default true)

        Returns:
            found (:class:`~exa.core.editor.Found`): Enumerated results

        Note:
            For multiline patterns use :func:`~exa.core.editor.Editor.regex`.
        """
        case = kwargs.pop("case", True)
        if case:
            check = lambda pat, lin: pat in lin
        else:
            patterns = [pattern.lower() for pattern in patterns]
            check = lambda pat, lin: pat in lin.lower()
        matches = Found(*patterns)
        for i, line in enumerate(self):
            for pattern in patterns:
                if check(pattern, line):
                    matches[pattern].add(Match(i, line))
        return matches

    def __iter__(self):
        for line in self.lines:
            yield line

    def __contains__(self, text):
        if not isinstance(text, str):
            text = str(text)
        # Use __iter__
        for line in self:
            if text in line:
                return True
        return False

    def __delitem__(self, line):
        del self.lines[line]

    def __getitem__(self, key):
        cls = self.__class__
        # The following makes a copy
        if isinstance(key, (tuple, list)):
            lines = [self.lines[i] for i in key]
        else:
            lines = self.lines[key]
        return cls(lines)

    def __setitem__(self, line, value):
        self.lines[line] = value

    def __str__(self):
        return "\n".join(self.lines)

    def __len__(self):
        return len(self.lines)

    def __init__(self, textobj, encoding=None, nprint=30):
        if isinstance(textobj, str) and os.path.exists(textobj):
            lines = read_file(textobj, encoding=encoding)
        elif isinstance(textobj, six.string_types):
            lines = str(textobj).splitlines()
        elif isinstance(textobj, (list, tuple)) and isinstance(textobj[0], six.string_types):
            lines = textobj
        elif isinstance(textobj, (TextIOWrapper, StringIO)):
            lines = textobj.read().splitlines()
        else:
            raise TypeError("Object of type {} not supported by Editors.".format(type(textobj)))
        self.lines = lines
        self.cursor = 0
        self.nprint = nprint

    def __repr__(self):
        r = ""
        nn = len(self)
        n = len(str(nn))
        fmt = "{0}: {1}".format
        if nn > 2*self.nprint:
            r += "\n".join(map(fmt, range(self.nprint), self.lines[:self.nprint]))
            r += "...\n".rjust(n, " ")
            r += "\n".join(map(fmt, range(self.nprint), self.lines[-self.nprint:]))
        else:
            r += "\n".join(map(fmt, range(len(self)), self.lines))
        return r






#import os, re, sys, bz2, gzip, six, json
#import pandas as pd
#from copy import copy, deepcopy
#from collections import defaultdict
#from itertools import chain
#from io import StringIO, TextIOWrapper
#from IPython.display import display
#from .base import Base
#from exa import TypedProperty
#from exa.typed import yield_typed
#if not hasattr(bz2, "open"):
#    bz2.open = bz2.BZ2File
#
#
#@typed
#class Editor(object):
#    """
#    An in memory representation of a text file.
#
#    The editor can be used to quickly and efficiently convert text data
#    to Python objects such as ints, floats, lists, arrays, etc.
#
#    Args:
#        data: File path, text, stream, or archived text file
#        nprint (int): Number of lines shown by the 'repr'
#        encoding (str): File encoding
#        meta (dict): Metadata
#        path_check (bool): Force file path check (default true)
#        ignore_warning (bool): Ignore file path warning (default false)
#
#    Attributes:
#        cursor (int): Cursor position (line number)
#        _fmt (str): Format string for display ('repr')
#        _tmpl (str): Regex for identifying templates
#
#    See Also:
#        :class:`~exa.core.composer.Compser`s are useful for building text
#        files programmatically. The :mod:`~exa.core.parser` module provides
#        classes useful for programatic parsing of text files.
#    """
#    _fmt = "{0}: {1}\n".format
#    _tmpl = "{.*?}"
#    meta = TypedProperty(dict, "Editor metadata")
#
#    @property
#    def templates(self):
#        """
#        Display a list of Python string templates present in this text.
#
#        .. code-block:: text
#
#            tmpl = "this is a {template}"
#            tmpl.format(template="other text")    # prints "this is a other text"
#
#        See Also:
#            `String formatting`_.
#
#        .. _String formatting: https://docs.python.org/3.6/library/string.html
#        """
#        return [match[1:-1] for match in self.regex(self._tmpl, num=False)[self._tmpl] if not match.startswith("{{")]
#
#    @property
#    def constants(self):
#        """
#        Display test of literal curly braces.
#
#        .. code-block:: text
#
#            cnst = "this is a {{constant}}"   # Cannot be "formatted"
#
#        See Also:
#            `String formatting`_.
#
#        .. _String formatting: https://docs.python.org/3.6/library/string.html
#        """
#        return [match[2:-1] for match in self.regex(self._tmpl, num=False)[self._tmpl] if match.startswith("{{")]
#
#    def regex(self, *patterns, **kwargs):
#        """
#        Match a line or lines by the specified regular expression(s).
#
#        Returned values may be a list of (number, text) pairs or a list of line
#        numbers or a list of text strings.
#
#        .. code-block:: python
#
#            ed = Editor(text)
#            ed.regex("^=+$")            # Returns (line number, text) pairs where the line contains only '='
#            ed.regex("^=+$", "find")    # Search for multiple regex simultaneously
#
#        Args:
#            patterns: Regular expressions
#            num (bool): Return line number (default true)
#            text (bool): Return line text (default true)
#            flags: Python regex flags (default re.MULTILINE)
#
#        Returns:
#            results (dict): Dictionary with pattern keys and list of values
#
#        Note:
#            By default, regular expression search multiple lines (``re.MULTILINE``).
#
#        See Also:
#            https://en.wikipedia.org/wiki/Regular_expression
#        """
#        num = kwargs.pop("num", True)
#        text = kwargs.pop("text", True)
#        flags = kwargs.pop('flags', re.MULTILINE)
#        results = defaultdict(list)
#        self_str = str(self)
#        for pattern in patterns:
#            match = pattern
#            if not type(pattern).__name__ == "SRE_Pattern":    # Compiled regular expression type check
#                match = re.compile(pattern, flags)
#            if num and text:
#                for m in match.finditer(self_str):
#                    results[match.pattern].append((self_str.count("\n", 0, m.start()) + 1, m.group()))
#            elif num:
#                for m in match.finditer(self_str):
#                    results[match.pattern].append(self_str.count("\n", 0, m.start()) + 1)
#            elif text:
#                for m in match.finditer(self_str):
#                    results[match.pattern].append(m.group())
#            else:
#                raise ValueError("At least one of ``num`` or ``text`` must be true.")
#        return results
#
#    def find(self, *patterns, **kwargs):
#        """
#        Search for patterns line by line.
#
#        Args:
#            strings (str): Any number of strings to search for
#            case (bool): Check case (default true)
#            num (bool): Return line number (default true)
#            text (bool): Return line text (default true)
#
#        Returns:
#            results (dict): Dictionary with pattern keys and list of (lineno, line) values
#        """
#        num = kwargs.pop("num", True)
#        text = kwargs.pop("text", True)
#        case = kwargs.pop("case", True)
#        results = defaultdict(list)
#        for i, line in enumerate(self):
#            for pattern in patterns:
#                if case:
#                    check = pattern in line
#                else:
#                    check = pattern.lower() in line.lower()
#                if check:
#                    if num and text:
#                        results[pattern].append((i, line))
#                    elif num:
#                        results[pattern].append(i)
#                    elif text:
#                        results[pattern].append(line)
#                    else:
#                        raise ValueError("At least one of ``num`` or ``text`` must be true.")
#        return results
#
#    def find_next(self, pattern, num=True, text=True, reverse=False):
#        """
#        From the current cursor position, find the next occurrence of the pattern.
#
#        Args:
#            pattern (str): String to search for from the cursor
#            num (bool): Return line number (default true)
#            text (bool): Return line text (default true)
#            reverse (bool): Find next in reverse (default false)
#
#        Returns:
#            tup (tuple): Tuple of line number and line of next occurrence
#
#        Note:
#            Searching will cycle the file and continue if an occurrence is not
#            found (forward or reverse direction determined by ``reverse``).
#        """
#        n = len(self)
#        n1 = n - 1
#        if reverse:
#            self.cursor = 0 if self.cursor == 0 else self.cursor - 1
#            positions = [(self.cursor - 1, 0, -1), (n1, self.cursor, -1)]
#        else:
#            self.cursor = 0 if self.cursor == n1 else self.cursor + 1
#            positions = [(self.cursor, n, 1), (0, self.cursor, 1)]
#        for start, stop, inc in positions:
#            for i in range(start, stop, inc):
#                if pattern in str(self[i]):
#                    self.cursor = i
#                    if num and text:
#                        return (i, str(self[i]))
#                    elif num:
#                        return i
#                    elif text:
#                        return str(self[i])
#                    else:
#                        raise ValueError("At least one of ``num`` or ``text`` must be true.")
#
#    def copy(self):
#        """Return a copy of the current editor."""
#        special = ("_lines", "as_interned", "nprint", "meta", "encoding")
#        cls = self.__class__
#        lines = self._lines[:]
#        as_interned = copy(self.as_interned)
#        nprint = copy(self.nprint)
#        meta = deepcopy(self.meta)
#        encoding = copy(self.encoding)
#        cp = {k: copy(v) for k, v in self._vars(True).items() if k not in special}
#        return cls(lines, as_interned, nprint, meta, encoding, **cp)
#
#    def format(self, *args, **kwargs):
#        """
#        Populate the editors templates.
#
#        Args:
#            args: Args for formatting
#            kwargs: Kwargs for formatting
#            inplace (bool): If True, overwrite editor's contents (default False)
#
#        Returns:
#            formatted: Returns the formatted editor (if inplace is False)
#        """
#        inplace = kwargs.pop("inplace", False)
#        if inplace:
#            self._lines = str(self).format(*args, **kwargs).splitlines()
#        else:
#            cp = self.copy()
#            cp._lines = str(cp).format(*args, **kwargs).splitlines()
#            return cp
#
#    def write(self, path, *args, **kwargs):
#        """
#        Write the editor contents to a file.
#
#        Args:
#            path (str): Full file path (default none, prints to stdout)
#            args: Positional arguments for formatting
#            kwargs: Keyword arguments for formatting
#        """
#        with open(path, "wb") as f:
#            if len(args) > 0 or len(kwargs) > 0:
#                f.write(six.b(str(self.format(*args, **kwargs))))
#            else:
#                f.write(six.b(str(self)))
#
#    def head(self, n=10):
#        """Display the top of the file."""
#        return "\n".join(self._lines[:n])
#
#    def tail(self, n=10):
#        """Display the bottom of the file."""
#        return "\n".join(self._lines[-n:])
#
#    def append(self, lines):
#        """
#        Append lines to the editor.
#
#        Args:
#            lines (list, str): List of lines or text to append to the editor
#
#        Note:
#            Occurs in-place, like ``list.append``.
#        """
#        if isinstance(lines, list):
#            self._lines += lines
#        elif isinstance(lines, six.string_types):
#            self._lines += lines.splitlines()
#        else:
#            raise TypeError("Unsupported type {} for lines.".format(type(lines)))
#
#    def prepend(self, lines):
#        """
#        Prepend lines to the editor.
#
#        Args:
#            lines (list, str): List of lines or text to append to the editor
#
#        Note:
#            Occurs in-place, like ``list.insert(0, ...)``.
#        """
#        if isinstance(lines, list):
#            self._lines = lines + self._lines
#        elif isinstance(lines, six.string_types):
#            self._lines = lines.splitlines() + self._lines
#        else:
#            raise TypeError("Unsupported type {} for lines.".format(type(lines)))
#
#    def insert(self, lineno, lines):
#        """
#        Insert lines into the editor after ``lineno``.
#
#        Args:
#            num (int): Line number after which to insert lines
#            text (list, str): List of lines or text to append to the editor
#
#        Note:
#            Occurs in-place, like ``list.insert(...)``.
#        """
#        if isinstance(lines, six.string_types):
#            lines = lines.splitlines()
#        elif not isinstance(lines, list):
#            raise TypeError("Unsupported type {} for lines.".format(type(lines)))
#        self._lines = self._lines[:lineno] + lines + self._lines[lineno:]
#
#    def replace(self, pattern, replacement, inplace=False):
#        """
#        Replace all instances of a pattern with a replacement.
#
#        Args:
#            pattern (str): Pattern to replace
#            replacement (str): Text to insert
#
#        """
#        lines = []
#        for line in self:
#            lines.append(line.replace(pattern, replacement))
#        if inplace:
#            self._lines = lines
#        else:
#            new = self.copy()
#            new._lines = lines
#            return new
#
#    def remove_blank_lines(self):
#        """Remove all blank lines (blank lines are those with zero characters)."""
#        to_remove = []
#        for i, line in enumerate(self):
#            ln = line.strip()
#            if ln == '':
#                to_remove.append(i)
#        self.delete_lines(to_remove)
#
#    def delete_lines(self, lines):
#        """
#        Delete all lines with given line numbers.
#
#        Args:
#            lines (list): List of integers corresponding to line numbers to delete
#        """
#        for k, i in enumerate(sorted(lines)):
#            del self[i-k]
#
#    def iterlines(self, start=0, stop=None, step=None):
#        """Line generator."""
#        for line in self._lines[slice(start, stop, step)]:
#            yield line
#
#    def info(self, df=False):
#        """
#        Describe the current editor and its data objects.
#
#        Args:
#            df (bool): If true, returns the full dataframe
#        """
#        l = len(self)
#        f = self.meta['filepath'] if self.meta is not None and "filepath" in self.meta else "NA"
#        print("Basic Info:\n    file length: {0}\n    file name: {1}".format(l, f))
#        names = []
#        types = []
#        docs = []
#        for name, _ in yield_typed(self):
#            attr = getattr(self, name)
#            names.append(name)
#            types.append(type(attr))
#            docs.append(attr.__doc__)
#        df_ = pd.DataFrame.from_dict({'name': names, 'data_type': types, 'docs': docs}).set_index('name')
#        display(df_)
#        if df:
#            return df_
#
#    def to_stream(self):
#        """Send editor text to a file stream (StringIO) object."""
#        return StringIO(six.u(str(self)))
#
#    def to_file(self, path, *args, **kwargs):
#        """Convenience name for :func:`~exa.core.editor.Editor.write`."""
#        self.write(path, *args, **kwargs)
#
#    def to_data(self, kind='pdcsv', *args, **kwargs):
#        """
#        Create a single appropriate data object using pandas read_csv.
#
#        Args:
#            kind (str): One of `pdcsv`_, `pdjson`_, `json`_, `fwf`_
#            args: Arguments to be passed to the pandas function
#            kwargs: Arguments to be passed to the pandas function
#
#        .. _pdcsv: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html
#        .. _pdjson: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_json.html
#        .. _json: https://docs.python.org/3/library/json.html
#        .. _fwf: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_fwf.html
#        """
#        if kind == "pdcsv":
#            return pd.read_csv(self.to_stream(), *args, **kwargs)
#        elif kind == "pdjson":
#            return pd.read_json(self.to_stream(), *args, **kwargs)
#        elif kind == "json":
#            return json.load(self.to_stream())
#        elif kind == "fwf":
#            return pd.read_fwf(self.to_stream(), *args, **kwargs)
#        else:
#            raise ValueError("Unexpected kind ({})".format(kind))
#
#    def __eq__(self, other):
#        if isinstance(other, Editor) and self._lines == other._lines:
#            return True
#        return False
#
#    def __len__(self):
#        return len(self._lines)
#
#    def __iter__(self):
#        for line in self._lines:
#            yield line
#
#    def __str__(self):
#        return '\n'.join(self._lines)
#
#    def __contains__(self, item):
#        for obj in self:
#            if item in obj:
#                return True
#
#    def __delitem__(self, line):
#        del self._lines[line]
#
#    def __getitem__(self, key):
#        # Getting attribute
#        if isinstance(key, six.string_types):
#            return getattr(self, key)
#        # Slicing a new editor
#        kwargs = {'nprint': self.nprint, 'meta': self.meta, 'path_check': False,
#                  'encoding': self.encoding, 'as_interned': self.as_interned}
#        if isinstance(key, (tuple, list)):
#            lines = [self._lines[i] for i in key]
#        else:
#            lines = self._lines[key]
#        return self.__class__(lines, **kwargs)
#
#    def __setitem__(self, line, value):
#        self._lines[line] = value
#
#    def __init__(self, data, *args, **kwargs):
#        as_interned = kwargs.pop("as_interned", False)
#        nprint = kwargs.pop("nprint", 30)
#        encoding = kwargs.pop("encoding", "utf-8")
#        meta = kwargs.pop("meta", None)
#        path_check = kwargs.pop("path_check", True)
#        ignore_warning = kwargs.pop("ignore_warning", False)
#        super(Editor, self).__init__(*args, **kwargs)
#        filepath = None
#        if path_check and check_path(data, ignore_warning):
#            self._lines = read_file(data, as_interned, encoding)
#            filepath = data
#        elif isinstance(data, six.string_types):
#            self._lines = read_string(data, as_interned)
#        elif isinstance(data, (TextIOWrapper, StringIO)):
#            self._lines = read_stream(data, as_interned)
#        elif isinstance(data, list) and all(isinstance(dat, six.string_types) for dat in data):
#            self._lines = data
#        elif isinstance(data, Editor):
#            self._lines = data._lines
#        else:
#            raise TypeError("Unknown type for arg data: {}".format(type(data)))
#        self.nprint = nprint
#        self.as_interned = as_interned
#        self.encoding = encoding
#        self.meta = meta
#        self.cursor = 0
#        if filepath is not None:
#            try:
#                self.meta['filepath'] = filepath
#            except TypeError:
#                self.meta = {'filepath': filepath}
#        else:
#            self.meta = {'filepath': None}
#
#    def __repr__(self):
#        r = ""
#        nn = len(self)
#        n = len(str(nn))
#        if nn > self.nprint * 2:
#            for i in range(self.nprint):
#                ln = str(i).rjust(n, " ")
#                r += self._fmt(ln, self._lines[i])
#            r += "...\n".rjust(n, " ")
#            for i in range(nn - self.nprint, nn):
#                ln = str(i).rjust(n, " ")
#                r += self._fmt(ln, self._lines[i])
#        else:
#            for i, line in enumerate(self):
#                ln = str(i).rjust(n, " ")
#                r += self._fmt(ln, line)
#        return r
#
#
#def check_path(path, ignore_warning=False):
#    """
#    Check if path is or looks like a file path (path can be any string data).
#
#    Args:
#        path (str): Potential file path
#        ignore_warning (bool): Force returning true
#
#    Returns:
#        result (bool): True if file path or warning ignored, false otherwise
#    """
#    try:
#        if os.path.exists(path) or (len(path.split("\n")) == 1 and os.sep in path):
#            if ignore_warning:
#                return False
#            return True
#    except TypeError:    # Argument ``path`` is not a string file path
#        return False
#
#
#def read_file(path, as_interned=False, encoding="utf-8"):
#    """
#    Create a list of file lines from a given filepath.
#
#    Interning lines is useful for large files that contain some repeating
#    information.
#
#    Args:
#        path (str): File path
#        as_interned (bool): Memory savings for large repeating text files
#
#    Returns:
#        strings (list): File line list
#    """
#    lines = None
#    if path.endswith(".gz"):
#        f = gzip.open(path, "rb")
#    elif path.endswith(".bz2"):
#        f = bz2.open(path, "rb")
#    else:
#        f = open(path, "rb")
#    read = f.read()
#    try:
#        read = read.decode(encoding)
#    except (AttributeError, UnicodeError):
#        pass
#    if as_interned:
#        lines = [sys.intern(line) for line in read.splitlines()]
#    else:
#        lines = read.splitlines()
#    f.close()
#    return lines
#
#
#def read_stream(f, as_interned=False):
#    """
#    Create a list of file lines from a given file stream.
#
#    Args:
#        f (:class:`~io.TextIOWrapper`): File stream
#        as_interned (bool): Memory savings for large repeating text files
#
#    Returns:
#        strings (list): File line list
#    """
#    if as_interned:
#        return [sys.intern(line) for line in f.read().splitlines()]
#    return f.read().splitlines()
#
#
#def read_string(string, as_interned=False):
#    """
#    Create a list of file lines from a given string.
#
#    Args:
#        string (str): File string
#        as_interned (bool): Memory savings for large repeating text files
#
#    Returns:
#        strings (list): File line list
#    """
#    if as_interned:
#        return [sys.intern(line) for line in string.splitlines()]
#    return string.splitlines()
#
#
#def concat(*editors, **kwargs):
#    """
#    Concatenate a collection of editors into a single editor.
#
#    Args:
#        editors: Collection of editors (in order) to be concatenated
#        kwargs: Arguments for editor creation
#
#    Returns:
#        editor: An instance of an editor
#
#    Note:
#        Metadata, names, descriptsion, etc. are not automatically propagated.
#    """
#    return Editor(list(chain(*(ed._lines for ed in editors))), **kwargs)
