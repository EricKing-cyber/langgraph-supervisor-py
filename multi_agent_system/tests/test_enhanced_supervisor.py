import unittest
from multi_agent_system.workflows.supervisor_workflow import EnhancedSupervisor
from langgraph_supervisor.supervisor import create_supervisor
from multi_agent_system.strategies import AgentProfile, TaskContext
from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph
from multi_agent_system.model_utils import create_model

# 在模块级别定义app变量
app = None


class TestEnhancedSupervisor(unittest.TestCase):
    """测试增强型主管代理的功能"""
    def setUp(self):
        """设置测试环境"""
        # 创建示例代理配置
        self.agents = [
            type('Agent', (), {"name": "math_expert", "type": "math", "capacity": 5})(),
            type('Agent', (), {"name": "weather_forecast", "type": "weather", "capacity": 4})(),
            type('Agent', (), {"name": "logistics_planner", "type": "logistics", "capacity": 3})()
        ]
        
        # 使用真实语言模型
        self.base_supervisor = create_supervisor(
            self.agents,
            model=create_model( "cogito:14b")  # 使用实际的语言模型
        )
        
        # 创建增强型主管代理
        self.enhanced_supervisor = EnhancedSupervisor(self.base_supervisor)

    def test_complex_task_handling(self):
        """测试复杂任务处理能力"""
        # 创建测试任务
        task_context = TaskContext(
            required_skills={"weather_forecast", "logistics_optimization"},
            complexity=0.8,
            urgency=0.6,
            history=[]
        )
        
        # 执行动态调度
        result = self.enhanced_supervisor.dynamic_handoff(task_context)
        
        # 验证基本结果
        self.assertIsNotNone(result)
        self.assertIn("selected_agents", result.get("config", {}))
        self.assertIn("resources", result.get("config", {}))
        self.assertIn("links", result.get("config", {}))
        
        # 验证通信链路
        links = result["config"]["links"]
        self.assertGreater(len(links), 0)
        
        # 验证资源分配
        resources = result["config"]["resources"]
        self.assertGreater(len(resources), 0)
        
        # 验证效率评分
        efficiency = result["config"].get("efficiency", 0)
        self.assertGreaterEqual(efficiency, 0.3)  # 最低预期效率

    def test_compile_method(self):
        """测试编译工作流图的功能"""
        # 调用compile方法
        compiled_graph = self.enhanced_supervisor.compile()
        
        # 验证返回值不为None
        self.assertIsNotNone(compiled_graph)

def get_app():
    """获取编译后的应用实例"""
    # 创建测试实例
    test_instance = TestEnhancedSupervisor()
    
    # 执行setUp方法初始化
    test_instance.setUp()
    
    # 获取编译后的应用
    return test_instance.enhanced_supervisor.compile()

# 直接将 app 指向 get_app() 的返回值（工厂函数）
app = get_app()

if __name__ == "__main__":
    # 获取编译后的应用
    app = get_app()
    
    # 自动执行langgraph dev命令
    import subprocess
    subprocess.run(["langgraph", "dev"])
