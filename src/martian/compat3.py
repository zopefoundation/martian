import types

import six


if hasattr(types, 'ClassType'):
    CLASS_TYPES = (type, types.ClassType)
else:
    CLASS_TYPES = (type,)


if six.PY2:
    str = unicode  # NOQA
else:
    str = str
