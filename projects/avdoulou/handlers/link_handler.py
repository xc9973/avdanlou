# handlers/link_handler.py
import yt_dlp
from dataclasses import dataclass
from utils.validators import is_x_video_url


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
            "format": "best",  # 选择最佳质量
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                if not info:
                    return None

                # 获取视频 URL
                video_url = info.get("url")
                if not video_url:
                    # 尝试从 formats 中获取
                    formats = info.get("formats", [])
                    if formats:
                        video_url = formats[-1].get("url")  # 通常最后一个是最佳质量

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
            print(f"Error extracting video info: {e}")
            return None
