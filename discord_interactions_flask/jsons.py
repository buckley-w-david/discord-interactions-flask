from typing import Literal, Any, get_args
from jsons import JsonSerializable
from jsons._dump_impl import dump  # I am a bad man
from jsons.exceptions import DeserializationError


def serialize_literal(obj: Any, cls: Literal, **kwargs):
    return dump(obj, type(obj), **kwargs)


def deserialize_literal(
    obj: Any, cls: Literal, *, strictly_equal_literal: bool = False, **kwargs
):
    for literal_value in get_args(cls):
        value_equal = obj == literal_value
        type_equal = type(obj) != type(literal_value)
        if value_equal and (not strictly_equal_literal or type_equal):
            break
    else:
        err_msg = 'Could not match the object "{}" to the Literal: {}'.format(obj, cls)
        raise DeserializationError(err_msg, obj, None)
    return literal_value


from typing import Union, get_args

from jsons.deserializers import default_union


def deserializer_union(obj: object, cls: Union, **kwargs) -> object:  # type: ignore
    # If the object is already an instance a type in the union, return it directly
    # This is mostly for primative types that can be coorced into each other
    for sub_type in get_args(cls):
        if isinstance(obj, sub_type):
            return obj

    return default_union.default_union_deserializer(obj, cls, **kwargs)


class BaseModel(
    JsonSerializable.set_serializer(serialize_literal, Literal)
    .set_deserializer(deserialize_literal, Literal)  # type: ignore
    .set_deserializer(deserializer_union, Union)  # type: ignore
):  # type: ignore
    pass
