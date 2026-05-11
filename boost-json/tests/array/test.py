import testlib
from testlib import ValueCheck


class TestBoostJsonArray(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("empty", ValueCheck(summary="[ size=0 ]", children=[]))
        self.assertVarPath(
            "one",
            ValueCheck(
                summary="[ size=1 ]",
                children=[ValueCheck(name="[0]", value="123")],
            ),
        )
        self.assertVarPath(
            "allTypes",
            ValueCheck(
                summary="[ size=10 ]",
                children=[
                    ValueCheck(name="[0]", summary="null"),
                    ValueCheck(name="[1]", value="true", summary=""),
                    ValueCheck(name="[2]", value="false", summary=""),
                    ValueCheck(name="[3]", value="-123", summary=""),
                    ValueCheck(name="[4]", value="123", summary=""),
                    ValueCheck(name="[5]", value="3.25", summary=""),
                    ValueCheck(name="[6]", summary='"string"'),
                    ValueCheck(
                        name="[7]",
                        summary='"a-very-long-string-so-we-allocate-it"',
                    ),
                    ValueCheck(
                        name="[8]",
                        summary="{ size=2 }",
                        children=[
                            ValueCheck(
                                name='["key"]',
                                summary="[ size=1 ]",
                                children=[
                                    ValueCheck(name="[0]", summary='"value"'),
                                ],
                            ),
                            ValueCheck(name='["something"]', value="true"),
                        ],
                    ),
                    ValueCheck(
                        name="[9]",
                        summary="[ size=4 ]",
                        children=[
                            ValueCheck(name="[0]", value="1"),
                            ValueCheck(name="[1]", value="true"),
                            ValueCheck(name="[2]", value="false"),
                            ValueCheck(
                                name="[3]",
                                summary="{ size=1 }",
                                children=[
                                    ValueCheck(name='["key"]', summary='"value"')
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )
