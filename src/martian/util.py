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
"""Martian utility functions.
"""

import re
import types
import sys
import inspect

from zope import interface

import martian
from martian.error import GrokError, GrokImportError

def not_unicode_or_ascii(value):
    if isinstance(value, unicode):
        return False
    if not isinstance(value, str):
        return True
    return is_not_ascii(value)

is_not_ascii = re.compile(eval(r'u"[\u0080-\uffff]"')).search

def isclass(obj):
    """We cannot use ``inspect.isclass`` because it will return True
    for interfaces"""
    return isinstance(obj, (types.ClassType, type))


def check_subclass(obj, class_):
    if not isclass(obj):
        return False
    return issubclass(obj, class_)


def caller_module():
    return sys._getframe(2).f_globals['__name__']

def is_baseclass(name, component):
    return (isclass(component) and martian.baseclass.bind().get(component))

def defined_locally(obj, dotted_name):
    obj_module = getattr(obj, '__grok_module__', None)
    if obj_module is None:
        obj_module = getattr(obj, '__module__', None)
    return obj_module == dotted_name


def check_implements_one(class_):
    check_implements_one_from_list(list(interface.implementedBy(class_)),
                                   class_)

def check_implements_one_from_list(list, class_):
    if len(list) < 1:
        raise GrokError("%r must implement at least one interface "
                        "(use grok.implements to specify)."
                        % class_, class_)
    elif len(list) > 1:
        raise GrokError("%r is implementing more than one interface "
                        "(use grok.provides to specify which one to use)."
                        % class_, class_)

def check_provides_one(obj):
    provides = list(interface.providedBy(obj))
    if len(provides) < 1:
        raise GrokError("%r must provide at least one interface "
                        "(use zope.interface.classProvides to specify)."
                        % obj, obj)
    if len(provides) > 1:
        raise GrokError("%r provides more than one interface "
                        "(use grok.provides to specify which one to use)."
                        % obj, obj)

def scan_for_classes(module, iface):
    """Given a module, scan for classes.
    """
    for name in dir(module):
        if '.' in name:
            # This must be a module-level variable that couldn't have
            # been set by the developer.  It must have been a
            # module-level directive.
            continue
        obj = getattr(module, name)
        if not defined_locally(obj, module.__name__) or not isclass(obj):
            continue

        if iface.implementedBy(obj):
            yield obj

def methods_from_class(class_):
    # XXX Problem with zope.interface here that makes us special-case
    # __provides__.
    candidates = [getattr(class_, name) for name in dir(class_)
                  if name != '__provides__' ]
    methods = [c for c in candidates if inspect.ismethod(c)]
    return methods

def public_methods_from_class(class_):
    return [m for m in methods_from_class(class_) if \
            not m.__name__.startswith('_')]

def frame_is_module(frame):
    return frame.f_locals is frame.f_globals

def frame_is_class(frame):
    return '__module__' in frame.f_locals
