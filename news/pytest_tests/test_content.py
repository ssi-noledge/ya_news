import pytest
from django.conf import settings

from news.forms import CommentForm


class TestNews:

    def test_comments_order(self, client, detail_url):
        response = client.get(detail_url)
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps

    def test_anonymous_client_has_no_form(self, client, detail_url):
        response = client.get(detail_url)
        assert 'form' not in response.context

    def test_authorized_client_has_form(self, client_with_login, detail_url):
        response = client_with_login.get(detail_url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)

    def test_news_order_on_homepage(self, client, news_list, home_url):
        response = client.get(home_url)
        news_list = response.context['news_list']
        timestamps = [news.date for news in news_list]
        sorted_timestamps = sorted(timestamps, reverse=True)
        assert timestamps == sorted_timestamps

    def test_news_count_on_homepage(self, client, news_list, home_url):
        response = client.get(home_url)
        assert response.context[
            'news_list'
        ].count() == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_non_author_can_view_form(self, client_with_reader_login,
                                      detail_url):
        response = client_with_reader_login.get(detail_url)
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
