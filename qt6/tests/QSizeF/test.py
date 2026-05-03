import testlib
from testlib import ValueCheck


class TestQSizeF(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "empty",
            ValueCheck(
                summary="(width: -1, height: -1)",
                children=[
                    ValueCheck(name="[width]", value="-1"),
                    ValueCheck(name="[height]", value="-1"),
                ],
            ),
        )
        self.assertVarPath(
            "size",
            ValueCheck(
                summary="(width: 1.25, height: 2.5)",
                children=[
                    ValueCheck(name="[width]", value="1.25"),
                    ValueCheck(name="[height]", value="2.5"),
                ],
            ),
        )
