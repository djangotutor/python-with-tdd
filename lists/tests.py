from django.test import TestCase

from lists.models import Item
from lists.models import List


class HomePageTest(TestCase):
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class ListAndItemModelTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = '첫번째 아이템'
        first_item.list = list_
        first_item.save()
        second_item = Item()
        second_item.text = '두번째 아이템'
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()

        self.assertEqual(saved_items.count(), 2)
        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, '첫번째 아이템')
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, '두번째 아이템')
        self.assertEqual(second_saved_item.list, list_)


class ListViewTest(TestCase):
    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text='아이템 1', list=correct_list)
        Item.objects.create(text='아이템 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='다른 아이템 1', list=other_list)
        Item.objects.create(text='다른 아이템 2', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, '아이템 1')
        self.assertContains(response, '아이템 2')
        self.assertNotContains(response, '다른 아이템 1')
        self.assertNotContains(response, '다른 아이템 2')

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertEqual(response.context['list'], correct_list)

class NewListTest(TestCase):
    def test_can_save_a_POST_request(self):
        self.client.post('/lists/new', data={'item_text': '새 아이템'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, '새 아이템')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'item_text': '새 아이템'})
        list_ = List.objects.first()
        self.assertRedirects(response, f'/lists/{list_.id}/')


class NewItemTest(TestCase):
    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
                f'/lists/{correct_list.id}/add_item',
                data={'item_text': '기존 리스트에 아이템 추가'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, '기존 리스트에 아이템 추가')
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_live_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
                f'/lists/{correct_list.id}/add_item',
                data={'item_text': '기존 리스트에 아이템 추가'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')
