import testlib
from testlib import ValueCheck


class TestQSizePolicy(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "exIg",
            ValueCheck(
                summary="horizontal=Expanding, vertical=Ignored",
                children=[
                    ValueCheck("[HorizontalPolicy]", value="Expanding"),
                    ValueCheck("[VerticalPolicy]", value="Ignored"),
                    ValueCheck("[HorizontalStretch]", value="0"),
                    ValueCheck("[VerticalStretch]", value="0"),
                    ValueCheck("[ControlType]", value="DefaultType"),
                    ValueCheck("[HeightForWidth]", value="false"),
                    ValueCheck("[WidthForHeight]", value="true"),
                ],
            ),
        )
        self.assertVarPath(
            "hfw",
            ValueCheck(
                summary="horizontal=Preferred, vertical=Maximum",
                children=[
                    ValueCheck("[HorizontalPolicy]", value="Preferred"),
                    ValueCheck("[VerticalPolicy]", value="Maximum"),
                    ValueCheck("[HorizontalStretch]", value="3"),
                    ValueCheck("[VerticalStretch]", value="4"),
                    ValueCheck("[ControlType]", value="CheckBox"),
                    ValueCheck("[HeightForWidth]", value="true"),
                    ValueCheck("[WidthForHeight]", value="false"),
                ],
            ),
        )
