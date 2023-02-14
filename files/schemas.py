from pydantic import BaseModel


class FileInput(BaseModel):
    file: str
    file_name: str
