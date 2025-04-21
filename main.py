from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import logging.config
import logging
import threading

from app.Utils.regular_update import job
from app.Utils.regular_send import send_sms

from app.Routers import dashboard
from app.Routers import auth
from app.Routers import socket
from app.Routers import stripe
from app.Routers import case
import app.Utils.database_handler as crud

app = FastAPI()

print("main python file")

# Disable all SQLAlchemy logging
logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)

origins = [
    "http://localhost:5173",  # React Vite frontend (local development)
    "http://192.168.148.98:5173",  # Local network access
    "http://192.168.148.98:8001",  # API server itself (optional)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(case.router, prefix="/api/v1")
app.include_router(socket.router, prefix="/api/v1")
app.include_router(stripe.router, prefix="/api/stripe")

@app.get("/")
async def health_checker():
    return {"status": "success"}

# Add this function to run send_sms in a loop
def send_sms_thread():
    print("Sending SMS")
    # while True:
    #     time.sleep(5)  # Sleep for 1 minute
    #     asyncio.run(send_sms())

@app.on_event("startup")
async def startup_event():
    # Start send_sms in a background thread
    sms_thread = threading.Thread(target=send_sms_thread, daemon=True)
    sms_thread.start()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
