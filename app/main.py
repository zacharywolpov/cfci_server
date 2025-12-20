from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.services import openai_service
from app.api import chat, auth
from dotenv import load_dotenv
from app.core import config
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load env variables
load_dotenv(dotenv_path=".env.development.local")

# Add middleware for formatting request logs
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        print(f"--- Incoming Request ---")
        print(f"URL: {request.url}")
        print(f"Method: {request.method}")
        print(f"Headers: {dict(request.headers)}")
        # print(f"Body: {body.decode('utf-8')}")
        response = await call_next(request)
        print(f"--- End Request ---\n")
        return response

# Properly create the lifespan of this fastapi app
# to start up and shut down services as needed
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Starting up the FastAPI application.")
    
    # Initialize services
    app.state.openai_client = openai_service.OpenAIService(api_key=os.getenv("OPENAI_KEY"))
    yield
    
    # Shutdown actions
    logger.info("Shutting down the FastAPI application.")

# Create app instance
app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get_settings().cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(auth.router)
# app.include_router(admin.router)