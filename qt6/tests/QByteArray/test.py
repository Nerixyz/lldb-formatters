import testlib
from testlib import ValueCheck


class TestQJsonObject(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("null", ValueCheck(summary='"" (null)', children=[]))
        self.assertVarPath("empty", ValueCheck(summary='""', children=[]))
        self.assertVarPath("oneChar", ValueCheck(summary='"a"'))
        self.assertVarPath("emojis", ValueCheck(summary='"🪐🪐🪐"'))
        self.assertVarPath("notNullTerminated", ValueCheck(summary='"ab"'))
