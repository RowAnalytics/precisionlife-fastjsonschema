import pytest

from precisionlife_fastjsonschema import JsonSchemaException


@pytest.mark.parametrize('value, expected', [
    (None, JsonSchemaException('data must be object, but is a: NoneType', value='{data}', name='data', definition='{definition}', rule='type')),
    ({}, {'a': '', 'b': 42, 'c': {}, 'd': []}),
    ({'a': 'abc'}, {'a': 'abc', 'b': 42, 'c': {}, 'd': []}),
    ({'b': 123}, {'a': '', 'b': 123, 'c': {}, 'd': []}),
    ({'a': 'abc', 'b': 123}, {'a': 'abc', 'b': 123, 'c': {}, 'd': []}),
])
def test_default_in_object(asserter, value, expected):
    asserter({
        'type': 'object',
        'properties': {
            'a': {'type': 'string', 'default': ''},
            'b': {'type': 'number', 'default': 42},
            'c': {'type': 'object', 'default': {}},
            'd': {'type': 'array', 'default': []},
        },
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    (None, JsonSchemaException('data must be array, but is a: NoneType', value='{data}', name='data', definition='{definition}', rule='type')),
    ([], ['', 42]),
    (['abc'], ['abc', 42]),
    (['abc', 123], ['abc', 123]),
])
def test_default_in_array(asserter, value, expected):
    asserter({
        'type': 'array',
        'items': [
            {'type': 'string', 'default': ''},
            {'type': 'number', 'default': 42},
        ],
    }, value, expected)
