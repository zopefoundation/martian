(Edge-case) tests of Martian core components
============================================

ModuleGrokker ignores values set by directives
----------------------------------------------

Consider the following module-level directive:

  >>> import martian
  >>> class store(martian.Directive):
  ...     scope = martian.MODULE
  ...     store = martian.ONCE
  ...
  >>> store.__module__ = 'somethingelse'  # just so that it isn't __builtin__

Now let's look at a module that contains a simple function and a call
to the directive defined above:

  >>> class module_with_directive(FakeModule):
  ...     fake_module = True
  ...
  ...     def some_function():
  ...         return 11
  ...
  ...     store(some_function)
  ...
  >>> from martiantest.fake import module_with_directive

Now imagine we have the following grokker for functions:

  >>> import types
  >>> class FunctionGrokker(martian.InstanceGrokker):
  ...     martian.component(types.FunctionType)
  ...     def grok(self, name, obj, **kw):
  ...         print('%s %s' % (name, obj()))
  ...         return True
  ...
  >>> module_grokker = martian.ModuleGrokker()
  >>> module_grokker.register(FunctionGrokker())

and let it loose on the module, we see that it will only find functions
set by regular variable assignment, not the ones stored by the
directive:

  >>> module_grokker.grok('module_with_directive', module_with_directive)
  some_function 11
  True

Directive scope and default edge cases
--------------------------------------

  >>> from martian import Directive, CLASS_OR_MODULE, CLASS, MODULE
  >>> from martian import ONCE 

MODULE scope directive on a module, with no explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = MODULE
  ...     store = ONCE  
  >>> class module_no_explicit_value(FakeModule):
  ...     fake_module = True
  >>> from martiantest.fake import module_no_explicit_value
  >>> mydir.bind().get(module_no_explicit_value) is None
  True

MODULE scope directive on a module, with an explicit value::

  >>> class mydir2(martian.Directive):
  ...     scope = MODULE
  ...     store = ONCE  
  >>> class module_with_explicit_value(FakeModule):
  ...     fake_module = True
  ...     mydir2('the explicit value')
  >>> from martiantest.fake import module_with_explicit_value
  >>> mydir2.bind().get(module_with_explicit_value)
  'the explicit value'

MODULE scope directive on a module, with no explicit value, with a custom default::

  >>> class mydir(martian.Directive):
  ...     scope = MODULE
  ...     store = ONCE  
  >>> class module_custom_default(FakeModule):
  ...     fake_module = True
  >>> from martiantest.fake import module_custom_default
  >>> def custom(component, module, **data):
  ...     return 'a custom default value'
  >>> mydir.bind(get_default=custom).get(module_custom_default)
  'a custom default value'
 
CLASS scope directive on a class, with no explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS
  ...     store = ONCE  
  >>> class module_get_from_class_no_explicit(FakeModule):
  ...     class MyClass(object):
  ...         pass
  >>> from martiantest.fake import module_get_from_class_no_explicit
  >>> mydir.bind().get(module_get_from_class_no_explicit.MyClass) is None
  True

CLASS scope directive on an instance, with no explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS
  ...     store = ONCE  
  >>> class module_get_from_instance_no_explicit(FakeModule):
  ...     class MyClass(object):
  ...         pass
  ...     obj = MyClass()
  >>> from martiantest.fake import module_get_from_instance_no_explicit
  >>> mydir.bind().get(module_get_from_instance_no_explicit.obj) is None
  True

CLASS scope directive on a class, with an explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS
  ...     store = ONCE  
  >>> class module_get_from_class_with_explicit(FakeModule):
  ...     class MyClass(object):
  ...         mydir('explicitly set')
  >>> from martiantest.fake import module_get_from_class_with_explicit
  >>> mydir.bind().get(module_get_from_class_with_explicit.MyClass)
  'explicitly set'

CLASS scope directive on an instance, with an explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS
  ...     store = ONCE  
  >>> class module_get_from_instance_with_explicit(FakeModule):
  ...     class MyClass(object):
  ...         mydir('explicitly set')
  ...     obj = MyClass()
  >>> from martiantest.fake import module_get_from_instance_with_explicit
  >>> mydir.bind().get(module_get_from_instance_with_explicit.obj)
  'explicitly set'

CLASS scope directive on a class, with a custom default::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS
  ...     store = ONCE  
  >>> class module_get_from_class_with_custom(FakeModule):
  ...     class MyClass(object):
  ...         pass
  >>> from martiantest.fake import module_get_from_class_with_custom
  >>> def custom_get_default(component, module, **data):
  ...     return 'custom default'
  >>> mydir.bind(get_default=custom_get_default).get(
  ...     module_get_from_class_with_custom.MyClass)
  'custom default'

CLASS scope directive on an instance, with a custom default::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS
  ...     store = ONCE  
  >>> class module_get_from_instance_with_custom(FakeModule):
  ...     class MyClass(object):
  ...         pass
  ...     obj = MyClass()
  >>> from martiantest.fake import module_get_from_instance_with_custom
  >>> mydir.bind(get_default=custom_get_default).get(
  ...     module_get_from_instance_with_custom.obj)
  'custom default'

CLASS_OR_MODULE scope directive on a module, with no explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS_OR_MODULE
  ...     store = ONCE  
  >>> class module(FakeModule):
  ...     fake_module = True
  ...     pass
  >>> from martiantest.fake import module
  >>> mydir.bind().get(module) is None
  True

CLASS_OR_MODULE scope directive on a class, with no explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS_OR_MODULE
  ...     store = ONCE  
  >>> class module(FakeModule):
  ...     fake_module = True
  ...     class MyClass(object):
  ...         pass
  >>> from martiantest.fake import module
  >>> mydir.bind().get(module.MyClass) is None
  True

CLASS_OR_MODULE scope directive on an instance, with no explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS_OR_MODULE
  ...     store = ONCE  
  >>> class module(FakeModule):
  ...     fake_module = True
  ...     class MyClass(object):
  ...         pass
  ...     obj = MyClass()
  >>> from martiantest.fake import module
  >>> mydir.bind().get(module.obj) is None
  True

CLASS_OR_MODULE scope directive on a module, with an explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS_OR_MODULE
  ...     store = ONCE  
  >>> class module(FakeModule):
  ...     fake_module = True
  ...     mydir('explicitly set, see?')
  >>> from martiantest.fake import module
  >>> mydir.bind().get(module)
  'explicitly set, see?'

CLASS_OR_MODULE scope directive on a class, with an explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS_OR_MODULE
  ...     store = ONCE  
  >>> class module(FakeModule):
  ...     fake_module = True
  ...     class MyClass(object):
  ...         mydir('explicitly set, see?')
  >>> from martiantest.fake import module
  >>> mydir.bind().get(module.MyClass)
  'explicitly set, see?'

CLASS_OR_MODULE scope directive on an instance, with an explicit value::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS_OR_MODULE
  ...     store = ONCE  
  >>> class module(FakeModule):
  ...     fake_module = True
  ...     class MyClass(object):
  ...         mydir('explicitly set, see?')
  ...     obj = MyClass()
  >>> from martiantest.fake import module
  >>> mydir.bind().get(module.obj)
  'explicitly set, see?'

CLASS_OR_MODULE scope directive on a module, with a custom default::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS_OR_MODULE
  ...     store = ONCE  
  >>> class module(FakeModule):
  ...     fake_module = True
  >>> from martiantest.fake import module
  >>> mydir.bind(get_default=custom_get_default).get(module)
  'custom default'

CLASS_OR_MODULE scope directive on a class, with a custom default::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS_OR_MODULE
  ...     store = ONCE  
  >>> class module(FakeModule):
  ...     fake_module = True
  ...     class MyClass(object):
  ...         pass
  >>> from martiantest.fake import module
  >>> mydir.bind(get_default=custom_get_default).get(module.MyClass)
  'custom default'

CLASS_OR_MODULE scope directive on an instance, with a custom default::

  >>> class mydir(martian.Directive):
  ...     scope = CLASS_OR_MODULE
  ...     store = ONCE  
  >>> class module(FakeModule):
  ...     fake_module = True
  ...     class MyClass(object):
  ...         pass
  ...     obj = MyClass()
  >>> from martiantest.fake import module
  >>> mydir.bind(get_default=custom_get_default).get(module.obj)
  'custom default'
  
  CLASS_OR_MODULE scope directive on the module, with inheritance::
  
  >>> class mydir(martian.Directive):
  ...     scope = CLASS_OR_MODULE
  ...     store = ONCE
  >>> class module_b(FakeModule):
  ...     fake_module = True
  ...     mydir('a value')
  ...     class B(object):
  ...         pass
  >>> from martiantest.fake import module_b  
  >>> class module_a(FakeModule):
  ...     fake_module = True
  ...     class A(module_b.B):
  ...         pass
  >>> from martiantest.fake import module_a
  >>> mydir.bind(get_default=custom_get_default).get(module_a.A)
  'a value'

