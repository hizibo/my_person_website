"""
测试执行器
通过 subprocess 调用 pytest，捕获输出并解析结果
"""
import asyncio
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Optional

from test_engine.engine.task_queue import Task, TaskStatus, get_queue

_ENGINE_ROOT = Path(__file__).parent.parent

# module → pytest 路径映射
_MODULE_PATH_MAP = {
    "login":   "api/test_website/test_login.py",
    "note":    "api/test_website/test_note.py",
    "plan":    "api/test_website/test_plan.py",
    "favorite":"api/test_website/test_favorite.py",
    "upload":  "api/test_website/test_upload.py",
    "tool":    "api/test_website/test_tool.py",
    "api":     "api/",
    "ui":      "ui/",
    "perf":    "perf/",
}


async def run_tests(task: Task) -> None:
    """
    执行测试任务
    task.result 中的字段：
      - module: str (login/note/plan/api/ui/perf)
      - test_path: str (具体测试文件或目录，可选，优先级高于 module)
      - case_ids: list[str] (用例库中的用例 ID 列表，用于读取测试文件路径)
      - env: str (dev/uat/prod)
    """
    opts = task.result
    module = opts.get("module", "api")
    test_path = opts.get("test_path", "")
    case_ids = opts.get("case_ids", [])
    env = opts.get("env", "dev")

    # 确定测试目标路径
    if test_path:
        target = _ENGINE_ROOT / test_path
    elif module in _MODULE_PATH_MAP:
        target = _ENGINE_ROOT / _MODULE_PATH_MAP[module]
    else:
        target = _ENGINE_ROOT / module

    # 构建 pytest 命令
    cmd = ["/usr/local/bin/pytest"]

    # case_ids 可以是：文件路径列表 或 用例名过滤列表
    # 规则：如果包含 "/" 或 ".py"，当作文件路径；否则当作用例名用 -k 过滤
    case_filter = []
    test_files = []

    for cid in case_ids:
        cid = str(cid).strip()
        if not cid:
            continue
        if "/" in cid or "\\" in cid or cid.endswith(".py"):
            # 文件路径
            test_files.append(_ENGINE_ROOT / cid)
        else:
            # 用例名或用例ID，当作 -k 过滤
            case_filter.append(cid)

    # 如果有指定文件，优先用文件；否则用 target
    if test_files:
        for f in test_files:
            cmd.append(str(f))
    else:
        cmd.append(str(target))

    cmd.extend(["-v", "--tb=short", f"--alluredir={_ENGINE_ROOT}/reports/allure-results"])

    if case_filter:
        cmd.extend(["-k", " or ".join(case_filter)])

    full_cmd = " ".join(cmd)
    task.result["command"] = full_cmd
    task.logs.append(f"[执行] {full_cmd}")

    # 打印诊断信息
    task.logs.append(f"[诊断] 目标={target} | module={module} | case_ids={case_ids}")

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
    total = passed = failed = errors = skipped = -1
    for line in reversed(logs):
        # 匹配 "====== 5 passed, 1 failed, 2 warnings in 10.23s ======"
        if "=" in line and ("passed" in line or "failed" in line or "error" in line):
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
    if total < 0:
        total = passed = failed = errors = skipped = 0
    return total, passed, failed, errors, skipped