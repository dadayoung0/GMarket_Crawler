from bs4 import BeautifulSoup
import requests
import json
import re


class Item():
    title = ''
    sale_count = 0
    review_count = 0
    url = ''


class Gmarket():
    def __init__(self, save_dir: str):
        self.save_dir = save_dir

        headers = {
            'Connection': 'keep-alive',
            'accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
            'content-type': 'application/json',
            'Origin': 'http://category.gmarket.co.kr',
            'Referer': 'http://category.gmarket.co.kr/',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        data = '[{"name":"Header","params":{"type":"sub","isAdult":false,"isSfc":false}}]'

        response = requests.post(
            'http://fnp.gmarket.co.kr/desktop-layout/models', headers=headers, data=data, verify=False)
        json_data = json.loads(response.text)[0]['categoryGroups']

        self.categories_1 = []
        self.categories_2 = []
        self.categories_3 = []
        for category1 in json_data:
            for category2 in category1['subgroups']:
                if category2['name'] != '':
                    for category3 in category2['categories']:
                        self.categories_3.append([len(self.categories_1), len(
                            self.categories_2), category3['name'], category3['href']])
                    self.categories_2.append(
                        [len(self.categories_1), category2['name']])
            self.categories_1.append(category1['name'])

        self.categories_num = {}
        self.result = []

    def set_categories_num(self, use_ctg: list):
        for ctg in self.categories_3:
            if ctg[1] in use_ctg:
                if 'http://category.gmarket.co.kr/listview' in ctg[3]:
                    res = requests.get(ctg[3]).text
                    soup = BeautifulSoup(res, 'html.parser')
                    for detail_ctg in soup.find_all('a', class_=None, href=re.compile("category=")):
                        self.categories_num[detail_ctg.string] = detail_ctg['href'].split('category=')[
                            1][:9]
                        self.result.append(
                            [self.categories_1[ctg[0]], self.categories_2[ctg[1]][1], ctg[2], detail_ctg.string])
                else:
                    print(ctg[2], ctg[3])
                    print("다른 페이지!!!!!!!!!!!")

    def get_crawl(self, order: str, crawl_count: int, min_sale_count: int):
        s = {
            "낮은 가격순": 1,
            "높은 가격순": 2,
            "신규 상품순": 3,
            "G마켓 랭크순": 7,
            "판매 인기순": 8,
            "상품평 많은 순": 13
        }

        for rst in self.result:
            url = f'http://browse.gmarket.co.kr/list?category={self.categories_num[rst[3]]}&s={s[order]}'
            res = requests.get(url).text
            soup = BeautifulSoup(res, 'html.parser')

            box_div = soup.find('div', class_="box__component-itemcard")

            item = Item()

            for i in range(crawl_count):
                try:
                    item.sale_count = int(box_div.find(
                        'li', class_="list-item__pay-count").span.contents[-1])
                    if item.sale_count < min_sale_count:
                        continue
                except:
                    item.sale_count = 0

                item.title = box_div.find('span', class_="text__item")['title']
                try:
                    item.review_count = int(box_div.find(
                        'li', class_="list-item__feedback-count").contents[1].contents[2])
                except:
                    item.review_count = 0
                item.url = box_div.find('a', class_="link__item")["href"]
                print(item.title)
                print(item.sale_count)
                print(item.review_count)
                print(item.url)

                box_div = box_div.next_sibling


g = Gmarket('')
g.set_categories_num([0])
g.get_crawl('판매 인기순', 5, 0)
