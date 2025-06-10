from langgraph.pregel import Pregel
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool, tool
from langchain_core.language_models import LanguageModelLike
from typing import Union, Dict, Any, List, Optional
from abc import ABC
import asyncio
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model

from open_deep_research.src.open_deep_research.multi_agent import Section, FinishResearch
from open_deep_research.src.open_deep_research.utils import (
    get_today_str, tavily_search, duckduckgo_search, 
    # 添加更多搜索API工具
    google_search_async, arxiv_search_async, pubmed_search_async, linkup_search
)
from open_deep_research.src.open_deep_research.prompts import RESEARCH_INSTRUCTIONS
from open_deep_research.src.open_deep_research.configuration import Configuration


class ResearchAgent(ABC):
    """研究员代理基类，定义通用接口"""
    def __init__(self, model: LanguageModelLike, specialty: str = "general"):
        self.model = model
        self.specialty = specialty
        self.name = f"{specialty}_researcher"

    def _create_agent(self, tools: List[BaseTool], prompt: str) -> Pregel:
        return create_react_agent(
            model=self.model,
            tools=tools,
            name=self.name,
            prompt=prompt
        )


class SpecialtyResearchAgent(ResearchAgent):
    """特定领域研究员代理"""
    def __init__(self, model: LanguageModelLike, specialty: str, search_api: str = "duckduckgo"):
        super().__init__(model, specialty)
        # 设置工具
        self.tools = []
        
        # 添加Section工具
        self.tools.append(tool(Section))
        self.tools.append(tool(FinishResearch))
        
        # 添加搜索工具
        self._add_search_tool(search_api)
        
        # 设置提示词，添加必要的格式化参数和强调工具使用
        self.prompt = RESEARCH_INSTRUCTIONS.format(
            today=get_today_str(), 
            specialty=specialty,
            section_description=f"Research on {specialty}",
            number_of_queries=3
        ) + self._get_tools_instruction(search_api)

    def _add_search_tool(self, search_api: Union[str, List[str]]):
        """添加搜索工具
        
        Args:
            search_api: 搜索API名称或列表
        """
        # 处理单个搜索API的情况
        if isinstance(search_api, str):
            search_apis = [search_api]
        else:
            search_apis = search_api
            
        # 遍历添加所有指定的搜索API
        for api_name in search_apis:
            tool_added = False
            
            # 根据API名称选择对应的工具
            if api_name.lower() == "tavily":
                search_tool = tavily_search
                tool_added = True
            elif api_name.lower() == "duckduckgo":
                search_tool = duckduckgo_search
                tool_added = True
            elif api_name.lower() == "google":
                # 将异步函数包装为工具
                @tool
                async def google_search(search_queries: List[str]):
                    """使用Google搜索引擎进行搜索
                    
                    Args:
                        search_queries: 搜索查询列表，每个查询是一个字符串
                    """
                    try:
                        results = await google_search_async(search_queries)
                        return results
                    except Exception as e:
                        return f"Google搜索出错: {str(e)}\n请尝试其他搜索方式或简化搜索查询。"
                
                search_tool = google_search
                tool_added = True
            elif api_name.lower() == "arxiv":
                # 将异步函数包装为工具，确保参数格式正确
                @tool
                async def arxiv_search(search_queries: List[str]):
                    """在arXiv上搜索学术论文
                    
                    Args:
                        search_queries: 搜索查询列表，每个查询是一个字符串，如 ["quantum computing", "neural networks"]
                    """
                    try:
                        # 对于arxiv搜索，我们需要确保参数格式正确
                        # 通常load_max_docs参数控制每个查询返回的最大文档数
                        results = await arxiv_search_async(
                            search_queries, 
                            load_max_docs=5,
                            get_full_documents=False  # 不获取完整文档，只获取摘要，以减少负载
                        )
                        return results
                    except Exception as e:
                        return f"arXiv搜索出错: {str(e)}\n请尝试其他搜索方式或使用更具体的学术关键词。"
                
                search_tool = arxiv_search
                tool_added = True
            elif api_name.lower() == "pubmed":
                # 将异步函数包装为工具
                @tool
                async def pubmed_search(search_queries: List[str]):
                    """在PubMed上搜索医学文献
                    
                    Args:
                        search_queries: 医学相关搜索查询列表
                    """
                    try:
                        results = await pubmed_search_async(
                            search_queries,
                            top_k_results=5  # 限制每个查询返回的结果数
                        )
                        return results
                    except Exception as e:
                        return f"PubMed搜索出错: {str(e)}\n请尝试使用更具体的医学关键词或其他搜索方式。"
                
                search_tool = pubmed_search
                tool_added = True
            elif api_name.lower() == "linkup":
                # 将异步函数包装为工具
                @tool
                async def linkup_web_search(search_queries: List[str]):
                    """使用LinkUp搜索引擎进行搜索
                    
                    Args:
                        search_queries: 搜索查询列表
                    """
                    try:
                        results = await linkup_search(
                            search_queries,
                            depth="standard"  # 使用标准深度，避免过度请求
                        )
                        return results
                    except Exception as e:
                        return f"LinkUp搜索出错: {str(e)}\n请尝试其他搜索方式或简化搜索查询。"
                
                search_tool = linkup_web_search
                tool_added = True
                
            # 添加工具到工具列表
            if tool_added:
                # 添加工具元数据
                tool_metadata = {**(search_tool.metadata or {}), "type": "search"}
                search_tool.metadata = tool_metadata
                self.tools.append(search_tool)
    
    def _get_tools_instruction(self, search_api: Union[str, List[str]]) -> str:
        """获取工具使用说明
        
        Args:
            search_api: 搜索API名称或列表
        
        Returns:
            str: 工具使用说明文本
        """
        # 转换为列表
        if isinstance(search_api, str):
            search_apis = [search_api]
        else:
            search_apis = search_api
            
        # 构建搜索工具描述
        search_tools_desc = ""
        for api in search_apis:
            search_tools_desc += f"   - 使用{api}_search工具\n"
            
        # 构建完整说明
        return f"""

【特别重要的工具使用提示】
1. 搜索工具: 你必须使用搜索工具来获取最新信息，这是必须的第一步！
{search_tools_desc}   - 每个研究任务必须执行至少1-2次搜索查询
   - 确保你的搜索查询相关且精确
   - 查询格式示例: ["远程工作效率研究", "远程工作对员工心理健康的影响"]
   - 搜索查询应简单明确，避免过长或复杂的查询

2. Section工具: 完成研究后必须使用Section工具提交结果
   - name: 章节标题
   - description: 简短描述章节内容
   - content: 详细研究内容，必须包含:
     * 研究主题介绍
     * 主要发现和分析
     * 数据支持的结论
     * 来源引用

3. FinishResearch工具: 必须在工作流结束时调用
   - 这是完成研究工作的关键步骤
   - 在完成Section提交后必须调用此工具

完整工作流示例:
1. 收到研究任务: "研究远程工作模式对企业生产力的影响"
2. 执行搜索: 使用搜索工具查询相关信息
3. 分析搜索结果
4. 撰写研究内容: 使用Section工具提交
5. 完成工作: 使用FinishResearch工具
"""

    def _create_agent(self) -> Pregel:
        return super()._create_agent(self.tools, self.prompt)


class MultiSourceResearchAgent(SpecialtyResearchAgent):
    """多搜索源研究代理"""
    def __init__(self, model: LanguageModelLike, specialty: str, search_apis: List[str] = ["tavily", "google"]):
        """
        初始化多搜索源研究代理
        
        Args:
            model: 语言模型
            specialty: 专业领域
            search_apis: 搜索API列表
        """
        # 安全检查：确保搜索API列表不包含可能导致问题的组合
        safe_apis = []
        for api in search_apis:
            if api.lower() in ["tavily", "duckduckgo", "google"]:
                safe_apis.append(api)
            # 仅在特定领域使用专业搜索API
            elif api.lower() == "arxiv" and specialty in ["science", "ai_technology", "climate"]:
                safe_apis.append(api)
            elif api.lower() == "pubmed" and specialty in ["medical", "science"]:
                safe_apis.append(api)
                
        # 确保至少有一个搜索API
        if not safe_apis:
            safe_apis = ["tavily"]  # 默认使用tavily
            
        # 调用父类初始化，但传递搜索API列表
        super().__init__(model, specialty, safe_apis)
        
        # 增强提示词，强调多搜索源使用策略
        self.prompt += """

【多搜索源使用策略】
你拥有多个搜索工具，应当根据不同情况选择最合适的工具:

1. 对于学术/科学问题，优先使用tavily_search或google_search
2. 对于一般性问题，优先使用tavily_search或duckduckgo_search
3. 对于最新新闻和事件，优先使用google_search或tavily_search
4. 当一个搜索工具未返回满意结果时，尝试使用其他搜索工具
5. 如果所有搜索工具都返回错误，尝试简化搜索查询或拆分为多个简单查询

确保在报告中注明每个信息的来源和搜索工具。
"""


def create_research_agent(specialty: str, model_name: str = "default_model", search_api: Union[str, List[str]] = "tavily"):
    """工厂函数创建研究员代理
    
    Args:
        specialty: 研究领域专长
        model_name: 模型名称
        search_api: 搜索API类型或列表
    """
    from multi_agent_system.model_utils import create_model
    
    model_ = create_model(model_name=model_name) if isinstance(model_name, str) else model_name
    
    # 根据搜索API参数决定创建哪种类型的代理
    if isinstance(search_api, list) and len(search_api) > 1:
        # 如果是多个搜索API，创建多源搜索代理
        agent = MultiSourceResearchAgent(model_, specialty, search_api)
    else:
        # 如果是单个搜索API，创建常规专业代理
        agent = SpecialtyResearchAgent(model_, specialty, search_api)
        
    return agent._create_agent()


# 从 langgraph_supervisor 导入交接工具
from langgraph_supervisor import handoff

__all__ = [
    "create_research_agent",
    "ResearchAgent",
    "SpecialtyResearchAgent",
    "MultiSourceResearchAgent"
] 