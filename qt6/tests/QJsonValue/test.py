import testlib
from testlib import ValueCheck


class TestQJsonObject(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("emptyDefault", ValueCheck(summary="null", children=[]))

        self.assertVarPath("emptyNull", ValueCheck(summary="null", children=[]))
        self.assertVarPath(
            "emptyBool", ValueCheck(value="false", summary="", children=[])
        )
        self.assertVarPath(
            "emptyDouble", ValueCheck(value="0", summary="", children=[])
        )
        self.assertVarPath("emptyString", ValueCheck(summary='""', children=[]))
        self.assertVarPath("emptyArray", ValueCheck(summary="[ size=0 ]", children=[]))
        self.assertVarPath("emptyObject", ValueCheck(summary="{ size=0 }", children=[]))
        self.assertVarPath(
            "emptyUndefined", ValueCheck(summary="undefined", children=[])
        )

        self.assertVarPath("vTrue", ValueCheck(value="true", children=[]))
        self.assertVarPath("vFalse", ValueCheck(value="false", children=[]))
        self.assertVarPath("vInt", ValueCheck(value="42", children=[]))
        self.assertVarPath("vInt64", ValueCheck(value="-42", children=[]))
        self.assertVarPath("vDouble", ValueCheck(value="1.75", children=[]))
        self.assertVarPath("vStr", ValueCheck(summary='"str"', children=[]))
        self.assertVarPath("vStrUtf16", ValueCheck(summary='u"str🚧"', children=[]))
        self.assertVarPath("vStrEmpty", ValueCheck(summary='""', children=[]))
        self.assertVarPath(
            "vArray",
            ValueCheck(
                summary="[ size=4 ]",
                children=[
                    ValueCheck(name="[0]", value="1"),
                    ValueCheck(name="[1]", value="2"),
                    ValueCheck(name="[2]", summary='"string"'),
                    ValueCheck(
                        name="[3]",
                        summary="{ size=1 }",
                        children=[ValueCheck(name='["object"]', value="true")],
                    ),
                ],
            ),
        )
        self.assertVarPath(
            "vObject",
            ValueCheck(
                summary="{ size=4 }",
                children=[
                    ValueCheck(name='[""]', value="false"),
                    ValueCheck(name='["a"]', summary='"value"'),
                    ValueCheck(name='["b"]', summary="[ size=0 ]", children=[]),
                    ValueCheck(name='["c"]', value="123"),
                ],
            ),
        )
