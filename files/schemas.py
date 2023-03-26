from pydantic import BaseModel
from datetime import datetime


class FileInput(BaseModel):
    file_name: str
    file: str
    size: int
    
class FileResponse(BaseModel):
    id: int
    file_name: str
    size: int
    created_at: datetime
    page_count: int

