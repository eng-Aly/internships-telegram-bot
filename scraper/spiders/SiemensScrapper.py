import requests
from bs4 import BeautifulSoup

from scraper.abstractScraper import AbstractScraper
from scraper.utils import jobOffer


class SiemensScrapper(AbstractScraper):
    RECORDS_PER_PAGE = 6

    STATIC_PARAMS = {
        "42386": "[812002]",
        "42386_format": "17546",
        "listFilterMode": "1",
        "folderRecordsPerPage": str(RECORDS_PER_PAGE),
    }

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self):
        super().__init__(name="Siemens", url="https://jobs.siemens.com/en_US/externaljobs/SearchJobs/")
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _build_params(self, offset: int = 0) -> dict:
        params = dict(self.STATIC_PARAMS)
        if offset:
            params["folderOffset"] = str(offset)
        return params

    def _fetch_page(self, offset: int = 0) -> BeautifulSoup:
        response = self.session.get(self.corporate_url, params=self._build_params(offset), timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _parse_jobs(self, soup: BeautifulSoup) -> list[jobOffer]:
        """Extract job entries from a parsed results page."""
        jobs = []
        for heading in soup.select("h3 a[href*='/JobDetail/']"):
            title = heading.get_text(strip=True)
            url = heading["href"]
            if not url.startswith("http"):
                url = f"https://jobs.siemens.com{url}"

            h3 = heading.find_parent("h3")
            meta_el = h3.find_next(
                lambda tag: tag.name in ("p", "div", "span") and "Job ID:" in tag.get_text()
            )
            meta_text = meta_el.get_text(separator=" ", strip=True) if meta_el else ""

            # Format: "Location •  Job ID: XXXXX •  Field of work"
            segments = [s.strip() for s in meta_text.split("•")]
            location = segments[0] if segments else ""
            job_type = segments[2] if len(segments) > 2 else None

            jobs.append(jobOffer(
                company=self.name,
                title=title,
                url=url,
                location=location,
                job_type=job_type,
                deadline=None
            ))
        return jobs

    def get_offers(self):
        """Fetch all job listings across paginated results, deduplicated by URL."""
        all_jobs = []
        seen_urls = set()
        offset = 0

        while True:
            soup = self._fetch_page(offset)
            page_jobs = self._parse_jobs(soup)
            if not page_jobs:
                break

            new_jobs = [job for job in page_jobs if job.url not in seen_urls]
            if not new_jobs:
                break

            for job in new_jobs:
                seen_urls.add(job.url)
            all_jobs.extend(new_jobs)
            offset += self.RECORDS_PER_PAGE

        return all_jobs

    def get_offers_keyword(self, keyword) -> list[jobOffer]:
        jobs_list = self.get_offers()
        keyword = keyword.strip().lower()
        return [
            job for job in jobs_list
            if (
                keyword in job.title.lower()
                or keyword in job.location.lower()
                or (job.job_type and keyword in job.job_type.lower())
            )
        ]


if __name__ == "__main__":
    scrapper = SiemensScrapper()
    for job in scrapper.get_offers():
        print(job)