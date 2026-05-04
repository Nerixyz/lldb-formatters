import testlib
from testlib import ValueCheck


class TestQBasicAtomicInteger(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("qBai", ValueCheck(value="42"))
        self.assertVarPath("qBall", ValueCheck(value="-1234567890123"))
