import testlib
from testlib import ValueCheck


class TestQPointF(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "point",
            ValueCheck(
                summary="(x: 1.25, y: -2.5)",
                children=[
                    ValueCheck(name="xp", value="1.25"),
                    ValueCheck(name="yp", value="-2.5"),
                ],
            ),
        )
