# math_agent.py
from typing import Annotated, List
from pydantic import BaseModel
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import create_react_agent
from ..tools.math_tools import calculate_sum, calculate_product

class MathAgentState(BaseModel):
    messages: List[BaseMessage]
    result: float | None = None
    active_agent: str | None = None
    remaining_steps: int = 5  # 添加最大步数限制

    class Config:
        arbitrary_types_allowed = True

def create_math_agent(model):
    """创建数学专家代理"""
    tools: list[BaseTool] = [calculate_sum, calculate_product]
    
    return create_react_agent(
        model=model,
        tools=tools,
        name="math_expert",
        prompt="你是一个数学专家，擅长进行数学计算。请使用提供的工具进行计算。",
        state_schema=MathAgentState
    )