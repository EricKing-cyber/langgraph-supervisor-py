# 新增 config.py 文件内容如下
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

class ModelConfig:
    MODEL_TYPE = os.getenv("MODEL_TYPE", "local")
    
    # 本地模型配置
    LOCAL_MODEL_URL = os.getenv("LOCAL_MODEL_URL", "http://localhost:11434/v1")
    LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "cogito:14b")
    
    # OpenAI 模型配置
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 不设默认值，强制要求提供