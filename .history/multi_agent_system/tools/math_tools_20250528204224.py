# math_tools.py
from typing import Annotated
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.prebuilt import InjectedState

@tool
def calculate_sum(
    a: float,
    b: float,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, "Tool call ID"]
) -> float:
    """计算两个数字的和"""
    result = a + b
    tool_message = ToolMessage(
        content=f"计算结果: {result}",
        name="calculate_sum",
        tool_call_id=tool_call_id,
    )
    return Command(
        update={
            "messages": state["messages"] + [tool_message],
            "result": result
        }
    )

@tool
def calculate_product(
    a: float,
    b: float,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, "Tool call ID"]
) -> float:
    """计算两个数字的乘积"""
    result = a * b
    tool_message = ToolMessage(
        content=f"计算结果: {result}",
        name="calculate_product",
        tool_call_id=tool_call_id,
    )
    return Command(
        update={
            "messages": state["messages"] + [tool_message],
            "result": result
        }
    )