import pytest

from http import HTTPStatus
from pytest_django.asserts import assertFormError, assertRedirects

from conftest import COMMENT_TEXT, NEW_COMMENT_TEXT
from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client, news_detail_url, form_data
):
    """
    Анонимный пользователь не может отправить комментарий.
    """

    client.post(news_detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(
        news, user, auth_client, news_detail_url, form_data
):
    """
    Авторизованный пользователь может отправить комментарий.
    """

    response = auth_client.post(news_detail_url, data=form_data)
    assertRedirects(response, f'{news_detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == user


def test_user_cant_use_bad_words(auth_client, news_detail_url):
    """
    Если комментарий содержит запрещённые слова, он не будет опубликован.
    """

    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = auth_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, delete_url, url_to_comments):
    """
    Авторизованный пользователь может удалять свои комментарии.
    """

    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(reader_client, delete_url):
    """
    Авторизованный пользователь не может удалять чужие комментарии.
    """

    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
        author_client, edit_url, new_form_data, url_to_comments, comment
):
    """
    Авторизованный пользователь может редактировать свои комментарии.
    """

    response = author_client.post(edit_url, data=new_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(
        reader_client, edit_url, new_form_data, comment
):
    """
    Авторизованный пользователь не может редактировать чужие комментарии.
    """

    response = reader_client.post(edit_url, data=new_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == COMMENT_TEXT
