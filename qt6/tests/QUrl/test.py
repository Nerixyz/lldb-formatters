import testlib
from testlib import ValueCheck
import re


class TestQUrl(testlib.TestCase):
    def runTest(self):
        self.runToRegex("// break here")
        self.assertVarPath("empty", ValueCheck(summary="(null)"))
        self.assertVarPath(
            "absLocalFile",
            ValueCheck(
                summary='"file:///my/local/file.txt"',
                children=[
                    ValueCheck(name="[Scheme]", summary=re.compile(r'^u?"file"$')),
                    ValueCheck(name="[Username]", summary='u"" (null)'),
                    ValueCheck(name="[Password]", summary='u"" (null)'),
                    ValueCheck(name="[Host]", summary='u"" (null)'),
                    ValueCheck(name="[Port]", value="-1"),
                    ValueCheck(
                        name="[Path]", summary=re.compile(r'^u?"/my/local/file\.txt"$')
                    ),
                    ValueCheck(name="[Query]", summary='u"" (null)'),
                    ValueCheck(name="[Fragment]", summary='u"" (null)'),
                ],
            ),
        )
        self.assertVarPath(
            "localFile",
            ValueCheck(
                summary='"file:my/local/file.txt"',
                children=[
                    ValueCheck(name="[Scheme]", summary=re.compile(r'^u?"file"$')),
                    ValueCheck(name="[Username]", summary='u"" (null)'),
                    ValueCheck(name="[Password]", summary='u"" (null)'),
                    ValueCheck(name="[Host]", summary='u"" (null)'),
                    ValueCheck(name="[Port]", value="-1"),
                    ValueCheck(
                        name="[Path]", summary=re.compile(r'^u?"my/local/file\.txt"$')
                    ),
                    ValueCheck(name="[Query]", summary='u"" (null)'),
                    ValueCheck(name="[Fragment]", summary='u"" (null)'),
                ],
            ),
        )
        self.assertVarPath(
            "example",
            ValueCheck(
                summary='"https://example.com"',
                children=[
                    ValueCheck(name="[Scheme]", summary=re.compile(r'^u?"https"$')),
                    ValueCheck(name="[Username]", summary='u"" (null)'),
                    ValueCheck(name="[Password]", summary='u"" (null)'),
                    ValueCheck(
                        name="[Host]", summary=re.compile(r'^u?"example\.com"$')
                    ),
                    ValueCheck(name="[Port]", value="-1"),
                    ValueCheck(name="[Path]", summary='u""'),
                    ValueCheck(name="[Query]", summary='u"" (null)'),
                    ValueCheck(name="[Fragment]", summary='u"" (null)'),
                ],
            ),
        )
        self.assertVarPath(
            "allComponents",
            ValueCheck(
                summary='"https://user:pass@example.com:443/path?query#fragment"',
                children=[
                    ValueCheck(name="[Scheme]", summary=re.compile(r'^u?"https"$')),
                    ValueCheck(name="[Username]", summary=re.compile(r'^u?"user"$')),
                    ValueCheck(name="[Password]", summary=re.compile(r'^u?"pass"$')),
                    ValueCheck(
                        name="[Host]", summary=re.compile(r'^u?"example\.com"$')
                    ),
                    ValueCheck(name="[Port]", value="443"),
                    ValueCheck(name="[Path]", summary=re.compile(r'^u?"/path"$')),
                    ValueCheck(name="[Query]", summary=re.compile(r'^u?"query"$')),
                    ValueCheck(
                        name="[Fragment]", summary=re.compile(r'^u?"fragment"$')
                    ),
                ],
            ),
        )
        self.assertVarPath(
            "lessComponents",
            ValueCheck(
                summary='"https://user@example.com:443/path#fragment"',
                children=[
                    ValueCheck(name="[Scheme]", summary=re.compile(r'^u?"https"$')),
                    ValueCheck(name="[Username]", summary=re.compile(r'^u?"user"$')),
                    ValueCheck(name="[Password]", summary='u"" (null)'),
                    ValueCheck(
                        name="[Host]", summary=re.compile(r'^u?"example\.com"$')
                    ),
                    ValueCheck(name="[Port]", value="443"),
                    ValueCheck(name="[Path]", summary=re.compile(r'^u?"/path"$')),
                    ValueCheck(name="[Query]", summary='u"" (null)'),
                    ValueCheck(
                        name="[Fragment]", summary=re.compile(r'^u?"fragment"$')
                    ),
                ],
            ),
        )
