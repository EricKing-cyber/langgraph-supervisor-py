from langgraph_supervisor.supervisor import create_supervisor
from multi_agent_system.workflows import *
from multi_agent_system.agents import create_math_agent, create_weather_agent
from multi_agent_system.model_utils import create_model


# 创建语言模型实例
model = create_model("cogito:14b")

# 创建代理
math_agent = create_math_agent("qwen3:8b")
weather_agent = create_weather_agent("granite3.3:8b")

math_team=build_supervisor_workflow(math_agent, model)


# 创建天气团队监督者
weather_team = create_supervisor(
    agents=[weather_agent],
    model=model,
    supervisor_name="weather_supervisor",
    prompt="你是天气团队监督者，负责处理天气相关任务。当需要与其他监督者协作时，通过通信处理器进行协调。任务完成后，必须明确说明'任务完成'。"
).compile(name="weather_team")

# 创建顶层监督者
supervisor = create_top_level_supervisor(
    middle_supervisors=[math_team, weather_team],
    model=model,
    supervisor_name="top_supervisor"
)

# 创建应用
app = supervisor.compile()

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