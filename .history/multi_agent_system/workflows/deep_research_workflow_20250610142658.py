from langgraph_supervisor.supervisor import create_supervisor
from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import tool, BaseTool
from typing import List, Dict, Any

# 导入open_deep_research中的相关模块
from open_deep_research.src.open_deep_research.multi_agent import (
    supervisor, 
    Sections, 
    Introduction, 
    Conclusion, 
    FinishReport, 
    Question
)
from open_deep_research.src.open_deep_research.prompts import SUPERVISOR_INSTRUCTIONS
from open_deep_research.src.open_deep_research.utils import get_today_str
from open_deep_research.src.open_deep_research.configuration import Configuration

def get_supervisor_tools() -> list[BaseTool]:
    """获取主管代理工具"""
    tools = [
        tool(Sections), 
        tool(Introduction), 
        tool(Conclusion), 
        tool(FinishReport),
        tool(Question)
    ]
    return tools

def build_deep_research_workflow(research_agents: list, model: LanguageModelLike, config: Dict[str, Any] = None):
    """
    构建深度研究工作流，集成open_deep_research的主管代理架构
    
    Args:
        research_agents: 研究员代理列表
        model: 语言模型
        config: 配置信息，用于设置deep_research的行为
    
    Returns:
        构建好的主管工作流图
    """
    # 初始化配置
    if config is None:
        config = {}
    
    # 获取主管工具
    supervisor_tools = get_supervisor_tools()
    
    # 创建提示词
    supervisor_prompt = SUPERVISOR_INSTRUCTIONS.format(today=get_today_str())
    
    # 使用create_supervisor构建工作流图
    return create_supervisor(
        agents=research_agents,
        model=model,
        prompt=supervisor_prompt,
        tools=supervisor_tools,
        config_schema=config  # 传递配置信息
    )

__all__ = ["build_deep_research_workflow"] 