import pytest

from precisionlife_fastjsonschema import JsonSchemaValidationException


exc = JsonSchemaValidationException('must be string, but is a: {value_type}', value='{data}', _rendered_path='data', definition='{definition}', rule='type')
@pytest.mark.parametrize('value, expected', [
    (0, exc),
    (None, exc),
    (True, exc),
    ('', ''),
    ('abc', 'abc'),
    ([], exc),
    ({}, exc),
])
def test_string(asserter, value, expected):
    asserter({'type': 'string'}, value, expected, value_type=type(value).__name__)


exc = JsonSchemaValidationException('must be shorter than or equal to 5 characters', value='{data}', _rendered_path='data', definition='{definition}', rule='maxLength')
@pytest.mark.parametrize('value, expected', [
    ('', ''),
    ('qwer', 'qwer'),
    ('qwert', 'qwert'),
    ('qwertz', exc),
    ('qwertzuiop', exc),
])
def test_max_length(asserter, value, expected):
    asserter({
        'type': 'string',
        'maxLength': 5,
    }, value, expected)


exc = JsonSchemaValidationException('must be longer than or equal to 5 characters', value='{data}', _rendered_path='data', definition='{definition}', rule='minLength')
@pytest.mark.parametrize('value, expected', [
    ('', exc),
    ('qwer', exc),
    ('qwert', 'qwert'),
    ('qwertz', 'qwertz'),
    ('qwertzuiop', 'qwertzuiop'),
])
def test_min_length(asserter, value, expected):
    asserter({
        'type': 'string',
        'minLength': 5,
    }, value, expected)


exc = JsonSchemaValidationException('"" does not match pattern "^[ab]*[^ab]+(c{2}|d)$"', value='{data}', _rendered_path='data', definition='{definition}', rule='pattern')
exc2 = JsonSchemaValidationException('"aacc" does not match pattern "^[ab]*[^ab]+(c{2}|d)$"', value='{data}', _rendered_path='data', definition='{definition}', rule='pattern')
exc3 = JsonSchemaValidationException('"aacd\n" does not match pattern "^[ab]*[^ab]+(c{2}|d)$"', value='{data}', _rendered_path='data', definition='{definition}', rule='pattern')
@pytest.mark.parametrize('value, expected', [
    ('', exc),
    ('aacc', exc2),
    ('aaccc', 'aaccc'),
    ('aacd', 'aacd'),
    ('aacd\n', exc3),
])
def test_pattern(asserter, value, expected):
    asserter({
        'type': 'string',
        'pattern': '^[ab]*[^ab]+(c{2}|d)$',
    }, value, expected)


@pytest.mark.parametrize('pattern', [
    ' ',
    '\\x20',
])
def test_pattern_with_space(asserter, pattern):
    asserter({
        'type': 'string',
        'pattern': pattern,
    }, ' ', ' ')


def test_pattern_with_escape_no_warnings(asserter):
    with pytest.warns(None) as record:
        asserter({
            'type': 'string',
            'pattern': '\\s'
        }, ' ', ' ')

    assert len(record) == 0


exc = JsonSchemaValidationException('must be a valid regex', value='{data}', _rendered_path='data', definition='{definition}', rule='format')
@pytest.mark.parametrize('value, expected', [
    ('[a-z]', '[a-z]'),
    ('[a-z', exc),
])
def test_regex_pattern(asserter, value, expected):
    asserter({
        'format': 'regex',
        'type': 'string'
    }, value, expected)
