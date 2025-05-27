# math_tools.py
from langgraph.prebuilt import tool

@tool
def calculate_sum(a: float, b: float) -> float:
    """计算两个数字的和"""
    return a + b

@tool
def calculate_product(a: float, b: float) -> float:
    """计算两个数字的乘积"""
    return a * b