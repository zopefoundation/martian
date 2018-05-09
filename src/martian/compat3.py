import sys
import types


if hasattr(types, 'ClassType'):
    CLASS_TYPES = (type, types.ClassType)
else:
    CLASS_TYPES = (type,)


if sys.version_info[0] < 3:
    str = unicode  # NOQA
else:
    str = str
