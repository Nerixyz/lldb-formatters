import testlib
from testlib import ValueCheck
import re


class TestQFileInfo(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("null", ValueCheck(summary='u"" (null)'))
        self.assertVarPath(
            "someFile", ValueCheck(summary=re.compile(r'^u?"some/file.txt"$'))
        )
