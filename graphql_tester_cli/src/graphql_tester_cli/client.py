from typing import Dict, Any, Optional, AsyncGenerator
import asyncio
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.websockets import WebsocketsTransport

INTROSPECTION_QUERY = """
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      ...FullType
    }
    directives {
      name
      description
      locations
      args {
        ...InputValue
      }
    }
  }
}

fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    args {
      ...InputValue
    }
    type {
      ...TypeRef
    }
    isDeprecated
    deprecationReason
  }
  inputFields {
    ...InputValue
  }
  interfaces {
    ...TypeRef
  }
  enumValues(includeDeprecated: true) {
    name
    description
    isDeprecated
    deprecationReason
  }
  possibleTypes {
    ...TypeRef
  }
}

fragment InputValue on __InputValue {
  name
  description
  type { ...TypeRef }
  defaultValue
}

fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
        }
      }
    }
  }
}
"""

class GraphQLClient:
    def __init__(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        ws_endpoint: Optional[str] = None,
    ):
        self.endpoint = endpoint
        self.headers = headers or {}
        self.transport = RequestsHTTPTransport(
            url=endpoint, headers=self.headers, verify=True
        )
        self.sync_client = Client(
            transport=self.transport, fetch_schema_from_transport=True
        )
        self.ws_endpoint = ws_endpoint or endpoint.replace("https://", "wss://").replace("http://", "ws://")

    def execute(self, document: str, variable_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute sync query/mutation."""
        query = gql(document)
        try:
            result = self.sync_client.execute(query, variable_values=variable_values)
            return result
        except Exception as e:
            return {"errors": [{"message": str(e)}]}

    async def aexecute(self, document: str, variable_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute async query/mutation."""
        transport = AIOHTTPTransport(url=self.endpoint, headers=self.headers)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        async with client:
            query = gql(document)
            result = await client.execute(query, variable_values=variable_values)
            return result

    async def subscribe(
        self, document: str, variable_values: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Subscribe to events. Yields results."""
        transport = WebsocketsTransport(url=self.ws_endpoint, headers=self.headers)
        client = Client(transport=transport)
        async with client:
            async for result in client.subscribe(gql(document), variable_values=variable_values):
                yield result