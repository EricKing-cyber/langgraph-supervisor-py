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
from typing import Any, Dict, TypedDict
from langgraph.prebuilt.chat_agent_executor import AgentState

app = FastAPI()

class GraphState(TypedDict):
    messages: list
    next: str

def create_graph(config: RunnableConfig) -> StateGraph:
    """创建基础图结构"""
    # 创建基础工作流
    workflow = StateGraph(state_schema=GraphState)
    
    # 定义节点处理函数
    def start_node(state: Dict[str, Any]) -> Dict[str, Any]:
        return {"messages": state.get("messages", []), "next": "node1"}
        
    def node1_handler(state: Dict[str, Any]) -> Dict[str, Any]:
        return {"messages": state.get("messages", []), "next": "node2"}
        
    def node2_handler(state: Dict[str, Any]) -> Dict[str, Any]:
        return {"messages": state.get("messages", []), "next": "END"}
    
    # 添加节点
    workflow.add_node("START", start_node)
    workflow.add_node("node1", node1_handler)
    workflow.add_node("node2", node2_handler)
    
    # 设置条件边
    workflow.add_conditional_edges(
        "START",
        lambda x: x["next"],
        {
            "node1": "node1",
            "END": "END"
        }
    )
    
    workflow.add_conditional_edges(
        "node1",
        lambda x: x["next"],
        {
            "node2": "node2",
            "END": "END"
        }
    )
    
    workflow.add_conditional_edges(
        "node2",
        lambda x: x["next"],
        {
            "END": "END"
        }
    )
    
    # 编译工作流
    return workflow.compile()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
