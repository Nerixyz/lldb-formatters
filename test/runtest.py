import argparse
import configuration
import sys
import os
import unittest
from pathlib import Path


def _exit_with(code=None):
    import lldb

    lldb.SBDebugger.Terminate()

    if code is not None:
        exit(code)


def _init_lldb(path: str):
    sys.path.insert(0, path)
    import lldb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", "-b", required=True)
    parser.add_argument("--lldb-py", required=True)
    parser.add_argument("--script", "-s", nargs="*")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("test")
    args = parser.parse_args()

    _init_lldb(args.lldb_py)

    # add common directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

    configuration.binary_path = args.binary
    configuration.scripts = args.script or []
    configuration.test_path = os.path.abspath(args.test)

    test_dir = os.path.dirname(args.test)
    test_name = os.path.splitext(os.path.basename(args.test))[0]
    sys.path.insert(0, test_dir)
    __import__(test_name)

    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromName(test_name))
    unittest.signals.installHandler()  # ctrl + c handler

    if suite.countTestCases() == 0:
        print("did not discover any matching tests")
        _exit_with(1)

    # Invoke the test runner.
    result = unittest.TextTestRunner(
        stream=sys.stderr,
        verbosity=2 if args.verbose else 0,
    ).run(suite)

    _exit_with(len(result.failures))


if __name__ == "__main__":
    main()
