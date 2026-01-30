# tests/test_validators.py
import pytest
from utils.validators import is_x_video_url, extract_tweet_id


def test_valid_x_url():
    """测试有效的 X 链接"""
    assert is_x_video_url("https://x.com/user/status/123456789") is True
    assert is_x_video_url("https://twitter.com/user/status/123456789") is True
    assert is_x_video_url("https://x.com/user/status/123456789/video/1") is True


def test_invalid_x_url():
    """测试无效的链接"""
    assert is_x_video_url("https://youtube.com/watch?v=123") is False
    assert is_x_video_url("https://example.com") is False
    assert is_x_video_url("not a url") is False
    assert is_x_video_url("https://x.com/home") is False


def test_extract_tweet_id():
    """测试提取推文 ID"""
    assert extract_tweet_id("https://x.com/user/status/123456789") == "123456789"
    assert extract_tweet_id("https://twitter.com/user/status/987654321") == "987654321"
    assert extract_tweet_id("https://x.com/user/status/123456789/video/1") == "123456789"


def test_extract_tweet_id_invalid():
    """测试无效链接返回 None"""
    assert extract_tweet_id("https://youtube.com/watch?v=123") is None
    assert extract_tweet_id("not a url") is None
