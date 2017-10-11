import doctest
import re
import unittest

from zope.testing import renormalizing

from martian.testing import FakeModule
from martian.testing import FakeModuleObject


optionflags = (doctest.NORMALIZE_WHITESPACE
               | doctest.ELLIPSIS
               | doctest.IGNORE_EXCEPTION_DETAIL)

globs = dict(FakeModule=FakeModule,
             object=FakeModuleObject)

checker = renormalizing.RENormalizing([
    (re.compile(r'<builtins\.'), r'<'),
    (re.compile(r'<__builtin__\.'), r'<'),
])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite('README.rst',
                             package='martian',
                             globs=globs,
                             checker=checker,
                             optionflags=optionflags),
        doctest.DocFileSuite('scan.rst',
                             package='martian',
                             optionflags=optionflags),
        doctest.DocFileSuite('directive.rst',
                             package='martian',
                             globs=globs,
                             optionflags=optionflags,
                             encoding='utf-8'),
        doctest.DocFileSuite('core.rst',
                             package='martian',
                             globs=globs,
                             optionflags=optionflags),
        doctest.DocFileSuite('edgecase.rst',
                             package='martian',
                             globs=globs,
                             optionflags=optionflags),
        doctest.DocFileSuite('scan_for_classes.rst',
                             package='martian.tests',
                             optionflags=optionflags),
        doctest.DocFileSuite('public_methods_from_class.rst',
                             package='martian.tests',
                             optionflags=optionflags),
        doctest.DocFileSuite('context.rst',
                             package='martian',
                             globs=globs,
                             optionflags=optionflags),
    ])
    return suite
