# bot.py
import logging
import signal
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.error import TelegramError
from config import Config
from handlers.message_handler import MessageHandler as MsgHandler


def setup_logging(log_level: str) -> None:
    """配置日志系统。

    Args:
        log_level: 日志级别字符串，如 'INFO', 'DEBUG'
    """
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=getattr(logging, log_level.upper()),
    )


def main():
    """启动 Bot"""
    # 加载配置
    config = Config()

    # 验证配置
    if not config.bot_token or config.bot_token == "your_bot_token_here":
        print("错误: 请设置有效的 BOT_TOKEN 环境变量")
        sys.exit(1)

    # 配置日志
    setup_logging(config.log_level)

    # 创建应用
    try:
        application = Application.builder().token(config.bot_token).build()
    except Exception as e:
        print(f"错误: 无法创建 Telegram 应用 - {e}")
        sys.exit(1)

    # 创建消息处理器
    msg_handler = MsgHandler()

    # 注册处理器
    application.add_handler(CommandHandler("start", msg_handler.start_command))
    application.add_handler(CommandHandler("help", msg_handler.help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler.handle_message)
    )

    # 信号处理器
    def signal_handler(sig, frame):
        logging.info("接收到退出信号，正在关闭 Bot...")
        print("\n正在关闭 Bot...")
        application.stop_running()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 启动 Bot
    try:
        print("Bot 启动中...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except TelegramError as e:
        logging.error(f"Telegram API 错误: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logging.error(f"Bot 运行出错: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
