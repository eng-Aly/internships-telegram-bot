import requests


url = "https://valeo.wd3.myworkdayjobs.com/wday/cxs/valeo/valeo_jobs/jobs"

payload = {
    "appliedFacets": {
        "locationCountry": [
            "d865e83093ad42319653b08e61f7db49"
        ]
    },
    "limit": 20,
    "offset": 0,
    "searchText": ""
}

response = requests.post(
    url,
    json=payload,
    timeout=10
)

response.raise_for_status()

data = response.json()

print(data)