import testlib
from testlib import ValueCheck


class TestQDate(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("null", ValueCheck(summary="(invalid)", children=[]))
        self.assertVarPath(
            "someDay",
            ValueCheck(
                summary="2026-05-10",
                children=[
                    ValueCheck(name="[year]", value="2026"),
                    ValueCheck(name="[month]", value="5"),
                    ValueCheck(name="[day]", value="10"),
                ],
            ),
        )
        self.assertVarPath(
            "min",
            ValueCheck(
                summary="-2147483648-01-01",
                children=[
                    ValueCheck(name="[year]", value="-2147483648"),
                    ValueCheck(name="[month]", value="1"),
                    ValueCheck(name="[day]", value="1"),
                ],
            ),
        )
        self.assertVarPath(
            "max",
            ValueCheck(
                summary="2147483647-12-31",
                children=[
                    ValueCheck(name="[year]", value="2147483647"),
                    ValueCheck(name="[month]", value="12"),
                    ValueCheck(name="[day]", value="31"),
                ],
            ),
        )
