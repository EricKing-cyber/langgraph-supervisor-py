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
    """构建监督者工作流"""
    return create_supervisor(
        agents=agents,
        model=model,
        prompt="你是一个团队监督者，管理数学专家和天气专家。对于数学问题，使用math_expert；对于天气问题，使用weather_expert。"
    )

__all__ = ["build_supervisor_workflow"]