from bs4 import BeautifulSoup
import urllib.request as req


class Item():
    title=''
    sale_count=0
    review_count=0
    url=''


s = {
    "낮은 가격순" : 1,
    "높은 가격순" : 2,
    "신규 상품순" : 3,
    "G마켓 랭크순" : 7,
    "판매 인기순" : 8,
    "상품평 많은 순" : 13
}


import requests
import json


class Gmarket():
    def __init__(self):
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

        response = requests.post('http://fnp.gmarket.co.kr/desktop-layout/models', headers=headers, data=data, verify=False)
        json_data = json.loads(response.text)[0]['categoryGroups']

        self.categories_1 = []
        self.categories_2 = []
        self.categories_3 = []
        for category1 in json_data:
            for category2 in category1['subgroups']:
                if category2['name'] != '':
                    for category3 in category2['categories']:
                        self.categories_3.append([len(self.categories_1), len(self.categories_2), category3['name'], category3['href']])
                    self.categories_2.append([len(self.categories_1), category2['name']])
            self.categories_1.append(category1['name'])
        
    def crawling(self, save_dir, use_ctg, max_num, min_sale_cnt):
        for ctg in self.categories_3:
            if ctg[1] in use_ctg:

    # def get_detail_categories(self):

    def get_categories(self):
        categories = []
        res = req.urlopen(self.main_url).read()
        soup = BeautifulSoup(res, 'html.parser')
        for i in soup.find('div', id='box__category-all-layer').find_all('a', class_='link__2depth-item'):
            categories.append({i.string: i['href']})
        return categories

    def get_item_list(self, item_count:int, min_sale_count:int):
        
        res = req.urlopen(self.url).read()
        soup = BeautifulSoup(res, 'html.parser')

        box_div = soup.find('p', class_="text__title", string="일반상품").find_parent('div', class_="box__component")

        item = Item()


        for i in range(item_count):
            try:
                item.sale_count = int(box_div.find('li', class_="list-item__pay-count").span.contents[-1])
                if item.sale_count < min_sale_count:
                    continue
            except:
                item.sale_count = 0
            
            item.title = box_div.find('span', class_="text__item")['title']
            try:
                item.review_count = int(box_div.find('li', class_="list-item__feedback-count").contents[1].contents[2])
            except:
                item.review_count = 0
            item.url = box_div.find('a', class_="link__item")["href"]
            print(item.title)
            print(item.sale_count)
            print(item.review_count)
            print(item.url)

            box_div = box_div.next_sibling
        # nth = soup.find_all('div', class_='box__tier-container')

g = Gmarket()
# g.get_category()