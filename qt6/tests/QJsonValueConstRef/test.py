import testlib
from testlib import ValueCheck
import re


class TestQJsonValueConstRef(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")

        tgt = self.target()
        if not tgt.FindFirstType("QJsonArray") or not tgt.FindFirstType("QJsonObject") or not tgt.FindFirstType("QJsonValue"):
            self.skipTest("QJson* types are not available")

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

        self.assertVarPath("oCrArray", arrCheck)
        self.assertVarPath("oCrDouble", doubleCheck)
        self.assertVarPath("oCrEmptyArray", emptyArrCheck)
        self.assertVarPath("oCrEmptyObject", emptyObjCheck)
        self.assertVarPath("oCrFalse", falseCheck)
        self.assertVarPath("oCrInt", intCheck)
        self.assertVarPath("oCrNull", nullCheck)
        self.assertVarPath("oCrObject", objCheck)
        self.assertVarPath("oCrStringAscii", strAsciiCheck)
        self.assertVarPath("oCrStringUtf16", strUtf16Check)
        self.assertVarPath("oCrTrue", trueCheck)

        self.assertVarPath("aCrArray", arrCheck)
        self.assertVarPath("aCrDouble", doubleCheck)
        self.assertVarPath("aCrEmptyArray", emptyArrCheck)
        self.assertVarPath("aCrEmptyObject", emptyObjCheck)
        self.assertVarPath("aCrFalse", falseCheck)
        self.assertVarPath("aCrInt", intCheck)
        self.assertVarPath("aCrNull", nullCheck)
        self.assertVarPath("aCrObject", objCheck)
        self.assertVarPath("aCrStringAscii", strAsciiCheck)
        self.assertVarPath("aCrStringUtf16", strUtf16Check)
        self.assertVarPath("aCrTrue", trueCheck)
