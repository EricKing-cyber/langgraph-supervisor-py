# langgraph_app.py
from fastapi import FastAPI
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.runnables.config import RunnableConfig
import uvicorn
import os

app = FastAPI()

async def create_graph(config: RunnableConfig):
    """创建基础图结构"""
    try:
        # 创建基础工作流
        workflow = StateGraph(state_schema=AgentState)
        
        # 定义入口节点
        def start_node(state):
            return {"next": "node1"}
        
        # 添加节点
        workflow.add_node("START", start_node)  # 添加入口节点
        workflow.add_node("node1", lambda x: x)
        workflow.add_node("node2", lambda x: x)
        
        # 设置边
        workflow.add_edge("START", "node1")
        workflow.add_edge("node1", "node2")
        workflow.add_edge("node2", "node1")
        workflow.add_edge("node2", "END")
        
        # 编译工作流
        return workflow.compile()
    except Exception as e:
        print(f"Error creating graph: {str(e)}")
        raise

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
