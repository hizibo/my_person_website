"""
性能测试脚本（Locust）
运行方式:
  单机: locust -f perf/locustfile.py --host=http://175.178.98.241
  无头: locust -f perf/locustfile.py --host=http://175.178.98.241 --headless -u 100 -r 10 -t 60s
"""
from locust import HttpUser, task, between
import random


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)
    _token = None

    def on_start(self):
        resp = self.client.post("/api/login", json={
            "username": "admin",
            "password": "<password>",
        })
        try:
            data = resp.json()
            token = data.get("data", {}).get("token", "")
            if token:
                self._token = token
                self.client.headers["Authorization"] = f"Bearer {token}"
        except Exception:
            pass

    @task(5)
    def browse_plan(self):
        self.client.get("/api/plan/list")

    @task(5)
    def browse_notes(self):
        self.client.get("/api/note/list")

    @task(2)
    def browse_favorites(self):
        self.client.get("/api/favorite/list")

    @task(1)
    def create_note(self):
        self.client.post("/api/note/add", json={
            "title": f"perf_test_{random.randint(1, 9999)}",
            "content": "performance test",
            "categoryId": 1,
        })
