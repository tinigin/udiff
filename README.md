# Udiff

**Udiff** is a simple library for parsing unified diff.

```python
>>> import udiff
>>> d = udiff.UdiffParser('diff --git a/sample b/sample\nindex 0000001..0ddf2ba\n--- a/sample\n+++ b/sample\n@@ -1 +1 @@\n-test\n+test1r\n')
>>> d.object
{'options': {'encoding': None, 'dst_prefix': None, 'src_prefix': None, 'diff_max_changes': None, 'diff_max_line_length': None, 'diff_too_big_message': None}, 'files': [{'deleted_lines': 1, 'added_lines': 1, 'is_git_diff': True, 'checksum_before': '0000001', 'checksum_after': '0ddf2ba', 'old_name': 'sample', 'language': '', 'new_name': 'sample', 'is_combined': False, 'blocks': [{'old_start_line': 1, 'old_start_line_2': None, 'new_start_line': 1, 'header': '@@ -1 +1 @@', 'lines': [{'source_line_no': 1, 'target_line_no': None, 'line_type': '-', 'content': '-test'}, {'source_line_no': None, 'target_line_no': 1, 'line_type': '+', 'content': '+test1r'}]}]}]}
>>> d.getitem('sample').added_lines
1
>>> d.getitem('sample').deleted_lines
1
```

## Installing Requests and Supported Versions

Udiff is available on PyPI:

```console
$ python -m pip install udiff
```

Udiff supports Python 2.7 & 3.5+.

## Usage

Parse from file:

```python
>>> from udiff import UdiffParser
>>> d = UdiffParser.from_filename(path_to_file)
```

Parse string:

```python
>>> from udiff import UdiffParser
>>> with codecs.open(path_to_file, 'r', encoding='utf-8') as diff:
>>>     d = UdiffParser.from_filename(diff.read())
```

Options:

- `src_prefix`: add a prefix to all source (before changes) filepaths, default is `''`. Should match the prefix used when
  [generating the diff](https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---src-prefixltprefixgt).
- `dst_prefix`: add a prefix to all destination (after changes) filepaths, default is `''`. Should match the prefix used
  when [generating the diff](https://git-scm.com/docs/git-diff#Documentation/git-diff.txt---dst-prefixltprefixgt)
- `diff_max_changes`: number of changed lines after which a file diff is deemed as too big and not displayed, default is
  `None`
- `diff_max_line_length`: number of characters in a diff line after which a file diff is deemed as too big and not
  displayed, default is `None`
- `diff_too_big_message`: message for file diff too big, default `Diff too big to be displayed`