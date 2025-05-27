# model_utils.py
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os                                # 用于读取环境变量


load_dotenv()                      # 加载环境变量，避免将敏感信息硬编码在代码中

def create_model():
    """根据环境变量创建语言模型实例"""
    model_type = os.getenv("MODEL_TYPE", "local")    # 获取模型类型，默认为 "local"
    if model_type == "local":
        return ChatOpenAI(
            base_url=os.getenv("LOCAL_MODEL_URL", "http://localhost:11434/v1"),
            api_key="not-needed",
            model=os.getenv("LOCAL_MODEL_NAME", "cogito:14b")
        )
    else:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
            api_key=os.getenv("OPENAI_API_KEY")
        )