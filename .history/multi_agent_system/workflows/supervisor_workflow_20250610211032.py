from langgraph_supervisor.supervisor import create_supervisor,create_top_level_supervisor
from langgraph.graph import StateGraph, START, END
from langgraph.state import get_messages
from langchain_core.messages import AIMessage
import re


def build_supervisor_workflow(agents, model):
    """构建监督者工作流"""
    return create_supervisor(
        agents=agents,
        model=model,
        prompt="你是一个团队监督者，管理研究与写作专家，数学专家和天气专家。对于代数问题，使用algebra_expert；对于微积分问题，使用calculus_expert。",
    )

# 添加一个消息拦截器函数，用于拦截监督者输出并添加工具调用
def message_interceptor(state):
    """拦截最后一条消息，检查是否包含工具调用描述，如果包含则添加工具调用"""
    messages = get_messages(state)
    if not messages or len(messages) == 0:
        return state
    
    last_message = messages[-1]
    if last_message.type != "ai" or last_message.name != "top_supervisor":
        return state
    
    # 检查是否包含工具调用描述
    content = last_message.content
    if not content:
        return state
    
    # 使用正则表达式寻找工具调用描述
    transfer_match = re.search(r"调用(?:工具)?\s*(transfer_to_(\w+)(?:_team)?)\s*(?:工具)?", content)
    if transfer_match:
        tool_name = transfer_match.group(1)
        # 设置工具调用
        tool_calls = [
            {
                'id': f'intercept_call_{0}',
                'name': tool_name,
                'args': {},
                'type': 'function'
            }
        ]
        
        # 使用这些信息创建一个新的带工具调用的消息
        updated_message = AIMessage(
            content="",  # 清空内容，让工具调用更明显
            name=last_message.name,
            tool_calls=tool_calls  # 添加工具调用
        )
        
        # 替换最后一条消息
        messages[-1] = updated_message
        
        # 更新状态
        return {"messages": messages}
    
    return state

def build_top_level_supervisor(middle_supervisors, model):
    """
    构建顶层监督者，接受 (state_graph, name) 元组列表
    
    Args:
        middle_supervisors_with_names: [(state_graph, name), ...]
        model: 语言模型
    """    
    
    # 添加增强的提示词，使顶层监督者更好地识别如何分配任务并防止递归
    top_supervisor_prompt = """
    你是一个高级团队协调者，负责管理多个专业团队。你需要根据用户查询的内容，决定将任务分配给哪个团队处理。

    你可以管理的团队如下：

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
    
    【工作流程】
    1. 仔细分析用户的查询意图和关键词
    2. 判断哪个团队最适合处理该查询
    3. 使用相应的工具将任务交给对应团队处理
    
    【重要规则】
    1. 如果刚从某个团队收到回传的结果，不要再次将任务发送回同一个团队！
    2. 当收到deep_research_team的回传结果时，不要再次将同一查询发送回deep_research_team
    3. 确保每个查询只分配给最合适的一个团队处理
    4. 任务转交后，等待该团队完全处理后再进行下一步决策
    
    【调用团队的方式】
    - 对于math_team：必须使用工具 transfer_to_math_team 
    - 对于weather_team：必须使用工具 transfer_to_weather_team
    - 对于deep_research_team：必须使用工具 transfer_to_deep_research_team
    
    【工具调用格式示例】
    假设你要将请求发送到深度研究团队，必须使用JSON格式的工具调用，如下所示:
    {"name": "transfer_to_deep_research_team", "arguments": {}}
    
    【避免重复调用】
    每个查询只应该调用一次团队。如果一个团队已经处理过查询并返回结果，你应该：
    1. 分析返回的结果是否完整回答了用户问题
    2. 如果回答完整，直接将结果呈现给用户
    3. 如果回答不完整，补充必要的信息，但不要再次调用同一团队
    4. 如果需要其他团队的专业知识，可以调用不同的团队
    
    【防止递归循环示例】
    如果用户请求"研究大语言模型的发展趋势"：
    - 你应该使用工具调用：{"name": "transfer_to_deep_research_team", "arguments": {}}
    - 当deep_research_team返回结果后，不要再次调用transfer_to_deep_research_team工具
    - 而是直接将结果返回给用户，或者进行必要的补充
    
    【成功响应示例】
    1. 用户:"求解方程x²+3x-4=0"
       你应该执行: {"name": "transfer_to_math_team", "arguments": {}}
    
    2. 用户:"北京今天的天气如何？"
       你应该执行: {"name": "transfer_to_weather_team", "arguments": {}}
    
    3. 用户:"请对量子计算进行研究分析"
       你应该执行: {"name": "transfer_to_deep_research_team", "arguments": {}}
    """
    
    # 创建顶层监督者
    supervisor_base = create_top_level_supervisor(
        middle_supervisors=[sg for sg, name in middle_supervisors],
        model=model,
        agent_names=[name for sg, name in middle_supervisors],
        prompt=top_supervisor_prompt
    )
    
    # 创建最终的状态图，添加消息拦截节点
    builder = StateGraph(supervisor_base.schema, config_schema=supervisor_base.config_schema)
    
    # 添加主监督者节点 
    supervisor_compiled = supervisor_base.compile()
    builder.add_node("main_supervisor", supervisor_compiled)
    
    # 添加消息拦截节点
    builder.add_node("interceptor", message_interceptor)
    
    # 添加其他节点：子团队supervisors
    for sg, name in middle_supervisors:
        builder.add_node(name, sg)
    
    # 添加边缘
    builder.add_edge(START, "main_supervisor")
    builder.add_edge("main_supervisor", "interceptor")
    builder.add_edge("interceptor", END)
    
    # 添加子团队到主管的边缘
    for _, name in middle_supervisors:
        builder.add_edge(name, "interceptor")
    
    return builder


__all__ = ["build_supervisor_workflow",
            "build_top_level_supervisor"]