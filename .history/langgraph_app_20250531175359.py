# langgraph_app.py
import uvicorn
from fastapi import FastAPI
from multi_agent_system.config import ModelConfig
from multi_agent_system.agents.math_agent import create_math_agent
from multi_agent_system.agents.weather_agent import create_weather_agent
from multi_agent_system.model_utils import create_model
from multi_agent_system.workflows.supervisor_workflow import EnhancedSupervisor, build_supervisor_workflow
from langgraph.graph import StateGraph
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph.graph import CompiledGraph
from typing import Any, Dict
from langgraph.prebuilt.chat_agent_executor import AgentState

app = FastAPI()

async def create_graph(config: RunnableConfig) -> CompiledGraph:
    """Factory function for creating a graph instance."""
    try:
        # 创建语言模型实例
        model = create_model("cogito:14b")
        
        # 创建基础代理
        math_agent = create_math_agent("cogito:14b")
        weather_agent = create_weather_agent("cogito:14b")
        
        # 创建基础主管工作流
        base_workflow = build_supervisor_workflow([math_agent, weather_agent], model)
        
        # 创建增强型主管代理
        enhanced_supervisor = EnhancedSupervisor(base_workflow)
        
        # 编译工作流
        workflow = enhanced_supervisor.compile()
        
        # 生成可视化
        enhanced_supervisor.visualize_topology("static/topology.png")
        enhanced_supervisor.visualize_workflow("static/workflow.png")
        
        return workflow
    except Exception as e:
        print(f"Error creating graph: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
