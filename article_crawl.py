import os
import csv
import requests
# import cloudscraper
import pandas as pd
from lxml import html

def save_articles_to_file(urlid, articles):
    folder_name = "Extracted_Articles"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    filename = os.path.join(folder_name, f"{urlid}.txt")
    with open(filename, 'w', encoding='utf-8') as file:
        for article in articles:
            file.write(f"Article Title: {article['title']}\n")
            file.write(f"Article Text: {article['text']}\n\n")
    print(f"Saved {filename}")

def extract_text_recursive(element):
    """
    Recursively extracts text content from an element and its children.
    """
    text_parts = []
    if element.text:
        text_parts.append(element.text.strip())
    for child in element:
        text_parts.extend(extract_text_recursive(child))
        if child.tail:
            text_parts.append(child.tail.strip())
    return text_parts

def get_article_data(urlid, url):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

    # scraper = cloudscraper.create_scraper()
    for i in range(3):
        try:
            articalresp = requests.get(url, headers=headers, timeout=70)
            if articalresp.status_code == 200:
                break
        except Exception as e:
            print(e)
            print("Retrying")

    if articalresp.status_code != 200:
        return None

    cattree = html.fromstring(articalresp.text)
    content_div = cattree.xpath('//div[@class="td-post-content tagdiv-type"]')[0]

    if len(content_div) == 0:
        with open('artical_pnf.csv', 'a', encoding='UTF-8', newline='') as pnf:
            writer = csv.writer(pnf)
            writer.writerow([urlid, url])
        return None

    articles = []
    titles = content_div.xpath('.//h1[@class="wp-block-heading"]')
    for title_element in titles:
        title = title_element.text_content().strip().lower()
        if title in ["summarize", "contact details"]:
            continue
        text_elements = []
        sibling = title_element.getnext()
        while sibling is not None and sibling.tag !='h1':
            text_elements.extend(extract_text_recursive(sibling))
            sibling = sibling.getnext()
        text = ' '.join(filter(None, text_elements))
        print("Title:",title)
        articles.append({'title': title, 'text': text})

    return articles

#----------Articles Crawl--------------------
raw_data = pd.read_excel('input.xlsx')
raw_dataf = pd.DataFrame(raw_data)
urlidlist = raw_dataf['URL_ID'].tolist()
urllist = raw_dataf['URL'].tolist()

for i, urlid in enumerate(urlidlist):
    print(f"{i:}{urlid}")
    articles = get_article_data(urlid, urllist[i])
    if articles:
        save_articles_to_file(urlid, articles)
