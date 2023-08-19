from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()


class TestRoutes(TestCase):
    """
    Тестирование маршрутов.
    """

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text='Текст комментария'
        )

    def test_pages_availability(self):
        """
        Главная страница доступна анонимному пользователю,
        страница отдельной новости доступна анонимному пользователю,
        страницы регистрации пользователей, входа в учётную запись и
        выхода из неё доступны анонимным пользователям.
        """

        urls = (
            ('news:home', None),
            ('news:detail', (self.news.id,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        """
        Страницы удаления и редактирования комментария доступны автору
        комментария. Авторизованный пользователь не может зайти на страницу
        редактирования или удаления чужих комментариев
        (возвращается ошибка 404).
        """

        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('news:edit', 'news:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.comment.id,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        При попытке перейти на страницу редактирования или удаления
        комментария анонимный пользователь перенаправляется на
        страницу авторизации.
        """

        login_url = reverse('users:login')
        for name in ('news:edit', 'news:delete'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.comment.id,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
