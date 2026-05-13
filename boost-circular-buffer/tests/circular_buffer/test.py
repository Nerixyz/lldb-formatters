import testlib
from testlib import ValueCheck


class TestBoostCircularBuffer(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("empty", ValueCheck(summary="size=0", children=[]))
        self.assertVarPath(
            "iBuffer10",
            ValueCheck(
                summary="size=10",
                children=[
                    ValueCheck(name="[0]", value="5"),
                    ValueCheck(name="[1]", value="6"),
                    ValueCheck(name="[2]", value="7"),
                    ValueCheck(name="[3]", value="8"),
                    ValueCheck(name="[4]", value="9"),
                    ValueCheck(name="[5]", value="10"),
                    ValueCheck(name="[6]", value="11"),
                    ValueCheck(name="[7]", value="12"),
                    ValueCheck(name="[8]", value="13"),
                    ValueCheck(name="[9]", value="14"),
                ],
            ),
        )
        self.assertVarPath(
            "iBuffer20",
            ValueCheck(
                summary="size=15",
                children=[
                    ValueCheck(name="[0]", value="0"),
                    ValueCheck(name="[1]", value="1"),
                    ValueCheck(name="[2]", value="2"),
                    ValueCheck(name="[3]", value="3"),
                    ValueCheck(name="[4]", value="4"),
                    ValueCheck(name="[5]", value="5"),
                    ValueCheck(name="[6]", value="6"),
                    ValueCheck(name="[7]", value="7"),
                    ValueCheck(name="[8]", value="8"),
                    ValueCheck(name="[9]", value="9"),
                    ValueCheck(name="[10]", value="10"),
                    ValueCheck(name="[11]", value="11"),
                    ValueCheck(name="[12]", value="12"),
                    ValueCheck(name="[13]", value="13"),
                    ValueCheck(name="[14]", value="14"),
                ],
            ),
        )
        self.assertVarPath("it", ValueCheck(value="5"))
        self.assertVarPath("cit", ValueCheck(value="5"))
        self.assertVarPath("end", ValueCheck(summary="end"))
        self.assertVarPath("last", ValueCheck(value="14"))
