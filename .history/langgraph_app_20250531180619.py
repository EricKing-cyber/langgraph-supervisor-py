# langgraph_app.py
from fastapi import FastAPI
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.runnables.config import RunnableConfig
import uvicorn
import os
from typing import Dict, Any

app = FastAPI()

async def create_graph(config: RunnableConfig):
    """创建基础图结构"""
    try:
        # 创建基础工作流
        workflow = StateGraph(state_schema=AgentState)
        
        # 定义节点处理函数
        def start_node(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"next": "node1"}
            
        def node1_handler(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"next": "node2"}
            
        def node2_handler(state: Dict[str, Any]) -> Dict[str, Any]:
            return {"next": "END"}
        
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
    except Exception as e:
        print(f"Error creating graph: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
