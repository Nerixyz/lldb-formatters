import testlib
from testlib import ValueCheck


class TestQDateTime(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("null", ValueCheck(summary="(invalid)", children=[]))
        self.assertVarPath(
            "utc",
            ValueCheck(
                summary="2026-05-13 02:43:10.500 UTC",
                children=[
                    ValueCheck(name="[ms]", value="1778640190500"),
                    ValueCheck(name="[offset-sec]", value="0"),
                ],
            ),
        )
        self.assertVarPath(
            "local",
            ValueCheck(
                summary="2026-05-13 02:43:10.500 (Local)",
                children=[
                    ValueCheck(name="[ms]", value="1778640190500"),
                ],
            ),
        )
        self.assertVarPath(
            "offPlus1h",
            ValueCheck(
                summary="2026-05-13 02:43:10.500 UTC+01:00",
                children=[
                    ValueCheck(name="[ms]", value="1778636590500"),
                    ValueCheck(name="[offset-sec]", value="3600"),
                ],
            ),
        )
        self.assertVarPath(
            "offMinus1h",
            ValueCheck(
                summary="2026-05-13 02:43:10.500 UTC-01:00",
                children=[
                    ValueCheck(name="[ms]", value="1778643790500"),
                    ValueCheck(name="[offset-sec]", value="-3600"),
                ],
            ),
        )
        self.assertVarPath(
            "negative",
            ValueCheck(
                summary="1969-08-11 02:38:41.500 UTC",
                children=[
                    ValueCheck(name="[ms]", value="-12345678500"),
                    ValueCheck(name="[offset-sec]", value="0"),
                ],
            ),
        )
        self.assertVarPath("invalidZone", ValueCheck(summary="(invalid)"))
