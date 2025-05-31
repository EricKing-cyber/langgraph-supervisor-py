# langgraph_app.py
import uvicorn
from fastapi import FastAPI, Depends
from langgraph_sdk import get_client  # 假设这是正确的导入路径

# 修复导入部分
from multi_agent_system.agents.math_agent import MathAgent
from multi_agent_system.agents.weather_agent import WeatherAgent
from langchain_openai import ChatOpenAI
# 添加缺失的create_supervisor导入
from langgraph_supervisor.supervisor import create_supervisor
from langgraph.graph import StateGraph

app = FastAPI()

# 修改工作流创建部分
@app.on_event("startup")
async def startup_event():
    # 创建示例代理系统并可视化工作流程
    from multi_agent_system.workflows.supervisor_workflow import EnhancedSupervisor
    from langgraph_supervisor.supervisor import create_supervisor
    from multi_agent_system.agents.math_agent import MathAgent
    from multi_agent_system.agents.weather_agent import WeatherAgent
    
    # 创建示例代理
    math_agent = MathAgent(name="math_expert")
    weather_agent = WeatherAgent(name="weather_forecast")
    
    # 创建主管代理
    base_supervisor = create_supervisor(
        [math_agent, weather_agent],
        model=ChatOpenAI(model="gpt-4o")
    )
    
    # 编译工作流
    workflow = base_supervisor.compile()
    
    # 将编译后的工作流赋值给FastAPI应用实例
    app.state.workflow = workflow

# 添加可视化路由

# 在启动事件中创建的应用实例会被FastAPI使用
__all__ = ["app"]
