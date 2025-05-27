# model_utils.py
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from .config import ModelConfig  # 引入统一配置

def create_model():
    """根据环境变量创建语言模型实例"""
    if ModelConfig.MODEL_TYPE == "local":
        return ChatOpenAI(
            base_url=ModelConfig.LOCAL_MODEL_URL,
            api_key=SecretStr("not-needed"),
            model=ModelConfig.LOCAL_MODEL_NAME
        )
    elif 
    else:
        if not ModelConfig.OPENAI_API_KEY:
            raise ValueError("缺少必要的环境变量：OPENAI_API_KEY")
        return ChatOpenAI(
            model=ModelConfig.OPENAI_MODEL_NAME,
            api_key=SecretStr(ModelConfig.OPENAI_API_KEY)
        )