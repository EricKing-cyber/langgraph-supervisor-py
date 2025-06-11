"""
评估工具模块

提供文档质量、可靠性等评估功能
"""

import re
import os
import json
import time
import string
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
from functools import wraps
from datetime import datetime
from langchain_core.tools import tool, BaseTool

# 尝试导入nltk
# 尝试导入 nltk，并设置本地资源路径
try:
    import nltk
    nltk.data.path.append('./nltk_data')  # 添加本地资源路径
    nltk_available = True
except ImportError:
    nltk_available = False

# 定义评估结果存储路径
EVAL_DIR = Path("data") / "evaluations"
EVAL_DIR.mkdir(parents=True, exist_ok=True)

# 简单的分词和句子切分函数，当nltk不可用时使用
def simple_tokenize(text):
    """简单的分词器"""
    return text.split()

def simple_sent_tokenize(text):
    """简单的句子切分"""
    # 按常见句子终止符切分
    sents = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sents if s.strip()]

def get_stopwords():
    """获取简单的停用词列表"""
    return {'the', 'and', 'of', 'to', 'a', 'in', 'for', 'is', 'on', 'that', 
            'by', 'this', 'with', 'are', 'be', 'as', 'an', 'it', 'at', 'from',
            'was', 'but', 'or', 'have', 'had', 'has', 'can', 'will', 'would', 'should'}

# 定义原始函数
def _evaluate_report_quality(report_content: str, criteria: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    评估研究报告的质量
    
    Args:
        report_content: 报告内容
        criteria: 评估标准列表，可选
        
    Returns:
        Dict[str, Any]: 评估结果
    """
    # 默认评估标准
    if not criteria:
        criteria = [
            "结构完整性", 
            "论证质量",
            "语言表达",
            "内容深度",
            "参考引用"
        ]
    
    # 基础文本统计
    word_count = len(simple_tokenize(report_content))
    
    # 使用nltk或简单句子切分
    if nltk_available:
        try:
            sentences = nltk.sent_tokenize(report_content)
        except:
            sentences = simple_sent_tokenize(report_content)
    else:
        sentences = simple_sent_tokenize(report_content)
        
    sentence_count = len(sentences)
    avg_sentence_length = word_count / max(sentence_count, 1)
    
    # 标题提取
    headers = [line.strip() for line in report_content.split('\n') if line.strip().startswith('#')]
    
    # 简单评估各标准
    scores = {}
    
    # 根据固定分析得分
    if "结构完整性" in criteria:
        # 根据标题和段落结构评估
        structure_quality = min(len(headers) / 5, 1.0) * 10  # 假设好的报告至少有5个标题
        scores["结构完整性"] = round(structure_quality, 1)
    
    if "语言表达" in criteria:
        # 基于句子长度和标点符号使用评估
        punctuation_ratio = sum(1 for char in report_content if char in string.punctuation) / len(report_content)
        if avg_sentence_length > 30:  # 句子太长
            language_quality = 7.0
        elif avg_sentence_length < 10:  # 句子太短
            language_quality = 7.5
        else:
            language_quality = 9.0
        
        # 标点符号使用过多或过少都不好
        if punctuation_ratio > 0.15 or punctuation_ratio < 0.05:
            language_quality -= 1.0
            
        scores["语言表达"] = round(language_quality, 1)
    
    if "内容深度" in criteria:
        # 基于内容长度、引用次数等评估
        content_depth = min(word_count / 1000, 2) * 4 + 2  # 2000字以上满分，最低2分
        # 检测引用模式 [数字] 或 (作者，年份)
        citation_matches = len(re.findall(r'\[\d+\]|\([A-Za-z]+ et al\., \d{4}\)|\([A-Za-z]+, \d{4}\)', report_content))
        if citation_matches > 5:
            content_depth = min(content_depth + 2, 10)
            
        scores["内容深度"] = round(content_depth, 1)
    
    if "参考引用" in criteria:
        # 检测是否有参考文献部分
        has_references = '参考文献' in report_content or 'References' in report_content or 'Bibliography' in report_content
        citation_count = citation_matches if 'citation_matches' in locals() else len(re.findall(r'\[\d+\]|\([A-Za-z]+ et al\., \d{4}\)|\([A-Za-z]+, \d{4}\)', report_content))
        
        if has_references and citation_count > 10:
            reference_score = 9.0
        elif has_references and citation_count > 5:
            reference_score = 8.0
        elif has_references:
            reference_score = 7.0
        elif citation_count > 0:
            reference_score = 6.0
        else:
            reference_score = 4.0
            
        scores["参考引用"] = round(reference_score, 1)
    
    if "论证质量" in criteria:
        # 判断是否包含常见推理词汇
        reasoning_terms = ['因此', '所以', '因为', '由于', '然而', '但是', '虽然', '尽管', '此外', '另外',
                          'therefore', 'thus', 'because', 'however', 'although', 'despite', 'furthermore', 'moreover']
        reasoning_count = sum(report_content.lower().count(term) for term in reasoning_terms)
        
        if reasoning_count > 15:
            reasoning_score = 9.0
        elif reasoning_count > 10:
            reasoning_score = 8.0
        elif reasoning_count > 5:
            reasoning_score = 7.0
        else:
            reasoning_score = 6.0
            
        scores["论证质量"] = round(reasoning_score, 1)
    
    # 填充其他自定义标准
    for criterion in criteria:
        if criterion not in scores:
            # 为未知标准设置默认分数
            scores[criterion] = 7.0
    
    # 计算总分
    average_score = sum(scores.values()) / len(scores)
    
    # 形成评级
    if average_score >= 9.0:
        rating = "优秀"
    elif average_score >= 8.0:
        rating = "良好"
    elif average_score >= 7.0:
        rating = "中等"
    elif average_score >= 6.0:
        rating = "及格"
    else:
        rating = "不及格"
    
    # 生成改进建议
    suggestions = []
    if scores.get("结构完整性", 0) < 7:
        suggestions.append("建议改进报告结构，增加更多合理的章节划分和小标题。")
    if scores.get("参考引用", 0) < 7:
        suggestions.append("建议增加参考文献和引用次数，提高报告的可信度和学术性。")
    if scores.get("论证质量", 0) < 7:
        suggestions.append("建议加强论证逻辑，增加因果关系分析和对比论证。")
    if scores.get("内容深度", 0) < 7:
        suggestions.append("建议深入研究主题，增加分析深度和具体案例。")
    
    # 保存评估结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_id = f"eval_{timestamp}"
    result_file = EVAL_DIR / f"{result_id}.json"
    
    result = {
        "id": result_id,
        "timestamp": timestamp,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "criteria": criteria,
        "scores": scores,
        "average_score": round(average_score, 2),
        "rating": rating,
        "suggestions": suggestions
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result


def _evaluate_reliability(text: str, check_sources: bool = True) -> Dict[str, Any]:
    """
    评估文本内容的可靠性和真实性
    
    Args:
        text: 待评估的文本内容
        check_sources: 是否检查引用源，默认为True
        
    Returns:
        Dict[str, Any]: 可靠性评估结果
    """
    # 可靠性指标
    reliability_metrics = {}
    
    # 检测引用模式
    citation_pattern = r'\[\d+\]|\([A-Za-z]+ et al\., \d{4}\)|\([A-Za-z]+, \d{4}\)'
    citations = re.findall(citation_pattern, text)
    citation_count = len(citations)
    
    # 检测数字和统计数据
    stat_pattern = r'\d+(\.\d+)?%|\d+(\.\d+)? percent'
    statistics = re.findall(stat_pattern, text)
    statistics_count = len(statistics)
    
    # 检测模糊词语
    hedge_words = ['可能', '或许', '大概', '似乎', '据说', '传言', '可能性', '猜测',
                   'may', 'might', 'perhaps', 'possibly', 'allegedly', 'reportedly', 'likely', 'speculation']
    hedge_count = sum(text.lower().count(word.lower()) for word in hedge_words)
    
    # 检测确定性词语
    certainty_words = ['确定', '肯定', '必然', '一定', '绝对', '毫无疑问', 
                       'definitely', 'certainly', 'absolutely', 'undoubtedly', 'surely']
    certainty_count = sum(text.lower().count(word.lower()) for word in certainty_words)
    
    # 计算文本长度
    word_count = len(simple_tokenize(text))
    
    # 计算各指标分数
    # 引用密度（每1000字的引用次数）
    citation_density = (citation_count / max(word_count, 1)) * 1000
    reliability_metrics["引用密度"] = round(citation_density, 2)
    
    # 引用充分性得分
    if citation_density >= 5:
        citation_score = 9.0
    elif citation_density >= 3:
        citation_score = 7.5
    elif citation_density >= 1:
        citation_score = 6.0
    else:
        citation_score = 4.0
    reliability_metrics["引用得分"] = round(citation_score, 1)
    
    # 统计数据使用得分
    stats_density = (statistics_count / max(word_count, 1)) * 1000
    if stats_density >= 3:
        stats_score = 9.0
    elif stats_density >= 1.5:
        stats_score = 7.5
    elif stats_density >= 0.5:
        stats_score = 6.0
    else:
        stats_score = 5.0
    reliability_metrics["统计数据得分"] = round(stats_score, 1)
    
    # 模糊语言使用（越少越好，但不能没有）
    hedge_density = (hedge_count / max(word_count, 1)) * 1000
    if hedge_density <= 5 and hedge_density > 0:
        hedge_score = 9.0
    elif hedge_density <= 10:
        hedge_score = 7.0
    elif hedge_density <= 20:
        hedge_score = 5.0
    else:
        hedge_score = 4.0
    reliability_metrics["谨慎用语得分"] = round(hedge_score, 1)
    
    # 确定性语言（适度最好）
    certainty_density = (certainty_count / max(word_count, 1)) * 1000
    if certainty_density <= 3 and certainty_density > 0:
        certainty_score = 9.0
    elif certainty_density <= 7:
        certainty_score = 7.0
    elif certainty_density <= 15:
        certainty_score = 5.0
    else:
        certainty_score = 4.0
    reliability_metrics["确定性表达得分"] = round(certainty_score, 1)
    
    # 计算综合可靠性得分（加权平均）
    weights = {
        "引用得分": 0.4,
        "统计数据得分": 0.25,
        "谨慎用语得分": 0.2,
        "确定性表达得分": 0.15
    }
    
    reliability_score = sum(reliability_metrics[metric] * weights[metric] 
                          for metric in weights if metric in reliability_metrics)
    
    # 可靠性等级
    if reliability_score >= 8.5:
        reliability_rating = "高度可靠"
    elif reliability_score >= 7.0:
        reliability_rating = "较为可靠"
    elif reliability_score >= 5.5:
        reliability_rating = "中等可靠"
    else:
        reliability_rating = "可靠性低"
    
    # 生成改进建议
    suggestions = []
    if reliability_metrics["引用得分"] < 6.5:
        suggestions.append("建议增加对权威来源的引用，提高内容的可信度。")
    if reliability_metrics["统计数据得分"] < 6.5:
        suggestions.append("建议适当增加数据和统计信息，使论述更具说服力。")
    if reliability_metrics["谨慎用语得分"] < 6.5:
        suggestions.append("注意减少模糊不确定的表达，增加内容的准确性。")
    if reliability_metrics["确定性表达得分"] < 6.5:
        suggestions.append("避免过度使用绝对化表达，保持适度的学术谨慎。")
    
    # 整理结果
    result = {
        "reliability_score": round(reliability_score, 2),
        "reliability_rating": reliability_rating,
        "metrics": reliability_metrics,
        "word_count": word_count,
        "citation_count": citation_count,
        "statistics_count": statistics_count,
        "suggestions": suggestions
    }
    
    # 如果开启了源检查（实际中可能需要更复杂的实现）
    if check_sources and citation_count > 0:
        # 这里简化处理，实际应用中应该验证引用源
        result["source_check"] = {
            "verified_citations": 0,
            "message": "源验证功能需要外部数据库支持，当前为简化实现"
        }
    
    return result


def _evaluate_content_relevance(content: str, topic: str, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    评估内容与主题的相关性
    
    Args:
        content: 待评估的内容
        topic: 主题
        keywords: 关键词列表（可选）
        
    Returns:
        Dict[str, Any]: 相关性评估结果
    """
    # 如果没有提供关键词，尝试从主题生成关键词
    if not keywords:
        # 简单分词
        words = re.findall(r'\w+', topic.lower())
        # 过滤停用词
        try:
            if nltk_available:
                from nltk.corpus import stopwords
                stop_words = set(stopwords.words('english'))
            else:
                stop_words = get_stopwords()
            keywords = [word for word in words if word not in stop_words and len(word) > 2]
        except:
            # 如果nltk停用词加载失败，使用简单逻辑
            stop_words = get_stopwords()
            keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # 计算关键词出现频率
    keyword_counts = {}
    normalized_content = content.lower()
    
    for keyword in keywords:
        count = normalized_content.count(keyword.lower())
        keyword_counts[keyword] = count
    
    # 计算总字数
    word_count = len(simple_tokenize(content))
    
    # 计算关键词密度
    total_keyword_count = sum(keyword_counts.values())
    keyword_density = (total_keyword_count / max(word_count, 1)) * 100 if word_count else 0
    
    # 主题出现频率
    topic_words = topic.lower().split()
    topic_word_counts = {}
    
    for word in topic_words:
        if len(word) > 2:  # 忽略短词
            count = normalized_content.count(word)
            topic_word_counts[word] = count
    
    topic_word_frequency = sum(topic_word_counts.values())
    
    # 主题相关段落比例
    paragraphs = content.split('\n\n')
    relevant_paragraphs = 0
    
    for para in paragraphs:
        # 检查段落是否包含关键词或主题词
        is_relevant = False
        for keyword in keywords:
            if keyword.lower() in para.lower():
                is_relevant = True
                break
        if not is_relevant:
            for word in topic_words:
                if len(word) > 2 and word.lower() in para.lower():
                    is_relevant = True
                    break
        
        if is_relevant:
            relevant_paragraphs += 1
    
    relevant_paragraph_ratio = relevant_paragraphs / max(len(paragraphs), 1) if paragraphs else 0
    
    # 计算主题相关性得分
    # 关键词密度得分 (理想范围 2-5%)
    if 2 <= keyword_density <= 5:
        density_score = 9.5
    elif keyword_density < 2:
        density_score = 7 + (keyword_density / 2) * 2.5  # 线性增长到9.5
    else:  # > 5%
        density_score = 9.5 - (keyword_density - 5) * 0.5  # 缓慢降低
        density_score = max(density_score, 6)  # 不低于6分
    
    # 段落相关性得分
    paragraph_score = relevant_paragraph_ratio * 10
    
    # 综合得分（加权平均）
    relevance_score = density_score * 0.6 + paragraph_score * 0.4
    
    # 相关性等级
    if relevance_score >= 8.5:
        relevance_rating = "高度相关"
    elif relevance_score >= 7.0:
        relevance_rating = "较为相关"
    elif relevance_score >= 5.5:
        relevance_rating = "部分相关"
    else:
        relevance_rating = "相关性低"
    
    # 生成改进建议
    suggestions = []
    if density_score < 7:
        suggestions.append("建议增加关键词和主题相关词汇的使用频率。")
    if density_score > 9 and keyword_density > 6:
        suggestions.append("关键词使用频率过高，建议适当减少以避免关键词堆砌。")
    if paragraph_score < 7:
        suggestions.append("内容中与主题无关的段落较多，建议增强内容与主题的关联性。")
    
    # 返回结果
    result = {
        "relevance_score": round(relevance_score, 2),
        "relevance_rating": relevance_rating,
        "keyword_density": round(keyword_density, 2),
        "relevant_paragraph_ratio": round(relevant_paragraph_ratio, 2),
        "keyword_counts": keyword_counts,
        "topic_word_counts": topic_word_counts,
        "suggestions": suggestions
    }
    
    return result


def _evaluate_coherence(text: str) -> Dict[str, Any]:
    """
    评估文本的连贯性和逻辑一致性
    
    Args:
        text: 待评估的文本
        
    Returns:
        Dict[str, Any]: 连贯性评估结果
    """
    # 分割为段落
    paragraphs = [p for p in text.split('\n\n') if p.strip()]
    
    # 分割为句子
    if nltk_available:
        try:
            sentences = nltk.sent_tokenize(text)
        except:
            sentences = simple_sent_tokenize(text)
    else:
        sentences = simple_sent_tokenize(text)
    
    # 句子连接词/短语
    transition_words = [
        '因此', '所以', '然而', '但是', '此外', '另外', '同样', '相反', '例如', '总之',
        'therefore', 'thus', 'however', 'but', 'furthermore', 'moreover', 'similarly',
        'in contrast', 'for example', 'in conclusion'
    ]
    
    # 检查过渡词使用
    transition_count = 0
    for sentence in sentences:
        s_lower = sentence.lower()
        for word in transition_words:
            if word.lower() in s_lower:
                transition_count += 1
                break
    
    # 计算过渡词密度
    transition_density = transition_count / max(len(sentences), 1)
    
    # 段落间连贯性（简化评估）
    paragraph_coherence_issues = 0
    para_transition_words = ['首先', '其次', '再次', '最后', '总结', '总之',
                          'first', 'second', 'third', 'finally', 'in summary', 'to conclude']
    
    for i, para in enumerate(paragraphs[1:], 1):
        # 检查段落开头是否有过渡词
        has_transition = False
        para_lower = para.lower()
        
        # 检查段落是否以过渡词开始
        for word in para_transition_words:
            if para_lower.strip().startswith(word.lower()):
                has_transition = True
                break
                
        # 如果没有过渡词，可能存在连贯性问题
        if not has_transition:
            paragraph_coherence_issues += 1
    
    paragraph_coherence_score = 1 - (paragraph_coherence_issues / max(len(paragraphs) - 1, 1))
    paragraph_coherence_score = max(min(paragraph_coherence_score, 1), 0)  # 限制在0-1范围
    
    # 句子长度变化（句子长度适中且变化适度表示更好的连贯性）
    sentence_lengths = [len(simple_tokenize(s)) for s in sentences]
    avg_sentence_length = sum(sentence_lengths) / max(len(sentence_lengths), 1)
    
    # 计算句子长度的标准差
    if len(sentence_lengths) > 1:
        mean_len = avg_sentence_length
        variance = sum((x - mean_len) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        std_dev = variance ** 0.5
        # 归一化标准差
        normalized_std_dev = min(std_dev / mean_len, 1)
    else:
        normalized_std_dev = 0
    
    # 理想的句子长度变化（标准差应在一定范围内）
    if 0.3 <= normalized_std_dev <= 0.7:
        sentence_variety_score = 0.9
    elif normalized_std_dev < 0.3:
        # 变化太小
        sentence_variety_score = 0.6 + normalized_std_dev
    else:  # > 0.7
        # 变化太大
        sentence_variety_score = 1.6 - normalized_std_dev
        
    sentence_variety_score = max(min(sentence_variety_score, 1), 0)  # 限制在0-1范围
    
    # 理想的句子长度（15-25词为佳）
    if 15 <= avg_sentence_length <= 25:
        sentence_length_score = 1.0
    elif avg_sentence_length < 15:
        # 句子偏短
        sentence_length_score = 0.5 + (avg_sentence_length / 30)
    else:  # > 25
        # 句子偏长
        sentence_length_score = 1.5 - (avg_sentence_length / 50)
        
    sentence_length_score = max(min(sentence_length_score, 1), 0)  # 限制在0-1范围
    
    # 整体连贯性得分（加权组合）
    weights = {
        "transition_density": 0.3,
        "paragraph_coherence": 0.3,
        "sentence_variety": 0.2,
        "sentence_length": 0.2
    }
    
    coherence_score = (
        transition_density * weights["transition_density"] * 10 +
        paragraph_coherence_score * weights["paragraph_coherence"] * 10 +
        sentence_variety_score * weights["sentence_variety"] * 10 +
        sentence_length_score * weights["sentence_length"] * 10
    )
    
    # 连贯性等级
    if coherence_score >= 8.5:
        coherence_rating = "高度连贯"
    elif coherence_score >= 7.0:
        coherence_rating = "良好连贯"
    elif coherence_score >= 5.5:
        coherence_rating = "一般连贯"
    else:
        coherence_rating = "连贯性差"
    
    # 生成建议
    suggestions = []
    if transition_density < 0.3:
        suggestions.append("建议增加过渡词和连接词的使用，增强句子间的逻辑连接。")
    
    if paragraph_coherence_score < 0.7:
        suggestions.append("段落间缺少明确的过渡表达，建议增加段落间的连接性。")
        
    if sentence_variety_score < 0.7:
        if normalized_std_dev < 0.3:
            suggestions.append("句子长度变化不足，建议增加句式多样性。")
        else:
            suggestions.append("句子长度变化过大，建议保持更一致的句子结构。")
            
    if sentence_length_score < 0.7:
        if avg_sentence_length < 15:
            suggestions.append("句子普遍偏短，建议适当增加句子长度和复杂度。")
        else:
            suggestions.append("句子普遍偏长，建议适当缩短句子以提高可读性。")
    
    # 返回结果
    metrics = {
        "transition_density": round(transition_density, 2),
        "transition_count": transition_count,
        "paragraph_coherence": round(paragraph_coherence_score, 2),
        "sentence_variety": round(sentence_variety_score, 2),
        "sentence_length_score": round(sentence_length_score, 2),
        "avg_sentence_length": round(avg_sentence_length, 1)
    }
    
    result = {
        "coherence_score": round(coherence_score, 2),
        "coherence_rating": coherence_rating,
        "metrics": metrics,
        "suggestions": suggestions
    }
    
    return result


# 定义工具包装器，允许直接调用
def tool_wrapper(func):
    original_func = func  # 保存原始函数引用

    @tool
    @wraps(original_func)
    def wrapped_func(*args, **kwargs):
        try:
            return original_func(*args, **kwargs)
        except Exception as e:
            return f"错误：评估工具执行失败 - {str(e)}"
    
    # 将原始函数直接挂在包装函数上，方便直接访问
    wrapped_func._original = original_func
    
    # 返回包装后的函数
    return wrapped_func


# 使用包装器包装函数
evaluate_report_quality = tool_wrapper(_evaluate_report_quality)
evaluate_reliability = tool_wrapper(_evaluate_reliability)
evaluate_content_relevance = tool_wrapper(_evaluate_content_relevance)
evaluate_coherence = tool_wrapper(_evaluate_coherence)

@tool
def evaluate_groundedness(text: str, check_sources: bool = True) -> Dict[str, Any]:
    """
    评估报告内容的可靠性
    
    Args:
        text: 要评估的文本
        check_sources: 是否检查来源引用
        
    Returns:
        Dict: 可靠性评估结果
    """
    return _evaluate_reliability(text, check_sources)

@tool
def get_evaluation_criteria() -> Dict[str, str]:
    """
    获取评估标准详情
    
    Returns:
        Dict: 评估标准详情
    """
    return {
        "结构完整性": "评估报告结构是否完整，包括引言、正文和结论等必要部分，以及章节组织是否合理。",
        "论证质量": "评估报告的论证是否清晰，逻辑是否严密，论据是否充分。",
        "语言表达": "评估报告的语言是否流畅，术语使用是否准确，表达是否清晰。",
        "内容深度": "评估报告内容是否深入、全面，是否超出表面分析。",
        "参考引用": "评估报告是否有适当的引用和参考文献，以支持其论点。",
        "可靠性": "评估报告内容是否基于可靠的信息源，事实陈述是否准确。",
        "相关性": "评估报告内容是否与主题相关，是否切中要点。",
        "连贯性": "评估报告各部分是否连贯一致，过渡是否自然。"
    }

@tool
def get_evaluation_summary(evaluation_results: Dict[str, Any]) -> str:
    """
    生成评估总结
    
    Args:
        evaluation_results: 评估结果
        
    Returns:
        str: 评估总结
    """
    # 提取评分
    scores = evaluation_results.get('scores', {})
    average_score = evaluation_results.get('average_score', 0)
    rating = evaluation_results.get('rating', '未知')
    suggestions = evaluation_results.get('suggestions', [])
    
    # 生成总结
    summary = f"报告评估总结：\n\n"
    summary += f"总体评分：{average_score:.1f}/10 ({rating})\n\n"
    
    summary += "各维度评分：\n"
    for criterion, score in scores.items():
        summary += f"- {criterion}: {score}/10\n"
    
    summary += "\n改进建议：\n"
    for suggestion in suggestions:
        summary += f"- {suggestion}\n"
    
    return summary

# 获取所有评估工具
def get_evaluation_tools() -> List[BaseTool]:
    """
    获取所有评估工具
    
    Returns:
        List[BaseTool]: 评估工具列表
    """
    return [
        evaluate_report_quality,
        evaluate_reliability,
        evaluate_content_relevance,
        evaluate_coherence,
        evaluate_groundedness,
        get_evaluation_criteria,
        get_evaluation_summary
    ] 