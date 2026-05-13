import testlib
from testlib import ValueCheck
import re
from lldb import SBValue


class TestBoostFoaMap(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self._check_map(self.frame().FindVariable("flat_map"))
        self._check_map(self.frame().FindVariable("node_map"))
        self._check_map(self.frame().FindVariable("cflat_map"))
        self._check_map(self.frame().FindVariable("cnode_map"))

        self.assertVarPath(
            "foit",
            ValueCheck(
                summary="",
                children=[
                    ValueCheck(name="first", summary='"6"'),
                    ValueCheck(name="second", value="33"),
                ],
            ),
        )
        self.assertVarPath("foend", ValueCheck(summary="end", children=[]))

    def _check_map(self, map: SBValue):
        self.assertEqual(map.GetSummary(), "size=5")
        self.assertEqual(map.GetNumChildren(), 5)
        name_re = re.compile(r"^\[\d\]+$")
        d = {}
        for i in range(map.GetNumChildren()):
            c = map.GetChildAtIndex(i)
            d[c.GetChildMemberWithName("first").GetSummary()] = (
                c.GetChildMemberWithName("second").GetValueAsUnsigned()
            )
            self.assertMatch(name_re, c.GetName())

        self.assertEqual(
            d,
            {
                '"0"': 0,
                '"2"': 11,
                '"4"': 22,
                '"6"': 33,
                '"8"': 44,
            },
        )
