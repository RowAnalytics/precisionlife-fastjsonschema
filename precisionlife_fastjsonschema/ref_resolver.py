"""
JSON Schema URI resolution scopes and dereferencing

https://tools.ietf.org/id/draft-zyp-json-schema-04.html#rfc.section.7

Code adapted from https://github.com/Julian/jsonschema
"""

import contextlib
import json
import re
from urllib import parse as urlparse
from urllib.parse import unquote
from urllib.request import urlopen

from .exceptions import JsonSchemaDefinitionException


def get_id(schema):
    """
    Originally ID was `id` and since v7 it's `$id`.
    """
    return schema.get('$id', schema.get('id', ''))


def fixed_urljoin(url0, url1):
    """
    Same as urlparse.urljoin(), but treats all schemes as hierarchical.
    Original urljoin() doesn't work correctly with custom schemas (see https://bugs.python.org/issue18828).
    """
    parts0 = urlparse.urlsplit(url0)
    if parts0.scheme in ['http', 'https']:
        return urlparse.urljoin(url0, url1)

    parts1 = urlparse.urlsplit(url1)
    if parts1.scheme != '':
        return url1

    url0_http = urlparse.urlunsplit(('http', *parts0[1:]))

    joined_url = urlparse.urljoin(url0_http, url1)

    joined_parts = urlparse.urlsplit(joined_url)
    fixed_url = urlparse.urlunsplit((parts0.scheme, *joined_parts[1:]))

    return fixed_url


def resolve_path(schema, fragment):
    """
    Return definition from path.

    Path is unescaped according https://tools.ietf.org/html/rfc6901
    """
    fragment = fragment.lstrip('/')
    parts = unquote(fragment).split('/') if fragment else []
    for part in parts:
        part = part.replace('~1', '/').replace('~0', '~')
        if isinstance(schema, list):
            schema = schema[int(part)]
        elif part in schema:
            schema = schema[part]
        else:
            raise JsonSchemaDefinitionException('Unresolvable ref: {}'.format(part))
    return schema


def normalize(uri):
    return urlparse.urlsplit(uri).geturl()


def resolve_remote(uri, handlers):
    """
    Resolve a remote ``uri``.

    .. note::

        urllib library is used to fetch requests from the remote ``uri``
        if handlers does notdefine otherwise.
    """
    scheme = urlparse.urlsplit(uri).scheme
    try:
        handler = handlers[scheme]  # This is done this way to work fine with defaultdict.
    except KeyError:
        handler = None

    if handler is not None:
        result = handler(uri)
    else:
        req = urlopen(uri)
        encoding = req.info().get_content_charset() or 'utf-8'
        try:
            result = json.loads(req.read().decode(encoding),)
        except ValueError as exc:
            raise JsonSchemaDefinitionException('{} failed to decode: {}'.format(uri, exc))
    return result


class RefResolver:
    """
    Resolve JSON References.
    """

    # pylint: disable=dangerous-default-value,too-many-arguments
    def __init__(self, base_uri, schema, store={}, cache=True, handlers={}):
        """
        `base_uri` is URI of the referring document from the `schema`.
        """
        self.base_uri = base_uri
        self.resolution_scope = base_uri
        self.schema = schema
        self.store = store
        self.cache = cache
        self.handlers = handlers
        self.walk(schema)

        # Dictionary used to make sure we will generate unique names for generated functions.
        self.unique_name_registry = {}
        # Set of names that are taken (equivalent to set(self.unique_name_registry.values())).
        self.unique_names_taken = set()

    @classmethod
    def from_schema(cls, schema, handlers={}, **kwargs):
        """
        Construct a resolver from a JSON schema object.
        """
        return cls(
            get_id(schema) if isinstance(schema, dict) else '',
            schema,
            handlers=handlers,
            **kwargs
        )

    @contextlib.contextmanager
    def in_scope(self, scope: str):
        """
        Context manager to handle current scope.
        """
        old_scope = self.resolution_scope
        self.resolution_scope = fixed_urljoin(old_scope, scope)
        try:
            yield
        finally:
            self.resolution_scope = old_scope

    @contextlib.contextmanager
    def resolving(self, ref: str):
        """
        Context manager which resolves a JSON ``ref`` and enters the
        resolution scope of this ref.
        """
        new_uri = fixed_urljoin(self.resolution_scope, ref)
        uri, fragment = urlparse.urldefrag(new_uri)

        normalized_uri = normalize(uri)
        if normalized_uri in self.store:
            schema = self.store[normalized_uri]
        elif not uri or uri == self.base_uri:
            schema = self.schema
        else:
            schema = resolve_remote(uri, self.handlers)
            if self.cache:
                scheme = urlparse.urlsplit(normalized_uri).scheme
                if scheme != 'internal-no-cache':
                    self.store[normalized_uri] = schema

        old_base_uri, old_schema = self.base_uri, self.schema
        self.base_uri, self.schema = uri, schema
        try:
            with self.in_scope(uri):
                yield resolve_path(schema, fragment)
        finally:
            self.base_uri, self.schema = old_base_uri, old_schema

    def get_uri(self):
        return normalize(self.resolution_scope)

    def get_scope_name(self):
        """
        Get current scope and return it as a valid function name.
        """
        if self.resolution_scope not in self.unique_name_registry:
            name = 'validate_' + unquote(self.resolution_scope)
            name = name.replace('~1', '_').replace('~0', '_').replace('"', '')
            name = re.sub(r'($[^a-zA-Z]|[^a-zA-Z0-9])', '_', name)
            name = name.lower().rstrip('_')

            unique_name = name
            idx = -1
            while unique_name in self.unique_names_taken:
                idx += 1
                unique_name = f'{name}_{idx}'

            self.unique_name_registry[self.resolution_scope] = unique_name
            self.unique_names_taken.add(unique_name)

        return self.unique_name_registry[self.resolution_scope]

    def walk(self, node: dict):
        """
        Walk thru schema and dereferencing ``id`` and ``$ref`` instances
        """
        if isinstance(node, bool):
            pass
        elif '$ref' in node and isinstance(node['$ref'], str):
            ref = node['$ref']
            node['$ref'] = fixed_urljoin(self.resolution_scope, ref)
        elif ('$id' in node or 'id' in node) and isinstance(get_id(node), str):
            with self.in_scope(get_id(node)):
                self.store[normalize(self.resolution_scope)] = node
                for _, item in node.items():
                    if isinstance(item, dict):
                        self.walk(item)
        else:
            for _, item in node.items():
                if isinstance(item, dict):
                    self.walk(item)
