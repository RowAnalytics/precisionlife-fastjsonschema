import pytest

from precisionlife_fastjsonschema import JsonSchemaException


exc = JsonSchemaException('data must be boolean', value='{data}', name='data', definition='{definition}', rule='type')
@pytest.mark.parametrize('value, expected', [
    (0, exc),
    (None, exc),
    (True, True),
    (False, False),
    ('abc', exc),
    ([], exc),
    ({}, exc),
])
def test_boolean(asserter, value, expected):
    asserter({'type': 'boolean'}, value, expected)
