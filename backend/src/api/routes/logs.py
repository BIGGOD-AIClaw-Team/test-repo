from fastapi import APIRouter, Query
from pathlib import Path
import json

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("/")
async def list_logs(
    logger: str = Query(None, description="日志器名称"),
    level: str = Query(None, description="日志级别"),
    limit: int = Query(100, description="返回条数"),
):
    """查询日志"""
    log_dir = Path("./logs")
    if not log_dir.exists():
        return {"logs": []}
    
    logs = []
    for log_file in sorted(log_dir.glob("*.jsonl"), reverse=True)[:1]:
        with open(log_file) as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    if logger and log_entry.get("logger") != logger:
                        continue
                    if level and log_entry.get("level") != level.upper():
                        continue
                    logs.append(log_entry)
                    if len(logs) >= limit:
                        break
                except:
                    continue
    
    return {"logs": logs}
