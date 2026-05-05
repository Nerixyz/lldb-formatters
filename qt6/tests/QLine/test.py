import testlib
from testlib import ValueCheck


class TestQLine(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("line", ValueCheck(summary="(1, 2) -> (3, 4)"))
