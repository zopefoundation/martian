Scanning for the context object
-------------------------------

Let's import a module that contains no ``Context`` subclass, nor classes
that implement ``IContext``::

  >>> from martian.tests.scanforclasses import IContext

We shouldn't see any classes that are contexts::

  >>> from martian.util import scan_for_classes
  >>> from martian.tests.scanforclasses import test1
  >>> list(scan_for_classes(test1, IContext))
  []

Now we look at a module with a single ``Context`` subclass::

  >>> from martian.tests.scanforclasses import test2
  >>> list(scan_for_classes(test2, IContext))
  [<class 'martian.tests.scanforclasses.test2.MyContext'>]

Now we'll look at a module with a single class that implements ``IContext``::

  >>> from martian.tests.scanforclasses import test3
  >>> list(scan_for_classes(test3, IContext))
  [<class 'martian.tests.scanforclasses.test3.MyContext'>]

Let's finish by looking at a module which defines multiple contexts::

  >>> from martian.tests.scanforclasses import test4
  >>> len(list(scan_for_classes(test4, IContext)))
  4
