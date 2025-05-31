# weather_agent.py
from langgraph.pregel import Pregel
from langgraph.prebuilt import create_react_agent
from ..tools.weather_tools import get_weather_info  #  导入已注册的工具函数
from langchain_core.language_models import LanguageModelLike
from typing import Union, Dict, Any

class WeatherAgent(Pregel):
    """天气预测代理"""
    def __init__(self, name: str):
        # 初始化Pregel基类时提供必要的空实现
        super().__init__(nodes={}, channels={}, input_channels=[], output_channels=[])  # type: ignore
        self.name = name
        self.type = "weather"
        
    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """执行天气预测"""
        # 实现代理逻辑
        return {"result": "Weather forecast result"}

def create_weather_agent(model: str | None = "default_model"):
    """创建天气专家代理"""
    from multi_agent_system.model_utils import create_model
    print(f"创建天气代理，传入的模型名称: {model}")
    if isinstance(model, str):
        model_: Union[LanguageModelLike, None] = create_model(model_name=model)
        print(f"天气代理使用的模型: {model}")
    elif model is None:
        model_ = create_model(model_name="default_model")
        print("天气代理使用默认模型")
    if model_ is None:
        raise ValueError("模型创建失败")
    return create_react_agent(
        model=model_,
        tools=[get_weather_info],  # 使用实际的 Tool 对象
        name="weather_expert",
        prompt="你是一个天气专家，可以提供天气相关信息。请使用提供的工具获取天气信息。"
    )

__all__ = [
    "create_weather_agent",
    "WeatherAgent"
]