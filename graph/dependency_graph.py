import networkx as nx
from graph.graph_schema import NodeType, EdgeType
from graph.architecture_inference import infer_architectural_layers # <-- NOVO IMPORT

class SystemGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._cached_risk = None

    def apply_architectural_layers(self): # <-- NOVO MÉTODO
        """Aplica a inferência de camadas zero-config ao grafo atual."""
        if len(self.graph.nodes) > 0:
            infer_architectural_layers(self.graph)

    def clear_graph(self):
        self.graph.clear()
        self._cached_risk = None

    def add_node(self, node_id: str, node_type: NodeType, **kwargs):
        self.graph.add_node(node_id, type=node_type, **kwargs)

    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType, **kwargs):
        self.graph.add_edge(source_id, target_id, relation=edge_type, **kwargs)

    def remove_subgraph(self, node_id: str):
        if not self.graph.has_node(node_id):
            return
        nodes_to_remove = set([node_id])
        queue = [node_id]
        while queue:
            current = queue.pop(0)
            for successor in self.graph.successors(current):
                edge_data = self.graph.get_edge_data(current, successor)
                if edge_data and edge_data.get('relation') == EdgeType.CONTAINS:
                    if successor not in nodes_to_remove:
                        nodes_to_remove.add(successor)
                        queue.append(successor)
        self.graph.remove_nodes_from(nodes_to_remove)
        self._cached_risk = None

    def get_subgraph_context(self, node_id: str, depth: int = 1) -> dict:
        if not self.graph.has_node(node_id):
            return {"node": node_id, "callers_and_dependencies": []}
        neighbors = set()
        current_layer = set([node_id])
        for _ in range(depth):
            next_layer = set()
            for n in current_layer:
                next_layer.update(self.graph.predecessors(n))
                next_layer.update(self.graph.successors(n))
            neighbors.update(next_layer)
            current_layer = next_layer
        if node_id in neighbors:
            neighbors.remove(node_id)
        return {"node": node_id, "callers_and_dependencies": list(neighbors)}

    def calculate_architectural_risk(self, force_recalculate: bool = False) -> list:
        if not force_recalculate and self._cached_risk is not None:
            return self._cached_risk
        if len(self.graph.nodes) == 0:
            return []
        in_degree_centrality = nx.in_degree_centrality(self.graph)
        k_val = min(50, len(self.graph.nodes))
        betweenness_centrality = nx.betweenness_centrality(self.graph, k=k_val) if k_val > 0 else {}
        risk_scores = []
        for node, data in self.graph.nodes(data=True):
            node_type = data.get("type")
            if node_type in [NodeType.TEST, NodeType.EXTERNAL_LIBRARY, NodeType.EXTERNAL_SERVICE]:
                continue
            complexity = data.get("complexity", 0.1)
            fan_in = in_degree_centrality.get(node, 0)
            bottleneck = betweenness_centrality.get(node, 0)
            risk_score = ((0.5 * fan_in) + (0.3 * bottleneck) + (0.2 * complexity)) * 100
            if risk_score > 0:
                risk_scores.append({
                    "component": node,
                    "type": node_type.value if hasattr(node_type, 'value') else str(node_type),
                    "risk_score": round(risk_score, 4),
                    "metrics": {"fan_in": round(fan_in, 4), "bottleneck": round(bottleneck, 4), "complexity": round(complexity, 4)}
                })
        self._cached_risk = sorted(risk_scores, key=lambda x: x["risk_score"], reverse=True)
        return self._cached_risk