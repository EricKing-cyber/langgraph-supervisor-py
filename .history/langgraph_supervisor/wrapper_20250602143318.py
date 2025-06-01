from langgraph.graph import StateGraph

class NamedStateGraph:
    def __init__(self, graph: StateGraph, name: str):
        self.graph = graph
        self.name = name

    def __getattr__(self, item):
        return getattr(self.graph, item)