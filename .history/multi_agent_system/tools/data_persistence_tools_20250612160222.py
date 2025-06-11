"""
数据持久化工具模块

提供文件读写、数据缓存等持久化功能
"""

import os
import json
import time
import pickle
import hashlib
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime
from functools import wraps
from langchain_core.tools import tool, BaseTool

# 定义数据存储路径
DATA_DIR = Path("data")
CACHE_DIR = DATA_DIR / "cache"
REPORTS_DIR = DATA_DIR / "reports"
EVAL_RESULTS_DIR = DATA_DIR / "evaluations"

# 确保目录存在
for directory in [DATA_DIR, CACHE_DIR, REPORTS_DIR, EVAL_RESULTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 定义原始函数，之后用装饰器转换为工具
def _save_report_to_file(report_content: str, topic: str, format: str = "md") -> str:
    """
    将研究报告保存到文件
    
    Args:
        report_content: 报告内容
        topic: 报告主题
        format: 文件格式，默认为md(markdown)
        
    Returns:
        str: 保存的文件路径
    """
    # 清理文件名
    topic_clean = "".join(c if c.isalnum() else "_" for c in topic)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{topic_clean}_{timestamp}.{format}"
    filepath = REPORTS_DIR / filename
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return str(filepath)


def _read_report_from_file(filepath: str) -> str:
    """
    从文件读取研究报告
    
    Args:
        filepath: 文件路径
        
    Returns:
        str: 报告内容
    """
    path = Path(filepath)
    if not path.exists():
        return f"错误：文件 {filepath} 不存在"
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content


def _save_evaluation_results(evaluation_results: Dict[str, Any], report_id: str) -> str:
    """
    保存评估结果
    
    Args:
        evaluation_results: 评估结果字典
        report_id: 报告ID或标识符
        
    Returns:
        str: 保存的文件路径
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"eval_{report_id}_{timestamp}.json"
    filepath = EVAL_RESULTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(evaluation_results, f, ensure_ascii=False, indent=2)
    
    return str(filepath)


def _cache_data(data: Any, key: Optional[str] = None, ttl: int = 3600) -> str:
    """
    将数据缓存到文件系统
    
    Args:
        data: 要缓存的数据
        key: 缓存键(可选)，如不提供会自动生成
        ttl: 缓存有效期(秒)，默认1小时
        
    Returns:
        str: 缓存键
    """
    # 如果没有提供key，生成一个基于数据内容的哈希值
    if not key:
        data_str = str(data)
        key = hashlib.md5(data_str.encode()).hexdigest()
    
    # 创建缓存对象
    cache_obj = {
        "data": data,
        "timestamp": time.time(),
        "expires_at": time.time() + ttl
    }
    
    # 保存到文件
    filepath = CACHE_DIR / f"{key}.pickle"
    with open(filepath, 'wb') as f:
        pickle.dump(cache_obj, f)
    
    return key


def _get_cached_data(key: str) -> Union[Any, str]:
    """
    获取缓存数据
    
    Args:
        key: 缓存键
        
    Returns:
        Any: 缓存数据，如果缓存不存在或已过期则返回错误信息
    """
    filepath = CACHE_DIR / f"{key}.pickle"
    
    if not filepath.exists():
        return f"错误：缓存键 {key} 不存在"
    
    try:
        with open(filepath, 'rb') as f:
            cache_obj = pickle.load(f)
        
        # 检查是否过期
        if time.time() > cache_obj["expires_at"]:
            return f"错误：缓存键 {key} 已过期"
        
        return cache_obj["data"]
    except Exception as e:
        return f"错误：读取缓存数据失败 - {str(e)}"


def _list_saved_reports() -> List[Dict[str, str]]:
    """
    列出所有保存的报告
    
    Returns:
        List[Dict[str, str]]: 报告文件列表，包含文件名和创建时间
    """
    reports = []
    
    for file_path in REPORTS_DIR.glob("*.*"):
        if file_path.is_file():
            # 从文件名中提取时间戳
            parts = file_path.stem.split("_")
            if len(parts) >= 2:
                timestamp_str = parts[-2] + "_" + parts[-1]
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    created_at = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    created_at = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            else:
                created_at = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            reports.append({
                "filename": file_path.name,
                "path": str(file_path),
                "created_at": created_at,
                "size_bytes": file_path.stat().st_size
            })
    
    # 按创建时间倒序排序
    reports.sort(key=lambda x: x["created_at"], reverse=True)
    return reports


def _list_evaluation_results() -> List[Dict[str, str]]:
    """
    列出所有保存的评估结果
    
    Returns:
        List[Dict[str, str]]: 评估结果文件列表
    """
    results = []
    
    for file_path in EVAL_RESULTS_DIR.glob("*.json"):
        if file_path.is_file():
            # 尝试读取评估结果
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                avg_score = data.get('average_score', 'N/A')
            except:
                avg_score = 'N/A'
            
            results.append({
                "filename": file_path.name,
                "path": str(file_path),
                "created_at": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "average_score": avg_score
            })
    
    # 按创建时间倒序排序
    results.sort(key=lambda x: x["created_at"], reverse=True)
    return results


# 定义工具包装器，允许直接调用
def tool_wrapper(func):
    original_func = func  # 保存原始函数引用

    @tool
    @wraps(original_func)
    def wrapped_func(*args, **kwargs):
        try:
            return original_func(*args, **kwargs)
        except Exception as e:
            return f"错误：函数执行失败 - {str(e)}"
    
    # 将原始函数直接挂在包装函数上，方便直接访问
    wrapped_func._original = original_func
    
    # 返回包装后的函数
    return wrapped_func


# 使用包装器包装函数
save_report_to_file = tool_wrapper(_save_report_to_file)
read_report_from_file = tool_wrapper(_read_report_from_file)
save_evaluation_results = tool_wrapper(_save_evaluation_results)
cache_data = tool_wrapper(_cache_data)
get_cached_data = tool_wrapper(_get_cached_data)
list_saved_reports = tool_wrapper(_list_saved_reports)
list_evaluation_results = tool_wrapper(_list_evaluation_results)


# 获取所有数据持久化工具
def get_persistence_tools() -> List[BaseTool]:
    """
    获取所有数据持久化工具
    
    Returns:
        List[BaseTool]: 持久化工具列表
    """
    return [
        save_report_to_file,
        read_report_from_file,
        save_evaluation_results,
        cache_data,
        get_cached_data,
        list_saved_reports,
        list_evaluation_results
    ] 