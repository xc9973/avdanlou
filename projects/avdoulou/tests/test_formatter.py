# tests/test_formatter.py
import pytest
from utils.formatter import format_success_message, format_error_message
from handlers.link_handler import VideoInfo


def test_format_success_message():
    """测试成功消息格式化"""
    video = VideoInfo(
        url="https://video.twimg.com/test.mp4",
        title="Test Video Title",
        duration=120,
        width=1920,
        height=1080,
    )

    message = format_success_message(video)

    assert "Test Video Title" in message
    assert "https://video.twimg.com/test.mp4" in message
    assert "2:00" in message or "120" in message
    assert "1920x1080" in message


def test_format_error_message_no_video():
    """测试无视频错误消息"""
    message = format_error_message("no_video")

    assert "视频" in message or "video" in message.lower()


def test_format_error_message_parse_failed():
    """测试解析失败错误消息"""
    message = format_error_message("parse_failed")

    assert "解析" in message or "失败" in message or "error" in message.lower()


def test_format_error_message_invalid_url():
    """测试无效链接错误消息"""
    message = format_error_message("invalid_url")

    assert "链接" in message or "url" in message.lower()
