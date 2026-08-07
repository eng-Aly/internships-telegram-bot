from abc import ABC, abstractmethod
from utils import InternshipOffer


class AbstractScraper(ABC):

    def __init__(self, name: str, url: str):
        self.name = name
        self.corporate_url = url

    
    @abstractmethod
    def get_offer(self) -> InternshipOffer:
        """Scrape and return all currently available internship offers."""
        pass

    @abstractmethod
    def get_offers(self) -> list[InternshipOffer]:
        """Scrape and return all currently available internship offers."""
        pass  