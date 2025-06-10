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
                    """使用Google搜索引擎进行搜索"""
                    results = await google_search_async(search_queries)
                    return results
                
                search_tool = google_search
                tool_added = True
            elif api_name.lower() == "arxiv":
                # 将异步函数包装为工具
                @tool
                async def arxiv_search(search_queries: List[str]):
                    """在arXiv上搜索学术论文"""
                    results = await arxiv_search_async(search_queries)
                    return results
                
                search_tool = arxiv_search
                tool_added = True
            elif api_name.lower() == "pubmed":
                # 将异步函数包装为工具
                @tool
                async def pubmed_search(search_queries: List[str]):
                    """在PubMed上搜索医学文献"""
                    results = await pubmed_search_async(search_queries)
                    return results
                
                search_tool = pubmed_search
                tool_added = True
            elif api_name.lower() == "linkup":
                # 将异步函数包装为工具
                @tool
                async def linkup_web_search(search_queries: List[str]):
                    """使用LinkUp搜索引擎进行搜索"""
                    results = await linkup_search(search_queries)
                    return results
                
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
   - 查询格式示例: ["大语言模型最新技术发展", "GPT-4技术架构分析"]

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
1. 收到研究任务: "研究大语言模型最新进展"
2. 执行搜索: 使用搜索工具查询相关信息
3. 分析搜索结果
4. 撰写研究内容: 使用Section工具提交
5. 完成工作: 使用FinishResearch工具
"""

    def _create_agent(self) -> Pregel:
        return super()._create_agent(self.tools, self.prompt)


class MultiSourceResearchAgent(SpecialtyResearchAgent):
    """多搜索源研究代理"""
    def __init__(self, model: LanguageModelLike, specialty: str, search_apis: List[str] = ["tavily", "google", "arxiv"]):
        """
        初始化多搜索源研究代理
        
        Args:
            model: 语言模型
            specialty: 专业领域
            search_apis: 搜索API列表
        """
        # 调用父类初始化，但传递搜索API列表
        super().__init__(model, specialty, search_apis)
        
        # 增强提示词，强调多搜索源使用策略
        self.prompt += """

【多搜索源使用策略】
你拥有多个搜索工具，应当根据不同情况选择最合适的工具:

1. 对于学术/科学问题，优先使用arxiv_search
2. 对于医学问题，优先使用pubmed_search
3. 对于最新新闻和事件，优先使用google_search或tavily_search
4. 对于复杂问题，考虑使用多个搜索工具对比结果
5. 当一个搜索工具未返回满意结果时，尝试使用其他搜索工具

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