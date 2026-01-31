#!/usr/bin/env python3
"""
X/Twitter 视频下载脚本

使用方法:
    python3 scripts/download_x_video.py <推文链接>
    python3 scripts/download_x_video.py <推文链接> --output /path/to/save

示例:
    python3 scripts/download_x_video.py https://x.com/user/status/123456
    python3 scripts/download_x_video.py https://x.com/user/status/123456 --output ~/Downloads
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from handlers.link_handler import LinkHandler


async def download_video(url: str, output_dir: str = None):
    """下载 X 视频"""
    config = Config()
    handler = LinkHandler(config)

    print(f"🔍 正在解析: {url}")
    print("-" * 60)

    # 解析视频信息
    video_info = await handler.parse_x_video(url)

    if not video_info:
        print("❌ 未找到视频，可能是一条纯文字推文")
        return False

    print(f"📹 标题: {video_info.title}")
    print(f"⏱️  时长: {video_info.duration}秒")
    print(f"📐 分辨率: {video_info.width}x{video_info.height}")
    print(f"🔗 直链: {video_info.url}")
    print()

    # 确定输出目录
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path.home() / "Downloads"

    output_path.mkdir(parents=True, exist_ok=True)

    # 生成文件名（清理特殊字符）
    safe_title = "".join(c for c in video_info.title if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_title:
        safe_title = "twitter_video"

    filename = f"{safe_title}.mp4"
    full_path = output_path / filename

    # 检查文件是否已存在
    if full_path.exists():
        response = input(f"⚠️  文件已存在: {full_path}\n是否覆盖? (y/N): ")
        if response.lower() != 'y':
            print("❌ 取消下载")
            return False

    # 下载视频
    print(f"📥 正在下载到: {full_path}")
    print()

    try:
        import yt_dlp

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': f'{full_path.with_suffix("")}.%(ext)s',
            'merge_output_format': 'mp4',
            'overwrite': True,
        }

        # 添加 Cookie 支持
        cookie_file = config.get_twitter_cookie_file()
        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    ydl.download,
                    [video_info.url]
                )
            print()
            print("✅ 下载完成!")

            # 检查实际下载的文件
            actual_file = full_path
            if not full_path.exists():
                # yt-dlp 可能添加了 .mp4 后缀或其他格式
                possible_files = [
                    full_path,
                    full_path.with_suffix('.mp4'),
                    full_path.with_suffix('.webm'),
                    output_path / f"{safe_title}.mp4",
                ]
                for f in possible_files:
                    if f.exists():
                        actual_file = f
                        break

            print(f"📁 文件位置: {actual_file}")

            # 显示文件大小
            if actual_file.exists():
                size_mb = actual_file.stat().st_size / (1024 * 1024)
                print(f"📊 文件大小: {size_mb:.2f} MB")

            return True
        finally:
            # 清理 Cookie 文件
            if cookie_file:
                try:
                    os.remove(cookie_file)
                except:
                    pass

    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="下载 X/Twitter 视频到本地",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s https://x.com/user/status/123456
  %(prog)s https://x.com/user/status/123456 --output ~/Downloads
  %(prog)s https://twitter.com/user/status/123456 -o /tmp
        """
    )
    parser.add_argument(
        "url",
        help="X/Twitter 推文链接"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出目录（默认: ~/Downloads）",
        default=None
    )

    args = parser.parse_args()

    # 运行下载
    success = asyncio.run(download_video(args.url, args.output))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
