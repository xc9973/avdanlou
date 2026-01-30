# utils/validators.py
import re
from urllib.parse import urlparse


def is_x_video_url(url: str) -> bool:
    """验证是否为 X/Twitter 推文链接"""
    if not url:
        return False

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # 检查域名
        if domain not in ["x.com", "twitter.com", "www.x.com", "www.twitter.com"]:
            return False

        # 检查路径是否包含 /status/
        return "/status/" in parsed.path
    except Exception:
        return False


def extract_tweet_id(url: str) -> str | None:
    """从 X 链接中提取推文 ID"""
    if not is_x_video_url(url):
        return None

    try:
        # 匹配 /status/ 后面的数字
        match = re.search(r"/status/(\d+)", url)
        if match:
            return match.group(1)
    except Exception:
        pass

    return None
