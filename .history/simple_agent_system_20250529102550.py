from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os

# 加载.env文件
load_dotenv()

from multi_agent_system.model_utils import create_model
from multi_agent_system.agents import create_math_agent, create_weather_agent
from langgraph_supervisor import create_supervisor

# 创建语言模型实例
model = create_model()

# 创建数学专家代理
math_agent = create_math_agent(model)

# 创建天气专家代理
weather_agent = create_weather_agent(model)

# 创建监督者工作流
workflow = create_supervisor(
    [math_agent, weather_agent],
    model=model,
    prompt="你是一个团队监督者，管理数学专家和天气专家。对于数学问题，使用math_expert；对于天气问题，使用weather_expert。"
)

# 编译工作流
app = workflow.compile()

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