from langchain_core.tools import tool
from datetime import datetime
import numexpr as ne


@tool
def calculator(expression: str) -> str:
    """数学计算器，可以安全地计算数学表达式。
    输入: 数学表达式，如 "2+2"、"sqrt(16) * 3"、"100 * 0.5"
    输出: 计算结果
    """
    try:
        result = ne.evaluate(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


@tool
def get_current_time() -> str:
    """获取当前时间。
    当用户询问时间、日期时使用此工具。
    返回当前日期和时间。
    """
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}, 星期{['一','二','三','四','五','六','日'][now.weekday()]}"


@tool
def document_retriever(query: str) -> str:
    """文档检索工具。
    当用户询问关于已上传文档的内容时使用此工具。
    输入: 用户的查询问题
    输出: 相关文档片段
    """
    from app.services.rag import rag_service
    
    retriever = rag_service.get_retriever(k=3)
    if retriever is None:
        return "暂无已上传的文档，请先上传文档。"
    
    docs = retriever.invoke(query)
    if not docs:
        return "未找到相关文档内容。"
    
    context = "\n\n".join([f"[来源{i+1}] {doc.page_content}" for i, doc in enumerate(docs)])
    return f"参考文档内容:\n{context}"

def get_tools():
    return [calculator, get_current_time, document_retriever]


AGENT_PROMPT = """Answer the following question as best as you can. You have access to the following tools:

{tools}

Use the following format. Each thought should be followed by either a tool or a final answer:

Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original question

Question: {input}
{agent_scratchpad}"""
