"""
Swagger / OpenAPI 解析器
支持 Swagger 2.0 / OpenAPI 3.0 的 $ref 解析，自动生成 pytest 用例骨架
"""
import json
import re
import httpx
from typing import Optional
from urllib.parse import urlparse


class SwaggerParser:
    def __init__(self):
        self._refs = {}

    def _resolve_ref(self, ref: str, doc: dict) -> dict:
        """解析 $ref 引用"""
        path = ref.lstrip("#/").split("/")
        node = doc
        for part in path:
            node = node.get(part, {})
        return node

    def _collect_refs(self, doc: dict, base: dict = None):
        """预收集 definitions/components 中的 $ref"""
        if base is None:
            base = doc
        # Swagger 2.0 definitions
        for name, schema in doc.get("definitions", {}).items():
            self._refs[f"#/definitions/{name}"] = schema
        # OpenAPI 3.0 components/schemas
        for name, schema in doc.get("components", {}).get("schemas", {}).items():
            self._refs[f"#/components/schemas/{name}"] = schema

    def _resolve_schema(self, schema: dict, doc: dict) -> dict:
        """递归解析 schema 中的 $ref"""
        if not isinstance(schema, dict):
            return schema
        if "$ref" in schema:
            resolved = self._refs.get(schema["$ref"])
            if resolved is not None:
                return self._resolve_schema(resolved, doc)
            resolved = self._resolve_ref(schema["$ref"], doc)
            return self._resolve_schema(resolved, doc) if resolved else schema
        result = {}
        for k, v in schema.items():
            if k == "$ref":
                resolved = self._refs.get(v)
                if resolved is not None:
                    merged = self._resolve_schema(resolved, doc)
                    result.update(merged)
                else:
                    resolved = self._resolve_ref(v, doc)
                    if resolved:
                        result.update(self._resolve_schema(resolved, doc))
            elif k in ("oneOf", "anyOf"):
                result[k] = [self._resolve_schema(s, doc) if isinstance(s, dict) else s for s in v]
            elif isinstance(v, dict):
                result[k] = self._resolve_schema(v, doc)
            elif isinstance(v, list):
                result[k] = [self._resolve_schema(item, doc) if isinstance(item, dict) else item for item in v]
            else:
                result[k] = v
        return result

    def parse(self, raw_doc: dict) -> list[dict]:
        """解析 Swagger 文档，返回接口列表"""
        self._refs = {}
        self._collect_refs(raw_doc)

        apis = []
        paths = raw_doc.get("paths", {})
        base_path = raw_doc.get("basePath", "")

        for path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            for method in ("get", "post", "put", "delete", "patch", "options", "head"):
                operation = methods.get(method)
                if not operation:
                    continue

                # 解析参数
                parameters = operation.get("parameters", [])
                if isinstance(parameters, dict):
                    parameters = list(parameters.values())

                params_info = []
                for p in parameters:
                    p = self._resolve_schema(p, raw_doc) if isinstance(p, dict) else {}
                    params_info.append({
                        "name": p.get("name", ""),
                        "in": p.get("in", ""),
                        "required": p.get("required", False),
                        "type": p.get("type", p.get("schema", {}).get("type", "string")),
                        "description": p.get("description", ""),
                    })

                # 解析请求体
                request_body = {}
                body_param = next((p for p in parameters if p.get("in") == "body"), None)
                if body_param:
                    schema = self._resolve_schema(body_param.get("schema", {}), raw_doc)
                    request_body = {
                        "type": "object",
                        "properties": schema.get("properties", {}),
                        "required": schema.get("required", []),
                    }
                # OpenAPI 3.0 requestBody
                rb = operation.get("requestBody", {})
                if rb:
                    content = rb.get("content", {}).get("application/json", {})
                    schema = self._resolve_schema(content.get("schema", {}), raw_doc)
                    request_body = {
                        "type": "object",
                        "properties": schema.get("properties", {}),
                        "required": schema.get("required", []),
                    }

                # 解析响应
                responses = {}
                for code, resp in operation.get("responses", {}).items():
                    resp_schema = resp.get("schema", {})
                    # OpenAPI 3.0
                    resp_content = resp.get("content", {}).get("application/json", {})
                    if resp_content:
                        resp_schema = resp_content.get("schema", {})
                    resp_schema = self._resolve_schema(resp_schema, raw_doc)
                    responses[code] = {
                        "description": resp.get("description", ""),
                        "type": resp_schema.get("type", "object"),
                        "properties": resp_schema.get("properties", {}),
                    }

                # 生成用例骨架
                case_skeleton = self._generate_case_skeleton(
                    method.upper(),
                    base_path + path,
                    operation.get("summary", ""),
                    params_info,
                    request_body,
                    responses,
                )

                api_info = {
                    "path": base_path + path,
                    "method": method.upper(),
                    "summary": operation.get("summary", ""),
                    "description": operation.get("description", ""),
                    "tags": operation.get("tags", []),
                    "parameters": params_info,
                    "request_body": request_body,
                    "responses": responses,
                    "case_skeleton": case_skeleton,
                }
                apis.append(api_info)

        return apis

    def _generate_case_skeleton(self, method: str, path: str, summary: str,
                                 params: list, body: dict, responses: dict) -> dict:
        """生成 pytest 用例骨架代码"""
        # 生成函数名
        func_name = summary.strip() if summary else path.strip("/")
        func_name = re.sub(r'[^\w]', '_', func_name).strip('_').lower()
        func_name = f"test_{func_name}" if not func_name.startswith("test_") else func_name

        # 路径参数
        path_params = [p for p in params if p["in"] == "path"]
        query_params = [p for p in params if p["in"] == "query"]

        # 请求体
        body_example = {}
        if body.get("properties"):
            for name, prop in body["properties"].items():
                if isinstance(prop, dict):
                    ptype = prop.get("type", "string")
                    if ptype == "integer":
                        body_example[name] = 1
                    elif ptype == "boolean":
                        body_example[name] = False
                    elif ptype == "array":
                        body_example[name] = []
                    else:
                        body_example[name] = "<TODO>"
                else:
                    body_example[name] = "<TODO>"

        # 构建代码
        lines = [
            f'"""',
            f'{method} {path} - {summary}' if summary else f'{method} {path}',
            f'"""',
            '',
        ]

        # 替换路径参数
        url_path = path
        for p in path_params:
            url_path = url_path.replace(f'{{{p["name"]}}}', f'<{p["name"]}>')

        if body_example:
            lines.append(f'resp = client.{method.lower()}("{url_path}", data={json.dumps(body_example, indent=4, ensure_ascii=False)})')
        else:
            lines.append(f'resp = client.{method.lower()}("{url_path}")')

        # 断言
        expected_code = next((c for c in responses.keys() if c.startswith("2")), "200")
        lines.append(f'assert resp["code"] == {expected_code}')
        lines.append('')

        return {
            "func_name": func_name,
            "code": "\n".join(lines),
            "body_example": body_example,
        }

    async def parse_url(self, url: str) -> list[dict]:
        """从 URL 获取并解析 Swagger 文档"""
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "yaml" in content_type or url.endswith((".yaml", ".yml")):
            import yaml
            raw = yaml.safe_load(resp.text)
        else:
            raw = resp.json()

        return self.parse(raw)

    def parse_file(self, content: bytes, filename: str) -> list[dict]:
        """解析文件内容"""
        if filename.endswith((".yaml", ".yml")):
            import yaml
            raw = yaml.safe_load(content.decode("utf-8"))
        else:
            raw = json.loads(content.decode("utf-8"))
        return self.parse(raw)


# 全局实例
parser = SwaggerParser()
