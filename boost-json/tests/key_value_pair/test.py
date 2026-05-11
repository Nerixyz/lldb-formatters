import testlib
from testlib import ValueCheck


class TestBoostJsonValue(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "kv",
            ValueCheck(
                summary='("key", 1234)',
                children=[
                    ValueCheck(name="[Key]", summary='"key"'),
                    ValueCheck(name="[Value]", value="1234"),
                ],
            ),
        )
        self.assertVarPath(
            "kvStr",
            ValueCheck(
                summary='("key", "a string")',
                children=[
                    ValueCheck(name="[Key]", summary='"key"'),
                    ValueCheck(name="[Value]", summary='"a string"'),
                ],
            ),
        )
