from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from multi_agent_system.config import ModelConfig

def create_model(model_name: str | None = None):
    """根据环境变量创建语言模型实例"""       #更细粒度的模型选择
    #=================================
    #OpenAI模型
    #=================================
    if not ModelConfig.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY must be set in the environment variables.")

    if model_name == "gpt-4.1-2025-04-14":
        return ChatOpenAI(
            model="gpt-4.1-2025-04-14",
            base_url=ModelConfig.OPENAI_BASE_URL,
            api_key=SecretStr(ModelConfig.OPENAI_API_KEY)
            )
    elif model_name == "qwen3-32b":                
        return ChatOpenAI(
            model="qwen3-32b",  
            base_url=ModelConfig.OPENAI_BASE_URL,
            api_key=SecretStr(ModelConfig.OPENAI_API_KEY)
            )
    #=================================
    #本地模型 (使用支持 bind_tools 的模型代替)
    #=================================
    elif model_name == "qwen3:8b":                
        return ChatOpenAI(
            model="qwen3:8b",  
            base_url=ModelConfig.LOCAL_MODEL_URL,
            api_key=SecretStr("no-need")
            )
    elif model_name == "granite3.3:8b":                
        return ChatOpenAI(
            model="granite3.3:8b",  
            base_url=ModelConfig.LOCAL_MODEL_URL,
            api_key=SecretStr("no-need")
            )
    else:
        # 默认使用 cogito:14b 模型
        return ChatOpenAI(
            model="cogito:14b",
            base_url=ModelConfig.LOCAL_MODEL_URL,
            api_key=SecretStr("no-need")
        )