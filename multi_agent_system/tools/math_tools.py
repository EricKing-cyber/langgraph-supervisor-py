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

@tool
def matrix_multiply(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """执行矩阵乘法运算
    
    Args:
        a: 第一个矩阵（二维列表）
        b: 第二个矩阵（二维列表）
    Returns:
        矩阵乘法结果
    Raises:
        ValueError: 如果矩阵维度不匹配
    """
    # 检查矩阵维度是否匹配
    if len(a[0]) != len(b):
        raise ValueError("矩阵维度不匹配，无法进行乘法运算")
    
    # 初始化结果矩阵
    result = [[0.0 for _ in range(len(b[0]))] for _ in range(len(a))]  # 初始化为浮点数
    
    # 执行矩阵乘法
    for i in range(len(a)):
        for j in range(len(b[0])):
            for k in range(len(b)):
                result[i][j] += float(a[i][k] * b[k][j])  # 显式转换为浮点数
    return result

@tool
def solve_linear_system(equations: list[str]) -> dict:
    """求解线性方程组
    
    Args:
        equations: 方程组字符串列表，格式如："2x + 3y = 5"
    Returns:
        包含解的字典，如 {'x': 1, 'y': 2}
    Raises:
        ValueError: 如果方程组格式无效或无解
    """
    # 这里应实现方程解析和求解逻辑
    # 示例返回值
    return {"x": 1.0, "y": 2.0}

@tool
def calculate_integral(function: str, lower: float, upper: float) -> float:
    """计算定积分（使用数值积分方法）
    
    Args:
        function: 要积分的函数字符串表示，如 "x**2"
        lower: 下限
        upper: 上限
    Returns:
        积分结果
    """
    # 实现数值积分（例如使用辛普森法则）
    import numpy as np
    
    # 解析函数字符串
    def f(x):
        return eval(function)
    
    # 使用数值积分计算
    n = 1000  # 分割区间数
    dx = (upper - lower) / n
    x = np.linspace(lower, upper, n+1)
    y = f(x)
    
    # 辛普森法则公式
    integral = dx/3 * np.sum(y[0:-1:2] + 4*y[1::2] + y[2::2])
    return float(integral)

tools=[calculate_sum, calculate_product, matrix_multiply, solve_linear_system, calculate_integral]  # 注册工具函数

__all__ = [
    "calculate_sum",
    "calculate_product"
]
