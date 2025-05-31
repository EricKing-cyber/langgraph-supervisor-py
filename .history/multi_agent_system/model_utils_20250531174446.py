from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from multi_agent_system.config import ModelConfig
import logging

logger = logging.getLogger(__name__)

def create_model(model_name: str | None = None):
    """根据环境变量创建语言模型实例"""       #更细粒度的模型选择
    try:
        # 本地模型配置
        if model_name in ["cogito:14b", "qwen3:8b", "granite3.3:8b"]:
            logger.info(f"Creating local model: {model_name}")
            return ChatOpenAI(
                model=model_name,
                base_url=ModelConfig.LOCAL_MODEL_URL,
                api_key=SecretStr("no-need")
            )
        
        # OpenAI模型配置
        if not ModelConfig.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in the environment variables.")
            
        if model_name in ["gpt-4.1-2025-04-14", "qwen3-32b"]:
            logger.info(f"Creating OpenAI model: {model_name}")
            return ChatOpenAI(
                model=model_name,
                base_url=ModelConfig.OPENAI_BASE_URL,
                api_key=SecretStr(ModelConfig.OPENAI_API_KEY)
            )
            
        # 默认使用本地模型
        logger.info("Using default model: cogito:14b")
        return ChatOpenAI(
            model="cogito:14b",
            base_url=ModelConfig.LOCAL_MODEL_URL,
            api_key=SecretStr("no-need")
        )
    except Exception as e:
        logger.error(f"Error creating model: {str(e)}")
        raise