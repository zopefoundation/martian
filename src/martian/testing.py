import sys
from types import ModuleType

def fake_import(fake_module):
    module_name = 'martiantest.fake.' + fake_module.__name__
    module = ModuleType(module_name)
    module_name_parts = module_name.split('.')
    module.__file__ =  '/' + '/'.join(module_name_parts)
    
    glob = {}
    for name in dir(fake_module):
        if name.startswith('__') and '.' not in name:
            continue
        obj = getattr(fake_module, name)
        glob[name] = obj
        try:
            obj = obj.im_func
        except AttributeError:
            pass
        __module__ = None
        try:
            __module__ == obj.__dict__.get('__module__')
        except AttributeError:
            try:
                __module__ = obj.__module__
            except AttributeError:
                pass
        if __module__ is None or __module__ == '__builtin__':
            try:
                obj.__module__ = module.__name__
            except AttributeError:
                pass
        setattr(module, name, obj)

    # provide correct globals for functions
    for name in dir(module):
        if name.startswith('__'):
            continue
        obj = getattr(module, name)
        try:
            code = obj.func_code
            new_func = new.function(code, glob, name)
            new_func.__module__ = module.__name__
            setattr(module, name, new_func)
            glob[name] = new_func
        except AttributeError:
            pass

    if not 'martiantest' in sys.modules:
        sys.modules['martiantest'] = ModuleType('martiantest')
        sys.modules['martiantest.fake'] = ModuleType('martiantest.fake')
        sys.modules['martiantest'].fake = sys.modules['martiantest.fake']

    sys.modules[module_name] = module
    setattr(sys.modules['martiantest.fake'], module_name.split('.')[-1],
            module)
    
    return module

class FakeModuleMetaclass(type):
    def __init__(cls, classname, bases, dict_):
        fake_import(cls)
        return type.__init__(cls, classname, bases, dict_)

if sys.version_info[0] < 3:
    class FakeModule(object):
        __metaclass__ = FakeModuleMetaclass
else:
    class FakeModule(object, metaclass = FakeModuleMetaclass):
        pass


class FakeModuleObjectMetaclass(type):
    """ Base metaclass to replace object in a fake Module.
        In python 3 we need to change the class name for
        inner classes. So all test will run in python 2 and 3.
        
        Without this class the name of fakemodule will be
        shown double in the class name, like this:
        <class 'martiantest.fake.basemodule.basemodule.A'>
        If this class name is returned, the doctest will fail.
    """

    def __init__(cls, classname, bases, dict_):
        normalname = cls.__qualname__.split('.')[-1:][0]
        dict_['__qualname__'] = normalname
        cls.__qualname__ = dict_['__qualname__']
        return type.__init__(cls, classname, bases, dict_)


if sys.version_info[0] < 3:
    class FakeModuleObject(object):
        pass
else:
    class FakeModuleObject(object, metaclass = FakeModuleObjectMetaclass):
        pass

