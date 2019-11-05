# -*- coding: utf-8 -*-
"""
​
fetch tennis data from suportsnavi.
テニスデータのみをスポナビから取得
​
"""


import requests, urllib.error
from bs4 import BeautifulSoup
import MeCab
import csv
import unicodedata

import os, re
from time import sleep
import string



def wakati_by_mecab(text):
    tagger = MeCab.Tagger('')
    tagger.parse('') 
    node = tagger.parseToNode(text)
    word_list = []
    while node:
        pos = node.feature.split(",")[0]
        if pos in ["名詞", "動詞", "形容詞"]:   # 対象とする品詞
            word = node.surface
            word_list.append(word)
        node = node.next
    return " ".join(word_list)


# baseURL とは、ホスト名を含む、各ページの基礎となるURL


base_url = "https://sports.yahoo.co.jp/news/list"
# 記事一覧のカテゴリ
# カテゴリはテニスのみとする​

# これらの記事一覧カテゴリ、1ページにつき20記事掲載されいてる。
# カテゴリにつき10ページ(200記事)取得し、CSVに保存する。
 

category_list = ["baseball", "soccer", 'keiba',
                'golf','figure','f1', 'motor',
                'fight','sumo','volley','rugby','athletic',
                'basket']

# カテゴリの初期値 
category_num = 1

# ページの初期値 

page_num = 1 

csvlist = []

# 1 ページにある記事数.  
nunmber_of_articles_in_a_page = 20

# 記事カテゴリごとに、何ページ分取得するかという変数
# 4ページ取得するので、4とする 20記事 x 4p = 80記事
iter_num_of_a_page = 4

# each_sentense_list = []

def format_text(text):
  # 前処理用の関数
  # 全角記号を半角へ置換（不完全）
    text = unicodedata.normalize("NFKC", text)  


    # 記号を消し去るためのテーブル作成
    table = str.maketrans("", "", string.punctuation  + "「」、。・")
    text = text.translate(table)
    return text


# urlにアクセスしてHTMLを取得し、パースする
# ​
# カテゴリの種類の数だけ、ループを回す
# 今回はカテゴリが1つなのでfor文でやる必要がないかもしれない

for z in range(len(category_list)):
    # そのカテゴリから取得したいページ数(10p)をループで回す
    for x in range(iter_num_of_a_page):
       #各ループで、アクセスするURLを変数を用いて生成する。
        target_url = base_url + "?id=" + str(category_list[z]) + "&p=" + str(page_num+x)
        
        # tennisの記事をターミナルに出力表示
        print(target_url)
            # ここから　bs４を使ってスクレイピング 
        
        # URLにアクセスして、データを取得　requests.get() はHttpでリソースを取得できるライブラリのメソッド
        html = requests.get(target_url)
        sleep(.500)
        # BeautifulSoupで開く
        soup = BeautifulSoup(html.text, "html.parser")

        # HTMLからニュース一覧に使用しているaタグを絞りこんでいく
        news_list_with_tags = soup.find_all("a", "linkMain")
        
        # CSVに書き込む記事タイトルの配列を作成
        # 記事見出しのリンクからリンク先の文字列を取得して、アクセスし、リンク先のHTMLを解析
        for news_txt in news_list_with_tags:
            
            # news_txt['href'] は、見出しの hrefタグの値を指している　
            body_target_url= news_txt['href']

            print(body_target_url)
             # リンク先（記事詳細（本文）ページ）にアクセスして、HTMLを取得
            body_page_html = requests.get(body_target_url)
                        
            # 取得したHTMLからボディ要素のみ取得
            body_page_html = body_page_html.text
             # Beautiful soupで解析
            body_soup = BeautifulSoup(body_page_html, "html.parser")
            
            body_list_with_tags = body_soup.find_all("p",{"class": ["ynDetailText", "yjDirectSLinkTarget"]})
          
            ##<p class="ynDetailText yjDirectSLinkTarget">

            print(body_list_with_tags )

        # リストの要素を文字列として結合　
            article = ''.join(str(body_list_with_tags))
            
            # HTMLタグの除去
            article = re.sub('<[^<]+?>', '', article)

            # 改行除去
            article = re.sub('\n', '', article)

            # URL除去
            article=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…■]+', "", article)
           
            # 数字を0に置き換え
            article = re.sub(r'\d+', '0', article)

            # 日本語記号の除去
            article = format_text(article)

            article = wakati_by_mecab( article)

            # CSVに書き込む記事タイトルの配列を作成
            csvlist.append(article)
                
# CSVに書き込む記事タイトルをコンソールに出
print(csvlist)


# CSVファイルを開く。ファイルがなければ新規作成する。
with open("Dataset_tennis_bodyfromsports_wakachi_nontennis.csv", "w") as f:
    for v in range(len(csvlist)):
      if 0 <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*1): 
        cate_num = 0
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*1) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*2):
        cate_num = 1
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*2) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*3):
        cate_num = 2
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*3) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*4):
        cate_num = 3
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*4) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*5):
        cate_num = 4
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*5) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*6):
        cate_num = 5
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*6) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*7):
        cate_num = 6
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*7) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*8):
        cate_num = 7
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*8) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*9):
        cate_num = 8
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*9) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*10):
        cate_num = 9
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*10) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*11):
       cate_num = 10
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*11) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*12):
        cate_num = 11
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*12) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*13):
       cate_num = 12
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*13) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*14):
       cate_num = 13
      elif nunmber_of_articles_in_a_page*(iter_num_of_a_page*14) <= v < nunmber_of_articles_in_a_page*(iter_num_of_a_page*15):
        cate_num = 14

      f.write("{},{}\n".format(csvlist[v], 'non-tennis'))