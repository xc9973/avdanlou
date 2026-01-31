#!/usr/bin/env python3
"""X 视频下载命令行工具

用法:
    python cli.py "https://x.com/user/status/123456789"
    python cli.py "https://x.com/user/status/123456789" --download
"""
import asyncio
import sys
import os
from handlers.link_handler import LinkHandler
from utils.validators import is_x_video_url


async def main():
    if len(sys.argv) < 2:
        print("用法: python cli.py \"<X视频链接>\" [--download]")
        print("示例: python cli.py \"https://x.com/user/status/123456789\"")
        print("      python cli.py \"https://x.com/user/status/123456789\" --download")
        sys.exit(1)

    url = sys.argv[1]
    download = "--download" in sys.argv

    # 验证链接格式
    if not is_x_video_url(url):
        print("❌ 无效的 X/Twitter 推文链接")
        print("请确保链接格式为: https://x.com/user/status/推文ID")
        sys.exit(1)

    handler = LinkHandler()

    if download:
        print(f"正在下载: {url}")
        print("-" * 50)

        video_file = await handler.download_x_video(url)

        if video_file and os.path.exists(video_file):
            file_size = os.path.getsize(video_file) / (1024 * 1024)
            print(f"✅ 下载完成!")
            print(f"  保存路径: {video_file}")
            print(f"  文件大小: {file_size:.2f}MB")
            print()
            print("提示: 临时文件，重启后会自动清理")
        else:
            print("❌ 下载失败")
            handler.cleanup_video_file(video_file)
    else:
        print(f"正在解析: {url}")
        print("-" * 50)

        video_info = await handler.parse_x_video(url)

        if not video_info:
            print("❌ 解析失败")
            print("可能原因:")
            print("  - 推文不包含视频")
            print("  - 推文为私密内容")
            print("  - 链接已失效")
            sys.exit(1)

        # 格式化时长
        minutes = int(video_info.duration // 60)
        seconds = int(video_info.duration % 60)
        duration_str = f"{minutes}:{seconds:02d}"

        # 格式化分辨率
        resolution = f"{video_info.width}x{video_info.height}" if video_info.width and video_info.height else "未知"

        print("✅ 解析成功!")
        print()
        print(f"  标题: {video_info.title}")
        print(f"  时长: {duration_str}")
        print(f"  分辨率: {resolution}")
        print()
        print("  视频直链:")
        print(f"  {video_info.url}")
        print()
        print("提示: 复制上面的链接到浏览器或下载工具中即可下载视频")
        print("      使用 --download 参数可直接下载到本地")


if __name__ == "__main__":
    asyncio.run(main())
