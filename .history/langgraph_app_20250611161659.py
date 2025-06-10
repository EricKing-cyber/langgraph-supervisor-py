from multi_agent_system.workflows import *
from multi_agent_system.agents import *
from multi_agent_system.model_utils import *
from multi_agent_system.config import *
import os

# 设置Ollama参数，提高稳定性
os.environ["OLLAMA_KEEP_ALIVE"] = "600s"  # 10分钟保活时间

# 创建语言模型实例 - 为所有代理创建一个共享模型实例
print("正在初始化共享模型...")
shared_model = create_model("qwen3:8b", 
                           temperature=0.7,
                           timeout=120,  # 增加超时时间
                           num_ctx=2048)  # 减小上下文窗口以节省内存

# 创建基础代理
print("正在创建基础团队代理...")
algebra_agent = create_math_agent("algebra", shared_model)
calculus_agent = create_math_agent("calculus", shared_model)
weather_agent = create_weather_agent(shared_model)

# 设置深度研究配置
deep_research_config = create_research_config(
    search_api="tavily",  # 指定使用tavily搜索API
    ask_for_clarification=True,  # 允许代理提问澄清
    supervisor_model="qwen3:8b",  # 确保使用与其他代理相同的模型
    researcher_model="qwen3:8b",  # 确保使用与其他代理相同的模型
    include_source_str=True,  # 包含搜索结果源数据
    process_search_results="summarize"  # 处理搜索结果的方式
)

# 创建研究代理 - 全部使用同一模型实例以减少内存使用
print("正在创建研究团队代理...")

# 基础研究团队 - 这些是必须的
ai_research_agent = create_research_agent("ai_technology", shared_model, search_api="tavily")
finance_research_agent = create_research_agent("finance", shared_model, search_api="tavily")
science_research_agent = create_research_agent("science", shared_model, search_api="tavily")

# 扩展研究团队 - 初始只激活两个最重要的，其他暂时禁用以降低系统负载
active_specialized_agents = []

# 激活法律研究代理
legal_research_agent = create_legal_research_agent(shared_model, search_api="tavily")
active_specialized_agents.append(legal_research_agent)

# 激活医疗研究代理
medical_research_agent = create_medical_research_agent(shared_model, search_api="tavily")
active_specialized_agents.append(medical_research_agent)

# 暂时禁用其他专业代理，以减轻系统负载
# engineering_research_agent = create_engineering_research_agent(shared_model, search_api="tavily")
# socialscience_research_agent = create_socialscience_research_agent(shared_model, search_api="tavily")
# climate_research_agent = create_multisource_research_agent("climate", shared_model, search_apis=["tavily"])

# 构建中间层监督者图（StateGraph）
print("正在构建团队监督图...")
math_team_graph = build_supervisor_workflow([algebra_agent, calculus_agent], shared_model)
weather_team_graph = build_supervisor_workflow([weather_agent], shared_model)

# 创建包含所有研究代理的深度研究团队
print("正在构建深度研究团队...")
research_agents = [
    ai_research_agent, 
    finance_research_agent, 
    science_research_agent
]

# 添加活跃的专业研究代理
research_agents.extend(active_specialized_agents)

deep_research_team_graph = build_deep_research_workflow(
    research_agents, 
    shared_model,
    deep_research_config
)

# 创建顶层监督者 - 管理所有专业团队的协作
print("正在构建顶层监督者...")
supervisor = build_top_level_supervisor(
    middle_supervisors=[
        (math_team_graph, "math_team"),
        (weather_team_graph, "weather_team"),
        (deep_research_team_graph, "deep_research_team")
    ],
    model=shared_model,
)

# 编译应用
print("编译完成，应用就绪!")
app = supervisor.compile()

__all__ = ["app"]