import testlib
from testlib import ValueCheck
import re


class TestQHostAddress(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("null", ValueCheck(summary="(invalid)"))
        self.assertVarPath(
            "ipv4",
            ValueCheck(
                summary="123.5.231.36",
                children=[
                    ValueCheck(name="[Protocol]", value="IPv4Protocol"),
                    ValueCheck(name="[ScopeID]", summary='u"" (null)'),
                ],
            ),
        )
        self.assertVarPath(
            "ipv6",
            ValueCheck(
                summary="0123:4567:89ab:cdef:1234:5678:9abc:def0",
                children=[
                    ValueCheck(name="[Protocol]", value="IPv6Protocol"),
                    ValueCheck(name="[ScopeID]", summary=re.compile(r'^u?"foobar"$')),
                ],
            ),
        )
