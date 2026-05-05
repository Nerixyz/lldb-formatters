import testlib
from testlib import ValueCheck
import re


class TestQDir(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("null", ValueCheck(summary=re.compile(r'^u?"."$')))
        self.assertVarPath("someDir", ValueCheck(summary=re.compile(r'^u?"some/dir"$')))
