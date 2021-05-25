# encoding: utf-8

# The MIT License (MIT)
# Copyright (c) 2021 Dmitrii Tinigin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.


"""Useful constants and regexes used by the package."""

from __future__ import unicode_literals

import re


BASE_DIFF_FILENAME_PREFIXES = ['a/', 'b/', 'i/', 'w/', 'c/', 'o/']

RE_SPECIALS = [
  # Order matters for these
  '-',
  '[',
  ']',
  # Order doesn't matter for any of these
  '/',
  '{',
  '}',
  '(',
  ')',
  '*',
  '+',
  '?',
  '.',
  '\\',
  '^',
  '$',
  '|',
]

# All characters will be escaped with '\'
# even though only some strictly require it when inside of []
RE_SPECIALS_RULE = '([' + '\\'.join(RE_SPECIALS) + '])'

OLD_FILE_NAME_HEADER = '--- '
NEW_FILE_NAME_HEADER = '+++ '
HUNK_HEADER_PREFIX = '@@'

RE_GIT_DIFF_START = re.compile(r'^diff --git "?(.+)"? "?(.+)"?')

RE_HUNK_HEADER_V1 = re.compile(r'^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@.*')
RE_HUNK_HEADER_V2 = re.compile(r'@@@ -(\d+)(?:,\d+)? -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@@.*')

RE_OLD_MODE = re.compile(r'^old mode (\d{6})')
RE_NEW_MODE = re.compile(r'^new mode (\d{6})')
RE_DELETED_FILE_MODE = re.compile(r'^deleted file mode (\d{6})')
RE_NEW_FILE_MODE = re.compile(r'^new file mode (\d{6})')

RE_COPY_FROM = re.compile(r'^copy from "?(.+)"?')
RE_COPY_TO = re.compile(r'^copy to "?(.+)"?')

RE_RENAME_FROM = re.compile(r'^rename from "?(.+)"?')
RE_RENAME_TO = re.compile(r'^rename to "?(.+)"?')

RE_SIMILARITY_INDEX = re.compile(r'^similarity index (\d+)%')
RE_DISSIMILARITY_INDEX = re.compile(r'^dissimilarity index (\d+)%')
RE_INDEX = re.compile(r'^index ([\da-z]+)\.\.([\da-z]+)\s*(\d{6})?')

RE_BINARY_FILES = re.compile(r'^Binary files (.*) and (.*) differ')
RE_BINARY_DIFF = re.compile(r'^GIT binary patch')

RE_COMBINED_INDEX = re.compile(r'^index ([\da-z]+),([\da-z]+)\.\.([\da-z]+)')
RE_COMBINED_MODE = re.compile(r'^mode (\d{6}),(\d{6})\.\.(\d{6})')
RE_COMBINED_NEW_FILE = re.compile(r'^new file mode (\d{6})')
RE_COMBINED_DELETED_FILE = re.compile(r'^deleted file mode (\d{6}),(\d{6})')

DEFAULT_ENCODING = 'UTF-8'

LINE_TYPE_ADDED = '+'
LINE_TYPE_REMOVED = '-'
LINE_TYPE_CONTEXT = ' '
LINE_TYPE_EMPTY = ''
LINE_TYPE_NO_NEWLINE = '\\'
LINE_VALUE_NO_NEWLINE = ' No newline at end of file'


def d(*vars):
    """ Debug object """

    import pprint
    import types
    import sys

    pp = pprint.PrettyPrinter(indent=2)
    for var in vars:
        if type(var) == types.MethodType:
            var = dir(var)

        pp.pprint(var)

    sys.exit(1)
