"""
XMind 解析服务
依赖: pip install fastapi uvicorn xmindparser2 openpyxl
启动: uvicorn main:app --reload --port 8001
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import json
import zipfile
import io
from typing import Optional

app = FastAPI(title="XMind解析服务", version="1.0.0")

# CORS 允许前端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ParseResponse(BaseModel):
    cases: list
    mindmap: dict
    message: str = "success"


def extract_cases_from_content(content: dict, path: list = None) -> list:
    """递归遍历XMind content.json，提取测试用例"""
    if path is None:
        path = []

    cases = []
    title = content.get("title", "")
    topics = content.get("topics", [])

    if not title:
        return cases

    current_path = path + [title]

    if not topics:
        # 叶子节点 = 一条测试用例
        test_case = build_test_case(current_path)
        cases.append(test_case)
    else:
        for topic in topics:
            cases.extend(extract_cases_from_content(topic, current_path))

    return cases


def build_test_case(path: list) -> dict:
    """根据思维导图路径构建测试用例"""
    size = len(path)
    tc = {
        "module": path[0] if size >= 1 else "",
        "feature": path[1] if size >= 2 else "",
        "caseName": path[-1] if size >= 1 else "未命名",
        "priority": "P0" if size <= 2 else ("P1" if size == 3 else "P2"),
        "precondition": "测试环境已就绪",
        "steps": " -> ".join(path[2:]) if size > 2 else "按需求执行测试",
        "expected": "功能正常运行"
    }
    return tc


def parse_xmind_file(file_bytes: bytes) -> dict:
    """解析XMind文件（ZIP格式）"""
    cases = []
    mindmap = {}

    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
            # 查找content.json
            content_json = None
            for name in zf.namelist():
                if name.endswith("content.json"):
                    with zf.open(name) as f:
                        content_json = json.loads(f.read().decode("utf-8"))
                    break

            if not content_json:
                raise ValueError("未找到content.json，文件格式可能不支持")

            # 递归提取用例
            # XMind 8+ 格式
            if "sheet" in content_json:
                for sheet in content_json["sheet"]:
                    root_topic = sheet.get("rootTopic", {})
                    sheet_cases = extract_cases_from_content(root_topic)
                    cases.extend(sheet_cases)
            elif "topic" in content_json:
                # XMind 7/8 另一种格式
                cases = extract_cases_from_content(content_json.get("topic", {}))
            elif isinstance(content_json, dict):
                cases = extract_cases_from_content(content_json)

            mindmap["raw"] = content_json

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析失败: {str(e)}")

    return {
        "cases": cases,
        "mindmap": mindmap
    }


@app.post("/parse-xmind", response_model=ParseResponse)
async def parse_xmind(file: UploadFile = File(...)):
    """解析XMind文件，转换为测试用例"""
    if not file.filename.endswith(".xmind"):
        raise HTTPException(status_code=400, detail="只支持.xmind格式文件")

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="文件内容为空")

    result = parse_xmind_file(file_bytes)
    return ParseResponse(
        cases=result["cases"],
        mindmap=result["mindmap"],
        message=f"成功解析 {len(result['cases'])} 条测试用例"
    )


@app.post("/parse-xmind-base64")
async def parse_xmind_base64(body: dict):
    """接收Base64编码的XMind文件"""
    try:
        file_bytes = base64.b64decode(body.get("file", ""))
    except Exception:
        raise HTTPException(status_code=400, detail="Base64解码失败")

    result = parse_xmind_file(file_bytes)
    return {
        "cases": result["cases"],
        "mindmap": result["mindmap"],
        "message": f"成功解析 {len(result['cases'])} 条测试用例"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "xmind-parser"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
