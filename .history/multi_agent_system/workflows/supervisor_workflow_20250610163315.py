from langgraph_supervisor.supervisor import create_supervisor,create_top_level_supervisor


def build_supervisor_workflow(agents, model):
    """构建监督者工作流"""
    return create_supervisor(
        agents=agents,
        model=model,
        prompt="你是一个团队监督者，管理研究与写作专家，数学专家和天气专家。对于代数问题，使用algebra_expert；对于微积分问题，使用calculus_expert。",
    )

def build_top_level_supervisor(middle_supervisors, model):
    """
    构建顶层监督者，接受 (state_graph, name) 元组列表
    
    Args:
        middle_supervisors_with_names: [(state_graph, name), ...]
        model: 语言模型
    """    
    
    # 添加增强的提示词，使顶层监督者更好地识别如何分配任务
    top_supervisor_prompt = """
    你是一个高级团队协调者，负责管理多个专业团队。你需要根据用户查询的内容，决定将任务分配给哪个团队处理。你可以管理的团队如下：

    1. math_team（数学团队）: 
       - 处理代数问题、微积分问题等各种数学计算和推理
       - 适用场景：方程求解、积分、导数、概率统计等数学问题
       - 关键词识别：计算、解方程、求导、积分、概率、统计等
    
    2. weather_team（天气团队）:
       - 处理天气预报、气候分析等与天气相关的查询
       - 适用场景：询问天气状况、气温、降水、气候变化等
       - 关键词识别：天气、温度、降雨、气候、台风、暴雨等
    
    3. deep_research_team（深度研究团队）:
       - 处理需要深入调研、收集资料和分析的复杂问题
       - 可进行网络搜索、数据分析、报告撰写，包含以下专家:
         * ai_technology_researcher: AI技术研究专家
         * finance_researcher: 金融领域研究专家
         * science_researcher: 科学领域研究专家
       - 适用场景：深度调研报告、趋势分析、行业研究、科技前沿探索
       - 关键词识别：研究、调查、分析报告、深入了解、最新进展、综合分析等
    
    当收到用户查询时:
    1. 仔细分析用户的查询意图和关键词
    2. 判断哪个团队最适合处理该查询
    3. 将任务交给相应的团队处理
    4. 如果是复杂问题需要深入调研，一定要选择deep_research_team
    
    示例:
    - "求解方程x²+3x-4=0" → math_team
    - "北京今天的天气如何？" → weather_team
    - "请对量子计算的最新进展进行调研分析" → deep_research_team
    - "帮我研究一下电动汽车行业的未来发展趋势" → deep_research_team
    """
    
    return create_top_level_supervisor(
        middle_supervisors=[sg for sg, name in middle_supervisors],
        model=model,
        agent_names=[name for sg, name in middle_supervisors],   # 生成器表达式（generator expression）
        prompt=top_supervisor_prompt
    )



__all__ = ["build_supervisor_workflow",
            "build_top_level_supervisor"]