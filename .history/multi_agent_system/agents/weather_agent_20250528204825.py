# weather_agent.py
from typing import Annotated, List
from pydantic import BaseModel
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import create_react_agent
from ..tools.weather_tools import get_weather_info

class WeatherAgentState(BaseModel):
    messages: List[BaseMessage]
    weather_info: str | None = None
    active_agent: str | None = None
    remaining_steps: int = 5  # 添加最大步数限制

    class Config:
        arbitrary_types_allowed = True

def create_weather_agent(model):
    """创建天气专家代理"""
    tools: list[BaseTool] = [get_weather_info]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="weather_expert",
        prompt="你是一个天气专家，可以提供天气相关信息。请使用提供的工具获取天气信息。",
        state_schema=WeatherAgentState
    )