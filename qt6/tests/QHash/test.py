import testlib
from lldb import SBValue
from testlib import ValueCheck


class TestQHash(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("empty", ValueCheck(summary="size=0", children=[]))
        self.assertVarPath(
            "one",
            ValueCheck(
                summary="size=1",
                children=[
                    ValueCheck(
                        name="[0]",
                        children=[
                            ValueCheck(name="key", value="1"),
                            ValueCheck(name="value", value="2"),
                        ],
                    )
                ],
            ),
        )
        self.assertVarPath("many", ValueCheck(summary="size=10"))
        many: SBValue = self.frame().GetValueForVariablePath("many")
        self.assertEqual(many.GetNumChildren(), 10)
        got = {}
        for i in range(10):
            c: SBValue = many.GetChildAtIndex(i)
            self.assertEqual(c.GetNumChildren(), 2)
            k = c.GetChildAtIndex(0)
            v = c.GetChildAtIndex(1)
            self.assertEqual(k.GetName(), "key")
            self.assertEqual(v.GetName(), "value")
            got[k.GetValue()] = v.GetValue()

        exp = {str(i): str(i * 2) for i in range(1, 11)}
        self.assertEqual(exp, got)
