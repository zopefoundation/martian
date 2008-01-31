import sys

from zope.interface.interfaces import IInterface

from martian import util
from martian.error import GrokImportError

# ONCE or MULTIPLE
ONCE = object()
MULTIPLE = object()

# arguments
SINGLE_ARG = object()
NO_ARG = object()
OPTIONAL_ARG = object()

_SENTINEL = object()
_USE_DEFAULT = object()

class ClassScope(object):
    description = 'class'
    
    def check(self, frame):
        return (util.frame_is_class(frame) and
                not is_fake_module(frame))

CLASS = ClassScope()

class ClassOrModuleScope(object):
    description = 'class or module'

    def check(self, frame):
        return (util.frame_is_class(frame) or
                util.frame_is_module(frame))

CLASS_OR_MODULE = ClassOrModuleScope()

class Directive(object):
    def __init__(self, namespace, name, scope, times, default,
                 validate=None, arg=SINGLE_ARG):
        self.namespace = namespace
        self.name = name
        self.scope = scope
        self.times = times
        self.default = default
        self.validate = validate
        self.arg = arg

    def __call__(self, value=_SENTINEL):            
        name = self.namespaced_name()

        if self.arg is NO_ARG:
            if value is _SENTINEL:
                value = True
            else:
                raise GrokImportError("%s accepts no arguments." % name)
        elif self.arg is SINGLE_ARG:
            if value is _SENTINEL:
                raise GrokImportError("%s requires a single argument." % name)
        elif self.arg is OPTIONAL_ARG:
            if value is _SENTINEL:
                value = _USE_DEFAULT

        if self.validate is not None:
            self.validate(name, value)

        frame = sys._getframe(1)
        if not self.scope.check(frame):
            raise GrokImportError("%s can only be used on %s level." %
                                  (name, self.scope.description))
        if self.times is ONCE:
            if name in frame.f_locals:
                raise GrokImportError("%s can only be called once per %s." %
                                      (name, self.scope.description))
            frame.f_locals[name] = value
        elif self.times is MULTIPLE:
            values = frame.f_locals.get(name, [])
            values.append(value)
            frame.f_locals[name] = values
        else:
            assert False, "Unknown value for times: %" % self.times

    def get(self, component, module=None):
        name = self.namespaced_name()
        value = getattr(component, name, _USE_DEFAULT)
        if value is _USE_DEFAULT and module is not None:
            value = getattr(module, name, _USE_DEFAULT)
        if value is _USE_DEFAULT:
            return self.get_default(component)
        return value

    def get_default(self, component):
        if callable(self.default):
            return self.default(component)
        return self.default

    def namespaced_name(self):
        return self.namespace + '.' + self.name

def validateText(name, value):
    if util.not_unicode_or_ascii(value):
        raise GrokImportError("%s can only be called with unicode or ASCII." %
                              name)

def validateInterfaceOrClass(name, value):
    if not (IInterface.providedBy(value) or util.isclass(value)):
        raise GrokImportError("%s can only be called with a class or "
                              "interface." %
                              name)


def validateInterface(name, value):
    if not (IInterface.providedBy(value)):
        raise GrokImportError("%s can only be called with an interface." %
                              name)

    
# this here only for testing purposes, which is a bit unfortunate
# but makes the tests a lot clearer for module-level directives
# also unfortunate that fake_module needs to be defined directly
# in the fake module being tested and not in the FakeModule base class;
# the system cannot find it on the frame if it is in the base class.
def is_fake_module(frame):
    return frame.f_locals.has_key('fake_module')
