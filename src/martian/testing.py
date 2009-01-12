import new
import sys

def fake_import(fake_module):
    module_name = 'martiantest.fake.' + fake_module.__name__
    module = new.module(module_name)
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
        sys.modules['martiantest'] = new.module('martiantest')
        sys.modules['martiantest.fake'] = new.module('martiantest.fake')
        sys.modules['martiantest'].fake = sys.modules['martiantest.fake']

    sys.modules[module_name] = module
    setattr(sys.modules['martiantest.fake'], module_name.split('.')[-1],
            module)
    
    return module

class FakeModuleMetaclass(type):
    def __init__(cls, classname, bases, dict_):
        fake_import(cls)
        return type.__init__(cls, classname, bases, dict_)

class FakeModule(object):
    __metaclass__ = FakeModuleMetaclass
