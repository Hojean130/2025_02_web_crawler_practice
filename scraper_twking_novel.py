import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd


## Step 1: 讀取主頁排行榜名單
book_tops = pd.read_csv('booktop.csv')
#print(book_tops.head(10))  # head()預設是前五個


book_top10s = book_tops.head(10)
last_chapter_titles = []  # 各本小說的最後章節標題
last_chapter_urls = []    # 各本小說的最後章節原文連結
nums_of_chapters = []     # 總共有幾個章節

for book_top10 in book_top10s.iterrows(): # iterrows() 遍歷每一行
    #print(book_top10[1]['novel_name'], book_top10[1]['novel_page_url'])

    ## Step 2: 
    page_url = book_top10[1]['novel_page_url']
    r = requests.get(page_url)
    r.encoding = 'utf-8' # 避免亂碼
    page_soup = BeautifulSoup(r.text, 'html.parser') # 'html.parser' 是解析器，內建於 Python，不需要額外安裝。

    chapter_wrapper = page_soup.find('div', attrs={"class":"info-chapters flex flex-wrap"})
    chapters = chapter_wrapper.find_all('a') # find_all()出來本身是一個list
    print(f"{book_top10[1]['novel_name']}, # of chapters: {len(chapters)}")
    last_chapter = chapters[-1]
    last_chapter_title = last_chapter.get('title')
    last_chapter_url = last_chapter.get('href')
    print(f"lasr chapter: {last_chapter_title}")
    print(f"whitch at {last_chapter_url}")
    print()

    # 也可以用count的方法
    # count = 0
    # for i in chapter_wrapper_a:
    #    count += 1
    # print(count)

    ## Step 3: 蒐集資訊
    last_chapter_titles.append(last_chapter_title)
    last_chapter_urls.append(last_chapter_url)
    nums_of_chapters.append(len(chapters))

book_top10s['chapter_numbers'] = nums_of_chapters
book_top10s['last_chapter_url'] = last_chapter_urls
book_top10s['last_chapter_title'] = last_chapter_titles

book_top10s.to_csv('book_top10s.csv')



