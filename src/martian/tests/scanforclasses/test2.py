# this is a module has a single Context subclass in it.
# this module is used in a scan_for_context.txt test.

import os
from martian.tests.scanforclasses import Context

foo = "Bar"

class Qux(object):
    pass

class Hallo:
    pass

class MyContext(Context):
    pass

qux = Qux()
hallo = Hallo()
mycontext = MyContext()
