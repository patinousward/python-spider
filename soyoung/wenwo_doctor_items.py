# -*- coding: utf-8 -*-
import requests
import csv
from lxml import etree  # 解析html
from lxml.html import fromstring, tostring  # xml标签tostring
import re  # 正则
# 获取项目分类树


def getItems(district_Dict):
    writeCSVHead()
    r = requests.get('https://y.soyoung.com/yuehui/shop')
    # 获取菜单
    menu1 = r.json()['responseData']['menu1_info']
    for m in menu1:
        if(m['name'] != "全部项目"):
            # 获取1级分类
            for s1 in m['son']:
                if(s1['name'] != "查看全部"):
                    # 获取二级分类
                    for s2 in s1['son']:
                        if(s2['name'] != "查看全部"):
                            print("开始爬取 => %s,%s,%s 分类下的商品" %
                                  (m['name'], s1['name'], s2['name']))
                            getProductInfo(m['name'], s1['name'],
                                           s2['name'], s2['item_id'], district_Dict)

# 菜单id，一级分类id，二级分类id，项目id


def getProductInfo(m_name, s1_name, s2_name, item_id, district_Dict):
    for dict in district_Dict:
        index = 0
        while 1:
            r = requests.post("https://y.soyoung.com/yuehui/shop", data={
                'district_id': dict['id'], 'sort': '0', 'item_id': item_id, 'brand': '0', 'index': index})
            product_info = r.json()['responseData']['product_info']
            for p in product_info:
                # 进入商品详情页
                detail_page = "https://y.soyoung.com/cp%s/" % p['pid']
                page_r = requests.get(detail_page)
                # 解析html，获取单品销量
                sale_cnt = getSaleCnt(page_r.text)
                hospital_id = p['hospital_id']
                hospital_name = p['hospital_name']
                pid = p['pid']
                title = p['title']
                price = p['price_cut']
                with open('/home/patinousward/test01.csv', 'a+')as f:  # 追加
                    f_csv = csv.writer(f)
                    f_csv.writerow([m_name, s1_name, s2_name, item_id,
                                    pid, title, price, hospital_id, hospital_name, sale_cnt, dict['name']])
            print("完成第 %s 页的爬取" % index)
            # 是否有下一页
            hasmore = r.json()['responseData']['has_more']
            if(hasmore):
                index += 1
            else:
                break


def getSaleCnt(page):
    selector = etree.HTML(page)
    data = selector.xpath(
        '//*[@id="baseInfo"]/div[3]/div[3]/em/text()')  # text获取标签中的文本
    # if(len(data) > 0):
    #str = tostring(data[0], encoding='utf-8').decode('utf-8')
    # else:  # 有些html的页面xpath有点问题
    #data = selector.xpath('//*[@id="baseInfo"]/div[2]/div[3]/em/text()')
    #str = tostring(data[0], encoding='utf-8').decode('utf-8')
    # str 格式<em>99</em>已售
    #pattern = re.compile(r'<em>(.+)</em>已售')
    #count = re.findall(pattern, str)[0]
    if(len(data) == 0):
        data = selector.xpath('//*[@id="baseInfo"]/div[2]/div[3]/em/text()')
    if(len(data) > 0):
        return data[0]
    return 'null'

# csv写头


def writeCSVHead():
    headers = ['菜单分类', '一级分类', '二级分类', '项目id',
               '产品id', '产品名', '产品价格', '产品医院id', '产品医院名称', '销售量', '城市']
    with open('/home/patinousward/test01.csv', 'w')as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)


def getCityList():
    district_dict = []
    selector = etree.HTML(requests.get("https://y.soyoung.com/").text)
    data = selector.xpath(
        '/html/body/div[3]/div/div[1]/div[2]/div/div/div[3]/div[2]/ul/node()')  # node()获取子标签
    for number in data:  # 字母分类，比如A开头的城市
       # /html/body/div[3]/div/div[1]/div[2]/div/div/div[3]/div[2]/ul/li[5]/div
        for province in number.xpath('./div/node()'):
            for city in province.xpath('./div/node()'):
                city_name = city.xpath('./text()')[0]
                #print(city_name)
                r = requests.get(
                    'https://y.soyoung.com/site/getCity?name=%s&m=0.16838172966340248' % city_name)
                has_key = 'list' in r.json().keys()
                if(has_key):
                    cityId = r.json()['list'][0]['id']
                    district_dict.append({'id': cityId, 'name': city_name})
    return district_dict


def main():
    district_dict = getCityList()
    getItems(district_dict)
    print("=======end======")


if __name__ == '__main__':
    main()
