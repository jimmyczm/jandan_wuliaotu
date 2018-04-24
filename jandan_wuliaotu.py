#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io , os , sys , re , time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup as bs
from hashlib import md5
import pymongo
import requests


sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') 

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser,10)

MAX_PAGE=200 #需要遍历的页面数

MONGO_URL = 'localhost'
MONGO_DB ='jandan_wuliaotu'
MONGO_COLLECTION = 'wuliaotu0424'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]


def get_page (page):
    url = 'http://jandan.net/pic/page-'+str(page)+'#comments'
    try:
        browser.get(url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.commentlist ')))
        time.sleep(20)
        get_texts()
        print('正在获取页面')
    except TimeoutException:
        get_page (page)
    
def get_texts ():
#获取oo大于100的无聊图片，,ooxx数，过滤不受欢迎的图
    html = browser.page_source
    doc = bs(html,'lxml')
    items = doc(id = re.compile('comment-.*'))
    for item in items :
        oo = int(item.find(class_ ='tucao-like-container').span.get_text(strip=True))
        img =  item.find(class_ = 'view_img_link').get('href')
        t = item('bad_content')
        if  t or  oo < 100 :
            continue
        imgs ={
            'img' : item.find(class_ = 'view_img_link').get('href'),
            'oo':int(item.find(class_ = 'tucao-like-container').span.get_text(strip=True)),
            'xx':int(item.find(class_ = 'tucao-unlike-container').span.get_text(strip=True)),
            'date': item.find('small').get_text(strip=True)
        }

        print('正在保存',imgs)
        save_image(img)
        save_to_mongo(imgs)

def  save_image(image):
#保存图片到本地
    if   not os.path.exists('wuliaotu'):
        os.mkdir('wuliaotu')
    file_path = 'wuliaotu\\'+ image.split('/')[4]
    img_data = requests.get('http:'+image)
    if  not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(img_data.content)
    else:
        print('早就下载了')

                                    
def save_to_mongo (result):
#保存图片信息到mongo
    try:
        if db[MONGO_COLLECTION].insert(result):
            print('储存成功')
    except Exception:
        print('储存失败')
        
       
def main ():
#需要遍历的页面
    for i  in range(1,MAX_PAGE+1):
        get_page(i)
    browser.close()

if __name__ == '__main__' :
    main()

