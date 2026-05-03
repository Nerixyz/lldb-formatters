import testlib
from testlib import ValueCheck
from lldb import SBValue


class TestQSet(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("empty", ValueCheck(summary="size=0", children=[]))
        self.assertVarPath(
            "one",
            ValueCheck(
                summary="size=1", children=[ValueCheck(name="[0]", summary="1")]
            ),
        )
        many: SBValue = self.frame().GetValueForVariablePath("many")
        self.assertEqual(many.GetNumChildren(), 10)
        got = set()
        for i in range(10):
            got.add(many.GetChildAtIndex(i).GetSummary())

        exp = set(str(i) for i in range(1, 11))
        self.assertEqual(exp, got)
