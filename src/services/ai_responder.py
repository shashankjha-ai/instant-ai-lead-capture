# Import time module to calculate exact execution latency in seconds
import time
# Import asyncio module to manage asynchronous timeouts and sleep simulations
import asyncio
# Import typing helpers to define clear dictionary type hint contracts
from typing import Dict, Any
# Import AsyncOpenAI client and error classes to interact with third-party LLM API
from openai import AsyncOpenAI, OpenAIError
# Import centralized settings object to access API key and model config
from src.config import settings
# Import system logger to log execution steps and SLA violations
from src.utils.logger import logger

# Define service class encapsulating instant lead response orchestration
class InstantAIResponder:
    # Initialize service instance and configure AsyncOpenAI API client
    def __init__(self):
        # Instantiate AsyncOpenAI client using configured API key string
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        # Define strict system instructions directing AI conversational persona
        self.system_prompt = (
            "You are an elite conversational AI concierge for Realates AI Systems. "
            "Your sole mission is to instantly engage incoming B2B leads within target SLA. "
            "Be professional, concise, empathetic, and immediately ask for their business service type "
            "and primary lead acquisition bottleneck. Do not use generic corporate fluff."
        )

    # Define asynchronous method to process lead data and return reply dictionary
    async def generate_instant_response(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        # Record start timestamp to measure processing duration against SLA
        start_time = time.time()
        # Extract lead name defaulting to Valued Leader if missing
        lead_name = lead_data.get("name", "Valued Leader")
        # Extract company name defaulting to your organization if missing
        company = lead_data.get("company", "your organization")
        # Extract inbound message text to contextualize AI reply
        incoming_message = lead_data.get("message", "Hello, I am interested in AI automation.")
        # Extract source channel string defaulting to web_chat
        source = lead_data.get("channel", "web_chat")

        # Log trace logging inbound capture attempt
        logger.info(f"Received instant capture request from {lead_name} ({company}) via {source}")

        # Format prompt string combining lead metadata for LLM ingestion
        user_prompt = f"Lead Name: {lead_name}\nCompany: {company}\nMessage: {incoming_message}"

        # Check if local mock API key is configured to avoid requiring paid credentials
        if settings.OPENAI_API_KEY.startswith("sk-mock") or settings.OPENAI_API_KEY == "sk-your-openai-api-key-here":
            # Log warning trace indicating simulated local fallback execution
            logger.warning("Mock OpenAI key detected. Simulating ultra-fast conversational AI reply.")
            # Await short asynchronous sleep to simulate realistic network latency
            await asyncio.sleep(0.3)
            # Calculate total elapsed latency rounded to three decimal places
            latency = round(time.time() - start_time, 3)
            # Return simulation response dictionary containing high-converting reply
            return {
                "status": "success",
                "mode": "simulated_target",
                "latency_seconds": latency,
                "lead_name": lead_name,
                "response": (
                    f"Hello {lead_name}! Welcome to Realates AI Systems. "
                    f"We noticed {company} is looking to eliminate lead leakage. "
                    "To get you plugged in immediately: what is your average lead response time right now, "
                    "and are you currently using a CRM like GoHighLevel?"
                )
            }

        # Wrap live API execution in try/except block to catch timeouts and API faults
        try:
            # Execute real OpenAI call wrapped in strict SLA timeout enforcement
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=150
                ),
                timeout=settings.RESPONSE_TIMEOUT_SECONDS
            )
            
            # Calculate total elapsed execution latency in seconds
            latency = round(time.time() - start_time, 3)
            # Extract generated reply text string from API completion object
            ai_reply = response.choices[0].message.content
            
            # Log success trace recording latency metric
            logger.info(f"Generated AI reply in {latency}s for {lead_name}")
            # Return live AI completion dictionary
            return {
                "status": "success",
                "mode": "live_ai",
                "latency_seconds": latency,
                "lead_name": lead_name,
                "response": ai_reply
            }

        # Catch TimeoutError if third-party LLM response exceeds SLA budget
        except asyncio.TimeoutError:
            # Calculate elapsed latency at timeout exception
            latency = round(time.time() - start_time, 3)
            # Log error trace indicating SLA violation
            logger.error(f"AI response exceeded SLA timeout of {settings.RESPONSE_TIMEOUT_SECONDS}s")
            # Return deterministic fallback dictionary to preserve lead experience
            return {
                "status": "fallback",
                "latency_seconds": latency,
                "lead_name": lead_name,
                "response": (
                    f"Hi {lead_name}, thank you for reaching out to Realates! "
                    "Our system received your inquiry. A senior systems architect is reviewing your note "
                    "and will send your custom booking link in just a moment."
                )
            }
        # Catch any OpenAI specific API exceptions such as rate limits or invalid keys
        except OpenAIError as e:
            # Calculate elapsed latency at error occurrence
            latency = round(time.time() - start_time, 3)
            # Log error trace recording third-party exception details
            logger.error(f"OpenAI API Error: {str(e)}")
            # Return error status dictionary containing failsafe greeting
            return {
                "status": "error",
                "latency_seconds": latency,
                "error_message": str(e),
                "response": "Thank you for contacting Realates AI. We have logged your request securely."
            }

# Instantiate singleton responder object for import across application routes
responder = InstantAIResponder()
