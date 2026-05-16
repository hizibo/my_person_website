"""
断言库
提供常用断言方法，失败时带清晰错误信息
"""
import re
import json
from typing import Any, List


class AssertionError(Exception):
    pass


def _fail(msg: str):
    raise AssertionError(msg)


def assert_equal(actual: Any, expected: Any, desc: str = ""):
    label = f" [{desc}]" if desc else ""
    if actual != expected:
        _fail(f"相等断言失败{label}: 期望={expected!r}, 实际={actual!r}")


def assert_not_equal(actual: Any, expected: Any, desc: str = ""):
    label = f" [{desc}]" if desc else ""
    if actual == expected:
        _fail(f"不等断言失败{label}: 值均为={expected!r}")


def assert_contains(haystack: Any, needle: Any, desc: str = ""):
    label = f" [{desc}]" if desc else ""
    if isinstance(haystack, str) and isinstance(needle, str):
        if needle not in haystack:
            _fail(f"包含断言失败{label}: '{needle}' 不在 '{haystack[:200]}' 中")
    elif hasattr(haystack, "__contains__"):
        if needle not in haystack:
            _fail(f"包含断言失败{label}: {needle!r} 不在集合中")
    else:
        _fail(f"不支持的类型: {type(haystack)}")


def assert_not_contains(haystack: Any, needle: Any, desc: str = ""):
    label = f" [{desc}]" if desc else ""
    if isinstance(haystack, str) and isinstance(needle, str):
        if needle in haystack:
            _fail(f"不包含断言失败{label}: '{needle}' 出现在 '{haystack[:200]}' 中")
    elif hasattr(haystack, "__contains__"):
        if needle in haystack:
            _fail(f"不包含断言失败{label}: {needle!r} 在集合中")
    else:
        _fail(f"不支持的类型: {type(haystack)}")


def assert_true(value: Any, desc: str = ""):
    label = f" [{desc}]" if desc else ""
    if not value:
        _fail(f"为真断言失败{label}: 值为 {value!r}")


def assert_false(value: Any, desc: str = ""):
    label = f" [{desc}]" if desc else ""
    if value:
        _fail(f"为假断言失败{label}: 值为 {value!r}")


def assert_code(response: dict, expected_code: int, desc: str = ""):
    label = f" [{desc}]" if desc else ""
    actual = response.get("code")
    if actual != expected_code:
        msg = response.get("message", "")
        _fail(f"响应码断言失败{label}: 期望={expected_code}, 实际={actual}, 消息={msg}")


def assert_length(obj: Any, expected_length: int, desc: str = ""):
    label = f" [{desc}]" if desc else ""
    actual = len(obj)
    if actual != expected_length:
        _fail(f"长度断言失败{label}: 期望={expected_length}, 实际={actual}")


def assert_regex(text: str, pattern: str, desc: str = ""):
    label = f" [{desc}]" if desc else ""
    if not re.search(pattern, text):
        _fail(f"正则断言失败{label}: '{pattern}' 不匹配 '{text[:200]}'")


def assert_json_schema(data: dict, schema: dict, desc: str = ""):
    """简易 JSON Schema 校验"""
    label = f" [{desc}]" if desc else ""

    def _check(d, s, path="$"):
        if "type" in s:
            expected_type = s["type"]
            if expected_type == "object" and not isinstance(d, dict):
                _fail(f"类型断言失败{label}: {path} 期望 object")
            elif expected_type == "array" and not isinstance(d, list):
                _fail(f"类型断言失败{label}: {path} 期望 array")
            elif expected_type == "string" and not isinstance(d, str):
                _fail(f"类型断言失败{label}: {path} 期望 string")
            elif expected_type == "number" and not isinstance(d, (int, float)):
                _fail(f"类型断言失败{label}: {path} 期望 number")
            elif expected_type == "boolean" and not isinstance(d, bool):
                _fail(f"类型断言失败{label}: {path} 期望 boolean")

        if "required" in s and isinstance(d, dict):
            for key in s["required"]:
                if key not in d:
                    _fail(f"必填字段缺失{label}: {path}.{key}")

        if "properties" in s and isinstance(d, dict):
            for key, sub_schema in s["properties"].items():
                if key in d:
                    _check(d[key], sub_schema, f"{path}.{key}")

        if "items" in s and isinstance(d, list):
            for i, item in enumerate(d):
                _check(item, s["items"], f"{path}[{i}]")

    _check(data, schema)


def assert_success(response: dict, desc: str = ""):
    """断言接口响应成功（code == 200）"""
    assert_code(response, 200, desc)


def assert_data_not_empty(response: dict, desc: str = ""):
    """断言响应 data 字段不为空"""
    label = f" [{desc}]" if desc else ""
    data = response.get("data")
    if data is None or (isinstance(data, (list, str, dict)) and len(data) == 0):
        _fail(f"data 为空断言失败{label}")
