from dataclasses import dataclass
from datetime import datetime


@dataclass
class jobOffer:
    company: str
    title: str
    url: str
    location: str | None = None
    job_type: str | None = None
    deadline: datetime | None = None
