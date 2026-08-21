import re
import requests
from bs4 import BeautifulSoup

from scraper.abstractScraper import AbstractScraper
from scraper.utils import jobOffer


class Blink22Scrapper(AbstractScraper):
    CAREERS_URL = "https://www.blink22.com/careers/"
    JOB_LINK_RE = re.compile(r"^/careers/[^/]+/?$")

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self):
        super().__init__(name="Blink22", url=self.CAREERS_URL)
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _fetch_page(self) -> BeautifulSoup:
        response = self.session.get(self.corporate_url, timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    @staticmethod
    def _preceding_text_blocks(link, count: int = 2) -> list[str]:
        """Walk backward from the Apply link, collecting the nearest
        non-empty text blocks (description, then title)."""
        results = []
        node = link
        seen_texts = set()
        while node is not None and len(results) < count:
            node = node.find_previous(["p", "div", "span", "h1", "h2", "h3", "h4", "h5", "h6"])
            if node is None:
                break
            text = node.get_text(strip=True)
            if not text or text.lower() == "apply" or text in seen_texts:
                continue
            # Stop if we've wandered back into a different job's card
            if node.find("a", href=Blink22Scrapper.JOB_LINK_RE):
                break
            seen_texts.add(text)
            results.append(text)
        return results

    def _parse_jobs(self, soup: BeautifulSoup) -> list[jobOffer]:
        jobs = []
        seen_urls = set()

        for link in soup.find_all("a", href=self.JOB_LINK_RE):
            href = link["href"]
            url = href if href.startswith("http") else f"https://www.blink22.com{href}"
            if url in seen_urls:
                continue
            seen_urls.add(url)

            blocks = self._preceding_text_blocks(link, count=2)
            # blocks[0] = description (closest), blocks[1] = title (further back)
            title = blocks[1] if len(blocks) > 1 else (blocks[0] if blocks else link.get_text(strip=True))

            jobs.append(jobOffer(
                company=self.name,
                title=title,
                url=url,
                location=None,
                job_type=None,
                deadline=None,
            ))
        return jobs

    def get_offers(self) -> list[jobOffer]:
        soup = self._fetch_page()
        return self._parse_jobs(soup)

    def get_offers_keyword(self, keyword) -> list[jobOffer]:
        jobs_list = self.get_offers()
        keyword = keyword.strip().lower()
        return [job for job in jobs_list if keyword in job.title.lower()]


if __name__ == "__main__":
    scrapper = Blink22Scrapper()
    for job in scrapper.get_offers():
        print(job)