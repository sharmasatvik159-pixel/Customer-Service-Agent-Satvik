# NexBank Agentic AI Customer Service: End-to-End Latency Budget & SLA Specification

## 1. Executive Latency Target

To deliver an exceptional, human-parity conversational banking experience, the NexBank platform enforces a **hard end-to-end response latency limit of 3,000 milliseconds (3.0s) at the 99th percentile (p99)** across all standard customer turns. For streaming-capable channels (Web and Mobile), Time-to-First-Token (TTFT) must be strictly under **800ms**.

Any single subsystem exceeding its allocated latency envelope must trigger automated circuit breaking and graceful fallback paths rather than stalling the conversation.

---

## 2. Stage-by-Stage Latency Budget Allocation

```
Total Response Envelope: <= 3,000ms (p99)
+-------------------------------------------------------------------------------------------------------+
| Ingress / PII | NLU Pipeline | State / Cache | Hybrid RAG |  LLM Inference Generation  | Guardrails | Net |
|    < 50ms     |   < 150ms    |    < 30ms     |  < 200ms   |         < 2,000ms          |  < 100ms   | 50ms|
+-------------------------------------------------------------------------------------------------------+
```

### 2.1. Percentile Budget Breakdown Matrix

| Execution Stage | Target Subsystem | P50 (Median) | P90 Budget | P99 Hard Cap | Max Timeout | Fallback Degradation Trigger |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1: Ingress & Security** | TLS Termination, WAF, Rate Limiting, PII Redaction | 18 ms | 35 ms | **50 ms** | 80 ms | Pass raw text through compiled regex-only fast redactor |
| **Stage 2: NLU Pipeline** | Rasa DIET Classifier, Intent Routing, Entity Extraction | 45 ms | 100 ms | **150 ms** | 200 ms | Skip secondary zero-shot classifier; use top Rasa intent |
| **Stage 3: State & Context** | Redis Session Read, Anaphora, History Window Pruning | 8 ms | 18 ms | **30 ms** | 50 ms | Read local thread memory; schedule async Redis sync |
| **Stage 4: Hybrid RAG Search** | Dense Vector (Pinecone/Chroma) + BM25 + bge-rerank | 65 ms | 140 ms | **200 ms** | 300 ms | Skip reranker; take top-2 BM25/Dense results directly |
| **Stage 5: Tool Execution** *(When Applicable)* | Core Banking API / Balance Check / Card Status | 80 ms | 180 ms | **350 ms** | 500 ms | Canned "System undergoing brief maintenance" message |
| **Stage 6: LLM Generation** | Prompt Assembly, Primary Gateway (GPT-4o-mini / Claude) | 750 ms | 1,400 ms | **2,000 ms** | 2,200 ms | Fallback to self-hosted Llama 3.1 8B on local GPU cluster |
| **Stage 7: Output Guardrails** | Hallucination Check, Financial Advice, De-masking | 25 ms | 65 ms | **100 ms** | 150 ms | Run deterministic regex-only disclaimer appender |
| **Stage 8: Egress & Network** | Network serialization, HTTP/WebSocket delivery | 15 ms | 35 ms | **50 ms** | 100 ms | Client TCP retransmit |
| **TOTAL (Turn Execution)** | **Full Round-Trip Envelope** | **1,006 ms** | **1,973 ms** | **2,980 ms** | **3,000 ms** | **Graceful Escalation to Live Banker** |

---

## 3. Subsystem Latency Management & Circuit Breaking

### 3.1. Natural Language Understanding (NLU) Budget: 150ms
* **Optimization**: Rasa DIET and tokenizers are loaded into shared worker memory (no remote HTTP hops).
* **Early Exit**: If Rasa intent classification confidence $\ge 0.88$, the zero-shot classifier is bypassed completely, reducing NLU stage time to $\approx 35\text{ms}$.
* **Timeout Behavior**: If NLU pipeline does not resolve in 200ms, query falls back to previous turn intent context or routes to `fallback.general_help`.

### 3.2. Knowledge Base Retrieval (RAG) Budget: 200ms
* **Optimization**:
  1. Dense embeddings generated via batched local `all-MiniLM-L6-v2` or cached OpenAI vectors.
  2. Pinecone / ChromaDB queries execute concurrently in parallel with BM25 lexical lookup using `asyncio.gather()`.
  3. If Dense Vector search takes $>120\text{ms}$, reranker stage is automatically bypassed and top lexical chunk is used.
* **Timeout Behavior**: If RAG exceeds 300ms, the agent proceeds without extra chunks and falls back on validated foundational banking disclosures.

### 3.3. LLM Generation Budget: 2,000ms
* **Token Throttling**: Generation is strictly capped at `max_tokens: 250` for standard banking responses. Conciseness is explicitly enforced in the system prompt.
* **Time-to-First-Token (TTFT)**: Target TTFT is $\le 600\text{ms}$. Streaming chunk emitters begin flushing tokens to the client over WebSocket immediately.
* **Circuit Breaker Policy**:
  - Failure condition: 3 consecutive requests exceeding 2,200ms or returning HTTP 429/500.
  - Action: Breaker opens for 60 seconds; traffic routes directly to local backup engine (Llama-3.1-8B-Instruct on NVIDIA L40S cluster with vLLM tensor parallelism, delivering $>120 \text{ tokens/sec}$).

### 3.4. Guardrails & Safety Verification Budget: 100ms
* **Optimization**:
  1. Two-tier guardrail execution:
     - Tier 1 (Synchronous, blocking): Regex policy scan, PII rehydration token mapping, and prohibited phrase dictionary matching ($<20\text{ms}$).
     - Tier 2 (Asynchronous verification): LLM-based hallucination / entailment checks run concurrently or in post-processing for non-financial general inquiries.
* **Timeout Behavior**: If complex guardrail model times out at 150ms, the system defaults to safe mode: injects standard regulatory disclaimer and serves output.

---

## 4. Latency Monitoring, Telemetry & SLA Breach Alerts

All turns are instrumented with OpenTelemetry distributed spans measuring each discrete hop:

```python
# Trace span structure
with tracer.start_as_current_span("nexbank.turn_execution") as root_span:
    with tracer.start_as_current_span("ingress.pii_redaction"): ...
    with tracer.start_as_current_span("nlu.dual_path_classification"): ...
    with tracer.start_as_current_span("state.redis_lookup"): ...
    with tracer.start_as_current_span("rag.hybrid_retrieval"): ...
    with tracer.start_as_current_span("llm.gateway_generation"): ...
    with tracer.start_as_current_span("guardrails.compliance_check"): ...
```

### Prometheus Alerting Rules:
* **Warning Alert**: `nexbank_turn_latency_seconds{quantile="0.90"} > 2.0` for 3 consecutive minutes.
* **Critical SLA Breach**: `nexbank_turn_latency_seconds{quantile="0.99"} > 3.0` for 1 minute (triggers PagerDuty to Conversational AI On-Call).
* **Provider Degradation**: `llm_gateway_latency_seconds{provider="openai", quantile="0.95"} > 1.8` triggers automated traffic shifting to Anthropic or self-hosted cluster.
