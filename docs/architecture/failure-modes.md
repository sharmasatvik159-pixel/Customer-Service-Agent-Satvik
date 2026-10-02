# NexBank Agentic AI Customer Service: Failure Modes and Effects Analysis (FMEA) & Graceful Degradation Policies

## 1. Executive Summary & FMEA Methodology

In mission-critical banking environments, silent failures, unhandled exceptions, and ungrounded model outputs present severe regulatory, financial, and reputational risks. The NexBank Conversational AI architecture enforces **Fault Tolerance by Design**, guaranteeing that no single component outage causes conversational collapse or data exposure.

Each potential failure is analyzed using standard Failure Modes and Effects Analysis (FMEA) metrics:
* **Severity (S)**: 1 (Minor inconvenience) to 5 (Critical regulatory breach or data loss).
* **Occurrence (O)**: 1 (Extremely rare) to 5 (Frequent / Expected under load).
* **Detection (D)**: 1 (Immediately detected via synthetic health checks) to 5 (Undetected / Silent).
* **Risk Priority Number (RPN)**: Calculated as $\text{RPN} = S \times O \times D$. Items with $\text{RPN} \ge 30$ mandate automated failover and runbook automation.

---

## 2. Failure Mode Analysis (FMEA) Matrix

| Component / Subsystem | Failure Mode | Impact Description | S | O | D | RPN | Mitigation & Degradation Policy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ingress & WAF** | Distributed DDoS or burst beyond rate limits | API Gateway saturated; valid customers get HTTP 429 | 4 | 3 | 1 | **12** | Cloudflare/Envoy Token Bucket rate limiting per IP/User; priority queueing for authenticated users. |
| **PII Redaction Engine** | Presidio service crash or latency spike (>100ms) | Sensitive PAN/SSN data risks leaking to downstream LLM | 5 | 2 | 2 | **20** | Synchronous fallback to compiled high-speed deterministic regex bank. If regex engine also fails, reject utterance with safe error code `SEC_002`. |
| **NLU Intent Pipeline** | Intent classification confidence below threshold ($<0.65$) | Agent misunderstands customer intent; gives wrong flow | 3 | 4 | 2 | **24** | Two-tier disambiguation protocol: present top-2 likely options. If user rejects both, escalate gracefully to general support. |
| **Session State (Redis)** | Redis Cluster node failure / network partition | Inability to read or persist ongoing conversation state | 4 | 2 | 2 | **16** | Redis Sentinel / Multi-AZ failover. Local in-memory worker fallback for ongoing turn; asynchronous state reconciliation via PostgreSQL primary store. |
| **Vector DB (Pinecone/Chroma)** | Vector store outage or query timeout (>300ms) | RAG knowledge lookup fails; cannot retrieve banking policies | 3 | 2 | 2 | **12** | Fallback to PostgreSQL lexical full-text search (`tsvector` with BM25 ranking). If both fail, serve approved static disclaimers and offer live agent. |
| **Primary LLM Provider** | API outage, rate limiting (HTTP 429), or 5xx response | Generation engine blocked; response times exceed 3.0s | 5 | 3 | 1 | **15** | Automated circuit breaker trips after 2 failures. Instantly redirects traffic to secondary cloud provider (Anthropic) or private on-prem Llama 3.1 8B cluster. |
| **Core Banking API** | Core banking service timeout during transfer or payment | Potential duplicate transaction or unresolved debit state | 5 | 2 | 1 | **10** | Strict idempotency keys on every transaction call. Two-phase commit via Temporal Sagas. If state is indeterminate, trigger automatic transaction hold and alert Fraud Desk. |
| **Safety Guardrails** | Hallucination detected or financial advice rule breached | LLM proposes unverified policy or forbidden investment advice | 5 | 2 | 1 | **10** | Output is intercepted and suppressed before reaching client. Replaced with pre-approved canned compliance response: *"I cannot offer financial advice..."* |
| **Live Escalation (CRM)** | CRM escalation webhook down or live queues full (>180s) | Customer stranded when requesting human banker | 4 | 3 | 1 | **12** | Asynchronous callback ticket generated in PostgreSQL with guaranteed customer SMS notification and callback SLA. |

---

## 3. Detailed Graceful Degradation Protocols

### 3.1. Policy 1: PII Protection Degradation (Fail-Closed)
* **Principle**: The platform operates on a **Fail-Closed** principle regarding customer PII and PCI-DSS data.
* **Execution**:
  1. Primary: Presidio Analyzer + Anonymizer.
  2. Fallback Tier 1: Local compiled regex rules targeting Credit Cards (Luhn algorithm verified), SSN (9 digits), US Phone numbers, and Email addresses.
  3. Failure Escalation: If both engines fail to return within 80ms, the turn is immediately aborted. The user receives:
     > *"We are currently experiencing technical difficulties processing your message securely. For your security, this interaction has been paused. Please contact customer support directly at 1-800-NEXBANK."*
  4. An encrypted error event is emitted to the security monitoring queue with high priority.

### 3.2. Policy 2: NLU Intent Disambiguation & Fallback Loop Breaker
* **Principle**: Prevent circular conversations where the agent repeatedly asks *"I didn't understand that, can you rephrase?"*
* **Execution**:
  1. **Turn 1 Unrecognized**: Confidence $<0.65$. Agent offers top-2 matched intents as interactive quick-reply buttons:
     > *"To make sure I assist you correctly, are you looking to check your balance or report a lost card?"*
  2. **Turn 2 Unrecognized**: If the customer response still yields $<0.65$ or user types *"Neither"*:
     > *"I want to ensure you get the exact help you need without delay. Let me connect you directly to a banking specialist who can assist."*
  3. System triggers seamless live agent handover; `consecutive_fallback_count` never exceeds 2.

### 3.3. Policy 3: LLM Provider Outage & Redundancy Hierarchy
* **Principle**: Zero customer-facing downtime during public cloud LLM outages.
* **Failover Hierarchy**:
  ```
  [Tier 1: OpenAI GPT-4o-mini] (Primary)
          │  (Timeout > 2.0s or 2 consecutive 5xx/429)
          ▼
  [Tier 2: Anthropic Claude 3.5 Sonnet] (Secondary Cloud)
          │  (Timeout > 2.0s or HTTP failure)
          ▼
  [Tier 3: Local Private Kubernetes vLLM (Llama 3.1 8B)] (On-Prem / Private VPC)
          │  (Cluster unreachable)
          ▼
  [Tier 4: Deterministic Canned Rule-Engine] (Emergency Fallback)
  ```
* Recovery: Circuit breaker tests primary Tier 1 with single synthetic heartbeat request every 30 seconds. When Tier 1 responds successfully twice consecutively, traffic returns to primary.

### 3.4. Policy 4: Core Banking Tool Idempotency & Saga Compensation
* **Principle**: Guarantee zero duplicate debits or unhandled financial mutations under network failure.
* **Execution**:
  1. Every mutating tool call (e.g., `initiate_domestic_transfer`) receives a deterministic idempotency key derived from:
     $$\text{IdempotencyKey} = \text{SHA256}(\text{session\_id} + \text{turn\_index} + \text{customer\_id} + \text{transaction\_amount})$$
  2. Calls are executed within a **Temporal.io Workflow Saga**.
  3. If the Core Banking API times out after sending the request:
     - The agent does **not** retry blindly.
     - Temporal initiates a status inquiry using the `idempotency_key`.
     - If status is `CONFIRMED`, transaction succeeds.
     - If status is `UNKNOWN`, the transaction is placed into `PENDING_INVESTIGATION`, the customer is notified with a reference number, and a Banker task is created in CRM.

### 3.5. Policy 5: CRM Escalation Queue Saturation
* **Principle**: Never leave a frustrated or urgent customer hanging in an infinite queue.
* **Execution**:
  1. When escalation occurs, the orchestrator queries CRM live agent queue depth.
  2. If estimated wait time $< 120$ seconds: Connect to live chat WebSocket.
  3. If estimated wait time $\ge 120$ seconds or outside business hours:
     > *"All of our banking specialists are currently assisting other customers. Your current wait time is approximately {wait_minutes} minutes. Would you like to keep waiting, or may we schedule a priority callback to your verified phone number (ending in {last_4}) within 15 minutes?"*
  4. If user accepts callback, Temporal schedules an automated dialer task with full context package pre-loaded.
