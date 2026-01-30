# utils/formatter.py
from handlers.link_handler import VideoInfo


def format_success_message(video: VideoInfo) -> str:
    """格式化成功消息"""
    # 格式化时长
    minutes = video.duration // 60
    seconds = video.duration % 60
    duration_str = f"{minutes}:{seconds:02d}"

    # 格式化分辨率
    resolution = f"{video.width}x{video.height}" if video.width and video.height else "未知"

    return f"""🎬 *{video.title}*

⏱ 时长: {duration_str}
📐 分辨率: {resolution}

🔗 [点击下载视频]({video.url})"""


def format_error_message(error_type: str) -> str:
    """格式化错误消息"""
    messages = {
        "invalid_url": "❌ 请发送有效的 X (Twitter) 推文链接",
        "no_video": "❌ 该推文不包含视频",
        "parse_failed": "❌ 解析失败，可能是私密内容或链接已失效",
        "rate_limit": "⚠️ 请求过于频繁，请稍后再试",
    }

    return messages.get(error_type, "❌ 发生未知错误")
