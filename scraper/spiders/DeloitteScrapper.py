from scraper.abstractScraper import AbstractScraper
from scraper.utils import jobOffer
import requests
from bs4 import BeautifulSoup


import re
import unicodedata


class DeloitteScrapper(AbstractScraper):
    RECORDS_PER_PAGE = 6

    STATIC_PARAMS = {
        "9570": "[25581143]",
        "9570_format": "11920",
        "listFilterMode": "1",
        "pipelineRecordsPerPage": str(RECORDS_PER_PAGE),
    }

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # Extend this list as new office locations turn up in future scrapes.
    KNOWN_LOCATIONS = [
        "Multiple locations",
        "Middle East",
        "Saudi Arabia",
        "Cairo",
        "Alexandria",
        "Egypt",
        "Jordan",
        "Lebanon",
        "Amman",
        "Beirut",
        "Dubai",
        "Abu Dhabi",
        "UAE",
        "KSA",
        "Riyadh",
        "Jeddah",
        "Doha",
        "Qatar",
        "Kuwait",
        "Bahrain",
        "Oman",
        "Iraq",
        "Palestine",
    ]

    _TOKEN_PATTERN = "|".join(
        r"\b" + re.escape(loc) + r"\b"
        for loc in sorted(KNOWN_LOCATIONS, key=len, reverse=True)
    )
    # Matches a trailing run of known-location tokens, separated by
    # commas/periods/slashes/dashes, right at the end of the string.
    _TRAILING_LOCATION_RE = re.compile(
        r"[,.\|\u2013\-]\s*((?:(?:" + _TOKEN_PATTERN + r")\s*[,./]?\s*)+)$",
        re.IGNORECASE,
    )
    _TOKEN_FINDALL_RE = re.compile(_TOKEN_PATTERN, re.IGNORECASE)

    def __init__(self):
        super().__init__(name="Deloitte", url="https://middleeastjobs.deloitte.com/careersME/SearchJobs/")
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Strip zero-width chars and collapse stray whitespace."""
        text = text.replace("\u200b", "")
        text = unicodedata.normalize("NFKC", text)
        return re.sub(r"\s+", " ", text).strip()

    def _split_title_location(self, raw_title: str) -> tuple[str, str]:
        """Crop a trailing known-location clause off the title, regardless of
        whether it's separated by a comma, period, pipe, or dash."""
        text = self._normalize_text(raw_title)
        match = self._TRAILING_LOCATION_RE.search(text)
        if not match:
            return text, ""

        tokens_found = self._TOKEN_FINDALL_RE.findall(match.group(1))
        location = ", ".join(tokens_found)
        title = text[: match.start()].strip().rstrip(",.|").strip()
        return title, location

    def _build_params(self, offset: int = 0) -> dict:
        params = dict(self.STATIC_PARAMS)
        if offset:
            params["pipelineOffset"] = str(offset)
        return params

    def _fetch_page(self, offset: int = 0) -> BeautifulSoup:
        response = self.session.get(self.corporate_url, params=self._build_params(offset), timeout=20)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _parse_jobs(self, soup: BeautifulSoup) -> list[jobOffer]:
        """Extract job entries from a parsed results page."""
        jobs = []
        for heading in soup.select("h3 a[href*='/PipelineDetail/']"):
            raw_title = heading.get_text(strip=True)
            url = heading["href"]
            if not url.startswith("http"):
                url = f"https://middleeastjobs.deloitte.com{url}"

            h3 = heading.find_parent("h3")
            meta_el = h3.find_next(
                lambda tag: tag.name in ("p", "div", "span") and "Posted on" in tag.get_text()
            )
            meta_text = self._normalize_text(meta_el.get_text(separator=" ", strip=True)) if meta_el else ""
            fallback_location = meta_text.split("|", 1)[0].strip() if "|" in meta_text else ""

            title, location = self._split_title_location(raw_title)
            if not location:
                location = fallback_location

            jobs.append(jobOffer(
                company=self.name,
                title=title,
                url=url,
                location=location,
                job_type=None,
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
    scrapper = DeloitteScrapper()
    for job in scrapper.get_offers():
        print(job)