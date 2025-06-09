from langgraph_supervisor.supervisor import create_supervisor
from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import tool, BaseTool
from typing import List, Dict, Any, Callable
from langchain_core.runnables import RunnableConfig
from functools import wraps

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

# 导入配置工具
from multi_agent_system.config.deep_research_config import config_to_runnable_config

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

def with_config_injection(graph_func):
    """装饰器：向图的调用中注入配置"""
    @wraps(graph_func)
    def wrapper(state, config=None):
        # 如果配置存在，使用它
        if hasattr(build_deep_research_workflow, 'config') and build_deep_research_workflow.config:
            # 合并传入的配置和存储的配置
            stored_config = config_to_runnable_config(build_deep_research_workflow.config)
            if config:
                merged_config = config.copy() if config else {}
                if 'configurable' in stored_config and 'configurable' in merged_config:
                    merged_config['configurable'].update(stored_config['configurable'])
                else:
                    merged_config.update(stored_config)
                return graph_func(state, merged_config)
            else:
                return graph_func(state, stored_config)
        else:
            # 如果没有存储配置，使用传入的配置
            return graph_func(state, config)
    
    return wrapper

def build_deep_research_workflow(research_agents: list, model: LanguageModelLike, config: Dict[str, Any] = None):
    """
    构建深度研究工作流，集成open_deep_research的主管代理架构
    
    Args:
        research_agents: 研究员代理列表
        model: 语言模型
        config: 配置信息，用于设置deep_research的行为（将通过后续调用时的config传递）
    
    Returns:
        构建好的主管工作流图
    """
    # 初始化配置 - 保存为类变量供后续使用
    if config is None:
        config = {}
    
    # 保存配置以便后续使用
    build_deep_research_workflow.config = config
    
    # 获取主管工具
    supervisor_tools = get_supervisor_tools()
    
    # 创建提示词
    supervisor_prompt = SUPERVISOR_INSTRUCTIONS.format(today=get_today_str())
    
    # 使用create_supervisor构建工作流图，不传递config参数
    graph = create_supervisor(
        agents=research_agents,
        model=model,
        prompt=supervisor_prompt,
        tools=supervisor_tools
    )
    
    # 为图的invoke和ainvoke方法添加配置注入装饰器
    original_invoke = (graph.compile()).invoke
    original_ainvoke = (graph.compile()).ainvoke
    
    graph.invoke = with_config_injection(original_invoke)
    graph.ainvoke = with_config_injection(original_ainvoke)
    
    return graph

__all__ = ["build_deep_research_workflow"] 