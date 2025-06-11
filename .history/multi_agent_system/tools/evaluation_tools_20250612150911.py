"""
评估工具模块

提供对研究报告和生成内容的自动评估功能
"""

from typing import Dict, Any, List, Optional
from langchain_core.tools import tool, BaseTool
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic

from open_deep_research.tests.evals.evaluators import (
    eval_overall_quality,
    eval_relevance,
    eval_structure,
    eval_groundedness,
    eval_model,
    OverallQualityScore,
    RelevanceScore, 
    StructureScore,
    GroundednessScore
)
from open_deep_research.tests.evals.prompts import (
    RELEVANCE_PROMPT,
    STRUCTURE_PROMPT,
    GROUNDEDNESS_PROMPT,
    OVERALL_QUALITY_PROMPT
)
from open_deep_research.src.open_deep_research.utils import get_today_str


@tool
def evaluate_report_quality(report_content: str, query: str) -> Dict[str, Any]:
    """
    评估报告的整体质量，包括相关性、结构和可靠性
    
    Args:
        report_content: 报告内容
        query: 用户查询/需求
        
    Returns:
        Dict: 包含各评估指标的结果
    """
    inputs = {"messages": [{"role": "user", "content": query}]}
    outputs = {"messages": [{"role": "assistant", "content": report_content}], "context": ""}
    
    # 评估总体质量
    overall_result = eval_overall_quality(inputs, outputs)
    # 评估相关性
    relevance_result = eval_relevance(inputs, outputs)
    # 评估结构
    structure_result = eval_structure(inputs, outputs)
    
    # 汇总评估结果
    evaluation_results = {
        "overall_quality": {
            "score": overall_result["score"],
            "comment": overall_result["comment"]
        },
        "relevance": {
            "score": relevance_result["score"],
            "comment": relevance_result["comment"]
        },
        "structure": {
            "score": structure_result["score"],
            "comment": structure_result["comment"]
        },
        "average_score": (overall_result["score"] + relevance_result["score"] + structure_result["score"]) / 3
    }
    
    return evaluation_results


@tool
def evaluate_groundedness(report_content: str, context: str) -> Dict[str, Any]:
    """
    评估报告内容的可靠性（是否基于事实和提供的上下文）
    
    Args:
        report_content: 报告内容
        context: 用于评估可靠性的上下文信息（例如搜索结果）
        
    Returns:
        Dict: 包含可靠性评估结果
    """
    outputs = {"messages": [{"role": "assistant", "content": report_content}], "context": context}
    
    # 评估可靠性
    groundedness_result = eval_groundedness({}, outputs)
    
    return {
        "groundedness": {
            "score": groundedness_result["score"],
            "comment": groundedness_result["comment"]
        }
    }


@tool
def get_evaluation_criteria() -> Dict[str, str]:
    """
    获取评估标准的详细说明
    
    Returns:
        Dict: 包含各评估指标的详细标准说明
    """
    today_str = get_today_str()
    
    return {
        "overall_quality": OVERALL_QUALITY_PROMPT.format(today=today_str),
        "relevance": RELEVANCE_PROMPT.format(today=today_str),
        "structure": STRUCTURE_PROMPT.format(today=today_str),
        "groundedness": GROUNDEDNESS_PROMPT
    }


@tool
def get_evaluation_summary(evaluation_results: Dict[str, Any]) -> str:
    """
    根据评估结果生成总结
    
    Args:
        evaluation_results: 包含评估结果的字典
        
    Returns:
        str: 评估总结
    """
    model = eval_model
    
    summary_prompt = f"""
    请根据以下评估结果，生成简洁的评估总结报告，重点突出优势和改进空间:

    总体质量评分: {evaluation_results.get('overall_quality', {}).get('score', 'N/A')}
    总体质量评论: {evaluation_results.get('overall_quality', {}).get('comment', 'N/A')}
    
    相关性评分: {evaluation_results.get('relevance', {}).get('score', 'N/A')}
    相关性评论: {evaluation_results.get('relevance', {}).get('comment', 'N/A')}
    
    结构评分: {evaluation_results.get('structure', {}).get('score', 'N/A')}
    结构评论: {evaluation_results.get('structure', {}).get('comment', 'N/A')}
    
    可靠性评分: {evaluation_results.get('groundedness', {}).get('score', 'N/A') if 'groundedness' in evaluation_results else 'N/A'}
    可靠性评论: {evaluation_results.get('groundedness', {}).get('comment', 'N/A') if 'groundedness' in evaluation_results else 'N/A'}
    
    平均评分: {evaluation_results.get('average_score', 'N/A')}
    
    请提供:
    1. 总体评价（1-2句）
    2. 主要优势（2-3点）
    3. 改进空间（2-3点）
    4. 具体建议（1-2点）
    """
    
    result = model.invoke([HumanMessage(content=summary_prompt)])
    return result.content

# 获取所有评估工具
def get_evaluation_tools() -> List[BaseTool]:
    """
    获取所有评估工具
    
    Returns:
        List[BaseTool]: 评估工具列表
    """
    return [
        tool(evaluate_report_quality),
        tool(evaluate_groundedness),
        tool(get_evaluation_criteria),
        tool(get_evaluation_summary)
    ] 