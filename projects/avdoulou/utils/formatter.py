# utils/formatter.py
import re
from handlers.link_handler import VideoInfo

# Telegram MarkdownV2 需要转义的字符
MARKDOWN_ESCAPE_CHARS = r'_*[]()~`>#+-=|{}.!'
MARKDOWN_ESCAPE_PATTERN = re.compile(f'([{re.escape(MARKDOWN_ESCAPE_CHARS)}])')

DEFAULT_RESOLUTION_TEXT = "未知"
UNKNOWN_ERROR_MESSAGE = "❌ 发生未知错误"
MAX_MESSAGE_LENGTH = 1024


__all__ = ['format_success_message', 'format_error_message']


def format_success_message(video: VideoInfo) -> str:
    """格式化成功消息"""
    # 格式化时长
    minutes = video.duration // 60
    seconds = video.duration % 60
    duration_str = f"{minutes}:{seconds:02d}"

    # 格式化分辨率
    resolution = f"{video.width}x{video.height}" if video.width and video.height else DEFAULT_RESOLUTION_TEXT

    # 转义标题中的 Markdown 特殊字符
    safe_title = MARKDOWN_ESCAPE_PATTERN.sub(r'\\\1', video.title)

    message = f"""🎬 *{safe_title}*

⏱ 时长: {duration_str}
📐 分辨率: {resolution}

🔗 [点击下载视频]({video.url})"""

    # 消息长度保护
    if len(message) > MAX_MESSAGE_LENGTH:
        # 截断标题
        max_title_length = MAX_MESSAGE_LENGTH - len(message) + len(safe_title) - 10
        safe_title = safe_title[:max_title_length] + "..."
        message = f"""🎬 *{safe_title}*

⏱ 时长: {duration_str}
📐 分辨率: {resolution}

🔗 [点击下载视频]({video.url})"""

    return message


def format_error_message(error_type: str) -> str:
    """格式化错误消息"""
    messages = {
        "invalid_url": "❌ 请发送有效的 X (Twitter) 推文链接",
        "no_video": "❌ 该推文不包含视频",
        "parse_failed": "❌ 解析失败，可能是私密内容或链接已失效",
        "rate_limit": "⚠️ 请求过于频繁，请稍后再试",
    }

    return messages.get(error_type, UNKNOWN_ERROR_MESSAGE)
