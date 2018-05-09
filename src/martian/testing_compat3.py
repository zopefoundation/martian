""" Just python classes that only work in
    python3. In python < 3 you will get a syntax error.
"""

from martian.testing import FakeModuleMetaclass


class FakeModuleObjectMetaclass(type):
    """ Base metaclass to replace object in a fake Module.
        In python 3 we need to change the class name for
        inner classes. So all test will run in python 2 and 3.

        Without this class the name of fakemodule will be
        shown double in the class name, like this:
        <class 'martiantest.fake.basemodule.basemodule.A'>
        If this class name is returned, the doctest will fail.
    """

    def __init__(cls, classname, bases, dict_):
        normalname = cls.__qualname__.split('.')[-1]
        dict_['__qualname__'] = normalname
        cls.__qualname__ = dict_['__qualname__']
        return type.__init__(cls, classname, bases, dict_)


class FakeModuleObject(object, metaclass=FakeModuleObjectMetaclass):
    pass


class FakeModule(object, metaclass=FakeModuleMetaclass):
    pass
