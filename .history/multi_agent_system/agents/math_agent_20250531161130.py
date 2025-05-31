# math_agent.py
from langgraph.graph import Pregel
from langgraph.prebuilt import create_react_agent
from ..tools.math_tools import *  # 导入已注册的工具函数
from langchain_core.language_models import LanguageModelLike
from typing import Union, Dict, Any

class MathAgent(Pregel):
    """数学计算代理"""
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.type = "math"
        
    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """执行数学计算"""
        return {"result": "Math calculation result"}

def create_math_agent(model: str | None = "default_model"):
    """创建数学专家代理"""
    from multi_agent_system.model_utils import create_model
    print(f"创建数学代理，传入的模型名称: {model}")
    if isinstance(model, str):
        model_: Union[LanguageModelLike, None] = create_model(model_name=model)
        print(f"数学代理使用的模型: {model}")
    elif model is None:
        model_ = create_model(model_name="default_model")
        print("数学代理使用默认模型")
    if model_ is None:
        raise ValueError("模型创建失败")
    return create_react_agent(
        model=model_,
        tools=[calculate_sum, calculate_product],  # 使用实际的 Tool 对象
        name="math_expert",
        prompt="你是一个数学专家，擅长进行数学计算。请使用提供的工具进行计算。"
    )

__all__ = [
    "create_math_agent",
     "MathAgent"
]