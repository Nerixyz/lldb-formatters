import testlib
import lldb


class TestQBasicAtomicPointer(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        v: lldb.SBValue = self.frame().GetValueForVariablePath("v")
        int_ptr: lldb.SBValue = self.frame().GetValueForVariablePath("intPtr")
        void_ptr: lldb.SBValue = self.frame().GetValueForVariablePath("voidPtr")

        v_addr = v.GetLoadAddress()
        i_addr = int(int_ptr.GetValue(), base=16)
        void_addr = int(void_ptr.GetValue(), base=16)

        self.assertEqual(v_addr, i_addr)
        self.assertEqual(v_addr, void_addr)
