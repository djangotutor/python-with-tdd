from selenium import webdriver


# 장고 설치 및 프로젝트 생성 확인
browser = webdriver.Firefox()
browser.get('http://localhost:8000')

assert 'Django' in browser.title
