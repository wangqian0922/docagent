from typing import List, Dict, Optional
import numpy as np
from app.services.rag import rag_service
from app.services.bm25_retriever import bm25_retriever
from app.config import settings


class HybridRetriever:
    def __init__(self):
        self.bm25_weight = settings.bm25_weight
        self.vector_weight = settings.vector_weight
        self.hybrid_top_k = settings.hybrid_top_k
        self.rerank_top_k = settings.rerank_top_k
    
    def retrieve(self, query: str, knowledge_base_id: str = "default") -> List[Dict]:
        vector_results = self._vector_retrieve(query, knowledge_base_id)
        bm25_results = self._bm25_retrieve(query, knowledge_base_id)
        
        merged_results = self._merge_results(vector_results, bm25_results)
        
        reranked = self._rerank(query, merged_results)
        
        return reranked[:self.rerank_top_k]
    
    def _vector_retrieve(self, query: str, knowledge_base_id: str) -> List[Dict]:
        retriever = rag_service.get_retriever(k=self.hybrid_top_k, knowledge_base_id=knowledge_base_id)
        if not retriever:
            return []
        
        try:
            docs = retriever.invoke(query)
            results = []
            for i, doc in enumerate(docs):
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "vector_score": 1.0 / (i + 1),
                    "source": "vector"
                })
            return results
        except:
            return []
    
    def _bm25_retrieve(self, query: str, knowledge_base_id: str) -> List[Dict]:
        try:
            from langchain_chroma import Chroma
            from langchain_huggingface import HuggingFaceEmbeddings
            
            embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
            persist_dir = rag_service._get_persist_directory(knowledge_base_id)
            
            if not persist_dir or not hasattr(persist_dir, '__iter__'):
                return []
                
            vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=embeddings
            )
            
            all_docs = vectorstore.get()
            
            if not all_docs or not all_docs.get("documents"):
                return []
            
            chunks = []
            for i, content in enumerate(all_docs["documents"]):
                chunks.append({
                    "content": content,
                    "metadata": all_docs["metadatas"][i] if all_docs.get("metadatas") else {}
                })
            
            bm25_retriever.build_index(chunks, knowledge_base_id)
            bm25_results = bm25_retriever.search(query, top_k=self.hybrid_top_k)
            
            for r in bm25_results:
                r["source"] = "bm25"
            
            return bm25_results
        except Exception as e:
            return []
    
    def _merge_results(self, vector_results: List[Dict], bm25_results: List[Dict]) -> List[Dict]:
        merged = {}
        
        for result in vector_results:
            key = result["content"][:100]
            if key not in merged:
                merged[key] = {
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "vector_score": result.get("vector_score", 0),
                    "bm25_score": 0,
                    "sources": []
                }
            merged[key]["vector_score"] = result.get("vector_score", 0)
            merged[key]["sources"].append("vector")
        
        for result in bm25_results:
            key = result["content"][:100]
            if key not in merged:
                merged[key] = {
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "vector_score": 0,
                    "bm25_score": result.get("score", 0),
                    "sources": []
                }
            merged[key]["bm25_score"] = result.get("score", 0)
            merged[key]["sources"].append("bm25")
        
        for key in merged:
            vec_score = merged[key]["vector_score"]
            bm25_score = merged[key]["bm25_score"]
            
            vec_norm = vec_score / (vec_score + bm25_score + 0.001)
            bm25_norm = bm25_score / (vec_score + bm25_score + 0.001)
            
            merged[key]["combined_score"] = (
                vec_norm * self.vector_weight + 
                bm25_norm * self.bm25_weight
            )
        
        results = list(merged.values())
        results.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return results
    
    def _rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        if not results:
            return []
        
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            from sklearn.metrics.pairwise import cosine_similarity
            
            embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
            
            query_embedding = embeddings.embed_query(query)
            doc_embeddings = embeddings.embed_documents([r["content"] for r in results])
            
            similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
            
            for i, result in enumerate(results):
                result["rerank_score"] = float(similarities[i])
                result["final_score"] = (
                    result["combined_score"] * 0.5 + 
                    float(similarities[i]) * 0.5
                )
            
            results.sort(key=lambda x: x["final_score"], reverse=True)
        except:
            results.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return results


hybrid_retriever = HybridRetriever()
