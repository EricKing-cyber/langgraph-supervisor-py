from langgraph.pregel import Pregel

class NamedPregel:
    def __init__(self, pregel: Pregel, name: str):
        self.pregel = pregel
        self.name = name

    def __getattr__(self, item):
        return getattr(self.pregel, item)