from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama  # 确保导入 ChatOllama
from pydantic import SecretStr
from multi_agent_system.config import ModelConfig

def create_model(model_name: str | None = None):
    """根据环境变量创建语言模型实例"""
    # if ModelConfig.MODEL_TYPE == "local":
    #     return ChatOpenAI(
    #         base_url=ModelConfig.LOCAL_MODEL_URL,
    #         api_key=SecretStr("not-needed"),
    #         model=ModelConfig.LOCAL_MODEL_NAME
    #     )
    
    if model_name == "gpt-4.1-2025-04-14":
        return ChatOpenAI(
            model="gpt-4.1-2025-04-14",
            base_url=ModelConfig.LOCAL_MODEL_URL,
            api_key=SecretStr("not-needed")
            )
    elif model_name == "cogito:14b":                #更细粒度的模型选择
        return ChatOllama(
            model="cogito:14b",
            base_url=ModelConfig.LOCAL_MODEL_URL,
            )
    # else:
    #     if not ModelConfig.OPENAI_API_KEY:
    #         raise ValueError("缺少必要的环境变量：OPENAI_API_KEY")
    #     return ChatOpenAI(
    #         model=ModelConfig.OPENAI_MODEL_NAME,
    #         api_key=SecretStr(ModelConfig.OPENAI_API_KEY)
    #     )