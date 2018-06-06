#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 19:08:55 2018

@author: little-frog
"""
import requests
from urllib.parse import urlencode
import os
from hashlib import md5
from multiprocessing.pool import Pool###多线程模块

def get_page(offset):
    params = {
        'offset':offset,
        'format':'json',
        'keyword':'街拍',
        'autoload':'true',
        'count':'20',
        'cur_tab':'1',
        'from':'search_tab'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None
###由于找不到image_detail了,所以在分析了图片地址之后，选择抓取image_list并改写来代替
def get_images(json):
    if json.get('data'):
        for item in json.get('data'):
            title = item.get('title')
            if item.get('image_list'):###这个有None,所以用这个命令来跳过None
                images = item.get('image_list')
                for image in images:
                    yield{
                    'image':'http:'+image.get('url').replace('list','origin'),
                    'title':title
                }

def save_image(item):
    path = '/今日头条街拍保存/'
    if not os.path.exists(path + item.get('title')):
        os.mkdir(path + item.get('title'))
    try:
        response = requests.get(item.get('image'))
        if response.status_code == 200:
            file_path = '{0}/{1}.{2}'.format(path + item.get('title'),md5(response.content).hexdigest(),'jpg')
            if not os.path.exists(file_path):
                with open(file_path,'wb') as f:
                    f.write(response.content)
            else:
                print('Already Download',file_path)
    except requests.ConnectionError:
        print('Failed to save Image')

def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        save_image(item)
    
GROUP_START = 1
GROUP_END = 20

if __name__=='__main__':
    pool = Pool()
    groups = ([x*20 for x in range(GROUP_START,GROUP_END+1)])
    pool.map(main,groups)
    pool.close()
    pool.join()
