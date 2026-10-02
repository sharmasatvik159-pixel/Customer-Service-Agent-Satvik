# NexBank Disambiguation Trees, Multi-Intent Handling & Fallback Policies

## 1. Disambiguation Framework

When a customer utterance displays semantic overlap between two closely related banking concepts, or when the NLU confidence margin between the top two intent candidates is narrow ($\Delta \le 0.15$ with confidence $0.65 \le c < 0.88$), deterministic disambiguation trees are invoked.

This document details decision trees for the 6 critical overlapping intent pairs, multi-intent decomposition protocols, out-of-scope (OOS) classification, and progressive fallback routines.

---

## 2. Decision Trees for the 6 Overlapping Intent Pairs

### 2.1. Pair 1: `TXN-001` vs `TXN-002` (Status Check vs. Dispute)
* **Semantic Ambiguity**: Utterance mentions a transaction problem (e.g., *"My transfer of 5000 to John is stuck and money got cut"*).
* **Core Distinction**:
  - `TXN-001`: Inquires whether the transfer is pending, successful, or scheduled for clearing.
  - `TXN-002`: Alleges wrong debit, merchant overcharge, or demands a formal chargeback.

```mermaid
graph TD
    IN1["Customer: 'My payment of 5000 is stuck / debited'"] --> Q1{"Did the customer authorize this transaction, and what is the current need?"}
    Q1 -->|"Check if money reached payee / clear status"| PATH_A["Route: TXN-001 (Transaction Status Enquiry)"]
    Q1 -->|"Merchant refused delivery / duplicate debit / file claim"| PATH_B["Route: TXN-002 (Raise Transaction Dispute)"]

    PATH_A --> RESP_A["Prompt: 'I can check the live clearing status of this transfer for you.'"]
    PATH_B --> RESP_B["Prompt: 'I can help you file a formal dispute to recover your funds.'"]
```

* **Disambiguation Prompt**:
  > *"I can help you with this transaction. Would you like me to:*
  > *1. [Check Transfer Status] (See if the transfer is still processing or reversed)*
  > *2. [Raise a Formal Dispute] (Report duplicate debit or unfulfilled merchant service)*

---

### 2.2. Pair 2: `PRD-001` vs `PRD-005` (Information vs. Investment Advisory)
* **Semantic Ambiguity**: Utterance mentions returns, products, or yields (e.g., *"Where should I put my money for best returns?"* vs *"What are your savings account interest rates?"*).
* **Core Distinction**:
  - `PRD-001`: Factual retrieval of bank interest rates, terms, and features (RAG-compliant).
  - `PRD-005`: Request for tailored portfolio allocation or forward-looking investment picks (Prohibited by regulatory guardrails; must refer to human advisor).

```mermaid
graph TD
    IN2["Customer: 'How should I invest / what returns can I get?'"] --> Q2{"Is customer asking for factual bank product terms, or tailored wealth advice?"}
    Q2 -->|"Factual interest rates / FD / RD / Account terms"| PATH_PRD1["Route: PRD-001 (General Product Information)"]
    Q2 -->|"Tailored advice / stock picks / mutual fund portfolio recommendation"| PATH_PRD5["Route: PRD-005 (Investment Advisory Request)"]

    PATH_PRD1 --> R_PRD1["Fetch verified rate sheets from RAG Knowledge Base"]
    PATH_PRD5 --> R_PRD5["Activate Financial Advice Guardrail -> Canned Disclaimer -> Human Wealth Specialist Referral"]
```

* **Disambiguation Prompt**:
  > *"I can provide details on NexBank's guaranteed deposit rates, or connect you with a certified wealth advisor for personalized investment planning:*
  > *1. [View NexBank FD/Savings Rates] (Factual rates and yield calculators)*
  > *2. [Consult a Wealth Advisor] (Personalized portfolio and investment guidance)*

---

### 2.3. Pair 3: `ACC-003` vs `ACC-004` (Contact vs. Address Update)
* **Semantic Ambiguity**: Utterance mentions updating personal profile or KYC info (e.g., *"I moved and need to update my details"* or *"Change my phone and address"*).
* **Core Distinction**:
  - `ACC-003`: Digital contact vectors (Mobile Number, Email Address). Requires Dual-OTP step-up authentication.
  - `ACC-004`: Physical residential / correspondence postal address. Requires Full KYC documentation (Aadhaar OTP / Passport / OVD proof).

```mermaid
graph TD
    IN3["Customer: 'Update my profile / details'"] --> Q3{"Which specific details need updating?"}
    Q3 -->|"Mobile Number or Email Address"| PATH_ACC3["Route: ACC-003 (Contact Update) -> Requires Dual OTP"]
    Q3 -->|"Mailing / Residential Postal Address"| PATH_ACC4["Route: ACC-004 (Address Update) -> Requires Full KYC Proof"]
    Q3 -->|"Both Phone & Address"| PATH_BOTH["Decompose into Multi-Intent Sequence (ACC-003 then ACC-004)"]
```

* **Disambiguation Prompt**:
  > *"Which contact or profile details would you like to update?*
  > *1. [Mobile Number or Email] (Fast verification via dual OTP)*
  > *2. [Residential Postal Address] (Requires valid address proof or Aadhaar OTP)*
  > *3. [Both]"*

---

### 2.4. Pair 4: `CMP-001` vs `CMP-003` (New Complaint vs. Escalation)
* **Semantic Ambiguity**: Utterance expresses strong dissatisfaction about an existing problem (e.g., *"No one solved my problem, this service is terrible, escalate this!"*).
* **Core Distinction**:
  - `CMP-001`: Registering a new grievance regarding branch, staff, charges, or app errors (generates new ticket).
  - `CMP-003`: Escalating an already registered grievance that has breached SLA or was resolved unsatisfactorily (escalates to Principal Nodal Officer).

```mermaid
graph TD
    IN4["Customer: 'Nobody helped me with my issue, take this to higher management!'"] --> Q4{"Does customer have an existing complaint ticket number?"}
    Q4 -->|"Yes (Ticket ID provided or found in active records)"| PATH_CMP3["Route: CMP-003 (Escalate Existing Complaint) -> Nodal Officer"]
    Q4 -->|"No (First time reporting this issue)"| PATH_CMP1["Route: CMP-001 (Register New Complaint) -> Standard Grievance SLA"]
    Q4 -->|"Unsure / Can't remember"| CHECK_REC["Search recent closed/open tickets for user -> Prompt customer"]
```

* **Disambiguation Prompt**:
  > *"I am very sorry for this experience. To make sure your issue is directed to the right team:*
  > *1. [Escalate an Existing Ticket] (I have an unresolved complaint reference number)*
  > *2. [Register a New Formal Complaint] (Log a new grievance with our customer care team)*

---

### 2.5. Pair 5: `SEC-001` vs `TXN-002` (Fraud Report vs. Merchant Dispute)
* **Semantic Ambiguity**: Utterance reports money debited from account or card (e.g., *"Money was taken from my card for a transaction I don't agree with"*).
* **Core Distinction**:
  - `SEC-001`: Unauthorized third-party fraud, phishing, stolen card credentials, or cyber compromise (Immediate card lock + fraud ticket).
  - `TXN-002`: Legitimate merchant transaction where customer authorized payment, but merchant failed to deliver, charged twice, or refused refund.

```mermaid
graph TD
    IN5["Customer: 'There is an unauthorized / bad charge on my card'"] --> Q5{"Did YOU participate in or authorize this transaction, or is it unknown third-party fraud?"}
    Q5 -->|"Unknown charge / Never heard of merchant / Stolen card"| PATH_SEC1["Route: SEC-001 (Report Fraud) -> Immediate Freeze + Cyber Incident"]
    Q5 -->|"I bought this, but charged twice / canceled order / merchant issue"| PATH_TXN2["Route: TXN-002 (Merchant Dispute) -> Chargeback Claim"]
```

* **Disambiguation Prompt**:
  > *"This sounds important. To take the correct security action immediately:*
  > *1. [Report Fraud / Unrecognized Charge] (You did NOT make this purchase; potential card compromise. We will freeze your card immediately)*
  > *2. [Dispute a Merchant Charge] (You recognize the merchant, but were overcharged, charged twice, or did not receive your order)*

---

### 2.6. Pair 6: `CRD-001` vs `SEC-001` (Card Block vs. Fraud Report)
* **Semantic Ambiguity**: Utterance requests card locking (e.g., *"Block my card right now!"*).
* **Core Distinction**:
  - `CRD-001`: Customer misplaced card, wants temporary freeze, or wants routine permanent block without unauthorized charges.
  - `SEC-001`: Card compromised by fraudsters, unauthorized OTPs received, or funds already stolen (Requires comprehensive account freeze + fraud investigation).

```mermaid
graph TD
    IN6["Customer: 'Lock my card immediately!'"] --> Q6{"Why do you need to block the card?"}
    Q6 -->|"Misplaced card / Preventative temporary freeze"| PATH_CRD1["Route: CRD-001 (Temporary or Permanent Block)"]
    Q6 -->|"Someone stole money / Fraudulent transactions occurring"| PATH_SEC1B["Route: SEC-001 (Fraud Report) -> Card Block + Account Alert + Fraud Desk Handover"]
```

* **Disambiguation Prompt**:
  > *"I can secure your card right away. Please let me know:*
  > *1. [Temporary or Standard Card Block] (Misplaced card, travel lock, or ordering replacement)*
  > *2. [Card Compromised / Fraud Incident] (Unauthorized charges or suspicious activity detected)*

---

## 3. Multi-Intent Extraction & Sequence Processing

Customers frequently submit compound utterances containing two or more distinct requests. The NLU architecture handles these through **Multi-Intent Decomposition**:

### 3.1. Decomposition Pipeline
```mermaid
graph LR
    COMP["Compound Utterance:<br/>'Check my balance and block my card ending 4912'"] --> SPLIT["Conjunctive Dependency Parser<br/>(and, also, then, plus, aur)"]
    SPLIT --> INT1["Sub-Intent 1:<br/>ACC-001 (Balance Check)"]
    SPLIT --> INT2["Sub-Intent 2:<br/>CRD-001 (Card Block)"]
    INT1 --> PRIO{"Safety & Urgency Priority Sort"}
    INT2 --> PRIO
    PRIO --> EXEC1["Step 1: Execute CRD-001<br/>(Higher Risk Tier: HIGH)"]
    EXEC1 --> EXEC2["Step 2: Execute ACC-001<br/>(Lower Risk Tier: LOW)"]
```

### 3.2. Prioritization Rules for Multi-Intent Sequences
When multiple intents are detected in a single turn, they are sorted by operational urgency and risk tier:
$$\text{CRITICAL (SEC-001, SEC-004)} > \text{HIGH (CRD-001, ACC-003, TXN-002)} > \text{MEDIUM} > \text{LOW (ACC-001, PRD-001)}$$

* **Execution Policy**:
  1. The urgent safety action is executed first (e.g., card freeze or fraud alert).
  2. The informational query is fulfilled immediately in the same response or as an immediate follow-up.
  3. *Example Response*:
     > *"1. Security Action: Your debit card ending in 4912 has been temporarily blocked immediately.*
     > *2. Account Balance: Your primary savings account balance is ₹48,250.00.*
     > *Is there anything else I can assist you with?"*

---

## 4. Out-of-Scope (OOS) Detection & Fallback Routines

### 4.1. Out-of-Scope Taxonomy
Utterances that do not map to the 30 banking intents are classified into distinct OOS categories:
* `OOS_CHITCHAT`: Pleasantries, greetings (*"Hello"*, *"How are you"*, *"Who made you"*). Handled with polite conversational banking personas.
* `OOS_UNRELATED`: General knowledge, weather, cooking, entertainment (*"What is the capital of France?"*, *"Write a poem"*). Handled with gentle redirection:
  > *"I am NexBank's dedicated virtual assistant, specifically trained to help you with your banking, accounts, cards, and payments. How can I assist you with your banking needs today?"*
* `OOS_PROHIBITED_ADVICE`: Legal, medical, or political queries (*"Should I sue my landlord?"*). Handled with clear domain boundary statements.
* `OOS_MALICIOUS`: Jailbreaks, prompt injections, and profanity. Handled by Layer 1/2 Guardrails.

### 4.2. Progressive Fallback & Probing Protocol
When confidence is below the low-confidence threshold ($c < 0.65$):
1. **Fallback Turn 1 (Clarification Probe)**:
   - Does not state generic confusion. Instead, identifies closest semantic domain:
   > *"I want to make sure I understand correctly. Are you looking for help with an Account, a Card, or a Recent Transaction?"*
   - Presents top domain buttons: `[Accounts]` `[Cards]` `[Transactions & UPI]` `[Other]`.
2. **Fallback Turn 2 (Secondary Probing)**:
   - If user still fails classification:
   > *"I'm having trouble understanding your specific request. To avoid any delay or mistake with your banking, would you like me to connect you with a banking specialist right now?"*
   - Buttons: `[Connect to Live Specialist]` `[Try Again]`.
3. **Fallback Turn 3 (Hard Escalation)**:
   - Mandatory escalation triggers. Context package is packaged and session routes to Live Banker CRM.
