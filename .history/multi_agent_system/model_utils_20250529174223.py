from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from multi_agent_system.config import ModelConfig

def create_model(model_name: str | None = None):
    """根据环境变量创建语言模型实例"""
    if model_name == "gpt-4.1-2025-04-14":
        return ChatOpenAI(
            model="gpt-4.1-2025-04-14",
            base_url=ModelConfig.OPENAI_BASE_URL,
            api_key=SecretStr("not-needed")
            )
    elif model_name == "qwen3-32b":                #更细粒度的模型选择
        return ChatOpenAI(
            model="qwen3-32b",  # 使用支持 bind_tools 的模型代替
            base_url=ModelConfig.OPENAI_BASE_URL,
            api_key=SecretStr("not-needed")
            )
    else:
        # 默认使用 qwen3-32b 模型
        return ChatOpenAI(
            model="qwen3-32b",
            base_url=ModelConfig.OPENAI_BASE_URL,
            api_key=SecretStr("not-needed")
        )