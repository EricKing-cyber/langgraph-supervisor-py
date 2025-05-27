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
# 这里的 tools 列表可以在其他模块中使用        