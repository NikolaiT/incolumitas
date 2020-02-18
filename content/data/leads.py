import requests
import json

ad_links = ['https://www.drunkdrivinglawyers.com/sem/dui-api1', 'https://ij.org/detroit-forfeiture/', 'https://www.fiegerlaw.com/employment-law/', 'http://immigrationlawyer911.com/', 'https://www.geoffreygnathanlaw.com/', 'https://www.duidenver.com/-/denver/dui-defense/', 'https://www.dui.com/colorado/denver-county/', 'https://www.lazzaralegal.com/criminal-defense/dui/', 'https://www.midsouthcriminaldefense.com/criminal-defense/dui/', 'https://www.duncanandhill.com/', 'https://www.bishoplawmd.com/practice-area/dui-law/', 'https://www.bishoplawmd.com/practice-area/criminal-law/', 'https://family.unbundledlegalhelp.com/alimony/baltimore-md?t=nil', 'https://cordellcordell.com/offices/maryland/baltimore/family-law-for-men-baltimore/', 'https://barrjoneslegal.com/', 'https://www.raygriffithlaw.com/', 'https://www.drunkdrivinglawyers.com/sem/dui-api1']

url = 'https://scrapeulous.com/api/cc'

payload = {
    "invocation_type": "request_response",
    "worker_type": "http",
    "function": "https://raw.githubusercontent.com/NikolaiT/scrapeulous/master/leads.js",
    "items": ad_links,
    "region": "de"
}

headers = {
    'X-Api-Key': ''
}

r = requests.post(url, data=json.dumps(payload), headers=headers)
data = r.json()

with open('leads.json', 'w') as f:
    json.dump(data, f, indent=4, sort_keys=True)