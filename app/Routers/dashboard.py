from fastapi import FastAPI,BackgroundTasks, APIRouter, Depends, HTTPException, status, File, UploadFile, Request, Form, Response
from fastapi.responses import FileResponse
from typing import List
from twilio.twiml.messaging_response import MessagingResponse
from sqlalchemy.orm import Session
from database import AsyncSessionLocal
import uuid

from app.Utils.chatgpt import get_last_message
from app.Utils.regular_send import send
from app.Utils.Auth import get_current_user
from app.Utils.regular_update import job, update_notification, update_database
from app.Utils.regular_send import send_opt_in_phone
from app.Utils.sendgrid import send_opt_in_email
import app.Utils.database_handler as crud
from app.Model.Settings import SettingsModel
from app.Model.MainTable import MainTableModel, PhoneModel
from app.Model.ScrapingStatusModel import ScrapingStatusModel
from app.Model.LastMessageModel import LastMessageModel
from pydantic import EmailStr

from copy import deepcopy
from typing import Annotated
from datetime import datetime
import os
import json

from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post('/add-message')
async def add_message(data: MainTableModel, email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    user = await crud.get_user_by_email(db, email)
    sms_balance = user.sms_balance - 1
    if sms_balance < 0:
        return {"success":"false", "message":"Not enough balance", "balace":user.sms_balance }
    else:
        await crud.update_sms_balance(db, email, -1)
    # Set default values
    message_data = MainTableModel(
        last_message=data.last_message,
        message_status=0,  # default value
        qued_timestamp=data.qued_timestamp,
        sent_timestamp=None,
        sent_success=0,  # default value
        image_url=data.image_url,
        categories=data.categories,
        phone_numbers=data.phone_numbers,
        num_sent=0,  # default value
        created_at=data.created_at
    )
    
    await crud.insert_message(db, message_data)
    return {"received": data, "message": "Raw data processed successfully", "balace":user.sms_balance}

@router.post('/update-message')
async def update_message(data: MainTableModel, email: Annotated[str, Depends(get_current_user)], message_id: int, db: Session = Depends(get_db)):
    print("dashboard - data: ", data)
    print("dashboard - message_id: ", message_id)
    message_data = MainTableModel(
        last_message=data.last_message,
        message_status=0,  # default value
        qued_timestamp=data.qued_timestamp,
        sent_timestamp=None,
        sent_success=0,  # default value
        image_url=data.image_url,
        categories=data.categories,
        phone_numbers=data.phone_numbers,
        num_sent=0,  # default value
        created_at=data.created_at
    )
    await crud.update_message(db, message_id, message_data)
    return {"success": "true"}


@router.get('/delete-message')
async def delete_message_route(email: Annotated[str, Depends(get_current_user)], message_id: int, db: Session = Depends(get_db)):
    await crud.delete_message(db, message_id)
    return {"success": "true"}


@router.get('/message-table')
async def get_message_table(db: Session = Depends(get_db)):
    main_table_data = await crud.get_main_table(db)
    
    main_table_data_dicts = [
        {
            "id": data.id,
            "last_message": data.last_message,
            "message_status": data.message_status,
            "qued_timestamp": data.qued_timestamp,
            "sent_timestamp": data.sent_timestamp,
            "sent_success": data.sent_success,
            "image_url": data.image_url,
            "categories": data.categories,
            "num_sent": data.num_sent,
            "phone_numbers": data.phone_numbers
        }
        for data in main_table_data
    ]
    
    return main_table_data_dicts

@router.get('/qued')
async def make_qued(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    qued_time = datetime.utcnow()
    # print("qued_time", qued_time)
    await crud.update_project(db, project_id, message_status=2, qued_timestamp=qued_time)
    return {"success": "true"}

@router.get('/cancel-qued')
async def cancel_qued(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    await crud.update_project(db, project_id, message_status=1, qued_timestamp=None)
    return {"success": "true"}

@router.get('/set-sent')
async def set_sent(email: Annotated[str, Depends(get_current_user)], project_id: int, db: Session = Depends(get_db)):
    sent_time = datetime.utcnow()
    print("sent_time", sent_time)
    await crud.update_project(db, project_id, message_status=3)
    ret = await send(project_id, db)  # Replace with appropriate send operation
    if ret:
        return {"success": "true"}
    else:
        return {"success": "false"}

@router.get('/change-status')
async def change_status(email: Annotated[str, Depends(get_current_user)], message_id: int, method: int, db: Session = Depends(get_db)):
    await crud.update_sending_method(db, message_id, method=method)
    return {"success": "true"}

@router.post('/update-last-message')
async def update_last_message(email: Annotated[str, Depends(get_current_user)], last_message: LastMessageModel, db: Session = Depends(get_db)):
    # print("message: ", last_message.message)
    await crud.update_project(db, last_message.project_id, last_message=last_message.message)
    return {"success": "true"}

@router.get('/download-message-history')
async def download_message_history(email: Annotated[str, Depends(get_current_user)], message_id: int, db: Session = Depends(get_db)):
    message = await crud.get_message_history_by_message_id(db, message_id)
    
    # Write data to a text file
    file_path = 'message_history.txt'
    with open(file_path, 'w') as f:
        f.write(message + '\n')
    
    # Ensure file was saved
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file as response
    return FileResponse(file_path, media_type='application/octet-stream', filename='message_history.txt')

@router.get('/download-history-message')
async def download_history_message(email: Annotated[str, Depends(get_current_user)], history_id: int, db: Session = Depends(get_db)):
    message = await crud.get_message_history_by_history_id(db, history_id)
    print(message)
    
    # Write data to a text file
    file_path = 'message.txt'
    with open(file_path, 'w') as f:
        f.write(message + '\n')
    
    # Ensure file was saved
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file as response
    return FileResponse(file_path, media_type='application/octet-stream', filename='message.txt')

@router.get('/send')
async def send_message_route(message_id: int, email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    await send(message_id, db)
    return {"success": "true"}

@router.post('/set-variables')
async def set_variables_route(variables: SettingsModel, db: Session = Depends(get_db)):
    
    data = await crud.get_variables(db)
    print(data)
    print("dashboard - set_variables", variables)
    if data is None:
        await crud.create_variables(db, **variables.dict())
    else:
        update_data = {k: (getattr(data, k) if v == "" else v) for k, v in variables.dict().items()}
        await crud.update_variables(db, data.id, **update_data)
    return {"success": "true"}

@router.get('/timer')
async def get_timer(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    data = await crud.get_variables(db)
    if data is None:
        return None
    else:
        print(data.timer)
        return data.timer
        
    return {"success": "true"}


@router.get('/set-opt-in-status-email')
async def set_opt_in_status_email(email: Annotated[str, Depends(get_current_user)], message_id: int, opt_in_status_email: int, db: Session = Depends(get_db)):
    print("dashboard - message_id: ", message_id)
    message = await crud.get_message(db, message_id)
    if opt_in_status_email == 1:
        await send_opt_in_email(message_id, message.email, db)
    await crud.update_opt_in_status_email(db, message_id, opt_in_status_email)
    return True

@router.get('/set-opt-in-status-phone')
async def set_opt_in_status_phone(email: Annotated[str, Depends(get_current_user)], phone_id: int, opt_in_status_phone: int, db: Session = Depends(get_db)):
    print("dashboard - phone_id: ", phone_id)
    phone = await crud.get_phone(db, phone_id)
    if opt_in_status_phone == 1:
        await send_opt_in_phone(phone.phone_number, phone_id, db)
    # await crud.update_opt_in_status_phone(db, phone_id, opt_in_status_phone)
    return True

@router.post('/send-optin-messages')
async def send_optin_messages(payload: list[dict], db: Session = Depends(get_db)):
    print("dashboard - payload: ", payload)
    for phone in payload:
        phone_id = phone.get('id')
        phone_number = phone.get('phone_number')
        await send_opt_in_phone(phone_number, phone_id, db)
    return {"success": "true", "message": "Send SMS messages successfully"}

@router.get('/confirm-opt-in-status')
async def set_opt_in_status(message_id: int, response: str, db: Session = Depends(get_db)):
    print("dashboard - confirm-opt-in-status - message_id: ", message_id)
    
    await crud.update_opt_in_status_email(db, message_id, 2 if response == "accept" else 3)
    
    data = await crud.get_status(db)
    if data is not None:
        await crud.set_db_update_status(db, data.id, 1)
    
    if response == "accept":
        return "Sent Successfully! Congulatulations!"
    else:
        return "Sent Successfully!"
    

@router.get('/approved')
async def set_opt_in_status(email: str, response: str, db: Session = Depends(get_db)):
    print("dashboard - approved - message_id: ", email)
    user = await crud.get_user_by_email(db, email)
    
    if response == "accept":
        await crud.update_user(db, user.id, approved=1)
        return "Sent Successfully! Congulatulations!"
    else:
        await crud.update_user(db, user.id, approved=0)
        return "Sent Successfully!"
    

@router.get('/variables')
async def get_variables(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    data = await crud.get_variables(db)
    return data

@router.get('/check-database-update')
async def get_variables(email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    
    data = await crud.get_status(db)
    if data is None:
        return False
    
    db_update_status = data.db_update_status
    print("dashboard - data.db_update_status: ", data.db_update_status)
    
    if db_update_status:
        await crud.set_db_update_status(db, data.id, 0)
        return True
    else:
        return False

@router.post('/add-customer')
async def add_customer(data: dict, email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    print("dashboard - add customer data: ", data)
    phone_numbers = data.get('phone_numbers', [])
    categories = data.get('categories', [])
    if not isinstance(phone_numbers, list):
        raise HTTPException(
            status_code=400,
            detail="phone_numbers must be a list"
        )
    if not isinstance(categories, list):
        raise HTTPException(
            status_code=400,
            detail="categories must be a list"
        )
    new_customer = await crud.insert_customer(db, phone_numbers, categories)
    # Create threads for phone creation and opt-in messages
    phones = []
    # First create all phones
    
    for phone_number in new_customer.phone_numbers:
        new_phone = await crud.create_phone(db, phone_number, new_customer.id, opt_in_status=0)
        phones.append(new_phone)

    print("twilio: ", "this is the main add phone number");

    for phone in phones:
        await send_opt_in_phone(phone.phone_number, phone.id, db)
            
    return {"success": "true", "message": "Customer added successfully"}

@router.post('/update-customer') 
async def update_customer(data: dict, email: Annotated[str, Depends(get_current_user)], customer_id: int, db: Session = Depends(get_db)):
    print("dashboard - update customer data: ", data)
    print("dashboard - customer_id: ", customer_id)
    phone_numbers = data.get('phone_numbers', [])
    categories = data.get('categories', [])
    if not isinstance(phone_numbers, list):
        raise HTTPException(
            status_code=400,
            detail="phone_numbers must be a list"
        )
    if not isinstance(categories, list):
        raise HTTPException(
            status_code=400,
            detail="categories must be a list"
        )
    await crud.update_customer(db, customer_id, phone_numbers, categories)
    return {"success": "true"}

@router.get('/delete-customer')
async def delete_customer(email: Annotated[str, Depends(get_current_user)], customer_id: int, db: Session = Depends(get_db)):
    if not customer_id:
        raise HTTPException(
            status_code=400,
            detail="customer_id is required"
        )
    await crud.delete_customer(db, customer_id)
    return {"success": "true"}

@router.get('/customer-table')
async def get_customer_table(db: Session = Depends(get_db)):
    customer_data = await crud.get_customer_table(db)
    
    customer_data_dicts = [
        {
            "id": data.id,
            "phone_numbers": json.loads(data.phone_numbers) if isinstance(data.phone_numbers, str) else data.phone_numbers,
            "categories": json.loads(data.categories) if isinstance(data.categories, str) else data.categories
        }
        for data in customer_data
    ]
    
    return customer_data_dicts

@router.get('/customer-categories')
async def get_customer_categories(db: Session = Depends(get_db)):
    categories = await crud.get_customer_categories(db)
    return categories

@router.post('/add-customer-category')
async def add_customer_category(data: dict, db: Session = Depends(get_db)):
    print("dashboard - add customer category data: ", data)
    name = data.get('name', '')
    if not name:
        raise HTTPException(
            status_code=400,
            detail="name is required"
        )
    
    existing_category = await crud.get_customer_category_by_name(db, name)
    
    if existing_category:
        return {"success": "false", "message": "Category already exists"}
    
    await crud.add_customer_category(db, name)
    return {"success": "true", "message": "New category is added!"}

@router.post('/update-customer-category')
async def update_customer_category(data: dict, db: Session = Depends(get_db)):
    print("dashboard - update customer category data: ", data)
    customer_id = data.get('categoryId', -1);
    category_name = data.get('name', "");

    await crud.update_customer_category(db, customer_id, category_name)
    return {"success": "true", "message": "Categoty name updated!"}

@router.get('/delete-customer-category') 
async def delete_customer_category(customer_id: int, db: Session = Depends(get_db)):
    if not customer_id:
        raise HTTPException(
            status_code=400,
            detail="customer_id is required"
        )
    await crud.delete_customer_category(db, customer_id)
    return {"success": "true"}

@router.post('/delete-customer-categories')
async def delete_customer_categories(customer_ids: List[int], db: Session = Depends(get_db)):
    print("DELETE - delete customer_ids: ", customer_ids)
    if not customer_ids:
        raise HTTPException(
            status_code=400,
            detail="customer_ids are required"
        )
    # Call the CRUD function to delete categories
    deleted_count = await crud.delete_customer_categories(db, customer_ids)
    if deleted_count == 0:
        return {"success": "false", "message": "No categories were deleted"}
    return {"success": "true", "deleted_count": deleted_count, "message": "Selected categories were deleted!"}

@router.get('/get-phone')
async def get_phone_route(email: Annotated[str, Depends(get_current_user)], phone_id: int = None, phone_number: str = None, customer_id: int = None, db: Session = Depends(get_db)):
    """Get phone record(s) by id, number or customer_id"""
    if phone_id:
        phone = await crud.get_phone(db, phone_id)
        return phone if phone else {"error": "Phone not found"}
    elif phone_number:
        phone = await crud.get_phone_by_number(db, phone_number)
        return phone if phone else {"error": "Phone not found"}
    elif customer_id:
        phones = await crud.get_phones_by_customer(db, customer_id)
        return phones if phones else {"error": "No phones found for customer"}
    else:
        # Return all phones if no specific query
        phones = await crud.get_phone_table(db)
        return phones if phones else {"error": "No phones found"}

@router.get('/phone-table')
async def get_phone_table(db: Session = Depends(get_db)):
    phones = await crud.get_phone_table(db)
    return phones if phones else {"error": "No phones found"}

@router.post('/add-phone')
async def add_phone_route(phone: PhoneModel, email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    """Add a new phone record"""
    try:
        new_phone = await crud.create_phone(
            db,
            phone_number=phone.phone_number,
            customer_id=phone.customer_id,
            opt_in_status=phone.opt_in_status
        )
        return new_phone
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post('/update-phone')
async def update_phone_route(phone_id: int, phone: PhoneModel, email: Annotated[str, Depends(get_current_user)], db: Session = Depends(get_db)):
    """Update an existing phone record"""

    try:
        updated_phone = await crud.update_phone(
            db,
            phone_id,
            phone_number=phone.phone_number,
            customer_id=phone.customer_id,
            opt_in_status=phone.opt_in_status,
            sent_timestamp=phone.sent_timestamp,
            back_timestamp=phone.back_timestamp
        )
        if updated_phone:
            # return updated_phone
            return {"success": "true", "updated_phone" : updated_phone}
        raise HTTPException(
            status_code=404,
            detail="Phone not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get('/delete-phone')
async def delete_phone_route(email: Annotated[str, Depends(get_current_user)], phone_id: int, db: Session = Depends(get_db)):
    """Delete a phone record"""
    try:
        success = await crud.delete_phone(db, phone_id)
        if success:
            return {"success": "true"}
        raise HTTPException(
            status_code=404,
            detail="Phone not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get('/get-optin-message')
async def get_optin_message(db: Session = Depends(get_db)):
    message = await crud.get_optin_message(db)
    return message

@router.post('/update-optin-message')
async def update_optin_message(data: dict, db: Session = Depends(get_db)):
    print("dashboard - update optin message data: ", data)
    await crud.update_optin_message(db, data.get('optin_message'))
    return {"success": "true"}


@router.post("/confirm-optin-response")
async def confirm_optin_response(Body: str = Form(...), From: str = Form(...), db: Session = Depends(get_db)):
    incoming_msg = Body.strip().upper()
    From = From.replace(' ', '')
    print("dashboard - From: ", From)
    # Create a Twilio MessagingResponse object
    response = MessagingResponse()
    
    # Check if the incoming message is a recognized keyword
    if incoming_msg == "#NO" or incoming_msg == "NO":
        print("dashboard - incoming_msg:", incoming_msg)
        await crud.update_opt_in_status_phone(db, From, 3)

        response.message("You have been unsubscribed from messages. Reply with #START to subscribe again.")
        
    elif incoming_msg == "#YES" or incoming_msg == "YES":
        print("dashboard - incoming_msg:", incoming_msg)
        await crud.update_opt_in_status_phone(db, From, 2)
        response.message("You have been subscribed to messages.")
        
    else:
        print("dashboard - incoming_msg:", incoming_msg)
        # The message is not a recognized keyword
        response.message("Sorry, we did not understand your message. Reply with #STOP to unsubscribe or #START to subscribe.")

    print("dashboard - response: ", response)
    return Response(content=str(response), media_type="application/xml")
