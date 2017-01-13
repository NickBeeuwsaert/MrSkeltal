'''
I'm embracing Python 3.6 here, using __init_subclass__ and relying on the order
of cls.__dict__
'''
import collections
import struct

from .decorator import reify


class DestructError(Exception):
    pass


class Type(object):
    __types__ = []

    def __init__(self, *args, **kwargs):
        self.children = self.__types__ + [
            ('', child) for child in args if isinstance(child, Type)
        ] + [
            (name, child)
            for name, child in kwargs.items()
            if isinstance(child, Type)
        ]

    def deserialize(self, fp):
        raise NotImplementedError(
            '{name} doesn\'t implement deserialize'.format(
                name=self.__class__.__name__
            )
        )

    def serialize(self, fp):
        raise NotImplementedError(
            '{name} doesn\'t implement serialize'.format(
                name=self.__class__.__name__
            )
        )

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.__types__ = cls.__types__ + [
            (name, child)
            for name, child in vars(cls).items()
            if isinstance(child, Type)
        ]


class Struct(Type):
    """A mapping of values"""
    def deserialize(self, fp):
        result = []
        for name, child in self.children:
            try:
                result.append((name, child.deserialize(fp)))
            except Exception as e:
                raise DestructError(
                    'Error when trying to deserialize {name}'.format(
                        name=name
                    )
                ) from e

        return dict(result)

    def serialize(self, data, fp):
        for name, child in self.children:
            child.serialize(data[name], fp)


class Tuple(Type):
    """A tuple of values."""
    def deserialize(self, fp):
        return tuple(
            child.deserialize(fp)
            for _, child in self.children
        )

    def serialize(self, data, fp):
        for (name, child), element in zip(self.children, data):
            child.serialize(element, fp)


class NamedTuple(Type):
    """Like the Tuple type, but uses a NamedTuple."""
    @reify
    def namedtuple(self):
        return collections.namedtuple(
            self.__class__.__name__,
            [name for name, child in self.children]
        )

    def deserialize(self, fp):
        return self.namedtuple._make(
            child.deserialize(fp)
            for name, child in self.children
        )

    def serialize(self, data, fp):
        for (name, child), element in zip(self.children, data):
            child.serialize(element, fp)


class Number(Type):
    """A number in the file. Really, this is just a thin wrapper around `struct`

    :param fmt: The `struct` fmt to use
    :param byte_order: The byte order to use, defaults to the hosts byteorder
    """
    def __init__(self, fmt, byte_order='='):
        self.fmt = fmt
        self.byte_order = byte_order

    @reify
    def struct(self):
        return struct.Struct('{byte_order}{fmt}'.format_map(vars(self)))

    def deserialize(self, fp):
        raw_data = fp.read(self.struct.size)
        result, = self.struct.unpack(raw_data)
        return result

    def serialize(self, data, fp):
        fp.write(self.struct.pack(data))


class Sequence(Type):
    """A variable-length sequence.

    :param length_type: The type to use to decode the length of the sequence
    :param target_type: The type to decode <length> times
    """
    def __init__(self, length_type, target_type):
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
            self.target_type.serialize(element, fp)


class String(Type):
    """A fixed length string.

    :param length: length of the string in bytes
    :param encoding: The encoding to use, defaults to UTF8
    """
    def __init__(self, length, encoding='utf8'):
        super().__init__()
        self.length = length
        self.encoding = encoding

    def deserialize(self, fp):
        raw_string, _, _ = fp.read(self.length).partition(b'\x00')

        return raw_string.decode(self.encoding)

    def serialize(self, data, fp):
        fp.write(data.encode(self.encoding).ljust(self.length, b'\x00'))


class DynamicString(Type):
    """A string of variable length, stored in file as <length><string>

    :param length_type: The `Type` to use to decode the string length
    :param encoding: The encoding of the string stored in the file.
    """
    def __init__(self, length_type, encoding='utf-8'):
        super().__init__()
        self.length_type = length_type
        self.encoding = encoding

    def deserialize(self, fp):
        length = self.length_type.deserialize(fp)
        return fp.read(length).decode(self.encoding)

    def serialize(self, data, fp):
        raw_data = data.encode(self.encoding)
        self.length_type.serialize(len(raw_data), fp)
        fp.write(raw_data)


class Signature(Type):
    """A static file signature. Throws an error if the signature doesn't match
    the signature configured.

    :param signature: The signature as a type
    """
    def __init__(self, signature):
        super().__init__()
        self.signature = signature

    def deserialize(self, fp):
        raw_data = fp.read(len(self.signature))

        assert raw_data == self.signature, 'File signature doesn\'t match!'

        return raw_data
