# langgraph_app.py
from multi_agent_system.workflows.supervisor_workflow import build_supervisor_workflow
from multi_agent_system.agents import *
from multi_agent_system.model_utils import create_model

# 创建语言模型实例
model = create_model()

# 创建代理
math_agent = create_math_agent(model)
weather_agent = create_weather_agent(model)

# 构建工作流
workflow = build_supervisor_workflow([math_agent, weather_agent], model)

# 编译为可执行对象
app = workflow.compile()