from langgraph_supervisor.supervisor import create_supervisor
from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import tool, BaseTool
from typing import List, Dict, Any, Callable
from langchain_core.runnables import RunnableConfig
from functools import wraps

# 导入open_deep_research中的相关模块
from open_deep_research.src.open_deep_research.multi_agent import (
    supervisor, 
    Sections, 
    Introduction, 
    Conclusion, 
    FinishReport, 
    Question
)
from open_deep_research.src.open_deep_research.prompts import SUPERVISOR_INSTRUCTIONS
from open_deep_research.src.open_deep_research.utils import get_today_str
from open_deep_research.src.open_deep_research.configuration import Configuration

# 导入新添加的工具
from multi_agent_system.tools.evaluation_tools import get_evaluation_tools
from multi_agent_system.tools.data_persistence_tools import get_persistence_tools
from multi_agent_system.tools.graph_analysis_tools import get_graph_analysis_tools

# 导入配置工具
from multi_agent_system.config.deep_research_config import config_to_runnable_config

def get_supervisor_tools() -> list[BaseTool]:
    """获取主管代理工具"""
    base_tools = [
        tool(Sections), 
        tool(Introduction), 
        tool(Conclusion), 
        tool(FinishReport),
        tool(Question)
    ]
    
    # 添加评估工具
    evaluation_tools = get_evaluation_tools()
    
    # 添加数据持久化工具
    persistence_tools = get_persistence_tools()
    
    # 添加图分析工具
    graph_analysis_tools = get_graph_analysis_tools()
    
    # 合并所有工具
    all_tools = base_tools + evaluation_tools + persistence_tools + graph_analysis_tools
    
    return all_tools

def with_config_injection(graph_func):
    """装饰器：向图的调用中注入配置"""
    @wraps(graph_func)
    def wrapper(state, config=None):
        # 如果配置存在，使用它
        if hasattr(build_deep_research_workflow, 'config') and build_deep_research_workflow.config:
            # 合并传入的配置和存储的配置
            stored_config = config_to_runnable_config(build_deep_research_workflow.config)
            if config:
                merged_config = config.copy() if config else {}
                if 'configurable' in stored_config and 'configurable' in merged_config:
                    merged_config['configurable'].update(stored_config['configurable'])
                else:
                    merged_config.update(stored_config)
                return graph_func(state, merged_config)
            else:
                return graph_func(state, stored_config)
        else:
            # 如果没有存储配置，使用传入的配置
            return graph_func(state, config)
    
    return wrapper

def build_deep_research_workflow(research_agents: list, model: LanguageModelLike, config: Dict[str, Any] = None):
    """
    构建深度研究工作流，集成open_deep_research的主管代理架构
    
    Args:
        research_agents: 研究员代理列表
        model: 语言模型
        config: 配置信息，用于设置deep_research的行为（将通过后续调用时的config传递）
    
    Returns:
        构建好的主管工作流图
    """
    # 初始化配置 - 保存为类变量供后续使用
    if config is None:
        config = {}
    
    # 保存配置以便后续使用
    build_deep_research_workflow.config = config
    
    # 获取主管工具
    supervisor_tools = get_supervisor_tools()
    
    # 创建增强的提示词，明确指导研究主管如何分配任务给不同领域的研究员
    enhanced_supervisor_prompt = f"""
    你是一个深度研究团队的主管，负责管理多个领域的研究专家。你的职责是协调研究工作、分配任务、评估研究进度并整合最终报告。

    【警告】你不能自己直接生成研究内容！你必须将具体研究工作分配给团队中的专业研究员执行。

    你的团队成员包括:
    1. ai_technology_researcher - AI技术研究专家，调用方式：使用transfer_to_ai_technology_researcher工具
       - 擅长领域：人工智能、机器学习、深度学习、大语言模型、计算机视觉、语音识别等
       - 适用任务：AI技术趋势分析、算法研究、技术应用分析等

    2. finance_researcher - 金融领域研究专家，调用方式：使用transfer_to_finance_researcher工具
       - 擅长领域：经济学、金融市场、投资分析、风险管理、金融科技、加密货币等
       - 适用任务：市场趋势分析、投资策略研究、经济政策影响分析等

    3. science_researcher - 科学领域研究专家，调用方式：使用transfer_to_science_researcher工具
       - 擅长领域：物理学、化学、生物学、环境科学、医学、天文学等
       - 适用任务：科学前沿研究分析、技术可行性研究、科学文献综述等
       
    4. legal_researcher - 法律领域研究专家，调用方式：使用transfer_to_legal_researcher工具
       - 擅长领域：法律条文检索、案例分析、合规性审查、合同条款审查等
       - 适用任务：法律风险评估、司法判决预测、法规解读分析等
       
    5. medical_researcher - 医疗健康研究专家，调用方式：使用transfer_to_medical_researcher工具
       - 擅长领域：医学文献检索、临床试验分析、药物研发、疾病诊断辅助等
       - 适用任务：新药研发趋势分析、医疗政策研究、疾病治疗方案比较等
       
    6. engineering_researcher - 工程技术研究专家，调用方式：使用transfer_to_engineering_researcher工具
       - 擅长领域：技术标准查询、专利分析、工程方案优化、建筑设计优化等
       - 适用任务：机械故障诊断、材料科学创新、工程效率分析等
       
    7. socialscience_researcher - 社会科学研究专家，调用方式：使用transfer_to_socialscience_researcher工具
       - 擅长领域：社会调查数据分析、政策影响评估、市场调研报告等
       - 适用任务：公共政策效果分析、行为经济学研究、消费趋势分析等
       
    8. climate_researcher - 气候科学研究专家，调用方式：使用transfer_to_climate_researcher工具
       - 擅长领域：气候模型分析、环境数据挖掘、气候变化预测等
       - 适用任务：碳排放政策制定、可持续发展研究、生态环境保护分析等

    【新增功能】你现在具备以下强大的功能:
    
    1. 评估功能 - 你可以使用以下工具评估研究报告的质量:
       - evaluate_report_quality: 评估报告的整体质量、相关性和结构
       - evaluate_groundedness: 评估报告内容的可靠性
       - get_evaluation_criteria: 获取评估标准详情
       - get_evaluation_summary: 生成评估总结
    
    2. 数据持久化功能 - 你可以使用以下工具保存和读取数据:
       - save_report_to_file: 将研究报告保存到文件
       - read_report_from_file: 从文件读取研究报告
       - save_evaluation_results: 保存评估结果
       - cache_data: 缓存数据
       - get_cached_data: 获取缓存数据
       - list_saved_reports: 列出所有保存的报告
       - list_evaluation_results: 列出所有评估结果
    
    3. 图分析功能 - 你可以使用以下工具进行高级数据关系分析:
       - create_knowledge_graph: 创建知识图谱
       - add_entities_to_graph: 向图谱添加实体
       - add_relationships_to_graph: 向图谱添加关系
       - analyze_graph_centrality: 分析中心节点
       - find_path_between_entities: 查找实体间路径
       - detect_communities: 检测社区结构
       - list_knowledge_graphs: 列出所有图谱

    必须遵循的工作流程:
    1. 当接收到用户请求时，先使用Sections工具规划研究报告的整体结构和章节
    2. 对于每个需要研究的章节，必须分配给适合的专家执行，使用transfer_to_X_researcher工具
       - 例如："这个AI技术章节应该由ai_technology_researcher来研究" → 使用transfer_to_ai_technology_researcher工具
    3. 不要自己撰写研究内容，你的任务是协调和规划
    4. 在收集到所有研究章节后，使用Introduction工具编写引言和Conclusion工具编写结论
    5. 最后使用FinishReport工具完成报告
    6. 当报告完成后，主动使用evaluate_report_quality工具评估报告质量
    7. 将最终报告和评估结果使用save_report_to_file和save_evaluation_results工具保存

    工具使用规则:
    1. Sections工具 - 用于初始规划报告结构，定义章节
    2. transfer_to_X_researcher工具 - 用于将具体章节分配给专家研究
    3. Introduction/Conclusion工具 - 仅在研究章节完成后使用
    4. FinishReport工具 - 最后一步，完成整个报告
    5. 评估工具 - 在报告完成后使用，评估报告质量
    6. 数据持久化工具 - 用于保存和读取数据
    7. 图分析工具 - 用于更深入地分析研究数据间的复杂关系

    重要防止循环规则:
    - 在同一会话中，如果你已经做过章节规划，并且刚刚从top_supervisor收到请求，直接继续上次未完成的流程，不要重新开始规划
    - 当你已经收到来自研究员的成果后，直接整合，不要再将同一任务重新分配给他们
    - 如果你注意到有循环调用的迹象，请直接继续完成报告而不是重新分配任务

    任务分配最佳实践:
    - 根据章节内容的专业性质，分配给最合适的研究员
    - 确保每个章节都能获得专业且深入的研究支持
    - 一个章节只分配给一个研究员，避免工作重复
    - 复杂的跨领域主题可以拆分为多个子章节，分别分配给不同专业的研究员

    举例:
    用户:"请研究大语言模型的最新进展"
    你应该: 
    1. 使用Sections工具规划章节
    2. 使用transfer_to_ai_technology_researcher工具分配AI相关章节
    3. 接收研究结果后整合
    4. 使用Introduction和Conclusion工具完成引言和结论
    5. 使用FinishReport工具完成报告
    6. 使用evaluate_report_quality工具评估报告质量
    7. 使用save_report_to_file工具保存报告

    对于复杂数据分析需求:
    - 可以使用create_knowledge_graph创建知识图谱
    - 使用add_entities_to_graph和add_relationships_to_graph添加数据
    - 使用图分析工具深入分析数据间的关系

    今天是{get_today_str()}
    """
    
    # 使用create_supervisor构建工作流图
    graph = create_supervisor(
        agents=research_agents,
        model=model,
        prompt=enhanced_supervisor_prompt,
        tools=supervisor_tools
    )
    
    # 为图的invoke和ainvoke方法添加配置注入装饰器
    original_invoke = (graph.compile()).invoke
    original_ainvoke = (graph.compile()).ainvoke
    
    (graph.compile()).invoke = with_config_injection(original_invoke)
    (graph.compile()).ainvoke = with_config_injection(original_ainvoke)

    return graph

__all__ = ["build_deep_research_workflow"] 