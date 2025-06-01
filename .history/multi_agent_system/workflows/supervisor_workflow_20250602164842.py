from langgraph_supervisor.supervisor import create_supervisor,create_top_level_supervisor


def build_supervisor_workflow(agents, model):
    """构建监督者工作流"""
    return create_supervisor(
        agents=agents,
        model=model,
        prompt="你是一个团队监督者，管理数学专家和天气专家。对于代数问题，使用algebra_expert；对于微积分问题，使用calculus_expert。",
    )

def build_top_level_supervisor(middle_supervisors, model):
    """
    构建顶层监督者，接受 (state_graph, name) 元组列表
    
    Args:
        middle_supervisors_with_names: [(state_graph, name), ...]
        model: 语言模型
    """    
    
    return create_top_level_supervisor(
        middle_supervisors=[sg for sg, name in middle_supervisors],
        model=model,
        agent_names=[name for sg, name in middle_supervisors]   # 生成器表达式（generator expression）
    )



__all__ = ["build_supervisor_workflow",
            "build_top_level_supervisor"]