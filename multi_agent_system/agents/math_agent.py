# math_agent.py
from langgraph.pregel import Pregel
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool, tool
from langchain_core.language_models import LanguageModelLike
from typing import Union, Dict, Any, List, Optional
from abc import ABC


class MathAgent(ABC):
    """数学代理基类，定义通用接口"""
    def __init__(self, model: LanguageModelLike):
        self.model = model
        self.name = ""  # 添加name属性

    def _create_agent(self, tools: List[BaseTool], prompt: str) -> Pregel:  # 明确参数类型和返回类型
        return create_react_agent(
            model=self.model,
            tools=tools,
            name=self.name,  # 使用实例变量name
            prompt=prompt
        )

class AlgebraAgent(MathAgent):
    """代数计算专家代理"""
    def __init__(self, model: LanguageModelLike):
        super().__init__(model)
        # 显式导入工具函数
        from ..tools.math_tools import calculate_sum, calculate_product
        self.tools = [calculate_sum, calculate_product]  # type: List[BaseTool]
        self.name = "algebra_expert"  # 添加唯一名称
        self.prompt = "你是一个代数专家，擅长进行基本运算和方程求解。"

    def _create_agent(self) -> Pregel:
        return super()._create_agent(self.tools, self.prompt)


class CalculusAgent(MathAgent):
    """微积分计算专家代理"""
    def __init__(self, model: LanguageModelLike):
        super().__init__(model)
        # 显式导入工具函数
        from ..tools.math_tools import calculate_integral
        self.tools = [calculate_integral]  # type: List[BaseTool]
        self.name = "calculus_expert"  # 添加唯一名称
        self.prompt = "你是一个微积分专家，擅长进行积分和导数计算。"

    def _create_agent(self) -> Pregel:
        return super()._create_agent(self.tools, self.prompt)


def create_math_agent(agent_type: str = "algebra", model: str | None = "default_model"):
    """工厂函数创建不同类型的数学代理
    
    Args:
        agent_type: 代理类型 ('algebra' 或 'calculus')
        model: 模型名称
    """
    from multi_agent_system.model_utils import create_model
    model_ = create_model(model_name=model) if isinstance(model, str) else create_model(model_name="default_model")
    
    if agent_type == "algebra":
        agent = AlgebraAgent(model_)
    elif agent_type == "calculus":
        agent = CalculusAgent(model_)
    else:
        raise ValueError(f"未知的代理类型: {agent_type}")
    
    return agent._create_agent()

__all__ = [
    "create_math_agent"
]