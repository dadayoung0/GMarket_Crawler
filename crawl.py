from bs4 import BeautifulSoup
import requests
import json
import csv
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
                        if '.aspx' not in category3['href'] and 'category=' not in category3['href']:
                            continue
                        self.categories_3.append([len(self.categories_1), len(
                            self.categories_2), category3['name'], category3['href']])
                    self.categories_2.append(
                        [len(self.categories_1), category2['name']])
            self.categories_1.append(category1['name'])

        self.result = []
        self.detail_categories = []

        before = 0
        for ctg in self.categories_3:
            if ctg[1] - before > 1:
                self.categories_2[before+1:ctg[1]] = ['']
            before = ctg[1]

    def set_detail_categories(self, use_ctg: list):
        url = 'http://browse.gmarket.co.kr/list?category='
        for ctg in self.categories_3:
            if ctg[1] in use_ctg:
                if 'http://category.gmarket.co.kr/listview' in ctg[3]:
                    res = requests.get(ctg[3])
                    soup = BeautifulSoup(res.text, 'html.parser')
                    if res.history:
                        continue

                    for detail_ctg in soup.find_all('a', class_=None, href=re.compile("category=")):
                        # 1차 / 2차 / 3차 / 4차 / url
                        # s = 8(판매량 순) / 7(지마켓 랭크순)
                        self.detail_categories.append([self.categories_1[ctg[0]], self.categories_2[ctg[1]][1],
                                                      ctg[2], detail_ctg.string, url+detail_ctg['href'].split('category=')[1][:9]+'&s=7'])

                elif 'category=' in ctg[3]:
                    # 1차 / 2차 / 3차 / - / url
                    self.detail_categories.append(
                        [self.categories_1[ctg[0]], self.categories_2[ctg[1]][1], ctg[2], '-', url+ctg[3].split('category=')[1][:9]+'&s=8'])
                else:
                    print("ERROR!!!!")

    def get_crawl(self, crawl_count: int, min_sale_count: int):
        cnt = 0
        for dtl in self.detail_categories:
            cnt += 1
            print(len(self.detail_categories), "개 중에", cnt, "개 진행중!!")
            res = requests.get(dtl[4]).text
            soup = BeautifulSoup(res, 'html.parser')

            box_div = soup.find('div', class_="box__component-itemcard")
            if box_div == None:
                print(f'"{dtl[3]}" 카테고리에 아무런 상품이 없습니다...')
                continue

            item = Item()
            c = 1
            for i in range(crawl_count):
                print(crawl_count, "중에", c, "번째 항목 조회")
                c += 1
                try:
                    item.sale_count = int(box_div.find(
                        'li', class_="list-item__pay-count").span.contents[-1].replace(',', ''))
                except:
                    item.sale_count = 0

                if item.sale_count < min_sale_count:
                    print(min_sale_count, "보다 적어서 다음 카테고리로...")
                    break

                item.title = box_div.find('span', class_="text__item")['title']

                try:
                    item.review_count = int(box_div.find(
                        'li', class_="list-item__feedback-count").contents[1].contents[2].replace(',', ''))
                except:
                    item.review_count = 0
                item.url = box_div.find('a', class_="link__item")["href"]

                # 1차 / 2차 / 3차 / 4차 / 아이템명 / 판매량 / 리뷰수 / 주소
                self.result.append([dtl[0], dtl[1], dtl[2], dtl[3], item.title,
                                   item.sale_count, item.review_count, item.url])

                box_div = box_div.next_sibling
                if box_div == None:
                    print(f'"{dtl[3]}" 카테고리에 더 이상 상품이 없습니다...')
                    break

    def save_data(self):
        with open('GMarket.csv', 'w', encoding='utf-8', newline='') as f:
            wr = csv.writer(f)
            for row in self.result:
                wr.writerow(row)


if __name__ == '__main__':
    gmk = Gmarket('')
    print("초기화 OK!!")
    gmk.set_detail_categories([9, 10, 11, 14, 15, 18, 19])
    # 9, 10, 11, 14, 15, 18, 19
    print("상세 카테고리 조회 OK!!")
    gmk.get_crawl(25, 0)
    print("크롤링 OK!!")
    gmk.save_data()
    print("저장 OK!!")
