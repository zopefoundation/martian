import sys

from martian import util
from martian.error import GrokImportError

NOT_FOUND = object()

# ONCE or MULTIPLE
ONCE = object()
MULTIPLE = object()

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
    def __init__(self, namespace, name, scope, times, default):
        self.namespace = namespace
        self.name = name
        self.scope = scope
        self.times = times
        self.default = default

    def __call__(self, value):
        frame = sys._getframe(1)
        name = self.namespaced_name()
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
        value = getattr(component, name, NOT_FOUND)
        if value is not NOT_FOUND:
            return value
        if module is not None:
            return getattr(module, name, self.default)
        return self.default
    
        return getattr(component, self.namespaced_name(), self.default)

    def namespaced_name(self):
        return self.namespace + '.' + self.name


# this here only for testing purposes, which is a bit unfortunate
# but makes the tests a lot clearer for module-level directives
# also unfortunate that fake_module needs to be defined directly
# in the fake module being tested and not in the FakeModule base class;
# the system cannot find it on the frame if it is in the base class.
def is_fake_module(frame):
    return frame.f_locals.has_key('fake_module')
