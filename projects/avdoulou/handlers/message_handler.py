# handlers/message_handler.py
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from handlers.link_handler import LinkHandler, PhotoInfo
from utils.validators import is_x_video_url
from utils.formatter import format_error_message


class MessageHandler:
    """Telegram 消息处理器"""

    logger = logging.getLogger(__name__)

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self.link_handler = LinkHandler(self.config)

    def _check_whitelist(self, update: Update) -> bool:
        """检查用户是否在白名单中"""
        user_id = update.effective_user.id
        if not self.config.is_user_allowed(user_id):
            self.logger.warning(f"Unauthorized access attempt from user_id: {user_id}")
            return False
        return True

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /start 命令"""
        if not self._check_whitelist(update):
            await update.message.reply_text("❌ 你没有权限使用此 Bot")
            return

        welcome_message = """👋 欢迎！我是 X 媒体直链 Bot

使用方法：
1. 发送 X (Twitter) 推文链接
2. 我会返回视频或图片的直链

支持的链接格式：
• https://x.com/user/status/123456
• https://twitter.com/user/status/123456"""

        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /help 命令"""
        if not self._check_whitelist(update):
            await update.message.reply_text("❌ 你没有权限使用此 Bot")
            return

        help_message = """📖 使用帮助

发送 X (Twitter) 推文链接，我会返回视频或图片的直链。

注意事项：
• 只支持公开推文
• 私密推文无法解析
• 自动选择最高画质
• 视频返回 MP4 直链
• 图片返回原图链接

如有问题请联系管理员。"""

        await update.message.reply_text(help_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理普通消息"""
        if not self._check_whitelist(update):
            await update.message.reply_text("❌ 你没有权限使用此 Bot")
            return

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
            # 先检查内容类型
            content = await self.link_handler.extract_x_content(text)

            await processing_msg.delete()

            if content["type"] == "video":
                # 处理视频 - 返回直链
                await self._handle_video(update, text)
            elif content["type"] == "photos":
                # 处理图片 - 返回直链
                await self._handle_photos(update, content["items"])
            else:
                await update.message.reply_text("❌ 该推文不包含视频或图片")

        except Exception as e:
            await processing_msg.delete()
            await update.message.reply_text("❌ 处理失败，请稍后重试")
            self.logger.error(f"Failed to handle {text[:50]}...: {e}", exc_info=True)

    async def _handle_video(self, update: Update, url: str) -> None:
        """处理视频 - 返回直链"""
        try:
            video_info = await self.link_handler.parse_x_video(url)
            if video_info:
                message = f"""🎬 视频直链

📌 {video_info.title}
📐 {video_info.width}x{video_info.height}
⏱️ {video_info.duration}秒

🔗 {video_info.url}"""
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("❌ 无法获取视频链接")

        except Exception as e:
            await update.message.reply_text("❌ 处理失败，请稍后重试")
            self.logger.error(f"Failed to handle video: {e}", exc_info=True)

    async def _handle_photos(self, update: Update, photos: list[PhotoInfo]) -> None:
        """处理图片 - 返回直链"""
        try:
            if not photos:
                await update.message.reply_text("❌ 无法获取图片链接")
                return

            message = f"📷 图片直链（共 {len(photos)} 张）\n\n"
            for i, photo in enumerate(photos, 1):
                message += f"{i}. {photo.url}\n"

            await update.message.reply_text(message)

        except Exception as e:
            await update.message.reply_text("❌ 处理失败，请稍后重试")
            self.logger.error(f"Failed to handle photos: {e}", exc_info=True)
