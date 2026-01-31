#!/usr/bin/env python3
"""
X 视频解析 API 服务

为 iOS 快捷指令提供简单的 HTTP API
"""
import logging
import argparse

from aiohttp import web
from aiohttp.web import Request, Response

from config import Config
from handlers.link_handler import LinkHandler


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoAPI:
    """视频解析 API"""

    def __init__(self):
        self.config = Config()
        self.handler = LinkHandler(self.config)

    async def parse(self, request: Request) -> Response:
        """解析视频 API

        POST /parse
        Body: {"url": "https://x.com/user/status/123456"}
        """
        try:
            data = await request.json()
            url = data.get('url', '')

            if not url:
                return web.json_response(
                    {'error': '缺少 url 参数'},
                    status=400
                )

            logger.info(f"解析请求: {url}")

            # 解析视频
            video_info = await self.handler.parse_x_video(url)

            if not video_info:
                return web.json_response(
                    {'error': '未找到视频'},
                    status=404
                )

            return web.json_response({
                'success': True,
                'data': {
                    'title': video_info.title,
                    'duration': video_info.duration,
                    'width': video_info.width,
                    'height': video_info.height,
                    'url': video_info.url,
                    'original_url': url
                }
            })

        except Exception as e:
            logger.error(f"解析失败: {e}", exc_info=True)
            return web.json_response(
                {'error': str(e)},
                status=500
            )

    async def extract(self, request: Request) -> Response:
        """提取内容 API（支持图片）

        GET /extract?url=https://x.com/user/status/123456
        """
        try:
            url = request.query.get('url', '')

            if not url:
                return web.json_response(
                    {'error': '缺少 url 参数'},
                    status=400
                )

            logger.info(f"提取请求: {url}")

            # 提取内容
            content = await self.handler.extract_x_content(url)

            if content['type'] == 'unknown':
                return web.json_response(
                    {'error': '未找到媒体内容'},
                    status=404
                )

            result = {
                'success': True,
                'type': content['type'],
                'original_url': url
            }

            if content['type'] == 'video':
                item = content['items'][0]
                # 从 yt-dlp 返回的数据中提取 URL
                video_url = item.get('url') or item.get('webpage_url', '')
                result['video'] = {
                    'title': item.get('title', ''),
                    'url': video_url,
                    'duration': item.get('duration', 0),
                    'width': item.get('width', 0),
                    'height': item.get('height', 0)
                }
            elif content['type'] == 'photos':
                result['photos'] = [
                    {'url': photo.url, 'width': photo.width, 'height': photo.height}
                    for photo in content['items']
                ]

            return web.json_response(result)

        except Exception as e:
            logger.error(f"提取失败: {e}", exc_info=True)
            return web.json_response(
                {'error': str(e)},
                status=500
            )

    async def health(self, request: Request) -> Response:
        """健康检查"""
        return web.json_response({'status': 'ok'})


def create_app() -> web.Application:
    """创建 aiohttp 应用"""
    api = VideoAPI()

    app = web.Application()
    app.router.add_post('/parse', api.parse)
    app.router.add_get('/extract', api.extract)
    app.router.add_get('/health', api.health)

    return app


def main():
    """启动服务器"""
    parser = argparse.ArgumentParser(description="X 视频解析 API 服务")
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    parser.add_argument('--port', type=int, default=8080, help='监听端口')
    args = parser.parse_args()

    logger.info(f"🚀 启动服务: http://{args.host}:{args.port}")
    logger.info(f"📝 API 端点:")
    logger.info(f"   POST   /parse   - 解析视频 (JSON Body)")
    logger.info(f"   GET    /extract - 提取内容 (URL 参数)")
    logger.info(f"   GET    /health  - 健康检查")

    app = create_app()
    web.run_app(app, host=args.host, port=args.port)


if __name__ == '__main__':
    main()
