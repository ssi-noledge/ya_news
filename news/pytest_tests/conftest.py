from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def author(db):
    return User.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(db):
    return User.objects.create(username='Читатель простой')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news, author=author, text='Текст комментария'
    )


@pytest.fixture
def news_list():
    news_count = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    news_items = [
        News(title=f'Заголовок {i}',
             text='Текст',
             date=datetime.now() - timedelta(days=i)
             )
        for i in range(news_count)
    ]
    News.objects.bulk_create(news_items)


@pytest.fixture
def client_with_login(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def client_with_reader_login(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=[news.id])


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=[comment.pk])


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=[comment.pk])


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comments(news, author):
    for i in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {i}'
        )
        comment.created = datetime.today() - timedelta(days=i)
        comment.save()


@pytest.fixture
def bad_words_data():
    return {'text': f'I like words {BAD_WORDS[0]}!'}


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
