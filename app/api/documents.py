from typing import Annotated, List

from fastapi import APIRouter, File, UploadFile

from app.schemas import Report
from app.schemas.documents import Document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload_one/")
async def upload_file(
    file: Annotated[UploadFile, File(description="Upload a single file")],
):
    return {"message": "Files uploaded successfully", "files": results}


@router.post("/upload/")
async def upload_files(
    files: Annotated[List[UploadFile], File(description="Upload multiple files")],
):
    results = []
    for file in files:
        content = await file.read()
        with open(file.filename, "wb") as f:
            f.write(content)
        results.append({"filename": file.filename, "size": len(content)})
    return {"message": "Files uploaded successfully", "files": results}


@router.post("/get_text")
async def get_text_from_documents(
    files: Annotated[List[UploadFile], File(description="Upload multiple files")],
):
    pass


@router.post("/recognize")
async def recognize_documents(files: list[UploadFile] = File(...)) -> list[Document]:
    pass


@router.post("/get_report")
async def get_report(files: list[UploadFile] = File(...)) -> Report:
    pass
