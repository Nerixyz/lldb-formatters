import testlib
from testlib import ValueCheck


class TestQRect(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "empty", ValueCheck(summary="(x: 0, y: 0, width: 0, height: 0)")
        )
        self.assertVarPath(
            "rect",
            ValueCheck(
                summary="(x: 10, y: 20, width: 30, height: 40)",
                children=[
                    ValueCheck(name="[x]", value="10"),
                    ValueCheck(name="[y]", value="20"),
                    ValueCheck(name="[width]", value="30"),
                    ValueCheck(name="[height]", value="40"),
                ],
            ),
        )
        self.assertVarPath(
            "invalid",
            ValueCheck(
                summary="(x: 10, y: 20, width: -9, height: -19)",
                children=[
                    ValueCheck(name="[x]", value="10"),
                    ValueCheck(name="[y]", value="20"),
                    ValueCheck(name="[width]", value="-9"),
                    ValueCheck(name="[height]", value="-19"),
                ],
            ),
        )
