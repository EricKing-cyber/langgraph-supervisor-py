# langgraph_app.py
from langgraph_supervisor.supervisor import create_supervisor
from langchain_openai import ChatOpenAI
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState
from multi_agent_system.agents import create_agents

# 创建基础代理
agents = create_agents()

# 创建模型
model = ChatOpenAI(model="gpt-3.5-turbo")

# 创建数学团队监督者
math_team = create_supervisor(
    agents=[agent for agent in agents if agent.name == "math_expert"],
    model=model,
    supervisor_name="math_supervisor"
).compile(name="math_team")

# 创建天气团队监督者
weather_team = create_supervisor(
    agents=[agent for agent in agents if agent.name == "weather_forecast"],
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

# 设置边
app.add_edge("__start__", "supervisor")
app.add_edge("supervisor", "__end__")

# 编译应用
app = app.compile()

__all__ = ["app"]