import sys
import inspect

from zope.interface.interfaces import IInterface
from zope.interface.interface import TAGGED_DATA

from martian import util
from martian.error import GrokImportError, GrokError
from martian import scan
from martian import compat3

UNKNOWN = object()
_unused = object()


class StoreOnce(object):

    def set(self, locals_, directive, value):
        if directive.dotted_name() in locals_:
            raise GrokImportError(
                "The '%s' directive can only be called once per %s." %
                (directive.name, directive.scope.description))
        locals_[directive.dotted_name()] = value

    def get(self, directive, component, default):
        return getattr(component, directive.dotted_name(), default)

    def setattr(self, context, directive, value):
        setattr(context, directive.dotted_name(), value)


ONCE = StoreOnce()


class StoreOnceGetFromThisClassOnly(StoreOnce):

    def get(self, directive, component, default):
        return component.__dict__.get(directive.dotted_name(), default)


ONCE_NOBASE = StoreOnceGetFromThisClassOnly()


class StoreMultipleTimes(StoreOnce):

    def get(self, directive, component, default):
        if getattr(component, directive.dotted_name(), default) is default:
            return default

        if getattr(component, 'mro', None) is None:
            return getattr(component, directive.dotted_name())

        result = []
        for base in reversed(component.mro()):
            list = getattr(base, directive.dotted_name(), default)
            if list is not default and list not in result:
                result.append(list)

        result_flattened = []
        for entry in result:
            result_flattened.extend(entry)
        return result_flattened

    def set(self, locals_, directive, value):
        values = locals_.setdefault(directive.dotted_name(), [])
        values.append(value)


MULTIPLE = StoreMultipleTimes()


class StoreMultipleTimesNoBase(StoreMultipleTimes):

    def get(self, directive, component, default):
        return component.__dict__.get(directive.dotted_name(), default)


MULTIPLE_NOBASE = StoreMultipleTimesNoBase()


class StoreDict(StoreOnce):

    def get(self, directive, component, default):
        if getattr(component, directive.dotted_name(), default) is default:
            return default

        if getattr(component, 'mro', None) is None:
            return getattr(component, directive.dotted_name())

        result = {}
        for base in reversed(component.mro()):
            mapping = getattr(base, directive.dotted_name(), default)
            if mapping is not default:
                result.update(mapping)
        return result

    def set(self, locals_, directive, value):
        values_dict = locals_.setdefault(directive.dotted_name(), {})
        try:
            key, value = value
        except (TypeError, ValueError):
            raise GrokImportError(
                "The factory method for the '%s' directive should return a "
                "key-value pair." % directive.name)
        values_dict[key] = value


DICT = StoreDict()


class TaggedValueStoreOnce(StoreOnce):
    """Stores the directive value in a interface tagged value.
    """

    def get(self, directive, component, default):
        return component.queryTaggedValue(directive.dotted_name(), default)

    def set(self, locals_, directive, value):
        if directive.dotted_name() in locals_:
            raise GrokImportError(
                "The '%s' directive can only be called once per %s." %
                (directive.name, directive.scope.description))
        # Make use of the implementation details of interface tagged
        # values.  Instead of being able to call "setTaggedValue()"
        # on an interface object, we only have access to the "locals"
        # of the interface object.  We inject whatever setTaggedValue()
        # would've injected.
        taggeddata = locals_.setdefault(TAGGED_DATA, {})
        taggeddata[directive.dotted_name()] = value

    def setattr(self, context, directive, value):
        context.setTaggedValue(directive.dotted_name(), value)


# for now, use scope = martian.CLASS to create directives that can
# work on interfaces (or martian.CLASS_OR_MODULE)
ONCE_IFACE = TaggedValueStoreOnce()

_USE_DEFAULT = object()


class UnknownError(GrokError):
    pass


def _default(mro, get_default):
    """Apply default rule to list of classes in mro.
    """
    error = None
    for base in mro:
        module_of_base = scan.resolve(base.__module__)
        try:
            if util.is_baseclass(base):
                break
            result = get_default(base, module_of_base)
        except UnknownError as e:
            # store error if this is the first UnknownError we ran into
            if error is None:
                error = e
            result = UNKNOWN
        if result is not UNKNOWN:
            return result
    # if we haven't found a result, raise the first error we had as
    # a GrokError
    if error is not None:
        raise GrokError(compat3.str(error), error.component)
    return UNKNOWN


class ClassScope(object):
    description = 'class'

    def check(self, frame):
        return util.frame_is_class(frame) and not is_fake_module(frame)

    def get(self, directive, component, get_default):
        result = directive.store.get(directive, component, _USE_DEFAULT)
        if result is not _USE_DEFAULT:
            return result
        # We may be really dealing with an instance instead of a class.
        if not util.isclass(component):
            component = component.__class__
        return _default(inspect.getmro(component), get_default)


CLASS = ClassScope()


class ClassOrModuleScope(object):
    description = 'class or module'

    def check(self, frame):
        return util.frame_is_class(frame) or util.frame_is_module(frame)

    def get(self, directive, component, get_default):
        # look up class-level directive on this class or its bases
        # we don't need to loop through the __mro__ here as Python will
        # do it for us
        result = directive.store.get(directive, component, _USE_DEFAULT)
        if result is not _USE_DEFAULT:
            return result

        # we may be really dealing with an instance or a module here
        if not util.isclass(component):
            return get_default(component, component)

        # now we need to loop through the mro, potentially twice
        mro = inspect.getmro(component)
        # look up module-level directive for this class or its bases
        for base in mro:
            module_of_base = scan.resolve(base.__module__)
            result = directive.store.get(directive, module_of_base,
                                         _USE_DEFAULT)
            if result is not _USE_DEFAULT:
                return result
        # look up default rule for this class or its bases
        return _default(mro, get_default)


CLASS_OR_MODULE = ClassOrModuleScope()


class ModuleScope(object):
    description = 'module'

    def check(self, frame):
        return util.frame_is_module(frame) or is_fake_module(frame)

    def get(self, directive, component, get_default):
        result = directive.store.get(directive, component, _USE_DEFAULT)
        if result is not _USE_DEFAULT:
            return result
        return get_default(component, component)


MODULE = ModuleScope()


class Directive(object):

    # The BoundDirective will fallback to the directive-level default value.
    default = None

    def __init__(self, *args, **kw):
        self.name = self.__class__.__name__

        self.frame = frame = sys._getframe(1)
        if not self.scope.check(frame):
            raise GrokImportError(
                "The '%s' directive can only be used on %s level." %
                (self.name, self.scope.description))

        self.check_factory_signature(*args, **kw)

        validate = getattr(self, 'validate', None)
        if validate is not None:
            validate(*args, **kw)

        value = self.factory(*args, **kw)
        self.store.set(frame.f_locals, self, value)

    # To get a correct error message, we construct a function that has
    # the same signature as factory(), but without "self".
    def check_factory_signature(self, *arguments, **kw):
        if sys.version_info.major == 2:
            (args, varargs, varkw, defaults) = inspect.getargspec(self.factory)
        else:
            (args, varargs, varkw, defaults,
             _, __, ___) = inspect.getfullargspec(self.factory)
        argspec = inspect.formatargspec(args[1:], varargs, varkw, defaults)
        ns = dict()
        exec("def signature_checker" + argspec + ": pass", dict(), ns)
        try:
            ns['signature_checker'](*arguments, **kw)
        except TypeError as e:
            message = e.args[0]
            message = message.replace("signature_checker()", self.name)
            raise TypeError(message)

    def factory(self, value):
        return value

    @classmethod
    def dotted_name(cls):
        return cls.__module__ + '.' + cls.__name__

    @classmethod
    def set(cls, component, value):
        cls.store.setattr(component, cls, value)

    @classmethod
    def bind(cls, default=_unused, get_default=None, name=None):
        return BoundDirective(cls, default, get_default, name)


class BoundDirective(object):

    def __init__(
            self, directive, default=_unused, get_default=None, name=None):
        self.directive = directive
        self.default = default
        if name is None:
            name = directive.__name__
        self.name = name
        # Whenever the requester provides its own get_default function,
        # it'll override the default get_default.
        if get_default is not None:
            self.get_default = get_default

    def get_default(self, component, module=None, **data):
        if self.default is not _unused:
            return self.default
        # Fallback to the directive-level default value. Call the
        # ``get_default`` classmethod when it is available, else use the
        # ``default`` attribute.
        if hasattr(self.directive, 'get_default'):
            return self.directive.get_default(component, module, **data)
        return self.directive.default

    def get(self, component=None, module=None, **data):
        directive = self.directive

        def get_default(component, module):
            return self.get_default(component, module, **data)

        return directive.scope.get(
            directive, component, get_default=get_default)


class MultipleTimesDirective(Directive):
    store = MULTIPLE
    default = []


class MarkerDirective(Directive):
    store = ONCE
    default = False

    def factory(self):
        return True


def validateText(directive, value):
    if util.not_unicode_or_ascii(value):
        raise GrokImportError("The '%s' directive can only be called with "
                              "unicode or ASCII." % directive.name)


def validateInterfaceOrClass(directive, value):
    if not (IInterface.providedBy(value) or util.isclass(value)):
        raise GrokImportError("The '%s' directive can only be called with "
                              "a class or an interface." % directive.name)


def validateClass(directive, value):
    if not util.isclass(value):
        raise GrokImportError("The '%s' directive can only be called with "
                              "a class." % directive.name)


def validateInterface(directive, value):
    if not (IInterface.providedBy(value)):
        raise GrokImportError("The '%s' directive can only be called with "
                              "an interface." % directive.name)


# this here only for testing purposes, which is a bit unfortunate
# but makes the tests a lot clearer for module-level directives
# also unfortunate that fake_module needs to be defined directly
# in the fake module being tested and not in the FakeModule base class;
# the system cannot find it on the frame if it is in the base class.
def is_fake_module(frame):
    return 'fake_module' in frame.f_locals
