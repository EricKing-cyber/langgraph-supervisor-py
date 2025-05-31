# langgraph_app.py
import uvicorn
from fastapi import FastAPI
from multi_agent_system.config import ModelConfig
from multi_agent_system.agents.math_agent import create_math_agent
from multi_agent_system.agents.weather_agent import create_weather_agent
from multi_agent_system.model_utils import create_model
from langgraph_supervisor.supervisor import create_supervisor
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
        
        # 创建代理
        math_agent = create_math_agent("cogito:14b")
        weather_agent = create_weather_agent("cogito:14b")
        
        # 创建主管代理
        base_supervisor = create_supervisor(
            [math_agent, weather_agent],
            model=model,
            state_schema=AgentState,
            prompt="你是一个主管代理，负责协调数学专家和天气专家的工作。请根据用户的需求，将任务分配给合适的专家。"
        )
        
        # 编译工作流
        workflow = base_supervisor.compile()
        
        return workflow
    except Exception as e:
        print(f"Error creating graph: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
