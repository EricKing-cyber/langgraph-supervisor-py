import os
from .agent_factory  import create_agent
# 创建 core/workflow_factory.py
workflow_factory_content = '''from multi_agent_system.workflows.supervisor_workflow import build_supervisor_workflow

def create_workflow(agents, model):
    """创建完整的工作流实例"""
    workflow = build_supervisor_workflow(agents, model)
    return workflow.compile()
'''

with open(os.path.join(core_dir, 'workflow_factory.py'), 'w', encoding='utf-8') as f:
    f.write(workflow_factory_content)