from zope.interface import Interface
from zope.interface import implementer


class IContext(Interface):
    pass


@implementer(IContext)
class Context(object):
    pass
