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
    def _build_job_url(self, external_path: str) -> str:
        job_path = external_path.removeprefix("/job/")

        return (
            "https://valeo.wd3.myworkdayjobs.com"
            f"/en-US/valeo_jobs/jobs/details/{job_path}"
            f"?locationCountry={self.EGYPT_LOCATION_ID}"
        )
    def get_offers(self) -> list[jobOffer]:
        offers = []
        offset = 0
        limit = 20

        while True:
            response = self._fetch_jobs(
                offset=offset,
                limit=limit
            )
            jobs = response.get("jobPostings", [])
            if not jobs:
                break
            for job in jobs:
                offers.append(
                    jobOffer(
                        company=self.name,
                        title=job["title"],
                        location=job["locationsText"],
                        job_type=None,
                        url=self._build_job_url(job["externalPath"])
                            
                    )
                )
            offset += len(jobs)
            total = response.get("total", 0)

            if offset >= total:
                break

        return offers    
    def get_offers_keyword(self, keyword):
        pass

if __name__ =="__main__":
    obj = ValeoScrapper()
    print("------------------------fetch method-------------------------------------")
    print(obj._fetch_jobs())
    print("--------------get jobs method--------------------------------------------")
    print(obj.get_offers())