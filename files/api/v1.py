from fastapi import APIRouter, Request, Body, status
from app.database import File, User
from ..schemas import FileInput
from app.database import File
import PyPDF2
from base64 import b64decode
from io import BytesIO
import re

router = APIRouter()



@router.get("/user_files")
async def get_file(request: Request):
    user = await User.objects.get(id=request.user.id)
    files = await File.objects.all(user=user)
    return files


@router.get("/{file_id}")
async def get_file(file_id):
    return "File" + file_id


@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def create_file(request: Request, payload: FileInput = Body()):
    if payload.file.startswith('http'):
        print("Handle url file")
    file_index = payload.file.find("base64,") + 7
    file = payload.file[file_index:]
    pdf_file = BytesIO(b64decode(file))
    page_count = PyPDF2.PdfReader(stream=pdf_file, strict=False).getNumPages()
    await File.objects.create(user=request.user.id, file_name=payload.file_name, file=file, page_count=page_count)
    return {"status": "success"}


@router.delete("/{file_id}")
async def delete_file(file_id):
    return "File Deleted: " + file_id
