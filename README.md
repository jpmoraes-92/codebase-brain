```markdown
# 🧠 Codebase Brain
### Continuous Architecture Intelligence for Modern Codebases

![Python](https://img.shields.io/badge/python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-green)
![React](https://img.shields.io/badge/frontend-React-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

**Codebase Brain** is an **AI-powered architecture intelligence platform** that predicts the **blast radius of code changes before they are merged**.

Instead of discovering architectural failures in production, Codebase Brain exposes them **during Pull Request review**.

It works as an **invisible GitHub Gatekeeper** that analyzes structural dependencies, computes architectural risk, and reports the impact directly inside your PR.

---

# 🚨 The Problem

In modern software systems, the hardest challenge is **not writing code — it's predicting the consequences of changing it**.

Traditional tools focus on:

- unit tests
- linting
- static analysis

But they **ignore system topology**.

When a developer modifies a central module, the cascading impact across services, packages, and dependencies often remains **invisible until runtime**.

This leads to:

- fragile architectures
- unpredictable regressions
- long debugging cycles
- production incidents

---

# 💡 The Solution

Codebase Brain converts your entire repository into a **mathematical dependency graph**.

Using **AST parsing, graph traversal, and semantic indexing**, the platform can simulate how changes propagate across the system.

The result:

**Architecture awareness inside the development workflow.**

Two core experiences power the platform.

---

# 👨‍💻 Developer Experience (Zero-Friction)

Developers don't open a dashboard.

They simply open a **Pull Request**.

Codebase Brain automatically:

1. Intercepts the PR webhook
2. Parses the `.diff`
3. Traverses the dependency graph
4. Calculates a **Risk Score**
5. Posts a report directly in the PR

Example PR feedback:

```

Architectural Risk Score: 72 / 100

Blast Radius:

* payment_service.py
* invoice_manager.py
* billing_controller.py

High Risk Nodes Detected

* payment_service.py (fan-out: 17)

Recommendation
Add integration tests covering payment flow before merging.

```

---

# 🧠 Tech Lead Experience (Architecture War Room)

While developers interact through GitHub, Tech Leads access a **React dashboard** that provides deep architectural visibility.

Capabilities include:

### 🔍 Architecture Graph

Interactive visualization of system dependencies.

Helps identify:

- tightly coupled modules
- central bottlenecks
- hidden architectural risks

---

### 🧪 What-If Simulation (Architecture Sandbox)

Before assigning a refactor, Tech Leads can simulate the change.

Input:

```

File: ingestion_service.py
Change: remove MongoDB dependency

```

Output:

```

Blast Radius: 12 services affected
Risk Score: 81
Critical Path: ingestion → queue → analytics

```

This allows architectural decisions **before code is written**.

---

### 💬 Cognitive Code Chat

An AI assistant with full architectural context of the codebase.

Example queries:

```

What breaks if we remove MongoDB from IngestionService?

```
```

Which components depend on PaymentService?

```
```

Where should QA focus testing for this Pull Request?

```

Powered by **vector embeddings + graph-aware retrieval (RAG).**

---

# ✨ Core Features

### 🛡️ Invisible PR Gatekeeper
- GitHub webhook integration
- diff analysis
- architectural risk scoring
- PR comment generation
- commit status updates

---

### 🕸️ Architecture Graph Engine
- AST parsing
- dependency extraction
- NetworkX graph modeling
- BFS impact traversal

---

### 📊 Architectural Risk Scoring
Risk is calculated using multiple structural signals:

- fan-in / fan-out
- dependency depth
- cyclomatic complexity
- graph centrality

---

### 🧠 Cognitive Code Intelligence
AI assistant capable of answering questions about:

- system architecture
- dependency relationships
- testing strategies
- refactoring impact

---

# 🏗️ System Architecture

```

Repository
│
▼
Ingestion Engine
(Repo Loader + AST Parser)
│
▼
Dependency Graph Builder
(NetworkX)
│
▼
Impact Analysis Engine
(Graph Traversal)
│
▼
Semantic Layer
(Embeddings + RAG)
│
▼
Interfaces
├── GitHub PR Integration
└── React Dashboard

````

---

# ⚡ Quick Start

Clone the repository:

```bash
git clone https://github.com/your-org/codebase-brain
cd codebase-brain
````

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

Windows

```
venv\Scripts\activate
```

Mac/Linux

```
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

Run the backend:

```
uvicorn main:app --reload --port 8080
```

Open the API docs:

```
http://localhost:8080/docs
```

---

# 🔌 Example API Usage

Analyze a repository:

```bash
curl -X POST http://127.0.0.1:8080/analyze \
-H "Content-Type: application/json" \
-d '{
  "repo_url_or_path": "C:\\Users\\User\\my-project"
}'
```

---

# 🗺️ Roadmap

### Phase 1 — Core Intelligence Engine

* [x] AST parser
* [x] dependency graph builder
* [x] blast radius analysis
* [x] architectural risk scoring

---

### Phase 2 — GitHub Native Integration

* [ ] GitHub App authentication
* [ ] webhook listener
* [ ] automatic PR analysis
* [ ] commit status checks

---

### Phase 3 — Architecture Intelligence Platform

* [ ] interactive architecture graph
* [ ] PR risk history
* [ ] architecture health dashboard
* [ ] AI architecture advisor

---

# 🌍 Vision

Codebase Brain aims to become the **central intelligence layer for software architecture**.

Just as **CI/CD pipelines automate builds and tests**, Codebase Brain introduces **automated architectural reasoning** into the development lifecycle.

The long-term goal:

> Every Pull Request should know the architectural consequences of the change before it is merged.

---

# 🤝 Contributing

Contributions are welcome.

If you'd like to improve the architecture engine, graph analysis, or AI layer, feel free to open an issue or submit a pull request.

---

# 👨‍💻 Author

**Juliano P Moraes**

QA Engineer specialized in **Test Automation & Software Architecture**
Technologist in **Systems Analysis and Development**

Focused on increasing engineering maturity and building bridges between **quality, architecture, and continuous delivery**.

---

# 📜 License

MIT License

```

---