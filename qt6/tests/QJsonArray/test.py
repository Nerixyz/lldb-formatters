import testlib
from testlib import ValueCheck
import re


class TestQJsonArray(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("empty", ValueCheck(summary="[ size=0 ]", children=[]))
        self.assertVarPath(
            "one",
            ValueCheck(
                summary="[ size=1 ]",
                children=[ValueCheck(name="[0]", summary='"key"')],
            ),
        )
        self.assertVarPath(
            "two",
            ValueCheck(
                summary="[ size=2 ]",
                children=[
                    ValueCheck(name="[0]", value="1", summary=""),
                    ValueCheck(name="[1]", value="false", summary=""),
                ],
            ),
        )
        self.assertVarPath(
            "allTypes",
            ValueCheck(
                summary="[ size=12 ]",
                children=[
                    ValueCheck(name="[0]", value="1.25", summary=""),
                    ValueCheck(name="[1]", value="true", summary=""),
                    ValueCheck(name="[2]", value="false", summary=""),
                    ValueCheck(name="[3]", value="1234567890", summary=""),
                    ValueCheck(name="[4]", summary="null"),
                    ValueCheck(name="[5]", summary='"stringAscii"'),
                    ValueCheck(name="[6]", summary=re.compile(r'^u?"utf16💔"$')),
                    ValueCheck(name="[7]", summary='""'),
                    ValueCheck(
                        name="[8]",
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
                    ValueCheck(name="[9]", summary="[ size=0 ]", children=[]),
                    ValueCheck(name="[10]", summary="{ size=0 }", children=[]),
                    ValueCheck(
                        name="[11]",
                        summary="{ size=1 }",
                        children=[
                            ValueCheck(
                                name='["nested"]',
                                summary="{ size=1 }",
                                children=[ValueCheck(name='["object"]', value="1")],
                            )
                        ],
                    ),
                ],
            ),
        )
