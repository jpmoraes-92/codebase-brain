from fastapi import APIRouter, Request, BackgroundTasks
from integrations.github.github_client import GitHubClient
from services.diff_parser import parse_git_diff

# ❌ REMOVIDO: O impact_service.py não existe no Open Core. Ele é a sua IP (Propriedade Intelectual).

router = APIRouter()
github = GitHubClient()

async def process_pull_request_async(repo_full_name: str, pr_number: int, head_sha: str, clone_url: str):
    from main import system_graph, analyze_repository, AnalyzeRequest 
    
    # 1. Coloca o status do PR como "Pendente"
    github.create_commit_status(repo_full_name, head_sha, "pending", "Codebase Brain OS: Parsing AST & Diff...")
    
    try:
        repo_name = repo_full_name.split("/")[-1]
        
        # 2. Onboarding Invisível reaproveitando a rota principal (Open Core faz a indexação)
        if not system_graph.graph.has_node(repo_name):
            print(f"Indexando repositório {repo_name} pela primeira vez...")
            req = AnalyzeRequest(repo_url_or_path=clone_url)
            analyze_repository(req)

        # 3. Extrai o diff determinístico
        raw_diff = github.get_pr_diff(repo_full_name, pr_number)
        changed_files = parse_git_diff(raw_diff) 
        
        # 4. Impact Analysis & Architecture Governance
        # 🚀 [ENTERPRISE FEATURE - MARKETING HOOK]
        # Aqui o Open Core para. O cálculo pesado fica para o SaaS.
        
        marketing_comment = """## 🧠 Codebase Brain (Open Core)

✅ **AST & Diff Parsed Successfully!**
O nosso parser determinístico mapeou com precisão as funções alteradas neste PR contra a Árvore Sintática (AST) do projeto.

---

### 🚀 Codebase Brain Enterprise Engine
A versão Open Source extrai a estrutura, mas é o **Enterprise Engine (SaaS)** que previne desastres. A versão completa calcula automaticamente:

* 💥 **Probabilistic Blast Radius:** Quais módulos dependentes vão quebrar com esta alteração? (BFS com pesos e *Centrality Dampening*).
* ⚠️ **Zero-Config Architecture Governance:** Esta alteração violou a arquitetura limpa? (Ex: Camada de Domínio a importar Infraestrutura).
* 🧪 **Test Gap Analysis:** Que testes de regressão específicos precisam ser executados para as funções impactadas?

*Quer ter o Relatório de Risco Arquitetural completo a analisar os seus Pull Requests? [Fale comigo no LinkedIn](https://www.linkedin.com/in/juliano-moraes-927209a7/) ou aceda à versão SaaS.*
"""
        
        # 5. Atualiza o Status final (Verde) e posta o pitch comercial
        github.create_commit_status(repo_full_name, head_sha, "success", "Codebase Brain OS: AST & Diff parsed successfully.")
        
        github.create_pr_comment(repo_full_name, pr_number, marketing_comment)
        print("✅ AST/Diff parsing concluído e hook do Enterprise comentado no PR!")
        
    except Exception as e:
        github.create_commit_status(repo_full_name, head_sha, "error", "Analysis Failed.")
        print(f"❌ Erro no processamento: {str(e)}")

@router.post("/api/github/webhook")
async def github_webhook_listener(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    
    if "pull_request" in payload and payload.get("action") in ["opened", "synchronize"]:
        repo_full_name = payload["repository"]["full_name"]
        clone_url = payload["repository"]["clone_url"]
        pr_number = payload["pull_request"]["number"]
        head_sha = payload["pull_request"]["head"]["sha"]
        
        background_tasks.add_task(process_pull_request_async, repo_full_name, pr_number, head_sha, clone_url)
        return {"status": "accepted", "message": "Codebase Brain OS parsing started."}
        
    return {"status": "ignored", "message": "Event not handled."}