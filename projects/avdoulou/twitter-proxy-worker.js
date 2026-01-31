// Cloudflare Worker - Twitter/X Proxy
// 用于代理 Twitter/X 视频和图片请求

export default {
  async fetch(request, env, ctx) {
    // 处理 CORS 预检请求
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': '*',
        },
      });
    }

    try {
      const url = new URL(request.url);
      const path = url.pathname;

      // 根路径返回说明
      if (path === '/') {
        return new Response(getIndexHTML(), {
          headers: { 'Content-Type': 'text/html; charset=utf-8' },
        });
      }

      // 代理路径格式: /https://xxx 或 /http://xxx
      if (path.startsWith('/http')) {
        // 提取目标 URL
        const targetUrl = path.substring(1); // 去掉开头的 /

        // 构建代理请求头
        const headers = new Headers();
        headers.set('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36');
        headers.set('Accept', '*/*');
        headers.set('Accept-Language', 'en-US,en;q=0.9,zh-CN;q=0.9');
        headers.set('Accept-Encoding', 'gzip, deflate, br');
        headers.set('Referer', 'https://twitter.com/');
        headers.set('Origin', 'https://twitter.com');

        // 可选：从请求头获取自定义 Cookie
        const customCookie = request.headers.get('X-Custom-Cookie');
        if (customCookie) {
          headers.set('Cookie', customCookie);
        }

        // 转发请求到目标 URL
        const response = await fetch(targetUrl, {
          method: request.method,
          headers: headers,
        });

        // 处理重定向
        if ([301, 302, 303, 307, 308].includes(response.status)) {
          const location = response.headers.get('location');
          if (location) {
            // 将重定向 URL 也包装成代理 URL
            const proxyLocation = '/' + encodeURIComponent(location);
            return new Response(response.body, {
              status: response.status,
              statusText: response.statusText,
              headers: {
                ...Object.fromEntries(response.headers),
                'Location': proxyLocation,
                'Access-Control-Allow-Origin': '*',
              },
            });
          }
        }

        // 构建响应头
        const modifiedHeaders = new Headers();
        response.headers.forEach((value, key) => {
          if (!['content-encoding', 'content-length', 'transfer-encoding'].includes(key.toLowerCase())) {
            modifiedHeaders.set(key, value);
          }
        });
        modifiedHeaders.set('Access-Control-Allow-Origin', '*');

        return new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: modifiedHeaders,
        });
      }

      // 404
      return new Response('Not Found', { status: 404 });

    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
      });
    }
  },
};

function getIndexHTML() {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>Twitter/X Proxy Worker</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
    h1 { color: #1DA1F2; }
    .box { border: 1px solid #e1e8ed; padding: 20px; border-radius: 12px; margin: 20px 0; background: #f7f9f9; }
    code { background: #e8f5fe; padding: 4px 8px; border-radius: 4px; font-family: monospace; }
    .step { margin: 15px 0; padding-left: 20px; }
  </style>
</head>
<body>
  <h1>🐦 Twitter/X Proxy Worker</h1>

  <div class="box">
    <h3>📖 使用方法</h3>
    <p>此 Worker 用于代理 Twitter/X 请求，支持 yt-dlp 通过代理访问 Twitter 视频。</p>
  </div>

  <div class="box">
    <h3>🚀 部署步骤</h3>
    <div class="step">1. 登录 <a href="https://dash.cloudflare.com" target="_blank">Cloudflare Dashboard</a></div>
    <div class="step">2. 进入 <strong>Workers & Pages</strong> → <strong>Create application</strong></div>
    <div class="step">3. 选择 <strong>Create Worker</strong>，输入名称（如 twitter-proxy）</div>
    <div class="step">4. 将本文件内容复制到编辑器中</div>
    <div class="step">5. 点击 <strong>Deploy</strong> 部署</div>
  </div>

  <div class="box">
    <h3>⚙️ 配置 Bot</h3>
    <p>在 Bot 的 .env 文件中添加：</p>
    <code>TWITTER_PROXY_URL=https://your-worker.workers.dev</code>
    <p style="margin-top: 10px; color: #666; font-size: 14px;">
      将 <code>your-worker.workers.dev</code> 替换为你的 Worker 实际地址
    </p>
  </div>

  <div class="box">
    <h3>✅ 测试</h3>
    <p>部署后访问：</p>
    <code>https://your-worker.workers.dev/</code>
    <p style="margin-top: 10px; color: #666; font-size: 14px;">
      应该能看到本页面
    </p>
  </div>
</body>
</html>`;
}
