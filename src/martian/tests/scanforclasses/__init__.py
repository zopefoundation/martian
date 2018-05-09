from zope.interface import Interface, implementer


class IContext(Interface):
    pass


@implementer(IContext)
class Context(object):
    pass
