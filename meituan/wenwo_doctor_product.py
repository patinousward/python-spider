# -*- coding: utf-8 -*-
import requests
import csv
from lxml import etree  # 解析html
from lxml.html import fromstring, tostring  # xml标签tostring
import re  # 正则
import time


def getCities():
    # 模拟浏览器
    citiesReturn = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    r = requests.get(
        'https://www.meituan.com/ptapi/getprovincecityinfo/', headers=headers)
    for province in r.json():
        cities = province['cityInfoList']
        for city in cities:
            citiesReturn.append(city)
    return citiesReturn


def getProducts(cities):
    writeCSVHead()
    for city in cities:
        print("开始爬取城市 => %s" % city['name'])
        acronym = city['acronym']  # 域名地址
        headers = {
            'Cookie': '__mta=149272841.1623744904483.1623744904483.1623744918295.2; _ga=GA1.2.1845603152.1621824448; uuid=5479ddd720a644be99b6.1623317312.1.0.0; _lxsdk_cuid=179f5407999bd-07e5b24ce57193-3972095d-100200-179f540799ac8; mtcdn=K; lsu=; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; lt=TOC_sqrnlkwZETF4Hd4LEm4d_j4AAAAAyQ0AANdj8hCJa2TS1d339RQbAbbOYfQAUKcjrtk8Ex57kMyzGbaFk50r6pdn3nw-HH9meA; u=79831267; n=VOM445770171; token2=TOC_sqrnlkwZETF4Hd4LEm4d_j4AAAAAyQ0AANdj8hCJa2TS1d339RQbAbbOYfQAUKcjrtk8Ex57kMyzGbaFk50r6pdn3nw-HH9meA; unc=VOM445770171; ci=224; rvct=224%2C993%2C238%2C10%2C1%2C60%2C65%2C30; __mta=149272841.1623744904483.1623744904483.1623744904483.1; firstTime=1623744916629; _lxsdk_s=17a0ea3dd4a-b03-b7b-b1f%7C%7C58',
            'Referer': 'https://%s.meituan.com/jiankangliren/c20423/' % acronym
        }
        uuid = "5479ddd720a644be99b6.1623317312.1.0.0"
        user_id = "79831267"
        offset = 0
        cateId = "20423"
        token = "TOC_sqrnlkwZETF4Hd4LEm4d_j4AAAAAyQ0AANdj8hCJa2TS1d339RQbAbbOYfQAUKcjrtk8Ex57kMyzGbaFk50r6pdn3nw-HH9meA"
        cityId = city['id']
        while 1:
            r = requests.get(
                'https://apimobile.meituan.com/group/v4/poi/pcsearch/%s?uuid=%s&userid=%s&limit=32&offset=%s&cateId=%s&token=%s&areaId=-1'
                % (cityId, uuid, user_id, offset, cateId, token), headers=headers)
            if(len(r.json()['data']['searchResult']) == 0):
                break
            offset += 32  # limit
            for item in r.json()['data']['searchResult']:
                # https://www.meituan.com/jiankangliren/160153611/
                item_id = item['id']
                item_title = item['title']
                item_url = "https://www.meituan.com/jiankangliren/%s/" % item_id
                score = item['avgscore']
                comment_cnt = item['comments']
                item_site = item['address']
                avgprice = item['avgprice']
                with open('/home/patinousward/test03.csv', 'a+')as f:  # 追加
                    f_csv = csv.writer(f)
                    f_csv.writerow([item_title, item_url, score, comment_cnt,
                                    item_site, avgprice, city['name']])
                time.sleep(1)  # 防止请求过快


def writeCSVHead():
    headers = ['项目名称', '项目url', '评分', '评论人数', '项目地址', '人均价格', '城市']
    with open('/home/patinousward/test03.csv', 'w')as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)


def main():
    cities = getCities()
    getProducts(cities)
    print("=======end======")


if __name__ == '__main__':
    main()
