import json

ad_links = []

with open('scraped_keywords.json') as f:
    data = json.load(f)
    
    for kw, value in data['results'].items():
    
        if '1' in value:
        
            for ad in value['1']['bottom_ads']:
                ad_links.append(ad.get('link'))
                
            for ad in value['1']['top_ads']:
                ad_links.append(ad.get('link'))
                
print(ad_links)
print(len(ad_links))
