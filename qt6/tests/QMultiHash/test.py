import testlib
from testlib import ValueCheck
from lldb import SBValue


class TestQMultiHash(testlib.TestCase):
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
                        summary="1",
                        children=[
                            ValueCheck(name="key", value="1"),
                            ValueCheck(
                                name="value",
                                summary="size=3",
                                children=[
                                    ValueCheck(name="[0]", value="4"),
                                    ValueCheck(name="[1]", value="3"),
                                    ValueCheck(name="[2]", value="2"),
                                ],
                            ),
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
            self.assertEqual(v.GetNumChildren(), 2)
            got[k.GetValue()] = (
                v.GetChildAtIndex(0).GetValue(),
                v.GetChildAtIndex(1).GetValue(),
            )

        exp = {str(i): (str(-i), str(i)) for i in range(1, 11)}
        self.assertEqual(exp, got)
