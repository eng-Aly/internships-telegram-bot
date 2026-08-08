from scraper.abstractScraper import AbstractScraper
import requests
from scraper.utils import jobOffer


class BrightSkiesScrapper(AbstractScraper):
        def __init__(self):
            super().__init__(name="BrightSkies",
                            url= "https://brightskiesinc.com/graphql"
                            )
            self.session=requests.Session()
        def _open_website(self):
            response = self.session.get(
            self.corporate_url,
            timeout=10
            )    
            response.raise_for_status()
            return response.text
        def _query_jobs(self):
            query = """
            query getJobs {
                jobs(pagination: { limit: 100 }) {
                    meta {
                        pagination {
                            total
                        }
                    }
                    data {
                        id
                        attributes {
                            title
                            location
                            job_type
                            department
                        }
                    }
                }
            }
            """
            response = self.session.post(
                self.corporate_url,
                json={
                    "query": query
                },
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            if "errors" in result:
                raise RuntimeError(
                    f"GraphQL error: {result['errors']}"
                )
            return result["data"]["jobs"]["data"] 
        def _parse_job(self, job):

            attributes = job["attributes"]

            return jobOffer(
                company=self.name,
                title=attributes["title"],
                location=attributes["location"],
                job_type=attributes["job_type"],
                url=f"https://brightskiesinc.com/careers/jobs/{job["id"]}"
            )
        def get_offers(self)   ->list[jobOffer]:

            jobs = self._query_jobs()
            return [
                self._parse_job(job)
                for job in jobs
            ]
        def get_offers_keyword(self, keyword) -> list[jobOffer]:
            jobs_list = self.get_offers()

            keyword = keyword.strip().lower()

            return [
                job
                for job in jobs_list
                if (
                    keyword in job.title.lower()
                    or keyword in job.location.lower()
                    or keyword in job.job_type.lower()
                )
            ]
if __name__=="__main__":
     obj=BrightSkiesScrapper()
     print("-------------------------------all offers-----------------------------------")
     print(obj.get_offers())
     print("-----------------------------offers with keywords---------------------------")
     print(obj.get_offers_keyword("HPC"))