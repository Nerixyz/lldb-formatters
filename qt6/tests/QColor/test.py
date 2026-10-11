import testlib
from testlib import ValueCheck
import re


class TestQColor(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("invalid", ValueCheck(summary="invalid"))
        self.assertVarPath("rgb", ValueCheck(summary="rgb(12, 34, 56)"))
        self.assertVarPath("rgba", ValueCheck(summary="rgba(1, 2, 3, 4)"))
        self.assertVarPath("hsl", ValueCheck(summary="hsl(42, 20, 64)"))
        self.assertVarPath("hsla", ValueCheck(summary="hsla(-1, 0, 64, 5)"))
        self.assertVarPath("hsv", ValueCheck(summary="hsv(42, 20, 64)"))
        self.assertVarPath("hsva", ValueCheck(summary="hsva(-1, 0, 64, 5)"))
        self.assertVarPath("cmyk", ValueCheck(summary="cmyk(1, 2, 3, 4)"))
        self.assertVarPath("cmyka", ValueCheck(summary="cmyka(1, 2, 3, 4, 20)"))
        self.assertVarPath(
            "extRgb",
            ValueCheck(summary=re.compile(r"^ergb\(-1\.0, 0\.13330\d+, 2\.0\)$")),
        )
        self.assertVarPath(
            "extRgba",
            ValueCheck(
                summary=re.compile(r"^ergba\(-1\.0, 0.13330\d+, 2.0, 0.0902\d+\)$")
            ),
        )
