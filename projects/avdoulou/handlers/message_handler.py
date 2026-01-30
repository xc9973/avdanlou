# handlers/message_handler.py
import logging
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
2. 我会解析并返回视频直链
3. 点击链接即可下载

支持的链接格式：
• https://x.com/user/status/123456
• https://twitter.com/user/status/123456"""

        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /help 命令"""
        help_message = """📖 使用帮助

发送 X (Twitter) 推文链接，我会返回视频的直链。

注意事项：
• 只支持公开推文
• 私密推文无法解析
• 自动选择最高画质

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
        processing_msg = await update.message.reply_text("⏳ 正在解析...")

        try:
            # 解析视频
            video_info = await self.link_handler.parse_x_video(text)

            # 删除处理中消息
            await processing_msg.delete()

            if video_info:
                # 发送结果
                await update.message.reply_text(
                    format_success_message(video_info),
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(format_error_message("no_video"))

        except Exception as e:
            await processing_msg.delete()
            await update.message.reply_text(format_error_message("parse_failed"))
            self.logger.error(f"Failed to parse video from {text[:50]}...: {e}", exc_info=True)
