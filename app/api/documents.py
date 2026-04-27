from fastapi import APIRouter, File, UploadFile
from schemas import Report

from app.schemas.documents import Document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
async def upload_documents(files: list[UploadFile] = File(...)):
    pass


@router.post("/get_text")
async def get_text_from_documents(files: list[UploadFile] = File(...)):
    pass


@router.post("/recognize")
async def recognize_documents(files: list[UploadFile] = File(...)) -> list[Document]:
    pass


@router.post("/get_report")
async def get_report(files: list[UploadFile] = File(...)) -> Report:
    pass
