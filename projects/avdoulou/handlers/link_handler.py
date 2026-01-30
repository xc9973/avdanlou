# handlers/link_handler.py
import asyncio
import logging
import yt_dlp
from dataclasses import dataclass
from utils.validators import is_x_video_url


logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """视频信息"""
    url: str
    title: str
    duration: int
    width: int
    height: int


class LinkHandler:
    """链接处理器"""

    async def parse_x_video(self, url: str) -> VideoInfo | None:
        """解析 X 视频链接，返回视频信息"""
        if not is_x_video_url(url):
            return None

        video_data = await self._extract_video_info(url)
        if not video_data:
            return None

        return VideoInfo(
            url=video_data["url"],
            title=video_data.get("title", "Unknown"),
            duration=video_data.get("duration", 0),
            width=video_data.get("width", 0),
            height=video_data.get("height", 0),
        )

    async def _extract_video_info(self, url: str) -> dict | None:
        """使用 yt-dlp 提取视频信息"""
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "format": "best[ext=mp4]/best[vcodec!=none]/best",
        }

        try:
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(
                    None,
                    ydl.extract_info,
                    url,
                    False,  # download=False
                )

                if not info:
                    return None

                # 获取视频 URL
                video_url = info.get("url")
                if not video_url:
                    # 尝试从 formats 中获取最佳格式
                    formats = info.get("formats", [])
                    if formats:
                        # 选择有视频流的最佳格式
                        best_format = None
                        for f in formats:
                            if f.get("vcodec") != "none":
                                if best_format is None or f.get("height", 0) > best_format.get("height", 0):
                                    best_format = f
                        if best_format:
                            video_url = best_format.get("url")

                if not video_url:
                    return None

                return {
                    "url": video_url,
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "width": info.get("width", 0),
                    "height": info.get("height", 0),
                }
        except Exception as e:
            logger.error(f"Error extracting video info from {url}: {e}", exc_info=True)
            return None
