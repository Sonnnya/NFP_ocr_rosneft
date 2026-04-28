import json
from pathlib import Path

from pydantic import BaseModel

from app.llm import ask_model
from app.schemas.documents import Expense, Report


def extract_with_schema(text: str, schema: type[BaseModel]) -> dict:
    prompt = f"""
    Extract structured data from the document below. For values use the original document language.

    Return ONLY valid JSON matching this schema:
    {schema.model_json_schema()}

    Document:
    <document>
    {text}
    </document>
    """
    response = ask_model(prompt)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        raise ValueError("Model returned invalid JSON")


def _format_documents_block(documents: list[dict]) -> str:
    """Render a list of parsed document dicts into clearly separated XML-style blocks."""
    parts = []
    for i, doc in enumerate(documents, start=1):
        parts.append(
            f'<document index="{i}">\n'
            f"{json.dumps(doc, ensure_ascii=False, indent=2)}\n"
            f"</document>"
        )
    return "\n\n".join(parts)


def create_report_from_documents(
    documents: list[dict],
    schema: type[BaseModel] = Report,
) -> dict:
    """
    Given a list of already-extracted document dicts (expenses, tickets, etc.),
    ask the model to compile them into a single Report JSON.

    Suitable for direct use or wrapping in a server route.
    """
    docs_block = _format_documents_block(documents)

    prompt = f"""
    You are an assistant for processing business-trip expense reports.

    You are given several financial documents that belong to one expense package.
    One of them is the main advance report; the rest are supporting documents (receipts, tickets, orders, etc.).

    Your task:
    1. Identify the main report document and extract its header fields (company, person, dates, etc.).
    2. Map each supporting document to an expense row and fill the `expenses` list.
    3. Return ONLY valid JSON that matches the schema below — no explanation, no markdown fences.

    Schema:
    {schema.model_json_schema()}

    Documents:
    {docs_block}
    """

    response = ask_model(prompt)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        raise ValueError(f"Model returned invalid JSON:\n{response}")


if __name__ == "__main__":
    _path = Path("./data/Образцы документов авансовый отчет/")
    REWRITE = False

    # --- Step 1: extract each OCR text into its own JSON ---
    for _ocr_path in _path.rglob("*.txt"):
        print(_ocr_path)
        json_path = _ocr_path.with_suffix(".json")
        if json_path.exists() and not REWRITE:
            print(f"  {json_path} already exists, skipping")
            continue

        with open(_ocr_path, encoding="utf-8") as f:
            ocr_text = f.read()

        data = extract_with_schema(ocr_text, schema=Expense)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    # --- Step 2: load all extracted JSONs and compile the report ---
    documents: list[dict] = []
    for _json_path in _path.rglob("*.json"):
        if _json_path.name == "report.json":
            continue  # don't feed a previous report back in
        with open(_json_path, encoding="utf-8") as f:
            documents.append(json.load(f))

    report_path = _path / "report.json"
    if report_path.exists() and not REWRITE:
        print(f"{report_path} already exists, skipping")
    else:
        report = create_report_from_documents(documents, schema=Report)
        with open(
            report_path, "w", encoding="utf-8"
        ) as f:  # <- was passing Path, not f
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(json.dumps(report, indent=2, ensure_ascii=False))
