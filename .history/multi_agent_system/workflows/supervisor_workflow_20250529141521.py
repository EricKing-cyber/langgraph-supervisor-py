# 创建 workflows/supervisor_workflow.py
workflows_dir = os.path.join(os.path.dirname(__file__), 'workflows')
os.makedirs(workflows_dir, exist_ok=True)

supervisor_content = '''from langgraph_supervisor import create_supervisor

def build_supervisor_workflow(agents, model):
    """构建监督者工作流"""
    return create_supervisor(
        agents=agents,
        model=model,
        prompt="你是一个团队监督者，管理数学专家和天气专家。对于数学问题，使用math_expert；对于天气问题，使用weather_expert。"
    )
'''

with open(os.path.join(workflows_dir, 'supervisor_workflow.py'), 'w', encoding='utf-8') as f:
    f.write(supervisor_content)