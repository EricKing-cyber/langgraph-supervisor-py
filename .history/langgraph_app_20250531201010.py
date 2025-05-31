# langgraph_app.py
from langgraph_supervisor.supervisor import create_supervisor
from langchain_openai import ChatOpenAI
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState
from multi_agent_system.agents import create_math_agent, create_weather_agent
from multi_agent_system.model_utils import create_model
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage

def route_task(state: Dict[str, Any]) -> Dict[str, Any]:
    """任务路由函数，根据任务内容决定发送到哪个团队"""
    messages = state.get("messages", [])
    if not messages:
        return {"next": "__end__"}
        
    last_message = messages[-1]
    content = last_message.content.lower()
    
    # 任务分发逻辑
    if "math" in content or "calculate" in content or "equation" in content:
        return {"next": "supervisor", "team": "math_team"}
    elif "weather" in content or "forecast" in content or "temperature" in content:
        return {"next": "supervisor", "team": "weather_team"}
    else:
        # 对于复杂任务，可能需要多个团队协作
        return {
            "next": "supervisor",
            "messages": messages + [AIMessage(content="这是一个复杂任务，需要多个团队协作。")]
        }

# 创建语言模型实例
model = create_model("cogito:14b")

# 创建代理
math_agent = create_math_agent("qwen3:8b")
weather_agent = create_weather_agent("granite3.3:8b")

# 创建数学团队监督者
math_team = create_supervisor(
    agents=[math_agent],
    model=model,
    supervisor_name="math_supervisor"
).compile(name="math_team")

# 创建天气团队监督者
weather_team = create_supervisor(
    agents=[weather_agent],
    model=model,
    supervisor_name="weather_supervisor"
).compile(name="weather_team")

# 创建顶层监督者
supervisor = create_supervisor(
    agents=[math_team, weather_team],
    model=model,
    supervisor_name="top_supervisor"
).compile(name="top_supervisor")

# 创建应用
app = StateGraph(state_schema=AgentState)

# 添加节点
app.add_node("supervisor", supervisor)
app.add_node("task_router", route_task)

# 设置边
app.add_edge("__start__", "task_router")
app.add_edge("task_router", "supervisor")
app.add_edge("supervisor", "__end__")

# 编译应用
app = app.compile()

__all__ = ["app"]