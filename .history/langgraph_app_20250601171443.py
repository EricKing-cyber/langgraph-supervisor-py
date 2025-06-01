from multi_agent_system.workflows import *
from multi_agent_system.agents import *
from multi_agent_system.model_utils import *


# 创建语言模型实例
model = create_model("cogito:14b")

# 创建代理
math_agent = create_math_agent("calculus", "qwen3:8b")
weather_agent = create_weather_agent("granite3.3:8b")

# 构建中间层监督者图（StateGraph）
math_team_graph = build_supervisor_workflow([math_agent], model, supervisor_name="math_team")
weather_team_graph = build_supervisor_workflow([weather_agent], model, supervisor_name="weather_team")

# 编译为可运行图并指定唯一名称
math_team = math_team_graph.compile(name="math_team")
weather_team = weather_team_graph.compile(name="weather_team")

# 创建顶层监督者
supervisor = build_top_level_supervisor(
    middle_supervisors=[math_team, weather_team],
    model=model,
)

# 编译应用
app = supervisor.compile()

__all__ = ["app"]