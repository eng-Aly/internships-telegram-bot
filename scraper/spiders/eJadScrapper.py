import requests
from bs4 import BeautifulSoup

from scraper.abstractScraper import AbstractScraper
from scraper.utils import jobOffer


class EjadScrapper(AbstractScraper):
    CAREERS_URL = "https://pages.ejad.com/career"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self):
        super().__init__(name="eJad", url=self.CAREERS_URL)
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _fetch_page(self) -> BeautifulSoup:
        response = self.session.get(self.corporate_url, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _parse_jobs(self, soup: BeautifulSoup) -> list[jobOffer]:
        """Each job is an h3 heading (title + code) followed by an
        employment-type text line, all on one static page -- no pagination."""
        jobs = []

        for heading in soup.find_all("h3"):
            title = heading.get_text(strip=True)
            if not title:
                continue

            # Employment type ("Permanent Full Time") is the next
            # non-empty text node right after the title heading.
            job_type = None
            candidate = heading.find_next(string=True)
            while candidate and not candidate.strip():
                candidate = candidate.find_next(string=True)
            if candidate:
                job_type = candidate.strip()

            jobs.append(jobOffer(
                company=self.name,
                title=title,
                url=self.corporate_url,
                location=None,
                job_type=job_type,
                deadline=None,
            ))
        return jobs

    def get_offers(self) -> list[jobOffer]:
        """No pagination -- everything's on one page."""
        soup = self._fetch_page()
        return self._parse_jobs(soup)

    def get_offers_keyword(self, keyword) -> list[jobOffer]:
        jobs_list = self.get_offers()
        keyword = keyword.strip().lower()
        return [
            job for job in jobs_list
            if keyword in job.title.lower()
            or (job.job_type and keyword in job.job_type.lower())
        ]


if __name__ == "__main__":
    scrapper = EjadScrapper()
    for job in scrapper.get_offers():
        print(job)