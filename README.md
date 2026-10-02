# NexBank Agentic AI Customer Service Agent with Feedback Loops

[![Architecture Status](https://img.shields.io/badge/Architecture-Phase%201%20(Days%201--3)-blue.svg)](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/docs/architecture/system-topology.md)
[![Project Code](https://img.shields.io/badge/Project-1C-emerald.svg)](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/zetheta-project.json)
[![Compliance](https://img.shields.io/badge/Compliance-PCI--DSS%20%7C%20SOC%202%20%7C%20GLBA-purple.svg)](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/docs/guardrails/security-rules.md)
[![Latency SLA](https://img.shields.io/badge/Latency%20SLA-p99%20%3C%203.0s-orange.svg)](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/docs/architecture/latency-budget.md)

An enterprise-grade, agentic conversational AI platform purpose-engineered for retail and commercial banking. The system combines deterministic finite-state control, dual-path natural language understanding (NLU), hybrid vector/lexical retrieval-augmented generation (RAG), strict regulatory safety guardrails, and human-in-the-loop continuous feedback loops.

---

## 🏛️ Architectural Pillars

1. **Deterministic State Machine + Agentic Reasoning**:
   Ensures that financial mutations (wire transfers, card locks, balance inquiries) are strictly validated against authentication privilege tiers and deterministic state transitions, while allowing LLMs to manage natural language nuances.
2. **Sub-3.0s p99 Response Latency**:
   Enforces a strict budget across all subsystem hops: NLU (<150ms), RAG Retrieval (<200ms), State lookup (<30ms), LLM Generation (<2,000ms), and Guardrails (<100ms).
3. **Multi-Tiered Safety & Regulatory Guardrails**:
   Automated blocking of unauthorized financial/investment advice (FINRA/CFPB), real-time PII/PCI redaction with cryptographic token vaults, and prompt injection defense via structural XML boundaries and canary tokens.
4. **Zero-Repetition Escalation Handover**:
   Pre-populates live banker CRM terminals with synthesized briefings, extracted parameters, and marked transcripts before the banker types their initial greeting.
5. **Closed Continuous Feedback Loop**:
   Captures explicit customer ratings, implicit behavioral drop-offs, and human banker post-escalation edits into an active learning pipeline with regression benchmarks.

---

## 📁 Repository Directory Layout

```
.
├── .env.example                               # Production & local environment variables template
├── CHANGELOG.md                               # Project session logs and design decisions
├── README.md                                  # Repository overview and quickstart guide
├── requirements.txt                           # Python dependencies & libraries
├── zetheta-project.json                       # Core Zetheta project metadata (Code 1C)
├── config/                                    # System runtime & guardrail configurations
│   ├── app-config.yaml                        # Application & threshold configuration
│   └── guardrails-config.yaml                 # Safety, PII, and financial advice rules
├── docs/                                      # Complete Architecture Specifications
│   ├── architecture/                          # Core Phase 1 Architecture
│   │   ├── system-topology.md                 # System topology, Mermaid diagram & scale blueprint
│   │   ├── dialogue-state-machine.md          # State schema, auth levels & multi-turn reasoning
│   │   ├── component-contracts.md             # Versioned JSON Schemas for all interfaces
│   │   ├── latency-budget.md                  # p50/p90/p99 budget & circuit breaking policies
│   │   └── failure-modes.md                   # FMEA analysis & graceful degradation policies
│   ├── intent-taxonomy/                       # NLU Hierarchy & Disambiguation
│   │   ├── taxonomy-spec.md                   # 6-domain hierarchy and intent matrix
│   │   ├── entity-rules.md                    # Regex, NER, and slot normalization
│   │   └── disambiguation-trees.md            # Clarification trees & fallback loops
│   ├── knowledge-base/                        # RAG & Document Store
│   │   ├── kb-schema.md                       # Knowledge chunk schema & metadata
│   │   ├── retrieval-pipeline.md              # Hybrid RRF search & cross-encoder rerank
│   │   └── sample-entries.json                # Sample verified banking policy chunks
│   ├── guardrails/                            # Compliance & Security Defenses
│   │   ├── financial-advice-guardrails.md     # Prohibitions & canned responses
│   │   ├── security-rules.md                  # PII/PCI masking & surrogate token vault
│   │   └── adversarial-defences.md            # Prompt injection defense & canaries
│   ├── learning-pipeline/                     # Continuous Improvement & Feedback
│   │   ├── feedback-loops.md                  # Human-in-the-loop active learning
│   │   ├── safety-preservation.md             # Golden test suite & automated rollback
│   │   └── ab-testing.md                      # Shadow evaluation & canary routing
│   ├── escalation/                            # Human Banker Handover
│   │   ├── trigger-conditions.md              # Quantitative thresholds & decision table
│   │   ├── routing-logic.md                   # Skill-based CRM queue assignment
│   │   └── context-package.md                 # Zero-repetition context package schema
│   └── metrics/                               # Observability & Business KPIs
│       ├── kpi-framework.md                   # Containment, CSAT, Latency & Faithfulness
│       └── dashboard-wireframes.md            # Operations console & banker terminal layout
├── diagrams/                                  # Exported architectural diagrams and assets
├── simulations/                               # Synthetic customer personas and load tests
└── tests/                                     # Automated test suites
    ├── conftest.py                            # Shared Pytest fixtures and state factories
    └── test_dialogue_state.py                 # Dialogue state validation & unit tests
```

---

## 🚀 Quickstart & Development Setup

### 1. Prerequisites
* Python 3.11 or higher
* PostgreSQL 16+ (with `pgvector`)
* Redis 7.0+
* Docker & Docker Compose (for local development dependencies)

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/nexbank/customer-service-agent.git
cd customer-service-agent

# Create virtual environment
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

### 3. Running Unit & Schema Validation Tests
```bash
pytest -v tests/
```

---

## 🗺️ Project Milestones & Roadmap

* **Phase 1 (Days 1–3) [COMPLETED]**: Core architecture, system topology, dialogue state machine schema, interface contracts, latency budget, and failure modes analysis.
* **Phase 2 (Days 4–7)**: Dual-path NLU pipeline implementation, Rasa DIET training, entity gazetteers, and disambiguation flows.
* **Phase 3 (Days 8–10)**: Hybrid RAG knowledge base, Pinecone/ChromaDB indexing, cross-encoder reranker, and financial compliance guardrails.
* **Phase 4 (Days 11–13)**: Continuous learning pipeline, feedback ingestion engine, golden regression test harness, and shadow evaluation runner.
* **Phase 5 (Days 14–16)**: Intelligent CRM escalation router, live banker WebSocket terminal, and executive metrics dashboard.

---

## 🔒 Security & Regulatory Compliance

This system is engineered under strict adherence to:
* **PCI-DSS v4.0**: Complete tokenization of primary account numbers (PAN) and zero retention of sensitive authentication data (CVV/PIN).
* **SOC 2 Type II**: Role-based access control, cryptographic audit trails, and VPC network isolation.
* **FINRA & CFPB**: Automated interception of unauthorized investment and tax advice with mandatory regulatory disclaimers.
