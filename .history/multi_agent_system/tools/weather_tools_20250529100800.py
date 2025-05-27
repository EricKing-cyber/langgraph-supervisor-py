# weather_tools.py
from langgraph.prebuilt import tool

@tool
def get_weather_info(city: str) -> str:
    """获取城市天气信息（示例函数）"""
    return f"{city}的天气信息：晴朗，温度25°C"