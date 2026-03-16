# DocAgent - 企业级知识库智能问答系统

## 项目概述

基于 **RAG (Retrieval-Augmented Generation) + Agent + Hybrid Retrieval** 架构的企业级知识库问答系统，支持文档语义检索、工具调用以及流式对话交互。

## 技术栈

- **后端**: FastAPI + LangChain + Chroma + Celery + Redis
- **LLM**: 阿里云百炼 Qwen3-plus API
- **Embedding**: sentence-transformers/all-MiniLM-L6-v2
- **前端**: Vue 3 + Element Plus + Vite
- **检索**: BM25 + 向量检索 (Hybrid Retrieval)
- **任务队列**: Celery + Redis

## 核心功能

### 文档处理
- 支持 **PDF / TXT / DOCX** 文档格式
- 异步文档处理 (Celery + Redis)
- 多知识库管理
- 增量向量索引更新

### Hybrid RAG 检索
- **向量检索**: 基于 sentence-transformers 语义匹配
- **BM25 检索**: 关键词精准匹配
- **混合检索**: 向量 + BM25 加权融合
- **Rerank 排序**: 语义重排序提升准确率

### Agent 工具调用
- 文档检索工具
- 数学计算工具
- 时间查询工具
- 网络信息查询工具
- 工具调用日志记录

### 对话管理
- SSE 流式响应
- 多轮上下文对话
- 对话历史持久化
- Undo 回滚功能

### 系统监控
- 请求统计
- Token 消耗统计
- Agent 调用日志

## 项目结构

```
docagent/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── routers/       # API 路由
│   │   │   ├── chat.py    # 对话接口
│   │   │   ├── upload.py  # 文档上传
│   │   │   └── monitor.py # 监控统计
│   │   ├── services/      # 核心业务逻辑
│   │   │   ├── rag.py           # RAG 服务
│   │   │   ├── hybrid_retriever.py  # 混合检索
│   │   │   ├── bm25_retriever.py   # BM25 检索
│   │   │   ├── agent.py           # Agent 工具
│   │   │   └── agent_logger.py    # 日志记录
│   │   ├── tasks/         # Celery 异步任务
│   │   ├── celery_app.py  # Celery 配置
│   │   └── config.py     # 配置管理
│   └── requirements.txt
└── frontend/               # Vue 3 前端
    └── src/
        ├── components/    # UI 组件
        │   ├── ChatWindow.vue
        │   ├── FileUpload.vue
        │   ├── DocumentList.vue
        │   └── KnowledgeBaseManager.vue
        └── api/          # API 封装
```

## 快速启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `backend/.env` 文件：

```env
dashscope_api_key=your_api_key_here
```

### 3. 启动服务

```bash
# 启动 Redis (需要先安装 Redis)
redis-server

# 启动 Celery Worker (终端1)
cd backend
celery -A app.celery_app worker --loglevel=info

# 启动 FastAPI (终端2)
cd backend
python -m app.main

# 启动前端 (终端3)
cd frontend
npm run dev
```

### 4. 访问系统

打开浏览器访问: http://localhost:5173

## API 文档

启动后访问: http://localhost:8000/docs

## 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | 流式对话 |
| `/api/upload` | POST | 文档上传 (异步) |
| `/api/documents` | GET | 文档列表 |
| `/api/knowledge-bases` | GET/POST | 知识库管理 |
| `/api/stats` | GET | 系统统计 |
| `/api/agent-logs` | GET | Agent 调用日志 |

## 配置说明

在 `backend/app/config.py` 中可配置：

```python
chunk_size: int = 500          # 文档分块大小
chunk_overlap: int = 50        # 分块重叠大小
bm25_weight: float = 0.3       # BM25 权重
vector_weight: float = 0.7     # 向量检索权重
rerank_top_k: int = 5          # Rerank 召回数
```

## 更新日志

### v2.0.0
- 新增 Hybrid Retrieval 混合检索
- 新增 Celery 异步文档处理
- 新增多知识库管理
- 新增网络搜索工具
- 新增系统监控统计
- 新增 DOCX 支持
