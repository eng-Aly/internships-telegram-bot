from dataclasses import dataclass
from datetime import datetime


@dataclass
class InternshipOffer:
    company: str
    title: str
    url: str
    location: str | None = None
    deadline: datetime | None = None
