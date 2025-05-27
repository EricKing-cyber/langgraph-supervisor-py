# weather_agent.py
from langgraph.prebuilt import create_react_agent
from ..tools.weather_tools import get_weather_info  #  导入已注册的工具函数

def create_weather_agent(model):
    """创建天气专家代理"""
    return create_react_agent(
        model=model,
        tools=[get_weather_info],  #  使用实际的 Tool 对象
        name="weather_expert",
        prompt="你是一个天气专家，可以提供天气相关信息。请使用提供的工具获取天气信息。"
    )

__all__ = [
    "create_weather_agent",
]