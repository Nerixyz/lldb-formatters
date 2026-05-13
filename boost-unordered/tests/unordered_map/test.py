import testlib
from testlib import ValueCheck
import re
from lldb import SBValue


class TestBoostUnorderedMap(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self._check_map(self.frame().FindVariable("map"))
        self._check_multimap(self.frame().FindVariable("multimap"))

        it_check = ValueCheck(
            summary="",
            children=[
                ValueCheck(name="first", summary='"6"'),
                ValueCheck(name="second", value="33"),
            ],
        )
        self.assertVarPath("uit", it_check)
        self.assertVarPath("uend", ValueCheck(summary="end", children=[]))
        self.assertVarPath("uit", it_check)
        self.assertVarPath("uend", ValueCheck(summary="end", children=[]))

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

    def _check_multimap(self, map: SBValue):
        self.assertEqual(map.GetSummary(), "size=10")
        self.assertEqual(map.GetNumChildren(), 10)
        name_re = re.compile(r"^\[\d\]+$")
        d = set()
        for i in range(map.GetNumChildren()):
            c = map.GetChildAtIndex(i)
            k = (
                c.GetChildMemberWithName("first").GetSummary(),
                c.GetChildMemberWithName("second").GetValueAsUnsigned(),
            )
            d.add(k)
            self.assertMatch(name_re, c.GetName())

        self.assertEqual(
            d,
            {
                ('"0"', 0),
                ('"0"', 0 + 1),
                ('"2"', 11),
                ('"2"', 11 + 1),
                ('"4"', 22),
                ('"4"', 22 + 1),
                ('"6"', 33),
                ('"6"', 33 + 1),
                ('"8"', 44),
                ('"8"', 44 + 1),
            },
        )
