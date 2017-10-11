Scanning modules
================

Martian can grok modules or packages. In order to grok packages, it
needs to scan all modules in it. The martian.scan package provides an
abstraction over packages and modules that helps with the scanning
process.

  >>> from martian.scan import module_info_from_dotted_name

We have provided a special test fixture package called stoneage that we are
going to scan, in ``martian.tests.stoneage``.

Modules
-------

The scanning module defines a class ``ModuleInfo`` that provides
information about a module or a package. Let's take a look at the
``cave`` module in the stone-age package::

  >>> module_info = module_info_from_dotted_name('martian.tests.stoneage.cave')

We get a ``ModuleInfo`` object representing the ``cave module``::

  >>> module_info
  <ModuleInfo object for 'martian.tests.stoneage.cave'>

``cave`` is a module, not a package.

  >>> module_info.isPackage()
  False

We can retrieve the name of the module::

  >>> module_info.name
  'cave'

We can also retrieve the dotted name of the module::

  >>> module_info.dotted_name
  'martian.tests.stoneage.cave'

And the dotted name of the package the module is in::

  >>> module_info.package_dotted_name
  'martian.tests.stoneage'

It is possible to get the actual module object that the ModuleInfo
object stands for, in this case the package's ``cave.py``::

  >>> module = module_info.getModule()
  >>> module
  <module 'martian.tests.stoneage.cave' from '...cave.py...'>

We can store a module-level annotation in the module::

  >>> module.__grok_foobar__ = 'GROK LOVE FOO'

The ModuleInfo object allows us to retrieve the annotation again::

  >>> module_info.getAnnotation('grok.foobar', None)
  'GROK LOVE FOO'

If a requested annotation does not exist, we get the default value::

  >>> module_info.getAnnotation('grok.barfoo', 42)
  42

A module has no sub-modules in it (only packages have this)::

  >>> module_info.getSubModuleInfos()
  []

Trying to retrieve any sub modules will give back None::

  >>> print(module_info.getSubModuleInfo('doesnotexist'))
  None

Packages
--------

Now let's scan a package::

  >>> module_info = module_info_from_dotted_name('martian.tests.stoneage')

We will get a ModuleInfo instance representing the ``stoneage`` package::

  >>> module_info
  <ModuleInfo object for 'martian.tests.stoneage'>

The object knows it is a package::

  >>> module_info.isPackage()
  True

Like with the module, we can get the package's name::

  >>> module_info.name
  'stoneage'

We can also get the package's dotted name back from it::

  >>> module_info.dotted_name
  'martian.tests.stoneage'

It is also possible to get the dotted name of the nearest package the
package resides in. This will always be itself::

  >>> module_info.package_dotted_name
  'martian.tests.stoneage'

Now let's go into the package and a few sub modules that are in it::

  >>> module_info.getSubModuleInfo('cave')
  <ModuleInfo object for 'martian.tests.stoneage.cave'>

  >>> module_info.getSubModuleInfo('hunt')
  <ModuleInfo object for 'martian.tests.stoneage.hunt'>

Trying to retrieve non-existing sub modules gives back None::

  >>> print(module_info.getSubModuleInfo('doesnotexist'))
  None

It is possible to get the actual module object that the ModuleInfo
object stands for, in this case the package's ``__init__.py``::

  >>> module = module_info.getModule()
  >>> module
  <module 'martian.tests.stoneage' from '...__init__.py...'>

A package has sub modules::

  >>> sub_modules = module_info.getSubModuleInfos()
  >>> sub_modules
  [<ModuleInfo object for 'martian.tests.stoneage.cave'>,
   <ModuleInfo object for 'martian.tests.stoneage.hunt'>,
   <ModuleInfo object for 'martian.tests.stoneage.painting'>]

Resource paths
--------------

Resources can be stored in a directory alongside a module (in their
containing package).  We can get the path to such a resource directory
using the ``getResourcePath`` method.

For packages, a resource path will be a child of the package directory:

  >>> import os.path
  >>> expected_resource_path = os.path.join(os.path.dirname(
  ...     module.__file__), 'stoneage-templates')
  >>> resource_path = module_info.getResourcePath('stoneage-templates')
  >>> resource_path == expected_resource_path
  True

For modules, a resource path will be a sibling of the module's file:

  >>> cave_module_info = module_info_from_dotted_name(
  ...    'martian.tests.stoneage.cave')
  >>> expected_resource_path = os.path.join(os.path.dirname(
  ...     cave_module_info.getModule().__file__), 'cave-templates')
  >>> resource_path = cave_module_info.getResourcePath('cave-templates')
  >>> resource_path == expected_resource_path
  True


Skipping packages and modules
-----------------------------

By default no packages and modules are skipped from the grokking
procedure to guarantee a generic behaviour::

  >>> from martian.scan import ModuleInfo, module_info_from_dotted_name
  >>> module_info = module_info_from_dotted_name(
  ...     'martian.tests.withtestspackages')
  >>> module_info
  <ModuleInfo object for 'martian.tests.withtestspackages'>
  >>> # *Will* contain the module info for the tests and ftests packages
  >>> print(module_info.getSubModuleInfos())
  [...<ModuleInfo object for 'martian.tests.withtestspackages.tests'>...]

You can, however, tell ``getSubmoduleInfos()`` to skip certain names
of packages and modules. To do that, you have to give a filter
function which takes a name and returns a boolean. Names, for which
the function returns ``True`` are skipped from the result.

For example, to get only those packages, which are *not* named 'tests'
nor 'ftests' we could do::

  >>> from martian.scan import ModuleInfo, module_info_from_dotted_name
  >>> no_tests_filter = lambda x: x in ['tests', 'ftests']
  >>> module_info = module_info_from_dotted_name(
  ...     'martian.tests.withtestsmodules', exclude_filter=no_tests_filter)
  >>> module_info
  <ModuleInfo object for 'martian.tests.withtestsmodules'>
  >>> no_tests_filter = lambda x: x in ['tests', 'ftests']
  >>> print(module_info.getSubModuleInfos())
  [<ModuleInfo object for 'martian.tests.withtestsmodules.subpackage'>]

By default __main__ packages are always ignored::

  >>> module_info = module_info_from_dotted_name(
  ...     'martian.tests.with__main__')
  >>> print(module_info.getSubModuleInfos())
  [<ModuleInfo object for 'martian.tests.with__main__.package'>]


Non-modules that look like modules
----------------------------------

Sometimes the environment (an editor or network file system, for
instance) will create a situation where there is a file or directory
that looks like a Python module or package but is in fact not really
one (file name starts with a dot, for instance). Module and package
names must be valid Python identifiers.

The package ``martian.tests.withbogusmodules`` contains only one real
module and one real package. The rest are almost right, but do not
start with an underscore and a letter and are therefore not valid. We
will see that Martian will ignore these other things::

  >>> module_info = module_info_from_dotted_name(
  ...     'martian.tests.withbogusmodules')
  >>> module_info.getSubModuleInfos()
  [<ModuleInfo object for 'martian.tests.withbogusmodules.nonbogus'>, 
   <ModuleInfo object for 'martian.tests.withbogusmodules.subpackage'>]

Packages which contain .pyc files only
--------------------------------------

When a .py file in a package is renamed, an "orphaned" .pyc object is
often left around.  By default, Martian will ignore such .pyc files:

Note: Python 3 will always store .pyc files in __pycache__ folder. So
we need force python to create a .pyc at the right place.

  >>> from py_compile import compile
  >>> from martian.tests.withpyconly import foo
  >>> c = compile(foo.__file__, foo.__file__ + 'c')
  >>> import martian.tests.withpyconly
  >>> d = os.path.abspath(os.path.dirname(martian.tests.withpyconly.__file__))
  >>> os.rename(os.path.join(d, 'foo.py'), os.path.join(d, 'foo.py_aside'))
  >>> module_info = module_info_from_dotted_name(
  ...     'martian.tests.withpyconly')
  >>> module_info.getSubModuleInfos()
  [<ModuleInfo object for 'martian.tests.withpyconly.subpackage'>]

However, if ``ignore_nonsource=False`` is passed to
``module_info_from_dotted_name`` (or friends, such as
``module_info_from_module``), we will pick up these modules::

  >>> module_info = module_info_from_dotted_name(
  ...     'martian.tests.withpyconly', ignore_nonsource=False)
  >>> module_info.getSubModuleInfos()
  [<ModuleInfo object for 'martian.tests.withpyconly.foo'>,
   <ModuleInfo object for 'martian.tests.withpyconly.subpackage'>]
  >>> # rename back to normal name
  >>> os.rename(os.path.join(d, 'foo.py_aside'), os.path.join(d, 'foo.py'))
