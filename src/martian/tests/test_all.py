import unittest
import manuel.testing
import manuel.isolation
import manuel.doctest
import manuelpi.fakemodule
from zope.testing import doctest

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

def test_suite():
    tests = ['../README.txt', '../scan.txt', '../directive.txt',
             '../core.txt', '../edgecase.txt', 'scan_for_classes.txt',
             'public_methods_from_class.txt', '../context.txt']

    m = manuel.doctest.Manuel(optionflags=optionflags)
    m += manuel.isolation.Manuel()
    m += manuelpi.fakemodule.Manuel()

    return manuel.testing.TestSuite(m, *tests)
