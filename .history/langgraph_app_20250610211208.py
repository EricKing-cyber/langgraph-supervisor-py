from multi_agent_system.workflows import *
from multi_agent_system.agents import *
from multi_agent_system.model_utils import *
from multi_agent_system.config import *


# 创建语言模型实例 - 所有代理使用相同的模型以确保兼容性
model = create_model("qwen3:8b")

# 创建基础代理
algebra_agent = create_math_agent("algebra", "qwen3:8b")
calculus_agent = create_math_agent("calculus", "qwen3:8b")
weather_agent = create_weather_agent("qwen3:8b")

# 设置深度研究配置
deep_research_config = create_research_config(
    search_api="tavily",  # 指定使用tavily搜索API
    ask_for_clarification=True,  # 允许代理提问澄清
    supervisor_model="qwen3:8b",  # 确保使用与其他代理相同的模型
    researcher_model="qwen3:8b",  # 确保使用与其他代理相同的模型
    include_source_str=True,  # 包含搜索结果源数据
    process_search_results="summarize"  # 处理搜索结果的方式
)

# 创建深度研究代理，明确指定搜索API为tavily
ai_research_agent = create_research_agent("ai_technology", "qwen3:8b", search_api="tavily")
finance_research_agent = create_research_agent("finance", "qwen3:8b", search_api="tavily")
science_research_agent = create_research_agent("science", "qwen3:8b", search_api="tavily")

# 构建中间层监督者图（StateGraph）
math_team_graph = build_supervisor_workflow([algebra_agent, calculus_agent], model)
weather_team_graph = build_supervisor_workflow([weather_agent], model)
deep_research_team_graph = build_deep_research_workflow(
    [ai_research_agent, finance_research_agent, science_research_agent], 
    model,
    deep_research_config
)

# 创建顶层监督者 - 管理所有专业团队的协作
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