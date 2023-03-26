from pydantic import BaseModel


class FileConfigBase(BaseModel):
    file_id: int
    copies: int
    price: int
    sheetSize: str
    # page_selection: str

class OrderBase(BaseModel):
    repro: str
    total_amount: int
    payment_method: str
    files: list[FileConfigBase]

