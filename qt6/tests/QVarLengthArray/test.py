import testlib
from testlib import ValueCheck


class TestQVarLengthArray(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("empty", ValueCheck(summary="size=0", children=[]))
        self.assertVarPath(
            "values",
            ValueCheck(
                summary="size=3",
                children=[
                    ValueCheck(name="[0]", value="1"),
                    ValueCheck(name="[1]", value="2"),
                    ValueCheck(name="[2]", value="3"),
                ],
            ),
        )
        self.assertVarPath(
            "heap",
            ValueCheck(
                summary="size=6",
                children=[
                    ValueCheck(name="[0]", value="1"),
                    ValueCheck(name="[1]", value="2"),
                    ValueCheck(name="[2]", value="3"),
                    ValueCheck(name="[3]", value="4"),
                    ValueCheck(name="[4]", value="5"),
                    ValueCheck(name="[5]", value="6"),
                ],
            ),
        )
