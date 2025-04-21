from pydantic import BaseModel
from datetime import datetime
from typing import List

class TimeRange(BaseModel):
    fromDate: datetime
    toDate: datetime

class FilterCondition(BaseModel):
    fromDate: datetime
    toDate: datetime
    offset: int
    selectedCaseTypes: List[str]
    selectedCourt: List[str]
    selectedCounty: List[str]
    