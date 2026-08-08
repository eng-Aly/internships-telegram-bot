from abc import ABC, abstractmethod
from .utils import jobOffer


class AbstractScraper(ABC):

    def __init__(self, name: str, url: str):
        self.name = name
        self.corporate_url = url


    @abstractmethod
    def get_offers(self) -> list[jobOffer]:
        """Scrape and return all currently available internship offers."""
        pass  
    
    @abstractmethod
    def get_offers_keyword(self,keyword) -> list[jobOffer]:
        """Scrape and return all currently available internship offers with a certain keyword in it."""
        pass