"""
XMind 解析服务
依赖: pip install fastapi uvicorn openpyxl
启动: 通过 main.py 统一入口，端口 8001

层级结构约定：
  Level 1 = 项目名称（根节点，不生成用例）
  Level 2 = 模块
  Level 3 = 预置条件
  Level 4 = 测试步骤
  Level 5+ = 预期结果

用例名 = 预置条件_测试步骤_预期结果（下划线连接）
层数不足4层（缺少步骤或预期结果）的分支跳过，返回识别数/转换数统计
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import json
import zipfile
import io
from typing import Optional

from fastapi import APIRouter

router = APIRouter()


class ParseResponse(BaseModel):
    cases: list
    mindmap: dict
    recognizedCount: int = 0
    convertedCount: int = 0
    message: str = "success"


# 全局计数器（每次请求重置）
_recognized = 0
_converted = 0


def get_children(node: dict) -> list:
    """提取子主题列表，兼容多种 XMind 格式"""
    topics = node.get("topics", [])
    if isinstance(topics, list):
        return topics
    if isinstance(topics, dict):
        # XMind Zen 格式: { "topics": { "attached": [...] } }
        attached = topics.get("attached", [])
        if isinstance(attached, list):
            return attached
    return []


def extract_cases_from_content(node: dict, path: list = None) -> list:
    """递归遍历 XMind content.json，提取测试用例"""
    global _recognized, _converted

    if path is None:
        path = []

    cases = []

    if not isinstance(node, dict):
        return cases

    title = node.get("title", "")
    if not title:
        # 处理 rootTopic 包裹
        root_topic = node.get("rootTopic")
        if root_topic and isinstance(root_topic, dict):
            return extract_cases_from_content(root_topic, path)
        return cases

    current_path = path + [title]
    children = get_children(node)

    if not children:
        # 叶子节点 —— 判断是否满足用例结构
        # path 索引: 0=项目, 1=模块, 2=预置条件, 3=测试步骤, 4+=预期结果
        if len(current_path) >= 3:
            # 识别到（至少有 预置条件 层）
            _recognized += 1

        tc = build_test_case(current_path)
        if tc is not None:
            _converted += 1
            cases.append(tc)
        # 层数不足的跳过
    else:
        for child in children:
            cases.extend(extract_cases_from_content(child, current_path))

    return cases


def build_test_case(path: list) -> dict | None:
    """
    根据路径构建测试用例

    层级映射（path index 从 0 开始）：
      path[0] = Level 1 项目名称（不参与用例名拼接）
      path[1] = Level 2 模块
      path[2] = Level 3 预置条件
      path[3] = Level 4 测试步骤
      path[4+] = Level 5+ 预期结果（取最深一层）

    用例名 = 预置条件_测试步骤_预期结果

    不足4层返回 None（跳过）
    """
    if len(path) < 4:
        return None

    module = path[1]       # 模块
    prereq = path[2]       # 预置条件
    step = path[3]         # 测试步骤
    expected = path[-1]    # 预期结果（最深一层）

    # 优先级：去掉根节点后层数
    depth = len(path) - 1
    if depth <= 3:
        priority = "P0"
    elif depth == 4:
        priority = "P1"
    else:
        priority = "P2"

    return {
        "module": module,
        "feature": prereq,
        "caseName": f"{prereq}_{step}_{expected}",
        "priority": priority,
        "precondition": prereq,
        "steps": step,
        "expected": expected,
    }


def parse_xmind_file(file_bytes: bytes) -> dict:
    """解析 XMind 文件（ZIP 格式）"""
    global _recognized, _converted
    _recognized = 0
    _converted = 0

    cases = []
    mindmap = {}

    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            # 查找 content.json
            content_json = None
            for name in zf.namelist():
                if name.endswith("content.json"):
                    with zf.open(name) as f:
                        content_json = json.loads(f.read().decode("utf-8"))
                    break

            if not content_json:
                raise ValueError("未找到 content.json，文件格式可能不支持")

            mindmap["raw"] = content_json

            # XMind 8+ 格式: content.json 是 sheet 数组
            if isinstance(content_json, list):
                for sheet in content_json:
                    root_topic = sheet.get("rootTopic")
                    if root_topic:
                        cases.extend(extract_cases_from_content(root_topic, []))
                    else:
                        cases.extend(extract_cases_from_content(sheet, []))
            elif isinstance(content_json, dict):
                # 兼容其他格式
                if "rootTopic" in content_json:
                    cases = extract_cases_from_content(content_json["rootTopic"], [])
                else:
                    cases = extract_cases_from_content(content_json, [])

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析失败: {str(e)}")

    return {
        "cases": cases,
        "mindmap": mindmap,
        "recognizedCount": _recognized,
        "convertedCount": _converted,
    }


@router.post("/parse-xmind", response_model=ParseResponse)
async def parse_xmind(file: UploadFile = File(...)):
    """解析 XMind 文件，转换为测试用例"""
    if not file.filename.endswith(".xmind"):
        raise HTTPException(status_code=400, detail="只支持 .xmind 格式文件")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="文件内容为空")

    result = parse_xmind_file(file_bytes)
    rc = result["recognizedCount"]
    cc = result["convertedCount"]

    return ParseResponse(
        cases=result["cases"],
        mindmap=result["mindmap"],
        recognizedCount=rc,
        convertedCount=cc,
        message=f"识别 {rc} 条，转换成功 {cc} 条",
    )


@router.post("/parse-xmind-base64")
async def parse_xmind_base64(body: dict):
    """接收 Base64 编码的 XMind 文件（保留兼容）"""
    try:
        file_bytes = base64.b64decode(body.get("file", ""))
    except Exception:
        raise HTTPException(status_code=400, detail="Base64 解码失败")

    result = parse_xmind_file(file_bytes)
    rc = result["recognizedCount"]
    cc = result["convertedCount"]

    return {
        "cases": result["cases"],
        "mindmap": result["mindmap"],
        "recognizedCount": rc,
        "convertedCount": cc,
        "message": f"识别 {rc} 条，转换成功 {cc} 条",
    }


@router.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "xmind-parser"}
