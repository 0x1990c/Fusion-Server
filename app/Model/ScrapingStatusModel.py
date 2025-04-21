from pydantic import BaseModel
from typing import List, Optional

class ScrapingStatusModel(BaseModel):
    buildertrend_total: Optional[int] = -1
    buildertrend_current: Optional[int] = -1
    xactanalysis_total: Optional[int] = -1
    xactanalysis_current: Optional[int] = -1