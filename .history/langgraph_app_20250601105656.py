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

def handle_supervisor_communication(state: Dict[str, Any]) -> Dict[str, Any]:
    """处理监督者之间的通信"""
    messages = state.get("messages", [])
    if not messages:
        return {"next": "__end__"}
    
    # 获取通信状态
    if "communication_state" not in state:
        state["communication_state"] = {}
    communication_state = state["communication_state"]
    last_message = messages[-1]
    # 确保需要协作字段存在
    if "needs_collaboration" not in communication_state:
        communication_state["needs_collaboration"] = False
    if "collaborating_supervisors" not in communication_state:
        communication_state["collaborating_supervisors"] = []

    # 检查任务是否已完成
    if "任务完成" in last_message.content or "task completed" in last_message.content.lower():
        return {"next": "__end__"}
    
    # 检查是否需要监督者之间的协作
    if "需要协作" in last_message.content or "complex" in last_message.content.lower():
        # 添加协作请求消息
        messages.append(AIMessage(content="正在协调监督者之间的协作..."))
        communication_state["needs_collaboration"] = True
        communication_state["collaborating_supervisors"] = ["math_supervisor", "weather_supervisor"]
        return {
            "next": "supervisor",
            "messages": messages,
            "communication_state": communication_state
        }
    
    # 检查监督者之间的任务状态
    if "supervisor_status" in communication_state:
        status = communication_state["supervisor_status"]
        if status == "in_progress":
            messages.append(AIMessage(content="监督者正在协作处理任务..."))
            return {
                "next": "supervisor",
                "messages": messages,
                "communication_state": communication_state
            }
        elif status == "completed":
            messages.append(AIMessage(content="监督者协作任务已完成"))
            return {"next": "__end__"}
    
    # 如果没有需要处理的通信，直接结束
    return {"next": "__end__"}

# 创建语言模型实例
model = create_model("cogito:14b")

# 创建代理
math_agent = create_math_agent("qwen3:8b")
weather_agent = create_weather_agent("granite3.3:8b")

# 创建数学团队监督者
math_team = create_supervisor(
    agents=[math_agent],
    model=model,
    supervisor_name="math_supervisor",
    prompt="你是数学团队监督者，负责处理数学相关任务。当需要与其他监督者协作时，通过通信处理器进行协调。任务完成后，必须明确说明'任务完成'。"
).compile(name="math_team")

# 创建天气团队监督者
weather_team = create_supervisor(
    agents=[weather_agent],
    model=model,
    supervisor_name="weather_supervisor",
    prompt="你是天气团队监督者，负责处理天气相关任务。当需要与其他监督者协作时，通过通信处理器进行协调。任务完成后，必须明确说明'任务完成'。"
).compile(name="weather_team")

# 创建顶层监督者
supervisor = create_supervisor(
    agents=[math_team, weather_team],
    model=model,
    supervisor_name="top_supervisor",
    prompt="""你是顶层监督者，负责协调数学团队和天气团队。你需要：
1. 根据任务类型分发给相应团队
2. 通过通信处理器处理监督者之间的协作
3. 协调复杂任务的执行
4. 确保任务状态正确传递
5. 当任务完成时，必须明确说明'任务完成'，以便系统结束处理
6. 如果收到'任务完成'的消息，请直接结束处理"""
).compile(name="top_supervisor")

# 创建应用
app = StateGraph(state_schema=AgentState)

# 添加节点
app.add_node("supervisor", supervisor)
app.add_node("task_router", route_task)
app.add_node("supervisor_communication", handle_supervisor_communication)

# 设置边
app.add_edge("__start__", "task_router")
app.add_edge("task_router", "supervisor")
app.add_edge("supervisor", "supervisor_communication")
app.add_edge("supervisor_communication", "supervisor")
app.add_edge("supervisor", "__end__")

# 编译应用
app = app.compile()

__all__ = ["app"]