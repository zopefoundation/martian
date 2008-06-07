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
from martian.martiandirective import directive, component

class GrokkerBase(object):
    implements(IGrokker)
   
    def grok(self, name, obj, **kw):
        raise NotImplementedError

    
class GlobalGrokker(GrokkerBase):
    """Grokker that groks once per module.
    """

    def grok(self, name, obj, **kw):
        raise NotImplementedError
    

class ComponentGrokkerBase(GrokkerBase):
    implements(IComponentGrokker)

    def grok(self, name, obj, **kw):
        raise NotImplementedError


class ClassGrokker(ComponentGrokkerBase):
    """Grokker that groks classes in a module.
    """

    def grok(self, name, class_, module_info=None, **kw):
        module = None
        if module_info is not None:
            module = module_info.getModule()

        # Populate the data dict with information from the directives:
        for d in directive.bind().get(self.__class__):
            kw[d.name] = d.get(class_, module, **kw)
        return self.execute(class_, **kw)

    def execute(self, class_, **data):
        raise NotImplementedError


class MethodGrokker(ClassGrokker):

    def grok(self, name, class_, module_info=None, **kw):
        module = None
        if module_info is not None:
            module = module_info.getModule()

        # Populate the data dict with information from class or module
        directives = directive.bind().get(self.__class__)
        for d in directives:
            kw[d.name] = d.get(class_, module, **kw)

        # Ignore methods that are present on the component baseclass.
        basemethods = set(util.public_methods_from_class(
            component.bind().get(self.__class__)))
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
            for bound_dir in directives:
                d = bound_dir.directive
                class_value = data[bound_dir.name]
                data[bound_dir.name] = d.store.get(d, method,
                                                   default=class_value)
            results.append(self.execute(class_, method, **data))

        return max(results)

    def execute(self, class_, method, **data):
        raise NotImplementedError


class InstanceGrokker(ComponentGrokkerBase):
    """Grokker that groks instances in a module.
    """
    def grok(self, name, class_, **kw):        
        return self.execute(class_, **kw)

    def execute(self, class_, **kw):
        raise NotImplementedError

