from rank_bm25 import BM25Okapi
from typing import List, Dict, Optional
import os
import json
import re
from app.config import settings


class BM25Retriever:
    def __init__(self):
        self.bm25_index: Optional[BM25Okapi] = None
        self.documents: List[Dict] = []
        self.corpus: List[str] = []
    
    def build_index(self, chunks: List[Dict], knowledge_base_id: str = "default"):
        self.corpus = [chunk.get("content", "") for chunk in chunks]
        self.documents = chunks
        
        if self.corpus:
            self.bm25_index = BM25Okapi(self.corpus)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        if not self.bm25_index or not self.corpus:
            return []
        
        query_tokens = self._tokenize(query)
        scores = self.bm25_index.get_scores(query_tokens)
        
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    "content": self.documents[idx].get("content", ""),
                    "metadata": self.documents[idx].get("metadata", {}),
                    "score": scores[idx],
                    "rank": len(results) + 1
                })
        
        return results
    
    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        return text.split()
    
    def clear(self):
        self.bm25_index = None
        self.documents = []
        self.corpus = []


bm25_retriever = BM25Retriever()
