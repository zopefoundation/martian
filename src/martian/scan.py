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
"""Scanning packages and modules
"""

import os

from zope.interface import implements

from martian.interfaces import IModuleInfo

def is_package(path):
    if not os.path.isdir(path):
        return False
    init_py = os.path.join(path, '__init__.py')
    init_pyc = init_py + 'c'
    # Check whether either __init__.py or __init__.pyc exist
    return os.path.isfile(init_py) or os.path.isfile(init_pyc)


class ModuleInfo(object):
    implements(IModuleInfo)

    def __init__(self, path, dotted_name, exclude_filter=None,
                 ignore_nonsource=True):
        # Normalize .pyc files to .py
        if path.endswith('c'):
            path = path[:-1]
        self.path = path
        self.dotted_name = dotted_name
        self.ignore_nonsource = ignore_nonsource

        if exclude_filter is None:
            # this exclude filter receives extensionless filenames
            self.exclude_filter = lambda x: False
        else:
            self.exclude_filter = exclude_filter

        name_parts = dotted_name.split('.')
        self.name = name_parts[-1]
        if self.isPackage():
            self.package_dotted_name = dotted_name
        else:
            self.package_dotted_name = '.'.join(name_parts[:-1])

        self._module = None

    def getResourcePath(self, name):
        """Get the absolute path of a resource directory 'relative' to this
        package or module.

        Case one: get the resource directory with name <name> from the same
        directory as this module

        Case two: get the resource directory with name <name> from the children
        of this package
        """
        return os.path.join(os.path.dirname(self.path), name)

    def getSubModuleInfos(self):
        if not self.isPackage():
            return []
        directory = os.path.dirname(self.path)
        module_infos = []
        seen = []
        for entry in sorted(os.listdir(directory)):
            # we are only interested in things that are potentially
            # python modules or packages, and therefore start with a
            # letter or _
            if not entry[0].isalpha() and entry[0] != '_':
                continue
            entry_path = os.path.join(directory, entry)
            name, ext = os.path.splitext(entry)
            dotted_name = self.dotted_name + '.' + name
            if self.exclude_filter(name):
                continue
            if self.ignore_nonsource:
                if ext in ['.pyo', '.pyc']:
                    continue
            # Case one: modules
            if (os.path.isfile(entry_path) and ext in ['.py', '.pyc']):
                if name == '__init__':
                    continue
                # Avoid duplicates when both .py and .pyc exist
                if name in seen:
                    continue
                seen.append(name)
                module_infos.append(
                    ModuleInfo(entry_path,
                               dotted_name,
                               exclude_filter=self.exclude_filter,
                               ignore_nonsource=self.ignore_nonsource)
                    )
            # Case two: packages
            elif is_package(entry_path):
                # We can blindly use __init__.py even if only
                # __init__.pyc exists because we never actually use
                # that filename.
                module_infos.append(ModuleInfo(
                    os.path.join(entry_path, '__init__.py'),
                    dotted_name,
                    exclude_filter=self.exclude_filter,
                    ignore_nonsource=self.ignore_nonsource))
        return module_infos

    def getSubModuleInfo(self, name):
        path = os.path.join(os.path.dirname(self.path), name)
        if is_package(path):
            return ModuleInfo(os.path.join(path, '__init__.py'),
                              '%s.%s' % (self.package_dotted_name, name),
                              exclude_filter=self.exclude_filter,
                              ignore_nonsource=self.ignore_nonsource)
        elif os.path.isfile(path + '.py') or os.path.isfile(path + '.pyc'):
                return ModuleInfo(path + '.py',
                                  '%s.%s' % (self.package_dotted_name, name),
                                  exclude_filter=self.exclude_filter,
                                  ignore_nonsource = self.ignore_nonsource)
        else:
            return None


    def getAnnotation(self, key, default):
        key = key.replace('.', '_')
        key = '__%s__' % key
        module = self.getModule()
        return getattr(module, key, default)

    def getModule(self):
        if self._module is None:
            self._module = resolve(self.dotted_name)
        return self._module

    def isPackage(self):
        return self.path.endswith('__init__.py')

    def __repr__(self):
        return "<ModuleInfo object for '%s'>" % self.dotted_name

class BuiltinDummyModule(object):
    """Needed for BuiltinModuleInfo"""
    pass

class BuiltinModuleInfo(object):
    implements(IModuleInfo)

    # to let view grokking succeed in tests
    package_dotted_name = 'dummy.dotted.name'
    
    def getModule(self):
        return BuiltinDummyModule()
    
    def isPackage(self):
        return False

    def getSubModuleInfos(self):
        return []

    def getSubModuleInfo(self, name):
        return None

    def getResourcePath(self, name):
        # XXX we break the contract here. We could return
        # a link to some temp directory for testing purposes?
        return None
    
    def getAnnotation(self, key, default):
        return default

def module_info_from_dotted_name(dotted_name, exclude_filter=None,
                                 ignore_nonsource=True):
    if dotted_name == '__builtin__':
        # in case of the use of individually grokking something during a
        # test the dotted_name being passed in could be __builtin__
        # in this case we return a special ModuleInfo that just
        # implements enough interface to work
        return BuiltinModuleInfo()
    module = resolve(dotted_name)
    return ModuleInfo(module.__file__, dotted_name, exclude_filter,
                      ignore_nonsource)

def module_info_from_module(module, exclude_filter=None, ignore_nonsource=True):
    return ModuleInfo(module.__file__, module.__name__, exclude_filter,
                      ignore_nonsource)


# taken from zope.dottedname.resolve
def resolve(name, module=None):
    name = name.split('.')
    if not name[0]:
        if module is None:
            raise ValueError("relative name without base module")
        module = module.split('.')
        name.pop(0)
        while not name[0]:
            module.pop()
            name.pop(0)
        name = module + name

    used = name.pop(0)
    found = __import__(used)
    for n in name:
        used += '.' + n
        try:
            found = getattr(found, n)
        except AttributeError:
            __import__(used)
            found = getattr(found, n)

    return found
