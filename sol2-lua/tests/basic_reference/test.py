import testlib
from testlib import ValueCheck, ChildrenUnordered, ChildrenStartsWith
import re


class TestBasicReference(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("a_bool", ValueCheck(summary="true", children=[]))
        self.assertVarPath(
            "a_int",
            ValueCheck(
                value="1234567890123",
                children=[
                    ValueCheck(name="[Value]", value="1234567890123", children=[])
                ],
            ),
        )
        self.assertVarPath(
            "a_double",
            ValueCheck(
                value=re.compile(r"^3.14(0+1)?$"),
                children=[
                    ValueCheck(
                        name="[Value]", value=re.compile(r"^3.14(0+1)?$"), children=[]
                    )
                ],
            ),
        )
        self.assertVarPath("a_nil", ValueCheck(summary="nil", children=[]))
        self.assertVarPath("a_string_empty", ValueCheck(summary='""', children=[]))
        self.assertVarPath("a_string_short", ValueCheck(summary='"a"'))
        self.assertVarPath(
            "a_string_long",
            ValueCheck(
                summary='"foobar abcdef this is some long text make sure it\'s correct yes"'
            ),
        )
        self.assertVarPath("a_string_with_nul", ValueCheck(summary='"foo bar\\0baz"'))
        self.assertVarPath("a_table_empty", ValueCheck(summary="table", children=[]))
        self.assertVarPath(
            "a_table_array",
            ValueCheck(
                summary="table",
                children=[
                    ValueCheck(name="[1]", value="0"),
                    ValueCheck(name="[2]", value="1"),
                    ValueCheck(name="[3]", value="2"),
                    ValueCheck(name="[4]", value="3"),
                    ValueCheck(name="[5]", value="4"),
                    ValueCheck(name="[6]", value="5"),
                    ValueCheck(name="[7]", value="6"),
                    ValueCheck(name="[8]", value="7"),
                    ValueCheck(name="[9]", value="8"),
                    ValueCheck(name="[10]", value="9"),
                    ValueCheck(name="[11]", value="10"),
                ],
            ),
        )
        self.assertVarPath(
            "a_table_mixed",
            ValueCheck(
                summary="table",
                children=[
                    ChildrenStartsWith(
                        [
                            ValueCheck(name="[1]", value="0"),
                            ValueCheck(name="[2]", value="1"),
                            ValueCheck(name="[3]", value="2"),
                        ]
                    ),
                    ChildrenUnordered(
                        [
                            ValueCheck(name='["d"]', summary='"what"'),
                            ValueCheck(name='["e"]', summary='"ever"'),
                        ]
                    ),
                ],
            ),
        )
        # FIXME: add synthetic children
        self.assertVarPath("a_lua_function", ValueCheck(summary="Lua closure"))
        self.assertVarPath(
            "a_c_closure",
            ValueCheck(
                summary="C closure",
                children=[
                    ValueCheck(
                        name="[function]",
                        summary=re.compile(
                            r"sol::function_detail::upvalue_free_function"
                        ),
                    ),
                    ValueCheck(name="[upvalues]"),
                ],
            ),
        )
        self.assertVarPath(
            "a_c_function",
            ValueCheck(
                value=re.compile("^0x"),
                children=[
                    ValueCheck(
                        name="[Value]",
                        summary=re.compile("luaB_print"),
                    )
                ],
            ),
        )
