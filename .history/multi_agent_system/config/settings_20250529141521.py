# 创建配置目录和 settings.py
import os

# 确保 config 目录存在
config_dir = os.path.join(os.path.dirname(__file__), 'config')
os.makedirs(config_dir, exist_ok=True)

# 创建 settings.py 内容
settings_content = '''from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()

class ModelConfig:
    MODEL_TYPE = os.getenv("MODEL_TYPE", "local")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "cogito:14b")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4")
'''

with open(os.path.join(config_dir, 'settings.py'), 'w', encoding='utf-8') as f:
    f.write(settings_content)