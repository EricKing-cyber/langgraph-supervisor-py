# langgraph_app.py
from multi_agent_system.workflows.supervisor_workflow import build_supervisor_workflow
from multi_agent_system.agents import *
from multi_agent_system.model_utils import create_model
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.runnables.config import RunnableConfig

load_dotenv()

def create_graph(config: RunnableConfig) -> StateGraph:
    """创建基础图结构"""
    # 创建语言模型实例
    model = create_model("cogito:14b")
    
    # 创建代理
    math_agent = create_math_agent("qwen3:8b")
    weather_agent = create_weather_agent("granite3.3:8b")
    
    # 构建基础工作流
    workflow = build_supervisor_workflow([math_agent, weather_agent], model)
    
    # 编译工作流
    return workflow.compile()

# 导出图工厂函数
__all__ = ["create_graph"]