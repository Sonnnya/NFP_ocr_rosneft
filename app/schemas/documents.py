from enum import Enum
from typing import List

from pydantic import BaseModel


class DocumentKind(str, Enum):
    REPORT = "Авансовый отчет"
    CHECK = "Чек"
    TICKET = "Билет"
    ORDER = "Приказ"
    REQUiSITION = "Заявление"
    OTHER = "Другое"


class CurrencyType(str, Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class Document(BaseModel):
    number: str
    name: str
    date: str

    kind: DocumentKind

    # accountable_person: str | None
    # signed_by_director: bool | None


class Expense(Document):
    sum_main: float
    sum_currency: float
    account: str
    currency: CurrencyType


class Report(Document):
    company_name: str
    accountable_person: str
    branch: str
    director: str
    chief_accountant: str
    accountant: str
    currency: CurrencyType
    comment: str
    expenses: List[Expense]
