# DocAgent - 智能文档问答助手

## 项目概述

基于 RAG + LangChain + Agent 架构的本地智能问答系统，用户上传文档后可通过聊天界面提问，系统自动检索文档内容并调用外部工具回答问题。

## 技术栈

- **后端**: FastAPI + LangChain + Chroma
- **LLM**: 阿里云百炼 Qwen3-plus API
- **Embedding**: sentence-transformers/all-MiniLM-L6-v2
- **前端**: Vue 3 + Element Plus + Vite

## 核心功能

- **文档上传**: 支持 PDF/TXT 格式，自动文本切分、向量化存储
- **RAG 检索**: 基于向量相似度检索文档相关内容
- **Agent 工具调用**: 支持文档检索、数学计算、时间查询三种工具
- **流式响应**: SSE 实现实时流式输出
- **对话历史**: 支持历史记录持久化与撤销

## 项目结构

```
docagent/
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── routers/  # API 路由
│   │   ├── services/ # 核心业务逻辑 (RAG/Agent/History)
│   │   └── models/   # 数据模型
│   └── requirements.txt
└── frontend/          # Vue 3 前端
    └── src/
        ├── components/ # UI 组件
        └── api/       # API 封装
```

## 个人职责

- 独立完成前后端开发
- 实现 RAG 文档检索流程
- 集成 LangChain Agent 工具调用
- 实现 SSE 流式响应与对话历史管理
