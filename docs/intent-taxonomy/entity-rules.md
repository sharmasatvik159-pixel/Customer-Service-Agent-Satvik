# NexBank Entity Extraction & Slot Validation Rules

## 1. Executive Overview & Extraction Stack

Entity extraction in the NexBank platform employs a defense-in-depth, three-tier hybrid pipeline:
1. **Deterministic Regular Expressions**: First-pass regex engines for strictly patterned identifiers (PAN, UPI IDs, Phone Numbers, partial digits).
2. **Transformer NER Models**: Fine-tuned multilingual RoBERTa / IndicBERT token classifiers for free-text context resolution (Merchant Names, Persons, Locations).
3. **Gazetteers & Dictionary Lookups**: Canonical lists of bank branches, account types, IFSC codes, and currency designations.

---

## 2. Key Banking Entity Specifications

### 2.1. Account Number (`ACCOUNT_NUMBER` / `ACCOUNT_NUMBER_LAST4`)
* **Extraction Method**: Hybrid (Regex + Contextual Dependency Parsing).
* **Regex Pattern (Full)**: `\b(?:\d{9,18})\b`
* **Regex Pattern (Masked/Last 4)**: `(?i)(?:acct|account|a/c|ending in|no\.?)\s*(?:[x*]{4,14})?(\d{4})\b`
* **Validation Rules**:
  - Full Account Numbers: 9 to 18 digits depending on core banking branch prefix. Checked against NexBank account checksum algorithm.
  - Partial Account Numbers: Exactly 4 digits.
* **Security & PII Rules**:
  - Full 9–18 digit account numbers in user input are matched by the Ingress PII filter and replaced with `{{BANK_ACCT_TOKEN_<UUID4>}}` prior to LLM forwarding.
  - Only the extracted last 4 digits (`ACCOUNT_NUMBER_LAST4`) may be passed in prompt context for conversational disambiguation.

### 2.2. Transaction Amount (`TRANSACTION_AMOUNT`)
* **Extraction Method**: Regex + Spacy Entity Extractor (`MONEY`).
* **Regex Pattern**: `(?i)(?:(?:rs\.?|inr|₹|\$|usd)\s*)?(\d{1,3}(?:,\d{2,3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)\s*(?:rupees|rs|bucks|inr|usd|dollars)?`
* **Normalization Logic**:
  - Strips currency symbols and comma separators.
  - Converts words (e.g., *"five thousand"*, *"do hazaar"*, *"5k"*, *"1.5 lakh"*) to canonical float representations (e.g., `5000.00`, `2000.00`, `150000.00`).
  - Sets ISO-4217 currency code (Default: `INR` for domestic Indian operations, `USD` for US cross-border).
* **Validation Rules**:
  - Must be $> 0.00$.
  - Maximum single-turn limit: ₹2,00,000 for standard UPI; ₹10,00,000 for NEFT/RTGS; amounts above ₹50,000 require PAN verification per tax regulations.

### 2.3. Partial Card Number (`CARD_LAST4`)
* **Extraction Method**: Deterministic Regex.
* **Regex Pattern**: `(?i)(?:card|ending in|ending with|debit|credit|last)\s*(?:(?:[x*]{4}[-\s]?){3})?(\d{4})\b`
* **Validation Rules**:
  - Must be exactly 4 digits.
  - Cross-referenced against the customer's linked active cards in core banking.
* **Security & Compliance Rule (PCI-DSS v4.0)**:
  - **Full 16-digit Primary Account Numbers (PAN) are strictly forbidden**.
  - If a user inputs 15 or 16 consecutive digits satisfying the Luhn algorithm, the Ingress PII Redactor instantly scrubs the input, tokenizes it into `{{PCI_PAN_TOKEN_<UUID4>}}`, and logs a security masking audit event. The conversational agent is strictly provided with `CARD_LAST4`.

### 2.4. Partial Aadhaar Number (`AADHAAR_LAST4`)
* **Extraction Method**: Strict Regex with Negative Lookaround.
* **Regex Pattern**: `(?i)(?:aadhaar|uidai|aadhar)\s*(?:[x*]{8}|\.{8}|(?:[x*]{4}\s*){2})?(\d{4})\b`
* **Validation Rules**:
  - Must be exactly 4 digits.
  - **STRICT PROHIBITION**: Full 12-digit Aadhaar numbers must **never** be stored or processed in raw text. Any 12-digit number matching the UIDAI Verhoeff checksum algorithm is redacted at the network boundary into `{{AADHAAR_TOKEN_<UUID4>}}`.
  - The agent only stores `AADHAAR_LAST4` to confirm customer identity against core KYC records.

### 2.5. Permanent Account Number (`PAN_NUMBER`)
* **Extraction Method**: Regex.
* **Regex Pattern**: `\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b`
* **Validation Rules**:
  - 10 alphanumeric characters.
  - 4th character must be entity status (e.g., `P` for Individual, `C` for Company, `H` for HUF, `F` for Firm, `A` for AOP, `T` for Trust).
  - 5th character must match the first letter of the customer's legal last name.
* **Normalization Logic**: Forced uppercase; leading/trailing whitespace trimmed.

### 2.6. Unified Payments Interface Virtual Payment Address (`UPI_ID` / `VPA`)
* **Extraction Method**: Regex + Handle Gazetteer.
* **Regex Pattern**: `\b([a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64})\b`
* **Validation Rules**:
  - Must contain exactly one `@` symbol.
  - Handle suffix matched against verified PSP list (e.g., `@okhdfcbank`, `@okaxis`, `@paytm`, `@ybl`, `@icici`, `@ibl`, `@axl`).
  - Total length between 3 and 100 characters.

### 2.7. Phone Number (`PHONE_NUMBER`)
* **Extraction Method**: Regex + Google `phonenumbers` library parser.
* **Regex Pattern**: `(?:\+?91[\-\s]?)?[6-9]\d{9}\b` (India domestic standard)
* **Normalization Logic**:
  - Standardized to E.164 format (e.g., `+919876543210`).
  - Strip spaces, hyphens, and leading zero.
* **Validation Rules**:
  - For Indian numbers: exactly 10 digits starting with digits 6, 7, 8, or 9.
  - Masked on UI displays as `+91 ******3210`.

### 2.8. Merchant Name (`MERCHANT_NAME`)
* **Extraction Method**: Named Entity Recognition (NER fine-tuned on banking POS transaction memos) + Gazetteer Lookup.
* **Gazetteer Dictionary**: Top 5,000 domestic and global merchants (Amazon, Flipkart, Swiggy, Zomato, Uber, Netflix, IRCTC, D-Mart, Shell, Starbucks).
* **Normalization Logic**: Strips aggregator prefixes and billing descriptors (e.g., `"AMZN MKTPLACE BLR"` $\to$ `"Amazon"`; `"ZOMATO*ORDER GGN"` $\to$ `"Zomato"`).

---

## 3. Entity Specification & Extraction Matrix

| Entity Type | Extraction Engine | Validation Algorithm / Rule | Normalized Format | PII Masking Rule |
| :--- | :--- | :--- | :--- | :--- |
| `ACCOUNT_NUMBER_LAST4` | Regex | 4 numeric digits | `1234` | Raw full acct redacted |
| `TRANSACTION_AMOUNT` | Regex + Spacy | Float $> 0.00$ | `{"amount": 2500.0, "currency": "INR"}` | None |
| `CARD_LAST4` | Regex | 4 numeric digits | `4912` | Full 16-digit PAN redacted |
| `AADHAAR_LAST4` | Regex | 4 numeric digits | `9012` | Full 12-digit Aadhaar redacted |
| `PAN_NUMBER` | Regex | Format `[A-Z]{5}[0-9]{4}[A-Z]{1}` | `ABCDE1234F` | Encrypted in audit log |
| `UPI_ID` | Regex | Valid PSP handle format | `username@okhdfcbank` | Username obfuscated |
| `PHONE_NUMBER` | `phonenumbers` | E.164 format, 10-digit mobile | `+919876543210` | Display masked |
| `MERCHANT_NAME` | Transformer NER | Dictionary lookup & memo stripping | `Amazon India` | None |

---

## 4. Slot-Filling Strategies & Dialogue Policies

### 4.1. Required vs. Optional Slots
* **Required Slots**: The intent cannot transition to execution (`Tool_Execution_Ready`) until all required slots have status `VALIDATED` or `CONFIRMED`.
* **Optional Slots**: Provide additional filtering or personalization. If omitted by the user, default values are assigned automatically.

### 4.2. Default Value Assignment Policies
When an optional slot is not mentioned, the state engine applies deterministic defaults:
* `delivery_channel` for statements: Default = `REGISTERED_EMAIL`.
* `file_format` for statements: Default = `PDF`.
* `date_range` for statements: Default = `"LAST_30_DAYS"`.
* `account_type` for balance inquiries: Default = `PRIMARY_SAVINGS` or `PRIMARY_CHECKING`.
* `delivery_speed` for card replacement: Default = `STANDARD`.

### 4.3. Clarification Probing Protocols
When a required slot is missing or ambiguous, the agent dispatches a targeted clarification prompt:
1. **Direct Slot Probe**: Asks explicitly for the missing parameter with examples.
   - *Example (Missing Amount)*: *"How much would you like to transfer?"*
   - *Example (Missing Tenure)*: *"What tenure would you prefer for your Fixed Deposit? We offer options ranging from 7 days up to 10 years."*
2. **Contextual Quick Replies**: Renders clickable buttons for enumerated choices (e.g., `[Last 1 Month]`, `[Last 3 Months]`, `[Financial Year 2025-26]`).
3. **Progressive Slot Probing**: Only ask for one missing required slot per turn to prevent cognitive overload.

### 4.4. Explicit Confirmation Protocols
For any high-impact intent (`CRD-001`, `CRD-002`, `TXN-002`, `TXN-005`, `TXN-006`, `ACC-003`, `ACC-005`):
1. **Parameter Summary Verification**: Prior to invoking core banking tools, the agent presents a structured summary:
   > *"Please confirm the details of your request:*
   > *• Action: Block Debit Card (Permanent)*
   > *• Card Ending: ...4912*
   > *• Replacement Card: Yes, dispatch to registered residence*
   > *Shall I proceed with blocking this card now?"*
2. **Binary Confirmation Gate**:
   - User affirmative (`"yes"`, `"confirm"`, `"go ahead"`, `"haan kar do"`) $\to$ Triggers tool execution.
   - User negative (`"no"`, `"cancel"`, `"stop"`, `"wait"`, `"nahi"`) $\to$ Cancels execution and asks for desired changes.
   - Ambiguous response $\to$ Repeats parameter summary with explicit Yes/No buttons.
