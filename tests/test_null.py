import pytest

from precisionlife_fastjsonschema import JsonSchemaException


exc = JsonSchemaException('data must be null', value='{data}', name='data', definition='{definition}', rule='type')
@pytest.mark.parametrize('value, expected', [
    (0, exc),
    (None, None),
    (True, exc),
    ('abc', exc),
    ([], exc),
    ({}, exc),
])
def test_null(asserter, value, expected):
    asserter({'type': 'null'}, value, expected)
