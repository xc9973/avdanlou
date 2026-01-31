# handlers/link_handler.py
import asyncio
import logging
import yt_dlp
from dataclasses import dataclass
from typing import List
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


@dataclass
class PhotoInfo:
    """图片信息"""
    url: str
    width: int
    height: int


class LinkHandler:
    """链接处理器"""

    def __init__(self, config=None):
        self.config = config

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
        # 如果配置了代理，重写 URL
        target_url = self._maybe_rewrite_url(url)

        # 第一步：使用 extract_flat 获取推文信息（支持转推）
        ydl_opts_flat = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,  # 支持转推，不解析格式
        }

        # 添加 Cookie 支持（用于 18+ 内容）
        cookie_file = None
        if self.config:
            cookie_file = self.config.get_twitter_cookie_file()
            if cookie_file:
                ydl_opts_flat["cookiefile"] = cookie_file

            if self.config.use_proxy():
                logger.info(f"Using proxy for URL: {target_url}")

        try:
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
                info = await loop.run_in_executor(
                    None,
                    ydl.extract_info,
                    target_url,
                    False,
                )

                if not info:
                    return None

                # 第二步：如果找到了视频，获取最佳格式的 URL
                # 如果 info 中有 url，直接使用；否则从 formats 中提取
                video_url = info.get("url")
                if not video_url:
                    formats = info.get("formats", [])
                    # 选择有视频流的最佳格式
                    best_format = None
                    for f in formats:
                        vcodec = f.get("vcodec", "none")
                        if vcodec and vcodec != "none":
                            height = f.get("height", 0)
                            if best_format is None or height > best_format.get("height", 0):
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
        finally:
            # 清理临时 cookie 文件
            if cookie_file:
                try:
                    import os
                    os.remove(cookie_file)
                except:
                    pass


    async def extract_x_content(self, url: str) -> dict:
        """提取 X 推文内容（视频或图片）

        Args:
            url: X/Twitter 推文链接

        Returns:
            包含内容的字典: {"type": "video"|"photos", "items": [...]}
        """
        if not is_x_video_url(url):
            return {"type": "unknown", "items": []}

        # 如果配置了代理，重写 URL
        target_url = self._maybe_rewrite_url(url)

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,  # 支持转推
        }

        # 添加 Cookie 支持
        cookie_file = None
        if self.config:
            cookie_file = self.config.get_twitter_cookie_file()
            if cookie_file:
                ydl_opts["cookiefile"] = cookie_file

            if self.config.use_proxy():
                logger.info(f"Using proxy for URL: {target_url}")

        info = None
        try:
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(
                    None,
                    ydl.extract_info,
                    target_url,
                    False,  # download=False
                )
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
        finally:
            # 清理临时 cookie 文件
            if cookie_file:
                try:
                    os.remove(cookie_file)
                except:
                    pass

        if not info:
            return {"type": "unknown", "items": []}

        # 优先检查是否有视频（通过 formats）
        formats = info.get("formats", [])
        has_video = any(f.get("vcodec") != "none" for f in formats if f.get("vcodec"))
        if has_video or info.get("duration"):
            return {"type": "video", "items": [info]}

        # 检查是否有图片
        thumbnails = info.get("thumbnails")
        if thumbnails:
            # 提取高质量图片
            photos = []
            seen_urls = set()
            for thumb in thumbnails:
                img_url = thumb.get("url")
                if img_url and "?format=" not in img_url and img_url not in seen_urls:
                    # 过滤掉小尺寸预览图，只保留原图
                    if "orig" in img_url or "large" in img_url or "medium" in img_url:
                        seen_urls.add(img_url)
                        photos.append(PhotoInfo(
                            url=img_url,
                            width=thumb.get("width", 0),
                            height=thumb.get("height", 0)
                        ))
                    if len(photos) >= 4:  # 最多4张图
                        break

            if photos:
                return {"type": "photos", "items": photos}

        return {"type": "unknown", "items": []}

    def _maybe_rewrite_url(self, url: str) -> str:
        """如果配置了代理，重写 URL 为代理格式"""
        if self.config and self.config.use_proxy():
            proxy_url = self.config.twitter_proxy_url.rstrip('/')
            # 格式: https://worker.workers.dev/https://original-url
            return f"{proxy_url}/{url}"
        return url

