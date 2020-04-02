import pytest

import precisionlife_fastjsonschema as fastjsonschema
from precisionlife_fastjsonschema import JsonSchemaDefinitionException, JsonSchemaException


exc = JsonSchemaException('data must be object, but is a: {value_type}', value='{data}', name='data', definition='{definition}', rule='type')
@pytest.mark.parametrize('value, expected', [
    (0, exc),
    (None, exc),
    (True, exc),
    (False, exc),
    ('abc', exc),
    ([], exc),
    ({}, {}),
    ({'x': 1, 'y': True}, {'x': 1, 'y': True}),
])
def test_object(asserter, value, expected):
    asserter({'type': 'object'}, value, expected, value_type=type(value).__name__)


@pytest.mark.parametrize('value, expected', [
    ({}, {}),
    ({'a': 1}, {'a': 1}),
    ({'a': 1, 'b': 2}, JsonSchemaException('data must contain less than or equal to 1 properties', value='{data}', name='data', definition='{definition}', rule='maxProperties')),
])
def test_max_properties(asserter, value, expected):
    asserter({
        'type': 'object',
        'maxProperties': 1,
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ({}, JsonSchemaException('data must contain at least 1 properties', value='{data}', name='data', definition='{definition}', rule='minProperties')),
    ({'a': 1}, {'a': 1}),
    ({'a': 1, 'b': 2}, {'a': 1, 'b': 2}),
])
def test_min_properties(asserter, value, expected):
    asserter({
        'type': 'object',
        'minProperties': 1,
    }, value, expected)


exc = JsonSchemaException('data is missing required properties: [a], [b]', value='{data}', name='data', definition='{definition}', rule='required-additionalProperties')
exc2 = JsonSchemaException('data is missing required properties: [b]', value='{data}', name='data', definition='{definition}', rule='required-additionalProperties')
@pytest.mark.parametrize('value, expected', [
    ({}, exc),
    ({'a': 1}, exc2),
    ({'a': 1, 'b': 2}, {'a': 1, 'b': 2}),
])
def test_required(asserter, value, expected):
    asserter({
        'type': 'object',
        'required': ['a', 'b'],
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ({}, {}),
    ({'a': 1}, {'a': 1}),
    ({'a': 1, 'b': ''}, {'a': 1, 'b': ''}),
    ({'a': 1, 'b': 2}, JsonSchemaException('data.b must be string, but is a: int', value=2, name='data.b', definition={'type': 'string'}, rule='type')),
    ({'a': 1, 'b': '', 'any': True}, {'a': 1, 'b': '', 'any': True}),
])
def test_properties(asserter, value, expected):
    asserter({
        'type': 'object',
        'properties': {
            'a': {'type': 'number'},
            'b': {'type': 'string'},
        },
    }, value, expected)


def test_invalid_properties(asserter):
    with pytest.raises(JsonSchemaDefinitionException):
        fastjsonschema.compile({
            'properties': {
                'item': ['wrong'],
            },
        })


@pytest.mark.parametrize('value, expected', [
    ({}, {}),
    ({'a': 1}, {'a': 1}),
    ({'a': 1, 'b': ''}, {'a': 1, 'b': ''}),
    ({'a': 1, 'b': 2}, JsonSchemaException('data.b must be string, but is a: int', value=2, name='data.b', definition={'type': 'string'}, rule='type')),
    ({'a': 1, 'b': '', 'additional': ''}, {'a': 1, 'b': '', 'additional': ''}),
    ({'a': 1, 'b': '', 'any': True}, JsonSchemaException('data.any must be string, but is a: bool', value=True, name='data.any', definition={'type': 'string'}, rule='type')),
])
def test_properties_with_additional_properties(asserter, value, expected):
    asserter({
        'type': 'object',
        'properties': {
            'a': {'type': 'number'},
            'b': {'type': 'string'},
        },
        'additionalProperties': {'type': 'string'},
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ({}, {}),
    ({'a': 1}, {'a': 1}),
    ({'a': 1, 'b': ''}, {'a': 1, 'b': ''}),
    ({'a': 1, 'b': 2}, JsonSchemaException('data.b must be string, but is a: int', value=2, name='data.b', definition={'type': 'string'}, rule='type')),
    ({'a': 1, 'b': '', 'any': True}, JsonSchemaException('data: additional properties are not allowed: [any]', value='{data}', name='data', definition='{definition}', rule='required-additionalProperties')),
    ({'cd': True}, JsonSchemaException('data: additional properties are not allowed: [cd]', value='{data}', name='data', definition='{definition}', rule='required-additionalProperties')),
    ({'c_d': True}, {'c_d': True}),
])
def test_properties_without_additional_properties(asserter, value, expected):
    asserter({
        'type': 'object',
        'properties': {
            'a': {'type': 'number'},
            'b': {'type': 'string'},
            'c_d': {'type': 'boolean'},
        },
        'additionalProperties': False,
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ({}, {}),
    ({'a': 1}, {'a': 1}),
    ({'xa': 1}, {'xa': 1}),
    ({'xa': ''}, JsonSchemaException('data.xa must be number, but is a: str', value='', name='data.xa', definition={'type': 'number'}, rule='type')),
    ({'xbx': ''}, {'xbx': ''}),
])
def test_pattern_properties(asserter, value, expected):
    asserter({
        'type': 'object',
        'patternProperties': {
            'a': {'type': 'number'},
            'b': {'type': 'string'},
        },
        'additionalProperties': False,
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ({}, {}),
    ({'a': 1}, {'a': 1}),
    ({'b': True}, {'b': True}),
    ({'c': ''}, {'c': ''}),
    ({'d': 1}, JsonSchemaException('data.d must be string, but is a: int', value=1, name='data.d', definition={'type': 'string'}, rule='type')),
])
def test_additional_properties(asserter, value, expected):
    asserter({
        'type': 'object',
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "boolean"},
        },
        "additionalProperties": {"type": "string"}
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ({'id': 1}, {'id': 1}),
    ({'id': 'a'}, JsonSchemaException('data.id must be integer, but is a: str', value='a', name='data.id', definition={'type': 'integer'}, rule='type')),
])
def test_object_with_id_property(asserter, value, expected):
    asserter({
        "type": "object",
        "properties": {
            "id": {"type": "integer"}
        }
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ({'$ref': 'ref://to.somewhere'}, {'$ref': 'ref://to.somewhere'}),
    ({'$ref': 1}, JsonSchemaException('data.$ref must be string, but is a: int', value=1, name='data.$ref', definition={'type': 'string'}, rule='type')),
])
def test_object_with_ref_property(asserter, value, expected):
    asserter({
        "type": "object",
        "properties": {
            "$ref": {"type": "string"}
        }
    }, value, expected)


@pytest.mark.parametrize('value, expected', [
    ({ "prop1": { "str": 1 } }, JsonSchemaException('data.prop1.str must be string, but is a: int', value=1, name='data.prop1.str', definition={'type': 'string'}, rule='type')),
])
def test_full_name_after_ref(asserter, value, expected):
    asserter({
        "definitions": {
            "SomeType": {
                "type": "object",
                "properties": {
                    "str": {"type": "string"},
                },
            },
        },
        "type": "object",
        "properties": {
            "prop1": {"$ref": "#/definitions/SomeType"},
        }
    }, value, expected)
