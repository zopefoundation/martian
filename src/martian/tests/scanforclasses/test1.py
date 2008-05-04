# this is a module that has deliberately NO Context subclass, nor a class
# that implements IContext class. It is used to write a scan_for_context.txt
# test.

import os

foo = "Bar"

class Qux(object):
    pass

class Hallo:
    pass

qux = Qux()
hallo = Hallo()
