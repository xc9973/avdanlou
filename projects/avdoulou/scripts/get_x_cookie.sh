#!/bin/bash
# 从 Chrome 浏览器提取 Twitter/X Cookie
# 使用方法: ./scripts/get_x_cookie.sh

echo "🍪 正在提取 Twitter/X Cookie..."
echo ""

# 使用 Python 解析 Chrome Cookies 数据库
python3 << 'EOF'
import sqlite3
import os
from pathlib import Path
import shutil

# Chrome Cookies 数据库路径
cookie_db = Path.home() / "Library/Application Support/Google/Chrome/Default/Cookies"

if not cookie_db.exists():
    print("❌ 未找到 Chrome Cookie 数据库")
    print("请确保已安装 Chrome 并登录了 Twitter")
    exit(1)

# 复制数据库（Chrome 可能正在使用）
temp_db = "/tmp/chrome_cookies_temp.db"
try:
    shutil.copy(cookie_db, temp_db)
except Exception as e:
    print(f"❌ 无法访问 Cookie 数据库: {e}")
    print("请尝试手动获取 Cookie")
    exit(1)

# 连接数据库
conn = sqlite3.connect(temp_db)
cursor = conn.cursor()

# Twitter 相关的 Cookie 名称
twitter_cookies = ["auth_token", "ct0", "twid", "koh", "gt0"]

# 查询 Twitter Cookie
cursor.execute("""
    SELECT name, value, host_key
    FROM cookies
    WHERE host_key LIKE '%twitter%' OR host_key LIKE '%x.com'
    ORDER BY creation_utc DESC
""")

cookies_found = {}
for name, value, host in cursor.fetchall():
    if name in twitter_cookies and value:
        if name not in cookies_found:
            cookies_found[name] = value

conn.close()

# 清理临时文件
os.remove(temp_db)

# 输出结果
if cookies_found:
    print("✅ 找到以下 Cookie:")
    for name in twitter_cookies:
        if name in cookies_found:
            value = cookies_found[name]
            # 截断长值用于显示
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"  {name}: {display_value}")

    # 生成 Cookie 字符串
    cookie_parts = []
    for name in ["auth_token", "ct0", "twid"]:
        if name in cookies_found:
            cookie_parts.append(f"{name}={cookies_found[name]}")

    if cookie_parts:
        cookie_string = "; ".join(cookie_parts)
        print(f"\n📝 复制以下内容到 .env 文件的 TWITTER_COOKIE:")
        print(f"\nTWITTER_COOKIE={cookie_string}")

        # 保存到文件
        with open(".env.cookie", "w") as f:
            f.write(f"TWITTER_COOKIE={cookie_string}\n")
        print(f"\n✅ 已保存到 .env.cookie 文件")

        print(f"\n💡 应用 Cookie:")
        print(f"   cat .env.cookie >> .env")
    else:
        print("⚠️  未找到必需的 Cookie (auth_token, ct0)")
else:
    print("❌ 未找到 Twitter Cookie")
    print("请确保：")
    print("1. 已在 Chrome 中登录 https://twitter.com")
    print("2. Chrome 浏览器正在运行")
EOF

echo ""
