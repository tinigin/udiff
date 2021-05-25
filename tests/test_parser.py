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


"""Tests for the unified diff parser process."""

from __future__ import unicode_literals

import codecs
import os.path
import unittest

from udiff.parser import UdiffParser
from udiff.parser import PY2
from udiff.errors import UdiffParseError

if not PY2:
    unicode = str


class TestUdiffParser(unittest.TestCase):
    """Tests for Udiff Parser."""

    def setUp(self):
        super(TestUdiffParser, self).setUp()

    def test_parse_unix_line_end(self):
        diff = \
            'diff --git a/sample b/sample\n' + \
            'index 0000001..0ddf2ba\n' + \
            '--- a/sample\n' + \
            '+++ b/sample\n' + \
            '@@ -1 +1 @@\n' + \
            '-test\n' + \
            '+test1r\n'

        parser = UdiffParser.from_string(diff)

        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('sample').added_lines, 1)
        self.assertEqual(parser.getitem('sample').deleted_lines, 1)

    def test_parse_windows_end(self):
        diff = \
            'diff --git a/sample b/sample\r\n' + \
            'index 0000001..0ddf2ba\r\n' + \
            '--- a/sample\r\n' + \
            '+++ b/sample\r\n' + \
            '@@ -1 +1 @@\r\n' + \
            '-test\r\n' + \
            '+test1r\r\n'

        parser = UdiffParser.from_string(diff)

        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('sample').added_lines, 1)
        self.assertEqual(parser.getitem('sample').deleted_lines, 1)

    def test_parse_end(self):
        diff = \
            'diff --git a/sample b/sample\r' + \
            'index 0000001..0ddf2ba\r' + \
            '--- a/sample\r' + \
            '+++ b/sample\r' + \
            '@@ -1 +1 @@\r' + \
            '-test\r' + \
            '+test1r\r'

        parser = UdiffParser.from_string(diff)

        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('sample').added_lines, 1)
        self.assertEqual(parser.getitem('sample').deleted_lines, 1)

    def test_parse_mixed_end(self):
        diff = \
            'diff --git a/sample b/sample\r' + \
            'index 0000001..0ddf2ba\r' + \
            '--- a/sample\r' + \
            '+++ b/sample\r\n' + \
            '@@ -1 +1 @@\r' + \
            '-test\r\n' + \
            '+test1r\r'

        parser = UdiffParser.from_string(diff)

        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('sample').added_lines, 1)
        self.assertEqual(parser.getitem('sample').deleted_lines, 1)

    def test_special_characters(self):
        diff = \
            'diff --git "a/bla with \ttab.scala" "b/bla with \ttab.scala"\n' + \
            'index 4c679d7..e9bd385 100644\n' + \
            '--- "a/bla with \ttab.scala"\n' + \
            '+++ "b/bla with \ttab.scala"\n' + \
            '@@ -1 +1,2 @@\n' + \
            '-cenas\n' + \
            '+cenas com ananas\n' + \
            '+bananas'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('tab.scala').added_lines, 2)
        self.assertEqual(parser.getitem('tab.scala').deleted_lines, 1)

    def test_diff_with_prefix(self):
        diff = \
            'diff --git "\tbla with \ttab.scala" "\tbla with \ttab.scala"\n' + \
            'index 4c679d7..e9bd385 100644\n' + \
            '--- "\tbla with \ttab.scala"\n' + \
            '+++ "\tbla with \ttab.scala"\n' + \
            '@@ -1 +1,2 @@\n' + \
            '-cenas\n' + \
            '+cenas com ananas\n' + \
            '+bananas'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('tab.scala').added_lines, 2)
        self.assertEqual(parser.getitem('tab.scala').deleted_lines, 1)

    def test_deleted_file(self):
        diff = \
            'diff --git a/src/var/strundefined.js b/src/var/strundefined.js\n' + \
            'deleted file mode 100644\n' + \
            'index 04e16b0..0000000\n' + \
            '--- a/src/var/strundefined.js\n' + \
            '+++ /dev/null\n' + \
            '@@ -1,3 +0,0 @@\n' + \
            '-define(() => {\n' + \
            '-  return typeof undefined;\n' + \
            '-});\n' \

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('strundefined.js').deleted_file_mode, '100644')

    def test_new_file(self):
        diff = \
            'diff --git a/test.js b/test.js\n' + \
            'new file mode 100644\n' + \
            'index 0000000..e1e22ec\n' + \
            '--- /dev/null\n' + \
            '+++ b/test.js\n' + \
            '@@ -0,0 +1,5 @@\n' + \
            "+var parser = require('./source/git-parser');\n" + \
            '+\n' + \
            '+var patchLineList = [ false, false, false, false ];\n' + \
            '+\n' + \
            '+console.log(parser.parsePatchDiffResult(text, patchLineList));\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('test.js').new_file_mode, '100644')
        self.assertEqual(parser.getitem('test.js').added_lines, 5)

    def test_nested_diff(self):
        diff = \
            'diff --git a/src/offset.js b/src/offset.js\n' + \
            'index cc6ffb4..fa51f18 100644\n' + \
            '--- a/src/offset.js\n' + \
            '+++ b/src/offset.js\n' + \
            '@@ -1,6 +1,5 @@\n' + \
            "+var parser = require('./source/git-parser');\n" + \
            '+\n' + \
            "+var text = 'diff --git a/components/app/app.html b/components/app/app.html\\nindex ecb7a95..027bd9b 100644\\n--- a/components/app/app.html\\n+++ b/components/app/app.html\\n@@ -52,0 +53,3 @@\\n+\\n+\\n+\\n@@ -56,0 +60,3 @@\\n+\\n+\\n+\\n'\n" + \
            '+var patchLineList = [ false, false, false, false ];\n' + \
            '+\n' + \
            '+console.log(parser.parsePatchDiffResult(text, patchLineList));\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('offset.js').added_lines, 6)

    def test_many_blocks(self):
        diff = \
            'diff --git a/src/attributes/classes.js b/src/attributes/classes.js\n' + \
            'index c617824..c8d1393 100644\n' + \
            '--- a/src/attributes/classes.js\n' + \
            '+++ b/src/attributes/classes.js\n' + \
            '@@ -1,10 +1,9 @@\n' + \
            ' define([\n' + \
            '   "../core",\n' + \
            '   "../var/rnotwhite",\n' + \
            '-  "../var/strundefined",\n' + \
            '   "../data/var/dataPriv",\n' + \
            '   "../core/init"\n' + \
            '-], function( jQuery, rnotwhite, strundefined, dataPriv ) {\n' + \
            '+], function( jQuery, rnotwhite, dataPriv ) {\n' + \
            ' \n' + \
            ' var rclass = /[\\t\\r\\n\\f]/g;\n' + \
            ' \n' + \
            '@@ -128,7 +127,7 @@ jQuery.fn.extend({\n' + \
            '         }\n' + \
            ' \n' + \
            '       // Toggle whole class name\n' + \
            '-      } else if ( type === strundefined || type === "boolean" ) {\n' + \
            '+      } else if ( value === undefined || type === "boolean" ) {\n' + \
            '         if ( this.className ) {\n' + \
            '           // store className if set\n' + \
            '           dataPriv.set( this, "__className__", this.className );\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('classes.js')[0].header, '@@ -1,10 +1,9 @@')
        self.assertEqual(len(parser.getitem('classes.js')[0]), 11)
        self.assertEqual(parser.getitem('classes.js')[1].header, '@@ -128,7 +127,7 @@ jQuery.fn.extend({')
        self.assertEqual(len(parser.getitem('classes.js')[1]), 8)

    def test_multiple_files(self):
        diff = \
            'diff --git a/src/core/init.js b/src/core/init.js\n' + \
            'index e49196a..50f310c 100644\n' + \
            '--- a/src/core/init.js\n' + \
            '+++ b/src/core/init.js\n' + \
            '@@ -101,7 +101,7 @@ var rootjQuery,\n' + \
            '     // HANDLE: $(function)\n' + \
            '     // Shortcut for document ready\n' + \
            '     } else if ( jQuery.isFunction( selector ) ) {\n' + \
            '-      return typeof rootjQuery.ready !== "undefined" ?\n' + \
            '+      return rootjQuery.ready !== undefined ?\n' + \
            '         rootjQuery.ready( selector ) :\n' + \
            '         // Execute immediately if ready is not present\n' + \
            '         selector( jQuery );\n' + \
            'diff --git a/src/event.js b/src/event.js\n' + \
            'index 7336f4d..6183f70 100644\n' + \
            '--- a/src/event.js\n' + \
            '+++ b/src/event.js\n' + \
            '@@ -1,6 +1,5 @@\n' + \
            ' define([\n' + \
            '   "./core",\n' + \
            '-  "./var/strundefined",\n' + \
            '   "./var/rnotwhite",\n' + \
            '   "./var/hasOwn",\n' + \
            '   "./var/slice",\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 2)
        self.assertEqual(parser.getitem('init.js').added_lines, 1)
        self.assertEqual(parser.getitem('init.js').deleted_lines, 1)
        self.assertEqual(parser.getitem('event.js').added_lines, 0)
        self.assertEqual(parser.getitem('event.js').deleted_lines, 1)

    def test_combined_diff(self):
        diff = \
            'diff --combined describe.c\n' + \
            'index fabadb8,cc95eb0..4866510\n' + \
            '--- a/describe.c\n' + \
            '+++ b/describe.c\n' + \
            '@@@ -98,20 -98,12 +98,20 @@@\n' + \
            '   return (a_date > b_date) ? -1 : (a_date == b_date) ? 0 : 1;\n' + \
            '  }\n' + \
            '  \n' + \
            '- static void describe(char *arg)\n' + \
            ' -static void describe(struct commit *cmit, int last_one)\n' + \
            '++static void describe(char *arg, int last_one)\n' + \
            '  {\n' + \
            ' + unsigned char sha1[20];\n' + \
            ' + struct commit *cmit;\n' + \
            '   struct commit_list *list;\n' + \
            '   static int initialized = 0;\n' + \
            '   struct commit_name *n;\n' + \
            '  \n' + \
            ' + if (get_sha1(arg, sha1) < 0)\n' + \
            ' +     usage(describe_usage);\n' + \
            ' + cmit = lookup_commit_reference(sha1);\n' + \
            ' + if (!cmit)\n' + \
            ' +     usage(describe_usage);\n' + \
            ' +\n' + \
            '   if (!initialized) {\n' + \
            '       initialized = 1;\n' + \
            '       for_each_ref(get_name);\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('describe.c').added_lines, 9)
        self.assertEqual(parser.getitem('describe.c').deleted_lines, 2)

    def test_copied_files(self):
        diff = \
            'diff --git a/index.js b/more-index.js\n' + \
            'dissimilarity index 5%\n' + \
            'copy from index.js\n' + \
            'copy to more-index.js\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('index.js').is_copy, True)

    def test_movied_files(self):
        diff = \
            'diff --git a/more-index.js b/other-index.js\n' + \
            'similarity index 86%\n' + \
            'rename from more-index.js\n' + \
            'rename to other-index.js\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('more-index.js').is_rename, True)

    def test_correct_line_numbers(self):
        diff = \
            'diff --git a/sample b/sample\n' + \
            'index 0000001..0ddf2ba\n' + \
            '--- a/sample\n' + \
            '+++ b/sample\n' + \
            '@@ -1 +1,2 @@\n' + \
            '-test\n' + \
            '+test1r\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(len(parser.getitem('sample')[0]), 2)

    def test_non_git_diff_with_timestamps(self):
        diff = \
            '--- a/sample.js  2016-10-25 11:37:14.000000000 +0200\n' + \
            '+++ b/sample.js  2016-10-25 11:37:14.000000000 +0200\n' + \
            '@@ -1 +1,2 @@\n' + \
            '-test\n' + \
            '+test1r\n' + \
            '+test2r\n' + \
            '--- a/sample2.js 2016-10-25 11:37:14.000000000 -0200\n' + \
            '+++ b/sample2.js  2016-10-25 11:37:14.000000000 -0200\n' + \
            '@@ -1 +1,2 @@\n' + \
            '-test\n' + \
            '+test1r\n' + \
            '+test2r\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 2)
        self.assertEqual(parser.getitem('sample.js').added_lines, 2)
        self.assertEqual(parser.getitem('sample.js').deleted_lines, 1)

    def test_unified_non_git_diff(self):
        diff = \
            '--- a/sample.js\n' + \
            '+++ b/sample.js\n' + \
            '@@ -1 +1,2 @@\n' + \
            '-test\n' + \
            '+test1r\n' + \
            '+test2r\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('sample.js').added_lines, 2)
        self.assertEqual(parser.getitem('sample.js').deleted_lines, 1)

    def test_diff_with_many_files_and_hunks(self):
        diff = \
            '--- sample.js\n' + \
            '+++ sample.js\n' + \
            '@@ -1 +1,2 @@\n' + \
            '-test\n' + \
            '@@ -10 +20,2 @@\n' + \
            '+test\n' + \
            '--- sample1.js\n' + \
            '+++ sample1.js\n' + \
            '@@ -1 +1,2 @@\n' + \
            '+test1\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 2)
        self.assertEqual(parser.getitem('sample.js').deleted_lines, 1)
        self.assertEqual(parser.getitem('sample1.js').added_lines, 1)

    def test_diff_with_custom_context(self):
        diff = \
            '--- sample.js\n' + \
            '+++ sample.js\n' + \
            '@@ -1,8 +1,8 @@\n' + \
            ' test\n' + \
            ' \n' + \
            '-- 1\n' + \
            '--- 1\n' + \
            '---- 1\n' + \
            ' \n' + \
            '++ 2\n' + \
            '+++ 2\n' + \
            '++++ 2\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('sample.js').deleted_lines, 3)
        self.assertEqual(parser.getitem('sample.js').added_lines, 3)

    def test_diff_without_proper_hunk_headers(self):
        diff = \
            '--- sample.js\n' + \
            '+++ sample.js\n' + \
            '@@ @@\n' + \
            ' test\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(len(parser.getitem('sample.js')[0]), 1)

    def tets_binary_diff(self):
        diff = \
            'diff --git a/last-changes-config.png b/last-changes-config.png\n' + \
            'index 322248b..56fc1f2 100644\n' + \
            '--- a/last-changes-config.png\n' + \
            '+++ b/last-changes-config.png\n' + \
            'Binary files differ\n'

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('last-changes-config.png').is_binary, True)

    def test_diff_with_find_renames(self):
        diff = \
            'diff --git a/src/test-bar.js b/src/test-baz.js\n' + \
            'similarity index 98%\n' + \
            'rename from src/test-bar.js\n' + \
            'rename to src/test-baz.js\n' + \
            'index e01513b..f14a870 100644\n' + \
            '--- a/src/test-bar.js\n' + \
            '+++ b/src/test-baz.js\n' + \
            '@@ -1,4 +1,32 @@\n' + \
            ' function foo() {\n' + \
            '-var bar = "Whoops!";\n' + \
            '+var baz = "Whoops!";\n' + \
            ' }\n' + \
            ' '

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 1)
        self.assertEqual(parser.getitem('src/test-bar.js').is_rename, True)
        self.assertEqual(parser.getitem('src/test-bar.js').unchanged_percentage, 98)
        self.assertEqual(parser.getitem('src/test-bar.js').added_lines, 1)
        self.assertEqual(parser.getitem('src/test-bar.js').deleted_lines, 1)

    def test_diff_with_prefix_2(self):
        diff = \
            'diff --git "\tTest.scala" "\tScalaTest.scala"\n' + \
            'similarity index 88%\n' + \
            'rename from Test.scala\n' + \
            'rename to ScalaTest.scala\n' + \
            'index 7d1f9bf..8b13271 100644\n' + \
            '--- "\tTest.scala"\n' + \
            '+++ "\tScalaTest.scala"\n' + \
            '@@ -1,6 +1,8 @@\n' + \
            ' class Test {\n' + \
            ' \n' + \
            '   def method1 = ???\n' + \
            '+\n' + \
            '+  def method2 = ???\n' + \
            ' \n' + \
            '   def myMethod = ???\n' + \
            ' \n' + \
            '@@ -10,7 +12,6 @@ class Test {\n' + \
            ' \n' + \
            '   def + = ???\n' + \
            ' \n' + \
            '-  def |> = ???\n' + \
            ' \n' + \
            ' }\n' + \
            ' \n' + \
            'diff --git "\ttardis.png" "\ttardis.png"\n' + \
            'new file mode 100644\n' + \
            'index 0000000..d503a29\n' + \
            'Binary files /dev/null and "\ttardis.png" differ\n' + \
            'diff --git a/src/test-bar.js b/src/test-baz.js\n' + \
            'similarity index 98%\n' + \
            'rename from src/test-bar.js\n' + \
            'rename to src/test-baz.js\n' + \
            'index e01513b..f14a870 100644\n' + \
            '--- a/src/test-bar.js\n' + \
            '+++ b/src/test-baz.js\n' + \
            '@@ -1,4 +1,32 @@\n' + \
            ' function foo() {\n' + \
            '-var bar = "Whoops!";\n' + \
            '+var baz = "Whoops!";\n' + \
            ' }\n' + \
            ' '

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 3)

        self.assertEqual(parser.getitem('Test.scala').is_rename, True)
        self.assertEqual(parser.getitem('Test.scala').added_lines, 2)
        self.assertEqual(parser.getitem('Test.scala').deleted_lines, 1)

        self.assertEqual(parser.getitem('src/test-bar.js').is_rename, True)
        self.assertEqual(parser.getitem('src/test-bar.js').unchanged_percentage, 98)
        self.assertEqual(parser.getitem('src/test-bar.js').added_lines, 1)
        self.assertEqual(parser.getitem('src/test-bar.js').deleted_lines, 1)

    def test_binary_diff_with_content(self):
        diff = \
            'diff --git a/favicon.png b/favicon.png\n' + \
            'deleted file mode 100644\n' + \
            'index 2a9d516a5647205d7be510dd0dff93a3663eff6f..0000000000000000000000000000000000000000\n' + \
            'GIT binary patch\n' + \
            'literal 0\n' + \
            'HcmV?d00001\n' + \
            '\n' + \
            'literal 471\n' + \
            'zcmeAS@N?(olHy`uVBq!ia0vp^0wB!61|;P_|4#%`EX7WqAsj$Z!;#Vf<Z~8yL>4nJ\n' + \
            'za0`Jj<E6WGe}IBwC9V-A&PAz-C7Jno3L%-fsSJk3`UaNzMkcGzh!g=;$beJ?=ckpF\n' + \
            'zCl;kLIHu$$r7E~(7NwTw7iAYKI0u`(*t4mJfq_xq)5S5wqIc=!hrWj$cv|<b{x!c(\n' + \
            'z;3r#y;31Y&=1q>qPVOAS4ANVKzqmCp=Cty@U^(7zk!jHsvT~YI{F^=Ex6g|gox78w\n' + \
            'z+Sn2Du3GS9U7qU`1*NYYlJi3u-!<?H-eky}wyIIL;8VU@wCDrb0``&v(jQ*DWSR4K\n' + \
            'zPq(3;isEyho{emNa=%%!jDPE`l3u;5d=q=<+v8kO-=C`*G#t-*AiE-D>-_B#8k9H0\n' + \
            'zGl{FnZs<2$wz5^=Q2h-1XI^s{LQL1#T4epqNPC%Orl(tD_@!*EY++~^Lt2<2&!&%=\n' + \
            'z`m>(TYj6uS7jDdt=eH>iOyQg(QMR<-Fw8)Dk^ZG)XQTuzEgl{`GpS?Cfq9818R9~=\n' + \
            'z{&h9@9n8F^?|qusoPy{k#%tVHzu7H$t26CR`BJZk*Ixf&u36WuS=?6m2^ho-p00i_\n' + \
            'I>zopr0Nz-&lmGw#\n' + \
            'diff --git a/src/test-bar.js b/src/test-baz.js\n' + \
            'similarity index 98%\n' + \
            'rename from src/test-bar.js\n' + \
            'rename to src/test-baz.js\n' + \
            'index e01513b..f14a870 100644\n' + \
            '--- a/src/test-bar.js\n' + \
            '+++ b/src/test-baz.js\n' + \
            '@@ -1,4 +1,32 @@\n' + \
            ' function foo() {\n' + \
            '-var bar = "Whoops!";\n' + \
            '+var baz = "Whoops!";\n' + \
            ' }\n' + \
            ' '

        parser = UdiffParser.from_string(diff)

        self.assertEqual(len(parser), 2)
        self.assertEqual(parser.removed, 1)
        self.assertEqual(parser.getitem('favicon.png').is_deleted, True)
        self.assertEqual(parser.modified, 1)
        self.assertEqual(parser.getitem('test-bar.js').is_rename, True)
        self.assertEqual(parser.getitem('test-bar.js').unchanged_percentage, 98)

    def test_diff_max_changes(self):
        diff = \
            'diff --git a/src/core/init.js b/src/core/init.js\n' + \
            'index e49196a..50f310c 100644\n' + \
            '--- a/src/core/init.js\n' + \
            '+++ b/src/core/init.js\n' + \
            '@@ -101,7 +101,7 @@ var rootjQuery,\n' + \
            '     // HANDLE: $(function)\n' + \
            '     // Shortcut for document ready\n' + \
            '     } else if ( jQuery.isFunction( selector ) ) {\n' + \
            '-      return typeof rootjQuery.ready !== "undefined" ?\n' + \
            '+      return rootjQuery.ready !== undefined ?\n' + \
            '         rootjQuery.ready( selector ) :\n' + \
            '         // Execute immediately if ready is not present\n' + \
            '         selector( jQuery );\n' + \
            'diff --git a/src/event.js b/src/event.js\n' + \
            'index 7336f4d..6183f70 100644\n' + \
            '--- a/src/event.js\n' + \
            '+++ b/src/event.js\n' + \
            '@@ -1,6 +1,5 @@\n' + \
            ' define([\n' + \
            '   "./core",\n' + \
            '-  "./var/strundefined",\n' + \
            '   "./var/rnotwhite",\n' + \
            '   "./var/hasOwn",\n' + \
            '   "./var/slice",\n'

        parser = UdiffParser.from_string(diff, options={'diff_max_changes': 1})

        self.assertEqual(len(parser), 2)
        self.assertEqual(parser.modified, 2)
        self.assertEqual(parser.getitem('src/core/init.js')[0].header, 'Diff too big to be displayed')

    def test_diff_max_changes_with_text(self):
        diff = \
            'diff --git a/src/core/init.js b/src/core/init.js\n' + \
            'index e49196a..50f310c 100644\n' + \
            '--- a/src/core/init.js\n' + \
            '+++ b/src/core/init.js\n' + \
            '@@ -101,7 +101,7 @@ var rootjQuery,\n' + \
            '     // HANDLE: $(function)\n' + \
            '     // Shortcut for document ready\n' + \
            '     } else if ( jQuery.isFunction( selector ) ) {\n' + \
            '-      return typeof rootjQuery.ready !== "undefined" ?\n' + \
            '+      return rootjQuery.ready !== undefined ?\n' + \
            '         rootjQuery.ready( selector ) :\n' + \
            '         // Execute immediately if ready is not present\n' + \
            '         selector( jQuery );\n' + \
            'diff --git a/src/event.js b/src/event.js\n' + \
            'index 7336f4d..6183f70 100644\n' + \
            '--- a/src/event.js\n' + \
            '+++ b/src/event.js\n' + \
            '@@ -1,6 +1,5 @@\n' + \
            ' define([\n' + \
            '   "./core",\n' + \
            '-  "./var/strundefined",\n' + \
            '   "./var/rnotwhite",\n' + \
            '   "./var/hasOwn",\n' + \
            '   "./var/slice",\n'

        parser = UdiffParser.from_string(diff, options={'diff_max_changes': 1, 'diff_too_big_message': 'Diff is too big'})

        self.assertEqual(len(parser), 2)
        self.assertEqual(parser.modified, 2)
        self.assertEqual(parser.getitem('src/core/init.js')[0].header, 'Diff is too big')

    def test_diff_max_line_length(self):
        diff = \
            'diff --git a/src/core/init.js b/src/core/init.js\n' + \
            'index e49196a..50f310c 100644\n' + \
            '--- a/src/core/init.js\n' + \
            '+++ b/src/core/init.js\n' + \
            '@@ -101,7 +101,7 @@ var rootjQuery,\n' + \
            '     // HANDLE: $(function)\n' + \
            '     // Shortcut for document ready\n' + \
            '     } else if ( jQuery.isFunction( selector ) ) {\n' + \
            '-      return typeof rootjQuery.ready !== "undefined" ?\n' + \
            '+      return rootjQuery.ready !== undefined ?\n' + \
            '         rootjQuery.ready( selector ) :\n' + \
            '         // Execute immediately if ready is not present\n' + \
            '         selector( jQuery );\n' + \
            'diff --git a/src/event.js b/src/event.js\n' + \
            'index 7336f4d..6183f70 100644\n' + \
            '--- a/src/event.js\n' + \
            '+++ b/src/event.js\n' + \
            '@@ -1,6 +1,5 @@\n' + \
            ' define([\n' + \
            '   "./core",\n' + \
            '-  "./var/strundefined",\n' + \
            '   "./var/rnotwhite",\n' + \
            '   "./var/hasOwn",\n' + \
            '   "./var/slice",\n'

        parser = UdiffParser.from_string(diff, options={'diff_max_line_length': 50, 'diff_too_big_message': 'Diff is too big'})

        self.assertEqual(len(parser), 2)
        self.assertEqual(parser.modified, 2)
        self.assertEqual(parser.getitem('src/core/init.js')[0].header, 'Diff is too big')

    def test_svn_diff(self):
        diff = """------------------------------------------------------------------------
r10005465 | some_user | 2016-11-17 08:39:32 +0300 (Thu, 17 Nov 2016) | 1 line

FCP In Action - Copy CR FB Reflection

Index: audi/index.html
===================================================================
--- audi/index.html	(revision 10005464)
+++ audi/index.html	(revision 10005465)
@@ -34,7 +34,7 @@
 			<div class="section-content">
 				<figure class="hero-image">
 					<h1 class="hero-headline">Audiを編集する</h1>
-					<h2 class="hero-subhead">複雑なコマーシャルが<wbr /><span class="nowrap">形になるまで。</span></h2>
+					<h2 class="hero-subhead">複雑なコマーシャルが<wbr /><span class="nowrap">形になるまで</span></h2>
 				</figure>
 			</div>
 		</header>
@@ -43,16 +43,16 @@
 			<div class="section-content">
 				<div class="row">
 					<div class="large-7 large-offset-1 medium-8 medium-offset-0 small-12 column">
-						<p>わずか数か月の間に、Trim Editing社には数多くの変化がありました。まず、この小さな編集スタジオはイーストロンドンにある完全に新しい2フロアのスペースに移転しました。編集室の数も2倍の10室になり、増え続ける編集スタッフのためにより良い環境を用意できるようになりました。時を同じくして、Trim社のプロジェクトの領域も大きく広がり、今ではBMW、Nike、Hennesyといった大手ブランドのためのパワフルな新作CMも手がけるようになりました。</p>
+						<p>わずか数か月の間に、Trim Editing社には数多くの変化がありました。まず、この小さな編集スタジオはイーストロンドンにある完全に新しい2フロアのスペースに移転しました。編集室の数も2倍の10室になり、増え続ける編集スタッフのためにより良い環境を用意できるようになりました。時を同じくして、Trim社のプロジェクトの領域も大きく広がり、今ではBMW、Nike、Hennessyといった大手ブランドのためのパワフルな新作CMも手がけるようになりました。</p>

-						<p>エディターのThomas Grove Carter氏にとって最も大きな変化は、Final Cut Pro 10.3の登場です。何年も前からTrim社でFinal Cut Pro Xを使ってきたCarter氏は、このお気に入りの編集ツールの最新バージョンを使うことを心待ちにしていました。そのテストドライブを行ったCMが「Everyday Extremes」。複雑なサウンドデザインと流れるような映像のトランジションが求められた、難易度の高いAudiのプロジェクトです。新しいFinal Cut Proは、Carter氏の高い期待をはるかに上回りました。これまでにない速さで、アイデアを新しい編集に反映できるようになったのです。</p>
+						<p>エディターのThomas Grove Carter氏にとって最も大きな変化は、Final Cut Pro 10.3の登場です。何年も前にFinal Cut Pro XをTrim社に導入したCarter氏は、このお気に入りの編集ツールの最新バージョンを使うことを心待ちにしていました。そのテストドライブを行ったCMが「Everyday Extremes」。複雑なサウンドデザインと流れるような映像のトランジションが求められた、難易度の高いAudiのプロジェクトです。新しいFinal Cut Proは、Carter氏の高い期待をはるかに上回りました。これまでにない速さで、アイデアを新しい編集に反映できるようになったのです。</p>
 					</div>
 					<div class="large-2 large-offset-1 medium-2 small-offset-0 small-6 featured column">
 						<div class="keyline-top"></div>
 						<figure class="audi-side-poster featured-thumbnail"></figure>
 						<a href="https://www.youtube.com/watch?v=cqwbg32ntUc" class="icon icon-external caption-copy cta" target="_blank">ビデオを見る</a>
 						<h5 class="caption-headline">Audi: Everyday Extremes</h5>
-						<p class="caption-copy">Audi Quattroが障害物コースのようなデパートの店内を走る映像全体に、複雑なサウンドスケープを重ねた60秒のCMです。</p>
+						<p class="caption-copy">quattro搭載のAudiが障害物コースのようなデパートの店内を走る映像全体に、複雑なサウンドスケープを重ねた60秒のCMです。</p>
 					</div>
 				</div>
 			</div>
@@ -61,14 +61,14 @@
 		<section class="section section-streamlined-look" data-analytics-section-engagement="name:streamlined-look">
 			<div class="section-content">
 				<figure class="image-streamlined-look image-hardware">
-					<figcaption class="caption-copy">Thomas Grove Carter氏はFinal Cut Pro 10.3を使い、「Everyday Extremes」の複雑なサウンドトラックを作りました。</figcaption>
+					<figcaption class="caption-copy">Thomas Grove Carter氏はFinal Cut Pro 10.3を使い、「Everyday Extremes」の複雑なサウンドトラックを作り上げました。</figcaption>
 				</figure>
 				<div class="row">
 					<div class="large-7 large-offset-1 medium-8 medium-offset-0 small-12 column">
 						<h2 class="section-headline large-9 small-12">目の覚めるような<wbr /><span class="nowrap">洗練されたデザイン。</span></h2>
-						<p>Final Cut Pro 10.3を使う楽しさは、最初に起動した瞬間から始まったとCarter氏は言います。「とてもすっきりしたフラットな見た目で、混み合った感じがありません。ビューアを見ている時に、視界の周囲がごちゃごちゃしないのです。ボタンも作り直されて、理にかなった配置になったと思います」</p>
+						<p>Final Cut Pro 10.3を使う楽しさは、最初に起動した瞬間から始まるとCarter氏は言います。「とてもすっきりしたフラットな見た目で、混み合った感じがありません。ビューアを見ている時に、視界の周囲がごちゃごちゃしないのです。ボタンも作り直されて、理にかなった配置になったと思います」</p>

-						<p>ワークフローに合わせてレイアウトを瞬時に変えられる、インターフェイスのカスタマイズ機能も気に入っているとCarter氏は語ります。「最初の段階で映像を整理する時にはタイムラインをまったく使わないので、それを完全に隠しておけるのは理想的です」。タイムラインを非表示にすることで、Carter氏はフルスクリーン表示でクリップを見たりタグを選べるようになりました。「おかげで目の前の作業に集中できます」</p>
+						<p>ワークフローに合わせてレイアウトを瞬時に変えられる、インターフェイスのカスタマイズ機能も気に入っているとCarter氏は語ります。「最初の段階で映像を整理する時にはタイムラインをまったく使わないので、それを完全に隠しておけるのは理想的です」。タイムラインを非表示にすることで、Carter氏はフルスクリーン表示でクリップを見たり、選択したクリップにタグを付けることができるようになりました。「おかげで目の前の作業に集中できます」</p>

 						<p>カスタムウインドウレイアウトなら、ワンクリックで好きなワークスペースに戻ることもできます。「カスタムレイアウトはとても便利です。レイアウトを保存すると、調節した細かなパラメータもすべて保存されます。ウインドウの位置だけでなく、慎重に微調整した設定も保存されるので本当に使いやすいです」</p>
 					</div>
@@ -86,14 +86,14 @@
 				</figure>
 				<div class="row">
 					<div class="large-7 large-offset-1 medium-8 medium-offset-0 small-12 column">
-						<h2 class="section-headline large-9 small-12">時間を節約できる、<wbr /><span class="nowrap">タイムラインの作業。</span></h2>
-						<p>「Everyday Extremes」では、Audi A4が薄暗いデパートの店内で滑らかなフロアを抜け、急なカーブを曲がり、俊敏に走り回ります。映像だけでも印象的ですが、きめ細かなサウンドデザインが加わると一段と引き込まれます。この複雑なサウンドスケープを組み立てるために、Carter氏は店内をリアルに再現するサウンドのほかに、車のタイヤがきしむ音やエンジンが回転する音をシミュレートできる新しいエフェクトを幅広く加えました。</p>
+						<h2 class="section-headline large-9 small-12">時間を節約できる、<wbr /><span class="nowrap">タイムラインでの作業。</span></h2>
+						<p>「Everyday Extremes」では、Audi A4が薄暗いデパートの店内で滑らかなフロアを抜け、急なカーブを曲がり、俊敏に走り回ります。映像だけでも印象的ですが、きめ細かなサウンドデザインが加わると一段と引き込まれます。この複雑なサウンドスケープを組み立てるために、Carter氏は店内をリアルに再現するサウンドのほかに、車のタイヤがきしむ音やエンジンが急回転する音をシミュレートできる新しいエフェクトを幅広く加えました。</p>

 						<p>Final Cut Pro 10.3の新しいタイムライン機能により、Carter氏は一段とすばやく簡単に作業ができるようになりました。オーディオクリップがロール（オーディオの種類）ごとに自動的にグループ分けされて色分けされるので、異なるカテゴリーのサウンドを一目で識別できるのです。タイヤの音、エンジンの響き、クライアントのAudiから提供されたそのほかのエフェクトに対して、Carter氏はそれぞれ別々のロールを作りました。「これらのクリップの構成も、一つひとつのクリップの意味も、瞬時にわかります」とCarter氏は言います。「タイムラインを見る方法として実に優れています」</p>

-						<p>タイムラインインデックス内の新しいオプションを使えば、必要なオーディオロールだけを必要な場所で必要な時に見ることができます。「ロールの順番を入れ替えられるのが気に入っています」とCarter氏は言います。これはインデックスの中でロールをドラッグするだけで、タイムラインのレイアウトを即座に組み立て直せる機能です。さらにフォーカスボタンをクリックすると、タイムライン上でほかのロールをすべて最小化し、例えばタイヤの音のような特定のオーディオロールに集中することができます。全体的なサウンドデザインの作業をする時は「オーディオレーンを表示」で瞬時にすべてのオーディオクリップをロールごとに整理し、それぞれを別々のレーンに配置することで、より複雑なプロジェクトを見やすいビジュアルでチェックできます。</p>
+						<p>タイムラインインデックス内の新しいオプションを使えば、必要なオーディオロールだけを必要な場所で必要な時に見ることができます。「ロールの順番を入れ替えられるのが気に入っています」とCarter氏は言います。これはインデックスの中でロールをドラッグするだけで、タイムラインのレイアウトを即座に組み立て直せる機能です。さらにフォーカスボタンをクリックすると、タイムライン上でほかのロールをすべて折りたたんで、例えばタイヤの音のような特定のオーディオロールに集中することができます。全体的なサウンドデザインの作業をする時は「オーディオレーンを表示」で瞬時にすべてのオーディオクリップをロールごとに整理し、それぞれを別々のレーンに配置することで、より複雑なプロジェクトを見やすいビジュアルでチェックできます。</p>

-						<p>Final Cut Pro 10.3は、オーディオの読み込みプロセスも効率化します。このアプリケーションはロケ現場のサウンドレコーダーで作ったiXMLメタデータを読み込み、その情報を使ってそれぞれのクリップに自動的にロールを割り当てます。そのためすべてのオーディオの読み込みでも、色分けでも、ロールごとのグループ化でも、Carter氏と彼のアシスタントエディターたちは準備にかける時間を大幅に節約できました。そして、その分の時間を店内の障害物コースを俊敏に走る車を描写する複雑なサウンドを作るために使うことができたのです。</p>
+						<p>Final Cut Pro 10.3は、オーディオの読み込みプロセスも効率化します。このアプリケーションはロケ現場のサウンドレコーダーで作ったiXMLメタデータを読み込み、その情報を使ってそれぞれのクリップに自動的にロールを割り当てます。すべてのオーディオが読み込まれ、色分けされ、ロールごとにグループ化されるので、Carter氏と彼のアシスタントエディターたちは準備にかける時間を大幅に節約できました。そしてその分の時間を、店内の障害物コースを俊敏に走る車を描写する、複雑なサウンドを作るために使うことができたのです。</p>
 					</div>
 					<blockquote class="large-3 large-offset-1 medium-3 small-offset-0 small-12 column side-quote-container">
 						<p class="narrowquote-copy">「新しいFinal Cut Proがクリップを整理して色分けしてくれるので、単純な手作業から完全に解放されました」</p>
@@ -112,9 +112,9 @@
 						<h2 class="section-headline large-10 small-12">編集の手間を減らせる、<wbr /><span class="nowrap">パワフルな機能。</span></h2>
 						<p>Final Cut Pro 10.3では、大きな進化のほかにも多くの編集機能が改良され、Carter氏のプロジェクトの高速化をサポートしています。新しいアイデアを試したり編集を磨き上げたい時は、隣接した接続クリップ上でロールトリムができるようになり、便利な「トリム開始」と「トリム終了」コマンドを複数のクリップで一度に使えるようになりました。Carter氏は編集中に色補正とエフェクトを頻繁に適用しますが、「パラメータを削除」の新しいオプションにより、不要な要素を選んで削除する作業をシンプルなインターフェイス上ですばやくできるようにもなりました。</p>

-						<p>Trim社の活気あふれる新しい仕事場では、一つの編集室のiMacから別の編集室のiMacにプロジェクトを移動させることがよくあります。これまではプロジェクトにMotionのテンプレートや他社製のエフェクトが含まれている場合、それらを一つずつ新しいMacに移さなくてはいけませんでした。Final Cut Pro 10.3を使えば、タイトル、テンプレート、エフェクトを同じライブラリにメディアとしてまとめておけるので、Carter氏はすべてをプロジェクトと一緒に移動させることができます。</p>
+						<p>Trim社の活気あふれる新しい仕事場では、一つの編集室のiMacから別の編集室のiMacにプロジェクトを移動させることがよくあります。これまではプロジェクトにMotionのテンプレートや他社製のエフェクトが含まれている場合、それらを一つずつ新しいMacに移さなくてはなりませんでした。Final Cut Pro 10.3を使えば、タイトル、テンプレート、エフェクトをメディアと同じライブラリにまとめておけるので、Carter氏はすべてをプロジェクトと一緒に移動させることができます。</p>

-						<p>Carter氏のお気に入りの新機能の一つが、ブラウザ内の連続再生オプションです。このオプションを使うと、タイムラインの中で手の込んだラフ編集を作ることなく、自分のセレクトをすべてチェックすることができます。「今まではセレクトを見るために気に入った部分をすべて集め、それを新しく作ったタイムラインに入れて再生しなくてはいけませんでした。そのためいくつか余計な手順が必要になり、追加したマーカーはすべてタイムライン上に残されていました。でも今ではブラウザを離れずに『再生』を押すだけです。ワンクリックで自分のセレクトが見られるのです。これも大きな前進です。私にとっては本当に重要な進化です」</p>
+						<p>Carter氏のお気に入りの新機能の一つが、ブラウザ内の連続再生オプションです。このオプションを使うと、タイムラインの中で扱いづらいラフ編集を作ることなく、自分のセレクトをすべてチェックすることができます。「今まではセレクトを見るために気に入った部分をすべて集め、それを新しく作ったタイムラインに入れて再生しなくてはなりませんでした。そのためいくつか余計な手順が必要になり、追加したマーカーはすべてタイムライン上に残されていました。でも今ではブラウザを離れずに再生ボタンを押すだけです。ワンクリックで自分のセレクトが見られるのです。これも大きな前進です。私にとっては本当に重要な進化です」</p>

 						<p>完成したCM「Everyday Extremes」は高い評価を得ました。Trim社の仲間たちにもFinal Cut Pro 10.3の利点を体験してもらいたいとCarter氏は思っています。「新しいインターフェイスは見た目が良くなっただけではありません。ほかのどこにもない機能を使えるので、クリックに費やす時間が減り、編集そのものに時間をかけられます」とCarter氏は言います。「そのためクリエイティブな部分に集中できるようになりました。それは私が最も喜びを感じるところです。クリエイティブな仕事こそ、私がエディターになった理由なのですから」</p>
 					</div>
@@ -122,7 +122,7 @@
 						<div class="keyline-top"></div>
 						<figure class="image-video-powerful-features featured-thumbnail"></figure>
 						<h5 class="caption-headline">Trim Editing</h5>
-						<p class="caption-copy">数々の賞を獲得しているポストプロダクションのスタジオ。Nike、Audi、Guinnessといったクライアントのためにハイエンドなコマーシャルを編集しています。</p>
+						<p class="caption-copy">数々の賞を獲得しているポストプロダクションスタジオ。Nike、Audi、Guinnessといったクライアントのためにハイエンドなコマーシャルを編集しています。</p>
 						<a href="/jp/final-cut-pro/in-action/trim-editing/" class="caption-copy cta" data-analytics-region="learn more">Trim Editingについて<wbr /><span class="nowrap more">さらに詳しく</span></a>
 					</blockquote>
 				</div>
Index: index.html
===================================================================
--- qwerty/index.html	(revision 10005464)
+++ qwerty/index.html	(revision 10005465)
@@ -39,7 +39,7 @@
 									<figure class="image-hero-editing-audi">
 										<figcaption class="hero-caption top-caption">
 											<h1 class="hero-headline">Audiを編集する</h1>
-											<h2 class="hero-subhead">複雑なコマーシャルが形になるまで。</h2>
+											<h2 class="hero-subhead">複雑なコマーシャルが形になるまで</h2>
 										</figcaption>
 									</figure>
 								</a>
@@ -91,7 +91,7 @@
 								<figure class="image-article-editing-audi"></figure>
 							</a>
 							<h3 class="smallblock-headline">Audiを編集する</h3>
-							<h4 class="smallblock-copy">複雑なコマーシャルが形になるまで。</h4>
+							<h4 class="smallblock-copy">複雑なコマーシャルが形になるまで</h4>
 							<p class="thumbnail-description">エディターのThomas Grove Carter氏は<wbr /><span class="nowrap">Final Cut Pro 10.3</span>を使い、Audiの巧みな<wbr /><span class="nowrap">コマー</span>シャル「Everyday Extremes」を編集しました。<a href="/jp/final-cut-pro/in-action/audi/" class="more" data-analytics-title="editing audi">さらに詳しく</a>
 							</p>
 						</div>

------------------------------------------------------------------------"""

        parser = UdiffParser.from_string(diff)
        self.assertEqual(len(parser), 2)

        self.assertEqual(parser.getitem('qwerty/index.html').added_lines, 2)
        self.assertEqual(parser.getitem('qwerty/index.html').deleted_lines, 2)

        self.assertEqual(parser.getitem('audi/index.html').added_lines, 14)
        self.assertEqual(parser.getitem('audi/index.html').deleted_lines, 14)

if __name__ == '__main__':
    unittest.main()
