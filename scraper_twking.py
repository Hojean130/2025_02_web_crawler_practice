import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd

### Step1: request
url = "https://www.twking.cc/"
r = requests.get(url)
r.encoding = 'utf-8' # 避免亂碼
#print(len(r.text))

soup = BeautifulSoup(r.text, 'html.parser')

#soup.find_all('div', class_='booktop') # 需要另外記住 class_=
#booktops = soup.find_all('div', attrs={"class":"booktop"}) # attributes形成一個字典，class為key，booktop為value

### Step2: 找訊息
# 方法一
""" 
for booktop in booktops:
    tops = booktop.find_all('p')
    tops_type = tops[0].text
    for top in tops[1:]:
        print('\t', top.a.text, '\t', top.a.get('href'))
 """
# 方法二:
""" for booktop in booktops:
    tops_type = booktop.p.text
    tops = booktop.css.select('p a') # 小說
    print(tops_type)
    for top in tops:
        print('\t', top.text, '\t', top.get('href')) """

### step3: collection
# 找存在這些top10幾次
booktop_summarize = dict()
booktops = soup.find_all('div', attrs={"class":"booktop"})

for booktop in booktops:
    tops = booktop.find_all('p')
    for top in tops[1:]:
        top_book_name = top.a.text.strip() # 小說名稱,清除前後的空白
        top_book_url = top.a.get('href')

        if top_book_name in booktop_summarize:
            booktop_summarize[top_book_name]['counts'] += 1 # 已存在紀錄中
        else:
            booktop_summarize[top_book_name] = {
                'counts': 1,
                'href': top_book_url
            }


#pprint(booktop_summarize) # 排版後的print

sorted_booktop_summarize = sorted(
    booktop_summarize.items(),
    reverse = True, # 降冪
    key=lambda x:x[1]['counts']
)


## 改成格式list
""" 
[
    {
        'novel_name': 'ABC'
        'top_count': '1'
        'nobel_page_url':'...'
    },
    {
        'novel_name': 'DEF'
        'top_count': '1'
        'nobel_page_url':'...'
    },
    {
        'novel_name': 'GHI'
        'top_count': '1'
        'nobel_page_url':'...'
    }
] 
"""

book_rows = list()
for book in sorted_booktop_summarize:
    book_name = book[0]
    book_count = book[1]['counts']
    book_page_url = book[1]['href']
    book_row = {
        'novel_name': book_name,
        'top_count': book_count,
        'novel_page_url': book_page_url
    }
    book_rows.append(book_row)


booktop_summarize_df = pd.DataFrame(book_rows)
booktop_summarize_df.to_csv('booktop.csv')