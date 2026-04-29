"""
app/api/packages.py
"""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.logic.packages import extract_documents, ocr_files, process_zip, unzip
from app.schemas.documents import Report

router = APIRouter(prefix="/packages", tags=["packages (.zips)"])


@router.post("/report/make/", response_model=Report)
async def make_report(
    file: Annotated[
        UploadFile, File(description=".zip archive of scanned document images")
    ],
) -> JSONResponse:
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are accepted")

    zip_bytes = await file.read()

    try:
        result = await process_zip(zip_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    headers = {}
    if result.skipped:
        headers["X-Skipped-Files"] = ", ".join(result.skipped)

    return JSONResponse(content=result.report.model_dump(), headers=headers)


@router.post("/report/validate/")
async def validate_report(
    file: Annotated[
        UploadFile, File(description=".zip archive of scanned document images")
    ],
):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are accepted")

    zip_bytes = await file.read()

    try:
        raw_files = unzip(zip_bytes)
        ocr_pairs = await ocr_files(raw_files)
        processed, skipped = await extract_documents(ocr_pairs)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "processed": [
            {"filename": p.filename, "extracted": p.extracted} for p in processed
        ],
        "skipped": skipped,
    }
