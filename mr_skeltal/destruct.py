'''
I'm embracing Python 3.6 here, using __init_subclass__ and relying on the order
of cls.__dict__
'''
import collections
import operator
import struct

from .decorator import reify

class Type(object):
    name = ''

    def __init__(self, *args, **kwargs):

        self.children = (
            self.__child_types__ +
            list(args) +
            list(self._handle_subtypes(kwargs))
        )

    def deserialize(self, fp):
        raise NotImplementedError(
            f'{self.__class__.__name__} doesn\'t implement deserialize'
        )

    def serialize(self, fp):
        raise NotImplementedError(
            f'{self.__class__.__name__} doesn\'t implement serialize'
        )

    @staticmethod
    def _handle_subtypes(d):
        for name, value in d.items():
            if not isinstance(value, Type):
                continue

            if not value.name:
                value.name = name

            yield value

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.__child_types__ = list(cls._handle_subtypes(cls.__dict__))


class Struct(Type):
    def deserialize(self, fp):
        return {
            child.name: child.deserialize(fp)
            for child in self.children
        }

    def serialize(self, data, fp):
        for child, element in zip(self.children, data):
            child.serialize(fp)


class Tuple(Type):
    def deserialize(self, fp):
        return tuple(
            child.deserialize(fp)
            for child in self.children
        )

    def serialize(self, data, fp):
        for child, element in zip(self.children, data):
            child.serialize(element, fp)

class NamedTuple(Type):
    @reify
    def namedtuple(self):
        return collections.namedtuple(
            self.__class__.__name__,
            map(operator.attrgetter('name'), self.children)
        )

    def deserialize(self, fp):
        return self.namedtuple._make(
            child.deserialize(fp)
            for child in self.children
        )

    def serialize(self, data, fp):
        for child, element in zip(self.children, data):
            child.serialize(element, fp)


class Number(Type):
    byte_order = '='

    @property
    def fmt(self):
        raise NotImplementedError()

    @reify
    def struct(self):
        return struct.Struct(f'{self.byte_order}{self.fmt}')

    def deserialize(self, fp):
        raw_data = fp.read(self.struct.size)
        result, = self.struct.unpack(raw_data)
        return result

    def serialize(self, data, fp):
        fp.write(self.struct.pack(data))

class Byte(Number):
    fmt = 'b'

class UnsignedByte(Number):
    fmt = 'B'

class Short(Number):
    fmt = 'h'

class UnsignedShort(Number):
    fmt = 'H'

class Int(Number):
    fmt = 'i'

class UnsignedInt(Number):
    fmt = 'I'

class Float(Number):
    fmt = 'f'


class Sequence(Type):
    def __init__(self, length_type: Number, target_type: Type):
        super().__init__()
        self.length_type = length_type
        self.target_type = target_type

    def deserialize(self, fp):
        length = self.length_type.deserialize(fp)

        return [
            self.target_type.deserialize(fp)
            for _ in range(length)
        ]

    def serialize(self, data, fp):
        self.length_type.serialize(len(data), fp)

        for element in data:
            self.target_type.serialize(element, data)


class String(Type):
    def __init__(self, length:int, encoding='utf8'):
        super().__init__()
        self.length = length
        self.encoding = encoding

    def deserialize(self, fp):
        raw_string, _, _ = fp.read(self.length).partition(b'\x00')

        return raw_string.decode(self.encoding)

    def serialize(self, data, fp):
        fp.write(data.encode(self.encoding).ljust(self.length, '\x00'))



class DynamicString(Type):
    """A string of variable length, stored in file as <length><string>

    :param length_type: The `Type` to use to decode the string length
    :param encoding: The encoding of the string stored in the file.
    """
    def __init__(self, length_type:Number, encoding='utf-8'):
        super().__init__()
        self.length_type = length_type
        self.encoding = encoding

    def deserialize(self, fp):
        length = self.length_type.deserialize(fp)
        return fp.read(length).decode(self.encoding)

    def serialize(self, data, fp):
        raw_data = data.encode(self.encoding)
        self.length_type.serialize(raw_data, fp)
        fp.write(raw_data)


class Signature(Type):
    def __init__(self, signature: bytes):
        super().__init__()
        self.signature = signature

    def deserialize(self, fp):
        raw_data = fp.read(len(self.signature))

        assert raw_data == self.signature, 'File signature doesn\'t match!'

        return raw_data
