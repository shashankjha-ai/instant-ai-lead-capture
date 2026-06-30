# ARCHITECTURE DOCUMENTATION
**Service:** Instant AI Lead Capture  
**Target SLA:** Sub-2-Second Concierge Reply  

## System Design
The service is structured as a non-blocking asynchronous FastAPI microservice. Inbound webhooks from landing pages or WhatsApp APIs are received at `/api/v1/webhook/capture`. 

```mermaid
sequenceDiagram
    autonumber
    actor Lead as Inbound Lead (Web/WhatsApp)
    participant API as FastAPI Webhook Endpoint
    participant Val as Pydantic Validator
    participant AI as AsyncOpenAI Engine
    participant Log as System Logger

    Lead->>API: POST /api/v1/webhook/capture (JSON Payload)
    API->>Val: Validate Schema
    Val-->>API: Validated Lead Object
    API->>AI: Async Stream / Generate Reply
    alt AI Responds within Target SLA (<2.0s)
        AI-->>API: Personalized Conversational Reply
        API->>Log: Log Latency & Success
        API-->>Lead: 200 OK + Instant AI Greeting
    else Timeout Exceeded (>2.0s) or Error
        AI-->>API: TimeoutException
        API->>Log: Log SLA Violation Warning
        API-->>Lead: 200 OK + Deterministic Fallback Greeting
    end
```

## Resiliency Design
- **Strict SLA Timeout Protection:** All third-party LLM calls are wrapped in `asyncio.wait_for(..., timeout=2.0)`. If network congestion occurs, fallback logic immediately fires.
- **Pydantic Validation:** Ensures malformed payloads are rejected with clear HTTP 422 errors.
