import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id_for_args',)),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_pages_availability(client, name, args):
    """
    Главная страница доступна анонимному пользователю,
    страница отдельной новости доступна анонимному пользователю,
    страницы регистрации пользователей, входа в учётную запись и
    выхода из неё доступны анонимным пользователям.
    """

    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args',)),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args',)),
    ),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, name, args, expected_status
):
    """
    Страницы удаления и редактирования комментария доступны автору
    комментария. Авторизованный пользователь не может зайти на страницу
    редактирования или удаления чужих комментариев
    (возвращается ошибка 404).
    """

    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id_for_args',)),
        ('news:delete', pytest.lazy_fixture('comment_id_for_args',)),
    ),
)
def test_redirect_for_anonymous_client(client, name, args):
    """
    При попытке перейти на страницу редактирования или удаления
    комментария анонимный пользователь перенаправляется на
    страницу авторизации.
    """

    login_url = reverse('users:login')
    url = reverse(name, args=args)
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
