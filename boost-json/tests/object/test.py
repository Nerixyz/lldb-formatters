import testlib
from testlib import ValueCheck


class TestBoostJsonObject(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("empty", ValueCheck(summary="{ size=0 }", children=[]))
        self.assertVarPath(
            "one",
            ValueCheck(
                summary="{ size=1 }",
                children=[ValueCheck(name='["key"]', summary='"value"')],
            ),
        )
        self.assertVarPath(
            "allTypes",
            ValueCheck(
                summary="{ size=10 }",
                children=[
                    ValueCheck(name='["null"]', summary="null"),
                    ValueCheck(name='["true"]', value="true", summary=""),
                    ValueCheck(name='["false"]', value="false", summary=""),
                    ValueCheck(name='["int64"]', value="-123", summary=""),
                    ValueCheck(name='["uint64"]', value="123", summary=""),
                    ValueCheck(name='["double"]', value="3.25", summary=""),
                    ValueCheck(name='["string"]', summary='"string"'),
                    ValueCheck(
                        name='["longString"]',
                        summary='"a-very-long-string-so-we-allocate-it"',
                    ),
                    ValueCheck(
                        name='["object"]',
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
                        name='["array"]',
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
