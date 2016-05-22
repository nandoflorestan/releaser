# -*- coding: utf-8 -*-

"""Deals with version numbers through literate regular expressions."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import codecs
import re
from bag.text import content_of
from grimace import RE  # https://github.com/benlast/grimace/wiki/Documentation


VERSION_NUMBER = str(
    RE().one_or_more.digits.dot.one_or_more.digits
    .then.any_number_of.any_of('0123456789-.()abcdefghijklmnopqrstuvwxyz'))
VERSION_NUMBER_RE = re.compile(VERSION_NUMBER)
VERSION_VALIDATOR = '^' + VERSION_NUMBER + '$'
VERSION_VALIDATOR_RE = re.compile(VERSION_VALIDATOR)


def error_in_version(val, allow_dev=True):
    """Validate a version number. Returns None if valid."""
    if not VERSION_VALIDATOR_RE.match(val):
        return '"{0}" is not a valid version number.'.format(val)
    if not allow_dev:
        for x in ('svn', 'dev', '('):
            if x in val:
                return '"{0}" is a development version number.'.format(val)


SOME_QUOTE = r'["\']'  # single or double quote
QUOTED_VERSION = SOME_QUOTE + '(' + VERSION_NUMBER + ')' + SOME_QUOTE


def version_in_python_source(text, replace=None, keyword='version'):
    """Given a string, finds or replaces the version number in it.

    If ``replace`` is None, returns the version number found in ``text``.
    Else, returns an updated ``text`` (with the version number specified in
    the ``replace`` argument).
    """
    PYTHON_VERSION_LINE = str(
        RE().zero_or_more.whitespace
        .between(0, 2).underscore.then(keyword).then.between(0, 2).underscore
        .then.zero_or_more.whitespace.then('=').then.zero_or_more.whitespace
        .then.regex(QUOTED_VERSION).then.zero_or_more.whitespace)
    PYTHON_VERSION_LINE_RE = re.compile(PYTHON_VERSION_LINE)
    match = PYTHON_VERSION_LINE_RE.search(text)
    assert match, 'Could not find version number in Python source code.'
    version = match.groups()[0]
    if replace:
        alist = []
        found = False
        for line in text.splitlines(True):  # True keeps line endings
            match = PYTHON_VERSION_LINE_RE.match(line)
            if not found and match:
                found = True
                line = line.replace(version, replace)
            alist.append(line)
        assert found, 'Could not replace version number in Python source code.'
        return ''.join(alist)
    else:
        return version


def version_in_python_source_file(path, replace=None, keyword='version',
                                  encoding='utf-8'):
    """Given a file path, returns or replaces the version number in it.

    If replace is None, returns the version number found in file ``path``.
    Else, replaces the version number with the one specified in ``replace``.
    """
    ret = version_in_python_source(content_of(path, encoding=encoding),
                                   replace=replace, keyword=keyword)
    if replace:
        with codecs.open(path, 'w', encoding=encoding) as stream:
            stream.write(ret)
        # Test the change we just did by reading the file we just wrote
        assert replace == version_in_python_source_file(
            path, keyword=keyword, encoding=encoding)
    else:
        return ret
