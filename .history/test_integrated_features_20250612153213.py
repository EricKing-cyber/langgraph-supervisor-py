"""
集成功能测试脚本

测试新集成的评估模块、数据持久化和图分析功能是否正常工作
"""

import os
import asyncio
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from pathlib import Path

from langgraph_supervisor.supervisor import create_supervisor
from multi_agent_system.model_utils import create_model
from multi_agent_system.agents import create_research_agent
from multi_agent_system.workflows.deep_research_workflow import build_deep_research_workflow
from multi_agent_system.config import create_research_config
from multi_agent_system.tools.evaluation_tools import (
    evaluate_report_quality, 
    evaluate_groundedness, 
    get_evaluation_criteria,
    get_evaluation_summary
)
from multi_agent_system.tools.data_persistence_tools import (
    save_report_to_file,
    read_report_from_file,
    save_evaluation_results,
    cache_data,
    get_cached_data,
    list_saved_reports,
    list_evaluation_results
)
from multi_agent_system.tools.graph_analysis_tools import (
    create_knowledge_graph,
    add_entities_to_graph,
    add_relationships_to_graph,
    analyze_graph_centrality,
    detect_communities,
    list_knowledge_graphs
)


async def test_evaluation_module():
    """测试评估模块功能"""
    print("=== 测试评估模块 ===")
    
    # 创建一个简单报告用于测试
    test_report = """
    # 深度学习技术发展趋势分析
    
    ## 引言
    深度学习技术在近年来取得了显著进步，影响了多个行业的发展。
    
    ## 大型语言模型
    大型语言模型如GPT-4和Claude已经展现出接近人类的语言理解和生成能力。这些模型采用了Transformer架构，通过大规模预训练和微调实现了卓越的性能。
    
    ## 多模态模型
    多模态模型能够同时处理文本、图像和音频等多种输入类型，为跨模态理解和生成提供了可能。
    
    ## 结论
    深度学习技术将继续快速发展，推动人工智能在更多领域的应用。
    """
    
    test_query = "分析深度学习技术的最新发展趋势"
    
    # 测试评估报告质量
    quality_result = evaluate_report_quality(test_report, test_query)
    print(f"报告质量评估结果: {quality_result}")
    
    # 测试评估可靠性
    groundedness_result = evaluate_groundedness(test_report, "深度学习技术采用了Transformer架构，通过大规模预训练实现了卓越的性能。")
    print(f"可靠性评估结果: {groundedness_result}")
    
    # 测试获取评估标准
    criteria = get_evaluation_criteria()
    print(f"评估标准数: {len(criteria.keys())}")
    
    # 测试获取评估总结
    combined_results = {**quality_result, **groundedness_result}
    summary = get_evaluation_summary(combined_results)
    print(f"评估总结: {summary[:100]}...")
    
    return quality_result


async def test_data_persistence():
    """测试数据持久化功能"""
    print("\n=== 测试数据持久化 ===")
    
    # 确保数据目录存在
    data_dir = Path("data")
    reports_dir = data_dir / "reports"
    for directory in [data_dir, reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # 测试保存报告
    test_report = "# 测试报告\n\n这是一个用于测试数据持久化功能的报告。"
    saved_path = save_report_to_file(test_report, "测试主题", "md")
    print(f"保存报告到: {saved_path}")
    
    # 测试读取报告
    read_content = read_report_from_file(saved_path)
    content_match = read_content.strip() == test_report.strip()
    print(f"读取报告内容匹配: {content_match}")
    
    # 测试缓存数据
    test_data = {"key1": "value1", "key2": [1, 2, 3]}
    cache_key = cache_data(test_data, "test_key")
    print(f"缓存数据键: {cache_key}")
    
    # 测试获取缓存数据
    cached_data = get_cached_data("test_key")
    data_match = (cached_data.get("key1") == test_data["key1"])
    print(f"缓存数据匹配: {data_match}")
    
    # 测试列出保存的报告
    reports = list_saved_reports()
    print(f"保存的报告数: {len(reports)}")
    
    # 测试保存评估结果
    eval_results = {
        "overall_quality": {"score": 0.8, "comment": "报告结构清晰"},
        "relevance": {"score": 0.9, "comment": "内容与主题高度相关"},
        "average_score": 0.85
    }
    eval_path = save_evaluation_results(eval_results, "test_report")
    print(f"保存评估结果到: {eval_path}")
    
    # 测试列出评估结果
    eval_results_list = list_evaluation_results()
    print(f"保存的评估结果数: {len(eval_results_list)}")
    
    return saved_path, eval_path


async def test_graph_analysis():
    """测试图分析功能"""
    print("\n=== 测试图分析 ===")
    
    # 创建测试知识图谱
    graph_name = "test_graph"
    result = create_knowledge_graph(graph_name)
    print(f"创建图谱结果: {result}")
    
    # 添加实体
    entities = [
        {"id": "entity1", "label": "Person", "properties": {"name": "张三", "age": 30}},
        {"id": "entity2", "label": "Person", "properties": {"name": "李四", "age": 28}},
        {"id": "entity3", "label": "Organization", "properties": {"name": "科技公司"}},
        {"id": "entity4", "label": "Technology", "properties": {"name": "人工智能"}},
        {"id": "entity5", "label": "Technology", "properties": {"name": "大数据"}}
    ]
    add_result = add_entities_to_graph(graph_name, entities)
    print(f"添加实体结果: {add_result}")
    
    # 添加关系
    relationships = [
        {"source": "entity1", "target": "entity3", "label": "WORKS_FOR", "weight": 1.0},
        {"source": "entity2", "target": "entity3", "label": "WORKS_FOR", "weight": 1.0},
        {"source": "entity3", "target": "entity4", "label": "DEVELOPS", "weight": 1.5},
        {"source": "entity3", "target": "entity5", "label": "USES", "weight": 1.2},
        {"source": "entity1", "target": "entity4", "label": "EXPERT_IN", "weight": 2.0},
        {"source": "entity2", "target": "entity5", "label": "EXPERT_IN", "weight": 1.8},
        {"source": "entity4", "target": "entity5", "label": "RELATED_TO", "weight": 1.5}
    ]
    rel_result = add_relationships_to_graph(graph_name, relationships)
    print(f"添加关系结果: {rel_result}")
    
    # 分析中心节点
    centrality_result = analyze_graph_centrality(graph_name, top_n=3)
    print(f"中心节点分析结果: {centrality_result}")
    
    # 社区检测
    community_result = detect_communities(graph_name)
    print(f"社区检测结果: {community_result}")
    
    # 列出知识图谱
    graphs = list_knowledge_graphs()
    print(f"知识图谱列表: {graphs}")
    
    return centrality_result, community_result


async def test_full_integration():
    """测试完整集成"""
    print("\n=== 测试完整集成 ===")
    
    # 创建模型
    model_name = "gpt-4.1-2025-04-14"
    print(f"创建模型: {model_name}")
    model = create_model(model_name)
    
    # 创建研究代理
    ai_research_agent = create_research_agent("ai_technology", model_name, search_api="tavily")
    science_research_agent = create_research_agent("science", model_name, search_api="tavily")
    
    # 创建深度研究配置
    config = create_research_config(
        search_api="tavily",
        ask_for_clarification=True,
        include_source_str=True
    )
    
    # 构建深度研究流程
    print("构建深度研究工作流")
    research_workflow = build_deep_research_workflow(
        research_agents=[ai_research_agent, science_research_agent],
        model=model,
        config=config
    )
    
    # 检查流程是否成功构建
    print(f"工作流构建成功: {research_workflow is not None}")
    
    return research_workflow


async def main():
    """主测试函数"""
    try:
        # 运行评估模块测试
        eval_result = await test_evaluation_module()
        
        # 运行数据持久化测试
        persistence_result = await test_data_persistence()
        
        # 运行图分析测试
        graph_result = await test_graph_analysis()
        
        # 运行完整集成测试
        workflow = await test_full_integration()
        
        print("\n=== 测试结果汇总 ===")
        print(f"1. 评估模块: {'成功' if eval_result else '失败'}")
        print(f"2. 数据持久化: {'成功' if persistence_result else '失败'}")
        print(f"3. 图分析功能: {'成功' if graph_result else '失败'}")
        print(f"4. 完整集成: {'成功' if workflow else '失败'}")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 