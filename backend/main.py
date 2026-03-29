from fastapi import FastAPI
from src.api.middleware import TracingMiddleware
from src.api.routes import logs

app = FastAPI(title="Trace & Log Service", version="1.2.0")

# 注册追踪中间件
app.add_middleware(TracingMiddleware)

# 注册路由
app.include_router(logs.router)

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.2.0"}

@app.get("/")
async def root():
    return {"message": "Trace & Log Service", "version": "1.2.0"}
