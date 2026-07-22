<div align="center">

# PRAGYA AI

**Industrial Knowledge Reasoning Engine**

*Reasons across regulations, maintenance history, permits, and expert knowledge — instead of just retrieving from one.*

Built for **ET AI Hackathon 2026 — Problem Statement #8** (Industrial Intelligence / Document Management / Knowledge Engineering)

</div>

---

## The Problem

Refinery and heavy-industry operations run on knowledge that's correct in isolation and dangerous in combination. A maintenance log, a permit-to-work system, and a regulatory clause each say something true — but they live in separate systems, and nobody reads all three together before a decision is made.

| Statistic | Source |
|---|---|
| 35% of working hours lost searching for information | McKinsey Global Survey 2024 |
| 7–12 disconnected document systems per plant | NASSCOM–EY Study |
| 18–22% of unplanned downtime from incomplete equipment history | BIS Research |
| 25% of senior engineers retiring within 10 years | Industry estimate |

**PRAGYA AI** ingests that fragmented knowledge, connects it in a live knowledge graph, and reasons across it with specialized agents — surfacing conflicts before they become incidents.

---

## What Makes It Different

A standard RAG system asked *"is it safe to weld on Line-4 this Saturday?"* retrieves OISD clauses about hot work. No permit awareness. No equipment context.

**PRAGYA AI** cross-references the active welding permit, the concurrent maintenance work order on the same line, and the governing OISD clause — flags a **high-severity conflict**, quantifies the ₹ downtime exposure, and proposes resolution windows. The answer is *reasoned across three sources*, not retrieved from one.

- 🧠 **Temporal Entity State Graph** — Neo4j nodes carry a full `state_history`, not static attributes, enabling reasoning about specific past or future timestamps
- ⚖️ **Conflict Arbitration as Top-Level Synthesis** — one prioritised recommendation with a composite score, not four panels to reconcile manually
- 👷 **Tacit Knowledge Capture** — retiring engineers' plain-language knowledge is extracted, graphed, and queryable identically to formal documents

---

## Architecture

![PRAGYA AI System Architecture](./Pragya_AI_Architecture.png)

**Request flow:** query → EventRouter classifies intent (cosine similarity, 5 prototypes) → parallel dispatch to specialist agents → each retrieves from Neo4j (graph/temporal) + Supabase (semantic) → Synthesis Agent arbitrates conflicts and outputs one composite-scored recommendation → streamed live via SSE.

**Ingestion flow:** upload → parse (PyMuPDF / openpyxl / python-docx / vision fallback) → LLM entity extraction → Neo4j graph update → parallel chunk + embed → Supabase HNSW index.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, React Query v5, React Router v7, Framer Motion, D3 |
| **Backend** | FastAPI (async), LangGraph (`StateGraph`), Server-Sent Events streaming |
| **LLM** | Groq — `llama-3.3-70b-versatile` (text), `llama-4-scout-17b-16e-instruct` (vision/OCR) |
| **Embeddings** | sentence-transformers `all-MiniLM-L6-v2` (384-dim) |
| **Knowledge Graph** | Neo4j Aura |
| **Vector Store** | Supabase (PostgreSQL + pgvector, HNSW index) |
| **Document Parsing** | PyMuPDF, openpyxl, python-docx |
| **PDF Generation** | ReportLab |

---

## Agents

| Agent | Role |
|---|---|
| **EventRouter** | Classifies query intent, dispatches to relevant specialists |
| **Copilot** | Dual retrieval (vector + graph), chat-aware, returns answer + confidence + citations |
| **Maintenance** | Composite risk scoring, financial exposure (₹), urgency tiering |
| **Compliance** | Regulation vs. procedure gap detection |
| **Expert** | Extracts and graphs operator tacit knowledge |
| **Synthesis** | Arbitrates all outputs, resolves conflicts, computes final composite score |

---

## Features

- 📄 Multi-format ingestion — PDF (text + scanned/vision), Excel, Word
- 🕸️ Interactive knowledge graph explorer (D3 force graph, drag/zoom/pan)
- 💬 Streaming copilot chat with live agent pipeline visibility
- ⚡ Real-time conflict detection with financial exposure in INR
- 📋 One-click work order PDF generation
- 🎓 Expert / tacit knowledge capture interface
- 📊 Benchmark suite with latency tracking

---

## Getting Started

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate   # .\venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # add NEO4J_URI, SUPABASE_URL, GROQ_API_KEY, etc.
uvicorn main:app --reload   # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

---

## Repository Structure

```
pragya-ai/
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── agents/                # LangGraph agents (router, copilot, maintenance, compliance, expert, synthesis)
│   ├── services/              # LLM, embedding, Neo4j, Supabase clients
│   ├── routers/                # query, documents, conflicts, graph, expert, benchmarks
│   └── scripts/                # seed data, benchmarks, regulatory doc ingestion
├── frontend/
│   └── src/
│       ├── pages/              # Home, Copilot, Conflicts, GraphExplorer, Documents, ExpertCapture, Dashboard
│       ├── components/
│       └── hooks/
├── Pragya_AI_Architecture.png
└── README.md
```

---

## Limitations & Roadmap

**Current scope:** proof-of-concept — no authentication layer, synthetic seed data for demo conflicts.

**Planned:** auth + multi-tenant `plant_id` namespacing, scheduled regulatory ingestion, query-result caching, graceful per-agent degradation, automated compliance audits, full PDF report export.

---

<div align="center">

*Built for ET AI Hackathon 2026 — Problem Statement #8*

</div>
