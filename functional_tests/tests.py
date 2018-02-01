from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import time


MAX_WAIT = 10


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def test_can_start_a_list_for_one_user(self):
        # 에디스는 작업 목록 온라인 앱이 나왔다는 소식을 듣고
        # 해당 웹 사이트를 확인한다
        self.browser.get(self.live_server_url)

        # 웹 페이지 타이틀과 헤더가 'To-Do'를 표시하고 있다
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # 그녀는 바로 작업을 추가하기로 한다
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(
                inputbox.get_attribute('placeholder'),
                'Enter a to-do item'
        )

        # "공작깃털 사기"라고 텍스트 상자에 입력한다
        inputbox.send_keys('공작깃털 사기')

        # 엔터키를 치면 페이지가 갱신되고 작업 목록에
        # "1: 공작깃털 사기" 아이템이 추가된다
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: 공작깃털 사기')

        # 추가 아이템을 입력할 수 있는 텍스트 상자가 존재한다
        # 다시 "공작깃털을 이용해서 그물 만들기"라고 입력한다
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('공작깃털을 이용해서 그물 만들기')
        inputbox.send_keys(Keys.ENTER)

        # 페이지는 다시 갱신되고, 두 개 아이템이 목록에 보인다
        self.wait_for_row_in_list_table('1: 공작깃털 사기')
        self.wait_for_row_in_list_table('2: 공작깃털을 이용해서 그물 만들기')

        # 만족하고 잠자리에 든다

    def test_multiple_users_can_start_lists_at_different_urls(self):
        # 에디스가 작업을 추가한다
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('공작깃털 사기')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: 공작깃털 사기')

        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('공작깃털로 그물 만들기')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: 공작깃털 사기')
        self.wait_for_row_in_list_table('2: 공작깃털로 그물 만들기')

        # 그녀는 자신을 위한 고유한 URL이 있음을 알게 된다
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')

        # 새로운 사용자 프란시스가 방문한다

        ## 에디스의 정보가 쿠키 등으로 유입되는 것을 방지하기 위해서
        ## 새로운 브라우저 세션을 사용한다
        self.browser.quit()
        self.browser = webdriver.Firefox()

        # 프란시스가 사이트에 접속하고 에디스의 리스트 흔적은 없다
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('공작깃털 사기', page_text)
        self.assertNotIn('공작깃털로 그물 만들기', page_text)

        # 프란시스는 새로운 아이템을 입력한다
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('우유 사기')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: 우유 사기')

        # 프란시스는 자신의 고유 URL를 얻게 된다
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # 에디스의 흔적이 없음을 다시 확인한다
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('공작깃털 사기', page_text)
        self.assertNotIn('공작깃털로 그물 만들기', page_text)
        self.assertIn('우유 사기', page_text)

        # 둘 다 만족하고 잠자리에 든다
