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
    company_name: str | None = None
    accountable_person: str | None = None
    branch: str | None = None
    director: str | None = None
    chief_accountant: str | None = None
    accountant: str | None = None
    currency: CurrencyType = CurrencyType.RUB
    comment: str | None = None
    expenses: List[Expense] = []
