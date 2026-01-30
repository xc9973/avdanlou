# bot.py
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, Update
from config import Config
from handlers.message_handler import MessageHandler as MsgHandler


def setup_logging(log_level: str):
    """配置日志"""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, log_level.upper()),
    )


def main():
    """启动 Bot"""
    # 加载配置
    config = Config()

    # 配置日志
    setup_logging(config.log_level)

    # 创建应用
    application = Application.builder().token(config.bot_token).build()

    # 创建消息处理器
    msg_handler = MsgHandler()

    # 注册处理器
    application.add_handler(CommandHandler("start", msg_handler.start_command))
    application.add_handler(CommandHandler("help", msg_handler.help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler.handle_message)
    )

    # 启动 Bot
    print("Bot 启动中...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
