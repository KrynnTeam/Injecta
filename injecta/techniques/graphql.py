"""
Injecta — GraphQL introspection & injection
"""
import json
import re
from typing import Any, Dict, List, Optional


INTROSPECTION_QUERY = """
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    types {
      name
      kind
      fields {
        name
        args {
          name
          type {
            name
            kind
            ofType { name kind }
          }
        }
        type {
          name
          kind
          ofType { name kind }
        }
      }
    }
  }
}
"""


class GraphQLInjector:
    def __init__(self, requester, config, logger):
        self.req = requester
        self.config = config
        self.log = logger
        self.schema = None
        self.endpoints = []

    def discover(self, url: str) -> Dict[str, Any]:
        self.log.info("Discovering GraphQL endpoints...")
        candidates = self._find_endpoints(url)
        if not candidates:
            self.log.debug2("No GraphQL endpoints found")
            return {"found": False, "endpoints": [], "schema_extracted": False}

        self.endpoints = candidates
        self.log.ok(f"Found {len(candidates)} GraphQL endpoint(s): {', '.join(candidates)}")

        for ep in candidates:
            schema = self._introspect(ep)
            if schema:
                self.schema = schema
                self.log.ok(f"Schema extracted from {ep} ({len(schema.get('types', []))} types)")
                return {"found": True, "endpoints": candidates, "schema_extracted": True, "schema": schema}

        return {"found": True, "endpoints": candidates, "schema_extracted": False}

    def _find_endpoints(self, url: str) -> List[str]:
        common_paths = [
            "/graphql", "/v1/graphql", "/v2/graphql", "/graph", "/gql",
            "/query", "/api", "/api/graphql", "/graphql/console",
            "/graphiql", "/playground",
        ]
        found = []

        from urllib.parse import urlparse
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        for path in common_paths:
            test_url = f"{base}{path}"
            resp, err = self.req.request(test_url, extra_headers={"Content-Type": "application/json"})
            if err or resp is None:
                continue
            if resp.status_code in (200, 400, 405):
                body = resp.text.lower() if resp.text else ""
                if any(kw in body for kw in ["errors", "query", "mutation", "subscription",
                                              "\"data\"", "\"__schema\"", "graphql"]):
                    found.append(test_url)
                elif resp.status_code == 400 and '"errors"' in body:
                    found.append(test_url)

        return found

    def _introspect(self, endpoint: str) -> Optional[Dict[str, Any]]:
        payload = json.dumps({"query": INTROSPECTION_QUERY})
        resp, err = self.req.request(
            endpoint,
            data=payload,
            extra_headers={"Content-Type": "application/json"},
        )
        if err or resp is None:
            return None
        try:
            data = json.loads(resp.text)
            if "data" in data and "__schema" in data["data"]:
                return data["data"]["__schema"]
        except (json.JSONDecodeError, KeyError):
            pass
        return None

    def test_injection(self, endpoint: str) -> Dict[str, Any]:
        self.log.info(f"Testing injection on {endpoint}")
        results = {"vulnerable": False, "tested_fields": [], "errors": []}

        if not self.schema:
            return results

        query_type = self.schema.get("queryType", {})
        mutation_type = self.schema.get("mutationType", {})

        for type_info in [query_type, mutation_type]:
            type_name = type_info.get("name", "")
            type_data = self._find_type(type_name)
            if not type_data:
                continue
            fields = type_data.get("fields", [])
            for field in fields:
                result = self._test_field_injection(endpoint, field)
                results["tested_fields"].append(field.get("name", ""))
                if result["vulnerable"]:
                    results["vulnerable"] = True
                    results["errors"].append(result)

        if results["vulnerable"]:
            self.log.warn(f"GraphQL injection confirmed on {endpoint}")
        else:
            self.log.ok(f"No injection found on {endpoint}")

        return results

    def _find_type(self, name: str) -> Optional[Dict[str, Any]]:
        if not self.schema:
            return None
        for t in self.schema.get("types", []):
            if t.get("name") == name:
                return t
        return None

    def _test_field_injection(self, endpoint: str, field: Dict[str, Any]) -> Dict[str, Any]:
        field_name = field.get("name", "")
        args = field.get("args", [])
        result = {"field": field_name, "vulnerable": False, "detail": ""}

        for arg in args:
            arg_name = arg.get("name", "")
            arg_type = arg.get("type", {})

            if any(kw in arg_name.lower() for kw in ["id", "key", "param", "input", "query"]):
                test_payloads = [
                    f'{{"{arg_name}": "1 AND 1=1"}}',
                    f'{{"{arg_name}": "1\'"}}',
                    f'{{"{arg_name}": {"$ne": null}}}',
                ]

                for p in test_payloads:
                    query = f'{{"{field_name}"({arg_name}: {p}){{ {field_name} }}}}'
                    payload = json.dumps({"query": f"query {{ {field_name}({arg_name}: {p}) {{ {field_name} }} }}"})
                    resp, err = self.req.request(
                        endpoint,
                        data=payload,
                        extra_headers={"Content-Type": "application/json"},
                    )
                    if err or resp is None:
                        continue

                    if resp.status_code == 200:
                        body = resp.text.lower()
                        if any(kw in body for kw in ["error", "syntax", "mysql", "postgresql",
                                                      "unexpected", "invalid input"]):
                            result["vulnerable"] = True
                            result["detail"] = f"Injection via {arg_name}: {p[:60]}"
                            break

        return result
