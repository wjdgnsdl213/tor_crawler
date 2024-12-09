
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Tor SOCKS5 프록시 설정
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050',
}

try:
    # Tor 네트워크를 통해 요청
    response = requests.get("http://check.torproject.org", proxies=proxies)
    print(response.text)
except Exception as e:
    print(f"Tor 연결 실패: {e}")