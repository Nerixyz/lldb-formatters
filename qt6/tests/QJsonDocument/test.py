import testlib
from testlib import ValueCheck


class TestQJsonObject(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("docEmpty", ValueCheck(summary="null", children=[]))
        an_array_children = [
            ValueCheck(name="[0]", summary='"foo"'),
            ValueCheck(name="[1]", summary='"bar"'),
            ValueCheck(
                name="[2]",
                summary="{ size=2 }",
                children=[
                    ValueCheck(name='["abc"]', summary='"def"'),
                    ValueCheck(name='["ghi"]', summary="null"),
                ],
            ),
            ValueCheck(
                name="[3]",
                summary="[ size=5 ]",
                children=[
                    ValueCheck(name="[0]", value="1"),
                    ValueCheck(name="[1]", value="2"),
                    ValueCheck(name="[2]", value="true"),
                    ValueCheck(name="[3]", value="false"),
                    ValueCheck(name="[4]", value="42.5"),
                ],
            ),
        ]
        an_object_children = [
            ValueCheck(
                name='["abc"]',
                summary="{ size=2 }",
                children=[
                    ValueCheck(name='["abc"]', summary='"def"'),
                    ValueCheck(name='["ghi"]', summary="null"),
                ],
            ),
            ValueCheck(
                name='["def"]',
                summary="[ size=5 ]",
                children=[
                    ValueCheck(name="[0]", value="1"),
                    ValueCheck(name="[1]", value="2"),
                    ValueCheck(name="[2]", value="true"),
                    ValueCheck(name="[3]", value="false"),
                    ValueCheck(name="[4]", value="42.5"),
                ],
            ),
            ValueCheck(name='["foo"]', summary='"bar"'),
        ]
        self.assertVarPath(
            "docArray",
            ValueCheck(
                summary="[ size=9 ]",
                children=[
                    ValueCheck(name="[0]", summary='u"😃😃😃"'),
                    ValueCheck(name="[1]", summary='"foo"'),
                    ValueCheck(name="[2]", summary='"foo"'),
                    ValueCheck(name="[3]", summary='"empty object->"'),
                    ValueCheck(name="[4]", summary="{ size=0 }", children=[]),
                    ValueCheck(name="[5]", summary='"empty array ->"'),
                    ValueCheck(name="[6]", summary="[ size=0 ]", children=[]),
                    ValueCheck(
                        name="[7]", summary="{ size=3 }", children=an_object_children
                    ),
                    ValueCheck(
                        name="[8]", summary="[ size=4 ]", children=an_array_children
                    ),
                ],
            ),
        )

        self.assertVarPath(
            "docObject",
            ValueCheck(
                summary="{ size=6 }",
                children=[
                    ValueCheck(
                        name='["an array"]',
                        summary="[ size=4 ]",
                        children=an_array_children,
                    ),
                    ValueCheck(
                        name='["an object"]',
                        summary="{ size=3 }",
                        children=an_object_children,
                    ),
                    ValueCheck(
                        name='["empty array ->"]', summary="[ size=0 ]", children=[]
                    ),
                    ValueCheck(
                        name='["empty object->"]', summary="{ size=0 }", children=[]
                    ),
                    ValueCheck(name='["foo"]', summary='"bar"'),
                    ValueCheck(name='[u"😃😃😃"]', summary='"foo"'),
                ],
            ),
        )
