"""Martian-specific directives"""

from martian.directive import (Directive, MultipleTimesDirective,
                               CLASS, ONCE, validateClass)
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
        raise GrokImportError("The '%s' directive can only be called with "
                              "a directive." % self.name)

    def factory(self, directive, *args, **kw):
        return directive.bind(*args, **kw)

class priority(Directive):
    scope = CLASS
    store = ONCE
    default = 0


