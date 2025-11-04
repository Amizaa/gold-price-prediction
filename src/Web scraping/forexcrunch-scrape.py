import requests
from bs4 import BeautifulSoup
import pandas as pd


data = {
    "Title": [],
    "Published Date": [],
    "Main Content": [],
    "Source": [],
}

for i in range(801 , 10105):
    try:
        url = f'https://www.forexcrunch.com/blog/fxstreet/page/{i}/'
            
        print("The main url: " + url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = soup.findAll('div', class_='m-post-archive-preview')

        for post in posts:
            link = post.find("h4", class_='m-post-card-title').find('a').get("href")
            print("Crawling: "+ link)

            response = requests.get(link)
            link_soup = BeautifulSoup(response.text, 'html.parser')

            title = link_soup.find('div', class_='m-mt-30').find('h1').text.strip()
            published_date = link_soup.find('time', class_='m-author-date__date').get('datetime')
            main_content = link_soup.find('div', class_='entry-summary').text.strip()

            data["Title"] += [title]
            data["Published Date"] += [published_date]
            data["Main Content"] += [main_content]
            data["Source"] += ['FXStreet']
        
        if i % 100 == 0:
            df = pd.DataFrame(data)
            df.to_excel(f'extracted_data{i}.xlsx', index=False)
    except:
        df = pd.DataFrame(data)
        df.to_excel(f'extracted_data{i}.xlsx', index=False)
        break