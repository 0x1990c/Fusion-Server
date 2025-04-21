from pydantic import BaseModel
from typing import List, Optional

class LastMessageModel(BaseModel):
    project_id: Optional[int] = None
    message: Optional[str] = None
    
