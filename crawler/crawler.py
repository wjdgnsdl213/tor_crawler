import requests
from bs4 import BeautifulSoup

# Tor SOCKS5 프록시 설정
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050',
}

def get_dynamic_id():
    base_url = "https://leakbase.io"
    session = requests.Session()
    response = session.get(base_url, proxies=proxies)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # 숫자가 포함된 링크 또는 요소 추출
        link = soup.find("a", {"href": lambda x: x and "/search/" in x})
        if link:
            dynamic_id = link['href'].split('/')[2]  # ID 추출
            return dynamic_id
    return None

def crawl_leakbase(search_query):
    dynamic_id = get_dynamic_id()
    if not dynamic_id:
        print("동적 ID를 가져오지 못했습니다.")
        return
    
    base_url = f"https://leakbase.io/search/{dynamic_id}/?q={search_query}&o=date"
    print(f"Requesting URL: {base_url}")

    # 검색 페이지 요청
    try:
        response = requests.get(base_url, proxies=proxies)
        if response.status_code != 200:
            print(f"Error {response.status_code}: 검색 페이지를 불러오지 못했습니다.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # 데이터 파싱
        n = 1
        while True:
            selector = f"li.block-row:nth-child({n}) > div:nth-child(1) > div:nth-child(2) > h3:nth-child(1) > a:nth-child(1)"
            element = soup.select_one(selector)
            if not element:
                break
            print(f"[+] Element {n}")
            print(f"    |-- Link Text: {element.text.strip()}")
            print(f"    |-- Link URL: {element['href']}")
            n += 1

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

if __name__ == "__main__":
    search_query = input("검색어를 입력하세요: ")
    crawl_leakbase(search_query)
