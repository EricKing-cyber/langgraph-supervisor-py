# weather_tools.py
from typing import Annotated
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.prebuilt import InjectedState

@tool
def get_weather_info(
    city: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, "Tool call ID"]
) -> str:
    """获取城市天气信息（示例函数）"""
    weather_info = f"{city}的天气信息：晴朗，温度25°C"
    tool_message = ToolMessage(
        content=weather_info,
        name="get_weather_info",
        tool_call_id=tool_call_id,
    )
    return Command(
        update={
            "messages": state["messages"] + [tool_message],
            "weather_info": weather_info
        }
    )