import types, inspect

from zope.interface import implementer

from martian.interfaces import IGrokker, IMultiGrokker
from martian import util, scan
from martian.components import (GrokkerBase, ClassGrokker, InstanceGrokker,
                                GlobalGrokker)
from martian.error import GrokError
from martian.martiandirective import component, priority
from martian.compat3 import CLASS_TYPES

@implementer(IMultiGrokker)
class MultiGrokkerBase(GrokkerBase):

    def register(self, grokker):
        raise NotImplementedError

    def grok(self, name, obj, **kw):
        grokked_status = False

        for g, name, obj in self.grokkers(name, obj):
            grokked = g.grok(name, obj, **kw)
            if grokked not in (True, False):
                raise GrokError(
                    "%r returns %r instead of True or False." %
                    (g, grokked), None)
            if grokked:
                grokked_status = True

        return grokked_status

    def clear(self):
        raise NotImplementedError

    def grokkers(self, name, obj):
        raise NotImplementedError

def _grokker_sort_key(args):
    """Helper function to calculate sort order of grokker.
    """
    grokker, name, obj = args
    return priority.bind().get(grokker)
    
class ModuleGrokker(MultiGrokkerBase):

    def __init__(self, grokker=None, prepare=None, finalize=None):
        if grokker is None:
            grokker = MultiGrokker()
        self._grokker = grokker
        self.prepare = prepare
        self.finalize = finalize

    def register(self, grokker):
        self._grokker.register(grokker)

    def clear(self):
        self._grokker.clear()

    def grok(self, name, module, **kw):
        grokked_status = False

        # prepare module grok - this can also influence the kw dictionary
        if self.prepare is not None:
            self.prepare(name, module, kw)

        # sort grokkers by priority
        grokkers = sorted(self.grokkers(name, module),
                          key=_grokker_sort_key,
                          reverse=True)

        for g, name, obj in grokkers:
            grokked = g.grok(name, obj, **kw)
            if grokked not in (True, False):
                raise GrokError(
                    "%r returns %r instead of True or False." %
                    (g, grokked), None)
            if grokked:
                grokked_status = True

        # finalize module grok
        if self.finalize is not None:
            self.finalize(name, module, kw)

        return grokked_status

    def grokkers(self, name, module):
        grokker = self._grokker
        # get any global grokkers
        for t in grokker.grokkers(name, module):
            yield t

        # try to grok everything in module
        for name in dir(module):
            if '.' in name:
                # This must be a module-level variable that couldn't
                # have been set by the developer.  It must have been a
                # module-level directive.
                continue
            obj = getattr(module, name)
            if not util.defined_locally(obj, module.__name__):
                continue
            if util.is_baseclass(obj):
                continue
            for t in grokker.grokkers(name, obj):
                yield t

class MultiInstanceOrClassGrokkerBase(MultiGrokkerBase):

    def __init__(self):
        self.clear()

    def register(self, grokker):
        key = component.bind().get(grokker)
        grokkers = self._grokkers.setdefault(key, [])
        for g in grokkers:
            if g.__class__ is grokker.__class__:
                return
        grokkers.append(grokker)

    def clear(self):
        self._grokkers = {}

    def grokkers(self, name, obj):
        used_grokkers = set()
        for base in self.get_bases(obj):
            grokkers = self._grokkers.get(base)
            if grokkers is None:
                continue
            for grokker in grokkers:
                if grokker not in used_grokkers:
                    yield grokker, name, obj
                    used_grokkers.add(grokker)

class MultiInstanceGrokker(MultiInstanceOrClassGrokkerBase):
    def get_bases(self, obj):
        return inspect.getmro(obj.__class__)

class MultiClassGrokker(MultiInstanceOrClassGrokkerBase):
    def get_bases(self, obj):
        if type(obj) is types.ModuleType:
            return []
        return inspect.getmro(obj)

class MultiGlobalGrokker(MultiGrokkerBase):

    def __init__(self):
        self.clear()

    def register(self, grokker):
        for g in self._grokkers:
            if grokker.__class__ is g.__class__:
                return
        self._grokkers.append(grokker)

    def clear(self):
        self._grokkers = []

    def grokkers(self, name, module):
        for grokker in self._grokkers:
            yield grokker, name, module

class MultiGrokker(MultiGrokkerBase):

    def __init__(self):
        self.clear()

    def register(self, grokker):
        if isinstance(grokker, InstanceGrokker):
            self._multi_instance_grokker.register(grokker)
        elif isinstance(grokker, ClassGrokker):
            self._multi_class_grokker.register(grokker)
        elif isinstance(grokker, GlobalGrokker):
            self._multi_global_grokker.register(grokker)
        else:
            assert 0, "Unknown type of grokker: %r" % grokker

    def clear(self):
        self._multi_instance_grokker = MultiInstanceGrokker()
        self._multi_class_grokker = MultiClassGrokker()
        self._multi_global_grokker = MultiGlobalGrokker()

    def grokkers(self, name, obj):
        if isinstance(obj, CLASS_TYPES):
            return self._multi_class_grokker.grokkers(name, obj)
        elif isinstance(obj, types.ModuleType):
            return self._multi_global_grokker.grokkers(name, obj)
        else:
            return self._multi_instance_grokker.grokkers(name, obj)

class MetaMultiGrokker(MultiGrokker):
    """Multi grokker which comes pre-registered with meta-grokkers.
    """
    def clear(self):
        super(MetaMultiGrokker, self).clear()
        # bootstrap the meta-grokkers
        self.register(ClassMetaGrokker(self))
        self.register(InstanceMetaGrokker(self))
        self.register(GlobalMetaGrokker(self))

def grok_dotted_name(dotted_name, grokker, exclude_filter=None,
                     ignore_nonsource=True, **kw):
    module_info = scan.module_info_from_dotted_name(dotted_name, exclude_filter,
                                                    ignore_nonsource)
    grok_package(module_info, grokker, **kw)

def grok_package(module_info, grokker, **kw):
    grok_module(module_info, grokker, **kw)
    for sub_module_info in module_info.getSubModuleInfos():
        grok_package(sub_module_info, grokker, **kw)

def grok_module(module_info, grokker, **kw):
    grokker.grok(module_info.dotted_name, module_info.getModule(),
                 module_info=module_info, **kw)

# deep meta mode here - we define grokkers that can pick up the
# three kinds of grokker: ClassGrokker, InstanceGrokker and ModuleGrokker
class MetaGrokker(ClassGrokker):
    def __init__(self, multi_grokker):
        """multi_grokker - the grokker to register grokkers with.
        """
        self.multi_grokker = multi_grokker

    def grok(self, name, obj, **kw):
        self.multi_grokker.register(obj())
        return True

class ClassMetaGrokker(MetaGrokker):
    component(ClassGrokker)

class InstanceMetaGrokker(MetaGrokker):
    component(InstanceGrokker)

class GlobalMetaGrokker(MetaGrokker):
    component(GlobalGrokker)

class GrokkerRegistry(ModuleGrokker):
    def __init__(self):
        super(GrokkerRegistry, self).__init__(MetaMultiGrokker())
