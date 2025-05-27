from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

class ModelConfig:
    MODEL_TYPE = os.getenv("MODEL_TYPE", "local")
    
    # 本地模型配置
    LOCAL_MODEL_URL = os.getenv("LOCAL_MODEL_URL")
    LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME")
    
    # OpenAI 模型配置
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 不设默认值，强制要求提供