"""
深度研究配置模块
管理OpenDeepResearch的配置信息
"""

from typing import Dict, Any, Optional, List
from open_deep_research.configuration import Configuration, SearchAPI

def create_default_config() -> Dict[str, Any]:
    """
    创建默认的深度研究配置
    
    返回值:
        配置字典
    """
    return {
        "configurable": {
            "report_structure": """使用以下结构创建一份关于用户提供主题的研究报告:

1. 引言（无需研究）
   - 主题领域的简要概述

2. 正文部分:
   - 每个部分应该专注于用户提供主题的一个子主题
   
3. 结论
   - 尽量提供一个结构性元素（列表或表格）来提炼正文部分的内容
   - 提供报告的简明总结""",
            "search_api": SearchAPI.DUCKDUCKGO,  # 默认使用DuckDuckGo搜索
            "process_search_results": "summarize",
            "summarization_model_provider": "anthropic",
            "summarization_model": "claude-3-5-haiku-latest",
            "include_source_str": True,  # 包含源字符串，用于评估
            "ask_for_clarification": True,  # 允许提问以澄清需求
        }
    }

def create_research_config(
    search_api: str = "duckduckgo",
    include_source_str: bool = True,
    ask_for_clarification: bool = True,
    process_search_results: str = "summarize",
    supervisor_model: str = None,
    researcher_model: str = None,
    custom_report_structure: str = None,
    mcp_tools: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    创建定制的深度研究配置
    
    参数:
        search_api: 搜索API类型 ('tavily', 'duckduckgo', 'googlesearch', 'perplexity' 等)
        include_source_str: 是否包含源字符串
        ask_for_clarification: 是否允许提问以澄清需求
        process_search_results: 处理搜索结果的方式 ('summarize' 或 'split_and_rerank')
        supervisor_model: 主管代理使用的模型
        researcher_model: 研究员代理使用的模型
        custom_report_structure: 自定义报告结构
        mcp_tools: 要包含的MCP工具名称列表
        
    返回值:
        配置字典
    """
    config = create_default_config()
    
    # 更新搜索API
    if search_api:
        try:
            search_enum = SearchAPI[search_api.upper()]
            config["configurable"]["search_api"] = search_enum
        except KeyError:
            config["configurable"]["search_api"] = SearchAPI.DUCKDUCKGO
            
    # 更新其他配置
    if include_source_str is not None:
        config["configurable"]["include_source_str"] = include_source_str
    
    if ask_for_clarification is not None:
        config["configurable"]["ask_for_clarification"] = ask_for_clarification
    
    if process_search_results:
        config["configurable"]["process_search_results"] = process_search_results
    
    if supervisor_model:
        config["configurable"]["supervisor_model"] = supervisor_model
    
    if researcher_model:
        config["configurable"]["researcher_model"] = researcher_model
    
    if custom_report_structure:
        config["configurable"]["report_structure"] = custom_report_structure
    
    if mcp_tools:
        config["configurable"]["mcp_tools_to_include"] = mcp_tools
    
    return config

__all__ = ["create_default_config", "create_research_config"] 