#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
综合工具测试脚本
同时支持两种工具包装风格：_original和原始函数直接调用
"""

import os
import sys
import json
from pathlib import Path

# 确保数据目录存在
Path("data").mkdir(exist_ok=True)
Path("data/reports").mkdir(exist_ok=True)
Path("data/evaluations").mkdir(exist_ok=True)
Path("data/graphs").mkdir(exist_ok=True)
Path("data/cache").mkdir(exist_ok=True)

class ToolTester:
    """
    工具测试器基类
    """
    def __init__(self, module_path):
        self.module_path = module_path
        self.module = None
    
    def import_module(self):
        """导入模块"""
        try:
            self.module = __import__(self.module_path, fromlist=['*'])
            return True
        except Exception as e:
            print(f"导入模块失败: {self.module_path}")
            print(f"错误: {str(e)}")
            return False
    
    def get_function(self, func_name):
        """获取函数，无论它是原始函数还是工具包装函数"""
        if not self.module:
            self.import_module()
        
        if not hasattr(self.module, func_name):
            print(f"模块中不存在函数: {func_name}")
            return None
        
        func = getattr(self.module, func_name)
        
        # 尝试获取原始函数（如果存在_original属性）
        if hasattr(func, '_original'):
            print(f"使用{func_name}._original")
            return func._original
        elif hasattr(func, '__wrapped__'):
            print(f"使用{func_name}.__wrapped__")
            return func.__wrapped__
        else:
            print(f"使用直接函数: {func_name}")
            return func
    
    def run_tests(self):
        """运行测试的抽象方法"""
        raise NotImplementedError("子类必须实现run_tests方法")


class PersistenceToolTester(ToolTester):
    """
    数据持久化工具测试器
    """
    def __init__(self):
        super().__init__('multi_agent_system.tools.data_persistence_tools')
    
    def run_tests(self):
        print("\n===== 测试数据持久化工具 =====")
        
        # 测试保存和读取文件
        save_report = self.get_function('save_report_to_file')
        read_report = self.get_function('read_report_from_file')
        list_reports = self.get_function('list_saved_reports')
        cache_data = self.get_function('cache_data')
        get_cached_data = self.get_function('get_cached_data')
        
        if not all([save_report, read_report, list_reports, cache_data, get_cached_data]):
            print("无法获取所有必要的函数，测试终止。")
            return False
        
        # 创建测试报告
        report_content = """# 集成测试报告

这是一个用于测试数据持久化工具的集成测试报告。

## 第一部分
这里是报告的第一部分内容。

## 第二部分
这里是报告的第二部分内容。
"""
        
        # 保存报告
        print("保存报告...")
        filepath = save_report(report_content, "集成测试", "md")
        print(f"文件保存成功: {filepath}")
        
        # 读取报告
        print("\n读取报告...")
        content = read_report(filepath)
        print(f"读取成功，长度: {len(content)} 字符")
        
        # 列出报告
        print("\n列出报告...")
        reports = list_reports()
        print(f"找到 {len(reports)} 个报告")
        
        # 测试缓存
        print("\n缓存数据...")
        test_data = {"type": "test", "value": 123, "items": ["a", "b", "c"]}
        cache_key = cache_data(test_data, "integration_test", 3600)
        print(f"缓存成功，键值: {cache_key}")
        
        # 获取缓存
        print("\n读取缓存...")
        cached = get_cached_data(cache_key)
        print(f"读取缓存成功: {type(cached)}")
        
        print("数据持久化工具测试完成!\n")
        return True


class GraphToolTester(ToolTester):
    """
    图分析工具测试器
    """
    def __init__(self):
        super().__init__('multi_agent_system.tools.graph_analysis_tools')
    
    def run_tests(self):
        print("\n===== 测试图分析工具 =====")
        
        # 获取函数
        create_graph = self.get_function('create_entity_graph')
        analyze_centrality = self.get_function('analyze_graph_centrality')
        find_path = self.get_function('find_shortest_path')
        
        if not all([create_graph, analyze_centrality, find_path]):
            print("无法获取所有必要的函数，测试终止。")
            return False
        
        # 创建测试实体和关系
        entities = [
            {"id": "e1", "name": "张三", "type": "人物"},
            {"id": "e2", "name": "李四", "type": "人物"},
            {"id": "e3", "name": "王五", "type": "人物"},
            {"id": "e4", "name": "ABC公司", "type": "组织"},
            {"id": "e5", "name": "XYZ科技", "type": "组织"}
        ]
        
        relationships = [
            {"source": "e1", "target": "e4", "type": "就职于"},
            {"source": "e2", "target": "e4", "type": "就职于"},
            {"source": "e3", "target": "e5", "type": "创立了"},
            {"source": "e4", "target": "e5", "type": "合作伙伴"},
            {"source": "e2", "target": "e3", "type": "朋友"},
            {"source": "e1", "target": "e2", "type": "认识"}
        ]
        
        # 创建图
        print("创建图...")
        try:
            graph_file = create_graph(entities, relationships, "集成测试图")
            print(f"图创建成功: {graph_file}")
            
            # 分析中心性
            print("\n分析图中心性...")
            centrality = analyze_centrality(graph_file)
            
            if isinstance(centrality, dict) and len(centrality) > 0:
                print(f"中心性分析成功，包含 {len(centrality)} 种指标")
                for metric, values in centrality.items():
                    if isinstance(values, list) and len(values) > 0:
                        top_entity = values[0]
                        print(f"  - {metric}: 顶部实体 '{top_entity.get('name', '')}' 分数为 {top_entity.get('score', 0)}")
            else:
                print(f"中心性分析错误或返回空结果: {centrality}")
            
            # 查找路径
            print("\n寻找最短路径...")
            path = find_path(graph_file, "e1", "e5")
            
            if isinstance(path, dict) and 'path_description' in path:
                print(f"路径查找成功: {path['path_description']}")
            else:
                print(f"路径查找返回: {path}")
                
        except Exception as e:
            print(f"图分析工具测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print("图分析工具测试完成!\n")
        return True


class EvaluationToolTester(ToolTester):
    """
    评估工具测试器
    """
    def __init__(self):
        super().__init__('multi_agent_system.tools.evaluation_tools')
    
    def run_tests(self):
        print("\n===== 测试评估工具 =====")
        
        # 获取函数
        eval_quality = self.get_function('evaluate_report_quality')
        eval_reliability = self.get_function('evaluate_reliability')
        
        if not all([eval_quality, eval_reliability]):
            print("无法获取所有必要的函数，测试终止。")
            return False
        
        # 创建测试文本
        test_report = """# 大语言模型发展趋势研究

## 引言
大语言模型(LLM)是近年来人工智能领域最重要的突破之一。本报告分析大语言模型的发展趋势。

## 模型规模演化
从GPT-1的1.17亿参数到GPT-3的1750亿参数[1]，再到GPT-4的未公开参数规模(估计超过1万亿)[2]，
模型规模呈指数级增长。这一趋势可能会在未来几年继续，但也面临计算资源和训练成本的挑战。

## 多模态能力
最新的大语言模型如GPT-4V、Claude 3 Opus和Gemini等都具备多模态处理能力，可以同时理解文本和图像[3]。
根据OpenAI的研究，这种能力显著提升了模型在复杂场景中的表现。

## 推理与知识整合
虽然大语言模型在推理能力上取得了长足进步，但研究表明它们仍然存在事实混淆的问题[4]。
未来的发展方向包括知识库增强和外部工具调用。

## 结论
大语言模型正朝着规模更大、能力更全面、推理更准确的方向发展，未来将深刻改变人机交互方式。

## 参考文献
[1] Brown, T. B., et al. (2020). Language Models are Few-Shot Learners.
[2] OpenAI. (2023). GPT-4 Technical Report.
[3] Bubeck, S., et al. (2023). Sparks of Artificial General Intelligence.
[4] Mallen, A., et al. (2023). When hallucinations improve reasoning: Emergent analogical inference.
"""
        
        # 评估质量
        print("评估报告质量...")
        try:
            quality_result = eval_quality(test_report)
            
            if isinstance(quality_result, dict) and 'average_score' in quality_result:
                print(f"质量评估成功，平均分: {quality_result['average_score']}, 等级: {quality_result['rating']}")
                print("评分详情:")
                for criterion, score in quality_result.get('scores', {}).items():
                    print(f"  - {criterion}: {score}")
            else:
                print(f"质量评估错误或返回不符合预期: {quality_result}")
        except Exception as e:
            print(f"质量评估测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        # 评估可靠性
        print("\n评估可靠性...")
        try:
            reliability_result = eval_reliability(test_report)
            
            if isinstance(reliability_result, dict) and 'reliability_score' in reliability_result:
                print(f"可靠性评估成功，分数: {reliability_result['reliability_score']}, 等级: {reliability_result['reliability_rating']}")
            else:
                print(f"可靠性评估错误或返回不符合预期: {reliability_result}")
        except Exception as e:
            print(f"可靠性评估测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print("评估工具测试完成!\n")
        return True


def main():
    """主函数"""
    print("===== 开始综合工具测试 =====")
    
    # 测试数据持久化工具
    persistence_tester = PersistenceToolTester()
    persistence_success = persistence_tester.run_tests()
    
    # 测试图分析工具
    graph_tester = GraphToolTester()
    graph_success = graph_tester.run_tests()
    
    # 测试评估工具
    eval_tester = EvaluationToolTester()
    eval_success = eval_tester.run_tests()
    
    # 输出总结
    print("\n===== 测试结果总结 =====")
    print(f"数据持久化工具: {'成功' if persistence_success else '失败'}")
    print(f"图分析工具: {'成功' if graph_success else '失败'}")
    print(f"评估工具: {'成功' if eval_success else '失败'}")
    
    overall_success = all([persistence_success, graph_success, eval_success])
    print(f"\n总体测试结果: {'成功' if overall_success else '失败'}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 