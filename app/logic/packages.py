"""
app/logic/packages.py

ZIP → OCR → extract → report pipeline.
All I/O stays in-memory; nothing is written to disk.

Blocking work (OCR inference, LLM calls) is offloaded to a thread pool
via asyncio.to_thread() so the FastAPI event loop stays free.
Per-file LLM extractions are fanned out concurrently with asyncio.gather().
"""

import asyncio
import io
import logging
import zipfile
from dataclasses import dataclass, field

from PIL import Image

from app.logic.documents import create_report_from_documents, extract_with_schema
from app.ocr.surya import ocr_surya, parse_result
from app.schemas.documents import Expense, Report

logger = logging.getLogger(__name__)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".webp"}


# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------


@dataclass
class RawFile:
    filename: str
    data: bytes


@dataclass
class ProcessedFile:
    filename: str
    text: str
    extracted: dict


@dataclass
class PackageResult:
    report: Report
    processed: list[ProcessedFile] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Step 1 — unzip  (pure CPU/memory, fast enough to run inline)
# ---------------------------------------------------------------------------


def unzip(zip_bytes: bytes) -> list[RawFile]:
    results: list[RawFile] = []

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for entry in zf.infolist():
            if entry.is_dir():
                continue

            filename = entry.filename
            if filename.startswith("__MACOSX") or filename.startswith("."):
                continue

            suffix = (
                "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            )
            if suffix not in IMAGE_SUFFIXES:
                logger.debug("Skipping unsupported file: %s", filename)
                continue

            results.append(RawFile(filename=filename, data=zf.read(entry)))
            logger.info("Unpacked: %s", filename)

    if not results:
        raise ValueError("ZIP contains no supported image files (.jpg, .png, .tiff, …)")

    return results


# ---------------------------------------------------------------------------
# Step 2 — OCR  (CPU-bound — offload to thread pool)
# ---------------------------------------------------------------------------


def _bytes_to_pil(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")


def _run_ocr(raw_files: list[RawFile]) -> list[tuple[RawFile, str]]:
    """Blocking OCR — called inside a thread via asyncio.to_thread."""
    images = [_bytes_to_pil(f.data) for f in raw_files]
    results = ocr_surya(images)  # one batched forward pass
    texts = [parse_result(r) for r in results]
    return list(zip(raw_files, texts))


async def ocr_files(raw_files: list[RawFile]) -> list[tuple[RawFile, str]]:
    """Non-blocking wrapper: runs Surya in a thread pool."""
    logger.info("Starting OCR for %d file(s)", len(raw_files))
    return await asyncio.to_thread(_run_ocr, raw_files)


# ---------------------------------------------------------------------------
# Step 3 — per-document LLM extraction  (I/O-bound — fan out concurrently)
# ---------------------------------------------------------------------------


async def _extract_one(raw: RawFile, text: str) -> ProcessedFile | None:
    """Extract a single document; returns None if it should be skipped."""
    if not text.strip():
        logger.warning("Empty OCR for %s — skipping", raw.filename)
        return None

    try:
        # ask_model is a blocking sync call — run it in a thread so all
        # per-file extractions can proceed concurrently via gather()
        extracted = await asyncio.to_thread(extract_with_schema, text, Expense)
        logger.info("Extracted: %s", raw.filename)
        return ProcessedFile(filename=raw.filename, text=text, extracted=extracted)
    except ValueError as e:
        logger.error("Extraction failed for %s: %s", raw.filename, e)
        return None


async def extract_documents(
    ocr_pairs: list[tuple[RawFile, str]],
) -> tuple[list[ProcessedFile], list[str]]:
    """
    Fan out all per-file LLM calls concurrently.
    Returns (processed, skipped_filenames).
    """
    tasks = [_extract_one(raw, text) for raw, text in ocr_pairs]
    results = await asyncio.gather(*tasks)  # all LLM calls in parallel

    processed: list[ProcessedFile] = []
    skipped: list[str] = []

    for (raw, _), result in zip(ocr_pairs, results):
        if result is None:
            skipped.append(raw.filename)
        else:
            processed.append(result)

    return processed, skipped


# ---------------------------------------------------------------------------
# Step 4 — assemble report  (one final LLM call — offload to thread)
# ---------------------------------------------------------------------------


async def assemble_report(processed: list[ProcessedFile]) -> Report:
    documents = [p.extracted for p in processed]
    report_dict = await asyncio.to_thread(
        create_report_from_documents, documents, Report
    )
    return Report.model_validate(report_dict)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


async def process_zip(zip_bytes: bytes) -> PackageResult:
    """
    Full async pipeline: ZIP bytes → PackageResult.
    The event loop is never blocked; all heavy work runs in threads.
    """
    raw_files = unzip(zip_bytes)  # fast, inline is fine
    ocr_pairs = await ocr_files(raw_files)  # ~slow, in thread pool
    processed, skipped = await extract_documents(ocr_pairs)  # concurrent LLM calls

    if not processed:
        raise ValueError(
            f"No documents could be extracted. Skipped: {skipped or 'none'}"
        )

    report = await assemble_report(processed)  # final LLM call

    return PackageResult(report=report, processed=processed, skipped=skipped)
