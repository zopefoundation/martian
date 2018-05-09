Context associating directives
==============================

Martian can help you implement directives that implicitly associate
with another object or class in the modules. The most common example
of this is the way Grok's ``context`` directive works.

It has the following rules:

* ``grok.context`` can be used on the class to establish the context
  class for this class.

* ``grok.context`` can be used on the module to establish the context
  class for all classes in the module that require a context. Only
  class-level ``grok.context`` use will override this.

* If there is no ``grok.context`` for the class or module, the context
  will be a class in the module that implements a special ``IContext``
  interface.

* If there are multiple possible impicit contexts, the context is
  ambiguous. This is an error.

* If there is no possible implicit context, the context cannot be
  established. This is an error too.

Let's implement a context directive with this behavior::

  >>> import martian
  >>> class context(martian.Directive):
  ...   scope = martian.CLASS_OR_MODULE
  ...   store = martian.ONCE

Let's use an explicit class context::

  >>> class A(object):
  ...   pass
  >>> class explicitclasscontext(FakeModule):
  ...    class B(object):
  ...      context(A)
  >>> from martiantest.fake import explicitclasscontext
  >>> context.bind().get(explicitclasscontext.B)
  <class 'A'>

Let's now use the directive on the module-level, explicitly::

  >>> class explicitmodulecontext(FakeModule):
  ...   context(A)
  ...   class B(object):
  ...     pass
  >>> from martiantest.fake import explicitmodulecontext
  >>> context.bind().get(explicitmodulecontext.B)
  <class 'martiantest.fake.explicitmodulecontext.A'>

XXX why does this get this put into martiantest.fake.explicitmodule? A
problem in FakeModule?

Let's see a combination of the two, to check whether context on the class
level overrides that on the module level::

  >>> class D(object):
  ...   pass
  >>> class explicitcombo(FakeModule):
  ...   context(A)
  ...   class B(object):
  ...     pass
  ...   class C(object):
  ...     context(D)
  >>> from martiantest.fake import explicitcombo
  >>> context.bind().get(explicitcombo.B)
  <class 'martiantest.fake.explicitcombo.A'>
  >>> context.bind().get(explicitcombo.C)
  <class 'D'>

So far so good. Now let's look at automatic association. Let's provide
a ``get_default`` function that associates with any class that implements
``IContext``:

  >>> from zope.interface import Interface
  >>> class IContext(Interface):
  ...    pass
  >>> get_default_context = martian.GetDefaultComponentFactory(
  ...   IContext, 'context', 'context')

We define a base class that will be automatically associated with::

  >>> from zope.interface import implementer

  >>> @implementer(IContext)
  ... class Context(object):
  ...    pass

Let's experiment whether implicit context association works::

  >>> class implicitcontext(FakeModule):
  ...    class A(Context):
  ...      pass
  ...    class B(object):
  ...      pass
  >>> from martiantest.fake import implicitcontext
  >>> context.bind(get_default=get_default_context).get(implicitcontext.B)
  <class 'martiantest.fake.implicitcontext.A'>

We now test the failure conditions.

There is no implicit context to associate with::

  >>> class noimplicitcontext(FakeModule):
  ...    class B(object):
  ...      pass
  >>> from martiantest.fake import noimplicitcontext
  >>> context.bind(get_default=get_default_context).get(noimplicitcontext.B)
  Traceback (most recent call last):
    ...
  GrokError: No module-level context for <class 'martiantest.fake.noimplicitcontext.B'>, please use the 'context' directive.

There are too many possible contexts::

  >>> class ambiguouscontext(FakeModule):
  ...   class A(Context):
  ...     pass
  ...   class B(Context):
  ...     pass
  ...   class C(object):
  ...     pass
  >>> from martiantest.fake import ambiguouscontext
  >>> context.bind(get_default=get_default_context).get(ambiguouscontext.B)
  Traceback (most recent call last):
    ...
  GrokError: Multiple possible contexts for <class 'martiantest.fake.ambiguouscontext.B'>, please use the 'context' directive.

Let's try this with inheritance, where an implicit context is provided
by a base class defined in another module::

  >>> class basemodule(FakeModule):
  ...   class A(Context):
  ...     pass
  ...   class B(object):
  ...     pass
  >>> from martiantest.fake import basemodule
  >>> class submodule(FakeModule):
  ...   class C(basemodule.B):
  ...     pass
  >>> from martiantest.fake import submodule
  >>> context.bind(get_default=get_default_context).get(submodule.C)
  <class 'martiantest.fake.basemodule.A'>

Let's try it again with an ambiguous context in this case, resolved because
there is an unambiguous context for the base class ``B``::

  >>> class basemodule2(FakeModule):
  ...   class A(Context):
  ...     pass
  ...   class B(object):
  ...     pass
  >>> from martiantest.fake import basemodule2
  >>> class submodule2(FakeModule):
  ...   class Ambiguous1(Context):
  ...     pass
  ...   class Ambiguous2(Context):
  ...     pass
  ...   class C(basemodule2.B):
  ...     pass
  >>> from martiantest.fake import submodule2
  >>> context.bind(get_default=get_default_context).get(submodule2.C)
  <class 'martiantest.fake.basemodule2.A'>

If the implicit context cannot be found in the base class either, the error
will show up for the most specific class (``C``)::

  >>> class basemodule3(FakeModule):
  ...   class B(object):
  ...     pass
  >>> from martiantest.fake import basemodule3
  >>> class submodule3(FakeModule):
  ...   class C(basemodule3.B):
  ...     pass
  >>> from martiantest.fake import submodule3
  >>> context.bind(get_default=get_default_context).get(submodule3.C)
  Traceback (most recent call last):
    ...
  GrokError: No module-level context for <class 'martiantest.fake.submodule3.C'>, please use the 'context' directive.
