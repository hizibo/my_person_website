"""
测试执行器
通过 subprocess 调用 pytest，捕获输出并解析结果
"""
import asyncio
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Optional

from engine.task_queue import Task, TaskStatus, get_queue

_ENGINE_ROOT = Path(__file__).parent.parent


async def run_tests(task: Task) -> None:
    """
    执行测试任务
    task.result 中的字段：
      - module: str (api/ui/perf)
      - test_path: str (具体测试文件或目录，可选)
      - case_ids: list[str] (具体用例名，可选)
    """
    opts = task.result
    module = opts.get("module", "api")
    test_path = opts.get("test_path", "")
    case_filter = opts.get("case_ids", [])
    env = opts.get("env", "dev")

    # 构建 pytest 命令
    cmd = ["pytest"]

    if test_path:
        target = _ENGINE_ROOT / test_path
    else:
        target = _ENGINE_ROOT / module

    cmd.append(str(target))

    cmd.extend(["-v", "--tb=short", f"--alluredir={_ENGINE_ROOT}/reports/allure-results"])

    if case_filter:
        cmd.extend(["-k", " or ".join(case_filter)])

    task.result["command"] = " ".join(cmd)

    # 执行
    env_vars = {**os.environ, "TEST_ENV": env, "PYTHONPATH": str(_ENGINE_ROOT)}

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=str(_ENGINE_ROOT),
        env=env_vars,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    task.result["pid"] = proc.pid

    # 流式读取 stdout
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        text = line.decode("utf-8", errors="replace").rstrip()
        if text:
            task.logs.append(text)
            # 推送通知
            _notify_progress(task, text)

    # 等待完成
    await proc.wait()
    stderr_text = (await proc.stderr.read()).decode("utf-8", errors="replace")

    # 解析 pytest 输出
    total, passed, failed, errors, skipped = _parse_pytest_summary(task.logs)

    task.result.update({
        "exit_code": proc.returncode,
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "pass_rate": round(passed / total * 100, 2) if total > 0 else 0,
    })

    if proc.returncode == 0:
        task.status = TaskStatus.PASS
    else:
        task.status = TaskStatus.FAIL
        task.result["stderr_tail"] = stderr_text[-1000:]

    task.finished_at = time.time()
    get_queue()._notify(task)


def _parse_pytest_summary(logs: list[str]) -> tuple:
    """从日志中解析 pytest 汇总行"""
    total = passed = failed = errors = skipped = 0
    for line in reversed(logs):
        if "=" in line and ("passed" in line or "failed" in line):
            # e.g. "====== 5 passed, 1 failed, 2 warnings in 10.23s ======"
            m = re.findall(r'(\d+)\s+(\w+)', line)
            for count, status in m:
                c = int(count)
                if status == "passed":
                    passed = c
                elif status == "failed":
                    failed = c
                elif status == "error" or status == "errors":
                    errors = c
                elif status == "skipped":
                    skipped = c
            total = passed + failed + errors + skipped
            break
    return total, passed, failed, errors, skipped


def _notify_progress(task: Task, line: str):
    """将日志行推送给 WebSocket 订阅者"""
    import re
    queue = get_queue()
    for sub in queue._subscribers.get(task.id, []):
        try:
            sub.put_nowait({
                "type": "log",
                "task_id": task.id,
                "line": line,
                "status": task.status.value,
            })
        except asyncio.QueueFull:
            pass
