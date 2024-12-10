from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# Tor 프록시 설정
def get_driver_with_tor():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 숨기기
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Tor 프록시 설정
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.socks_proxy = "127.0.0.1:9050"  # Tor SOCKS5 프록시 설정
    proxy.socks_version = 5

    # 프록시를 ChromeOptions에 추가
    options.proxy = proxy

    driver = webdriver.Chrome(options=options)
    return driver

# 로그인 함수
def login(driver, login_url, username, password, posts_url):
    driver.get(login_url)

    try:
        # 아이디 입력 필드 대기 및 입력
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "login"))
        )
        username_field.clear()
        username_field.send_keys(username)

        # 비밀번호 입력 필드 대기 및 입력
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_field.clear()
        password_field.send_keys(password)

        # 로그인 버튼 대기 및 클릭
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'button--primary') and @type='submit']//span[text()='Log in']"))
        )
        login_button.click()

        print(f"로그인 성공! new posts 확인 중...")
        driver.get(posts_url)  # 바로 posts 페이지로 이동
    except Exception as e:
        # 오류 발생 시 화면 캡처
        driver.save_screenshot("login_error.png")
        print(f"로그인 실패: {e}")
        driver.quit()
        raise

# 게시글 제목과 다음 페이지 URL 추출
def scrape_page(driver):
    titles = []

    # 게시글 제목 추출
    try:
        for title_element in driver.find_elements(By.CSS_SELECTOR, "div.structItem-title a"):
            titles.append(title_element.text)
    except Exception as e:
        print(f"게시물 제목 추출 실패: {e}")

    return titles

# 모든 페이지 크롤링
def crawl_all_posts(driver):
    all_titles = []
    current_page = 1

    # 현재 URL에서 기본 URL과 페이지 번호 추출
    base_url = driver.current_url.rstrip("/")  # 끝에 '/' 제거
    if "/page-" in base_url:
        base_url = base_url.split("/page-")[0]

    while current_page <= 4:
        print(f"현재 페이지 URL: {driver.current_url} (페이지 {current_page})")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.structItem-title a"))
            )
        except Exception as e:
            print(f"페이지 로드 오류: {e}")
            break

        # 현재 페이지에서 제목 추출
        titles = scrape_page(driver)
        all_titles.extend(titles)

        # 다음 페이지 URL 생성
        if current_page == 4:
            return all_titles
        next_page_url = f"{base_url}/page-{current_page + 1}"

        # 페이지 이동
        driver.get(next_page_url)
        current_page += 1
        time.sleep(2)  # 페이지 로드 대기

        # 다음 페이지가 없을 경우 확인
        if "Page Not Found" in driver.page_source or not driver.find_elements(By.CSS_SELECTOR, "div.structItem-title a"):
            print("더 이상 페이지가 없습니다. 크롤링 종료.")
            break
        

    return all_titles

if __name__ == "__main__":
    # 시작 페이지 URL
    BASE_URL = "https://leakbase.io"
    LOGIN_URL = f"{BASE_URL}/login"
    NEW_POSTS_URL = f"{BASE_URL}/whats-new/posts"

    # 사용자 정보
    USERNAME = "Sogood1234@naver.com"  # 사용자 아이디
    PASSWORD = "Sogood1234"  # 사용자 비밀번호

    print("Selenium + Tor 기반 크롤러 시작...")

    # Selenium 드라이버 초기화
    driver = get_driver_with_tor()

    try:
        # 로그인 실행
        login(driver, LOGIN_URL, USERNAME, PASSWORD, NEW_POSTS_URL)

        # 게시글 크롤링 실행
        titles = crawl_all_posts(driver)

        # 결과 출력
        print(f"\n크롤링 완료! 총 {len(titles)}개의 게시글을 찾았습니다.\n")
        for idx, title in enumerate(titles, 1):
            print(f"{idx}. {title}")
    finally:
        driver.quit()
