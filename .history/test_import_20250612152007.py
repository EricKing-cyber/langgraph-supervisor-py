"""
测试模块导入
仅测试能否正确导入新添加的功能模块
"""

def test_evaluation_module_import():
    """测试评估模块导入"""
    try:
        from multi_agent_system.tools.evaluation_tools import get_evaluation_tools
        print("评估模块导入成功")
        return True
    except Exception as e:
        print(f"评估模块导入失败: {e}")
        return False

def test_persistence_module_import():
    """测试数据持久化模块导入"""
    try:
        from multi_agent_system.tools.data_persistence_tools import get_persistence_tools
        print("数据持久化模块导入成功")
        return True
    except Exception as e:
        print(f"数据持久化模块导入失败: {e}")
        return False

def test_graph_module_import():
    """测试图分析模块导入"""
    try:
        from multi_agent_system.tools.graph_analysis_tools import get_graph_analysis_tools
        print("图分析模块导入成功")
        return True
    except Exception as e:
        print(f"图分析模块导入失败: {e}")
        return False

def test_deep_research_workflow():
    """测试深度研究工作流导入"""
    try:
        from multi_agent_system.workflows.deep_research_workflow import build_deep_research_workflow
        print("深度研究工作流导入成功")
        return True
    except Exception as e:
        print(f"深度研究工作流导入失败: {e}")
        return False

if __name__ == "__main__":
    print("=== 测试模块导入 ===")
    eval_result = test_evaluation_module_import()
    persistence_result = test_persistence_module_import()
    graph_result = test_graph_module_import()
    workflow_result = test_deep_research_workflow()
    
    print("\n=== 测试结果汇总 ===")
    print(f"评估模块: {'成功' if eval_result else '失败'}")
    print(f"数据持久化: {'成功' if persistence_result else '失败'}")
    print(f"图分析: {'成功' if graph_result else '失败'}")
    print(f"工作流: {'成功' if workflow_result else '失败'}")
    
    if eval_result and persistence_result and graph_result and workflow_result:
        print("\n所有模块导入成功!")
    else:
        print("\n一些模块导入失败，请检查错误信息") 