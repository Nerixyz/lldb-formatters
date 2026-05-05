import testlib
from testlib import ValueCheck
import re


class TestQObject(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        root_addr = self.frame().FindValue("root").GetValueAsAddress()
        level1a_addr = self.frame().FindValue("level1a").GetValueAsAddress()
        self.assertVarPath(
            "root",
            ValueCheck(
                summary=re.compile(r'^u?"root"$'),
                children=[
                    ValueCheck(name="[Parent]", value=re.compile(r"^0x0+$")),
                    ValueCheck(name="[Name]", value=re.compile(r'^u"root"$')),
                ],
            ),
        )
        self.assertVarPath(
            "level1a",
            ValueCheck(
                children=[
                    ValueCheck(name="[Parent]", value=f"{root_addr:#x}"),
                ],
            ),
        )
        self.assertVarPath(
            "level1b",
            ValueCheck(
                children=[
                    ValueCheck(name="[Parent]", value=f"{root_addr:#x}"),
                ],
            ),
        )
        self.assertVarPath(
            "level2a",
            ValueCheck(
                summary=re.compile(r'^u?"object"$'),
                children=[
                    ValueCheck(name="[Parent]", value=f"{level1a_addr:#x}"),
                    ValueCheck(name="[Name]", value=re.compile(r'^u"object"$')),
                    ValueCheck(
                        name="[PropertyNames]",
                        summary="size=2",
                        children=[
                            ValueCheck(name="[0]", summary='"prop"'),
                            ValueCheck(name="[1]", summary='"something"'),
                        ],
                    ),
                    ValueCheck(
                        name="[PropertyValues]",
                        summary="size=2",
                        children=[
                            ValueCheck(name="[0]", value="false"),
                            ValueCheck(name="[1]", value="123"),
                        ],
                    ),
                ],
            ),
        )
