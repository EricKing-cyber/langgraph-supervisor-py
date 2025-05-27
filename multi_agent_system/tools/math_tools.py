# math_tools.py
from langchain_core.tools import tool

@tool
def calculate_sum(a: float, b: float) -> float:
    """计算两个数字的和"""
    return a + b

@tool
def calculate_product(a: float, b: float) -> float:
    """计算两个数字的乘积"""
    return a * b

tools=[calculate_sum, calculate_product]  # 注册工具函数

__all__ = [
    "calculate_sum",
    "calculate_product"
]
