import os
import sys
from pathlib import Path
from pprint import pprint
import json

# 添加父级目录到系统路径，确保可以导入模块
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from multi_agent_system.workflows.deep_research_workflow import build_deep_research_workflow
from multi_agent_system.model_utils import create_model
from multi_agent_system.agents import create_research_agent
from multi_agent_system.config.deep_research_config import create_research_config

def test_parallel_tool_calls():
    """测试并行工具调用配置"""
    print("测试并行工具调用...")
    
    # 创建语言模型
    model = create_model("gpt-4.1-2025-04-14")
    
    # 创建研究代理
    ai_research_agent = create_research_agent("ai_technology", "gpt-4.1-2025-04-14", search_api="tavily")
    finance_research_agent = create_research_agent("finance", "gpt-4.1-2025-04-14", search_api="tavily")
    science_research_agent = create_research_agent("science", "gpt-4.1-2025-04-14", search_api="tavily")
    
    # 创建研究配置并添加并行工具调用
    research_config = create_research_config(
        search_api="tavily",
        include_source_str=True,
        ask_for_clarification=True,
        process_search_results="summarize",
        supervisor_model="gpt-4.1-2025-04-14",
        researcher_model="gpt-4.1-2025-04-14"
    )
    
    # 手动添加并行工具调用配置
    if "configurable" not in research_config:
        research_config["configurable"] = {}
    research_config["configurable"]["parallel_tool_calls"] = True
    
    # 构建深度研究工作流
    graph = build_deep_research_workflow(
        [ai_research_agent, finance_research_agent, science_research_agent],
        model,
        research_config
    )
    
    # 编译工作流图
    compiled_graph = graph.compile()
    
    # 检查和打印配置
    if hasattr(compiled_graph, 'config'):
        print("工作流图配置:")
        pprint(compiled_graph.config)
    else:
        print("工作流图没有config属性")
        
    # 查看图对象的属性
    print("\n工作流图属性:")
    for attr in dir(compiled_graph):
        if attr.startswith('_'):
            continue
        print(f"- {attr}")
        
    # 尝试获取模型配置
    try:
        from langchain_core.globals import get_debug
        print("\n全局调试配置:")
        pprint(get_debug())
    except ImportError:
        print("无法导入langchain_core.globals")

if __name__ == "__main__":
    test_parallel_tool_calls() 