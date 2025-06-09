from multi_agent_system.workflows import *
from multi_agent_system.agents import *
from multi_agent_system.model_utils import *
from multi_agent_system.config import *


# 创建语言模型实例
model = create_model("cogito:14b")

# 创建代理
algebra_agent = create_math_agent("algebra", "qwen3:8b")
calculus_agent = create_math_agent("calculus", "qwen3:8b")
weather_agent = create_weather_agent("granite3.3:8b")

# 创建深度研究代理
ai_research_agent = create_research_agent("ai_technology", "qwen3:8b")
finance_research_agent = create_research_agent("finance", "qwen3:8b")
science_research_agent = create_research_agent("science", "qwen3:8b")

# 设置深度研究配置
deep_research_config = create_research_config(
    search_api="tavily",
    ask_for_clarification=True,
    supervisor_model="qwen3:8b",
    researcher_model="qwen3:8b"
)

# 构建中间层监督者图（StateGraph）
math_team_graph = build_supervisor_workflow([algebra_agent, calculus_agent], model)
weather_team_graph = build_supervisor_workflow([weather_agent], model)
deep_research_team_graph = build_deep_research_workflow(
    [ai_research_agent, finance_research_agent, science_research_agent], 
    model,
    deep_research_config
)

# 创建顶层监督者
supervisor = build_top_level_supervisor(
    middle_supervisors=[
        (math_team_graph, "math_team"),
        (weather_team_graph, "weather_team"),
        (deep_research_team_graph, "deep_research_team")
    ],
    model=model,
)

# 编译应用
app = supervisor.compile()

__all__ = ["app"]