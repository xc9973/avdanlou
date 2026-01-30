# tests/test_link_handler.py
import pytest
from handlers.link_handler import LinkHandler, VideoInfo
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_parse_x_video_success():
    """测试成功解析 X 视频"""
    handler = LinkHandler()

    mock_result = {
        "url": "https://video.twimg.com/test.mp4",
        "title": "Test Video",
        "duration": 60,
        "width": 1920,
        "height": 1080,
    }

    with patch.object(handler, "_extract_video_info", AsyncMock(return_value=mock_result)):
        result = await handler.parse_x_video("https://x.com/user/status/123456789")

        assert result.url == "https://video.twimg.com/test.mp4"
        assert result.title == "Test Video"
        assert result.duration == 60
        assert result.width == 1920
        assert result.height == 1080


@pytest.mark.asyncio
async def test_parse_x_video_no_video():
    """测试推文无视频"""
    handler = LinkHandler()

    with patch.object(handler, "_extract_video_info", AsyncMock(return_value=None)):
        result = await handler.parse_x_video("https://x.com/user/status/123456789")

        assert result is None


@pytest.mark.asyncio
async def test_parse_x_video_invalid_url():
    """测试无效 URL"""
    handler = LinkHandler()
    result = await handler.parse_x_video("https://youtube.com/watch?v=123")

    assert result is None
