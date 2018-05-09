# this is a module has a single Context subclass in it.
# this module is used in a scan_for_context.txt test.

from zope.interface import implementer
from martian.tests.scanforclasses import IContext

foo = "Bar"


class Qux(object):
    pass


class Hallo:
    pass


@implementer(IContext)
class MyContext(object):
    pass


qux = Qux()
hallo = Hallo()
mycontext = MyContext()
