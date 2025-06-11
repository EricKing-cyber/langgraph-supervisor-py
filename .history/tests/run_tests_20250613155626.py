"""
测试启动脚本 - 用于运行针对功能模块的测试

使用方法:
    python tests/run_tests.py parallel  # 测试并行处理功能
    python tests/run_tests.py graph     # 测试图分析功能
    python tests/run_tests.py cache     # 测试数据缓存功能
    python tests/run_tests.py all       # 测试所有功能
"""

import sys
import os
import importlib.util
from pathlib import Path

# 确保能够导入项目模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def import_module_from_path(module_path):
    """从文件路径导入模块"""
    spec = importlib.util.spec_from_file_location("test_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_parallel_test():
    """运行并行处理测试"""
    print("\n==========================================")
    print("正在测试并行处理功能...")
    print("==========================================")
    
    test_module = import_module_from_path("tests/test_deep_research_parallel_processing.py")
    test = test_module.TestParallelProcessing()
    
    # 测试 Section 类的 content 字段
    print("测试 Section 类的 content 字段...")
    test.test_section_content_field()
    print("✓ Section 类的 content 字段测试通过")
    
    # 测试并行处理
    print("测试 initiate_final_section_writing 函数...")
    test.test_initiate_final_section_writing()
    print("✓ 并行处理功能测试通过")

def run_graph_test():
    """运行图分析功能测试"""
    print("\n==========================================")
    print("正在测试图分析功能...")
    print("==========================================")
    
    test_module = import_module_from_path("tests/test_deep_research_parallel_processing.py")
    test = test_module.TestParallelProcessing()
    
    # 测试工具
    print("测试图分析工具...")
    test.test_graph_analysis_tools()
    print("✓ 图分析工具测试通过")
    
    # 准备测试数据
    graph_data = {
        "entities": [
            {"id": "e1", "name": "实体1", "type": "person"},
            {"id": "e2", "name": "实体2", "type": "organization"},
            {"id": "e3", "name": "实体3", "type": "place"},
            {"id": "e4", "name": "实体4中文测试", "type": "concept"}
        ],
        "relationships": [
            {"source": "e1", "target": "e2", "type": "works_for"},
            {"source": "e2", "target": "e3", "type": "located_in"},
            {"source": "e4", "target": "e1", "type": "related_to"}
        ],
        "name": "测试知识图谱"
    }
    
    # 测试图谱创建
    print("测试创建实体图谱...")
    test.test_create_entity_graph(graph_data)
    print("✓ 创建实体图谱测试通过")
    
    # 测试图谱可视化
    print("测试图谱可视化...")
    test.test_visualize_graph(graph_data)
    print("✓ 图谱可视化测试通过")

def run_cache_test():
    """运行数据缓存功能测试"""
    print("\n==========================================")
    print("正在测试数据缓存功能...")
    print("==========================================")
    
    test_module = import_module_from_path("tests/test_deep_research_parallel_processing.py")
    test = test_module.TestParallelProcessing()
    
    # 测试数据持久化
    print("测试数据持久化功能...")
    test.test_data_persistence()
    print("✓ 数据持久化测试通过")

def run_all_tests():
    """运行所有测试"""
    run_parallel_test()
    run_graph_test()
    run_cache_test()

def print_usage():
    """打印用法指南"""
    print("\n用法:")
    print("  python tests/run_tests.py [测试类型]")
    print("\n可选的测试类型:")
    print("  parallel  - 测试并行处理功能")
    print("  graph     - 测试图分析功能")
    print("  cache     - 测试数据缓存功能")
    print("  all       - 测试所有功能")
    print("\n示例:")
    print("  python tests/run_tests.py parallel")

if __name__ == "__main__":
    # 确保我们在项目根目录下运行
    if not os.path.exists("tests/run_tests.py"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(os.path.dirname(script_dir))
        if not os.path.exists("tests/run_tests.py"):
            print("错误: 请在项目根目录下运行此脚本")
            sys.exit(1)

    # 解析命令行参数
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)
    
    test_type = sys.argv[1].lower()
    
    if test_type == "parallel":
        run_parallel_test()
    elif test_type == "graph":
        run_graph_test()
    elif test_type == "cache":
        run_cache_test()
    elif test_type == "all":
        run_all_tests()
    else:
        print(f"错误: 未知的测试类型 '{test_type}'")
        print_usage()
        sys.exit(1)
    
    print("\n所有指定的测试已完成!") 