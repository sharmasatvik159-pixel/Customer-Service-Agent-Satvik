# NexBank Agentic AI Customer Service: Component Interface Contracts

## 1. Scope & Design Philosophy

This document defines the strict, versioned interface contracts (JSON Schemas) governing all inter-component communication across the NexBank Conversational AI ecosystem. All schemas adhere to JSON Schema Draft 2020-12 and correspond directly to Pydantic v2 models implemented in the core codebase.

Any contract breach or schema mismatch fails fast at the API Gateway or serialization boundary with structured validation errors, preventing undefined agentic behavior.

---

## 2. Ingress API Gateway Contract

### 2.1. Request: `POST /api/v1/chat/message`
Received by the FastAPI Ingress Layer from Omnichannel frontends.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "IngressMessageRequest",
  "type": "object",
  "required": ["session_id", "channel", "message", "timestamp"],
  "properties": {
    "session_id": { "type": "string", "format": "uuid" },
    "conversation_id": { "type": "string", "format": "uuid" },
    "channel": {
      "type": "string",
      "enum": ["MOBILE_APP", "WEB_PORTAL", "TELEPHONY_IVR", "SECURE_MESSAGING"]
    },
    "message": {
      "type": "string",
      "minLength": 1,
      "maxLength": 1000
    },
    "auth_token": {
      "type": "string",
      "description": "Optional Bearer JWT containing authenticated claims"
    },
    "client_metadata": {
      "type": "object",
      "properties": {
        "device_id": { "type": "string" },
        "ip_address": { "type": "string", "format": "ipv4" },
        "user_agent": { "type": "string" },
        "locale": { "type": "string", "default": "en-US" }
      }
    },
    "timestamp": { "type": "string", "format": "date-time" }
  },
  "additionalProperties": false
}
```

### 2.2. Response: `POST /api/v1/chat/message`
Returned to Omnichannel frontends.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "IngressMessageResponse",
  "type": "object",
  "required": ["session_id", "turn_index", "response_text", "status", "timestamp"],
  "properties": {
    "session_id": { "type": "string", "format": "uuid" },
    "turn_index": { "type": "integer", "minimum": 0 },
    "response_text": { "type": "string" },
    "suggested_quick_replies": {
      "type": "array",
      "items": { "type": "string" }
    },
    "ui_action": {
      "type": "object",
      "properties": {
        "action_type": {
          "type": "string",
          "enum": ["NONE", "PROMPT_OTP", "PROMPT_BIOMETRIC", "OPEN_LINK", "HANDOVER_LIVE_AGENT"]
        },
        "payload": { "type": "object" }
      }
    },
    "disclaimers": {
      "type": "array",
      "items": { "type": "string" }
    },
    "status": {
      "type": "string",
      "enum": ["SUCCESS", "NEEDS_AUTH", "ESCALATED", "DISAMBIGUATION"]
    },
    "timestamp": { "type": "string", "format": "date-time" }
  },
  "additionalProperties": false
}
```

---

## 3. NLU Pipeline Contract

### 3.1. Input to NLU: `POST /internal/nlu/analyze`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "NLUAnalyzeRequest",
  "type": "object",
  "required": ["sanitized_text", "session_id", "turn_index"],
  "properties": {
    "sanitized_text": { "type": "string" },
    "session_id": { "type": "string", "format": "uuid" },
    "turn_index": { "type": "integer" },
    "active_intent": { "type": ["string", "null"] },
    "expected_slots": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "additionalProperties": false
}
```

### 3.2. Output from NLU: `NLUAnalyzeResponse`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "NLUAnalyzeResponse",
  "type": "object",
  "required": ["primary_intent", "confidence", "entities", "sentiment", "processing_time_ms"],
  "properties": {
    "primary_intent": {
      "type": "object",
      "required": ["name", "confidence"],
      "properties": {
        "name": { "type": "string" },
        "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
      }
    },
    "top_intents": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "confidence"],
        "properties": {
          "name": { "type": "string" },
          "confidence": { "type": "number" }
        }
      }
    },
    "entities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["entity", "value", "confidence", "start", "end"],
        "properties": {
          "entity": { "type": "string" },
          "value": { "type": ["string", "number", "boolean"] },
          "normalized_value": { "type": ["string", "number", "boolean", "null"] },
          "confidence": { "type": "number" },
          "start": { "type": "integer" },
          "end": { "type": "integer" }
        }
      }
    },
    "sentiment": {
      "type": "object",
      "required": ["score", "label"],
      "properties": {
        "score": { "type": "number", "minimum": -1.0, "maximum": 1.0 },
        "label": { "type": "string", "enum": ["POSITIVE", "NEUTRAL", "NEGATIVE"] }
      }
    },
    "disambiguation_required": { "type": "boolean" },
    "processing_time_ms": { "type": "number" }
  },
  "additionalProperties": false
}
```

---

## 4. Knowledge Base RAG Contract

### 4.1. Input to Retrieval Engine: `POST /internal/rag/retrieve`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RAGRetrieveRequest",
  "type": "object",
  "required": ["query", "session_id", "top_k"],
  "properties": {
    "query": { "type": "string", "description": "Rewritten search query" },
    "session_id": { "type": "string", "format": "uuid" },
    "top_k": { "type": "integer", "default": 3, "minimum": 1, "maximum": 10 },
    "filters": {
      "type": "object",
      "properties": {
        "domain": { "type": "string", "enum": ["ACCOUNTS", "CARDS", "LOANS", "TRANSFERS", "SECURITY", "GENERAL"] },
        "customer_segment": { "type": "string", "enum": ["RETAIL", "PREMIER", "COMMERCIAL"] },
        "max_effective_date": { "type": "string", "format": "date-time" }
      }
    },
    "min_relevance_score": { "type": "number", "default": 0.70 }
  },
  "additionalProperties": false
}
```

### 4.2. Output from Retrieval Engine: `RAGRetrieveResponse`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RAGRetrieveResponse",
  "type": "object",
  "required": ["chunks", "retrieval_strategy", "execution_time_ms"],
  "properties": {
    "chunks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["chunk_id", "document_id", "content", "relevance_score", "source_url"],
        "properties": {
          "chunk_id": { "type": "string" },
          "document_id": { "type": "string" },
          "title": { "type": "string" },
          "content": { "type": "string" },
          "relevance_score": { "type": "number" },
          "source_url": { "type": "string", "format": "uri" },
          "compliance_version": { "type": "string" },
          "last_reviewed_at": { "type": "string", "format": "date-time" }
        }
      }
    },
    "retrieval_strategy": {
      "type": "string",
      "enum": ["HYBRID_RRF", "DENSE_FALLBACK", "LEXICAL_FALLBACK"]
    },
    "execution_time_ms": { "type": "number" }
  },
  "additionalProperties": false
}
```

---

## 5. Tool Execution & Core Banking Contract

All tool calls adhere to strict deterministic invocation standards via gRPC / REST with required idempotency tokens.

### 5.1. Tool Invocation Schema: `CoreBankingToolRequest`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CoreBankingToolRequest",
  "type": "object",
  "required": ["tool_name", "idempotency_key", "customer_id", "auth_level", "parameters"],
  "properties": {
    "tool_name": {
      "type": "string",
      "enum": [
        "get_account_balance",
        "list_recent_transactions",
        "lock_debit_card",
        "unlock_debit_card",
        "initiate_domestic_transfer",
        "stop_check_payment"
      ]
    },
    "idempotency_key": {
      "type": "string",
      "format": "uuid",
      "description": "Unique key ensuring at-most-once execution"
    },
    "customer_id": { "type": "string" },
    "auth_level": { "type": "string" },
    "parameters": {
      "type": "object",
      "description": "Tool-specific strongly-typed arguments"
    }
  },
  "additionalProperties": false
}
```

### 5.2. Tool Invocation Result: `CoreBankingToolResponse`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CoreBankingToolResponse",
  "type": "object",
  "required": ["tool_name", "status", "idempotency_key", "timestamp"],
  "properties": {
    "tool_name": { "type": "string" },
    "status": { "type": "string", "enum": ["SUCCESS", "FAILED", "PENDING_CONFIRMATION", "UNAUTHORIZED"] },
    "idempotency_key": { "type": "string" },
    "result_payload": { "type": ["object", "null"] },
    "error_details": {
      "type": ["object", "null"],
      "properties": {
        "error_code": { "type": "string" },
        "message": { "type": "string" },
        "retryable": { "type": "boolean" }
      }
    },
    "timestamp": { "type": "string", "format": "date-time" }
  },
  "additionalProperties": false
}
```

---

## 6. Safety & Guardrail Contract

### 6.1. Input to Guardrails: `POST /internal/guardrails/evaluate`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "GuardrailEvaluationRequest",
  "type": "object",
  "required": ["draft_response", "user_query", "session_id", "retrieved_chunks"],
  "properties": {
    "draft_response": { "type": "string" },
    "user_query": { "type": "string" },
    "session_id": { "type": "string", "format": "uuid" },
    "retrieved_chunks": {
      "type": "array",
      "items": { "type": "string" }
    },
    "intent": { "type": "string" }
  },
  "additionalProperties": false
}
```

### 6.2. Output from Guardrails: `GuardrailEvaluationResponse`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "GuardrailEvaluationResponse",
  "type": "object",
  "required": ["is_safe", "action", "sanitized_response", "violations"],
  "properties": {
    "is_safe": { "type": "boolean" },
    "action": {
      "type": "string",
      "enum": ["APPROVE", "APPEND_DISCLAIMER", "REPLACE_WITH_CANNED", "ESCALATE_IMMEDIATE"]
    },
    "sanitized_response": { "type": "string" },
    "violations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["rule_id", "severity", "description"],
        "properties": {
          "rule_id": { "type": "string" },
          "severity": { "type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"] },
          "description": { "type": "string" }
        }
      }
    },
    "grounding_score": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
    "disclaimer_text": { "type": ["string", "null"] },
    "execution_time_ms": { "type": "number" }
  },
  "additionalProperties": false
}
```

---

## 7. Escalation Handover Package Contract

When an escalation triggers, the orchestrator serializes the complete conversation record into this standardized payload for CRM dispatch.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "EscalationContextPackage",
  "type": "object",
  "required": [
    "escalation_id",
    "session_id",
    "customer_id",
    "timestamp",
    "target_queue",
    "primary_reason",
    "conversation_summary",
    "sentiment_summary",
    "extracted_slots",
    "sanitized_transcript"
  ],
  "properties": {
    "escalation_id": { "type": "string", "format": "uuid" },
    "session_id": { "type": "string", "format": "uuid" },
    "customer_id": { "type": ["string", "null"] },
    "customer_tier": { "type": "string", "enum": ["STANDARD", "PREMIER", "PRIVATE_WEALTH", "COMMERCIAL"] },
    "timestamp": { "type": "string", "format": "date-time" },
    "target_queue": {
      "type": "string",
      "enum": ["GENERAL_SUPPORT", "FRAUD_AND_DISPUTES", "WIRE_SPECIALISTS", "MORTGAGE_DESK"]
    },
    "primary_reason": {
      "type": "string",
      "enum": [
        "USER_REQUESTED",
        "SENTIMENT_PLUNGE",
        "REPETITIVE_NLU_FALLBACK",
        "POLICY_GUARDRAIL_VIOLATION",
        "AUTH_LOCKOUT",
        "HIGH_VALUE_TRANSACTION"
      ]
    },
    "conversation_summary": {
      "type": "string",
      "maxLength": 500,
      "description": "Agent-generated TL;DR synthesized for the incoming human banker"
    },
    "sentiment_summary": {
      "type": "object",
      "required": ["final_score", "trajectory"],
      "properties": {
        "final_score": { "type": "number" },
        "trajectory": { "type": "string" },
        "detected_frustration_indicators": { "type": "array", "items": { "type": "string" } }
      }
    },
    "extracted_slots": { "type": "object" },
    "sanitized_transcript": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["turn", "speaker", "text", "timestamp"],
        "properties": {
          "turn": { "type": "integer" },
          "speaker": { "type": "string" },
          "text": { "type": "string" },
          "timestamp": { "type": "string" }
        }
      }
    }
  },
  "additionalProperties": false
}
```

---

## 8. Event Bus & Audit Logging Contract

Emitted asynchronously over Kafka / EventBridge for compliance audit trails, OpenTelemetry tracing, and the continuous feedback learning pipeline.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "AgentAuditEventMessage",
  "type": "object",
  "required": ["event_id", "trace_id", "event_type", "session_id", "timestamp", "payload"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "trace_id": { "type": "string" },
    "event_type": {
      "type": "string",
      "enum": [
        "CONVERSATION_TURN_COMPLETED",
        "GUARDRAIL_TRIGGERED",
        "TOOL_EXECUTION_COMPLETED",
        "DISAMBIGUATION_PRESENTED",
        "ESCALATION_DISPATCHED",
        "FEEDBACK_SUBMITTED"
      ]
    },
    "session_id": { "type": "string", "format": "uuid" },
    "customer_id": { "type": ["string", "null"] },
    "timestamp": { "type": "string", "format": "date-time" },
    "latency_breakdown_ms": {
      "type": "object",
      "properties": {
        "nlu_ms": { "type": "number" },
        "rag_ms": { "type": "number" },
        "llm_ms": { "type": "number" },
        "guardrails_ms": { "type": "number" },
        "total_ms": { "type": "number" }
      }
    },
    "payload": { "type": "object" }
  },
  "additionalProperties": false
}
```
