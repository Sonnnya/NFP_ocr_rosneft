import json
from pathlib import Path

from pydantic import BaseModel

from app.llm import ask_model
from app.schemas.documents import Expense


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


def create_report_with_documents(documents: list[str], schema: type[BaseModel]):
    prompt = f"""
    You are an assistant for processing financial documents.
    Extract structured data from the documents below and create a report.
    Use the documents to fill the expences rows in report. For values use the original document language.

    Return ONLY valid JSON matching this schema:
    {schema.model_json_schema()}

    Document:
    <document>
    {documents}
    </document>
    """

    response = ask_model(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        raise ValueError("Model returned invalid JSON")


if __name__ == "__main__":
    _path = "./data/Образцы документов авансовый отчет/"
    REWRITE = False
    for _ocr_path in Path(_path).rglob("*.txt"):
        print(_ocr_path)
        with open(_ocr_path, "r", encoding="utf-8") as f:
            _ocr = f.read()

        if _ocr_path.with_suffix(".json").exists() and not REWRITE:
            print(f"{_ocr_path.with_suffix('.json')} already exists, skipping")
            continue

        data = extract_with_schema(_ocr, schema=Expense)

        with open(_ocr_path.with_suffix(".json"), "w", encoding="utf-8") as f:
            print(json.dumps(data, indent=2, ensure_ascii=False))
            json.dump(data, f, indent=2, ensure_ascii=False)

    documents = []
    for _json_path in Path(_path).rglob("*.json"):
        with open(_json_path, "r", encoding="utf-8") as f:
            documents.append(f.read())

    # report_path = Path(_path) / "report.json"
    # if report_path.exists() and not REWRITE:
    #     print(f"{report_path} already exists, skipping")
    # else:
    #     report = create_report_with_documents(documents, schema=Report)
    #     with open(report_path, "w", encoding="utf-8") as f:
    #         print(json.dumps(report, indent=2, ensure_ascii=False))
    #         json.dump(report, report_path, indent=2, ensure_ascii=False)
