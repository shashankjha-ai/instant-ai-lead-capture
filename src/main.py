# Import FastAPI framework to create asynchronous web service routes
from fastapi import FastAPI, HTTPException, Request
# Import Pydantic models for strict payload data validation and type checking
from pydantic import BaseModel, Field
# Import Optional type hint to allow nullable fields in webhook payload
from typing import Optional
# Import responder service instance to handle AI concierge generation logic
from src.services.ai_responder import responder
# Import system logger utility to record telemetry and debugging traces
from src.utils.logger import logger
# Import centralized settings object to access configuration variables
from src.config import settings

# Initialize FastAPI application instance with descriptive OpenAPI metadata
app = FastAPI(
    title="Instant AI Lead Capture Webhook Service",
    description="Production microservice engineered for Realates AI Systems to target <2s lead response SLA.",
    version="1.0.0"
)

# Define Pydantic schema class to enforce incoming lead capture structure
class WebhookPayload(BaseModel):
    # Require lead name string field to personalize downstream AI greeting
    name: str = Field(..., example="Mostafa Walid")
    # Optional email field to allow multichannel fallback follow-ups
    email: Optional[str] = Field(None, example="lead@clientcompany.com")
    # Optional phone field to allow WhatsApp message routing
    phone: Optional[str] = Field(None, example="+201061929895")
    # Optional company name defaulting to Independent Enterprise if omitted
    company: Optional[str] = Field("Independent Enterprise", example="Apex Tech")
    # Require incoming message string field to extract lead pain points
    message: str = Field(..., example="We are losing 50% of inbound web leads due to slow replies.")
    # Require channel identifier string defaulting to web_chat
    channel: str = Field("web_chat", example="whatsapp")

# Define asynchronous HTTP POST endpoint to handle lead webhooks
@app.post("/api/v1/webhook/capture")
async def handle_lead_capture(payload: WebhookPayload):
    # Log informational trace indicating inbound webhook reception
    logger.info(f"Incoming webhook received on channel: {payload.channel}")
    # Wrap processing logic in try/except block to catch unhandled runtime errors
    try:
        # Delegate payload dictionary to AI responder service and await result
        result = await responder.generate_instant_response(payload.model_dump())
        # Return HTTP 200 JSON response containing generated concierge reply
        return result
    # Catch any general exception raised during AI API communication
    except Exception as e:
        # Log error trace recording exception message for debugging
        logger.error(f"Unhandled system exception: {str(e)}")
        # Raise HTTP 500 Internal Server Error to client webhook caller
        raise HTTPException(status_code=500, detail="Internal server error during lead processing.")

# Define health check HTTP GET endpoint for load balancer monitoring
@app.get("/health")
async def health_check():
    # Return JSON status object confirming service operational health
    return {
        "status": "healthy",
        "service": "instant-ai-lead-capture",
        "sla_target_seconds": settings.RESPONSE_TIMEOUT_SECONDS
    }

# Execute server directly if script is invoked from command line
if __name__ == "__main__":
    # Import uvicorn server library to bind ASGI application
    import uvicorn
    # Boot Uvicorn server bound to all local network interfaces on configured port
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
