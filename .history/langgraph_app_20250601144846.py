from langgraph_supervisor.supervisor import create_supervisor
from multi_agent_system.workflows import *
from multi_agent_system.agents import create_math_agent, create_weather_agent
from multi_agent_system.model_utils import create_model


# 创建语言模型实例
model = create_model("cogito:14b")

# 创建代理
math_agent = create_math_agent("qwen3:8b")
weather_agent = create_weather_agent("granite3.3:8b")

math_team = build_supervisor_workflow(math_agent, model)
weather_team = build_supervisor_workflow(weather_agent, model)


# 创建顶层监督者
supervisor = build_top_level_supervisor(
    middle_supervisors=[math_team, weather_team],
    model=model,
)

# 编译应用
app = supervisor.compile()

__all__ = ["app"]