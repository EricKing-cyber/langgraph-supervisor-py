# from typing import List, Dict, Any
# from dataclasses import dataclass
# import networkx as nx

# @dataclass
# class CommunicationLink:
#     """通信链路描述"""
#     source: str
#     target: str
#     bandwidth: float
#     protocol: str = "REST"

# @dataclass
# class CommunicationTopology:
#     """通信拓扑结构"""
#     links: List[CommunicationLink]
#     efficiency_score: float = 0.0

# class CommunicationProtocol:
#     """通信协议基类"""
#     def establish_links(self, agents: List[str], context: Dict[str, Any]) -> CommunicationTopology:
#         raise NotImplementedError()
        
# class DynamicRoutingProtocol(CommunicationProtocol):
#     """动态路由通信协议"""
#     def establish_links(self, agents: List[str], context: Dict[str, Any]) -> CommunicationTopology:
#         links = []
#         task_complexity = context.get("complexity", 0.5)
        
#         # 创建全连接拓扑
#         for i, source in enumerate(agents):
#             for j, target in enumerate(agents):
#                 if i != j:
#                     # 计算带宽需求
#                     bandwidth = max(0.3, 1 - task_complexity * 0.7)
#                     links.append(CommunicationLink(
#                         source=source,
#                         target=target,
#                         bandwidth=bandwidth,
#                         protocol="gRPC" if bandwidth > 0.6 else "REST"
#                     ))
                    
#         # 计算拓扑效率
#         efficiency_score = 1 - (task_complexity * 0.3)
        
#         return CommunicationTopology(
#             links=links,
#             efficiency_score=efficiency_score
#         )