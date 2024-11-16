from urllib.request import Request, urlopen
import pandas as pd
from bs4 import BeautifulSoup
import re
import time
from tqdm import tqdm

import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import traceback
from selenium.webdriver.common.by import By


def scrape_kaisai_date(from_, to_):
    """
    from_とto_はyyyy-mmの形で指定すると、その間の開催日を取得する関数
    """
    kaisai_date_list = []
    for date in tqdm(pd.date_range(from_, to_, freq="MS")):
        year = date.year
        month = date.month
    
        url = f"https://race.netkeiba.com/top/calendar.html?year={year}&month={month}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}

        request = Request(url, headers=headers)
        html = urlopen(request).read()   #スクレイピング

        time.sleep(1) #サーバーの負荷を減らすため一秒間ごとにアクセスするようにする、絶対必要

        soup = BeautifulSoup(html)
        
        a_list = soup.find("table", class_="Calendar_Table").find_all("a")

        for a in a_list:
            kaisai_date = re.findall(r"kaisai_date=(\d{8})", a["href"])[0]
            kaisai_date_list.append(kaisai_date)
    return kaisai_date_list

def scrape_race_id_list(kaisai_date_list: list[str]): #引数の型を指定している
    """
    開催日(yyyymmdd形式)をリストで入れると、レースid一覧が返ってくる関数
    """
    options = Options()
    options.add_argument("--headless") #バックグラウンドで処理
    driver_path = ChromeDriverManager().install()
    race_id_list = []
    
    with webdriver.Chrome(service=Service(driver_path), options=options) as driver:
        for kaisai_date in tqdm(kaisai_date_list):
            url = f"https://race.netkeiba.com/top/race_list.html?kaisai_date={kaisai_date}"
            try:
                driver.get(url)
                time.sleep(1)
                li_list = driver.find_elements(By.CLASS_NAME, "RaceList_DataItem")
                
                for li in li_list:
                    href = li.find_element(By.TAG_NAME, "a").get_attribute("href")
                    race_id = re.findall(r"race_id=(\d{12})", href)[0]
                    race_id_list.append(race_id)
            except: #エラーが出た時の処理
                print(f"stopped at {url}")
                print(traceback.format_exc())
                break
    return race_id_list