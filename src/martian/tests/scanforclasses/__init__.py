from zope.interface import Interface, implements

class IContext(Interface):
    pass

class Context(object):
    implements(IContext)
