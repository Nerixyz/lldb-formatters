import testlib
from testlib import ValueCheck


class TestBoostJsonValue(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("defaultC", ValueCheck(summary="null", children=[]))
        self.assertVarPath("null", ValueCheck(summary="null", children=[]))
        self.assertVarPath("vTrue", ValueCheck(value="true", children=[]))
        self.assertVarPath("vFalse", ValueCheck(value="false", children=[]))
        self.assertVarPath("int64", ValueCheck(value="-123456", children=[]))
        self.assertVarPath("uint64", ValueCheck(value="123456", children=[]))
        self.assertVarPath("vDouble", ValueCheck(value="123.5", children=[]))
        self.assertVarPath("vString", ValueCheck(summary='"abcde"'))
        self.assertVarPath(
            "vStringLong",
            ValueCheck(summary='"a-very-long-string-so-we-allocate-it"'),
        )
        self.assertVarPath(
            "vObject",
            ValueCheck(
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
        )
        self.assertVarPath(
            "array",
            ValueCheck(
                summary="[ size=4 ]",
                children=[
                    ValueCheck(name="[0]", value="1"),
                    ValueCheck(name="[1]", value="true"),
                    ValueCheck(name="[2]", value="false"),
                    ValueCheck(
                        name="[3]",
                        summary="{ size=1 }",
                        children=[ValueCheck(name='["key"]', summary='"value"')],
                    ),
                ],
            ),
        )
