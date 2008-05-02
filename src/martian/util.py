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
    return (isclass(component) and martian.baseclass.get(component))

def class_annotation(obj, name, default):
    return getattr(obj, '__%s__' % name.replace('.', '_'), default)

def class_annotation_list(obj, name, default):
    """This will process annotations that are lists correctly in the face of
    inheritance.
    """
    if class_annotation(obj, name, default) is default:
        return default

    result = []
    for base in reversed(obj.mro()):
        list = class_annotation(base, name, [])
        if list not in result:
            result.append(list)

    result_flattened = []
    for entry in result:
        result_flattened.extend(entry)
    return result_flattened

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


def scan_for_classes(module, classes):
    """Given a module, scan for classes.
    """
    result = set()
    for name in dir(module):
        if name.startswith('__grok_'):
            continue
        obj = getattr(module, name)
        if not defined_locally(obj, module.__name__):
            continue
        for class_ in classes:
            if check_subclass(obj, class_):
                result.add(obj)
    return list(result)

def methods_from_class(class_):
    # XXX Problem with zope.interface here that makes us special-case
    # __provides__.
    candidates = [getattr(class_, name) for name in dir(class_)
                  if name != '__provides__' ]
    methods = [c for c in candidates if inspect.ismethod(c)]
    return methods

def frame_is_module(frame):
    return frame.f_locals is frame.f_globals

def frame_is_class(frame):
    return '__module__' in frame.f_locals
