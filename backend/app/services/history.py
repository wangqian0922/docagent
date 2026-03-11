import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from app.config import settings


class ChatHistoryManager:
    def __init__(self, history_file: Optional[str] = None):
        self.history_file = history_file or settings.history_file
        self.history: List[Dict] = self._load()
    
    def _load(self) -> List[Dict]:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def add_user_message(self, content: str):
        self.history.append({
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
    
    def add_ai_message(self, content: str):
        self.history.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save()
    
    def get_recent(self, n: int = 10) -> List[Dict]:
        return self.history[-n:] if len(self.history) > n else self.history
    
    def clear(self):
        self.history = []
        self._save()
    
    def undo(self) -> bool:
        if len(self.history) < 2:
            return False
        self.history = self.history[:-2]
        self._save()
        return True
    
    def to_langchain_messages(self) -> List:
        messages = []
        for msg in self.history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        return messages
    
    def get_history_text(self, max_chars: int = 2000) -> str:
        if not self.history:
            return "无历史对话"
        
        history_text = "\n".join([
            f"用户: {m['content']}" if m["role"] == "user" 
            else f"助手: {m['content']}"
            for m in self.history
        ])
        
        if len(history_text) > max_chars:
            return history_text[-max_chars:]
        return history_text


history_manager = ChatHistoryManager()
