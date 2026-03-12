import networkx as nx

# Quanto maior o número, mais externa é a camada (O fluxo deve ser sempre de Maior para Menor)
LAYER_ORDER = {
    "controller": 3,
    "service": 2,
    "domain": 1,
    "infra": 0,
    "unknown": -1
}

def infer_architectural_layers(graph: nx.DiGraph):
    """Zero-Config Architecture Discovery: Infere as camadas de cada nó automaticamente."""
    layers = {}

    for node in graph.nodes():
        node_name = str(node).lower()

        # 1. Naming Heuristics
        if any(w in node_name for w in ["controller", "route", "api", "handler", "view"]):
            layers[node] = "controller"
            continue
        if any(w in node_name for w in ["service", "manager", "usecase", "use_case"]):
            layers[node] = "service"
            continue
        if any(w in node_name for w in ["model", "entity", "domain", "schema"]):
            layers[node] = "domain"
            continue
        if any(w in node_name for w in ["repository", "adapter", "client", "db", "database", "util", "config"]):
            layers[node] = "infra"
            continue

        # 2. Topological Fallback (Matemática do Grafo)
        in_deg = graph.in_degree(node)
        out_deg = graph.out_degree(node)
        score = out_deg - in_deg

        if score > 3:
            layers[node] = "controller"
        elif score > 0:
            layers[node] = "service"
        elif score > -3:
            layers[node] = "domain"
        else:
            layers[node] = "infra"

    # Salva a inferência diretamente nos nós do NetworkX
    nx.set_node_attributes(graph, layers, "layer")
    return layers