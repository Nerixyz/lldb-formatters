import testlib
from testlib import ValueCheck


class TestQLineF(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("line", ValueCheck(summary="(1.25, 2) -> (3.5, 4.75)"))
