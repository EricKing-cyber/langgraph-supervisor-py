"""
测试工作流集成
测试工具模块是否能被正确加载到工作流中
"""

from multi_agent_system.workflows.deep_research_workflow import get_supervisor_tools
from multi_agent_system.tools.evaluation_tools import get_evaluation_tools
from multi_agent_system.tools.data_persistence_tools import get_persistence_tools
from multi_agent_system.tools.graph_analysis_tools import get_graph_analysis_tools

def test_tools_availability():
    """测试各工具是否可用"""
    # 获取各个工具集
    print("获取评估工具...")
    eval_tools = get_evaluation_tools()
    print(f"评估工具数量: {len(eval_tools)}")
    
    print("\n获取数据持久化工具...")
    persistence_tools = get_persistence_tools()
    print(f"数据持久化工具数量: {len(persistence_tools)}")
    
    print("\n获取图分析工具...")
    graph_tools = get_graph_analysis_tools()
    print(f"图分析工具数量: {len(graph_tools)}")
    
    return all([eval_tools, persistence_tools, graph_tools])

def test_workflow_tools():
    """测试工作流中的工具集成"""
    print("\n获取工作流工具...")
    workflow_tools = get_supervisor_tools()
    print(f"工作流工具总数: {len(workflow_tools)}")
    
    # 检查工具名称
    tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in workflow_tools]
    print(f"\n工具名称列表: {tool_names[:5]}...")
    
    # 检查是否包含各种类型的工具
    basic_tools = ["sections", "introduction", "conclusion", "finishReport", "question"]
    eval_tools = ["evaluate_report_quality", "evaluate_groundedness"]
    persistence_tools = ["save_report_to_file", "read_report_from_file"]
    graph_tools = ["create_knowledge_graph", "add_entities_to_graph"]
    
    contains_basic = any(name.lower() in [t.lower() for t in tool_names] for name in basic_tools)
    contains_eval = any(name.lower() in [t.lower() for t in tool_names] for name in eval_tools)
    contains_persistence = any(name.lower() in [t.lower() for t in tool_names] for name in persistence_tools)
    contains_graph = any(name.lower() in [t.lower() for t in tool_names] for name in graph_tools)
    
    print(f"\n包含基础工具: {contains_basic}")
    print(f"包含评估工具: {contains_eval}")
    print(f"包含数据持久化工具: {contains_persistence}")
    print(f"包含图分析工具: {contains_graph}")
    
    return contains_basic and contains_eval and contains_persistence and contains_graph

if __name__ == "__main__":
    print("=== 测试工作流集成 ===")
    
    print("测试1: 各工具模块可用性")
    tools_available = test_tools_availability()
    
    print("\n测试2: 工作流工具集成")
    workflow_integration = test_workflow_tools()
    
    print("\n=== 测试结果汇总 ===")
    print(f"工具可用性: {'成功' if tools_available else '失败'}")
    print(f"工作流集成: {'成功' if workflow_integration else '失败'}")
    
    if tools_available and workflow_integration:
        print("\n工作流集成测试成功!")
    else:
        print("\n工作流集成测试失败，请查看错误信息") 