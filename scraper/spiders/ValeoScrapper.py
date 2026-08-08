from scraper.abstractScraper import AbstractScraper
from scraper.utils import jobOffer
import requests


# url = "https://valeo.wd3.myworkdayjobs.com/wday/cxs/valeo/valeo_jobs/jobs"
# 
# payload = {
    # "appliedFacets": {
        # "locationCountry": [
            # "d865e83093ad42319653b08e61f7db49"
        # ]
    # },
    # "limit": 20,
    # "offset": 0,
    # "searchText": ""
# }
# 
# response = requests.post(
    # url,
    # json=payload,
    # timeout=10
# )
# 
# response.raise_for_status()
# 
# data = response.json()
# 
# print(data)
class ValeoScrapper(AbstractScraper):
    def __init__(self):
        super().__init__(name="Valeo", url="https://valeo.wd3.myworkdayjobs.com/wday/cxs/valeo/valeo_jobs/jobs")
        self.EGYPT_LOCATION_ID = "d865e83093ad42319653b08e61f7db49"
    def _build_payload(self, offset: int = 0, limit: int = 20, search_text: str = "") -> dict:
        return {
            "appliedFacets": {
                "locationCountry": [self.EGYPT_LOCATION_ID]
            },
            "limit": limit,
            "offset": offset,
            "searchText": search_text
        }    
    def _fetch_jobs(self, offset: int = 0, limit: int = 20) -> dict:
        payload = self._build_payload(offset=offset, limit=limit)
        response = requests.post(self.corporate_url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    def get_offers_keyword(self, keyword):
        pass
    def get_offers(self):
        pass

if __name__ =="__main__":
    obj = ValeoScrapper()
    print(obj._fetch_jobs())