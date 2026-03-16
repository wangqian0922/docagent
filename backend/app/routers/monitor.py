from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import Dict, List
import json
import os
from app.config import settings

router = APIRouter()


class StatsManager:
    def __init__(self):
        self.stats_file = "./logs/stats.json"
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        self._init_stats()
    
    def _init_stats(self):
        if not os.path.exists(self.stats_file):
            self._save_stats({
                "total_requests": 0,
                "total_tokens": 0,
                "total_vector_searches": 0,
                "total_tool_calls": 0,
                "daily_stats": {}
            })
    
    def _load_stats(self) -> Dict:
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "total_requests": 0,
            "total_tokens": 0,
            "total_vector_searches": 0,
            "total_tool_calls": 0,
            "daily_stats": {}
        }
    
    def _save_stats(self, stats: Dict):
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    
    def increment_request(self, tokens: int = 0, vector_searches: int = 0, tool_calls: int = 0):
        stats = self._load_stats()
        stats["total_requests"] += 1
        stats["total_tokens"] += tokens
        stats["total_vector_searches"] += vector_searches
        stats["total_tool_calls"] += tool_calls
        
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in stats["daily_stats"]:
            stats["daily_stats"][today] = {
                "requests": 0,
                "tokens": 0,
                "vector_searches": 0,
                "tool_calls": 0
            }
        
        stats["daily_stats"][today]["requests"] += 1
        stats["daily_stats"][today]["tokens"] += tokens
        stats["daily_stats"][today]["vector_searches"] += vector_searches
        stats["daily_stats"][today]["tool_calls"] += tool_calls
        
        self._save_stats(stats)
    
    def get_stats(self) -> Dict:
        return self._load_stats()
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        stats = self._load_stats()
        result = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            daily = stats["daily_stats"].get(date, {
                "requests": 0,
                "tokens": 0,
                "vector_searches": 0,
                "tool_calls": 0
            })
            result.append({
                "date": date,
                **daily
            })
        
        return result


stats_manager = StatsManager()


@router.get("/stats")
async def get_stats():
    stats = stats_manager.get_stats()
    daily = stats_manager.get_daily_stats(7)
    return {
        "total": stats,
        "daily": daily
    }


@router.post("/stats/increment")
async def increment_stats(
    tokens: int = 0,
    vector_searches: int = 0,
    tool_calls: int = 0
):
    stats_manager.increment_request(
        tokens=tokens,
        vector_searches=vector_searches,
        tool_calls=tool_calls
    )
    return {"success": True}


@router.get("/agent-logs")
async def get_agent_logs(limit: int = 50):
    from app.services.agent_logger import agent_logger
    logs = agent_logger.get_recent_logs(limit)
    return {"logs": logs}
