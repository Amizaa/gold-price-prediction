import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the website you want to scrape

data = {
    "Title": [],
    "Submitted Date": [],
    "Main Content": []
}

for i in range(18):
    if i == 0:
        url = 'https://www.bullionvault.com/gold-news/gold-price-news'
    else:
        url = f'https://www.bullionvault.com/gold-news/gold-price-news?page={i}'
        
    print("the main url: " + url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.findAll('td', class_='views-field views-field-title')

    for row in rows:
        link = row.find("a").get("href")
        print("Crawling: "+ link)

        response = requests.get(link)
        if response.status_code == 200:
            link_soup = BeautifulSoup(response.text, 'html.parser')

            title = link_soup.find('header').find('h1').text.strip()
            submitted_date = link_soup.find('div', class_='submitted').text.strip()
            main_content = link_soup.find('div', class_='field-item even').text.strip()

            data["Title"] += [title]
            data["Submitted Date"] += [submitted_date]
            data["Main Content"] += [main_content]

df = pd.DataFrame(data)
df.to_excel("extracted_data.xlsx", index=False)