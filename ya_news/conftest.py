import pytest

from datetime import datetime, timedelta
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


from news.models import Comment, News

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def user(django_user_model, client):
    return django_user_model.objects.create(username='Мимо Крокодил')


@pytest.fixture
def auth_client(user, client):
    client.force_login(user)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def news_id_for_args(news):
    return news.id,


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text=COMMENT_TEXT
    )
    return comment


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def set_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def detail_url(news_id_for_args):
    return reverse('news:detail', args=news_id_for_args)


@pytest.fixture
def set_comments(news, author):
    now = timezone.now()
    comments = [
        Comment(
            news=news,
            author=author,
            text=f'Текст {index}',
            created=now + timedelta(days=index)
        ) for index in range(2)
    ]
    Comment.objects.bulk_create(comments)


@pytest.fixture
def form_data():
    return {'text': COMMENT_TEXT}


@pytest.fixture
def new_form_data():
    return {'text': NEW_COMMENT_TEXT}


@pytest.fixture
def news_detail_url(news_id_for_args):
    return reverse('news:detail', args=news_id_for_args)


@pytest.fixture
def url_to_comments(news_detail_url):
    return news_detail_url + '#comments'


@pytest.fixture
def edit_url(comment_id_for_args):
    return reverse('news:edit', args=comment_id_for_args)


@pytest.fixture
def delete_url(comment_id_for_args):
    return reverse('news:delete', args=comment_id_for_args)
