import testlib
from testlib import ValueCheck


class TestQUuid(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath(
            "zero",
            ValueCheck(summary="00000000-0000-0000-0000-000000000000"),
        )
        self.assertVarPath(
            "uuid",
            ValueCheck(summary="12345678-1234-5678-9abc-def012345678"),
        )
