"""
简单的 FastAPI 后端服务 - 替代 Spring Boot
提供工具列表和 XMind 解析接口
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
import uuid
import datetime

app = FastAPI(title="My Toolbox API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据库
TOOLS_DB = [
    {"id": 1, "name": "XMind转测试用例", "description": "将XMind思维导图转换为标准测试用例格式", "icon": "file-text", "path": "/tools/xmind", "status": 1, "sortOrder": 1},
    {"id": 2, "name": "JSON格式化", "description": "JSON数据格式化、压缩、校验工具", "icon": "code", "path": "/tools/json", "status": 1, "sortOrder": 2},
    {"id": 3, "name": "正则测试", "description": "正则表达式在线测试工具", "icon": "search", "path": "/tools/regex", "status": 1, "sortOrder": 3},
]

TEST_CASES_DB = []

# 数据模型
class Tool(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    path: str
    status: int
    sortOrder: int

class TestCase(BaseModel):
    id: str
    name: str
    precondition: Optional[str] = ""
    steps: List[str] = []
    expected: Optional[str] = ""
    priority: Optional[str] = "P2"
    moduleId: Optional[str] = None
    createdAt: str

class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None

# 工具管理接口
@app.get("/api/tools")
async def get_tools():
    """获取所有工具列表"""
    return ApiResponse(data=TOOLS_DB)

@app.get("/api/tools/{tool_id}")
async def get_tool(tool_id: int):
    """获取单个工具详情"""
    tool = next((t for t in TOOLS_DB if t["id"] == tool_id), None)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return ApiResponse(data=tool)

# XMind 解析接口
@app.post("/api/xmind/parse")
async def parse_xmind(file: UploadFile = File(...)):
    """解析 XMind 文件"""
    import httpx

    # 转发到 Python XMind 服务
    async with httpx.AsyncClient() as client:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        response = await client.post(
            "http://localhost:8001/parse-xmind",
            files=files,
            timeout=30.0
        )
        return response.json()

@app.post("/api/xmind/save")
async def save_test_cases(test_cases: List[dict]):
    """保存测试用例"""
    saved = []
    for tc in test_cases:
        tc["id"] = str(uuid.uuid4())
        tc["createdAt"] = datetime.datetime.now().isoformat()
        TEST_CASES_DB.append(tc)
        saved.append(tc)
    return ApiResponse(data=saved, message=f"成功保存 {len(saved)} 条测试用例")

@app.get("/api/xmind/testcases")
async def get_test_cases():
    """获取所有测试用例"""
    return ApiResponse(data=TEST_CASES_DB)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
