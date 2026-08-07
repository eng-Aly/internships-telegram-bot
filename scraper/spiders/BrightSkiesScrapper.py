from scraper.abstractScraper import AbstractScraper
import requests
from scraper.utils import InternshipOffer


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

        def get_offer(self) -> InternshipOffer:
             pass
        def get_offers(self) -> list[InternshipOffer]:
             pass
    
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

    
if __name__=="__main__":
     obj=BrightSkiesScrapper()
     print(obj._query_jobs())