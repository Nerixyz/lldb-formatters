import testlib
from testlib import ValueCheck


class TestQSizeF(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "unsized",
            ValueCheck(
                summary="size=5",
                children=[
                    ValueCheck(name="[0]", value="1"),
                    ValueCheck(name="[1]", value="2"),
                    ValueCheck(name="[2]", value="3"),
                    ValueCheck(name="[3]", value="4"),
                    ValueCheck(name="[4]", value="5"),
                ],
            ),
        )
        self.assertVarPath(
            "sized",
            ValueCheck(
                summary="size=2",
                children=[
                    ValueCheck(name="[0]", value="1"),
                    ValueCheck(name="[1]", value="2"),
                ],
            ),
        )
