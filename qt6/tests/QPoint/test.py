import testlib
from testlib import ValueCheck


class TestQPoint(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "point",
            ValueCheck(
                summary="(x: 1, y: 2)",
                children=[
                    ValueCheck(name="xp", value="1"),
                    ValueCheck(name="yp", value="2"),
                ],
            ),
        )
