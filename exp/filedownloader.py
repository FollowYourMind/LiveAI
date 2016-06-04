#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time

from BeautifulSoup import BeautifulSoup

BASE_URL = "http://seanlahman.com/"
EXTENSION = "csv.zip"

urls = [
    "http://seanlahman.com/baseball-archive/statistics/",
]

for url in urls:

    download_urls = []
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    links = soup.findAll('a')

    # URLの抽出
    for link in links:

        href = link.get('href')

        if href and EXTENSION in href:
            download_urls.append(href)

    # ファイルのダウンロード（ひとまず3件に制限）
    for download_url in download_urls[:3]:

        # 一秒スリープ
        time.sleep(1)

        file_name = download_url.split("/")[-1]

        if BASE_URL in download_url:
            r = requests.get(download_url)
        else:
            r = requests.get(BASE_URL + download_url)

        # ファイルの保存
        if r.status_code == 200:
            f = open(file_name, 'w')
            f.write(r.content)
            f.close()