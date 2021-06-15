# -*- coding: utf-8 -*-
import requests
import csv
from lxml import etree  # 解析html
from lxml.html import fromstring, tostring  # xml标签tostring
import re  # 正则
# 获取项目分类树


def getProducts(district_Dict, material_dict):
    writeCSVHead()  # 搜索不走商品品类
    for dict in district_Dict:
        print("爬取城市 => %s" % dict['name'])
        for material in material_dict:
            page = 1  # page从1开始
            keyword = material['title']
            city_id = dict['id']
            while 1:
                r = requests.get(
                    "https://www.soyoung.com/searchNew/product?keyword=%s&cityId=%s&_json=1&page=%s" % (keyword, city_id, page))
                product_info = r.json()['responseData']['arr_product']
                for p in product_info:
                    pid = p['pid']
                    title = p['title']
                    price = p['price_cut']
                    hospital_id = p['hospital_id']
                    hospital_name = p['hospital_name']
                    # 进入商品详情页
                    detail_page = "https://y.soyoung.com/cp%s/" % p['pid']
                    page_r = requests.get(detail_page)
                    # 解析html，获取单品销量
                    sale_cnt = getSaleCnt(page_r.text)
                    with open('/home/patinousward/test02.csv', 'a+')as f:  # 追加
                        f_csv = csv.writer(f)
                        f_csv.writerow([material['classification_name'], material['title'], material['material_url'], material['title_company'],
                                        material['material_name'], material['labelsList'], material['adaptorList'],
                                        material['brand'], material['producing_area'], material['go_public_time'], material['company'], material['cfda'], material['price'], pid, title, price, hospital_id, hospital_name, sale_cnt, dict['name']])
                print("完成第 %s 页的爬取" % page)
                # 是否有下一页
                hasmore = r.json()['responseData']['has_more']
                if(hasmore):
                    page += 1
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
    headers = ['材料分类', 'title', 'material_url', 'title_company', '材料名称', '功效', '适用项目', '品牌', '产地/厂商', '上市时间', '公司', 'cfda', '材料价格',
               '产品id', '产品名', '产品价格', '产品医院id', '产品医院名称', '销售量', '城市']
    with open('/home/patinousward/test02.csv', 'w')as f:
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
                # print(city_name)
                r = requests.get(
                    'https://y.soyoung.com/site/getCity?name=%s&m=0.16838172966340248' % city_name)
                has_key = 'list' in r.json().keys()
                if(has_key):
                    cityId = r.json()['list'][0]['id']
                    district_dict.append({'id': cityId, 'name': city_name})
    return district_dict


def getMaterialList():
    material_dict = []
    selector = etree.HTML(requests.get(
        "https://www.soyoung.com/itemk/material/").text)
    classification20024 = selector.xpath('//*[@id="product20024"]')[0]
    parseMaterialClassification(classification20024, material_dict)
    classification20025 = selector.xpath('//*[@id="product20025"]')[0]
    parseMaterialClassification(classification20025, material_dict)
    classification20026 = selector.xpath('//*[@id="product20026"]')[0]
    parseMaterialClassification(classification20026, material_dict)
    classification20027 = selector.xpath('//*[@id="product20027"]')[0]
    parseMaterialClassification(classification20027, material_dict)
    classification20030 = selector.xpath('//*[@id="product20030"]')[0]
    parseMaterialClassification(classification20030, material_dict)
    classification20031 = selector.xpath('//*[@id="product20031"]')[0]
    parseMaterialClassification(classification20031, material_dict)
    return material_dict


def parseMaterialClassification(classification, material_dict):
    classification_name = classification.xpath('./div[1]/text()')
    product_nodes = classification.xpath('./div[2]/div[2]/node()')
    for node in product_nodes:
        # title
        title = node.xpath('./div[2]/text()')[0].strip()
        # url
        material_url = node.xpath('./@data-url')[0]
        # 公司信息
        title_company = node.xpath('./div[4]/a[1]/text()')
        # 材料详情页
        selector = etree.HTML(requests.get(
            "https://www.soyoung.com" + material_url).text)
        # 获取材料名称
        material_name = selector.xpath(
            '/html/body/div[4]/div[1]/div/div[1]/div/h1/text()')
        # 获取功效
        labels = selector.xpath(
            '/html/body/div[4]/div[3]/div[1]/section[2]/div[1]/node()')
        # ==0是判断404页面的
        if(len(labels) == 0 or len(labels[0].xpath('./span/text()')) == 0):
            labels = selector.xpath(
                '/html/body/div[4]/div[3]/div[1]/section[1]/div[1]/node()')  # 老模板
        labelsList = []
        for label in labels:
            if(len(label.xpath('./span/text()')) != 0):  # 缺少label的情况
                labelsList.append(label.xpath('./span/text()')[0])
        # 获取适用项目
        adaptors = selector.xpath(
            '/html/body/div[4]/div[3]/div[1]/section[2]/div[3]/div/node()')
        # ==0是i判断404页面的
        if(len(adaptors) == 0 or len(adaptors[0].xpath('./span/text()')) == 0):
            labels = selector.xpath(
                '/html/body/div[4]/div[3]/div[1]/section[1]/div[3]/div')  # 老模板
        adaptorList = []
        for adaptor in adaptors:
            if(len(adaptor.xpath('./span/text()')) != 0):  # 缺少label的情况
                adaptorList.append(adaptor.xpath('./span/text()')[0])

        # 获取品牌
        brand = ""
        brand_node = selector.xpath(
            '/html/body/div[4]/div[3]/div[1]/section[2]/div[2]/ul/li[1]/div[1]/span[2]/text()')  # 普通情况
        if(len(brand_node) == 0):  # 404
            brand_node = selector.xpath(
                '/html/body/div[4]/div[3]/div[1]/section[1]/div[2]/ul/li[1]/div[1]/span[2]/text()')  # 兼容老模板
        if(len(brand_node) != 0):  # 缺少信息的情况
            brand = brand_node[0]

        # 获取产地
        producing_area = ""
        producing_area_node = selector.xpath(
            '/html/body/div[4]/div[3]/div[1]/section[2]/div[2]/ul/li[1]/div[2]/span[2]/text()')  # 普通情况
        if(len(producing_area_node) == 0):  # 404
            producing_area_node = selector.xpath(
                '/html/body/div[4]/div[3]/div[1]/section[1]/div[2]/ul/li[1]/div[2]/span[2]/text()')  # 兼容老模板
        if(len(producing_area_node) != 0):  # 缺少信息的情况
            producing_area = producing_area_node[0]
        # 上市时间
        go_public_time = ""
        go_public_time_node = selector.xpath(
            '/html/body/div[4]/div[3]/div[1]/section[2]/div[2]/ul/li[2]/div[1]/span[2]/text()')  # 普通情况
        if(len(go_public_time_node) == 0):  # 404
            go_public_time_node = selector.xpath(
                '/html/body/div[4]/div[3]/div[1]/section[1]/div[2]/ul/li[2]/div[1]/span[2]/text()')  # 兼容老模板
        if(len(go_public_time_node) != 0):  # 缺少信息的情况
            go_public_time = go_public_time_node[0]

        # 公司/厂商
        company = ""
        company_node = selector.xpath(
            '/html/body/div[4]/div[3]/div[1]/section[2]/div[2]/ul/li[2]/div[2]/span[2]/text()')  # 普通情况
        if(len(company_node) == 0):  # 404
            company_node = selector.xpath(
                '/html/body/div[4]/div[3]/div[1]/section[1]/div[2]/ul/li[2]/div[2]/span[2]/text()')  # 兼容老模板
        if(len(company_node) != 0):  # 缺少信息的情况
            company = company_node[0]

        # cfda
        cfda = ""
        cfda_node = selector.xpath(
            '/html/body/div[4]/div[3]/div[1]/section[2]/div[2]/ul/li[3]/div[1]/span[2]/text()')  # 普通情况
        if(len(cfda_node) == 0):  # 404
            cfda_node = selector.xpath(
                '/html/body/div[4]/div[3]/div[1]/section[1]/div[2]/ul/li[3]/div[1]/span[2]/text()')  # 兼容老模板
        if(len(cfda_node) != 0):  # 缺少信息的情况
            cfda = cfda_node[0]

        # price
        price = ""
        price_node = selector.xpath(
            '/html/body/div[4]/div[3]/div[1]/section[2]/div[2]/ul/li[3]/div[2]/span[2]/text()')  # 普通情况
        if(len(price_node) == 0):  # 404
            price_node = selector.xpath(
                '/html/body/div[4]/div[3]/div[1]/section[1]/div[2]/ul/li[3]/div[2]/span[2]/text()')  # 兼容老模板
        if(len(price_node) != 0):  # 缺少信息的情况
            price = price_node[0]

        print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (title, material_url,
                                                       title_company, material_name, labelsList,
                                                       adaptorList, brand, producing_area, go_public_time,
                                                       company, cfda, price))

        material_dict.append({'classification_name': classification_name, 'title': title, 'material_url': material_url,
                              'title_company': title_company, 'material_name': material_name, 'labelsList': labelsList,
                              'adaptorList': adaptorList, 'brand': brand, 'producing_area': producing_area, 'go_public_time': go_public_time,
                              'company': company, 'cfda': cfda, 'price': price})


def main():
    material_dict = getMaterialList()
    district_dict = getCityList()
    # print(len(material_dict))
    getProducts(district_dict, material_dict)
    print("=======end======")


if __name__ == '__main__':
    main()
