# weather_agent.py
from langgraph.pregel import Pregel
from langgraph.prebuilt import create_react_agent
from ..tools.weather_tools import get_weather_info  #  导入已注册的工具函数
from langchain_core.language_models import LanguageModelLike
from typing import Union, Dict, Any

def create_weather_agent(model: str | None = "default_model"):
    """创建天气专家代理"""
    from multi_agent_system.model_utils import create_model
    print(f"创建天气代理，传入的模型名称: {model}")
    if isinstance(model, str):
        model_: Union[LanguageModelLike, None] = create_model(model_name=model)
        print(f"天气代理使用的模型: {model}")
    elif model is None:
        model_ = create_model(model_name="default_model")
        print("天气代理使用默认模型")
    if model_ is None:
        raise ValueError("模型创建失败")
    return create_react_agent(
        model=model_,
        tools=[get_weather_info],  # 使用实际的 Tool 对象
        name="weather_expert",
        prompt="你是一个天气专家，可以提供天气相关信息。请使用提供的工具获取天气信息。"
    )

# 从 langgraph_supervisor 导入交接工具
from langgraph_supervisor import handoff

# 创建 math_team_graph 到 weather_team_graph 的交接工具
math_to_weather_tool = handoff.create_handoff_tool(agent_name="weather_team_graph")

# 创建 weather_team_graph 到 math_team_graph 的交接工具
weather_to_math_tool = handoff.create_handoff_tool(agent_name="math_team_graph")

__all__ = [
    "create_weather_agent",
    "math_to_weather_tool",
    "weather_to_math_tool"
]
