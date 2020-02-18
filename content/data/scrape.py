import requests
import json

url = 'https://scrapeulous.com/api/new'

req = requests.get('https://incolumitas.com/data/law_keywords.txt')
keywords = [kw for kw in req.text.split('\n') if kw]

payload = {
    "search_engine": "google",
    "num_pages": 1,
    "region": "us",
    "keywords": keywords
}

headers = {
    'X-Api-Key': 'A_GQjGbDukBls21mhoqaC1IEjKA1sK9iUX9e_97tLXU'
}

r = requests.post(url, data=json.dumps(payload), headers=headers)
data = r.json()

with open('scraped_keywords.json', 'w') as f:
    json.dump(data, f)
