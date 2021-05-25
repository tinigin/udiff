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


"""Classes used by the unified diff parser."""


from __future__ import unicode_literals

import codecs
import sys
import re

from udiff.constants import (
    DEFAULT_ENCODING,
    LINE_TYPE_ADDED,
    LINE_TYPE_CONTEXT,
    LINE_TYPE_REMOVED,
    RE_OLD_MODE,
    RE_NEW_MODE,
    RE_DELETED_FILE_MODE,
    RE_NEW_FILE_MODE,
    RE_COPY_FROM,
    RE_COPY_TO,
    RE_RENAME_FROM,
    RE_RENAME_TO,
    RE_SIMILARITY_INDEX,
    RE_DISSIMILARITY_INDEX,
    RE_INDEX,
    RE_BINARY_FILES,
    RE_BINARY_DIFF,
    RE_COMBINED_INDEX,
    RE_COMBINED_MODE,
    RE_COMBINED_NEW_FILE,
    RE_COMBINED_DELETED_FILE,
    RE_GIT_DIFF_START,
    RE_SPECIALS_RULE,
    BASE_DIFF_FILENAME_PREFIXES,
    OLD_FILE_NAME_HEADER,
    NEW_FILE_NAME_HEADER,
    RE_HUNK_HEADER_V1,
    RE_HUNK_HEADER_V2,
    HUNK_HEADER_PREFIX,
    d
)
from udiff.errors import UdiffParseError


PY2 = sys.version_info[0] == 2
if PY2:
    open_file = codecs.open
    make_str = lambda x: x.encode(DEFAULT_ENCODING)

    def implements_to_string(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode(DEFAULT_ENCODING)
        return cls

else:
    open_file = open
    make_str = str
    implements_to_string = lambda x: x
    unicode = str
    basestring = str


def merge_two_dicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


@implements_to_string
class UdiffLine(object):
    """A diff line."""

    source_line_no = None
    target_line_no = None
    line_type = None
    content = ''

    def __init__(self, content, line_type=None, source_line_no=None, target_line_no=None):
        super(UdiffLine, self).__init__()
        self.source_line_no = source_line_no
        self.target_line_no = target_line_no
        self.line_type = line_type
        self.content = content

    def __repr__(self):
        return make_str("<UdiffLine: %s%s>") % (self.line_type, self.content)

    def __str__(self):
        return "%s%s\n" % (self.line_type, self.content)

    def __eq__(self, other):
        return (self.source_line_no == other.source_line_no and
                self.target_line_no == other.target_line_no and
                self.line_type == other.line_type and
                self.content == other.content)

    @property
    def is_added(self):
        return self.line_type == LINE_TYPE_ADDED

    @property
    def is_removed(self):
        return self.line_type == LINE_TYPE_REMOVED

    @property
    def is_context(self):
        return self.line_type == LINE_TYPE_CONTEXT


@implements_to_string
class UdiffBlock(list):
    """A diff block."""

    old_start_line = None
    old_start_line_2 = None
    new_start_line = None
    header = ''

    def __init__(self, header='', old_start_line=None, old_start_line_2=None, new_start_line=None):
        super(UdiffBlock, self).__init__()
        self.old_start_line = old_start_line
        self.old_start_line_2 = old_start_line_2
        self.new_start_line = new_start_line
        self.header = header

    def __repr__(self):
        value = "<UdiffBlock: %s, added %s, removed %s, context %s>" % (self.header, self.added, self.removed, self.modified)
        return make_str(value)

    def __str__(self):
        return "%s, added %s, removed %s, context %s\n" % (self.header, self.added, self.removed, self.modified)

    @property
    def object(self):
        return merge_two_dicts(self.__dict__, {'lines': [x.__dict__ for x in self]})

    @property
    def added(self):
        return sum([1 for l in self if l.is_added])

    @property
    def removed(self):
        return sum([1 for l in self if l.is_removed])

    @property
    def modified(self):
        return sum([1 for l in self if l.is_context])


@implements_to_string
class UdiffFile(list):
    """A diff file."""

    old_name = None
    new_name = None
    added_lines = 0
    deleted_lines = 0
    is_git_diff = False
    is_combined = False
    language = None
    mode = None
    old_mode = None
    new_mode = None
    deleted_file_mode = None
    new_file_mode = None
    is_deleted = False
    is_new = False
    is_copy = False
    is_rename = False
    is_binary = False
    is_too_big = False
    unchanged_percentage = 0
    changed_percentage = 0
    checksum_before = None
    checksum_after = None

    def __init__(self, deleted_lines=0, added_lines=0):
        super(UdiffFile, self).__init__()

        self.deleted_lines = deleted_lines
        self.added_lines = added_lines

    def __repr__(self):
        value = "<UdiffFile: %s, %s>" % (
            self.new_name if self.new_name else self.old_name,
            'added' if self.is_new else 'deleted' if self.is_deleted else 'modified'
        )

        return make_str(value)

    def __str__(self):
        header = "UdiffFile (%s, %s)\n" % (
            self.new_name if self.new_name else self.old_name,
            'added' if self.is_new else 'deleted' if self.is_deleted else 'modified'
        )

        return header + ''.join(unicode(block) for block in self)

    @property
    def object(self):
        return merge_two_dicts(self.__dict__, {'blocks': [x.object for x in self]})

    @property
    def is_added_file(self):
        return self.is_new

    @property
    def is_removed_file(self):
        return self.is_deleted

    @property
    def is_modified_file(self):
        return not self.is_new and not self.is_deleted


@implements_to_string
class UdiffParser(list):
    """Udiff Parser."""

    options = {
        'encoding': None,
        'dst_prefix': None,
        'src_prefix': None,
        'diff_max_changes': None,
        'diff_max_line_length': None,
        'diff_too_big_message': ''
    }

    current_file = None
    possible_old_name = None
    possible_new_name = None

    current_block = None
    old_start_line = None
    old_start_line_2 = None
    new_start_line = None

    def __init__(self, content, options=None):
        super(UdiffParser, self).__init__()

        if options:
            self._set_options(options)
        else:
            self._reset_options()

        # convert string inputs to StringIO objects
        if self._get_option('encoding'):
            content = self._convert_string(content, self._get_option('encoding'))

        content = re.sub(r'\\ No newline at end of file', '', content)
        content = re.sub(r'\r\n?', '\n', content)

        content = re.sub(r'[\-]{10,}', '', content)
        content = re.sub(r'[=]{10,}', '', content)

        content = content.splitlines()

        self._parse(content)

    def __repr__(self):
        return make_str('<UdiffParser: %s>') % super(UdiffParser, self).__repr__()

    def __str__(self):
        result = 'UdiffParser (added %s, removed %s, modified %s)\n' % (self.added, self.removed, self.modified)
        for file in self:
            result += ('\n' if result else '') + unicode(file)

        return result

    def getitem(self, filename):
        for file in self:
            if (file.old_name and filename in file.old_name) or \
                    (file.new_name and filename in file.new_name):
                return file

        return None

    @property
    def object(self):
        return {
            'options': self.options,
            'files': [x.object for x in self]
        }

    def _set_options(self, options=None):
        # encoding — default utf-8
        # dst_prefix —
        # src_prefix —
        # diff_max_changes — number of changed lines after which a file diff is deemed as too big and not displayed, default is undefined
        # diff_max_line_length — number of characters in a diff line after which a file diff is deemed as too big
        # diff_too_big_message — text for diff too big

        self._reset_options()

        if options and type(options) in [dict, tuple]:
            for name, value in options.items():
                self.options[name] = value

    def _get_option(self, key, default=None):
        if key in self.options:
            return self.options[key]

        else:
            return default

    def _set_option(self, key, value=None):
        self.options[key] = value

    def _reset_options(self):
        for key, value in self.options.items():
            self.options[key] = None

    @staticmethod
    def _get_extension(filename):
        filename_parts = filename.split('.')
        return filename_parts[-1] if len(filename_parts) > 1 else ''

    @staticmethod
    def _get_filename(line, line_prefix=None, extra_prefix=None):
        prefixes = BASE_DIFF_FILENAME_PREFIXES if not extra_prefix else BASE_DIFF_FILENAME_PREFIXES + [extra_prefix]
        filename_exp = re.compile(
            r'^' + re.sub(RE_SPECIALS_RULE, '\\\\\g<1>', line_prefix) + ' "?(.+?)"?$') if line_prefix else re.compile(
            r'^"?(.+?)"?$')

        filename = filename_exp.match(line)
        if filename:
            filename = filename.group(1)

            matching_prefix = None
            for prefix in prefixes:
                if filename.startswith(prefix):
                    matching_prefix = prefix
                    break

            filename_without_prefix = filename[len(matching_prefix):] if matching_prefix else filename

            # Cleanup timestamps generated by the unified diff (diff command) as specified in
            # https://www.gnu.org/software/diffutils/manual/html_node/Detailed-Unified.html
            # Ie: 2016-10-25 11:37:14.000000000 +0200

            return re.sub(r'\s+\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)? [+-]\d{4}.*$', '', filename_without_prefix)

        return ''

    def _get_src_filename(self, line, prefix=None):
        return self._get_filename(line, '---', prefix)

    def _get_dst_filename(self, line, prefix=None):
        return self._get_filename(line, '+++', prefix)

    def _save_block(self):
        if self.current_block is not None and self.current_file is not None:
            self.current_file.append(self.current_block)
            self.current_block = None

    def _start_block(self, line):
        self._save_block()

        if self.current_file is not None:
            is_hunk_header_v1 = RE_HUNK_HEADER_V1.match(line)
            is_hunk_header_v2 = RE_HUNK_HEADER_V2.match(line)

            if is_hunk_header_v1:
                self.current_file.is_combined = False
                self.old_start_line = int(is_hunk_header_v1.group(1))
                self.new_start_line = int(is_hunk_header_v1.group(2))

            elif is_hunk_header_v2:
                self.current_file.is_combined = True
                self.old_start_line = int(is_hunk_header_v2.group(1))
                self.old_start_line_2 = int(is_hunk_header_v2.group(2))
                self.new_start_line = int(is_hunk_header_v2.group(3))

            else:
                if line.startswith(HUNK_HEADER_PREFIX):
                    # Warning
                    pass
                    # raise UdiffParseError('Failed to parse lines, starting in 0!')

                self.current_file.is_combined = False
                self.old_start_line = 0
                self.new_start_line = 0

        self.current_block = UdiffBlock(old_start_line=self.old_start_line, old_start_line_2=self.old_start_line_2,
                                        new_start_line=self.new_start_line, header=line)

    def _save_file(self):
        if self.current_file is not None:
            if not self.current_file.old_name and self.possible_old_name is not None:
                self.current_file.old_name = self.possible_old_name

            if not self.current_file.new_name and self.possible_new_name is not None:
                self.current_file.new_name = self.possible_new_name

            if self.current_file.new_name:
                self.append(self.current_file)
                self.current_file = None

        self.possible_old_name = None
        self.possible_new_name = None

    def _start_file(self):
        self._save_block()
        self._save_file()
        self.current_file = UdiffFile(deleted_lines=0, added_lines=0)

    def _exist_hunk_header(self, line, line_no):
        idx = line_no

        while idx < len(self.diff) - 3:
            if line.startswith('diff'):
                return False

            if self.diff[idx].startswith(OLD_FILE_NAME_HEADER) and \
                self.diff[idx + 1].startswith(NEW_FILE_NAME_HEADER) and \
                self.diff[idx + 2].startswith(HUNK_HEADER_PREFIX):
                return True

            idx += 1

        return False

    def _starts_with_any(self, line, prefixes):
        for prefix in prefixes:
            if line.startswith(prefix):
                return True

        return False

    def _create_line(self, line):
        if self.current_block is None or \
                self.current_file is  None or \
                self.old_start_line is None or \
                self.new_start_line is None:
            return

        current_line = UdiffLine(content=line)
        added_prefixes = ['+ ', ' +', '++'] if self.current_file.is_combined else ['+']
        delete_prefixes = ['- ', ' -', '--'] if self.current_file.is_combined else ['-']

        if self._starts_with_any(line, added_prefixes):
            self.current_file.added_lines += 1

            current_line.line_type = LINE_TYPE_ADDED
            current_line.source_line_no = None
            current_line.target_line_no = self.new_start_line
            self.new_start_line += 1

        elif self._starts_with_any(line, delete_prefixes):
            self.current_file.deleted_lines += 1

            current_line.line_type = LINE_TYPE_REMOVED

            current_line.source_line_no = self.old_start_line
            self.old_start_line += 1
            current_line.target_line_no = None

        else:
            current_line.line_type = LINE_TYPE_CONTEXT

            current_line.source_line_no = self.old_start_line
            self.old_start_line += 1
            current_line.target_line_no = self.new_start_line
            self.new_start_line += 1

        self.current_block.append(current_line)

    def _parse(self, diff):
        self.diff = diff

        for line_no, line in enumerate(self.diff):
            if not line or line.startswith('*'):
                continue

            prev_line = diff[line_no - 1] if line_no - 1 >= 0 else ''
            next_line = diff[line_no + 1] if line_no + 1 <= len(diff) - 1 else ''
            after_next_line = diff[line_no + 2] if line_no + 2 <= len(diff) - 1 else ''

            if line.startswith('diff'):
                self._start_file()

                # diff --git a / blocked_delta_results.png b / blocked_delta_results.png
                is_git_diff_start = RE_GIT_DIFF_START.match(line)
                if is_git_diff_start:
                    self.possible_old_name = self._get_filename(is_git_diff_start.group(1), extra_prefix=self._get_option('dst_prefix'))
                    self.possible_new_name = self._get_filename(is_git_diff_start.group(2), extra_prefix=self._get_option('src_prefix'))

                if self.current_file is None:
                    raise UdiffParseError('Where is my file !!!')

                self.current_file.is_git_diff = True
                continue

            if self.current_file is None or \
                    (
                        self.current_file is not None and
                        not self.current_file.is_git_diff and
                        line.startswith(OLD_FILE_NAME_HEADER) and
                        next_line.startswith(NEW_FILE_NAME_HEADER) and
                        after_next_line.startswith(HUNK_HEADER_PREFIX)
                    ):

                self._start_file()

            if self.current_file.is_too_big:
                continue

            if self.current_file is not None and (
                    (
                        self._get_option('diff_max_changes') and
                        self.current_file.added_lines + self.current_file.deleted_lines > self._get_option(
                        'diff_max_changes')
                    ) or (
                        self._get_option('diff_max_line_length') and len(line) > self._get_option(
                        'diff_max_line_length')
                    )):
                self.current_file.is_too_big = True
                self.current_file.added_lines = 0
                self.current_file.deleted_lines = 0
                self.current_file[:] = []
                self.current_block = None

                self._start_block(self._get_option('diff_too_big_message') if self._get_option(
                    'diff_too_big_message') else 'Diff too big to be displayed')
                continue

            # We need to make sure that we have the three lines of the header.
            if (line.startswith(OLD_FILE_NAME_HEADER) and next_line.startswith(NEW_FILE_NAME_HEADER)) or \
                    (line.startswith(NEW_FILE_NAME_HEADER) and prev_line.startswith(OLD_FILE_NAME_HEADER)):

                src_filename = self._get_src_filename(line)
                dst_filename = self._get_dst_filename(line)

                # --- Date Timestamp[FractionalSeconds] TimeZone
                # --- 2002-02-21 23:30:39.942229878 -0800
                if self.current_file is not None and not self.current_file.old_name and line.startswith(
                        OLD_FILE_NAME_HEADER) and src_filename:
                    self.current_file.old_name = src_filename
                    self.current_file.language = self._get_extension(self.current_file.old_name)
                    continue

                # +++ Date Timestamp[FractionalSeconds] TimeZone
                # +++ 2002-02-21 23:30:39.942229878 -0800
                if self.current_file is not None and not self.current_file.new_name and line.startswith(
                        NEW_FILE_NAME_HEADER) and dst_filename:
                    self.current_file.new_name = dst_filename
                    self.current_file.language = self._get_extension(self.current_file.new_name)
                    continue

            if self.current_file is not None and \
                    (
                        line.startswith(HUNK_HEADER_PREFIX) or
                        (
                            self.current_file.is_git_diff and
                            self.current_file.old_name and
                            self.current_file.new_name and
                            self.current_block is None
                        )
                    ):
                self._start_block(line)
                continue

            # There are three types of diff lines. These lines are defined by the way they start.
            # 1. New line     starts with: +
            # 2. Old line     starts with: -
            # 3. Context line starts with: <SPACE>
            if self.current_block is not None and \
                    (line.startswith('+') or line.startswith('-') or line.startswith(' ')):
                self._create_line(line)
                continue

            is_hunk_header_does_not_exist = not self._exist_hunk_header(line, line_no)

            if self.current_file is None:
                raise UdiffParseError('Where is my file !!!')

            # Git diffs provide more information regarding files modes, renames, copies,
            # commits between changes and similarity indexes
            for exp in [RE_OLD_MODE,
                        RE_NEW_MODE,
                        RE_DELETED_FILE_MODE,
                        RE_NEW_FILE_MODE,
                        RE_COPY_FROM,
                        RE_COPY_TO,
                        RE_RENAME_FROM,
                        RE_RENAME_TO,
                        RE_SIMILARITY_INDEX,
                        RE_DISSIMILARITY_INDEX,
                        RE_INDEX,
                        RE_BINARY_FILES,
                        RE_BINARY_DIFF,
                        RE_COMBINED_INDEX,
                        RE_COMBINED_MODE,
                        RE_COMBINED_NEW_FILE,
                        RE_COMBINED_DELETED_FILE]:
                matches = exp.match(line)
                if matches:
                    if exp == RE_OLD_MODE:
                        self.current_file.old_mode = matches.group(1)

                    elif exp == RE_NEW_MODE:
                        self.current_file.new_mode = matches.group(1)

                    elif exp == RE_DELETED_FILE_MODE:
                        self.current_file.deleted_file_mode = matches.group(1)
                        self.current_file.is_deleted = True

                    elif exp == RE_NEW_FILE_MODE:
                        self.current_file.new_file_mode = matches.group(1)
                        self.current_file.is_new = True

                    elif exp == RE_COPY_FROM:
                        if is_hunk_header_does_not_exist:
                            self.current_file.old_name = matches.group(1)
                        self.current_file.is_copy = True

                    elif exp == RE_COPY_TO:
                        if is_hunk_header_does_not_exist:
                            self.current_file.new_name = matches.group(1)
                        self.current_file.is_copy = True

                    elif exp == RE_RENAME_FROM:
                        if is_hunk_header_does_not_exist:
                            self.current_file.old_name = matches.group(1)
                        self.current_file.is_rename = True

                    elif exp == RE_RENAME_TO:
                        if is_hunk_header_does_not_exist:
                            self.current_file.new_name = matches.group(1)
                        self.current_file.is_rename = True

                    elif exp == RE_BINARY_FILES:
                        self.current_file.is_binary = True
                        self.current_file.old_name = self._get_filename(matches.group(1),
                                                                        extra_prefix=self._get_option('src_prefix'))
                        self.current_file.new_name = self._get_filename(matches.group(2),
                                                                        extra_prefix=self._get_option('dst_prefix'))
                        self._start_block('Binary file')

                    elif exp == RE_BINARY_DIFF:
                        self.current_file.is_binary = True
                        self._start_block(line)

                    elif exp == RE_SIMILARITY_INDEX:
                        self.current_file.unchanged_percentage = int(matches.group(1))

                    elif exp == RE_DISSIMILARITY_INDEX:
                        self.current_file.changed_percentage = int(matches.group(1))

                    elif exp == RE_INDEX:
                        self.current_file.checksum_before = matches.group(1)
                        self.current_file.checksum_after = matches.group(2)
                        if matches.group(3):
                            self.current_file.mode = matches.group(3)

                    elif exp == RE_COMBINED_INDEX:
                        self.current_file.checksum_before = [matches.group(2), matches.group(3)]
                        self.current_file.checksum_after = matches.group(1)

                    elif exp == RE_COMBINED_MODE:
                        self.current_file.old_mode = [matches.group(2), matches.group(3)]
                        self.current_file.new_mode = matches.group(1)

                    elif exp == RE_COMBINED_NEW_FILE:
                        self.current_file.new_file_mode = matches.group(1)
                        self.current_file.is_new = True

                    elif exp == RE_COMBINED_DELETED_FILE:
                        self.current_file.deleted_file_mode = matches.group(1)
                        self.current_file.is_deleted = True

        self._save_block()
        self._save_file()

        return self

    @staticmethod
    def _convert_string(data, encoding=None, errors='strict'):
        if encoding is not None:
            # if encoding is given, assume bytes and decode
            data = unicode(data, encoding=encoding, errors=errors)

        return data

    @classmethod
    def from_filename(cls, filename, encoding=DEFAULT_ENCODING, options=None, errors=None):
        """Return a UdiffParser instance given a diff filename."""
        with open_file(filename, 'r', encoding=encoding, errors=errors) as f:
            instance = cls(f.read(), options=options)
        return instance

    @classmethod
    def from_string(cls, data, encoding=None, options=None, errors='strict'):
        """Return a UdiffParser instance given a diff string."""
        return cls(cls._convert_string(data, encoding, errors), options=options)

    @property
    def added_files(self):
        """Return added files as a list."""
        return [f for f in self if f.is_added_file]

    @property
    def removed_files(self):
        """Return removed files as a list."""
        return [f for f in self if f.is_removed_file]

    @property
    def modified_files(self):
        """Return modified files as a list."""
        return [f for f in self if f.is_modified_file]

    @property
    def added(self):
        """Return the total added lines."""
        return sum([1 for f in self if f.is_added_file])

    @property
    def removed(self):
        """Return the total removed lines."""
        return sum([1 for f in self if f.is_removed_file])

    @property
    def modified(self):
        """Return the total modified lines."""
        return sum([1 for f in self if f.is_modified_file])
