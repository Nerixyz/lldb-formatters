import testlib
from testlib import ValueCheck


class TestQPolygon(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "p",
            ValueCheck(
                summary="size=3",
                children=[
                    ValueCheck(name="[0]", summary="(x: 1, y: 2)"),
                    ValueCheck(name="[1]", summary="(x: 3, y: 4)"),
                    ValueCheck(name="[2]", summary="(x: 5, y: 6)"),
                ],
            ),
        )
