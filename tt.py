import requests

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

params = (
    ('position', 'main'),
    ('callback', ''),
    ('dn', ''),
    ('keyword', '오징어'),
)

response = requests.get('https://www.ryo.co.kr/naver/keyword', headers=headers, params=params)
print("한달간 pc 검색량")
monthlyPcQcCnt = int(response.text.split(',')[1].split(':')[1].replace('\"', ''))
print(monthlyPcQcCnt)
print("한달간 모바일 검색량")
monthlyMobileQcCnt = int(response.text.split(',')[2].split(':')[1].replace('\"', '').replace('})', ''))
print(monthlyMobileQcCnt)