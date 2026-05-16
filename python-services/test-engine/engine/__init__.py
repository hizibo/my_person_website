"""
测试执行引擎 - FastAPI 路由
V2.0 核心：开放 REST/WebSocket 接口，前端直接调用
"""
import json
import os
import uuid
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from test_engine.engine.task_queue import Task, TaskStatus, TaskPriority, get_queue
from test_engine.engine.swagger_parser import SwaggerParser, parser as swagger_parser

router = APIRouter(tags=["测试引擎"])
_ENGINE_ROOT = Path(__file__).parent.parent


# ========== 请求/响应模型 ==========

class ExecuteRequest(BaseModel):
    module: str = "api"
    test_path: str = ""
    case_ids: list[str] = []
    env: str = "dev"
    priority: str = "P1"


class SwaggerUrlRequest(BaseModel):
    url: str


class CaseCreate(BaseModel):
    name: str
    module: str = ""
    method: str = "GET"
    path: str = ""
    headers: str = '{"Content-Type": "application/json"}'
    params: str = ""
    assertions: str = "code == 200"


# ========== 用例存储（内存） ==========
_test_cases: list[dict] = []
_case_counter = 0


def _init_default_cases():
    global _case_counter, _test_cases
    defaults = [
        ("管理员正确登录", "login", "POST", "/api/login", '{"username":"admin","password":"<pwd>"}', "code == 200, data.token != null"),
        ("密码错误登录", "login", "POST", "/api/login", '{"username":"admin","password":"wrong"}', "code != 200"),
        ("未登录访问需认证接口", "login", "GET", "/api/note/list", "", "code == 401"),
        ("创建笔记", "note", "POST", "/api/note/add", '{"title":"测试笔记","content":"内容"}', "code == 200"),
        ("查询笔记列表", "note", "GET", "/api/note/list", "", "code == 200"),
        ("更新笔记", "note", "PUT", "/api/note/update", '{"id":1,"title":"更新"}', "code == 200"),
        ("删除笔记", "note", "DELETE", "/api/note/delete", '{"id":999}', "code != null"),
        ("创建计划", "plan", "POST", "/api/plan/add", '{"title":"测试计划"}', "code == 200"),
        ("查询计划列表", "plan", "GET", "/api/plan/list", "", "code == 200"),
        ("添加收藏", "favorite", "POST", "/api/favorite/add", '{"url":"http://test.com"}', "code == 200"),
        ("查询收藏列表", "favorite", "GET", "/api/favorite/list", "", "code == 200"),
        ("XMind 解析", "tool", "POST", "/api/tool/xmind/parse", "", "code == 200"),
        ("图片上传", "upload", "POST", "/api/upload/image", "", "code == 200"),
    ]
    for name, mod, method, path, params, assertions in defaults:
        _case_counter += 1
        _test_cases.append({
            "id": _case_counter,
            "name": name,
            "module": mod,
            "method": method,
            "path": path,
            "params": params,
            "headers": '{"Content-Type": "application/json"}',
            "assertions": assertions,
            "status": "ready",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        })


_init_default_cases()


# ========== 引擎健康检查 ==========

@router.get("/health")
async def health():
    q = get_queue()
    return {
        "status": "ok",
        "service": "test-engine",
        "version": "2.0.0",
        "running_tasks": q.running_count,
        "queued_tasks": q.queued_count,
    }


# ========== 用例管理 ==========

@router.get("/cases")
async def list_cases(module: str = "", search: str = ""):
    cases = _test_cases
    if module:
        cases = [c for c in cases if c["module"] == module]
    if search:
        s = search.lower()
        cases = [c for c in cases if s in c["name"].lower() or s in c.get("path", "").lower()]
    return {"cases": cases, "total": len(cases)}


@router.post("/cases")
async def create_case(body: CaseCreate):
    global _case_counter
    _case_counter += 1
    case = {
        "id": _case_counter,
        "name": body.name,
        "module": body.module,
        "method": body.method,
        "path": body.path,
        "headers": body.headers,
        "params": body.params,
        "assertions": body.assertions,
        "status": "ready",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _test_cases.append(case)
    return {"case": case, "message": "用例创建成功"}


@router.put("/cases/{case_id}")
async def update_case(case_id: int, body: CaseCreate):
    for c in _test_cases:
        if c["id"] == case_id:
            c.update({
                "name": body.name,
                "module": body.module,
                "method": body.method,
                "path": body.path,
                "headers": body.headers,
                "params": body.params,
                "assertions": body.assertions,
            })
            return {"case": c, "message": "用例更新成功"}
    raise HTTPException(status_code=404, detail="用例不存在")


@router.delete("/cases/{case_id}")
async def delete_case(case_id: int):
    global _test_cases
    _test_cases = [c for c in _test_cases if c["id"] != case_id]
    return {"message": "用例已删除"}


# ========== 执行管理 ==========

@router.post("/execute")
async def start_execute(body: ExecuteRequest):
    q = get_queue()
    task = Task(
        name=f"test-{uuid.uuid4().hex[:8]}",
        priority=TaskPriority(body.priority.upper()),
        result={
            "module": body.module,
            "test_path": body.test_path,
            "case_ids": body.case_ids,
            "env": body.env,
        },
    )

    async def coro(t: Task):
        from test_engine.engine.execute import run_tests
        await run_tests(t)

    task_id = await q.submit(task, coro)
    return {"task_id": task_id, "status": "queued", "message": "任务已提交"}


@router.post("/stop/{task_id}")
async def stop_execute(task_id: str):
    q = get_queue()
    ok = await q.cancel(task_id)
    if ok:
        return {"task_id": task_id, "status": "stopped", "message": "任务已停止"}
    raise HTTPException(status_code=404, detail="任务不存在或已结束")


@router.get("/status/{task_id}")
async def get_status(task_id: str):
    q = get_queue()
    task = q.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task.to_dict()


@router.get("/logs/{task_id}")
async def get_logs(task_id: str, offset: int = 0):
    q = get_queue()
    task = q.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    logs = task.logs[offset:]
    return {"task_id": task_id, "logs": logs, "offset": offset, "has_more": False}


# ========== 报告管理 ==========

_report_dir = _ENGINE_ROOT / "reports"


@router.get("/reports")
async def list_reports():
    reports = []
    html_dir = _report_dir / "html"
    if html_dir.exists():
        for d in sorted(html_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if d.is_dir():
                reports.append({
                    "id": d.name,
                    "name": d.name,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d.stat().st_mtime)),
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "rate": 0,
                })
    # 补充执行记录中的报告数据
    q = get_queue()
    for t in q._tasks.values():
        if t.status in (TaskStatus.PASS, TaskStatus.FAIL):
            reports.append({
                "id": t.id,
                "name": t.name,
                "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t.created_at)),
                "total": t.result.get("total", 0),
                "passed": t.result.get("passed", 0),
                "failed": t.result.get("failed", 0),
                "rate": t.result.get("pass_rate", 0),
            })
    return {"reports": reports}


@router.get("/report/{report_id}")
async def get_report(report_id: str):
    q = get_queue()
    task = q.get(report_id)
    if not task:
        raise HTTPException(status_code=404, detail="报告不存在")
    return task.to_dict()


@router.get("/report/{report_id}/download")
async def download_report(report_id: str):
    zip_path = _report_dir / f"{report_id}.zip"
    if zip_path.exists():
        return FileResponse(zip_path, filename=f"report-{report_id}.zip")
    raise HTTPException(status_code=404, detail="报告文件不存在")


# ========== 环境配置 ==========

@router.get("/envs")
async def list_envs():
    return {
        "envs": [
            {"name": "dev", "label": "开发环境", "base_url": "http://175.178.98.241"},
            {"name": "uat", "label": "UAT 环境", "base_url": "http://uat.example.com"},
            {"name": "prod", "label": "生产环境", "base_url": "http://prod.example.com"},
        ]
    }


# ========== Swagger 导入 ==========

@router.post("/swagger/parse-url")
async def swagger_parse_url(body: SwaggerUrlRequest):
    try:
        apis = await swagger_parser.parse_url(body.url)
        return {"apis": apis, "total": len(apis), "message": f"成功解析 {len(apis)} 个接口"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Swagger 解析失败: {str(e)}")


@router.post("/swagger/parse-file")
async def swagger_parse_file(file: UploadFile = File(...)):
    allowed = (".json", ".yaml", ".yml")
    if not any(file.filename.endswith(ext) for ext in allowed):
        raise HTTPException(status_code=400, detail="仅支持 .json / .yaml / .yml 格式")
    try:
        content = await file.read()
        apis = swagger_parser.parse_file(content, file.filename)
        return {"apis": apis, "total": len(apis), "message": f"成功解析 {len(apis)} 个接口"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {str(e)}")


@router.post("/swagger/generate-cases")
async def swagger_generate_cases(body: dict):
    """将选中的 Swagger API 转为测试用例"""
    apis = body.get("apis", [])
    generated = []
    for api in apis:
        skeleton = api.get("case_skeleton", {})
        if not skeleton:
            continue
        global _case_counter
        _case_counter += 1
        case = {
            "id": _case_counter,
            "name": api.get("summary") or api.get("path", "/"),
            "module": api.get("tags", ["api"])[0] if api.get("tags") else "api",
            "method": api.get("method", "GET"),
            "path": api.get("path", ""),
            "headers": '{"Content-Type": "application/json"}',
            "params": json.dumps(skeleton.get("body_example", {}), ensure_ascii=False),
            "assertions": f"code == 200",
            "status": "draft",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "case_code": skeleton.get("code", ""),
        }
        _test_cases.append(case)
        generated.append(case)
    return {"generated": generated, "total": len(generated), "message": f"成功生成 {len(generated)} 个用例"}


# ========== WebSocket 实时推送 ==========

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(ws: WebSocket, task_id: str):
    q = get_queue()
    task = q.get(task_id)
    if not task:
        await ws.accept()
        await ws.send_json({"error": "任务不存在"})
        await ws.close()
        return

    await ws.accept()
    sub = q.subscribe(task_id)

    # 发送当前状态
    await ws.send_json({"type": "status", "data": task.to_dict()})

    try:
        while True:
            msg = await sub.get()
            await ws.send_json(msg)
    except WebSocketDisconnect:
        pass
    finally:
        q.unsubscribe(task_id, sub)
