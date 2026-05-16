"""
HTTP 请求封装
自动管理 Cookie/Token/Header，统一错误处理
"""
import json
import time
import requests
from typing import Optional, Any


class HttpClient:
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._token = None
        self._last_resp = None

    @property
    def last_response(self):
        return self._last_resp

    def set_token(self, token: str, scheme: str = "Bearer"):
        self.session.headers["Authorization"] = f"{scheme} {token}"
        self._token = token

    def set_header(self, key: str, value: str):
        self.session.headers[key] = value

    def remove_header(self, key: str):
        self.session.headers.pop(key, None)

    def _full_url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        return f"{self.base_url}{path}"

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = self._full_url(path)
        kwargs.setdefault("timeout", self.timeout)

        start = time.time()
        try:
            resp = self.session.request(method, url, **kwargs)
            self._last_resp = resp
            elapsed = int((time.time() - start) * 1000)

            # 尝试解析 JSON
            try:
                data = resp.json()
            except ValueError:
                data = {"_raw": resp.text}

            # 记录请求日志（简要）
            from common.logger import get_logger
            log = get_logger("http")
            log.debug(
                "%s %s → %d (%dms)",
                method.upper(), path, resp.status_code, elapsed,
            )

            if resp.status_code >= 400:
                detail = data if isinstance(data, str) else data.get("message", resp.text[:200])
                raise HttpError(resp.status_code, detail, data)

            return data if isinstance(data, dict) else {"data": data}

        except requests.RequestException as e:
            raise HttpError(0, f"请求失败: {str(e)}", None) from e

    def get(self, path: str, params: dict = None, **kwargs) -> dict:
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path: str, data: dict = None, json_data: dict = None, **kwargs) -> dict:
        if json_data:
            kwargs["json"] = json_data
        elif data:
            kwargs["json"] = data
        return self._request("POST", path, **kwargs)

    def put(self, path: str, data: dict = None, **kwargs) -> dict:
        if data:
            kwargs["json"] = data
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> dict:
        return self._request("DELETE", path, **kwargs)

    def upload(self, path: str, file_path: str, field_name: str = "file", extra_data: dict = None) -> dict:
        url = self._full_url(path)
        with open(file_path, "rb") as f:
            files = {field_name: f}
            resp = self.session.post(url, files=files, data=extra_data or {}, timeout=self.timeout)
        self._last_resp = resp
        try:
            return resp.json()
        except ValueError:
            return {"_raw": resp.text}

    def close(self):
        self.session.close()


class HttpError(Exception):
    def __init__(self, status_code: int, message: str, data: Any = None):
        self.status_code = status_code
        self.message = message
        self.data = data
        super().__init__(f"HTTP {status_code}: {message}")
