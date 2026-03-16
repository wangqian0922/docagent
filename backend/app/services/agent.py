from langchain_core.tools import tool
from datetime import datetime
import numexpr as ne
import time
import httpx
from app.services.agent_logger import agent_logger
from app.services.hybrid_retriever import hybrid_retriever


@tool
def calculator(expression: str) -> str:
    """数学计算器，可以安全地计算数学表达式。
    输入: 数学表达式，如 "2+2"、"sqrt(16) * 3"、"100 * 0.5"
    输出: 计算结果
    """
    start_time = time.time()
    try:
        result = ne.evaluate(expression)
        output = f"计算结果: {result}"
        agent_logger.log_tool_call("calculator", expression, output, True, None, time.time() - start_time)
        return output
    except Exception as e:
        error_msg = f"计算错误: {str(e)}"
        agent_logger.log_tool_call("calculator", expression, error_msg, False, str(e), time.time() - start_time)
        return error_msg


@tool
def get_current_time() -> str:
    """获取当前时间。
    当用户询问时间、日期时使用此工具。
    返回当前日期和时间。
    """
    start_time = time.time()
    now = datetime.now()
    output = f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}, 星期{['一','二','三','四','五','六','日'][now.weekday()]}"
    agent_logger.log_tool_call("get_current_time", "", output, True, None, time.time() - start_time)
    return output


@tool
def document_retriever(query: str, knowledge_base_id: str = "default") -> str:
    """文档检索工具。
    当用户询问关于已上传文档的内容时使用此工具。
    输入: 用户的查询问题
    输出: 相关文档片段
    """
    start_time = time.time()
    try:
        results = hybrid_retriever.retrieve(query, knowledge_base_id)
        
        if not results:
            output = "未找到相关文档内容。"
            agent_logger.log_tool_call("document_retriever", query, output, True, None, time.time() - start_time)
            return output
        
        context_parts = []
        for i, doc in enumerate(results):
            source_info = doc.get("metadata", {}).get("file_name", "未知来源")
            context_parts.append(f"[来源{i+1}: {source_info}]\n{doc['content']}")
        
        output = "参考文档内容:\n\n" + "\n\n".join(context_parts)
        agent_logger.log_tool_call("document_retriever", query, output, True, None, time.time() - start_time)
        return output
    except Exception as e:
        error_msg = f"检索错误: {str(e)}"
        agent_logger.log_tool_call("document_retriever", query, error_msg, False, str(e), time.time() - start_time)
        return error_msg


@tool
def web_search(query: str) -> str:
    """网络信息查询工具。
    当用户询问需要最新信息、新闻、实时数据时使用此工具。
    输入: 查询关键词或问题
    输出: 搜索结果摘要
    """
    start_time = time.time()
    try:
        search_results = _perform_web_search(query)
        
        if not search_results:
            output = "未找到相关信息"
            agent_logger.log_tool_call("web_search", query, output, True, None, time.time() - start_time)
            return output
        
        output = "搜索结果:\n\n"
        for i, result in enumerate(search_results[:5], 1):
            output += f"{i}. {result.get('title', '无标题')}\n"
            output += f"   {result.get('snippet', '无描述')}\n\n"
        
        agent_logger.log_tool_call("web_search", query, output, True, None, time.time() - start_time)
        return output
    except Exception as e:
        error_msg = f"搜索错误: {str(e)}"
        agent_logger.log_tool_call("web_search", query, error_msg, False, str(e), time.time() - start_time)
        return error_msg


def _perform_web_search(query: str, max_retries: int = 2) -> list:
    for attempt in range(max_retries):
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for item in data.get("RelatedTopics", []):
                        if isinstance(item, dict):
                            results.append({
                                "title": query,
                                "snippet": item.get("Text", ""),
                                "url": item.get("URL", "")
                            })
                    return results[:5]
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(1)
    
    return []


def get_tools():
    return [calculator, get_current_time, document_retriever, web_search]


AGENT_PROMPT = """你是一个智能助手，可以帮助用户回答各种问题。你有以下工具可以使用：

1. calculator - 数学计算器，用于计算数学表达式
2. get_current_time - 获取当前时间
3. document_retriever - 检索已上传文档的内容
4. web_search - 搜索网络信息

使用工具的规则：
- 当用户询问文档相关内容时，使用 document_retriever 工具
- 当用户询问数学问题时，使用 calculator 工具
- 当用户询问时间日期时，使用 get_current_time 工具
- 当用户询问需要最新信息、新闻、实时数据时，使用 web_search 工具
- 如果问题不需要使用任何工具，可以直接回答

请根据用户的问题，选择合适的工具来回答。如果需要多个工具，按顺序使用。

Question: {input}
"""
