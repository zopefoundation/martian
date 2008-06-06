import unittest
from zope.testing import doctest
from martian.testing import FakeModule, fake_import

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

globs = dict(FakeModule=FakeModule, fake_import=fake_import)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite('README.txt',
                             package='martian',
                             globs=globs,
                             optionflags=optionflags),
        doctest.DocFileSuite('scan.txt',
                             package='martian',
                             optionflags=optionflags),
        doctest.DocFileSuite('directive.txt',
                             package='martian',
                             globs=globs,
                             optionflags=optionflags),
        doctest.DocFileSuite('core.txt',
                             package='martian',
                             globs=globs,
                             optionflags=optionflags),
        doctest.DocFileSuite('edgecase.txt',
                             package='martian',
                             globs=globs,
                             optionflags=optionflags),
        doctest.DocFileSuite('scan_for_classes.txt',
                             package='martian.tests',
                             optionflags=optionflags),
        doctest.DocFileSuite('public_methods_from_class.txt',
                             package='martian.tests',
                             optionflags=optionflags),
        ])
    return suite
