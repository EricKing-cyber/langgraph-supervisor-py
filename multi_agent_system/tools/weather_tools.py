# weather_tools.py
from langchain_core.tools import tool

@tool
def get_weather_info(city: str) -> str:
    """获取城市天气信息（示例函数）"""
    return f"{city}的天气信息：晴朗，温度25°C"

tools=[get_weather_info]  # 注册工具函数

__all__ = [
    "get_weather_info"
]
# 限制从该模块通过 from weather_tools import * 导出的内容，仅包括 get_weather_info