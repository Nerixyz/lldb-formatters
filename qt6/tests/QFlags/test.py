import testlib
from testlib import ValueCheck


class TestQFlags(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "zero1",
            ValueCheck(value="0x0", children=[ValueCheck(name="[int]", value="0")]),
        )
        self.assertVarPath(
            "oneFlag1",
            ValueCheck(value="MyVal1", children=[ValueCheck(name="[int]", value="1")]),
        )
        self.assertVarPath(
            "twoFlags1",
            ValueCheck(
                value="MyVal1 | MyVal2", children=[ValueCheck(name="[int]", value="3")]
            ),
        )
        self.assertVarPath(
            "diffFlag1",
            ValueCheck(
                value="MyVal1 | MyVal2 | 0x80",
                children=[ValueCheck(name="[int]", value="131")],
            ),
        )

        self.assertVarPath(
            "zero2",
            ValueCheck(value="0x0", children=[ValueCheck(name="[int]", value="0")]),
        )
        self.assertVarPath(
            "oneFlag2",
            ValueCheck(
                value="Val53",
                children=[ValueCheck(name="[int]", value="9007199254740992")],
            ),
        )
        self.assertVarPath(
            "twoFlags2",
            ValueCheck(
                value="Val1 | Val53",
                children=[ValueCheck(name="[int]", value="9007199254740993")],
            ),
        )
        self.assertVarPath(
            "diffFlag2",
            ValueCheck(
                value="Val1 | Val52 | 0x80",
                children=[ValueCheck(name="[int]", value="4503599627370625")],
            ),
        )
