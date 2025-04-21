from pydantic import BaseModel
from typing import List, Optional
from fastapi import Form
from datetime import datetime

class MainTableModel(BaseModel):
    last_message: Optional[str] = None
    message_status: Optional[int] = None
    categories: Optional[List[int]] = None
    phone_numbers: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    qued_timestamp: Optional[datetime] = None
    sent_timestamp: Optional[datetime] = None
    num_sent: Optional[int] = None
    sent_success: Optional[int] = None
    image_url: Optional[str] = None
    
    
class MessageModel(BaseModel):
    message: Optional[str]
    sent_timestamp: Optional[datetime]
    phone_numbers: Optional[List[str]]
    opt_in_status: Optional[int]
    categories: Optional[List[int]]
    
    
# Add this class near the top with other models
class PhoneModel(BaseModel):
    phone_number: str
    customer_id: int
    opt_in_status: Optional[int] = None
    sent_timestamp: Optional[datetime] = None
    back_timestamp: Optional[datetime] = None
    
    
    
