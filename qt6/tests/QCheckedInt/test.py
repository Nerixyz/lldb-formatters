import testlib
from testlib import ValueCheck


class TestQCheckedInt(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("zero", ValueCheck(value="0", children=[]))
        self.assertVarPath("two", ValueCheck(value="2", children=[]))
        self.assertVarPath("negative", ValueCheck(value="-2", children=[]))
        self.assertVarPath("llTwo", ValueCheck(value="2", children=[]))
