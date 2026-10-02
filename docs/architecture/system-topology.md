# NexBank Agentic AI Customer Service: System Topology & Architecture

## 1. Executive Summary & Architectural Overview

The NexBank Agentic AI Customer Service Agent (`Project 1C`) is an enterprise-grade conversational AI platform purpose-built for regulated retail and commercial banking. The architecture blends deterministic finite-state control with generative agentic intelligence to guarantee strict regulatory compliance, low-latency execution (<3.0s p99), zero financial misinformation, and autonomous self-improvement through closed feedback loops.

The platform handles omnichannel customer interactions (Mobile App, Web Portal, Telephony IVR, Messaging APIs) through a centralized orchestration fabric governed by Temporal.io workflows, FastAPI asynchronous microservices, hybrid retrieval-augmented generation (RAG), and dual-path natural language understanding (NLU).

---

## 2. End-to-End System Topology Diagram

```mermaid
graph TD
    subgraph Omnichannel Ingress Layer
        MOB["Mobile Banking App (iOS/Android)"]
        WEB["NexBank Web Banking Portal"]
        IVR["Telephony / Voice IVR Gateway"]
        MSG["Secure Messaging API"]
    end

    subgraph API Gateway & Edge Security
        APIGW["API Gateway (FastAPI / Envoy)"]
        WAF["Web Application Firewall & DDoS"]
        AUTH["OAuth2 / mTLS / Session Token Auth"]
        RL["Distributed Token-Bucket Rate Limiter"]
    end

    subgraph Ingress Security & Privacy Boundary
        PII_MASK["PII/PCI Redactor (Presidio + Regex)"]
        IN_FILTER["Prompt Injection & Jailbreak Guardrail"]
    end

    subgraph Core Orchestration & Dialogue Engine
        ORCH["Agentic Orchestrator (LangChain / Temporal)"]
        DSM["Dialogue State Machine (State + Context)"]
        SESS_STORE[("Redis Enterprise Cluster: Session State")]
    end

    subgraph Dual-Path NLU Pipeline
        ROUTER_NLU{"Intent Confidence Router"}
        RASA["Rasa NLU (Deterministic Classifier & DIET)"]
        ZERO_SHOT["Transformer Zero-Shot / Semantic Matcher"]
        NER["Hybrid Named Entity Recognizer"]
    end

    subgraph Retrieval-Augmented Generation (RAG)
        QUERY_TRANS["Query Rewriter & Expander"]
        HYBRID_RET["Hybrid Retriever (Dense + BM25 Lexical)"]
        RERANK["Cross-Encoder Reranker (bge-reranker)"]
        VEC_DB[("Pinecone / ChromaDB Vector Store")]
        DOC_STORE[("PostgreSQL 16: Document Store")]
    end

    subgraph Reasoning & Tool Execution Layer
        LLM_GW["LLM Gateway & Circuit Breaker"]
        LLM_PRI["Primary LLM (GPT-4o / Claude 3.5 Sonnet)"]
        LLM_FALLBACK["Self-Hosted Fallback LLM (Llama 3.1 8B)"]
        TOOL_EXEC["Deterministic Banking Tool Execution Engine"]
        CORE_BANKING[("Core Banking API (REST/gRPC)")]
    end

    subgraph Safety, Policy & Financial Guardrails
        POLICY_VAL["Policy & Regulatory Compliance Validator"]
        FIN_ADVICE["FINRA/CFPB Financial Advice Classifier"]
        OUT_PII["De-Anonymizer & Cryptographic Token Rehydrator"]
        FACT_CHECK["Hallucination & Grounding Check (Faithfulness)"]
    end

    subgraph Escalation & Human-in-the-Loop Handover
        ESC_ROUTER{"Escalation Condition Check"}
        QUEUE_MGR["Temporal Escalation Queue Manager"]
        AGENT_DESKTOP["NexBank Live Banker Desktop (CRM)"]
    end

    subgraph Continuous Learning & Feedback Loop
        EVENT_BUS["Kafka / EventBridge Event Bus"]
        AUDIT_LOG[("PostgreSQL Audit Trail & TimescaleDB")]
        TELEMETRY["OpenTelemetry & Prometheus Exporter"]
        FEEDBACK_PROC["Automated Feedback Ingestion & Labeling"]
        SHADOW_TEST["Shadow Evaluation & Canary Model Runner"]
    end

    %% Ingress Connections
    MOB --> APIGW
    WEB --> APIGW
    IVR --> APIGW
    MSG --> APIGW

    APIGW --> WAF --> AUTH --> RL
    RL --> PII_MASK --> IN_FILTER --> ORCH

    %% Dialogue & NLU Connections
    ORCH <--> DSM
    DSM <--> SESS_STORE
    ORCH --> ROUTER_NLU
    ROUTER_NLU --> RASA
    ROUTER_NLU --> ZERO_SHOT
    ROUTER_NLU --> NER
    RASA --> ORCH
    ZERO_SHOT --> ORCH
    NER --> ORCH

    %% RAG Connections
    ORCH --> QUERY_TRANS --> HYBRID_RET
    HYBRID_RET <--> VEC_DB
    HYBRID_RET <--> DOC_STORE
    HYBRID_RET --> RERANK --> ORCH

    %% Tool & Model Execution
    ORCH --> LLM_GW
    LLM_GW --> LLM_PRI
    LLM_GW -. Fallback .-> LLM_FALLBACK
    ORCH --> TOOL_EXEC --> CORE_BANKING

    %% Safety & Verification
    ORCH --> FACT_CHECK --> FIN_ADVICE --> POLICY_VAL --> OUT_PII

    %% Escalation Logic
    OUT_PII --> ESC_ROUTER
    ESC_ROUTER -- "Escalate Triggered" --> QUEUE_MGR --> AGENT_DESKTOP
    ESC_ROUTER -- "Pass Clean" --> APIGW

    %% Feedback & Telemetry
    ORCH -. Event Stream .-> EVENT_BUS
    FACT_CHECK -. Flags .-> EVENT_BUS
    AGENT_DESKTOP -. Corrections .-> EVENT_BUS
    EVENT_BUS --> AUDIT_LOG
    EVENT_BUS --> TELEMETRY
    EVENT_BUS --> FEEDBACK_PROC --> SHADOW_TEST
```

---

## 3. Core Component Specifications

### 3.1. Ingress Security & Privacy Boundary
* **Inputs**: Raw omnichannel requests (`user_id`, `session_id`, `channel`, `raw_payload`, `auth_context`).
* **Processing Logic**:
  1. TLS 1.3 termination and JWT assertion verification.
  2. Rate limiting check (Token bucket per `user_id` and IP: default 10 requests / 10s burst).
  3. PII/PCI scanning via Microsoft Presidio and compiled regex banks for PAN (Primary Account Numbers), CVV, SSN, Tax ID, and account numbers. PII is tokenized into deterministic surrogate tokens (e.g., `{{CARD_NUM_TOKEN_a8f9}}`).
  4. Prompt injection detection using heuristic signature matching, perplexity evaluation, and adversarial delimiter isolation.
* **Outputs**: Sanitized user utterance payload, tokenized entities, security risk vector.
* **Fallback Mechanism**: Reject malicious prompts with static error response code `SEC_001`; if PII masking fails, abort session to live support with encrypted crash dump.

### 3.2. Dual-Path Natural Language Understanding (NLU) Pipeline
* **Inputs**: Sanitized customer utterance string and active conversation context.
* **Processing Logic**:
  1. High-speed intent inference through Rasa NLU DIETClassifier (Dual Intent and Entity Transformer).
  2. If primary intent confidence is $\ge 0.88$, accept deterministic intent classification.
  3. If primary intent confidence is between $0.65$ and $0.88$, invoke lightweight zero-shot semantic classifier (DeBERTa-v3-small) and evaluate top-2 margin.
  4. Extract domain-specific entities (amounts, dates, transaction references, account types) using Spacy + regex patterns + contextual dictionary lookups.
* **Outputs**: Structured `NLUResult` containing `primary_intent`, `confidence_score`, `sub_intents`, `extracted_entities`, and `disambiguation_required` flag.
* **Fallback Mechanism**: If confidence $< 0.65$, trigger conversational disambiguation protocol (presenting top-2 canonical choices) or route to universal fallback intent `fallback.unrecognized_intent`.

### 3.3. Dialogue State Machine (DSM) & Orchestrator
* **Inputs**: `NLUResult`, active session state record from Redis, customer profile metadata, historical turn memory.
* **Processing Logic**:
  1. Resolve anaphora and ellipses using contextual conversational turn stack.
  2. Verify whether requested intent requires higher step-up authentication (e.g., balance inquiry vs. international wire transfer).
  3. Enforce deterministic state transitions; block illegal state jumps (e.g., cannot execute transfer without explicit user confirmation step).
  4. Synthesize current task goal: Retrieval question, deterministic tool invocation, or human handover.
* **Outputs**: `DialogueAction` directing whether to query RAG, execute Core Banking Tool, request disambiguation, or escalate.
* **Fallback Mechanism**: Corrupted session state reverts to latest persistent PostgreSQL snapshot; unrecoverable state drops smoothly to live agent with full contextual state serialization.

### 3.4. Retrieval-Augmented Generation (RAG) Knowledge Base
* **Inputs**: Resolved search query, customer segment metadata, channel permissions.
* **Processing Logic**:
  1. Dense vector search via Pinecone / ChromaDB with `text-embedding-3-small` embeddings (cosine similarity, top-20).
  2. Sparse lexical search via BM25 over tokenized policy documents (top-20).
  3. Reciprocal Rank Fusion (RRF) with reciprocal constant $k=60$.
  4. Cross-encoder reranking via `bge-reranker-large`, filtering top-3 highest scored chunks (minimum score threshold $\ge 0.72$).
* **Outputs**: Top-3 contextual document snippets, source document citations, compliance revision timestamps.
* **Fallback Mechanism**: In the event of vector store timeout ($>200\text{ms}$), execute fallback search on PostgreSQL full-text search index (`tsvector`). If no chunks meet confidence threshold, trigger verified banking disclaimers or escalate.

### 3.5. Reasoning, Tool Execution & LLM Gateway
* **Inputs**: System prompt, assembled state history, verified RAG context chunks, tool schema definitions.
* **Processing Logic**:
  1. Dynamic prompt assembly incorporating strict system instructions, guardrails, and deterministic tool schemas.
  2. Generation via OpenAI `gpt-4o-mini` or Claude 3.5 Sonnet with temperature $= 0.0$ and strict JSON schema output enforcement.
  3. For banking operations, generate verified gRPC / REST tool parameters, validate against Pydantic schema, and invoke Core Banking API via idempotency keys.
* **Outputs**: Proposed draft response or verified tool execution result.
* **Fallback Mechanism**: Automated circuit breaker kicks in after 2 consecutive timeouts or 5xx responses from primary LLM provider. Traffic instantly shifts to self-hosted Ollama / vLLM Llama 3.1 8B instance deployed on private VPC Kubernetes cluster.

### 3.6. Safety, Policy & Financial Guardrails
* **Inputs**: Proposed response draft, retrieved context chunks, original user query.
* **Processing Logic**:
  1. Hallucination and Faithfulness verification: All factual statements must be grounded in provided context chunks or API responses (NLI entailment score $\ge 0.85$).
  2. FINRA/CFPB Financial Advice Guardrail: Detect unauthorized investment recommendations, guarantee promises, or forward-looking price predictions.
  3. Mandatory banking disclaimer injection (e.g., FDIC insurance limits, loan APR disclosure terms).
  4. Rehydration of encrypted PII tokens back to authorized display representation for the client channel.
* **Outputs**: Certified safe, compliant customer-facing response text.
* **Fallback Mechanism**: Any guardrail violation immediately suppresses generated text and replaces it with approved canned compliance response or auto-escalates to human agent.

### 3.7. Escalation Router & Human-in-the-Loop Handover
* **Inputs**: Guardrail breaches, sentiment plunge ($<-0.60$), repetitive intent failure ($\ge 2$ consecutive fallbacks), or high-risk transaction intent.
* **Processing Logic**:
  1. Packets formatted into standardized `EscalationContextPackage` (summary of issue, slot values, raw transcript, sentiment trajectory, customer value tier).
  2. Push to CRM skill-based routing queue (e.g., Fraud Desk, Tier 2 Disputes, Mortgage Specialist).
  3. Seamlessly notify user and switch transport session to live agent WebSocket bridge.
* **Outputs**: Escalated ticket ID, live agent queue assignment, client handoff message.
* **Fallback Mechanism**: If live agent queue wait time exceeds 180 seconds, offer asynchronous callback booking with guaranteed SLA window.

---

## 4. Scalability Blueprint (1x, 10x, 100x Capacity)

| Dimension / Metric | 1x Baseline Capacity | 10x Scale Capacity | 100x Scale Capacity |
| :--- | :--- | :--- | :--- |
| **Daily Session Volume** | 18,000 sessions / day | 180,000 sessions / day | 1,800,000 sessions / day |
| **Average Query Rate** | 2.1 RPS | 21 RPS | 210 RPS |
| **Peak Query Rate (5x Surge)** | 10.5 RPS | 105 RPS | 1,050 RPS |
| **FastAPI Microservices** | 2 pods (2 vCPU, 4GB RAM) | 8 pods (4 vCPU, 8GB RAM) | 40 pods with Horizontal Pod Autoscaler (HPA) |
| **Dialogue State Cache** | Redis Single Primary + 1 Replica | Redis Enterprise 3-Node Cluster | Redis Enterprise Multi-Region Active-Active Sharded Cluster |
| **Primary Relational Store** | PostgreSQL 16 (4 vCPU, 16GB) | PostgreSQL Aurora Cluster (1 Writer, 2 Readers) | Partitioned Aurora Serverless v2 + Read Replicas + PgBouncer Poolers |
| **Vector Database** | ChromaDB Persistent Volume / Pinecone Standard | Pinecone Serverless (Multi-Pod Enterprise) | Dedicated Pinecone Enterprise Pods with Regional Vector Caches |
| **Orchestration Workers** | 2 Temporal Workers | 10 Temporal Workers | 50 Temporal Workers across partitioned task queues |
| **LLM Gateway Throughput** | 15 tokens/sec avg | 150 tokens/sec avg | 1,500 tokens/sec avg (Tier-4 enterprise quotas + multi-region failover) |
| **Network Ingress Bandwidth** | 50 Mbps burst | 500 Mbps burst | 5 Gbps dedicated DirectConnect / ExpressRoute |

### 4.1. Caching & Throughput Optimizations
1. **L1 In-Memory Fast Cache**: Compiled regexes, static policy rules, and frequent intent embeddings cached directly within worker RAM.
2. **L2 Semantic Query Cache (Redis)**: Frequent static banking FAQs (e.g., routing numbers, branch hours, wire cutoffs) cached with embedding similarity threshold $>0.98$; avoids LLM and vector DB calls entirely, responding in $<15\text{ms}$.
3. **Connection Pooling**: Managed via PgBouncer with `transaction` pooling mode, keeping active database connections strictly bounded under surge traffic.
4. **Graceful Queue Buffering**: Temporal and Kafka decouple non-blocking telemetry, audit logs, and feedback loops from user-facing latency.

---

## 5. Security & Regulatory Compliance Topology

```mermaid
graph LR
    subgraph DMZ / Public Boundary
        USER["Omnichannel User"] --> WAF["WAF / TLS 1.3"]
    end

    subgraph Secure Ingress Zone
        WAF --> ENVOY["Envoy Ingress"]
        ENVOY --> MASK["Presidio Tokenizer"]
    end

    subgraph Internal Secure VPC (PCI-DSS & SOC 2 Scope)
        MASK --> APP["Agent Orchestrator"]
        APP --> INT_DB[("Postgres / pgvector")]
        APP --> SESS[("Redis TLS")]
    end

    subgraph External Isolated Gateways
        APP --> LLM_GW["LLM Secure Proxy (Zero-Retention)"]
        LLM_GW --> LLM["Enterprise LLM (BAA Signed)"]
    end

    subgraph Human Operator Boundary
        APP --> SEC_CRM["Encrypted CRM Gateway"]
        SEC_CRM --> BANKER["Authenticated Banker Terminal"]
    end
```

* **Data At Rest**: AES-256-GCM encryption with AWS KMS / HashiCorp Vault customer-managed keys (CMK) rotated every 90 days.
* **Data In Transit**: Strict TLS 1.3 enforcement with mutual TLS (mTLS) between all microservices.
* **Zero Data Retention**: LLM API calls execute strictly under signed Enterprise Zero Data Retention agreements (no customer data used for foundational model training).
* **Immutable Audit Trail**: Turn-by-turn cryptographic hashing stored in append-only TimescaleDB hypertable for compliance audits.
