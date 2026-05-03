import testlib
from testlib import ValueCheck


class TestQRectF(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "empty", ValueCheck(summary="(x: 0, y: 0, width: 0, height: 0)")
        )
        self.assertVarPath(
            "rect",
            ValueCheck(
                summary="(x: 1.5, y: 2.5, width: 3.5, height: 4.5)",
                children=[
                    ValueCheck(name="[x]", value="1.5"),
                    ValueCheck(name="[y]", value="2.5"),
                    ValueCheck(name="[width]", value="3.5"),
                    ValueCheck(name="[height]", value="4.5"),
                ],
            ),
        )
        self.assertVarPath(
            "invalid",
            ValueCheck(
                summary="(x: 10.5, y: 20.5, width: -10.5, height: -20.5)",
                children=[
                    ValueCheck(name="[x]", value="10.5"),
                    ValueCheck(name="[y]", value="20.5"),
                    ValueCheck(name="[width]", value="-10.5"),
                    ValueCheck(name="[height]", value="-20.5"),
                ],
            ),
        )
