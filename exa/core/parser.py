# -*- coding: utf-8 -*-
# Copyright (c) 2015-2017, Exa Analytics Development Team
# Distributed under the terms of the Apache License 2.0
"""
Parsing Editors
####################################
This module provides editors specifically tailored to parsing text files that
have distinct, typically repeating, regions. The paradigm followed here is to
divide up regions of text until a logical unit text is obtained. A logical
unit of text is one that contains distinct datas. A specific 'parser' is
responsible for converting that text to data.

.. code-block:: text

    42.0 42.0 42.0
    --------------
    42.0 42.0 42.0
    --------------
    42.0 42.0 42.0

Given the above text, a parser might look like the following. Note that the
``Data`` class acts as the user facing class and the ``Block`` class is what
is responsible for performing the actual parsing. We start with the parser
(``Block``) that converts a line of text between '---' delimiters to an array.

.. code-block:: python

    from exa.typed import cta

    class Block(Parser):
        array = cta("array", pd.Series)

        def _parse(self):
            # For simplicity we use built-in functionality of the
            # Editor class (of which Parser is a subclass). There are
            # other ways we could have done this and typically parsing
            # is not this straightforward or easy.
            self.array = self.to_data(delim_whitespace=True, names=range(3))

The user facing object is the editor that accepts the text sample above as a
whole; it doesn't expect a single section like the parser above.

.. code-block:: python

    class Data(Sections):
        _key_sep = "^-+$"    # Regular expression to find section delimiters
        _key_start = 0
        _key_sp = 1

        # This is the only method we need a concrete implementation for.
        # It is responsible for populating the sections attribute.
        def _parse(self):
            # In parsing the sections we simply identify lines that contain
            # only '----'
            delimlines = self.regex(self._key_sep, text=False)[self._key_sep]
            startlines = [self._key_start] + [delim + self._key_sp for delim in delimlines]
            endlines = startlines[self._key_sp:]
            endlines.append(len(self))
            parsers = [Block]*len(startlines)    # Using the parser class above
            # The ``sections`` attribute can be constructed this way
            # or by hand.
            self._sections_helper(parser=parsers, start=startlines, end=endlines)

Now we have a modular and efficient parsing system for the prototypical text
example above. Advanced machinery for lazy (automatic) parsing and additional
triggering is possible via the ``cta`` function provided by
:mod:`~exa.typed`. For examples see the tests of the aforementioned module and
of this module (:mod:`~exa.tests.test_typed` and
:mod:`~exa.core.tests.test_parser`).
"""
import six
import warnings
import numpy as np
from abc import abstractmethod
from .editor import Editor
from .dataframe import SectionDataFrame
from exa.typed import yield_typed, cta


class Sections(Editor):
    """
    An editor tailored to handling files with distinct regions of text.

    A concrete implementation of this class provides the main editor-like
    object that a user interacts with. This object's purpose is to identify
    sections based on the structure of the text it is designed for. Identified
    sections are automatically parsed. Sections may themselves be
    :class:`~exa.core.parsing.Sections` objects (i.e. sub-sections).

    The abstract method :func:`~exa.core.parsing.Sections._parse` is used to
    define the ``sections`` attribute, a dataframe containing, at a minimum,
    section starting and ending lines, and the parser name (associated with a
    :class:`~exa.core.parsing.Sections` or :class:`~exa.core.parsing.Parser`
    object). An example ``sections`` table is given below with an optional
    column, ``title``, used to aid the user in identifying sections.

    +---------+-------------+---------------+-------+-----+
    |         | parser      | title         | start | end |
    +---------+-------------+---------------+-------+-----+
    | section |             |               |       |     |
    +---------+-------------+---------------+-------+-----+
    | 0       | parser_name | Title  1      | 0     |  m  |
    +---------+-------------+---------------+-------+-----+
    | 1       | parser_name | Title  2      | m     |  n  |
    +---------+-------------+---------------+-------+-----+

    Attributes:
        sections (DataFrame): Dataframe of section numbers, names, and starting/ending lines

    See Also:
        :class:`~exa.core.parsing.Parser`
    """
    _parsers = {}
    sections = cta("sections", SectionDataFrame, "Parser sections")

    def parse(self, recursive=False, verbose=False, **kwargs):
        """
        Parse the current file.

        Args:
            recursive (bool): If true, parses all sub-section/parser objects' data
            verbose (bool): Print parser warnings
            kwargs: Keyword arguments passed to parser

        Tip:
            Helpful methods for describing parsing and data are
            :attr:`~exa.core.parsing.Sections.sections`,
            :func:`~exa.core.parsing.Sections.describe`, and
            :func:`~exa.core.parsing.Sections.describe_parsers`.

        See Also:
            :func:`~exa.core.parsing.Sections.parse_section`
        """
        # This helper function is used to setup auto-parsing, see below.
        def section_parser_helper(i):
            def section_parser():
                self.parse_section(i)
            return section_parser
        # Set the value of the ``sections`` attribute
        self._parse(**kwargs)
        if not hasattr(self, "_sections") or self._sections is None:
            raise ValueError("Parsing method ``_parse`` does not correctly set ``sections``.")
        # Now generate section attributes for the sections present
        for i, sec in self.sections.iterrows():
            parser, attrname = sec[['parser', 'attribute']]
            if not isinstance(parser, type):
                if verbose:
                    warnings.warn("No parser for section '{}'!".format(parser.__class__))
                # Default type is a simple editor
                prop = cta(attrname, Editor)
            else:
                # Otherwise use specific sections/parser
                prop = cta(attrname, parser)
            # Now we perform a bit of class gymnastics:
            # Because we don't want to attach our typed property paradigm
            # (see exa.special.cta) to all instances of this
            # object's class (note that properties must be attached to class
            # definitions not instances of a class), we dynamically create a
            # copy of this object's class, attach our properties to that
            # class definition, and set it as the class of our current object.
            cls = type(self)
            if not hasattr(cls, '__unique'):
                uniquecls = type(cls.__name__, (cls, ), {})
                uniquecls.__unique = True
                self.__class__ = uniquecls
            setattr(self.__class__, attrname, prop)
            # And attach a lazy evaluation method using the above helper.
            # Again, see exa's documentation for more information.
            setattr(self, "parse_" + attrname, section_parser_helper(i))
            if recursive:
                self.parse_section(i, recursive=True, verbose=verbose)

    def parse_section(self, number, recursive=False, verbose=False, **kwargs):
        """
        Parse specific section of this object.

        Parse section data can be accessed via the ``sectionID`` attribute, where
        ID is the number of the section as listed in the ``describe_sections``
        table or in the order given by the ``sections`` attribute.

        Args:
            number (int): Section number (of the ``sections`` list)
            recursive (bool): Parse sub-section/parser objects
            verbose (bool): Display additional warnings
            kwargs: Keyword arguments passed to parser

        Tip:
            To see what objects exist, see the :attr:`~exa.core.sections.Sections.sections`
            attribute and :func:`~exa.core.sections.Sections.describe`,
            :func:`~exa.core.sections.Sections.describe_sections`, and
            :func:`~exa.core.sections.Sections.describe_parsers`.
        """
        parser, start, end, attrname = self.sections.loc[number, ["parser", "start", "end", "attribute"]]    # HARDCODED
        if not isinstance(parser, type):
            if verbose:
                warnings.warn("No parser for section '{}'! Using generic editor.".format(parser.__name__))
            sec = Editor(self[start:end], path_check=False)
        else:
            # Note that we don't actually parse anything until an
            # attributed is requested by the user or some code...
            sec = parser(self[start:end], path_check=False)
        setattr(self, attrname, sec)
        # ...except in the case recursive is true.
        if recursive and hasattr(sec, "parse"):
            # Propagate recursion
            sec.parse(recursive=True, verbose=verbose, **kwargs)

    def get_section(self, section):
        """
        Select a section by (parser) name or section number.

        Args:
            section: Section number or parser name

        Returns:
            section_editor: Editor-like sections or parser object

        Warning:
            If multiple sections with the same parser name exist, selection must
            be performed by section number.
        """
        inttypes = six.integer_types + (np.int, np.int8, np.int16, np.int32, np.int64)
        if isinstance(section, six.string_types) and section.startswith("section"):
            return getattr(self, section)
        elif isinstance(section, six.string_types):
            idx = self.sections[self.sections["parser"] == section].index.tolist()
            if len(idx) > 1:
                raise ValueError("Multiple sections with parser name {} found".format(section))
            elif len(idx) == 0:
                raise ValueError("No sections with parser name {} found".format(section))
        elif isinstance(section, inttypes):
            idx = section
        else:
            raise TypeError("Unknown type for section arg with type {}".format(type(section)))
        idx = idx[0] if not isinstance(idx, inttypes) else idx
        return getattr(self, str(self.sections.loc[idx, "attribute"]))

    @abstractmethod
    def _parse(self, **kwargs):
        """
        This abstract method is overwritten by a concrete implementation and is
        responsible for setting the ``sections`` attribute.

        Concrete implementations depend on the specific file. Note that the names
        column of the dataframe must contain values corresponding to existing
        parsers.

        .. code-block:: python

            class MySections(Sections):
                def _parse(self):
                    # This function should actually perform parsing
                    names = [Parser0, Parser1]
                    starts = [0, 10]
                    ends = [10, 20]
                    titles = ["A Title", "Another Title"]
                    self._sections_helper(parsers, starts, ends, title=titles)
        """
        pass

    def _get_sections(self):
        """Convenience method that lazily evaluates ``sections``."""
        self.parse()

    def _sections_helper(self, parser, start, end, **kwargs):
        """
        Convenience method for building the ``sections`` attribute.

        Automatically converts class types to string names.

        .. code-block:: python

            # End of the _parse() function
            self._sections_helper(parsers, starts, ends, title=titles)
        """
        dct = {'parser': parser, 'start': start, 'end': end}
        dct.update(kwargs)
        self.sections = SectionDataFrame.from_dict(dct)


class Parser(Editor):
    """
    An editor-like object that is responsible for transforming a region
    of text into an appropriate data object or objects.

    This class can be used individually or in concert with the
    :class:`~exa.core.parsing.Sections` class to build a comprehensive parsing
    system.

    .. code-block:: python

        import pandas as pd
        from exa.typed import cta

        text = '''comment1: 1
        comment2: 2
        comment3: 3'''

        class MyParser(Parser):
            comments = cta("comments", list, "List of comments")
            data = cta("data", pd.Series)
            _key_d = ":"

            def _parse(self):
                comments = []
                data = []
                for line in self:
                    comment, dat = line.split(self._key_d)
                    comments.append(comment)
                    data.append(dat)
                self.data = data     # Automatic type conversion
                self.comments = comments

    See Also:
        :class:`~exa.core.parsing.Sections`
    """
    def parse(self, **kwargs):
        """
        Parse data objects from the current file.

        Args:
            verbose (bool): Performs a check for missing data objects
        """
        verbose = kwargs.pop("verbose", False)
        self._parse()
        if verbose:
            for name, _ in yield_typed(self.__class__):
                if not hasattr(self, name) or getattr(self, name) is None:
                    warnings.warn("Missing data object {}".format(name))

    @abstractmethod
    def _parse(self, *args, **kwargs):
        """
        The parsing algorithm, specific to the text in question, should be
        developed here. This function should assign the values of relevant
        data objects based on the parsed text.
        """
        pass