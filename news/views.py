from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from django.http import JsonResponse
from urllib.parse import urljoin


def fetch_news_with_selenium(url):
    # Selenium을 설정
    options = Options()
    options.add_argument('--headless')  # 브라우저를 화면에 표시하지 않음
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # ChromeDriver를 설정
    driver = webdriver.Chrome(service=Service('/Users/dgsw8th74/.wdm/drivers/chromedriver/mac64/127.0.6533.72/chromedriver-mac-arm64/chromedriver'), options=options)


    # URL로 웹 페이지를 연다
    driver.get(url)

    # 페이지가 완전히 로드될 때까지 대기
    driver.implicitly_wait(10)  # 최대 10초 대기

    # 웹 페이지의 HTML을 가져옴
    html = driver.page_source
    driver.quit()

    return html


def news_by_category(request, category):
    category_urls = {
        'securities': 'https://news.naver.com/breakingnews/section/101/258',  # 증권
        'finance': 'https://news.naver.com/breakingnews/section/101/259',  # 금융
        'economy': 'https://news.naver.com/breakingnews/section/101/263',  # 경제
        'realEstate': 'https://news.naver.com/breakingnews/section/101/260',  # 부동산
        'industrialBusiness': 'https://news.naver.com/breakingnews/section/101/261'  # 산업/재계
    }

    url = category_urls.get(category)
    if not url:
        return JsonResponse({"error": "존재하지 않는 카테고리입니다."}, status=404)

    try:
        # Selenium을 사용하여 페이지를 로드하고 HTML을 가져옴
        html = fetch_news_with_selenium(url)
        soup = BeautifulSoup(html, 'html.parser')

        # 뉴스 항목을 포함한 li 태그를 선택
        news_items_divs = soup.select("li.sa_item._LAZY_LOADING_WRAP")

        news_items = []
        for item_div in news_items_divs:
            # 제목 및 URL 추출
            title_tag = item_div.select_one("a.sa_text_title")
            title = title_tag.select_one("strong.sa_text_strong").text.strip() if title_tag else None
            relative_url = title_tag.get('href') if title_tag else None
            absolute_url = urljoin(url, relative_url) if relative_url else None

            # 언론사 추출
            company_tag = item_div.select_one("div.sa_text_press")
            company = company_tag.text.strip() if company_tag else None

            # 썸네일 이미지 URL 추출
            thumbnail_tag = item_div.select_one("div.sa_thumb img")
            thumbnail_url = thumbnail_tag['src'] if thumbnail_tag and 'src' in thumbnail_tag.attrs else None

            news_items.append({
                'title': title,
                'url': absolute_url,
                'company': company,
                'thumbnail': thumbnail_url
            })

        return JsonResponse(news_items, safe=False)

    except Exception as e:
        return JsonResponse({"error": "뉴스를 가져오는 데 실패했습니다.", "details": str(e)}, status=500)
