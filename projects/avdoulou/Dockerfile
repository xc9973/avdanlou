FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（yt-dlp 可能需要 ffmpeg）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY --chown=appuser:appuser . .

# 切换到非 root 用户
USER appuser

# 运行 Bot
CMD ["python", "bot.py"]
