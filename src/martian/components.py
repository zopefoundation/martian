##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope.interface import implements

from martian import util
from martian.error import GrokError
from martian.interfaces import IGrokker, IComponentGrokker

NOT_DEFINED = object()

class GrokkerBase(object):
    implements(IGrokker)

    priority = 0
    
    def grok(self, name, obj, **kw):
        raise NotImplementedError

    
class GlobalGrokker(GrokkerBase):
    """Grokker that groks once per module.
    """

    def grok(self, name, obj, **kw):
        raise NotImplementedError
    

class ComponentGrokkerBase(GrokkerBase):
    implements(IComponentGrokker)

    component_class = NOT_DEFINED

    def grok(self, name, obj, **kw):
        raise NotImplementedError


class ClassGrokker(ComponentGrokkerBase):
    """Grokker that groks classes in a module.
    """
    # Use a tuple instead of a list here to make it immutable, just to be safe
    directives = ()

    def grok(self, name, class_, module_info=None, **kw):
        module = None
        if module_info is not None:
            module = module_info.getModule()

        # Populate the data dict with information from the directives:
        for directive in self.directives:
            kw[directive.name] = directive.get(class_, module, **kw)
        return self.execute(class_, **kw)

    def execute(self, class_, **data):
        raise NotImplementedError


class MethodGrokker(ComponentGrokkerBase):
    # Use a tuple instead of a list here to make it immutable, just to be safe
    directives = ()

    def grok(self, name, class_, module_info=None, **kw):
        module = None
        if module_info is not None:
            module = module_info.getModule()

        # Populate the data dict with information from class or module
        for directive in self.directives:
            kw[directive.name] = directive.get(class_, module, **kw)

        # Ignore methods that are present on the component baseclass.
        basemethods = set(util.public_methods_from_class(self.component_class))
        methods = set(util.public_methods_from_class(class_)) - basemethods
        if not methods:
            raise GrokError("%r does not define any public methods. "
                            "Please add methods to this class to enable "
                            "its registration." % class_, class_)

        results = []
        for method in methods:
            # Directives may also be applied to methods, so let's
            # check each directive and potentially override the
            # class-level value with a value from the method *locally*.
            data = kw.copy()
            for bound_dir in self.directives:
                directive = bound_dir.directive
                class_value = data[bound_dir.name]
                data[bound_dir.name] = directive.store.get(directive, method,
                                                           default=class_value)
            results.append(self.execute(class_, method, **data))

        return max(results)

    def execute(self, class_, method, **data):
        raise NotImplementedError


class InstanceGrokker(ComponentGrokkerBase):
    """Grokker that groks instances in a module.
    """
    pass
