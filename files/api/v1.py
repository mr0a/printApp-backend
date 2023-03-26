from fastapi import APIRouter, Request, Body, status, HTTPException
from app.database import File, User
from ..schemas import FileInput, FileResponse
from app.database import File
import PyPDF2
from base64 import b64decode
from io import BytesIO
import re

router = APIRouter()



@router.get("/user_files", response_model=list[FileResponse])
# @router.get("/user_files")
async def get_files(request: Request):
    user = await User.objects.get(id=request.user.id)
    files = await File.objects.all(owner=user)
    # files = list(map( lambda file: {"file_name": file.file_name}, files))
    return files


@router.get("/file/{file_id}", response_model=FileResponse)
async def get_file(request: Request, file_id):
    user = await User.objects.get(id=request.user.id)
    file = await File.objects.get_or_none(pk=file_id, owner=user)
    if file is None:
        raise HTTPException(status_code=404, detail="File Not Found")
    return File


@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def create_file(request: Request, payload: FileInput = Body()):
    if payload.file.startswith('http'):
        print("Handle url file")
    file_index = payload.file.find("base64,") + 7
    file = payload.file[file_index:]
    pdf_file = BytesIO(b64decode(file))
    page_count = PyPDF2.PdfReader(stream=pdf_file, strict=False).getNumPages()
    await File.objects.create(owner=request.user.id, file_name=payload.file_name, file=file, size=payload.size, page_count=page_count)
    return {"status": "success"}


@router.delete("/{file_id}")
async def delete_file(request: Request, file_id):
    count = await File.objects.delete(pk=file_id, owner=request.user.id)
    if count == 0:
        raise HTTPException(status_code=404, detail="File Not Found")
    return {"success": True}
