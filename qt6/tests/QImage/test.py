import testlib
from testlib import ValueCheck
import re


class TestQHostAddress(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("null", ValueCheck(summary="(null)", children=[]))
        self.assertVarPath(
            "i200x300Pm",
            ValueCheck(
                summary="200x300",
                children=[
                    ValueCheck(name="[Width]", value="200"),
                    ValueCheck(name="[Height]", value="300"),
                    ValueCheck(name="[Format]", value="Format_ARGB32_Premultiplied"),
                    ValueCheck(name="[Data]", value=re.compile(r"^0x")),
                    ValueCheck(name="[ByteSize]", value="240000"),
                    ValueCheck(name="[Stride]", value="800"),
                    ValueCheck(name="[DevicePixelRatio]", value="1"),
                ],
            ),
        )
        d = self.frame().FindValue("data")
        i200x300Pm = self.frame().FindValue("i200x300OPm")
        self.assertEqual(d.GetValue(), i200x300Pm.GetValue())
        self.assertEqual(d.GetValueAsAddress(), i200x300Pm.GetValueAsAddress())
