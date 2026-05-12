import testlib
from testlib import ValueCheck


class TestRapidjsonValueUtf8(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("empty", ValueCheck(summary="null", children=[]))
        self.assertVarPath("vInt", ValueCheck(value="1234", children=[]))
        self.assertVarPath("vUint", ValueCheck(value="1234", children=[]))
        self.assertVarPath("vInt64", ValueCheck(value="1234", children=[]))
        self.assertVarPath("vUint64", ValueCheck(value="1234", children=[]))
        self.assertVarPath("vDouble", ValueCheck(value="1.25", children=[]))
        self.assertVarPath("vTrue", ValueCheck(value="true", children=[]))
        self.assertVarPath("vFalse", ValueCheck(value="false", children=[]))
        self.assertVarPath("vShortStr", ValueCheck(summary='"short"', children=[]))
        self.assertVarPath(
            "vLongStr",
            ValueCheck(
                summary='"quite a long string that has to be allocated..."', children=[]
            ),
        )

        arrChildren = [
            ValueCheck(name="[0]", summary="null"),
            ValueCheck(name="[1]", value="1234"),
            ValueCheck(name="[2]", value="1234"),
            ValueCheck(name="[3]", value="-1234"),
            ValueCheck(name="[4]", value="true"),
            ValueCheck(name="[5]", value="false"),
            ValueCheck(name="[6]", summary='"short"'),
            ValueCheck(
                name="[7]",
                summary='"quite a long string that has to be allocated2..."',
            ),
            ValueCheck(
                name="[8]",
                summary="[ size=1 ]",
                children=[
                    ValueCheck(name="[0]", summary='"abc"'),
                ],
            ),
            ValueCheck(
                name="[9]",
                summary="{ size=3 }",
                children=[
                    ValueCheck(name='["a"]', value="true"),
                    ValueCheck(name='["b"]', value="false"),
                    ValueCheck(name='["c"]', summary='"abc"'),
                ],
            ),
        ]
        self.assertVarPath(
            "vArray",
            ValueCheck(
                summary="[ size=10 ]",
                children=arrChildren,
            ),
        )

        self.assertVarPath(
            "vObject",
            ValueCheck(
                summary="{ size=13 }",
                children=[
                    ValueCheck(name='["int"]', value="123"),
                    ValueCheck(name='["null"]', summary="null"),
                    ValueCheck(name='["uint"]', value="456"),
                    ValueCheck(name='["int64"]', value="123"),
                    ValueCheck(name='["uint64"]', value="123"),
                    ValueCheck(name='["double"]', value="1.25"),
                    ValueCheck(name='["true"]', value="true"),
                    ValueCheck(name='["false"]', value="false"),
                    ValueCheck(name='["string"]', summary='"abc"'),
                    ValueCheck(
                        name='["longString"]',
                        summary='"a long string so write something here to overshoot"',
                    ),
                    ValueCheck(
                        name='["array"]',
                        summary="[ size=10 ]",
                        children=arrChildren,
                    ),
                    ValueCheck(
                        name='["object"]',
                        summary="{ size=3 }",
                        children=[
                            ValueCheck(name='["a"]', value="true"),
                            ValueCheck(name='["b"]', value="false"),
                            ValueCheck(name='["c"]', summary='"abc"'),
                        ],
                    ),
                    ValueCheck(
                        name='["aLongMemberNameThatHasToBeAllocated"]', summary='"ok"'
                    ),
                ],
            ),
        )
