import doctest
import re
import unittest

from zope.testing import renormalizing

from martian.testing import FakeModule
from martian.testing import FakeModuleObject


optionflags = (doctest.NORMALIZE_WHITESPACE
               + doctest.ELLIPSIS
               + doctest.IGNORE_EXCEPTION_DETAIL)

globs = dict(FakeModule=FakeModule,
             object=FakeModuleObject)

checker = renormalizing.RENormalizing([
    (re.compile(r'<builtins\.'), r'<'),
    (re.compile(r'<__builtin__\.'), r'<'),
])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite('README.txt',
                             package='martian',
                             globs=globs,
                             checker=checker,
                             optionflags=optionflags),
        doctest.DocFileSuite('scan.txt',
                             package='martian',
                             optionflags=optionflags),
        doctest.DocFileSuite('directive.txt',
                             package='martian',
                             globs=globs,
                             optionflags=optionflags,
                             encoding='utf-8'),
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
        doctest.DocFileSuite('context.txt',
                             package='martian',
                             globs=globs,
                             optionflags=optionflags),
    ])
    return suite
