from langgraph_supervisor.supervisor import create_supervisor
from multi_agent_system.strategies.game_theory import ShapleyValueStrategy, NashEquilibriumAllocation
from multi_agent_system.protocols.communication import DynamicRoutingProtocol, CommunicationTopology
from multi_agent_system.strategies import AgentProfile
from multi_agent_system.strategies import TaskContext
from multi_agent_system.visualization.network_visualizer import NetworkVisualizer
from multi_agent_system.visualization.workflow_visualizer import WorkflowVisualizer
from typing import List, Dict, Any, Optional
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.runnables.config import RunnableConfig

def build_supervisor_workflow(agents, model):
    """构建三层监督者工作流"""
    # 创建顶层监督者
    top_supervisor = create_supervisor(
        agents=agents,
        model=model,
        prompt="你是顶层监督者，负责整体任务分配和协调。根据任务类型，将任务分配给数学监督者或天气监督者。"
    )
    
    # 创建数学监督者
    math_supervisor = create_supervisor(
        agents=[agent for agent in agents if agent.name == "math_expert"],
        model=model,
        prompt="你是数学监督者，负责处理所有数学相关任务。"
    )
    
    # 创建天气监督者
    weather_supervisor = create_supervisor(
        agents=[agent for agent in agents if agent.name == "weather_forecast"],
        model=model,
        prompt="你是天气监督者，负责处理所有天气相关任务。"
    )
    
    # 创建基础工作流
    workflow = StateGraph(state_schema=AgentState)
    
    # 添加监督者节点
    workflow.add_node("top_supervisor", top_supervisor)
    workflow.add_node("math_supervisor", math_supervisor)
    workflow.add_node("weather_supervisor", weather_supervisor)
    
    # 添加代理节点
    for agent in agents:
        workflow.add_node(agent.name, agent)
    
    # 设置边
    # 从开始到顶层监督者
    workflow.add_edge("__start__", "top_supervisor")
    
    # 从顶层监督者到中间层监督者
    workflow.add_edge("top_supervisor", "math_supervisor")
    workflow.add_edge("top_supervisor", "weather_supervisor")
    
    # 从中间层监督者到代理
    workflow.add_edge("math_supervisor", "math_expert")
    workflow.add_edge("weather_supervisor", "weather_forecast")
    
    # 从代理回到各自的监督者
    workflow.add_edge("math_expert", "math_supervisor")
    workflow.add_edge("weather_forecast", "weather_supervisor")
    
    # 从中间层监督者回到顶层监督者
    workflow.add_edge("math_supervisor", "top_supervisor")
    workflow.add_edge("weather_supervisor", "top_supervisor")
    
    # 添加结束边
    workflow.add_edge("top_supervisor", "__end__")
    workflow.add_edge("math_supervisor", "__end__")
    workflow.add_edge("weather_supervisor", "__end__")
    for agent in agents:
        workflow.add_edge(agent.name, "__end__")
    
    return workflow

__all__ = ["build_supervisor_workflow"]