from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
import json
import asyncio

from app.config import settings
from app.services.agent import get_tools, AGENT_PROMPT
from app.services.history import history_manager

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    use_history: bool = True


async def generate_response(message: str, use_history: bool = True):
    try:
        llm = ChatOpenAI(
            model="qwen-plus",
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            streaming=True,
            temperature=0.7
        )
        
        if use_history:
            history_messages = history_manager.to_langchain_messages()
        else:
            history_messages = []
        
        prompt = PromptTemplate.from_template(AGENT_PROMPT)
        
        tools = get_tools()
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            max_iterations=settings.max_iterations,
            verbose=True,
            handle_parsing_errors=True
        )
        
        history_manager.add_user_message(message)
        
        full_response = ""
        
        if use_history and history_messages:
            input_with_history = f"""Previous conversation:
{history_manager.get_history_text()}

Current question: {message}"""
        else:
            input_with_history = message
        
        async for event in agent_executor.astream_events(
            {"input": input_with_history},
            version="v1"
        ):
            if event["event"] == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    full_response += content
                    yield f"data: {json.dumps({'content': content})}\n\n"
                    await asyncio.sleep(0.02)
        
        history_manager.add_ai_message(full_response)
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        error_msg = f"错误: {str(e)}"
        yield f"data: {json.dumps({'error': error_msg})}\n\n"


@router.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        generate_response(request.message, request.use_history),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/history")
async def get_history():
    return {"history": history_manager.get_recent(20)}


@router.post("/history/clear")
async def clear_history():
    history_manager.clear()
    return {"message": "历史已清除"}


@router.post("/history/undo")
async def undo_history():
    success = history_manager.undo()
    if success:
        return {"message": "已撤销上轮对话", "success": True}
    return {"message": "没有可撤销的对话", "success": False}
