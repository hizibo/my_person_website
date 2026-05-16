"""
测试执行器
通过 subprocess 调用 pytest，捕获输出并解析结果
"""
import asyncio
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Optional

from test_engine.engine.task_queue import Task, TaskStatus, get_queue

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
    task.logs.append(f"[执行] {' '.join(cmd)}")

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
    task.logs.append(f"[启动] PID={proc.pid}")

    # 流式读取 stdout 和 stderr
    async def read_stream(stream, label):
        while True:
            try:
                line = await asyncio.wait_for(stream.readline(), timeout=60)
            except asyncio.TimeoutError:
                task.logs.append(f"[{label}] 无输出 60s，可能卡住")
                continue
            if not line:
                break
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                task.logs.append(f"[{label}] {text}")
                _notify_progress(task, text)

    # 同时读取 stdout 和 stderr
    await asyncio.gather(
        read_stream(proc.stdout, "OUT"),
        read_stream(proc.stderr, "ERR"),
    )

    # 等待进程结束
    return_code = await proc.wait()
    task.result["exit_code"] = return_code
    task.logs.append(f"[完成] exit_code={return_code}")

    # 解析 pytest 输出
    total, passed, failed, errors, skipped = _parse_pytest_summary(task.logs)

    task.result.update({
        "total": total,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "skipped": skipped,
        "pass_rate": round(passed / total * 100, 2) if total > 0 else 0,
    })

    if return_code == 0:
        task.status = TaskStatus.PASS
    else:
        task.status = TaskStatus.FAIL

    task.finished_at = time.time()
    get_queue()._notify(task)


def _notify_progress(task: Task, line: str):
    """将日志行推送给 WebSocket 订阅者"""
    queue = get_queue()
    payload = {
        "type": "log",
        "task_id": task.id,
        "line": line,
        "status": task.status.value,
    }
    for sub in queue._subscribers.get(task.id, []):
        try:
            sub.put_nowait(payload)
        except asyncio.QueueFull:
            pass


def _parse_pytest_summary(logs: list[str]) -> tuple:
    """从日志中解析 pytest 汇总行，返回 (total, passed, failed, errors, skipped)"""
    total = passed = failed = errors = skipped = -1  # -1 表示未解析到
    for line in reversed(logs):
        if "=" in line and ("passed" in line or "failed" in line or "error" in line):
            # e.g. "====== 5 passed, 1 failed, 2 warnings in 10.23s ======"
            m = re.findall(r'(\d+)\s+(\w+)', line)
            for count, status in m:
                c = int(count)
                if status in ("passed", "pass"):
                    passed = c
                elif status in ("failed", "fail"):
                    failed = c
                elif status in ("error", "errors"):
                    errors = c
                elif status in ("skipped", "skip"):
                    skipped = c
            if passed >= 0 or failed >= 0:
                total = (passed if passed >= 0 else 0) + (failed if failed >= 0 else 0) + (errors if errors >= 0 else 0) + (skipped if skipped >= 0 else 0)
            break
    # 如果解析失败，尝试从 result 中推断
    if total < 0:
        total = passed = failed = errors = skipped = 0
    return total, passed, failed, errors, skipped