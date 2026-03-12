from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import Counter, deque
from ingest.repo_loader import RepoLoader
from ingest.file_scanner import FileScanner
from parser.ast_parser import ASTParser
from parser.language_detector import LanguageDetector
from graph.dependency_graph import SystemGraph
from graph.graph_schema import NodeType, EdgeType
from ai.openai_client import CodeCognitionAI
from db.vector_store import VectorStore
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from integrations.github import github_webhook
from services.impact_service import analyze_change_impact
import os

app = FastAPI(title="Codebase Brain API - Enterprise Edition", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repo_loader = RepoLoader()
ast_parser = ASTParser()
system_graph = SystemGraph()
vector_store = VectorStore()
ai_client = CodeCognitionAI()

app.include_router(github_webhook.router)

class AnalyzeRequest(BaseModel):
    repo_url_or_path: str

class AskRequest(BaseModel):
    question: str

class ChangedFile(BaseModel):
    path: str
    changed_lines: List[int]

class DiffRequest(BaseModel):
    repo: str
    base_commit: Optional[str] = "HEAD"
    head_commit: Optional[str] = "WORKING_DIR"
    changed_files: List[ChangedFile]

@app.get("/health")
def health_check():
    return {"status": "ok", "system": "Codebase Brain Online"}

@app.get("/graph/summary")
def get_graph_summary():
    nodes_count = len(system_graph.graph.nodes)
    edges_count = len(system_graph.graph.edges)
    
    node_types = {}
    functions_without_tests = []

    for node, data in system_graph.graph.nodes(data=True):
        t = data.get("type")
        type_name = t.value if hasattr(t, 'value') else str(t)
        node_types[type_name] = node_types.get(type_name, 0) + 1

        if type_name == NodeType.FUNCTION.value:
            in_edges = system_graph.graph.in_edges(node, data=True)
            has_test = any(edge_data.get("relation") == EdgeType.TESTS.value or edge_data.get("relation") == EdgeType.TESTS for _, _, edge_data in in_edges)
            if not has_test:
                functions_without_tests.append(node)

    top_risks = system_graph.calculate_architectural_risk()

    return {
        "metrics": {
            "total_nodes": nodes_count,
            "total_edges": edges_count,
            "node_types": node_types,
            "functions_without_tests": len(functions_without_tests)
        },
        "top_10_risks": top_risks[:10]
    }

@app.get("/graph/node/{node_id:path}")
def get_node_details(node_id: str):
    if not system_graph.graph.has_node(node_id):
        raise HTTPException(status_code=404, detail="Nó não encontrado no grafo.")

    node_data = system_graph.graph.nodes[node_id]
    
    in_edges = [{"source": u, "relation": d.get("relation").value if hasattr(d.get("relation"), 'value') else d.get("relation")} for u, _, d in system_graph.graph.in_edges(node_id, data=True)]
    out_edges = [{"target": v, "relation": d.get("relation").value if hasattr(d.get("relation"), 'value') else d.get("relation")} for _, v, d in system_graph.graph.out_edges(node_id, data=True)]

    risk_ranking = system_graph.calculate_architectural_risk()
    node_risk_info = next((item for item in risk_ranking if item["component"] == node_id), None)

    return {
        "node_id": node_id,
        "type": node_data.get("type").value if hasattr(node_data.get("type"), 'value') else node_data.get("type"),
        "metrics": {
            "fan_in_count": len(in_edges),
            "fan_out_count": len(out_edges),
            "architectural_risk": node_risk_info["risk_score"] if node_risk_info else "N/A"
        },
        "incoming_relations": in_edges,
        "outgoing_relations": out_edges
    }

@app.get("/graph/impact/{node_id:path}")
def get_change_impact(node_id: str, max_depth: int = 3):
    if not system_graph.graph.has_node(node_id):
        raise HTTPException(status_code=404, detail="Nó não encontrado no grafo.")

    impacted_nodes = set()
    traversed_edges = []
    queue = deque([(node_id, 0)])

    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue

        for predecessor in system_graph.graph.predecessors(current):
            edge_data = system_graph.graph.get_edge_data(predecessor, current)
            rel = edge_data.get("relation") if edge_data else None
            rel_str = rel.value if hasattr(rel, 'value') else str(rel)
            
            traversed_edges.append({
                "source": predecessor,
                "target": current,
                "relation": rel_str
            })

            if predecessor not in impacted_nodes:
                impacted_nodes.add(predecessor)
                queue.append((predecessor, depth + 1))

    nodes_summary = {}
    for n in impacted_nodes:
        t = system_graph.graph.nodes[n].get("type")
        type_str = t.value if hasattr(t, 'value') else str(t)
        nodes_summary.setdefault(type_str, []).append(n)

    return {
        "target_node": node_id,
        "max_depth_reached": max_depth,
        "blast_radius": {
            "nodes": nodes_summary,
            "edges": traversed_edges
        }
    }

@app.get("/graph/dependencies/{node_id:path}")
def get_dependencies(node_id: str, max_depth: int = 3):
    if not system_graph.graph.has_node(node_id):
        raise HTTPException(status_code=404, detail="Nó não encontrado no grafo.")

    dependencies = set()
    traversed_edges = []
    queue = deque([(node_id, 0)])

    while queue:
        current, depth = queue.popleft()
        if depth >= max_depth:
            continue

        for successor in system_graph.graph.successors(current):
            edge_data = system_graph.graph.get_edge_data(current, successor)
            rel = edge_data.get("relation") if edge_data else None
            rel_str = rel.value if hasattr(rel, 'value') else str(rel)
            
            traversed_edges.append({
                "source": current,
                "target": successor,
                "relation": rel_str
            })

            if successor not in dependencies:
                dependencies.add(successor)
                queue.append((successor, depth + 1))

    nodes_summary = {}
    for n in dependencies:
        t = system_graph.graph.nodes[n].get("type")
        type_str = t.value if hasattr(t, 'value') else str(t)
        nodes_summary.setdefault(type_str, []).append(n)

    return {
        "target_node": node_id,
        "max_depth_reached": max_depth,
        "dependency_tree": {
            "nodes": nodes_summary,
            "edges": traversed_edges
        }
    }

@app.post("/analyze")
def analyze_repository(req: AnalyzeRequest):
    try:
        repo_path = repo_loader.clone_or_load(req.repo_url_or_path)
        files = FileScanner.scan_directory(repo_path)
        repo_name = os.path.basename(os.path.normpath(repo_path))

        system_graph.clear_graph()
        vector_store.clear_collection()
        system_graph.add_node(repo_name, NodeType.REPOSITORY)

        symbol_table = {} 
        calls_to_resolve = []
        file_imports = {} 
        symbol_origins = {} 

        processed_count = 0
        ignored_count = 0
        ignored_by_lang = {}

        print(f"\nDEBUG: Scanner encontrou {len(files)} arquivos\n")

        for file_path in files:
            lang = LanguageDetector.detect(file_path)
            
            if lang not in ["python", "javascript", "typescript", "tsx"]:
                ignored_count += 1
                ignored_by_lang[lang] = ignored_by_lang.get(lang, 0) + 1
                continue

            processed_count += 1
            rel_path = os.path.relpath(file_path, repo_path).replace("\\", "/")
            file_id = f"{repo_name}/{rel_path}"

            system_graph.add_node(file_id, NodeType.FILE)
            system_graph.add_edge(repo_name, file_id, EdgeType.CONTAINS)

            try:
                with open(file_path, "rb") as f:
                    source_code = f.read()
            except Exception:
                continue

            structure = ast_parser.extract_structure(source_code, lang)
            file_imports[file_id] = structure["imports"]
            
            symbol_origins[file_id] = {}
            for imp_data in structure["imports"]:
                for sym in imp_data["symbols"]:
                    symbol_origins[file_id][sym] = imp_data["module"]

            for func in structure["functions"] + structure["tests"]:
                func_id = f"{file_id}/{func['name']}"
                system_graph.add_node(func_id, NodeType.FUNCTION if not func['name'].startswith("test_") else NodeType.TEST)
                system_graph.add_edge(file_id, func_id, EdgeType.CONTAINS)
                system_graph.graph.nodes[func_id]["start_line"] = func.get("start_line", 0)
                system_graph.graph.nodes[func_id]["end_line"] = func.get("end_line", 0)

                text_to_embed = f"Função: {func['name']}\nCódigo:\n{func['code']}"
                embedding = ai_client.generate_embedding(text_to_embed)
                vector_store.upsert_node(
                    node_id=func_id,
                    vector=embedding,
                    payload={"node_id": func_id, "name": func['name'], "file": file_id, "code": func['code']}
                )

                raw = func["raw_name"]
                symbol_table.setdefault(raw, []).append(func_id)
                if func["name"] != raw:
                    symbol_table.setdefault(func["name"], []).append(func_id)
                
                calls_to_resolve.append({"file_id": file_id, "caller": func_id, "calls": func.get("calls", [])})

        for file_id, imports in file_imports.items():
            for imp_data in imports:
                imp = imp_data["module"]
                potential_file_py = f"{repo_name}/{imp.replace('.', '/')}.py"
                potential_dir_py = f"{repo_name}/{imp.replace('.', '/')}/__init__.py"
                potential_file_ts = f"{repo_name}/{imp.replace('.', '/')}.ts"
                potential_file_tsx = f"{repo_name}/{imp.replace('.', '/')}.tsx"
                
                target_module_id = None
                if system_graph.graph.has_node(potential_file_py):
                    target_module_id = potential_file_py
                elif system_graph.graph.has_node(potential_dir_py):
                    target_module_id = potential_dir_py
                elif system_graph.graph.has_node(potential_file_ts):
                    target_module_id = potential_file_ts
                elif system_graph.graph.has_node(potential_file_tsx):
                    target_module_id = potential_file_tsx
                
                if target_module_id:
                    system_graph.add_edge(file_id, target_module_id, EdgeType.IMPORTS)
                else:
                    lib_id = f"lib:{imp}"
                    if not system_graph.graph.has_node(lib_id):
                        system_graph.add_node(lib_id, NodeType.EXTERNAL_LIBRARY)
                    system_graph.add_edge(file_id, lib_id, EdgeType.IMPORTS)

        for item in calls_to_resolve:
            caller_id = item["caller"]
            file_id = item["file_id"]
            call_counts = Counter(item["calls"]) 

            for call_name, weight in call_counts.items():
                if call_name in symbol_table:
                    origin_module = symbol_origins[file_id].get(call_name)
                    possible_targets = symbol_table[call_name]
                    
                    if origin_module:
                        filtered_targets = [t for t in possible_targets if origin_module.replace('.', '/') in t]
                        if filtered_targets:
                            possible_targets = filtered_targets

                    for target_id in possible_targets:
                        system_graph.add_edge(caller_id, target_id, EdgeType.CALLS, weight=weight)

        print(f"\n========= SUMMARY =========")
        print(f"Files scanned: {len(files)}, Processed: {processed_count}, Ignored: {ignored_count} {ignored_by_lang}")
        print(f"===========================\n")

        return {"status": "success", "repo": repo_name, "processed_files": processed_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
def ask_codebase(req: AskRequest):
    try:
        query_vector = ai_client.generate_embedding(req.question)
        search_results = vector_store.search_similar(query_vector, limit=3)

        if not search_results:
            return {"question": req.question, "answer": "Não encontrei código relevante para responder a isso."}

        context_blocks = []
        sources = []
        for result in search_results:
            node_id = result.payload["node_id"]
            sources.append(node_id)
            
            subgraph_context = system_graph.get_subgraph_context(node_id, depth=1)
            
            context_blocks.append({
                "target_function": node_id,
                "relevance_score": result.score,
                "source_code": result.payload["code"],
                "architectural_dependencies": subgraph_context["callers_and_dependencies"]
            })

        answer = ai_client.answer_architectural_query(req.question, context_blocks)

        return {
            "question": req.question,
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na consulta cognitiva: {str(e)}")

@app.get("/report/qa-strategy")
def generate_qa_strategy():
    top_risks = system_graph.calculate_architectural_risk()[:10]
    
    if not top_risks:
        raise HTTPException(status_code=400, detail="O grafo está vazio. Rode o /analyze primeiro.")

    context_blocks = []

    for item in top_risks:
        node_id = item["component"]
        subgraph = system_graph.get_subgraph_context(node_id, depth=1)

        context_blocks.append({
            "target_component": node_id,
            "risk_metrics": item["metrics"],
            "architectural_neighbors": subgraph["callers_and_dependencies"]
        })

    try:
        qa_report = ai_client.generate_qa_strategy(context_blocks)
        
        return {
            "status": "success",
            "analyzed_components": len(context_blocks),
            "qa_strategy_report": qa_report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na geração cognitiva: {str(e)}")

@app.post("/analyze/diff")
def analyze_change_impact_route(req: DiffRequest):
    try:
        # Repassamos para a camada de domínio perfeitamente desacoplada
        result = analyze_change_impact(req.repo, req.changed_files, system_graph)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))