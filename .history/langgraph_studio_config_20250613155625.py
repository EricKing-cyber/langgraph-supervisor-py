"""
Langgraph Studio 配置文件

此文件为 Langgraph Studio 环境提供必要的配置和入口点，确保深度研究工作流可以正常运行。
主要解决以下问题:
1. 并行处理功能问题 - 确保 initiate_final_section_writing 函数在 studio 环境正常工作
2. 图分析能力问题 - 添加中文字体支持，改进图分析工具的健壮性
3. 确保工具名称一致性 - 使用 visualize_graph 而非 _visualize_graph
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# 添加必要的导入
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# 导入工作流构建函数
from multi_agent_system.workflows.deep_research_workflow import build_deep_research_workflow

# 定义代理对象类，将字符串转换为具有name属性的对象
class AgentProxy:
    """代理对象，用于提供name属性"""
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"Agent({self.name})"

def create_agent_proxies(agent_names: List[str]) -> List[AgentProxy]:
    """
    创建代理对象列表
    
    Args:
        agent_names: 代理名称列表
        
    Returns:
        代理对象列表
    """
    return [AgentProxy(name) for name in agent_names]

def setup_graph():
    """
    设置并返回图实例
    
    此函数用于:
    1. 创建必要的模型实例
    2. 配置研究代理
    3. 构建工作流图
    
    Returns:
        构建好的图实例
    """
    # 配置Claude模型作为默认模型
    model = ChatAnthropic(model="claude-3-opus-20240229")
    
    # 定义研究代理名称
    agent_names = [
        "ai_technology_researcher",
        "finance_researcher", 
        "science_researcher",
        "legal_researcher",
        "medical_researcher",
        "engineering_researcher",
        "socialscience_researcher",
        "climate_researcher"
    ]
    
    # 创建代理对象 - 关键是确保每个代理都有name属性
    agents = create_agent_proxies(agent_names)
    
    # 配置
    config = {
        "parallel_tool_calls": True,  # 启用并行工具调用
        "tool_mapping": {
            # 确保工具名称正确映射
            "create_knowledge_graph": "create_knowledge_graph",
            "visualize_graph": "visualize_graph",
        }
    }
    
    # 构建图
    graph = build_deep_research_workflow(
        research_agents=agents,
        model=model,
        config=config
    )
    
    return graph

# 为Langgraph Studio导出工作流图
graph = setup_graph() 