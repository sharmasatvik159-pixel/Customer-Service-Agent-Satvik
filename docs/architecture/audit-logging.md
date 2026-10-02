# NexBank Conversational AI Audit Logging & Statutory Ledger Architecture

```
Document Reference: DOC-ARCH-006
Classification: Confidential - NexBank Information Security & Compliance Architecture
Version: 1.0.0 (Phase 7 / Day 15 Release)
Effective Date: 2026-10-02
Statutory Retention Mandate: 7 Years (2,555 Days per RBI / PMLA Guidelines)
Target Infrastructure: Kafka Streams -> Apache Flink -> PostgreSQL TimescaleDB / AWS WORM S3
```

---

## 1. Compliance Mandate & Architectural Principles

Under the Reserve Bank of India (RBI) Master Directions on Information Technology Governance, Risk, Controls and Statutory Assurance, and the Prevention of Money Laundering Act (PMLA), all conversational transactions and automated advice delivered by AI systems must maintain an **immutable, tamper-evident audit trail**.

### Core Audit Principles
1. **Immutable Write-Once-Read-Many (WORM)**: Audit logs are streamed synchronously to encrypted, append-only cold storage where modification or premature deletion is cryptographically impossible.
2. **Double Encryption for PII**: All conversation payloads undergo field-level envelope encryption (AES-256-GCM) with Hardware Security Module (HSM) keys before database insertion.
3. **Statutory 7-Year Retention**: All interaction records are retained for a minimum of 2,555 days (7 years) to support regulatory inquiries and judicial discovery.
4. **Sub-Second Reconstruction**: Any past conversational session must be completely reconstructible in its exact operational state within 500 milliseconds.

---

## 2. Telemetry Ingestion Architecture

```mermaid
graph TD
    AGENT["AI Dialogue Agent"] -->|Turn Event Payload| BUFFER["Local In-Memory Zero-Copy RingBuffer"]
    BUFFER -->|Batch Flush (100ms)| KAFKA["Kafka Audit Topic (Replication Factor = 3)"]
    
    KAFKA --> FLINK["Apache Flink Stream Processor"]
    
    FLINK -->|Index Telemetry| TIMESCALE["TimescaleDB Hot Store (90 Days Fast Query)"]
    FLINK -->|Field Double-Encryption| HSM["Thales Luna HSM Key Envelope"]
    HSM --> S3_WORM["AWS S3 Glacier WORM (7-Year Immutable Storage)"]
    
    FLINK -->|Anomaly Detection| COMPLIANCE["Real-Time Compliance Alert Engine"]
```

---

## 3. Interaction-Level Audit Log Schema

The **Interaction-Level Log** captures the macroeconomic lifecycle, outcome, and compliance footprint of the entire conversation.

### JSON Schema Specification

```json
{
  "$schema": "https://json-schema.nexbank.internal/v1/interaction-audit-log.json",
  "conversation_id": "CONV-20261002-88412-9901",
  "customer_id_hashed": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "channel": "MOBILE_APP_IOS",
  "client_ip_hashed": "a82b99f1234c",
  "device_fingerprint": "DEV-FP-IOS-18.0.1-A16",
  "session_start_timestamp": "2026-10-02T13:00:12.108Z",
  "session_end_timestamp": "2026-10-02T13:04:45.920Z",
  "duration_seconds": 273.812,
  "turn_count": 6,
  
  "authentication_level": "BIOMETRIC_VERIFIED",
  "auth_method_chain": ["DEVICE_PASSCODE", "FIDO2_FACEID"],
  "auth_token_reference": "AUTH_REF_8812c49a",
  
  "primary_intent": "ACC-001",
  "intent_category": "Account Management",
  "resolution_status": "RESOLVED_FIRST_CONTACT",
  
  "escalated": false,
  "escalation_trigger_id": null,
  "escalation_queue": null,
  
  "guardrails_activated": [
    {
      "guardrail_id": "SEC-RULE-001",
      "rule_name": "Zero Plaintext PII",
      "action_taken": "PII_MASKED"
    },
    {
      "guardrail_id": "SEC-RULE-002",
      "rule_name": "Mandatory Step-Up Authentication",
      "action_taken": "STEP_UP_CHALLENGED_AND_VERIFIED"
    }
  ],
  
  "csat_score": 5,
  "customer_effort_score": 7,
  "net_sentiment_delta": 0.45,
  
  "model_version": "v0.6.0-alpha",
  "prompt_layer_0_hash": "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
  "prompt_layer_1_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4",
  "prompt_layer_2_hash": "8f434346648f6b96df89dda901c5176b10a6d839",
  
  "pii_detected": true,
  "pii_entity_types_redacted": ["BANK_ACCOUNT_NUMBER", "PHONE_NUMBER"],
  
  "compliance_certifications": {
    "rbi_ombudsman_compliant": true,
    "pci_dss_pan_masked": true,
    "financial_advice_zero_breach": true
  },
  
  "retention_policy": {
    "retention_category": "REGULATORY_STATUTORY_7YR",
    "retention_expiration_date": "2033-10-02T13:00:00Z",
    "legal_hold_active": false
  }
}
```

---

## 4. Turn-Level Audit Log Schema

The **Turn-Level Log** captures millisecond-granular telemetry for every round-trip exchange, recording model latencies, intent scores, retrieved knowledge chunks, and guardrail decisions.

### JSON Schema Specification

```json
{
  "$schema": "https://json-schema.nexbank.internal/v1/turn-audit-log.json",
  "turn_id": "TURN-20261002-88412-004",
  "conversation_id": "CONV-20261002-88412-9901",
  "turn_index": 4,
  "speaker": "AGENT",
  "timestamp": "2026-10-02T13:02:15.412Z",
  
  "raw_message_redacted": "Your NexBank Classic Savings Account (ending in 4812) has an available balance of INR 34,850.50 as of today, 02-Oct-2026. Would you like to view recent transactions or download a mini-statement?",
  "encrypted_raw_payload_b64": "ENCRYPTED_AES256GCM_HMAC_ENVELOPE_KEY_HSM_9921...",
  
  "intent_classification": {
    "predicted_intent": "ACC-001",
    "intent_confidence": 0.984,
    "secondary_candidate": "ACC-002",
    "secondary_confidence": 0.012
  },
  
  "entities_extracted": [
    {
      "entity_type": "ACCOUNT_TYPE",
      "value": "SAVINGS",
      "confidence": 0.99
    },
    {
      "entity_type": "ACCOUNT_NUMBER_LAST4",
      "value": "4812",
      "confidence": 1.00
    }
  ],
  
  "sentiment_score": 0.20,
  "sentiment_trajectory_slope": 0.05,
  
  "knowledge_items_retrieved": [
    {
      "item_id": "KB-ACC-BAL-01",
      "similarity_score": 0.912,
      "source_collection": "retail_banking_policy_v4"
    }
  ],
  
  "guardrails_checked": [
    {
      "guardrail_id": "ADV-001",
      "check_name": "Prohibited Financial Advice Classifier",
      "passed": true,
      "latency_ms": 14
    },
    {
      "guardrail_id": "ADV-002",
      "check_name": "PII / PCI Exfiltration Scanner",
      "passed": true,
      "latency_ms": 8
    },
    {
      "guardrail_id": "CANARY-001",
      "check_name": "Canary UUID Token Leakage Interceptor",
      "passed": true,
      "latency_ms": 2
    }
  ],
  
  "execution_latencies": {
    "total_round_trip_ms": 1150,
    "nlu_intent_ms": 84,
    "guardrails_pre_inference_ms": 22,
    "kb_hybrid_retrieval_ms": 142,
    "llm_ttft_ms": 380,
    "llm_generation_ms": 460,
    "guardrails_post_inference_ms": 24,
    "network_egress_ms": 38
  },
  
  "action_taken": "RENDER_BALANCE_AND_OFFER_MINI_STATEMENT",
  "tool_calls_executed": [
    {
      "tool_name": "cbs_balance_inquiry",
      "status": "SUCCESS",
      "upstream_latency_ms": 198
    }
  ]
}
```

---

## 5. Security & Cryptographic Compliance Protocols

### AES-256-GCM Envelope Double-Encryption
1. **Primary Encryption**: Sensitive user utterances containing unmasked parameters undergo local client-side hashing and masking.
2. **Secondary Envelope Encryption**: The raw unredacted text payload is encrypted using a unique Per-Session Data Key (DEK). The DEK is encrypted under a Key Encryption Key (KEK) housed within a **FIPS 140-2 Level 3 Hardware Security Module (Thales Luna HSM)**.
3. **Key Separation of Duties**: The AI application layer *never* holds the master private keys; decryption keys are accessible solely to the designated Internal Bank Auditor role under dual-authorization access.

### TLS 1.3 Strict In-Transit Transport
* All REST, gRPC, and WebSocket streaming hops strictly enforce TLS 1.3 with Ephemeral Diffie-Hellman (ECDHE-RSA-AES256-GCM-SHA384) with mandatory Perfect Forward Secrecy (PFS).

### Quarterly Automated HSM Key Rotation
* HSM master keys automatically rotate every 90 days. Older logs retain decryption envelope metadata pointing to historical key version IDs stored in the HSM vault.

### Role-Based Access Control (RBAC) Audit Matrix

| Role | Interaction Summary | Redacted Conversation | Unredacted PII Raw Logs | Regulatory Export Privilege |
| :--- | :--- | :--- | :--- | :--- |
| **Contact Center Agent** | Yes (Assigned queue) | Yes (Current session) | No | No |
| **QA Supervisor** | Yes | Yes | No | No |
| **Data Science / ML Engineer** | Yes (Anonymized) | Yes (Aggregated) | No | No |
| **Compliance Officer** | Yes | Yes | Yes (Dual-auth required) | Yes |
| **RBI External Auditor** | Yes | Yes | Yes (Statutory warrant) | Yes (Full cryptographic ledger) |

---

## 6. GDPR / DPDP 30-Day Right-to-Deletion Protocol

Under the Digital Personal Data Protection (DPDP) Act and global privacy standards, customers may request deletion of their personal conversational data. However, banking regulations mandate a 7-year audit retention.

### Cryptographic Shredding Solution
1. When a verified customer deletion request is processed:
   * The customer's unique identity mapping key is **cryptographically shredded** from the HSM Identity Vault.
2. **Result**:
   * The underlying conversational transaction record remains in the TimescaleDB ledger for statutory compliance, but is rendered mathematically irreversible and anonymous.
   * All PII association is permanently broken within the statutory 30-day window.

---

## 7. Automated Monthly & Quarterly Regulatory Export Specifications

The audit logging subsystem includes an automated reporting export engine designed to satisfy periodic statutory filings with regulatory bodies (RBI, NPCI, SEBI).

### 1. Monthly RBI Customer Service & Escalation Filing (`RPT-RBI-M-01`)
* **Cadence**: Generated on the 1st of every calendar month at 02:00 IST.
* **Format**: Encrypted XML + signed SHA-256 manifest.
* **Fields Exported**:
  * Total conversational interactions handled.
  * Self-service containment percentage.
  * Count of escalations categorized by trigger code (`ESC-001` through `ESC-015`).
  * SLA adherence rate for P0, P1, and P2 queues.
  * Volume and average resolution turnaround time for unauthorized electronic transactions.

### 2. Quarterly Fraud & Cybersecurity Surveillance Digest (`RPT-RBI-Q-CYBER`)
* **Cadence**: Generated quarterly (Jan 1, Apr 1, Jul 1, Oct 1).
* **Fields Exported**:
  * Count of blocked prompt injection and jailbreak attempts.
  * Total emergency card locks executed (`SEC-001` / `CRD-001`).
  * Total accounts routed for suspected money laundering (`ESC-012`).
  * Confirmation of zero canary token leakage instances.

### 3. SEBI Advisory Compliance Affirmation (`RPT-SEBI-M-04`)
* **Cadence**: Monthly.
* **Fields Exported**:
  * Volume of investment, stock, or mutual fund queries received.
  * Confirmation of 100% refusal diversion script compliance.
  * Count of warm transfers executed to certified SEBI Registered Investment Advisers.
