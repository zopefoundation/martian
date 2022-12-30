"""Martian-specific directives"""

from martian.directive import CLASS
from martian.directive import MODULE
from martian.directive import MULTIPLE
from martian.directive import ONCE
from martian.directive import ONCE_NOBASE
from martian.directive import Directive
from martian.directive import MarkerDirective
from martian.directive import MultipleTimesDirective
from martian.directive import validateClass
from martian.error import GrokImportError


class component(Directive):
    scope = CLASS
    store = ONCE
    default = None
    validate = validateClass


class directive(MultipleTimesDirective):
    scope = CLASS

    def validate(self, directive, *args, **kw):
        try:
            if issubclass(directive, Directive):
                return
        except TypeError:
            # directive is not a class, so error too
            pass
        raise GrokImportError(
            "The '{}' directive can only be called with a directive.".format(
                self.name))

    def factory(self, directive, *args, **kw):
        return directive.bind(*args, **kw)


class priority(Directive):
    scope = CLASS
    store = ONCE
    default = 0


class baseclass(MarkerDirective):
    """Marker directive. Declares that a subclass of an otherwise automatically
    configured component should not be registered, and that it serves as a base
    class instead.
    """
    scope = CLASS
    store = ONCE_NOBASE


class ignore(Directive):
    """Allow to ignore a name in a module.
    """
    scope = MODULE
    store = MULTIPLE
