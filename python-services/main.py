"""
Python 工具服务 - 统一入口
所有工具路由在此挂载，后续新增工具只需添加 router 模块
"""
import sys
import os
# 确保 test_engine 作为包可被导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from xmind_parser.main import router as xmind_router
from data_generator.main import router as datagen_router
from test_engine.engine import router as test_engine_router

app = FastAPI(title="Python工具服务", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载各工具路由
app.include_router(xmind_router, prefix="/xmind", tags=["XMind解析"])
app.include_router(datagen_router, prefix="/datagen", tags=["批量数据生成"])
app.include_router(test_engine_router, prefix="/test-engine", tags=["测试引擎"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "python-tools", "modules": ["xmind", "datagen", "test-engine"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
