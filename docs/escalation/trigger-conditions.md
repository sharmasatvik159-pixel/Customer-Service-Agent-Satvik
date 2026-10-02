# NexBank Escalation Trigger Conditions & SLA Matrix

```
Document Reference: DOC-ESC-001
Classification: Confidential - NexBank Internal Architecture
Version: 1.0.0 (Phase 6 / Day 12 Release)
Effective Date: 2026-10-02
Review Cycle: Bi-Weekly Banking Risk & Safety Review
Target Architecture: NexBank Agentic AI Customer Service Platform
```

---

## 1. Executive Summary & Policy Mandate

Escalation from the NexBank Agentic AI Customer Service Agent to human banking professionals is a core architectural feature rather than a system failure. The platform operates under a **Zero-Harm, Fast-Escalation Protocol**: when high-risk transactions, regulatory ambiguities, security threats, emotional distress, or low model confidence are detected, sessions are immediately escalated to specialized banking queues.

### Priority Level Definitions & SLA Standards

| Priority Tier | Description | Maximum Queue Wait Time SLA | Target Queue Routing | Dedicated Channel Mode |
| :--- | :--- | :--- | :--- | :--- |
| **P0 (Emergency)** | Critical security breach, active fraud, AML anomalies, or customer life safety crises. | **$< 2\text{ minutes}$** (Immediate for life safety) | Specialized Security / Fraud / Crisis Desks | Synchronous Live Audio / Screen Takeover |
| **P1 (High)** | High-value retention risks, legal threats, SEBI advisory demands, PEP compliance, high-value disputes. | **$< 5\text{ minutes}$** | Priority Relationship / Compliance / Dispute Desks | Synchronous Video / Live Chat WebSockets |
| **P2 (Operational)** | Repetitive fallbacks, explicit human demands, extended dialogues, or technical core banking outages. | **$< 10\text{ minutes}$** ($< 15\text{ min}$ for supervisors) | General Support / Technical Tier 2 / Supervisor Queue | Synchronous Live Chat / Callback Option |

---

## 2. Mandatory Escalation Trigger Taxonomy (ESC-001 to ESC-015)

The table below formally specifies all 15 mandatory escalation triggers, their detection logic, target queues, and hard service-level agreements.

| Trigger ID | Trigger Name | Priority | Detection Condition / Mathematical Logic | Target Queue | SLA Target | Pre-Transfer Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ESC-001`** | **Confirmed or Suspected Fraud** | **P0** | User reports unauthorized debit, stolen card, SIM swap, phishing credential compromise, or fraud detector classification $> 0.85$. | `FRAUD_INVESTIGATION_DESK` | **$< 2\text{ min}$** | Instantly freeze affected card/channel; emit `SEC-001` alert; zero PII redaction loss. |
| **`ESC-002`** | **Legal Action Threat** | **P1** | Regex / NLU matches legal escalation tokens (*"lawyer"*, *"advocate"*, *"legal notice"*, *"consumer court"*, *"banking ombudsman"*, *"police FIR"*). | `SENIOR_RESOLUTION_MANAGEMENT` | **$< 5\text{ min}$** | Cease automated debate; emit neutral acknowledgment; flag session for legal hold. |
| **`ESC-003`** | **Low Model Confidence** | **P2** | $\text{Confidence}(T_i) < 0.40$ for $k \ge 3$ consecutive turns: $\prod_{i=t-2}^t \mathbb{I}(\text{conf}_i < 0.40) = 1$. | `GENERAL_RETAIL_SUPPORT` | **$< 10\text{ min}$** | Synthesize customer utterances into single-paragraph query summary. |
| **`ESC-004`** | **Persistent Negative Sentiment** | **P1** | Real-time sentiment score $S_i < -0.70$ on $[-1.0, +1.0]$ scale for $k \ge 2$ consecutive turns ($S_t < -0.70 \land S_{t-1} < -0.70$). | `CUSTOMER_RETENTION_TEAM` | **$< 5\text{ min}$** | Issue Empathy-First acknowledgment; prevent canned automated apology loops. |
| **`ESC-005`** | **High-Value Dispute** | **P1** | Disputed transaction amount $A_{\text{dispute}} > \text{INR } 50,000$ (or non-INR equivalent $> \$600\text{ USD}$). | `DISPUTE_RESOLUTION_DESK` | **$< 5\text{ min}$** | Extract Txn ID, RRN, date, and amount; pre-draft dispute ticket in Finacle. |
| **`ESC-006`** | **Frequent Human Agent Requests** | **P2** | User explicitly demands human representative $n \ge 3$ times within a single session ($\sum \mathbb{I}(\text{intent} = \text{HUMAN\_REP}) \ge 3$). | `NEXT_AVAILABLE_AGENT` | **$< 10\text{ min}$** | Immediate warm handover with apology; zero friction or deflection attempts. |
| **`ESC-007`** | **High-Value Account Closure** | **P1** | Account closure intent (`ACC-005`) triggered for customer with Aggregate Relationship Value (ARV) or balance $> \text{INR } 5,00,000$. | `RELATIONSHIP_MANAGER_CONCIERGE` | **$< 5\text{ min}$** | Fetch assigned RM ID; if offline, route to Senior Wealth Retention Desk. |
| **`ESC-008`** | **Regulatory Ambiguity / Dispute** | **P1** | Inquiry citing conflicting regulatory guidelines (RBI master circulars, TDS rules, FATCA status, FEMA cross-border transfer laws). | `COMPLIANCE_HELPDESK` | **$< 10\text{ min}$** | Flag exact statutory clause cited; retrieve relevant circular from vector KB. |
| **`ESC-009`** | **Unauthorized Account Access** | **P0** | Notification of unknown device login, OTP prompt received without customer action, or password changed by unknown third party. | `SECURITY_OPERATIONS_CENTER` | **$< 2\text{ min}$** | Terminate active web/app sessions; lock digital banking credentials; issue SMS alert. |
| **`ESC-010`** | **Extended Unresolved Conversation** | **P2** | Dialogue turn count $T \ge 15$ turns without reaching terminal resolution state ($S_{\text{final}} \ne \text{RESOLVED}$). | `SUPERVISOR_REVIEW_QUEUE` | **$< 15\text{ min}$** | Compile turn progression tree and highlight unresolved entity gaps. |
| **`ESC-011`** | **Self-Harm / Crisis / Emergency** | **P0** | Detection of life safety, suicide, self-harm, or extreme violence keywords/intents. | `CRISIS_RESPONSE_UNIT` | **Immediate ($< 30\text{s}$)** | Render statutory crisis hotline numbers (Vandrevala Foundation, AASRA); notify duty manager. |
| **`ESC-012`** | **AML / Money Laundering Indicators** | **P0** | Structuring patterns mentioned (*"split deposits under 10L"*, *"cash mule"*, *"shell company fund routing"*, *"crypto bypass"*). | `AML_COMPLIANCE_CELL` | **$< 2\text{ min}$** | Silent covert escalation; agent produces benign generic response without alerting user. |
| **`ESC-013`** | **Prohibited Investment Advisory** | **P1** | Customer requests individual stock/mutual fund recommendations, portfolio restructuring, or profit guarantees. | `WEALTH_ADVISORY_DESK` | **$< 10\text{ min}$** | Render mandatory SEBI refusal disclaimer; warm transfer to licensed SEBI advisor. |
| **`ESC-014`** | **Core Data Access Outage** | **P2** | System HTTP 5xx or database timeout from Core Banking System (Finacle / LOS / UPI switch) preventing balance/statement retrieval. | `TECHNICAL_SUPPORT_TIER_2` | **$< 10\text{ min}$** | Capture service API span ID; present downtime notice; log internal PagerDuty alert. |
| **`ESC-015`** | **Politically Exposed Person (PEP)** | **P1** | Customer profile or counterparty identified as PEP or immediate family member of PEP per KYC/AML sanctions database. | `ENHANCED_DUE_DILIGENCE_DESK` | **$< 5\text{ min}$** | Route to AML EDD officer; lock transaction limits to standard ceiling. |

---

## 3. Detailed Specification for Each Trigger Condition

### ESC-001: Confirmed or Suspected Fraud (Priority P0)
* **Trigger Criteria**:
  * Explicit customer statement indicating unauthorized transaction, skimming, card theft, SIM swap, or social engineering fraud.
  * Integration with fraud engine: real-time fraud probability score $> 0.85$.
* **Automated Guardrail Action**:
  * Agent immediately calls `emergency_card_freeze(account_id, reason="FRAUD_REPORTED")`.
  * Generates an incident token `FRD-YYYYMMDD-XXXX`.
* **Routing Path**: Ingress directly to `FRAUD_INVESTIGATION_DESK`.
* **SLA**: Maximum wait time 120 seconds. If queue is full, voice override automatically calls out to customer registered mobile.

### ESC-002: Legal Action Threat (Priority P1)
* **Trigger Criteria**:
  * Detection of legal recourse threats, retaining counsel, filing consumer forum cases, or invoking RBI Ombudsman with hostility.
  * Regex patterns: `(?i)(file.*lawsuit|see.*in.*court|legal.*notice|advocate.*notice|consumer.*forum|police.*complaint|rbi.*ombudsman.*complaint)`.
* **Tone & Guardrail Rules**:
  * The agent must *never* argue, admit legal liability, or debate bank policies.
  * Agent delivers neutral, respectful acknowledgment: *"We take your concerns with utmost seriousness. I am connecting you directly with our Senior Resolution Management team who have the authority to address this matter."*
* **Routing Path**: `SENIOR_RESOLUTION_MANAGEMENT`.
* **SLA**: Maximum wait time 300 seconds.

### ESC-003: Low Model Confidence (Priority P2)
* **Trigger Criteria**:
  * Three consecutive user turns where top intent confidence is strictly below 0.40 ($\text{conf} < 0.40$).
  * Prevents conversational "infinite loops" where the agent repeatedly asks vague clarifying questions.
* **Routing Path**: `GENERAL_RETAIL_SUPPORT`.
* **SLA**: Maximum wait time 600 seconds.

### ESC-004: Persistent Negative Sentiment (Priority P1)
* **Trigger Criteria**:
  * Two consecutive turns with sentiment score $S \le -0.70$ on the normalized $[-1.0, +1.0]$ VADER / RoBERTa-sentiment scale.
  * Common lexical cues: *"useless bot"*, *"worst bank ever"*, *"you are robbing me"*, *"stop giving me robotic answers"*.
* **Routing Path**: `CUSTOMER_RETENTION_TEAM`.
* **SLA**: Maximum wait time 300 seconds.

### ESC-005: High-Value Dispute (Priority P1)
* **Trigger Criteria**:
  * Transaction dispute request (`TXN-002`) where disputed principal $> \text{INR } 50,000$.
  * Self-service dispute filing is constrained to $\le \text{INR } 50,000$ to mitigate unauthorized chargeback claims.
* **Routing Path**: `DISPUTE_RESOLUTION_DESK`.
* **SLA**: Maximum wait time 300 seconds.

### ESC-006: Frequent Human Agent Requests (Priority P2)
* **Trigger Criteria**:
  * Customer submits 3 explicit requests for human assistance in the same conversation.
  * The agent must not attempt a 3rd deflection or rebuttal.
* **Routing Path**: `NEXT_AVAILABLE_AGENT`.
* **SLA**: Maximum wait time 600 seconds.

### ESC-007: High-Value Account Closure (Priority P1)
* **Trigger Criteria**:
  * Customer initiates account closure intent `ACC-005` or deposit liquidation `DEP-004` and customer total balance or relationship value $\ge \text{INR } 5,00,000$.
* **Routing Path**: `RELATIONSHIP_MANAGER_CONCIERGE`.
* **SLA**: Maximum wait time 300 seconds.

### ESC-008: Regulatory Ambiguity / Dispute (Priority P1)
* **Trigger Criteria**:
  * Complex regulatory queries involving contradictory legal interpretations (e.g., FEMA NRI remittance taxation, inheritance succession certificates without a registered nominee).
* **Routing Path**: `COMPLIANCE_HELPDESK`.
* **SLA**: Maximum wait time 600 seconds.

### ESC-009: Unauthorized Account Access (Priority P0)
* **Trigger Criteria**:
  * Customer reports unsolicited SMS OTPs, unexpected login alerts from unfamiliar IP addresses, or device credential compromise.
* **Automated Guardrail Action**:
  * Immediately invoke `invalidate_all_sessions(customer_id)`.
  * Require out-of-band biometric or in-branch verification.
* **Routing Path**: `SECURITY_OPERATIONS_CENTER`.
* **SLA**: Maximum wait time 120 seconds.

### ESC-010: Extended Unresolved Conversation (Priority P2)
* **Trigger Criteria**:
  * Conversation reaches turn 15 without a confirmed resolution or closed intent state.
  * Identifies cases where user and agent are stuck in polite but circular exchanges.
* **Routing Path**: `SUPERVISOR_REVIEW_QUEUE`.
* **SLA**: Maximum wait time 900 seconds.

### ESC-011: Self-Harm / Crisis / Life Safety (Priority P0)
* **Trigger Criteria**:
  * Mention of suicide, self-harm, severe clinical depression, domestic violence, or hostage/kidnapping emergency.
* **Immediate Response**:
  * Renders standardized crisis helplines immediately in UI (KIRAN 1800-599-0019, Vandrevala 9999 666 555, Police 112).
  * Simultaneously pages the bank's On-Duty Crisis Response Manager.
* **Routing Path**: `CRISIS_RESPONSE_UNIT`.
* **SLA**: Immediate ($< 30\text{ seconds}$).

### ESC-012: Potential Money Laundering / AML (Priority P0)
* **Trigger Criteria**:
  * Detection of structuring queries (how to deposit cash without PAN reporting under Section 285BA), cryptocurrency illicit off-ramping, or nominee fronting for shell entities.
* **Covert Operation Mode**:
  * In compliance with PMLA (Prevention of Money Laundering Act), the agent *must not "tip off" the customer*.
  * The agent responds with standard regulatory cash thresholds and silently dispatches a high-priority AML alert.
* **Routing Path**: `AML_COMPLIANCE_CELL`.
* **SLA**: Maximum wait time 120 seconds (covert review).

### ESC-013: Prohibited Investment Advisory (Priority P1)
* **Trigger Criteria**:
  * Customer demands specific equity, mutual fund, crypto, or derivative recommendations, or asks the agent to evaluate external investment portfolios.
* **Guardrail Enforcement**:
  * Agent cites SEBI Investment Advisers Regulations (2013) prohibiting automated non-certified advice.
  * Offers transfer to a registered NexBank Wealth Advisory professional.
* **Routing Path**: `WEALTH_ADVISORY_DESK`.
* **SLA**: Maximum wait time 600 seconds.

### ESC-014: Core Data Access Outage (Priority P2)
* **Trigger Criteria**:
  * Downstream API failure (Finacle CBS, Card Switch, UPI NPCI Gateway) returning 500, 502, 503, or connection timeouts after 2 retries.
* **Routing Path**: `TECHNICAL_SUPPORT_TIER_2`.
* **SLA**: Maximum wait time 600 seconds.

### ESC-015: Politically Exposed Person (PEP) Detected (Priority P1)
* **Trigger Criteria**:
  * Customer or declared beneficial owner matches PEP registry during onboarding, KYC update (`ACC-004`), or loan origination.
* **Routing Path**: `ENHANCED_DUE_DILIGENCE_DESK`.
* **SLA**: Maximum wait time 300 seconds.

---

## 4. Deduplication & Escalation Cooldown Rules

1. **Anti-Flapping Cooldown**:
   * Once an escalation condition is evaluated and placed into a queue, identical triggers occurring within 60 seconds are suppressed and appended as supplemental telemetry to the active ticket.
2. **Priority Monotonicity**:
   * A session's priority can only *increase* (e.g., $P2 \to P1 \to P0$). An active P0 or P1 session can never be downgraded to P2 by subsequent user utterances.
3. **Multi-Trigger Precedence**:
   * If a single turn triggers both `ESC-001` (Fraud, P0) and `ESC-004` (Sentiment, P1), the higher priority trigger (`P0`) governs queue routing, and both trigger IDs are recorded in the Context Package.
