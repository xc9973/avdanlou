# handlers/message_handler.py
import logging
import os
from telegram import Update
from telegram.ext import ContextTypes
from handlers.link_handler import LinkHandler
from utils.validators import is_x_video_url
from utils.formatter import format_success_message, format_error_message


class MessageHandler:
    """Telegram 消息处理器"""

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.link_handler = LinkHandler()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /start 命令"""
        welcome_message = """👋 欢迎！我是 X 视频下载 Bot

使用方法：
1. 发送 X (Twitter) 推文链接
2. 我会自动下载视频并发送给你

支持的链接格式：
• https://x.com/user/status/123456
• https://twitter.com/user/status/123456

注意：视频超过 50MB 将返回直链"""

        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /help 命令"""
        help_message = """📖 使用帮助

发送 X (Twitter) 推文链接，我会自动下载视频并发送给你。

注意事项：
• 只支持公开推文
• 私密推文无法解析
• 自动选择最高画质
• 50MB 以内直接发送视频文件
• 超过 50MB 返回下载直链

如有问题请联系管理员。"""

        await update.message.reply_text(help_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理普通消息"""
        # 获取消息文本
        text = update.message.text

        if not text:
            return

        # 检查是否为 X 链接
        if not is_x_video_url(text):
            await update.message.reply_text(format_error_message("invalid_url"))
            return

        # 发送处理中消息
        processing_msg = await update.message.reply_text("⏳ 正在下载视频...")

        video_file = None
        try:
            # 下载视频
            video_file = await self.link_handler.download_x_video(text)

            # 删除处理中消息
            await processing_msg.delete()

            if video_file and os.path.exists(video_file):
                # 发送视频文件
                file_size = os.path.getsize(video_file)
                file_size_mb = file_size / (1024 * 1024)

                # Telegram 限制 50MB，超过则提示
                if file_size > 50 * 1024 * 1024:
                    await update.message.reply_text(
                        f"⚠️ 视频过大 ({file_size_mb:.1f}MB)，超过 Telegram 50MB 限制\n"
                        f"请使用以下方式获取："
                    )
                    # 仍然返回直链作为备选
                    video_info = await self.link_handler.parse_x_video(text)
                    if video_info:
                        await update.message.reply_text(
                            format_success_message(video_info),
                            parse_mode="Markdown"
                        )
                else:
                    with open(video_file, "rb") as video:
                        await update.message.reply_video(
                            video,
                            caption=f"🎬 {os.path.basename(video_file)}",
                            read_timeout=60,
                            write_timeout=60
                        )
                    await update.message.reply_text("✅ 下载完成！")
            else:
                await update.message.reply_text(format_error_message("no_video"))

        except Exception as e:
            await processing_msg.delete()
            await update.message.reply_text("❌ 下载失败，请稍后重试")
            self.logger.error(f"Failed to download video from {text[:50]}...: {e}", exc_info=True)

        finally:
            # 清理临时文件
            if video_file:
                self.link_handler.cleanup_video_file(video_file)
