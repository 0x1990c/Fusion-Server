from sqlalchemy.orm import Session
from database import AsyncSessionLocal
import app.Utils.database_handler as crud
from app.Utils.chatgpt import get_last_message
import requests
from datetime import datetime
from pydantic import BaseModel
import time
class AuthModel(BaseModel):
    source: str
    builder_user: str
    builder_pass: str
    xact_user: str
    xact_pass: str

import asyncio
import aiohttp

async def send_notification(json_data):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://108.61.203.106/api/v1/notification', json=json_data) as response:
            # Not waiting for the response
            pass

async def job(source: str):
    print("Scraping started!")

    # Create an instance of AuthModel with your credentials
    auth_data = AuthModel(
        source=source,
        builder_user='Angelab@getdelmar.com',
        builder_pass='Liamb0218.',
        xact_user='Angelab@getdelmar.com',
        xact_pass='Liamb0218$'
    )
    
    json_data = auth_data.dict()
    print(source)
    # response = requests.post('https://api.cultuurtickets.nl/buildertrend/api/v1/notification', json=json_data)
    task = asyncio.create_task(send_notification(json_data))
    await task
    return


def process_phone_number(phone):  
    phone = phone.replace("Call", "")  
    phone = phone.replace(" ", "")  
    phone = phone.replace('(', '')  
    phone = phone.replace(')', '')  
    phone = phone.replace('-', '')  
    phone = phone.replace('.', '')  
    if len(phone) < 5:  
        return ""  
    if '+' in phone:  
        return phone  
    else:  
        return '+1' + phone  
        

async def update_notification(db: Session):
    
    # reports_list = await crud.get_reports_by_project_id(db, 80)
    # tmp = ""
    # for report in reports_list:
    #     tmp += report.message + '\n'
    # print("message for Mike Hudek: ", tmp)
    
    
    project_list = await crud.get_all_projects(db)
    print('regular_update - project_list: ', project_list)
    count = 0
    status = await crud.get_status(db)
    if status is not None:
        await crud.update_rerun_status(db, status.id, len(project_list), count)
    for project in project_list:
        try:
            count += 1
            print("regular_update - customer_id: ", project.customer_id)
            print("regular_update - project_id: ", project.id)
            customer = await crud.get_customer(db, project.customer_id)
            reports_list = await crud.get_reports_by_project_id(db, project.id)
            # Get personalized message based on reports
            last_message = await get_last_message(db, customer.manager_name, customer.manager_phone, customer.manager_email, reports_list, customer.first_name + ' ' + customer.last_name)
            await crud.update_project(db, project.id, last_message=last_message)
            if status is not None:
                await crud.update_rerun_status(db, status.id, len(project_list), count)
        except Exception as e:
            print(e)

    if status is not None:
        await crud.set_db_update_status(db, status.id, 1)

async def update_database(data):    
    # Start a new SQLAlchemy session
    db = AsyncSessionLocal()
    status = await crud.get_status(db)
    project_total = len(data)
    project_current = 0
    if status is not None:
        await crud.update_rerun_status(db, status.id, project_total, project_current)
    
    for report in data:
        project_current += 1
        try:
            first_name = report['first_name'].capitalize()
            last_name = report['last_name'].capitalize()
            phone = report['phone']
            phone = process_phone_number(phone)
            print("phone: ", phone)
            address = report['address']
            email = report['email']
            note_list = report['reports']
            claim_number = report['claim_number']
            project_name = report['project_name']
            manager_name = report['manager_name']
            manager_phone = report['manager_phone']
            manager_phone = process_phone_number(manager_phone)
            manager_email = report['manager_email']
            
            # Insert the customer into the database and get the customer_id
            customer = await crud.insert_customer(db,  manager_name, manager_phone, manager_email, first_name, last_name, email, phone, address)
                
            send_method = customer.sending_method
            print("regular_update - send_method: ", send_method)
            print("regular_update - customer_id: ", customer.id)
            
            # Insert the project into the database and get the project_id
            project = await crud.insert_project(db, claim_number, customer.id, project_name)
            print("project_id: ", project.id)
            
            await crud.update_project(db, project.id, message_status=send_method, qued_timestamp=datetime.utcnow())
            
            flag = 0
            # Insert each report into the database
            for message in note_list:
                print('++++++++++++++++++++++++++++++++++++++')
                print(project.id, "--\n", message['title'] + message['note'])
                print('++++++++++++++++++++++++++++++++++++++')
                flag = 1
                try:
                    await crud.insert_report(db, project.id, message['title'] + '\n' + message['note'] + '\n' + message['date'], message['date'])
                except Exception as e:
                    print("------------------------------------------")
                    print(project.id, "--\n", message['title'] + message['note'])
                    print('===')
                    print(e)
                    print("------------------------------------------")
            print('regular_update - flag', flag)
            if flag == 1:
                # Get all reports in this claim
                try:
                    reports_list = await crud.get_reports_by_project_id(db, project.id)
                    # Get personalized message based on reports
                    print("reposts_list: ", reports_list)
                    last_message = await get_last_message(db, manager_name, manager_phone, manager_email, reports_list, first_name + ' ' + last_name)
                    print('regular_update - last_message: ', last_message)
                    # Save message in this claim
                    await crud.update_project(db, project.id, last_message=last_message)
                    
                except Exception as e:
                    print('++++++++++++++++++++++++++++++++++++++')
                    print(project.id)
                    print(e)
                    print('+++++++++++++++++++++++++++++++++++++++')
        except Exception as e:
            print(e)
        if status is not None:
            await crud.update_rerun_status(db, status.id, project_total, project_current)
    if status is not None:
        project_list = await crud.get_all_projects(db)
        await crud.update_rerun_status(db, status.id, len(project_list), len(project_list))
    print("DB updated!")
    
    variables = await crud.get_variables(db)
    if variables is not None:
        await crud.set_db_update_status(db, variables.id, 1)
    # db.close()