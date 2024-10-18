from http import HTTPStatus

import pytest
from django.contrib.auth import get_user

from news.forms import WARNING
from news.models import Comment

COMMENT_TEXT = 'New comment'
UPDATED_COMMENT_TEXT = 'Updated comment'


def test_author_can_delete_comment(client_with_login, delete_url):
    initial_comment_count = Comment.objects.count()
    response = client_with_login.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_comment_count - 1


def test_user_cant_delete_comment_of_another_user(
    client_with_reader_login, delete_url
):
    initial_comment_count = Comment.objects.count()
    response = client_with_reader_login.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_comment_count


def test_author_can_edit_comment(client_with_login, edit_url, comment, news):
    response = client_with_login.post(edit_url, {'text': UPDATED_COMMENT_TEXT})
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    user = get_user(client_with_login)
    assert comment.text == UPDATED_COMMENT_TEXT
    assert comment.author == user
    assert comment.news == news


def test_user_cant_edit_comment_of_another_user(
    client_with_reader_login, edit_url, comment
):
    new_text = COMMENT_TEXT
    response = client_with_reader_login.post(edit_url, {'text': new_text})
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == comment.text
    assert updated_comment.author == comment.author
    assert updated_comment.news == comment.news


def test_anonymous_user_cant_post_comment(client, detail_url):
    original_comment_count = Comment.objects.count()
    response = client.post(
        detail_url,
        data={'text': COMMENT_TEXT}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == original_comment_count


def test_authorized_user_can_post_comment(
    client_with_login, detail_url, news, author
):
    Comment.objects.all().delete()
    initial_comment_count = Comment.objects.count()
    response = client_with_login.post(
        detail_url,
        data={'text': COMMENT_TEXT})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_comment_count + 1
    comment = Comment.objects.get(text=COMMENT_TEXT)
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(client_with_login, detail_url,
                                 bad_words_data):
    initial_comment_count = Comment.objects.count()
    response = client_with_login.post(detail_url, data=bad_words_data)
    assert 'form' in response.context
    assert 'text' in response.context['form'].errors
    assert WARNING in response.context['form'].errors['text']
    assert Comment.objects.count() == initial_comment_count
