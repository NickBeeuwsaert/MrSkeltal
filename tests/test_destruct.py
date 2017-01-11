from io import BytesIO

from mr_skeltal import destruct

# Test binary for decoding
BINARY_FILE = (b'Hello, world!\x00\x00\x00\x00\x00\x00\x00'
               b'\x84\xff' b'\xfa\xff\xd3\x04'
               b'p\x11\x01\x00\xd9\xb6\x01\x00'
               b'\x02\x00'
               b'\x08\x00String 1'
               b'\x00\x00\x80?\x00\x00\x00@\x00\x00@@'
               b'\x00\x00\x80?\x00\x00\x00@\x00\x00@@'
               b'\x08\x00String 2'
               b'\x00\x00\x80@\x00\x00\xa0@\x00\x00\xc0@'
               b'\x00\x00\x80@\x00\x00\xa0@\x00\x00\xc0@')

TEST_DATA = dict(
    string='Hello, world!',
    byte=-124,
    unsigned_byte=255,
    short=1235,
    unsigned_short=65530,
    unsigned_integer=70000,
    integer=112345,
    sequence=[
        dict(
            dynamic_string='String 1',
            named_tuple_inline=(1.0, 2.0, 3.0),
            named_tuple=(1.0, 2.0, 3.0)
        ),
        dict(
            dynamic_string='String 2',
            named_tuple_inline=(4.0, 5.0, 6.0),
            named_tuple=(4.0, 5.0, 6.0)
        )
    ]
)


class NamedTuple(destruct.NamedTuple):
    x=destruct.Number('f', '<')
    y=destruct.Number('f', '<')
    z=destruct.Number('f', '<')

class SomeChild(destruct.Struct):
    dynamic_string = destruct.DynamicString(destruct.Number('h', '<'))
    named_tuple_inline = destruct.NamedTuple(
        x=destruct.Number('f', '<'),
        y=destruct.Number('f', '<'),
        z=destruct.Number('f', '<')
    )
    named_tuple = NamedTuple()

class SomeStruct(destruct.Struct):
    string = destruct.String(20)
    byte = destruct.Number('b', '<')
    unsigned_byte = destruct.Number('B', '<')
    unsigned_short = destruct.Number('H', '<')
    short = destruct.Number('h', '<')
    unsigned_integer = destruct.Number('I', '<')
    integer = destruct.Number('i', '<')

    sequence = destruct.Sequence(
        destruct.Number('H', '<'),
        SomeChild()
    )

spec = SomeStruct()

def test_deserialize():
    fp = BytesIO(BINARY_FILE)

    assert TEST_DATA == spec.deserialize(fp), 'deserialized struct doesn\'t match reference!'

def test_serialize():
    fp = BytesIO()
    spec.serialize(TEST_DATA, fp)

    assert BINARY_FILE == fp.getvalue(), 'serialized struct doesn\'t match reference binary!'
