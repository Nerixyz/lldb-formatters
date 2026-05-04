import testlib
from testlib import ValueCheck
import re


class TestQFile(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("null", ValueCheck(summary='u"" (null)'))
        self.assertVarPath(
            "someFile", ValueCheck(summary=re.compile(r'^u?"some/file.txt"$'))
        )
