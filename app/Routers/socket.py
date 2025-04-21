from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.Utils.database_handler import get_message_num_sent, get_phone_table
from database import AsyncSessionLocal
import asyncio
from typing import List
from datetime import datetime

router = APIRouter()

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
        
        
# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.websocket("/ws-message")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
   
    try:
        print("websocket_endpoint message accept")
        prev_data = []
        while True and websocket.client_state == WebSocket.OPEN:
            # Query the database
            main_table_data = None
            async with AsyncSessionLocal() as session:
                main_table_data = await get_message_num_sent(session, datetime.now())
            
            if main_table_data:
                # print("main_table_data: ", main_table_data)
                # print("prev_data: ", prev_data)
                
                if(prev_data != main_table_data):
                    prev_data = main_table_data    # Convert data to a list of dictionaries

                    data_list = [
                        {
                            "id": item.id,
                            "num_sent": item.num_sent,
                        }
                        for item in main_table_data
                    ]
                
                    # Send the data even if the list is empty to notify frontend of no data
                    data_to_send = {
                        "type": "MESSAGE_UPDATE",
                        "data": data_list
                    }
                    if data_list:
                        await websocket.send_json(data_to_send)
               
            
            # Reduce sleep time for more frequent updates
            await asyncio.sleep(2)
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        await websocket.close()

@router.websocket("/ws-phone")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    print("websocket_endpoint")
    # await websocket.accept()
    # try:
    #     while True:
    #         # Query the database
    #         phone_table_data = await get_phone_table(db)
    #         print("phone_table_data: ", phone_table_data)
    #         # Convert data to a list of dictionaries, even if empty
    #         data_list = [
    #             {
    #                 "id": item.id,
    #                 "phone_number": item.phone_number,
    #                 "optin_status": item.optin_status,
    #                 "sent_timestamp": item.sent_timestamp,
    #                 "back_timestamp": item.back_timestamp,
    #                 "categories": item.categories
    #             }
    #             for item in phone_table_data or []
    #         ]
            
    #         # Always send update to client
    #         data_to_send = {
    #             "type": "PHONE_UPDATE",
    #             "data": data_list
    #         }
    #         if data_list:
    #             await websocket.send_json(data_to_send)
            
    #         # Reduce sleep time for more frequent updates
    #         await asyncio.sleep(0.5)
            
    # except Exception as e:
    #     print(f"Connection closed: {e}")
    # finally:
    #     await websocket.close()