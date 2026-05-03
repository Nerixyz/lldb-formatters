import testlib
from testlib import ValueCheck
import re


class TestQJsonObject(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("defaultC", ValueCheck(summary='u""', children=[]))
        self.assertVarPath("empty", ValueCheck(summary='u""', children=[]))
        self.assertVarPath("oneChar", ValueCheck(summary=re.compile(r'^u?"a"$')))
        self.assertVarPath("emojis", ValueCheck(summary=re.compile(r'u?"🪐🪐🪐"')))
        self.assertVarPath(
            "notNullTerminated",
            ValueCheck(summary=re.compile(r'^u?"ab"$')),
        )
