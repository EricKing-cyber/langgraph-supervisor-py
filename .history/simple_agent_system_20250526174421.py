from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os
from typing import Dict, Any

# 加载.env文件
load_dotenv()

# 创建语言模型实例
# 根据环境变量选择模型
model_type = os.getenv("MODEL_TYPE", "local")  # 默认使用本地模型

if model_type == "local":
    # Ollama本地模型配置
    model = ChatOpenAI(
        base_url=os.getenv("LOCAL_MODEL_URL", "http://localhost:11434/v1"),
        api_key="not-needed",
        model=os.getenv("LOCAL_MODEL_NAME", "cogito:14b")
    )
else:
    # 使用OpenAI配置
    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

# 定义工具函数
def calculate_sum(a: float, b: float) -> float:
    """计算两个数字的和"""
    return a + b

def calculate_product(a: float, b: float) -> float:
    """计算两个数字的乘积"""
    return a * b

def get_weather_info(city: str) -> str:
    """获取城市天气信息（示例函数）"""
    return f"{city}的天气信息：晴朗，温度25°C"

# 创建数学专家代理
math_agent = create_react_agent(
    model=model,
    tools=[calculate_sum, calculate_product],
    name="math_expert",
    prompt="你是一个数学专家，擅长进行数学计算。请使用提供的工具进行计算。"
)

# 创建天气专家代理
weather_agent = create_react_agent(
    model=model,
    tools=[get_weather_info],
    name="weather_expert",
    prompt="你是一个天气专家，可以提供天气相关信息。请使用提供的工具获取天气信息。"
)

# 创建监督者工作流
workflow = create_supervisor(
    [math_agent, weather_agent],
    model=model,
    prompt="你是一个团队监督者，管理数学专家和天气专家。对于数学问题，使用math_expert；对于天气问题，使用weather_expert。"
)

# 编译工作流
app = workflow.compile()

# 定义条件函数
def is_math_task(state: Dict[str, Any]) -> bool:
    """判断是否为数学任务"""
    last_message = state["messages"][-1]["content"]
    math_keywords = ["计算", "数学", "加法", "乘法", "数字"]
    return any(keyword in last_message for keyword in math_keywords)

def is_weather_task(state: Dict[str, Any]) -> bool:
    """判断是否为天气任务"""
    last_message = state["messages"][-1]["content"]
    weather_keywords = ["天气", "温度", "气候"]
    return any(keyword in last_message for keyword in weather_keywords)

# 导出所有必要的对象
__all__ = [
    "app",
    "workflow",
    "math_agent",
    "weather_agent",
    "is_math_task",
    "is_weather_task"
]

# 测试系统
def test_agent_system():
    try:
        # 测试数学问题
        math_result = app.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": "请计算 5 和 3 的和"
                }
            ]
        })
        print("数学问题结果:", math_result)

        # 测试天气问题
        weather_result = app.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": "北京今天的天气怎么样？"
                }
            ]
        })
        print("天气问题结果:", weather_result)
    except Exception as e:
        print(f"发生错误: {str(e)}")
        print("请确保：")
        print("1. Ollama服务已启动")
        print("2. 已下载所需的模型（例如：ollama pull llama2）")
        print("3. 环境变量配置正确")

if __name__ == "__main__":
    test_agent_system() 