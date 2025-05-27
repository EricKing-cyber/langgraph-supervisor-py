from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()
    
class ModelConfig:
    MODEL_TYPE = os.getenv("MODEL_TYPE", "local")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "cogito:14b")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
