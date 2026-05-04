import testlib
from testlib import ValueCheck
import re


class TestQVariant(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")

        self.assertVarPath("null", ValueCheck(summary="(null)"))
        self.assertVarPath(
            "vBool",
            ValueCheck(
                value="true",
                children=[
                    ValueCheck(name="[Type]", summary='"bool"'),
                    ValueCheck(name="[Value]", value="true"),
                ],
            ),
        )
        self.assertVarPath(
            "vInt",
            ValueCheck(
                value="-10",
                children=[
                    ValueCheck(name="[Type]", summary='"int"'),
                    ValueCheck(name="[Value]", value="-10"),
                ],
            ),
        )
        self.assertVarPath(
            "vUint",
            ValueCheck(
                value="10",
                children=[
                    ValueCheck(name="[Type]", summary='"uint"'),
                    ValueCheck(name="[Value]", value="10"),
                ],
            ),
        )
        self.assertVarPath(
            "vLongLong",
            ValueCheck(
                value="42",
                children=[
                    ValueCheck(name="[Type]", summary='"qlonglong"'),
                    ValueCheck(name="[Value]", value="42"),
                ],
            ),
        )
        self.assertVarPath(
            "vULongLong",
            ValueCheck(
                value="42",
                children=[
                    ValueCheck(name="[Type]", summary='"qulonglong"'),
                    ValueCheck(name="[Value]", value="42"),
                ],
            ),
        )
        self.assertVarPath(
            "vDouble",
            ValueCheck(
                value="3.25",
                children=[
                    ValueCheck(name="[Type]", summary='"double"'),
                    ValueCheck(name="[Value]", value="3.25"),
                ],
            ),
        )
        self.assertVarPath(
            "vLong",
            ValueCheck(
                value="42",
                children=[
                    ValueCheck(name="[Type]", summary='"long"'),
                    ValueCheck(name="[Value]", value="42"),
                ],
            ),
        )
        self.assertVarPath(
            "vShort",
            ValueCheck(
                value="42",
                children=[
                    ValueCheck(name="[Type]", summary='"short"'),
                    ValueCheck(name="[Value]", value="42"),
                ],
            ),
        )
        self.assertVarPath(
            "vChar",
            ValueCheck(
                value="'V'",
                children=[
                    ValueCheck(name="[Type]", summary='"char"'),
                    ValueCheck(name="[Value]", value="'V'"),
                ],
            ),
        )
        self.assertVarPath(
            "vULong",
            ValueCheck(
                value="42",
                children=[
                    ValueCheck(name="[Type]", summary='"ulong"'),
                    ValueCheck(name="[Value]", value="42"),
                ],
            ),
        )
        self.assertVarPath(
            "vUShort",
            ValueCheck(
                value="42",
                children=[
                    ValueCheck(name="[Type]", summary='"ushort"'),
                    ValueCheck(name="[Value]", value="42"),
                ],
            ),
        )

        self.assertVarPath(
            "vUChar",
            ValueCheck(
                value="'U'",
                children=[
                    ValueCheck(name="[Type]", summary='"uchar"'),
                    ValueCheck(name="[Value]", value="'U'"),
                ],
            ),
        )
        self.assertVarPath(
            "vFloat",
            ValueCheck(
                value="3.5",
                children=[
                    ValueCheck(name="[Type]", summary='"float"'),
                    ValueCheck(name="[Value]", value="3.5"),
                ],
            ),
        )

        ptr_re = re.compile("^0x")
        self.assertVarPath(
            "vVoidStar",
            ValueCheck(
                value=ptr_re,
                children=[
                    ValueCheck(name="[Type]", summary='"void*"'),
                    ValueCheck(name="[Value]", value=ptr_re),
                ],
            ),
        )
        self.assertVarPath(
            "vQChar",
            ValueCheck(
                value="U+00e4",
                children=[
                    ValueCheck(name="[Type]", summary='"QChar"'),
                    ValueCheck(name="[Value]", value="U+00e4"),
                ],
            ),
        )
        self.assertVarPath(
            "vQString",
            ValueCheck(
                summary=re.compile(r'^u?"Hello World🍳"$'),
                children=[
                    ValueCheck(name="[Type]", summary='"QString"'),
                    ValueCheck(
                        name="[Value]", summary=re.compile(r'^u?"Hello World🍳"$')
                    ),
                ],
            ),
        )
        self.assertVarPath(
            "vQStringList",
            ValueCheck(
                summary="size=2",
                children=[
                    ValueCheck(name="[Type]", summary='"QStringList"'),
                    ValueCheck(
                        name="[Value]",
                        summary="size=2",
                        children=[
                            ValueCheck(name="[0]", summary=re.compile(r'^u?"foo"$')),
                            ValueCheck(name="[1]", summary=re.compile(r'^u?"bar"$')),
                        ],
                    ),
                ],
            ),
        )
        self.assertVarPath("vQByteArray", ValueCheck(summary='"Hello World!"'))

        self.assertVarPath(
            "vQDate",
            ValueCheck(
                summary="2026-05-02",
                children=[
                    ValueCheck(name="[Type]", summary='"QDate"'),
                    ValueCheck(
                        name="[Value]",
                        summary="2026-05-02",
                        children=[
                            ValueCheck(name="[year]", value="2026"),
                            ValueCheck(name="[month]", value="5"),
                            ValueCheck(name="[day]", value="2"),
                        ],
                    ),
                ],
            ),
        )
        self.assertVarPath(
            "vQTime",
            ValueCheck(
                summary="13:42",
                children=[
                    ValueCheck(name="[Type]", summary='"QTime"'),
                    ValueCheck(
                        name="[Value]",
                        summary="13:42",
                        children=[
                            ValueCheck(name="[hour]", value="13"),
                            ValueCheck(name="[minute]", value="42"),
                            ValueCheck(name="[second]", value="0"),
                            ValueCheck(name="[millisecond]", value="0"),
                        ],
                    ),
                ],
            ),
        )

        self.assertVarPath(
            "vSChar",
            ValueCheck(
                value="'V'",
                children=[
                    ValueCheck(name="[Type]", summary='"signed char"'),
                    ValueCheck(name="[Value]", value="'V'"),
                ],
            ),
        )
        self.assertVarPath("vChar16", ValueCheck(value="U+0056"))
        self.assertVarPath("vChar32", ValueCheck(value="U+0x00000056"))
        self.assertVarPath("vNullptr", ValueCheck(summary="(null)"))

        self.assertVarPath(
            "qObjectStar",
            ValueCheck(
                value=ptr_re,
            ),
        )
        self.assertVarPath(
            "qSize",
            ValueCheck(
                summary="(width: 42, height: 42)",
                children=[
                    ValueCheck(name="[Type]", summary='"QSize"'),
                    ValueCheck(
                        name="[Value]",
                        summary="(width: 42, height: 42)",
                        children=[
                            ValueCheck(name="[width]", value="42"),
                            ValueCheck(name="[height]", value="42"),
                        ],
                    ),
                ],
            ),
        )

        self.assertVarPath(
            "qVList",
            ValueCheck(
                summary="size=4",
                children=[
                    ValueCheck(name="[Type]", summary='"QVariantList"'),
                    ValueCheck(
                        name="[Value]",
                        summary="size=4",
                        children=[
                            ValueCheck(name="[0]", value="1"),
                            ValueCheck(name="[1]", value="true"),
                            ValueCheck(name="[2]", value="false"),
                            ValueCheck(name="[3]", summary=re.compile(r"^1970-01-01")),
                        ],
                    ),
                ],
            ),
        )
        self.assertVarPath(
            "qVMap",
            ValueCheck(
                summary="size=2",
                children=[
                    ValueCheck(name="[Type]", summary='"QVariantMap"'),
                    ValueCheck(
                        name="[Value]",
                        summary="size=2",
                        children=[
                            ValueCheck(
                                name="[0]",
                                children=[
                                    ValueCheck(summary=re.compile(r'^u?"bar"')),
                                    ValueCheck(value="42"),
                                ],
                            ),
                            ValueCheck(
                                name="[1]",
                                children=[
                                    ValueCheck(summary=re.compile(r'^u?"foo"')),
                                    ValueCheck(value="true"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )
        self.assertVarPath(
            "qVHash",
            ValueCheck(
                summary="size=1",
                children=[
                    ValueCheck(name="[Type]", summary='"QVariantHash"'),
                    ValueCheck(
                        name="[Value]",
                        summary="size=1",
                        children=[
                            ValueCheck(
                                name="[0]",
                                children=[
                                    ValueCheck(summary=re.compile(r'^u?"foo"')),
                                    ValueCheck(value="true"),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )

        self.assertVarPath(
            "qUserTypeNoTemplate",
            ValueCheck(
                children=[
                    ValueCheck(name="[Type]", summary='"MyType"'),
                    ValueCheck(
                        name="[Value]",
                        children=[
                            ValueCheck(name="a", value="42"),
                            ValueCheck(name="b", value="43"),
                        ],
                    ),
                ],
            ),
        )

        self.assertVarPath("qUserPtr", ValueCheck(value=ptr_re))

        self.assertVarPath(
            "qUserTypeLarge",
            ValueCheck(
                children=[
                    ValueCheck(name="[Type]", summary='"MyLargeType"'),
                    ValueCheck(
                        name="[Value]",
                        children=[
                            ValueCheck(name="str1", summary='"foo"'),
                            ValueCheck(name="str2", summary='"bar"'),
                        ],
                    ),
                ],
            ),
        )

        self.assertVarPath(
            "qIntPtr",
            ValueCheck(
                value=ptr_re,
                children=[
                    ValueCheck(name="[Type]", summary='"int*"'),
                    ValueCheck(
                        name="[Value]",
                        children=[
                            ValueCheck(name="*[Value]", value="1234"),
                        ],
                    ),
                ],
            ),
        )
