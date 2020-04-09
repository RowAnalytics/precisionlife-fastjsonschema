import pytest

from precisionlife_fastjsonschema import JsonSchemaValidationException


exc = JsonSchemaValidationException('must be array, but is a: {value_type}', value='{data}', _rendered_path='data', definition='{definition}', rule='type')
@pytest.mark.parametrize('value, expected', [
    (0, exc),
    (None, exc),
    (True, exc),
    (False, exc),
    ('abc', exc),
    ([], []),
    ([1, 'a', True], [1, 'a', True]),
    ((1, 'a', True), (1, 'a', True)),
    (range(5), range(5)),
    ({}, exc),
])
def test_array(asserter, value, expected):
    asserter({'type': 'array'}, value, expected, value_type=type(value).__name__)


exc = JsonSchemaValidationException('must contain less than or equal to 1 items', value='{data}', _rendered_path='data', definition='{definition}', rule='maxItems')
@pytest.mark.parametrize('value, expected', [
    ([], []),
    ([1], [1]),
    ([1, 1], exc),
    ([1, 2, 3], exc),
])
def test_max_items(asserter, value, expected):
    asserter({
        'type': 'array',
        'maxItems': 1,
    }, value, expected)


exc = JsonSchemaValidationException('must contain at least 2 items', value='{data}', _rendered_path='data', definition='{definition}', rule='minItems')
@pytest.mark.parametrize('value, expected', [
    ([], exc),
    ([1], exc),
    ([1, 1], [1, 1]),
    ([1, 2, 3], [1, 2, 3]),
])
def test_min_items(asserter, value, expected):
    asserter({
        'type': 'array',
        'minItems': 2,
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ([], []),
    ([1], [1]),
    ([1, 1], JsonSchemaValidationException('must contain unique items', value='{data}', _rendered_path='data', definition='{definition}', rule='uniqueItems')),
    ([1, 2, 3], [1, 2, 3]),
])
def test_unique_items(asserter, value, expected):
    asserter({
        'type': 'array',
        'uniqueItems': True,
    }, value, expected)


def test_min_and_unique_items(asserter):
    value = None
    asserter({
        'type': ['array', 'null'],
        'minItems': 1,
        'uniqueItems': True,
    }, value, value)


@pytest.mark.parametrize('value, expected', [
    ([], []),
    ([1], [1]),
    ([1, 'a'], JsonSchemaValidationException('must be number, but is a: str', value='a', _rendered_path='data[1]', definition={'type': 'number'}, rule='type')),
])
def test_items_all_same(asserter, value, expected):
    asserter({
        'type': 'array',
        'items': {'type': 'number'},
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ([], []),
    ([1], [1]),
    ([1, 'a'], [1, 'a']),
    ([1, 2], JsonSchemaValidationException('must be string, but is a: int', value=2, _rendered_path='data[1]', definition={'type': 'string'}, rule='type')),
    ([1, 'a', 2], [1, 'a', 2]),
    ([1, 'a', 'b'], [1, 'a', 'b']),
])
def test_different_items(asserter, value, expected):
    asserter({
        'type': 'array',
        'items': [
            {'type': 'number'},
            {'type': 'string'},
        ],
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ([], []),
    ([1], [1]),
    ([1, 'a'], [1, 'a']),
    ([1, 2], JsonSchemaValidationException('must be string, but is a: int', value=2, _rendered_path='data[1]', definition={'type': 'string'}, rule='type')),
    ([1, 'a', 2], JsonSchemaValidationException('must be string, but is a: int', value=2, _rendered_path='data[2]', definition={'type': 'string'}, rule='type')),
    ([1, 'a', 'b'], [1, 'a', 'b']),
])
def test_different_items_with_additional_items(asserter, value, expected):
    asserter({
        'type': 'array',
        'items': [
            {'type': 'number'},
            {'type': 'string'},
        ],
        'additionalItems': {'type': 'string'},
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ([], []),
    ([1], [1]),
    ([1, 'a'], [1, 'a']),
    ([1, 2], JsonSchemaValidationException('must be string, but is a: int', value=2, _rendered_path='data[1]', definition={'type': 'string'}, rule='type')),
    ([1, 'a', 2], JsonSchemaValidationException('must contain only specified items', value='{data}', _rendered_path='data', definition='{definition}', rule='items')),
    ([1, 'a', 'b'], JsonSchemaValidationException('must contain only specified items', value='{data}', _rendered_path='data', definition='{definition}', rule='items')),
])
def test_different_items_without_additional_items(asserter, value, expected):
    asserter({
        'type': 'array',
        'items': [
            {'type': 'number'},
            {'type': 'string'},
        ],
        'additionalItems': False,
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ((), ()),
    (('a',), ('a',)),
    (('a', 'b'), ('a', 'b')),
    (('a', 'b', 3), JsonSchemaValidationException('must be string, but is a: int', value=3, _rendered_path='data[2]',
                                        definition={'type': 'string'}, rule='type')),
])
def test_tuples_as_arrays(asserter, value, expected):
    asserter({
        '$schema': 'http://json-schema.org/draft-06/schema',
        'type': 'array',
        'items':
            {'type': 'string'},

    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ({'a': [], 'b': ()}, {'a': [], 'b': ()}),
    ({'a': (1, 2), 'b': (3, 4)}, {'a': (1, 2), 'b': (3, 4)}),
])
def test_mixed_arrays(asserter, value, expected):
    asserter({
        'type': 'object',
        'properties': {
            'a': {'type': 'array'},
            'b': {'type': 'array'},
        },
    }, value, expected)

