# NexBank Safety Invariant Preservation & Continuous Learning Governance

## 1. Executive Summary & Safety Invariant Philosophy

Continuous learning introduces the acute risk of **Catastrophic Forgetting**, **Alignment Drift**, or **Data Poisoning**, wherein an updated model solves novel colloquial phrasings but inadvertently regresses on compliance boundaries, drops required disclaimers, or exhibits security vulnerabilities.

To prevent any compromise of banking integrity, the NexBank platform enforces:
1. **The Immutable Safety Layer (Layers 0–2)**: Cryptographically pinned system prompt and guardrail code that cannot be altered by fine-tuning, RLHF, or active learning updates.
2. **The Fixed Golden Safety Benchmark Test Suite (200+ Cases)**: Mandating a **100% pass rate** before any candidate model can be promoted to canary deployment.
3. **Four-Stage Gradual Canary Deployment ($1\% \to 5\% \to 25\% \to 100\%$)**: Governed by real-time Kolmogorov-Smirnov drift testing and automated sub-3.0s circuit breaker rollbacks.

---

## 2. The Immutable Safety Architecture (Layers 0–2)

The system prompt and operational orchestrator are architected into hierarchical layers. Layers 0 through 2 are **Hard-Pinned and Read-Only**:

```
+===================================================================================================+
| LAYER 0: IMMUTABLE PERIMETER POLICY (HARDCODED IN C/RUST GATEWAY - ZERO OVERRIDE)                 |
| - Hard rate limiting (10 req/10s)                                                                 |
| - Input payload boundary cap (1,000 characters maximum)                                           |
| - Deterministic Luhn & Verhoeff PAN/Aadhaar scrubbing into cryptographic surrogate tokens          |
+===================================================================================================+
| LAYER 1: REGULATORY & COMPLIANCE GUARDRAIL KERNEL (COMPILED DETERMINISTIC PYTHON - READ ONLY)     |
| - SEBI / FINRA Financial Advice Interceptor (Templates A, B, C)                                   |
| - PCI DSS v4.0 Zero-Display enforcement & secret non-echo                                         |
| - Absolute cross-customer multi-tenant isolation filters (`WHERE customer_id = :session_id`)       |
| - 5-Minute Inactivity Session Expiry Controller                                                   |
+===================================================================================================+
| LAYER 2: IMMUTABLE SYSTEM PROMPT ANCHORS (PINNED & CHECKSUMMED - CANNOT BE TUNED OUT)            |
| - Bank Identity Persona: "You are the NexBank AI Assistant, an informational and operational..."  |
| - Statutory XML Boundary Isolation: `<system_boundary>` and `<untrusted_user_input>`               |
| - Prohibition of Autonomous Debits: Out-of-band customer biometric signing mandatory              |
| - Dynamic 128-bit UUID Canary Token monitoring                                                    |
+===================================================================================================+
| LAYER 3: DYNAMIC RETRIEVAL & FEW-SHOT ADAPTATION (UPDATED VIA CONTINUOUS PIPELINE)                 |
| - Verified RAG Knowledge Base Chunks (Pinecone / PostgreSQL)                                      |
| - Supervised In-Context Few-Shot Exemplars (Curated via Active Learning)                          |
| - Domain-Specific Vocabulary & Synonyms                                                           |
+===================================================================================================+
| LAYER 4: CANDIDATE TUNABLE WEIGHTS (FINE-TUNED VIA DVC ACTIVE LEARNING CORPS)                      |
| - Intent Classification Head (Rasa DIET / Modern Small LLM)                                      |
| - Tokenizer & Named Entity Normalizer                                                             |
+===================================================================================================+
```

### 2.1. Cryptographic Invariant Enforcement
* The code and prompt text for Layers 0, 1, and 2 are hashed via SHA-256 (`INVARIANT_POLICY_HASH`).
* At container startup and prior to each inference call, the orchestrator computes the hash of the active prompt kernel. If the hash deviates from the signed production manifest, the runtime throws a `SecurityInvariantViolationException` and refuses to initialize.

---

## 3. The Fixed Golden Safety Benchmark Test Suite (200+ Cases)

Prior to promoting any updated model, prompt configuration, or NLU pipeline from staging to production canary, the candidate artifact must pass the **Golden Safety Regression Test Suite**:

```mermaid
graph TD
    CANDIDATE["Candidate Model / Prompt Artifact (vN+1)"] --> TEST_RUNNER["Automated CI/CD Safety Test Runner"]

    subgraph Golden Safety Suite (200+ Mandatory Cases)
        TC_FIN["Financial Advice Boundaries (60 Cases)"]
        TC_PII["PII/PCI Credential Defense (50 Cases)"]
        TC_INJ["Prompt Injection & Jailbreak Defense (50 Cases)"]
        TC_AUTH["Step-Up Auth & Cross-Customer Isolation (40 Cases)"]
    end

    TEST_RUNNER --> TC_FIN
    TEST_RUNNER --> TC_PII
    TEST_RUNNER --> TC_INJ
    TEST_RUNNER --> TC_AUTH

    TC_FIN --> PASS_EVAL{"Pass Rate = 100.0% ?"}
    TC_PII --> PASS_EVAL
    TC_INJ --> PASS_EVAL
    TC_AUTH --> PASS_EVAL

    PASS_EVAL -->|"100% Pass (0 Regressions)"| PROMOTE["Authorize Canary Deployment Stage 1 (1%)"]
    PASS_EVAL -->|"< 100% (Even 1 Failure)"| REJECT["Immediate CI Build Termination & Alert"]
```

### 3.1. Test Suite Composition & Strict Zero-Tolerance Thresholds

| Test Suite Category | Minimum Case Count | Target Pass Rate | Permitted Regressions | Description & Key Assertions |
| :--- | :--- | :--- | :--- | :--- |
| **Financial Advice Boundaries** | **60 Cases** | **100.0%** | **0** | Tests stock recommendations, crypto advice, return guarantees, tax avoidance, and loan approval promises. Must trigger canned refusal and wealth referral. |
| **PII & Credential Defense** | **50 Cases** | **100.0%** | **0** | Tests raw credit card PANs, Aadhaar numbers, CVVs, passwords, and OTP disclosure. Must scrub credentials and issue security warnings. |
| **Prompt Injections & Jailbreaks** | **50 Cases** | **100.0%** | **0** | Tests DAN framing, Base64 ciphers, hypothetical novels, delimiter escapes, and system prompt exfiltration. Zero canary token leakage permitted. |
| **Step-Up Auth & Cross-Customer Data** | **40 Cases** | **100.0%** | **0** | Tests spousal inquiries, unauthenticated card unfreezing, and profile modification without biometric signing. Must enforce auth barriers. |
| **Core Intent & Entity Accuracy** | **150 Cases** | $\ge 98.5\%$ | $\le 2$ | Tests core banking operational intents (balance, transfers, disputes, card locks) for semantic stability. |
| **Grounded Faithfulness (RAG)** | **100 Cases** | $\ge 99.0\%$ | $\le 1$ | Tests NLI contradiction scores against verified policy chunks; zero fabricated numbers permitted. |

---

## 4. Four-Stage Gradual Canary Deployment Strategy

Model rollouts progress through four sequential traffic stages with automated health telemetry evaluation:

```
[Stage 1: 1% Traffic]  ----(12 Hours Stable, p-val > 0.05)----> [Stage 2: 5% Traffic]
         │                                                               │
(Alert Spike / KS Drift)                                        (Alert Spike / KS Drift)
         │                                                               │
         ▼                                                               ▼
[Instant 3s Rollback]                                           [Instant 3s Rollback]
         ▲                                                               ▲
         │                                                               │
[Stage 4: 100% Traffic] <--(24 Hours Stable, p-val > 0.05)---- [Stage 3: 25% Traffic]
```

### 4.1. Stage Progression Schedule & Minimum Observation Windows
1. **Stage 1 (1% Production Traffic - Shadow & Canary)**:
   - Minimum Duration: 12 hours (minimum 2,000 completed turns).
   - Target Audience: Low-risk retail inquiries (branch hours, FAQs, balance inquiries).
   - Gate: Zero security guardrail exceptions; latency within SLA.
2. **Stage 2 (5% Production Traffic)**:
   - Minimum Duration: 24 hours (minimum 10,000 completed turns).
   - Expands to transactional flows (card locks, statement requests).
   - Gate: CSAT non-inferiority ($p < 0.05$); fallback rate stable ($\le 8\%$).
3. **Stage 3 (25% Production Traffic)**:
   - Minimum Duration: 48 hours (minimum 50,000 completed turns).
   - Full omnichannel routing across Web and Mobile apps.
   - Gate: Kolmogorov-Smirnov drift test confirms output distribution stability.
4. **Stage 4 (100% Full Production Rollout)**:
   - Full fleet promotion. Prior model version kept in hot-standby for 7 days.

---

## 5. Automated Statistical Drift Detection & Real-Time Circuit Breakers

### 5.1. Kolmogorov-Smirnov (KS) Output Drift Test
The continuous evaluation engine compares the embedding and token length distribution of the candidate model against the baseline production model on identical query clusters.

Using the two-sample **Kolmogorov-Smirnov Test**:
$$D = \sup_x |F_{\text{candidate}}(x) - F_{\text{baseline}}(x)|$$
* If the $p$-value of the KS test drops below $0.05$ ($p < 0.05$), an anomalous statistical shift in response length, vocabulary entropy, or sentiment variance is detected.
* Automated Action: Halts canary stage progression; flags the deployment for human review.

### 5.2. Real-Time Circuit Breakers & Sub-3.0s Automated Rollbacks
The deployment controller continuously ingests Prometheus metrics from the canary pods. The circuit breaker **instantly trips** if any of the following conditions are met:

```python
# Real-Time Canary Health Circuit Breaker Rules
CIRCUIT_BREAKER_TRIGGERS = {
    # 1. Any safety failure trips the breaker immediately
    "canary_token_leakage_count": {"operator": ">", "threshold": 0},
    "pii_leakage_detected_count": {"operator": ">", "threshold": 0},
    
    # 2. Quality degradations evaluated over rolling 5-minute window
    "escalation_rate_surge": {"operator": ">", "threshold": 1.25}, # 25% surge over baseline
    "negative_sentiment_surge": {"operator": ">", "threshold": 1.20}, # 20% surge over baseline
    "p99_latency_ms": {"operator": ">", "threshold": 3000}, # SLA breach
    "http_5xx_error_rate_pct": {"operator": ">", "threshold": 1.0} # 1% error rate
}
```

### 5.3. Sub-3.0s Automated Rollback Execution
When the circuit breaker trips:
1. **Envoy / API Gateway Traffic Shift**: The ingress routing weight for the candidate model is updated from $N\%$ to $0\%$ via Kubernetes Service Mesh (Istio / Envoy VirtualService) within **$< 1.5\text{ seconds}$**.
2. **Session Drain**: In-flight active turns fail over to the stable baseline model instance using the serialized Redis dialogue state.
3. **Automated Incident Logging**: Creates an emergency SEV-1 incident ticket in Jira and notifies the on-call team via PagerDuty with the triggering telemetry snapshot.
4. Total elapsed rollback time: **$< 3.0\text{ seconds}$** with zero downtime or user session disconnection.
