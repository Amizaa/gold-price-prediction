import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the website you want to scrape

import json

with open('api-links1.json') as f:
    news = json.load(f)

data = {
    "Title": [],
    "Published Date": [],
    "Main Content": [],
    "Source": []
}

for n in news:
    path = n['storyPath']
    url = f'https://www.tradingview.com{path}'
        
    print("Crawling: "+ url)
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        published_date = soup.find('time').get('datetime')
        if soup.find('div', class_='body-KX2tCBZq') is None:
            main_content = 'none'
        else:
            main_content = soup.find('div', class_='body-KX2tCBZq').text.strip()

        data["Title"] += [n['title']]
        data["Published Date"] += [published_date]
        data["Main Content"] += [main_content]
        data["Source"] += [n['provider']['name']]
    except:
        df = pd.DataFrame(data)
        df.to_excel("extracted_data.xlsx", index=False)

df = pd.DataFrame(data)
df.to_excel("extracted_data.xlsx", index=False)