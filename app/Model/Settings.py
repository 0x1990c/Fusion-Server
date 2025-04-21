from pydantic import BaseModel
from typing import List, Optional

class SettingsModel(BaseModel):
    openAIKey: Optional[str]
    twilioPhoneNumber: Optional[str]
    twilioAccountSID: Optional[str]
    twilioAuthToken: Optional[str]
    sendgridEmail: Optional[str]
    sendgridApiKey: Optional[str]
    prompts: Optional[str]
    timer: Optional[int]