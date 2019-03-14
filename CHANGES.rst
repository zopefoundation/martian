CHANGES
*******

1.4 (unreleased)
================

- Nothing changed yet.


1.3.post1 (2019-03-14)
======================

- Fix rendering of PyPI page.


1.3 (2019-03-14)
================

- Add support for Python 3.7 and 3.8.


1.2 (2018-05-09)
================

- Add a new directive ``martian.ignore()`` to explicitly not grok
  something in a module::

    class Example:
        pass

    martian.ignore('Example')

- Fix the code to be pep 8 compliant.

1.1 (2018-01-25)
================

- Bypass bootstrap, add coverage to tox

- Fix ``inspect.getargspec()`` deprecation in python3


1.0 (2017-10-19)
================

- Add support for Python 3.5, 3.6, PyPy2 and PyPy3.

- Drop support for Python 2.6 and 3.3.


0.15 (2015-04-21)
=================

- compatibility for python 3
- adjust egg to work with newer version of setuptools
- Fix an encoding issue under Python-2.7 in the doctests.


0.14 (2010-11-03)
=================

Feature changes
---------------

* The computation of the default value for a directive can now be defined inside
  the directive class definition. Whenever there is a ``get_default``
  classmethod, it is used for computing the default::

      class name(Directive):
          scope = CLASS
          store = ONCE

          @classmethod
          def get_default(cls, component, module=None, **data):
             return component.__name__.lower()

  When binding the directive, the default-default behaviour can still be
  overriden by passing a ``get_default`` function::

      def another_default(component, module=None, **data):
         return component.__name__.lower()

      name.bind(get_default=another_default).get(some_component)

  Making the default behaviour intrinsic to the directive, prevents having to
  pass the ``get_default`` function over and over when getting values, for
  example in the grokkers.

0.13 (2010-11-01)
=================

Feature changes
---------------

* Ignore all __main__ modules.

* List zope.testing as a test dependency.

0.12 (2009-06-29)
=================

Feature changes
---------------

* Changes to better support various inheritance scenarios in combination with
  directives. Details follow.

* ``CLASS_OR_MODULE`` scope directives will be aware of inheritance of
  values that are defined in module-scope. Consider the following case::

    module a:
      some_directive('A')
      class Foo(object):
        pass

    module b:
      import a
      class Bar(a.Foo):
        pass

  As before, ``Foo`` will have the value ``A`` configured for it. ``Bar``,
  since it inherits from ``Foo``, will inherit this value.

* ``CLASS_OR_MODULE`` and ``CLASS`` scope directives will be aware of
  inheritance of computed default values. Consider the following case::

    module a:
      class Foo(object):
         pass

    module b:
      import a
      class Bar(a.Foo):
         pass

    def get_default(component, module, **data):
        if module.__name__ == 'a':
           return "we have a default value for module a"
        return martian.UNKNOWN

  When we now do this::

    some_directive.bind(get_default=get_default).get(b.Bar)

  We will get the value "we have a default value for module a". This
  is because when trying to compute the default value for ``Bar`` we
  returned ``martian.UNKNOWN`` to indicate the value couldn't be found
  yet. The system then looks at the base class and tries again, and in
  this case it succeeds (as the module-name is ``a``).

* ``martian.ONCE_IFACE`` storage option to allow the creation of
  directives that store their value on ``zope.interface``
  interfaces. This was originally in ``grokcore.view`` but was of
  wider usefulness.

Bugs fixed
----------

* Ignore things that look like Python modules and packages but aren't.
  These are sometimes created by editors, operating systems and
  network file systems and we don't want to confuse them.

* Ignore .pyc and .pyo files that don't have a matching .py file via
  ``module_info_from_dotted_name`` if its ``ignore_nonsource``
  parameter is ``True``.  The default is ``True``.  To revert to the
  older behavior where .pyc files were honored, pass
  ``ignore_nonsource=False``.

* Pass along ``exclude_filter`` (and the new ``ignore_nonsource``
  flag) to ModuleInfo constructor when it calls itself recursively.

* Replace ``fake_import`` to import fake modules in tests with a real
  python import statement (``from martiantest.fake import
  my_fake_module``). This works by introducing a metaclass for
  ``FakeModule`` that automatically registers it as a module. The
  irony does not escape us. This also means that
  ``martian.scan.resolve()`` will now work on fake modules.

0.11 (2008-09-24)
=================

Feature changes
---------------

* Added MULTIPLE_NOBASE option for directive store. This is like MULTIPLE
  but doesn't inherit information from the base class.

0.10 (2008-06-06)
=================

Feature changes
---------------

* Add a ``validateClass`` validate function for directives.

* Moved ``FakeModule`` and ``fake_import`` into a ``martian.testing``
  module so that they can be reused by external packages.

* Introduce new tutorial text as README.txt. The text previously in
  ``README.txt`` was rather too detailed for a tutorial, so has been
  moved into ``core.txt``.

* Introduce a ``GrokkerRegistry`` class that is a ``ModuleGrokker``
  with a ``MetaMultiGrokker`` in it. This is the convenient thing to
  instantiate to start working with Grok and is demonstrated in the
  tutorial.

* Introduced three new martian-specific directives:
  ``martian.component``, ``martian.directive`` and
  ``martian.priority``. These replace the ``component_class``,
  ``directives`` and ``priority`` class-level attributes. This way
  Grokkers look the same as what they grok. This breaks backwards
  compatibility again, but it's an easy replace operation. Note that
  ``martian.directive`` takes the directive itself as an argument, and
  then optionally the same arguments as the ``bind`` method of
  directives (``name``, ``default`` and ``get_default``). It may be
  used multiple times. Note that ``martian.baseclass`` was already a
  Martian-specific directive and this has been unchanged.

* For symmetry, add an ``execute`` method to ``InstanceGrokker``.

0.9.7 (2008-05-29)
==================

Feature changes
---------------

* Added a ``MethodGrokker`` base class for grokkers that want to grok
  methods of a class rather than the whole class itself.  It works
  quite similar to the ``ClassGrokker`` regarding directive
  definition, except that directives evaluated not only on class (and
  possibly module) level but also for each method.  That way,
  directives can also be applied to methods (as decorators) in case
  they support it.

0.9.6 (2008-05-14)
==================

Feature changes
---------------

* Refactored the ``martian.Directive`` base class yet again to allow
  more declarative (rather than imperative) usage in grokkers.
  Directives themselves no longer have a ``get()`` method nor a
  default value factory (``get_default()``).  Instead you will have to
  "bind" the directive first which is typically done in a grokker.

* Extended the ``ClassGrokker`` baseclass with a standard ``grok()``
  method that allows you to simply declare a set of directives that
  are used on the grokked classes.  Then you just have to implement an
  ``execute()`` method that will receive the data from those
  directives as keyword arguments.  This simplifies the implementation
  of class grokkers a lot.

0.9.5 (2008-05-04)
==================

* ``scan_for_classes`` just needs a single second argument specifying
  an interface. The support for scanning for subclasses directly has
  been removed as it became unnecessary (due to changes in
  grokcore.component).

0.9.4 (2008-05-04)
==================

Features changes
----------------

* Replaced the various directive base classes with a single
  ``martian.Directive`` base class:

  - The directive scope is now defined with the ``scope`` class
    attribute using one of ``martian.CLASS``, ``martian.MODULE``,
    ``martian.CLASS_OR_MODULE``.

  - The type of storage is defined with the ``store`` class attribute
    using one of ``martian.ONCE``, ``martian.MULTIPLE``,
    ``martian.DICT``.

  - Directives have now gained the ability to read the value that they
    have set on a component or module using a ``get()`` method.  The
    ``class_annotation`` and ``class_annotation_list`` helpers have
    been removed as a consequence.

* Moved the ``baseclass()`` directive from Grok to Martian.

* Added a ``martian.util.check_provides_one`` helper, in analogy to
  ``check_implements_one``.

* The ``scan_for_classes`` helper now also accepts an ``interface``
  argument which allows you to scan for classes based on interface
  rather than base classes.

Bug fixes
---------

* added dummy ``package_dotted_name`` to ``BuiltinModuleInfo``. This
  allows the grokking of views in test code using Grok's
  ``grok.testing.grok_component`` without a failure when it sets up the
  ``static`` attribute.

* no longer use the convention that classes ending in -Base will be considered
  base classes. You must now explicitly use the grok.baseclass() directive.

* The type check of classes uses isinstance() instead of type(). This means
  Grok can work with Zope 2 ExtensionClasses and metaclass programming.

0.9.3 (2008-01-26)
==================

Feature changes
---------------

* Added an OptionalValueDirective which allows the construction of
  directives that take either zero or one argument. If no arguments
  are given, the ``default_value`` method on the directive is
  called. Subclasses need to override this to return the default value
  to use.

Restructuring
-------------

* Move some util functions that were really grok-specific out of Martian
  back into Grok.

0.9.2 (2007-11-20)
==================

Bug fixes
---------

* scan.module_info_from_dotted_name() now has special behavior when it
  runs into __builtin__. Previously, it would crash with an error. Now
  it will return an instance of BuiltinModuleInfo. This is a very
  simple implementation which provides just enough information to make
  client code work. Typically this client code is test-related so that
  the module context will be __builtin__.

0.9.1 (2007-10-30)
==================

Feature changes
---------------

* Grokkers now receive a ``module_info`` keyword argument.  This
  change is completely backwards-compatible since grokkers which don't
  take ``module_info`` explicitly will absorb the extra argument in
  ``**kw``.

0.9 (2007-10-02)
=================

Feature changes
---------------

* Reverted the behaviour where modules called tests or ftests were skipped
  by default and added an API to provides a filtering function for skipping
  modules to be grokked.

0.8.1 (2007-08-13)
==================

Feature changes
---------------

* Don't grok tests or ftests modules.

Bugs fixed
----------

* Fix a bug where if a class had multiple base classes, this could end up
  in the resultant list multiple times.

0.8 (2007-07-02)
================

Feature changes
---------------

* Initial public release.
