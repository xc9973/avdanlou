# handlers/link_handler.py
import asyncio
import logging
import os
import tempfile
import yt_dlp
from dataclasses import dataclass
from pathlib import Path
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

    async def download_x_video(self, url: str) -> str | None:
        """下载 X 视频，返回本地文件路径

        Args:
            url: X/Twitter 推文链接

        Returns:
            下载的视频文件路径，失败返回 None
        """
        if not is_x_video_url(url):
            return None

        # 创建临时目录
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, "x_video_$(id)s.%(ext)s")

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "outtmpl": temp_file,
            "format": "best[ext=mp4]/best[vcodec!=none]/best",
        }

        try:
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(
                    None,
                    ydl.extract_info,
                    url,
                    True,  # download=True
                )

                if not info:
                    return None

                # 获取下载的文件路径
                filename = ydl.prepare_filename(info)
                if os.path.exists(filename):
                    logger.info(f"Video downloaded to {filename}")
                    return filename

                # yt-dlp 可能会添加 .mp4 等扩展名
                possible_files = [
                    filename,
                    filename + ".mp4",
                    filename + ".webm",
                ]
                for f in possible_files:
                    if os.path.exists(f):
                        logger.info(f"Video downloaded to {f}")
                        return f

                return None

        except Exception as e:
            logger.error(f"Error downloading video from {url}: {e}", exc_info=True)
            return None

    @staticmethod
    def cleanup_video_file(file_path: str) -> None:
        """清理下载的视频文件

        Args:
            file_path: 视频文件路径
        """
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up video file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up video file {file_path}: {e}")
