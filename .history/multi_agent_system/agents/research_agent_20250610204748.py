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
from open_deep_research.src.open_deep_research.utils import get_today_str, tavily_search, duckduckgo_search
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
        if search_api.lower() == "tavily":
            search_tool = tavily_search
            tool_metadata = {**(search_tool.metadata or {}), "type": "search"}
            search_tool.metadata = tool_metadata
            self.tools.append(search_tool)
        elif search_api.lower() == "duckduckgo":
            search_tool = duckduckgo_search
            tool_metadata = {**(search_tool.metadata or {}), "type": "search"}
            search_tool.metadata = tool_metadata
            self.tools.append(search_tool)
        else:
            # 默认使用tavily搜索
            search_tool = tavily_search
            tool_metadata = {**(search_tool.metadata or {}), "type": "search"}
            search_tool.metadata = tool_metadata
            self.tools.append(search_tool)
        
        # 设置提示词，添加必要的格式化参数和强调工具使用
        self.prompt = RESEARCH_INSTRUCTIONS.format(
            today=get_today_str(), 
            specialty=specialty,
            section_description=f"Research on {specialty}",
            number_of_queries=3
        ) + """

【特别重要的工具使用提示】
1. 搜索工具: 你必须使用搜索工具来获取最新信息，这是必须的第一步！
   - 使用tavily_search或duckduckgo_search工具
   - 每个研究任务必须执行至少1-2次搜索查询
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
2. 执行搜索: 使用tavily_search工具查询相关信息
3. 分析搜索结果
4. 撰写研究内容: 使用Section工具提交
5. 完成工作: 使用FinishResearch工具
"""

    def _create_agent(self) -> Pregel:
        return super()._create_agent(self.tools, self.prompt)


def create_research_agent(specialty: str, model_name: str = "default_model", search_api: str = "tavily"):
    """工厂函数创建研究员代理
    
    Args:
        specialty: 研究领域专长
        model_name: 模型名称
        search_api: 搜索API类型 ('tavily' 或 'duckduckgo')，默认使用tavily
    """
    from multi_agent_system.model_utils import create_model
    
    model_ = create_model(model_name=model_name) if isinstance(model_name, str) else model_name
    
    agent = SpecialtyResearchAgent(model_, specialty, search_api)
    return agent._create_agent()


# 从 langgraph_supervisor 导入交接工具
from langgraph_supervisor import handoff

__all__ = [
    "create_research_agent",
    "ResearchAgent",
    "SpecialtyResearchAgent"
] 