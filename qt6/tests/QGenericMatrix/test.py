import testlib
from testlib import ValueCheck


class TestQGenericMatrix(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "cols2rows3",
            ValueCheck(
                summary="2x3",
                children=[
                    ValueCheck(name="[m11]", value="0"),
                    ValueCheck(name="[m12]", value="1"),
                    ValueCheck(name="[m21]", value="2"),
                    ValueCheck(name="[m22]", value="3"),
                    ValueCheck(name="[m31]", value="4"),
                    ValueCheck(name="[m32]", value="5"),
                ],
            ),
        )
        self.assertVarPath(
            "cols3rows2",
            ValueCheck(
                summary="3x2",
                children=[
                    ValueCheck(name="[m11]", value="0"),
                    ValueCheck(name="[m12]", value="1"),
                    ValueCheck(name="[m13]", value="2"),
                    ValueCheck(name="[m21]", value="3"),
                    ValueCheck(name="[m22]", value="4"),
                    ValueCheck(name="[m23]", value="5"),
                ],
            ),
        )
