Martian tutorial
****************

Introduction
============

"There was so much to grok, so little to grok from." -- Stranger in a
Strange Land, by Robert A. Heinlein

Martian provides infrastructure for declarative configuration of
Python code. Martian is especially useful for the construction of
frameworks that need to provide a flexible plugin
infrastructure. Martian doesn't actually provide infrastructure for
plugin registries (except for itself). Many frameworks have their own
systems for this, and if you need a generic one, you might want to
consider ``zope.component``. Martian just allows you to make the
registration of plugins less verbose.

You can see Martian as doing something that you can also solve with
metaclasses, with the following advantages:

* the developer of the framework doesn't have to write a lot of ad-hoc
  metaclasses anymore; instead we offer an infrastructure to make life
  easier.

* configuration doesn't need to happen at import time, but can happen at
  program startup time. This also makes configuration more tractable for
  a developer.

* we don't bother the developer that *uses* the framework with the
  surprising behavior that metaclasses sometimes bring. The classes
  the user has to deal with are normal classes.

Why is this package named ``martian``? In the novel "Stranger in a
Strange Land", the verb *grok* is introduced:

  Grok means to understand so thoroughly that the observer becomes a
  part of the observed -- to merge, blend, intermarry, lose identity
  in group experience.

In the context of this package, "grokking" stands for the process of
deducing declarative configuration actions from Python code. In the
novel, grokking is originally a concept that comes from the planet
Mars. Martians *grok*. Since this package helps you grok code, it's
called Martian.

Martian provides a framework that allows configuration to be expressed
in declarative Python code. These declarations can often be deduced
from the structure of the code itself. The idea is to make these
declarations so minimal and easy to read that even extensive
configuration does not overly burden the programmers working with the
code.

The ``martian`` package is a spin-off from the `Grok project`_, in the
context of which this codebase was first developed. While Grok uses
it, the code is completely independent of Grok.

.. _`Grok project`: http://grok.zope.org

Motivation
==========

"Deducing declarative configuration actions from Python code" - that
sounds very abstract. What does it actually mean? What is
configuration?  What is declarative configuration? In order to explain
this, we'll first take a look at configuration.

Larger frameworks often offer a lot of points where you can modify
their behavior: ways to combine its own components with components you
provide yourself to build a larger application. A framework offers
points where it can be *configured* with plugin code. When you plug
some code into a plugin point, it results in the updating of some
registry somewhere with the new plugin. When the framework uses a
plugin, it will first look it up in the registry. The action of
registering some component into a registry can be called
*configuration*.

Let's look at an example framework that offers a plugin point. We
introduce a very simple framework for plugging in different template
languages, where each template language uses its own extension. You
can then supply the framework with the template body and the template
extension and some data, and render the template.

Let's look at the framework::

  >>> import string
  >>> class templating(FakeModule):
  ...
  ...   class InterpolationTemplate(object):
  ...      "Use %(foo)s for dictionary interpolation."
  ...      def __init__(self, text):
  ...          self.text = text
  ...      def render(self, **kw):
  ...          return self.text % kw
  ...
  ...   class TemplateStringTemplate(object):
  ...      "PEP 292 string substitutions."
  ...      def __init__(self, text):
  ...          self.template = string.Template(text)
  ...      def render(self, **kw):
  ...          return self.template.substitute(**kw)
  ...
  ...   # the registry, we plug in the two templating systems right away
  ...   extension_handlers = { '.txt': InterpolationTemplate, 
  ...                          '.tmpl': TemplateStringTemplate }
  ...
  ...   def render(data, extension, **kw):
  ...      """Render the template at filepath with arguments.
  ...  
  ...      data - the data in the file
  ...      extension - the extension of the file
  ...      keyword arguments - variables to interpolate
  ...
  ...      In a real framework you could pass in the file path instead of
  ...      data and extension, but we don't want to open files in our
  ...      example.
  ...
  ...      Returns the rendered template
  ...      """
  ...      template = extension_handlers[extension](data)
  ...      return template.render(**kw)

Since normally we cannot create modules in a doctest, we have emulated
the ``templating`` Python module using the ``FakeModule``
class. Whenever you see ``FakeModule`` subclasses, imagine you're
looking at a module definition in a ``.py`` file. Now that we have
defined a module ``templating``, we also need to be able to import
it. To do so we can use a a fake import statement that lets us do
this::

  >>> templating = fake_import(templating)

Now let's try the ``render`` function for the registered template
types, to demonstrate that our framework works::

  >>> templating.render('Hello %(name)s!', '.txt', name="world")
  'Hello world!'
  >>> templating.render('Hello ${name}!', '.tmpl', name="universe")
  'Hello universe!'

File extensions that we do not recognize cause a ``KeyError`` to be
raised::

  >>> templating.render('Hello', '.silly', name="test")
  Traceback (most recent call last):
  ...
  KeyError: '.silly'

We now want to plug into this filehandler framework and provide a
handler for ``.silly`` files. Since we are writing a plugin, we cannot
change the ``templating`` module directly. Let's write an extension
module instead::

  >>> class sillytemplating(FakeModule):
  ...   class SillyTemplate(object):
  ...      "Replace {key} with dictionary values."
  ...      def __init__(self, text):
  ...          self.text = text
  ...      def render(self, **kw):
  ...          text = self.text
  ...          for key, value in kw.items():
  ...              text = text.replace('{%s}' % key, value)
  ...          return text
  ...
  ...   templating.extension_handlers['.silly'] = SillyTemplate
  >>> sillytemplating = fake_import(sillytemplating)

In the extension module, we manipulate the ``extension_handlers``
dictionary of the ``templating`` module (in normal code we'd need to
import it first), and plug in our own function. ``.silly`` handling
works now::

  >>> templating.render('Hello {name}!', '.silly', name="galaxy")
  'Hello galaxy!'

Above we plug into our ``extension_handler`` registry using Python
code. Using separate code to manually hook components into registries
can get rather cumbersome - each time you write a plugin, you also
need to remember you need to register it. 

Doing template registration in Python code also poses a maintenance
risk. It is tempting to start doing fancy things in Python code such
as conditional configuration, making the configuration state of a
program hard to understand. Another problem is that doing
configuration at import time can also lead to unwanted side effects
during import, as well as ordering problems, where you want to import
something that really needs configuration state in another module that
is imported later. Finally, it can also make code harder to test, as
configuration is loaded always when you import the module, even if in
your test perhaps you don't want it to be.

Martian provides a framework that allows configuration to be expressed
in declarative Python code. Martian is based on the realization that
what to configure where can often be deduced from the structure of
Python code itself, especially when it can be annotated with
additional declarations. The idea is to make it so easy to write and
register a plugin so that even extensive configuration does not overly
burden the developer. 

Configuration actions are executed during a separate phase ("grok
time"), not at import time, which makes it easier to reason about and
easier to test.

Configuration the Martian Way
=============================

Let's now transform the above ``templating`` module and the
``sillytemplating`` module to use Martian. First we must recognize
that every template language is configured to work for a particular
extension. With Martian, we annotate the classes themselves with this
configuration information. Annotations happen using *directives*,
which look like function calls in the class body.

Let's create an ``extension`` directive that can take a single string
as an argument, the file extension to register the template class
for::

  >>> import martian
  >>> class extension(martian.Directive):
  ...   scope = martian.CLASS
  ...   store = martian.ONCE
  ...   default = None

We also need a way to easily recognize all template classes. The normal
pattern for this in Martian is to use a base class, so let's define a
``Template`` base class::

  >>> class Template(object):
  ...   pass

We now have enough infrastructure to allow us to change the code to use
Martian style base class and annotations::

  >>> class templating(FakeModule):
  ...
  ...   class InterpolationTemplate(Template):
  ...      "Use %(foo)s for dictionary interpolation."
  ...      extension('.txt')
  ...      def __init__(self, text):
  ...          self.text = text
  ...      def render(self, **kw):
  ...          return self.text % kw
  ...
  ...   class TemplateStringTemplate(Template):
  ...      "PEP 292 string substitutions."
  ...      extension('.tmpl')
  ...      def __init__(self, text):
  ...          self.template = string.Template(text)
  ...      def render(self, **kw):
  ...          return self.template.substitute(**kw)
  ...
  ...   # the registry, empty to start with
  ...   extension_handlers = {}
  ...
  ...   def render(data, extension, **kw):
  ...      # this hasn't changed
  ...      template = extension_handlers[extension](data)
  ...      return template.render(**kw)
  >>> templating = fake_import(templating)

As you can see, there have been very few changes:

* we made the template classes inherit from ``Template``.

* we use the ``extension`` directive in the template classes.

* we stopped pre-filling the ``extension_handlers`` dictionary.

So how do we fill the ``extension_handlers`` dictionary with the right
template languages? Now we can use Martian. We define a *grokker* for
``Template`` that registers the template classes in the
``extension_handlers`` registry::

  >>> class meta(FakeModule):   
  ...   class TemplateGrokker(martian.ClassGrokker):
  ...     martian.component(Template)
  ...     martian.directive(extension)
  ...     def execute(self, class_, extension, **kw):
  ...       templating.extension_handlers[extension] = class_
  ...       return True
  >>> meta = fake_import(meta)

What does this do? A ``ClassGrokker`` has its ``execute`` method
called for subclasses of what's indicated by the ``martian.component``
directive. You can also declare what directives a ``ClassGrokker``
expects on this component by using ``martian.directive()`` (the
``directive`` directive!) one or more times. 

The ``execute`` method takes the class to be grokked as the first
argument, and the values of the directives used will be passed in as
additional parameters into the ``execute`` method. The framework can
also pass along an arbitrary number of extra keyword arguments during
the grokking process, so we need to declare ``**kw`` to make sure we
can handle these.

All our grokkers will be collected in a special Martian-specific
registry::

  >>> reg = martian.GrokkerRegistry()

We will need to make sure the system is aware of the
``TemplateGrokker`` defined in the ``meta`` module first, so let's
register it first. We can do this by simply grokking the ``meta``
module::

  >>> reg.grok('meta', meta)
  True

Because ``TemplateGrokker`` is now registered, our registry now knows
how to grok ``Template`` subclasses. Let's grok the ``templating``
module::

  >>> reg.grok('templating', templating)
  True

Let's try the ``render`` function of templating again, to demonstrate
we have successfully grokked the template classes::

  >>> templating.render('Hello %(name)s!', '.txt', name="world")
  'Hello world!'
  >>> templating.render('Hello ${name}!', '.tmpl', name="universe")
  'Hello universe!'

``.silly`` hasn't been registered yet::

  >>> templating.render('Hello', '.silly', name="test")
  Traceback (most recent call last):
  ...
  KeyError: '.silly'

Let's now register ``.silly`` from an extension module::

  >>> class sillytemplating(FakeModule):
  ...   class SillyTemplate(Template):
  ...      "Replace {key} with dictionary values."
  ...      extension('.silly')
  ...      def __init__(self, text):
  ...          self.text = text
  ...      def render(self, **kw):
  ...          text = self.text
  ...          for key, value in kw.items():
  ...              text = text.replace('{%s}' % key, value)
  ...          return text
  >>> sillytemplating = fake_import(sillytemplating)

As you can see, the developer that uses the framework has no need
anymore to know about ``templating.extension_handlers``. Instead we can
simply grok the module to have ``SillyTemplate`` be register appropriately::

  >>> reg.grok('sillytemplating', sillytemplating)
  True

We can now use the ``.silly`` templating engine too::

  >>> templating.render('Hello {name}!', '.silly', name="galaxy")
  'Hello galaxy!'

Admittedly it is hard to demonstrate Martian well with a small example
like this. In the end we have actually written more code than in the
basic framework, after all. But even in this small example, the
``templating`` and ``sillytemplating`` module have become more
declarative in nature. The developer that uses the framework will not
need to know anymore about things like
``templating.extension_handlers`` or an API to register things
there. Instead the developer can registering a new template system
anywhere, as long as he subclasses from ``Template``, and as long as
his code is grokked by the system.

Finally note how Martian was used to define the ``TemplateGrokker`` as
well. In this way Martian can use itself to extend itself.

Grokking instances
==================

Above we've seen how you can grok classes. Martian also supplies a way
to grok instances. This is less common in typical frameworks, and has
the drawback that no class-level directives can be used, but can still
be useful.

Let's imagine a case where we have a zoo framework with an ``Animal``
class, and we want to track instances of it::

  >>> class Animal(object):
  ...   def __init__(self, name):
  ...     self.name = name
  >>> class zoo(FakeModule):
  ...   horse = Animal('horse')
  ...   chicken = Animal('chicken')
  ...   elephant = Animal('elephant')
  ...   lion = Animal('lion')
  ...   animals = {}
  >>> zoo = fake_import(zoo)
 
We define an ``InstanceGrokker`` subclass to grok ``Animal`` instances::

  >>> class meta(FakeModule):   
  ...   class AnimalGrokker(martian.InstanceGrokker):
  ...     martian.component(Animal)
  ...     def execute(self, instance, **kw):
  ...       zoo.animals[instance.name] = instance
  ...       return True
  >>> meta = fake_import(meta)

Let's create a new registry with the ``AnimalGrokker`` in it::
   
  >>> reg = martian.GrokkerRegistry()
  >>> reg.grok('meta', meta)
  True

We can now grok the ``zoo`` module::

  >>> reg.grok('zoo', zoo)
  True

The animals will now be in the ``animals`` dictionary::

  >>> sorted(zoo.animals.items())
  [('chicken', <Animal object at ...>), 
   ('elephant', <Animal object at ...>), 
   ('horse', <Animal object at ...>), 
   ('lion', <Animal object at ...>)]

More information
================

For many more details and examples of more kinds of grokkers, please
see ``src/martian/core.txt``. For more information on directives see
``src/martian/directive.txt``.
