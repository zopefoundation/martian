import types


if hasattr(types, 'ClassType'):
    CLASS_TYPES = (type, types.ClassType)
else:
    CLASS_TYPES = (type,)