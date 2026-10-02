# NexBank Knowledge Base Maintenance & Regulatory Update Procedures

## 1. Executive Summary & Governance Model

To prevent outdated banking policies, ungrounded answers, or regulatory non-compliance from reaching customers, the NexBank Knowledge Base (KB) operates under strict **Continuous Governance**. 

No content modification, rate change, or regulatory disclosure is published to the live RAG vector store without cryptographic verification and dual-approval sign-off. This document establishes:
1. The **Standard Dual-Approval Workflow** (Content Owner + Compliance Officer).
2. The **Fast-Track Emergency Pipeline** for same-day regulatory circulars (RBI, SEBI, IRDAI).
3. **Automated Freshness Monitoring, TTL Expiration, and Zero-Downtime Hot Swapping**.
4. **Instant Version Rollback Mechanisms**.

---

## 2. Standard Dual-Approval Update Workflow (Zero-Downtime)

```mermaid
sequenceDiagram
    autonumber
    actor CO as Content Owner (Product Team)
    participant PORTAL as Knowledge Management Portal
    actor RCO as Risk & Compliance Officer
    participant CI as Automated Validation & Regression CI
    participant REG as Staging KB & Vector Index
    participant PROD as Production Pinecone & Redis Cluster

    CO->>PORTAL: Draft New or Revised KB Item (JSON payload)
    PORTAL->>PORTAL: Validate against KB JSON Schema Draft 2020-12
    PORTAL->>CI: Trigger Automated Regression & Hallucination Check
    CI->>CI: Test 1,200 Golden Question-Answer Pairs against draft
    CI-->>PORTAL: Test Results: 100% Pass
    PORTAL->>RCO: Dispatch Approval Request with Diff View & Circular Reference
    RCO->>RCO: Verify Legal Accuracy, Effective Date & Disclaimers
    RCO->>PORTAL: Sign & Cryptographically Approve (mTLS / PGP)
    PORTAL->>REG: Generate Embeddings (BGE-large / text-embedding-3)
    PORTAL->>PROD: Execute Blue/Green Atomic Vector Index Swap
    PROD-->>PORTAL: Vector Re-indexing Complete (Zero Downtime)
    PORTAL-->>CO: Item Published (Live in < 5 seconds)
```

### 2.1. Dual-Approval Operational Rules
1. **Separation of Duties**: The Content Owner who submits the draft and the Risk & Compliance Officer who signs off must be distinct individuals with verified IAM role permissions (`ROLE_KB_AUTHOR` vs `ROLE_KB_COMPLIANCE_SIGNER`).
2. **Cryptographic Lineage**: The published item records the SHA-256 hash of the content body and the digital signature timestamp of the approving officer.
3. **Automated Schema & Golden Suite Gate**: Any schema error, broken URL citation, or regression in the Golden Test Suite automatically rejects the submission before it reaches the compliance queue.

---

## 3. Fast-Track Emergency Pipeline (RBI / SEBI Statutory Directives)

When a regulator issues an emergency policy directive (e.g. an emergency Repo Rate cut, sanction list addition, or cyber vulnerability alert):

```mermaid
graph LR
    CIRCULAR["Statutory Directive (e.g. RBI Repo Rate Alert)"] --> FAST_INGEST["Fast-Track Emergency Ingest Script"]
    FAST_INGEST --> AUTO_DRAFT["Automated Draft Generator & Diff Formatter"]
    AUTO_DRAFT --> DUAL_EXPEDITE{"Expedited Dual-Sign-Off<br/>(CISO / Head of Compliance)"}
    DUAL_EXPEDITE -->|"Approved (< 15 mins)"| HOT_SWAP["Atomic Hot Swap to Pinecone & Redis Cache"]
    DUAL_EXPEDITE -->|"Rejected"| REVIEW["Standard Review Queue"]
    HOT_SWAP --> FLUSH["Selective Cache Invalidation via Redis Pub/Sub"]
```

### 3.1. Fast-Track SLAs:
* **Detection & Draft Generation**: $\le 10\text{ minutes}$ from circular publication on the regulatory feed.
* **Compliance Sign-Off SLA**: $\le 15\text{ minutes}$ (escalated via priority SMS and PagerDuty to designated On-Call Compliance Officers).
* **Live Deployment & Vector Hot Swap**: $\le 30\text{ seconds}$ across all operational nodes via Redis Pub/Sub cache invalidation.

---

## 4. Automated Freshness Monitoring & TTL Expiration Alerts

Knowledge items are continuously audited by a background Kubernetes cron job (`nexbank-kb-freshness-monitor`) running every 60 minutes:

```mermaid
graph TD
    CRON["Cron Job: Freshness Auditor (Hourly)"] --> SCAN["Scan Active PostgreSQL KB Items"]
    SCAN --> EXPIRY{"Expiry Date <= Current Date + 7 Days?"}
    SCAN --> TTL{"Last Reviewed Date > 90 Days Ago?"}

    EXPIRY -->|"Expiring Soon (T-7 Days)"| WARN_ALERT["Slack Alert to Product Owner: Review Expiry"]
    EXPIRY -->|"Expired (T <= 0)"| AUTO_DEACTIVATE["Auto-Deactivate: Demote from Production Vector Index"]

    TTL -->|"Stale Content (90+ Days)"| STALE_ALERT["Jira Ticket Created: Mandatory Annual Review"]
    AUTO_DEACTIVATE --> PURGE["Purge Redis Cache & Invalidate Embeddings"]
```

### 4.1. Freshness Rules:
1. **Dynamic Rate Sheets**: Interest rate cards have a mandatory maximum TTL of 30 days. If not re-certified by Treasury within 30 days, the item triggers an emergency warning.
2. **Auto-Deactivation**: Once `expiry_date` has passed, the item is automatically excluded from Pinecone and ChromaDB search filters via the active metadata filter clause:
   ```sql
   effective_date <= NOW() AND (expiry_date IS NULL OR expiry_date >= NOW())
   ```
   This ensures that no customer is ever quoted an expired promotional rate, even before physical re-indexing occurs.

---

## 5. Instant Version Rollback Mechanism

If a published knowledge item is found to contain a typographical error or inadvertent policy mistake:

### 5.1. Automated Rollback Protocol
1. **Single-Command Rollback**: Authorized administrators can execute:
   ```bash
   python -m nexbank.kb.manager rollback --item-id "00000001-0000-0000-0000-000000000006" --target-version "2026.09.1"
   ```
2. **Atomic Hot Swap Execution**:
   - The primary PostgreSQL store switches the `status` flag of version `2026.10.1` to `ROLLED_BACK` and restores version `2026.09.1` to `ACTIVE`.
   - Redis emits an invalidation event over the `kb:cache:invalidate` channel.
   - Vector store metadata updates the version filter immediately.
   - Total rollback time: **$< 3.0\text{ seconds}$** with zero conversational session disruption.
