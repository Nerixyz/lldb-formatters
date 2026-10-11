import testlib
from testlib import ValueCheck
import re


class TestQChar(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("zero", ValueCheck(value="U+0000", summary="U+0000 u'\\0'"))
        self.assertVarPath("a", ValueCheck(value="U+0061", summary="U+0061 u'a'"))
        self.assertVarPath(
            "umlaut",
            ValueCheck(value="U+00e4", summary=re.compile(r"^U\+00[eE]4 u'ä'$")),
        )
