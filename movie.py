import requests
import csv
from bs4 import BeautifulSoup
import re

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36' }
base_url = 'https://movie.douban.com/top250'
page_list = [base_url + '?start=' + str(i * 25) for i in range(10)]
htmls = [requests.get(url, headers=headers).text for url in page_list]
soups = [BeautifulSoup(html, 'lxml') for html in htmls]
items = []
for soup in soups:

    for item in soup.find_all('div', class_='info'):
        info = {}
        title_spans = item.find_all('div',class_='hd')
        for title_span in title_spans:
            titles = title_span.find_all('span', class_='title')
            fir_title = titles[0].text.strip()
            if len(titles) > 1 :
                sec_pan = titles[1].text
                sec_title = sec_pan.replace('\xa0/\xa0', '').strip()
            try:
                cleaned_title = []
                other_title = title_span.find('span', class_='other').text.replace('/\xa0', '').strip()
                parts = other_title.split('/')
                for i in range(len(parts)):
                    parts[i] = parts[i].strip()
                    cleaned_title.append(parts[i])
                cleaned_titles = '/'.join(cleaned_title)
                 

                
                title = '/'.join([fir_title, sec_title, cleaned_titles])
            except:
                title = '/'.join([fir_title, sec_title])
        Director_tags = item.find_all('div', class_='bd')
        for Director_tag in Director_tags:
            match = re.search(r'导演:\s*(.*?)\s*主演:', Director_tag.text)
            if match:
                Director = match.group(1).strip()
        ranking = item.find('span', class_='rating_num').text
        rank_tag = item.find('div', class_='bd').text
        result = re.search(r'(\d+)人评价', rank_tag)
        rating_counts = result.group(1) if result else 'N/A'
        quote = item.find('p', class_='quote').text if item.find('p', class_='quote') else 'N/A'
        info['电影名']=title
        info['导演']=Director
        info['评分']=ranking
        info['评价人数']=f'{rating_counts}人'   
        info['评价']=quote.strip()
        items.append(info)



        
            
        
with open('movie.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['电影名', '导演', '评分','评价人数','评价'])
    writer.writeheader()
    writer.writerows(items)



