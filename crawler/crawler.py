import requests
from bs4 import BeautifulSoup

# Tor SOCKS5 프록시 설정
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050',
}

# Tor 연결 테스트
def test_tor_connection():
    try:
        response = requests.get("http://check.torproject.org", proxies=proxies)
        if "Congratulations" in response.text:
            print("Tor 네트워크 연결 성공!")
        else:
            print("Tor 네트워크 연결 실패!")
    except Exception as e:
        print(f"Tor 연결 테스트 중 오류 발생: {e}")

# LeakBase에서 검색 후 크롤링
def crawl_leakbase(search_query):
    base_url = "https://leakbase.io/search/1615446/?q={}&o=date"
    search_url = base_url.format(search_query)

    # 검색 페이지 요청
    try:
        response = requests.get(search_url, proxies=proxies)
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
                break  # 더 이상 항목이 없으면 종료
            print(f"[+] Element {n}")
            print(f"    |-- Link Text: {element.text.strip()}")
            print(f"    |-- Link URL: {element['href']}")
            n += 1

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")

if __name__ == "__main__":
    # Tor 연결 테스트
    test_tor_connection()

    # 사용자 입력 받기
    search_query = input("검색어를 입력하세요: ")

    # LeakBase 크롤링 실행
    crawl_leakbase(search_query)
