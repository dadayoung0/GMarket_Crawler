from bs4 import BeautifulSoup
import requests

from google_oauth import oauth, get_sheet

import json
import time
from datetime import date

# 구글 인증
oauth()


# 검색용 데이터 가져오기
def get_google_data(worksheet):
    # 데이터 넣을 리스트
    google_sheet_data = []

    # gspread의 get_all_valiues()는
    # 시트의 모든 데이터를 2차원 리스트로 가져온다
    for row in worksheet.get_all_values():
        # 가져온 데이터 리스트에 dict형태로 넣기
        google_sheet_data.append({
            'name': row[0],
            'url': row[1],
            'search_keyword': row[2],
            'search_count': row[3],
            'naver_ranking': row[4],
            'seller_count': row[5],
            'review': row[6],
            'zzim': row[7]
        })

    return google_sheet_data


# 판매자수 가져오기
def get_seller_count(url):
    # 반복문의 마지막 row는 header이기 때문에
    # url넣을 시에 error발생
    try:
        req = requests.get(url)
    except:
        return '0'

    html = req.text
    soup = BeautifulSoup(html, 'html.parser')

    # 네이버 스마트스토어의 마지막 script를 보면 데이터가 담겨있는 JSON파일을 확인 할 수 있다.
    script = soup.find_all('script')[-1].string
    # JSON파일 변환
    json_data = json.loads(script)

    # 판매자수 JSON에서 추출
    # 없다면 '0' 반환
    try:
        seller_count = json_data['props']['pageProps']['initialState']['catalog']['info']['productCount']
    except:
        return '0'

    return str(seller_count)


# 네이버 쇼핑에서 순위, 리뷰, 찜 추출 함수
def get_naver_ranking(target_url, search_keyword):
    # page_index를 선언
    page_index = 1

    while True:
        try:
            # pagingSize argument로 한 페이지에 들어오는 상품 개수를 선택할 수 있다.
            # 최대 80개
            req = requests.get(
                f'https://search.shopping.naver.com/search/all?query={search_keyword}&pagingIndex={page_index}&pagingSize=80')
        except:
            break

        html = req.text
        soup = BeautifulSoup(html, 'html.parser')

        script = soup.find_all('script')[-1].string
        json_data = json.loads(script)

        # product_id는 가격비교 상품들 고유의 번호
        # url뒤에 붙어있기 때문에 떼어내준다
        product_id = target_url[target_url.find('log/')+4:]

        # JSON에서 상품 목록 추출
        # error발생 시에는 0, 0, 0 반환
        try:
            products = json_data['props']['pageProps']['initialState']['products']['list']
        except:
            return '0', '0', '0'

        # 가져온 상품들 반복
        for product in products:
            try:
                product['item']['crUrl']

                # 같은 product_id를 가진 상품을 찾았다면
                if product['item']['id'] == product_id:
                    item = product['item']

                    # 순위, 리뷰, 찜을 가져온다
                    # 하나하나 없는 데이터가 있을 수도 있기 때문에 각각 try문 실행
                    try:
                        rank = item['rank']
                        if rank == None:
                            rank = '0'
                    except:
                        rank = '0'
                    try:
                        review = item['reviewCountSum']
                        if review == None:
                            review = '0'
                    except:
                        review = '0'
                    try:
                        zzim = item['keepCnt']
                        if zzim == None:
                            zzim = '0'
                    except:
                        zzim = '0'

                    print(rank, review, zzim, 'done')
                    return str(rank), str(review), str(zzim)

            except:
                continue
        else:
            # 너무 빠르게 호출하면 ip차단을 받기 때문에
            # 어느정도 여유를 두고 실행
            time.sleep(2)
            page_index += 1

            # 만약 page_index가 6이 되면 종료 (5페이지까지)
            # 더 낮은 순위까지 추출하고 싶으면 이 숫자를 올리면 된다
            if page_index == 6:
                print('순위권 밖')
                return '순위권 밖', '0', '0'


# 시트에서 어떤 row를 수정해야 하는지 index를 반환하는 함수
def find_data_index(google_data, url):
    for index, row in enumerate(google_data):
        # url이 같은 상품 반환
        if row['url'] == url:
            print(index)
            return index+1
    else:
        print('xxxxx')
        return -1


# 순위, 숫자 변동을 위한 함수 세 번째 파라미터가 'rank'이면 순위를 계산한다
# 나눈 이유는 순위는 숫자가 낮아질 수록 증감이 오른것으로 판단해야 하기 때문
def calc_number(google_data, crawl_data, mode):
    # 가져온 데이터가 '순위권 밖'이라면 바로 반환함
    if crawl_data == '순위권 밖':
        return crawl_data
    else:
        # 시트에서 가져온 데이터에서 괄호가 없으면
        # 새로 들어온 데이터라고 판단
        if google_data.find('(') == -1:
            try:
                google_data = int(google_data)
            except:
                return f'{crawl_data}(new)'
        else:
            # 시트에서 가져온 데이터에서 괄호가 있으면
            # 괄호를 제거하고 int형으로 변환
            google_data = int(google_data[:google_data.find('(')])

            # rank와 다른 데이터들을 나눠서 증감량 계산
            if mode == 'rank':
                return f'{crawl_data}({int(google_data) - int(crawl_data)})'

            else:
                return f'{crawl_data}({int(crawl_data) - int(google_data)})'


# 구글 시트에 업데이트 하는 함수
def write_google_sheet(sheet, input_data, index):
    # index가 -1이면(error) 바로 끝내기
    if index == -1:
        return

    time.sleep(2)
    # cell을 기준으로 업데이트 할 때는 2차원 리스트를 넣어야 하기 때문에
    # 들어온 리스트를 한 번 더 감싼다
    sheet.update(f'A{index}:H{index}', [input_data])
    print(input_data, 'done')


if __name__ == '__main__':
    start = time.time()

    read_sheet = get_google_data(get_sheet('데이터2'))
    print(read_sheet)
    input_sheet = get_sheet('데이터2')

    # 반복문을 돌 때 반대로 뒤집어서 돌게 함
    # 혹시 추후에 데이터를 계속 삽입하게 된다면 반대로 도는게 더 용이함
    for google_data in reversed(read_sheet):
        seller_count = get_seller_count(google_data['url'])

        naver_ranking, review, zzim = get_naver_ranking(
            google_data['url'], google_data['search_keyword'])

        # input할 데이터 전처리
        data = {
            'name': google_data['name'],
            'url': google_data['url'],
            'search_keyword': google_data['search_keyword'],
            'search_count': google_data['search_count'],
            'naver_ranking': calc_number(google_data['naver_ranking'], naver_ranking, 'rank'),
            'seller_count': calc_number(google_data['seller_count'], seller_count, ''),
            'review': calc_number(google_data['review'], review, ''),
            'zzim': calc_number(google_data['zzim'], zzim, ''),
        }

        data_index = find_data_index(read_sheet, google_data['url'])

        write_google_sheet(input_sheet, list(data.values()), data_index)

    print('총 소요시간: ' + str(time.time() - start) + '초')