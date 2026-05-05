import testlib
from testlib import ValueCheck
import re


class TestQJsonValueRef(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        arrCheck = ValueCheck(
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
        )
        doubleCheck = ValueCheck(value="1.25", summary="")
        emptyArrCheck = ValueCheck(summary="[ size=0 ]", children=[])
        emptyObjCheck = ValueCheck(summary="{ size=0 }", children=[])
        falseCheck = ValueCheck(value="false", summary="")
        intCheck = ValueCheck(value="1234567890", summary="")
        nullCheck = ValueCheck(summary="null")
        objCheck = ValueCheck(
            summary="{ size=1 }",
            children=[
                ValueCheck(
                    name='["nested"]',
                    summary="{ size=1 }",
                    children=[ValueCheck(name='["object"]', value="1")],
                )
            ],
        )
        trueCheck = ValueCheck(value="true", summary="")
        strAsciiCheck = ValueCheck(summary='"stringAscii"')
        strUtf16Check = ValueCheck(summary=re.compile(r'u?"utf16💔"$'))

        self.assertVarPath("oRArray", arrCheck)
        self.assertVarPath("oRDouble", doubleCheck)
        self.assertVarPath("oREmptyArray", emptyArrCheck)
        self.assertVarPath("oREmptyObject", emptyObjCheck)
        self.assertVarPath("oRFalse", falseCheck)
        self.assertVarPath("oRInt", intCheck)
        self.assertVarPath("oRNull", nullCheck)
        self.assertVarPath("oRObject", objCheck)
        self.assertVarPath("oRStringAscii", strAsciiCheck)
        self.assertVarPath("oRStringUtf16", strUtf16Check)
        self.assertVarPath("oRTrue", trueCheck)

        self.assertVarPath("aRArray", arrCheck)
        self.assertVarPath("aRDouble", doubleCheck)
        self.assertVarPath("aREmptyArray", emptyArrCheck)
        self.assertVarPath("aREmptyObject", emptyObjCheck)
        self.assertVarPath("aRFalse", falseCheck)
        self.assertVarPath("aRInt", intCheck)
        self.assertVarPath("aRNull", nullCheck)
        self.assertVarPath("aRObject", objCheck)
        self.assertVarPath("aRStringAscii", strAsciiCheck)
        self.assertVarPath("aRStringUtf16", strUtf16Check)
        self.assertVarPath("aRTrue", trueCheck)
