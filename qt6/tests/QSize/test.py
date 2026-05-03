import testlib
from testlib import ValueCheck


class TestQSize(testlib.TestCase):
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
                summary="(width: 10, height: 20)",
                children=[
                    ValueCheck(name="[width]", value="10"),
                    ValueCheck(name="[height]", value="20"),
                ],
            ),
        )
