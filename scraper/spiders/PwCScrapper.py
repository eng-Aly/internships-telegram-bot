from scraper.abstractScraper import AbstractScraper
from scraper.utils import jobOffer
import requests

class PwCScrapper(AbstractScraper):
    BASE_URL = "https://pwc.wd3.myworkdayjobs.com/wday/cxs/pwc/Global_Campus_Careers/jobs"
    JOB_DETAIL_BASE = "https://pwc.wd3.myworkdayjobs.com/Global_Campus_Careers"
    PAGE_SIZE = 20

    CAIRO_ETIC_LOCATION_ID = "3f65865fb3201000e97aa22899830000"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    def __init__(self):
        super().__init__(name="PwC", url=self.BASE_URL)
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _build_payload(self, offset: int = 0, search_text: str = "") -> dict:
        return {
            "appliedFacets": {
                "locations": [self.CAIRO_ETIC_LOCATION_ID]
            },
            "limit": self.PAGE_SIZE,
            "offset": offset,
            "searchText": search_text,
        }

    def _fetch_page(self, offset: int = 0) -> dict:
        response = self.session.post(
            self.corporate_url,
            json=self._build_payload(offset=offset),
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def _parse_jobs(self, data: dict) -> list[jobOffer]:
        jobs = []
        for posting in data.get("jobPostings", []):
            title = posting.get("title", "").strip()
            location = posting.get("locationsText", "").strip()
            path = posting.get("externalPath", "")
            url = f"{self.JOB_DETAIL_BASE}{path}" if path else ""

            jobs.append(jobOffer(
                company=self.name,
                title=title,
                url=url,
                location=location,
                job_type=posting.get("timeType"),
                deadline=None,
            ))
        return jobs

    def get_offers(self) -> list[jobOffer]:
        """Fetch all Cairo-location postings across paginated results, deduped by URL."""
        all_jobs = []
        seen_urls = set()
        offset = 0

        while True:
            data = self._fetch_page(offset)
            total = data.get("total", 0)
            page_jobs = self._parse_jobs(data)
            if not page_jobs:
                break

            new_jobs = [job for job in page_jobs if job.url not in seen_urls]
            for job in new_jobs:
                seen_urls.add(job.url)
            all_jobs.extend(new_jobs)

            offset += self.PAGE_SIZE
            if offset >= total:
                break

        return all_jobs

    def get_offers_keyword(self, keyword) -> list[jobOffer]:
        jobs_list = self.get_offers()
        keyword = keyword.strip().lower()
        return [
            job for job in jobs_list
            if keyword in job.title.lower() or keyword in job.location.lower()
        ]


if __name__ == "__main__":
    scrapper = PwCScrapper()
    for job in scrapper.get_offers():
        print(job)