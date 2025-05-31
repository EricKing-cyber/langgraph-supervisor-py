# langgraph_app.py
import uvicorn
from fastapi import FastAPI, Depends
from langgraph_sdk import get_client  # 假设这是正确的导入路径
from multi_agent_system.config import ModelConfig
# 修复导入部分
from multi_agent_system.agents.math_agent import MathAgent
from multi_agent_system.agents.weather_agent import WeatherAgent
from langchain_openai import ChatOpenAI
# 添加缺失的create_supervisor导入
from langgraph_supervisor.supervisor import create_supervisor
from langgraph.graph import StateGraph
from langchain_core.runnables.config import RunnableConfig
from langgraph_api.graph import Graph
from langgraph.graph.graph import CompiledGraph
from typing import Any

app = FastAPI()

# 将 create_graph 挂载到 app 上（可选）
app.state.StateGraph = create_graph


async def create_graph(config: RunnableConfig) -> CompiledGraph:
    """Factory function for creating a graph instance."""
    # 确保这里使用了RunnableConfig类型的config参数
    graph = Graph()
    # 创建示例代理
    math_agent = MathAgent(name="math_expert")
    weather_agent = WeatherAgent(name="weather_forecast")
    
    # 创建主管代理
    base_supervisor = create_supervisor(
        [math_agent, weather_agent],
        model=ChatOpenAI(model="cogito:14b")
    )
    
    # 编译工作流
    workflow = base_supervisor.compile()
    
    # 将编译后的工作流赋值给FastAPI应用实例
    app.state.workflow = workflow
    
    return workflow


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
