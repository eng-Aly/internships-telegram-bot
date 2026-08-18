import requests
from bs4 import BeautifulSoup

from scraper.abstractScraper import AbstractScraper
from scraper.utils import jobOffer


class ElsewedyScrapper(AbstractScraper):
    PAGE_URL_TEMPLATE = "https://www.elsewedy.net/careers-2/page/{page}/"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self):
        super().__init__(name="Elsewedy", url="https://www.elsewedy.net/careers-2/")
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _fetch_page(self, page: int = 1) -> BeautifulSoup:
        url = self.PAGE_URL_TEMPLATE.format(page=page)
        response = self.session.get(url, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _parse_jobs(self, soup: BeautifulSoup) -> list[jobOffer]:
        """Extract job entries from a parsed careers listing page."""
        jobs = []
        seen_on_page = set()

        for link in soup.select("a[href*='/job/']"):
            title = link.get_text(strip=True)
            url = link.get("href", "")

            # Skip the duplicate "View" links and empty/anchor-only matches
            if not title or title.lower() == "view" or url in seen_on_page:
                continue
            seen_on_page.add(url)

            # Employment type ("Full-time") sits as plain text right after the
            # title heading, before the "View" link -- best-effort extraction.
            job_type = None
            heading = link.find_parent(["h1", "h2", "h3", "h4", "h5", "h6"])
            if heading:
                candidate = heading.find_next(string=True)
                while candidate and not candidate.strip():
                    candidate = candidate.find_next(string=True)
                if candidate:
                    text = candidate.strip()
                    if text and text.lower() != "view":
                        job_type = text

            jobs.append(jobOffer(
                company=self.name,
                title=title,
                url=url,
                location=None,
                job_type=job_type,
                deadline=None,
            ))
        return jobs

    def get_offers(self) -> list[jobOffer]:
        """Fetch all job listings across paginated results, deduplicated by URL."""
        all_jobs = []
        seen_urls = set()
        page = 1

        while True:
            soup = self._fetch_page(page)
            page_jobs = self._parse_jobs(soup)
            if not page_jobs:
                break

            new_jobs = [job for job in page_jobs if job.url not in seen_urls]
            if not new_jobs:
                break

            for job in new_jobs:
                seen_urls.add(job.url)
            all_jobs.extend(new_jobs)
            page += 1

        return all_jobs

    def get_offers_keyword(self, keyword) -> list[jobOffer]:
        jobs_list = self.get_offers()
        keyword = keyword.strip().lower()
        return [
            job for job in jobs_list
            if keyword in job.title.lower()
            or (job.job_type and keyword in job.job_type.lower())
        ]


if __name__ == "__main__":
    scrapper = ElsewedyScrapper()
    for job in scrapper.get_offers():
        print(job)