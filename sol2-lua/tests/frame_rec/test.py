import testlib
from testlib import ValueCheck, ChildrenUnordered, ChildrenStartsWith
import re


class TestFrameRec(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
