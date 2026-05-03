import testlib
from testlib import ValueCheck


class TestQTime(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("null", ValueCheck(summary="(null)", children=[]))
        self.assertVarPath(
            "valid",
            ValueCheck(
                summary="02:03:04.005",
                children=[
                    ValueCheck(name="[hour]", value="2"),
                    ValueCheck(name="[minute]", value="3"),
                    ValueCheck(name="[second]", value="4"),
                    ValueCheck(name="[millisecond]", value="5"),
                ],
            ),
        )
        self.assertVarPath(
            "noMs",
            ValueCheck(
                summary="10:20:04",
                children=[
                    ValueCheck(name="[hour]", value="10"),
                    ValueCheck(name="[minute]", value="20"),
                    ValueCheck(name="[second]", value="4"),
                    ValueCheck(name="[millisecond]", value="0"),
                ],
            ),
        )
        self.assertVarPath(
            "noS",
            ValueCheck(
                summary="15:03",
                children=[
                    ValueCheck(name="[hour]", value="15"),
                    ValueCheck(name="[minute]", value="3"),
                    ValueCheck(name="[second]", value="0"),
                    ValueCheck(name="[millisecond]", value="0"),
                ],
            ),
        )
