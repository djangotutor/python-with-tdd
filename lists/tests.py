from django.test import TestCase


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_save_a_POST_request(self):
        response = self.client.post(
                '/',
                data={'item_text': '새 아이템'}
        )

        self.assertIn('새 아이템', response.content.decode('utf8'))
        self.assertTemplateUsed(response, 'home.html')
