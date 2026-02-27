import requests
import csv
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}

# 基础URL
base_url = 'https://movie.douban.com/top250'

# 生成10页的URL列表
page_list = [base_url + '?start=' + str(i * 25) for i in range(10)]

# 发送请求，获取所有页面的HTML源码
htmls = [requests.get(url, headers=headers).text for url in page_list]

# 将HTML源码解析为BeautifulSoup对象，使用lxml解析器
soups = [BeautifulSoup(html, 'lxml') for html in htmls]

# 存储所有电影信息的列表
items = []

# 遍历每一页的解析结果
for soup in soups:
    # 每个电影信息都包含在class为"info"的div中
    for item in soup.find_all('div', class_='info'):
        info = {}  # 存放单部电影的信息字典

        # 提取电影标题部分（位于class为"hd"的div中）
        title_spans = item.find_all('div', class_='hd')
        for title_span in title_spans:
            # 获取所有class为"title"的span
            titles = title_span.find_all('span', class_='title')
            fir_title = titles[0].text.strip()

            # 如果有第二个标题，则处理
            if len(titles) > 1:
                sec_pan = titles[1].text
                # 去掉多余的\xa0（不间断空格）和斜杠
                sec_title = sec_pan.replace('\xa0/\xa0', '').strip()
            else:
                sec_title = ''  # 没有则置空

            # 尝试提取别名，位于class为other的span中
            try:
                cleaned_title = []
                other_title = title_span.find('span', class_='other').text
                # 去掉"/\xa0"并分割多个别名
                other_title = other_title.replace('/\xa0', '').strip()
                parts = other_title.split('/')
                for i in range(len(parts)):
                    parts[i] = parts[i].strip()
                    cleaned_title.append(parts[i])
                cleaned_titles = '/'.join(cleaned_title)  # 用斜杠连接多个别名
                # 组合完整标题：中文名 / 英文名 / 别名
                title = '/'.join([fir_title, sec_title, cleaned_titles])
            except AttributeError:
                # 如果没有别名，则只组合标题
                title = '/'.join([fir_title, sec_title])

        # 提取导演信息（位于class为"bd"的div中）
        Director_tags = item.find_all('div', class_='bd')
        for Director_tag in Director_tags:
            # 使用正则表达式查找"导演:"后面的内容，直到遇到"主演:"
            match = re.search(r'导演:\s*(.*?)\s*主演:', Director_tag.text)
            if match:
                Director = match.group(1).strip()
            else:
                Director = ''  # 如果没有匹配到，置空

        # 获取评分（class为"rating_num"的span中的文本）
        ranking = item.find('span', class_='rating_num').text

        # 提取评价人数
        rank_tag = item.find('div', class_='bd').text
        result = re.search(r'(\d+)人评价', rank_tag)
        rating_counts = result.group(1) if result else 'N/A'

        # 提取评价，如果没有则用'N/A'代替
        quote_tag = item.find('p', class_='quote')
        quote = quote_tag.text if quote_tag else 'N/A'

        # 将信息存入字典
        info['电影名'] = title
        info['导演'] = Director
        info['评分'] = ranking
        info['评价人数'] = f'{rating_counts}人'
        info['评价'] = quote.strip()

        # 将单部电影信息添加到总列表
        items.append(info)

# 将数据写入CSV文件
with open('movie.csv', 'w', encoding='utf-8', newline='') as f:
    # 定义CSV的列名
    fieldnames = ['电影名', '导演', '评分', '评价人数', '评价']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()      # 写入表头
    writer.writerows(items)   # 写入所有数据

print("爬取完成，数据已保存到 movie.csv")



