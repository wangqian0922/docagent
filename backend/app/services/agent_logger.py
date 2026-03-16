import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class AgentLogger:
    def __init__(self, log_dir: str = "./logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "agent_calls.jsonl")
    
    def log_tool_call(self, tool_name: str, input_data: str, output_data: str, 
                      success: bool, error: Optional[str] = None, duration: float = 0):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "input": input_data[:500] if input_data else "",
            "output": output_data[:1000] if output_data else "",
            "success": success,
            "error": error,
            "duration_seconds": duration
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        
        logger.info(f"Tool call: {tool_name}, Success: {success}, Duration: {duration:.2f}s")
    
    def get_recent_logs(self, limit: int = 50) -> List[Dict]:
        if not os.path.exists(self.log_file):
            return []
        
        logs = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except:
                    continue
        
        return logs[-limit:]


agent_logger = AgentLogger()
