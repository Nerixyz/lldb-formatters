import testlib
from testlib import ValueCheck
import re


class TestQJsonObject(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")

        tgt = self.target()
        if not tgt.FindFirstType("QJsonArray") or not tgt.FindFirstType("QJsonObject") or not tgt.FindFirstType("QJsonValue"):
            self.skipTest("QJson* types are not available")

        self.assertVarPath("empty", ValueCheck(summary="{ size=0 }", children=[]))
        self.assertVarPath(
            "one",
            ValueCheck(
                summary="{ size=1 }",
                children=[ValueCheck(name='["key"]', summary='"value"')],
            ),
        )
        self.assertVarPath(
            "two",
            ValueCheck(
                summary="{ size=2 }",
                children=[
                    ValueCheck(name='["key"]', value="1", summary=""),
                    ValueCheck(name='["value"]', value="2", summary=""),
                ],
            ),
        )
        self.assertVarPath(
            "allTypes",
            ValueCheck(
                summary="{ size=12 }",
                children=[
                    ValueCheck(
                        name='["array"]',
                        summary="[ size=6 ]",
                        children=[
                            ValueCheck(name="[0]", value="1"),
                            ValueCheck(name="[1]", value="2"),
                            ValueCheck(name="[2]", summary="null"),
                            ValueCheck(name="[3]", summary='"foo"'),
                            ValueCheck(
                                name="[4]",
                                summary="{ size=1 }",
                                children=[
                                    ValueCheck(name='["bar"]', value="false"),
                                ],
                            ),
                            ValueCheck(name="[5]", value="true"),
                        ],
                    ),
                    ValueCheck(name='["double"]', value="1.25", summary=""),
                    ValueCheck(
                        name='["emptyArray"]', summary="[ size=0 ]", children=[]
                    ),
                    ValueCheck(
                        name='["emptyObject"]', summary="{ size=0 }", children=[]
                    ),
                    ValueCheck(name='["false"]', value="false", summary=""),
                    ValueCheck(name='["int"]', value="1234567890", summary=""),
                    ValueCheck(name='["null"]', summary="null"),
                    ValueCheck(
                        name='["object"]',
                        summary="{ size=1 }",
                        children=[
                            ValueCheck(
                                name='["nested"]',
                                summary="{ size=1 }",
                                children=[ValueCheck(name='["object"]', value="1")],
                            )
                        ],
                    ),
                    ValueCheck(name='["stringAscii"]', summary='"stringAscii"'),
                    # FIXME: LLDB before 23 doesn't use the array bounds for strings
                    ValueCheck(
                        name=re.compile(r'^\[u?"stringKeyUtf16🐛"]$'), summary='""'
                    ),
                    # FIXME: LLDB before 23 doesn't use the array bounds for strings
                    ValueCheck(
                        name='["stringUtf16"]', summary=re.compile(r'u?"utf16💔"$')
                    ),
                    ValueCheck(name='["true"]', value="true", summary=""),
                ],
            ),
        )
