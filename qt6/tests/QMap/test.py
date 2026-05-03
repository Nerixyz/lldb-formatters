import testlib
from testlib import ValueCheck


class TestQMap(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("empty", ValueCheck(summary="size=0", children=[]))
        self.assertVarPath(
            "one",
            ValueCheck(
                summary="size=1",
                children=[
                    ValueCheck(
                        name="[0]",
                        children=[
                            ValueCheck(name="first", value="1"),
                            ValueCheck(name="second", value="2"),
                        ],
                    )
                ],
            ),
        )
        self.assertVarPath(
            "many",
            ValueCheck(
                summary="size=10",
                children=[
                    ValueCheck(
                        name=f"[{i}]",
                        children=[
                            ValueCheck(name="first", value=str(i + 1)),
                            ValueCheck(name="second", value=str((i + 1) * 2)),
                        ],
                    )
                    for i in range(10)
                ],
            ),
        )
