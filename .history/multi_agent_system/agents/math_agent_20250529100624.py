# math_agent.py
from langgraph.prebuilt import create_react_agent
from ..tools.math_tools import calculate_sum, calculate_product  # ✅ 导入已注册的工具函数

def create_math_agent(model):
    """创建数学专家代理"""
    return create_react_agent(
        model=model,
        tools=[calculate_sum, calculate_product],  # ✅ 使用实际的 Tool 对象
        name="math_expert",
        prompt="你是一个数学专家，擅长进行数学计算。请使用提供的工具进行计算。"
    )