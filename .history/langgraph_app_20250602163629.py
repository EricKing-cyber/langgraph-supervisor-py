from multi_agent_system.workflows import *
from multi_agent_system.agents import *
from multi_agent_system.model_utils import *


# 创建语言模型实例
model = create_model("cogito:14b")

# 创建代理
algebra_agent = create_math_agent("algebra", "qwen3:8b")
calculus_agent = create_math_agent("calculus", "qwen3:8b")
weather_agent = create_weather_agent("granite3.3:8b")

# 构建中间层监督者图（StateGraph）
math_team_graph = build_supervisor_workflow([algebra_agent, calculus_agent], model)
weather_team_graph = build_supervisor_workflow([weather_agent], model)


# 创建顶层监督者
supervisor = build_top_level_supervisor(
    middle_supervisors=[
        (math_team_graph),
        (weather_team_graph)
    ],
    model=model,
)

# 编译应用
app = supervisor.compile()

__all__ = ["app"]