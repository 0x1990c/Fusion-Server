import os
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import stripe

from app.Model.StripeModel import StripeModel
from sqlalchemy.orm import Session
from database import AsyncSessionLocal
import app.Utils.database_handler as crud
from app.Utils.Auth import get_current_user
from app.Utils.database_handler import update_usertype
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

stripe.api_key = os.getenv('STRIPE_API_KEY')

YOUR_DOMAIN = 'http://localhost:5173'
# YOUR_DOMAIN = 'https://text.thequarrythornton.com'

Base_Price_Id = "price_1R2c2IAZfjTlvHBosrQOiw6y"
endpoint_secret = 'whsec_XPGOeNd1WYFhtn4ICi5rdnUd06yNnzbP'
endpoint_Id =  'we_1Qyq0LAZfjTlvHBoOZBPYG7W'
# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        
@router.post("/checkout")
async def checkout(model: StripeModel, db: Session = Depends(get_db)):
    try:
        print("model.email:", model)
        checkout_session = stripe.checkout.Session.create(
            customer_email=model.email,
            # line_items=[{"price": model.plan_id, "quantity": 1}],
            
            line_items=[{
                "price": model.plan_id, 
                "quantity": 1
            }],

            mode="subscription",
            
            success_url= YOUR_DOMAIN + "/main?success=true",
            cancel_url= YOUR_DOMAIN + "/main?success=false",
        )
        print("checkout session:", checkout_session)
        await crud.update_usertype(db, model.email, 1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return checkout_session.url

@router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    print("webhook")
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        raise HTTPException(status_code=400, detail=str(e))

    # print("event:", event)
      
    if event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        await handle_subscription_succeeded(db, invoice)
        
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        await handle_subscription_failed(db, invoice)
        
    else:
        print(f"Unhandled event type {event['type']}")
    return JSONResponse(status_code=200, content={"success": True})
    
async def handle_subscription_succeeded(db: Session, invoice):
    line_item = invoice['lines']['data'][0]
    plan_id = line_item['plan']['id']
    email = invoice['customer_email']
    
    if plan_id == Base_Price_Id:
        await crud.update_sms_balance(db, email, 5000)

async def handle_subscription_failed(db: Session, invoice):
    print("Subscription failed:", invoice)
    
