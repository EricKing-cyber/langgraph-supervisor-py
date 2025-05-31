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
from langgraph.graph import Sta
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
    
    # 获取工作流图
    workflow_graph = base_supervisor.workflow.graph  # 使用正确的属性路径
    
    # 创建增强型主管代理
    enhanced_supervisor = EnhancedSupervisor(base_supervisor)
    
    # 可视化通信拓扑
    enhanced_supervisor.visualize_topology("topology.png")
    
    # 可视化工作流程
    enhanced_supervisor.visualize_workflow("workflow.png")

# 添加可视化路由

# 创建语言模型实例
model = ChatOpenAI(model="gpt-4o")

# 修复代理导入
from multi_agent_system.agents.math_agent import MathAgent
from multi_agent_system.agents.weather_agent import WeatherAgent

# 构建工作流
base_supervisor = create_supervisor(
    [MathAgent(name="math_expert"), WeatherAgent(name="weather_forecast")],
    model=model
)
workflow = base_supervisor.workflow

# 编译为可执行对象
app = workflow.compile()

__all__ = ["app"]