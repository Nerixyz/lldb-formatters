import testlib
from testlib import ValueCheck
import re
from lldb import SBValue


class TestBoostUnorderedSet(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self._check_set(self.frame().FindVariable("set"))
        self._check_multiset(self.frame().FindVariable("multiset"))

        it_check = ValueCheck(summary='"6"')
        self.assertVarPath("uit", it_check)
        self.assertVarPath("uend", ValueCheck(summary="end", children=[]))
        self.assertVarPath("uit", it_check)
        self.assertVarPath("uend", ValueCheck(summary="end", children=[]))

    def _check_set(self, v: SBValue):
        self.assertEqual(v.GetSummary(), "size=5")
        self.assertEqual(v.GetNumChildren(), 5)
        name_re = re.compile(r"^\[\d\]+$")
        d = set()
        for i in range(v.GetNumChildren()):
            c = v.GetChildAtIndex(i)
            d.add(c.GetSummary())
            self.assertMatch(name_re, c.GetName())

        self.assertEqual(
            d,
            {
                '"0"',
                '"2"',
                '"4"',
                '"6"',
                '"8"',
            },
        )

    def _check_multiset(self, v: SBValue):
        self.assertEqual(v.GetSummary(), "size=10")
        self.assertEqual(v.GetNumChildren(), 10)
        name_re = re.compile(r"^\[\d\]+$")
        d = {}
        for i in range(v.GetNumChildren()):
            c = v.GetChildAtIndex(i)
            k = c.GetSummary()
            if k in d:
                d[k] += 1
            else:
                d[k] = 1
            self.assertMatch(name_re, c.GetName())

        self.assertEqual(
            d,
            {
                '"0"': 2,
                '"2"': 2,
                '"4"': 2,
                '"6"': 2,
                '"8"': 2,
            },
        )
