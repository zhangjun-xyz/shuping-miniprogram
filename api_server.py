from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
import tempfile
from pathlib import Path
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from book_extractor import BookInfoExtractor
from douban_scraper import DoubanScraper
from book_api import BookAPI

# 设置日志
log_level = logging.INFO if os.getenv('FLASK_ENV') == 'production' else logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 生产环境CORS配置
if os.getenv('FLASK_ENV') == 'production':
    # 生产环境：只允许特定域名
    CORS(app, origins=['https://servicewechat.com'])
else:
    # 开发环境：允许所有域名
    CORS(app)

# 配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/', methods=['GET'])
def index():
    """API根路径"""
    return jsonify({
        'name': '书评助手 API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'recognize': '/api/recognize-book',
            'search': '/api/search-douban'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'message': 'API服务正常运行'})

@app.route('/MP_verify_<path:filename>')
def wechat_verify(filename):
    """微信域名验证文件"""
    try:
        return send_from_directory('.', f'MP_verify_{filename}')
    except FileNotFoundError:
        return '', 404

@app.route('/api/recognize-book', methods=['POST'])
def recognize_book():
    """识别书籍信息"""
    try:
        logger.info(f"收到图片识别请求 - Content-Type: {request.content_type}")
        logger.info(f"请求文件: {list(request.files.keys())}")

        # 检查请求
        has_image_file = 'image' in request.files
        has_base64 = False

        # 安全地检查JSON数据
        try:
            has_base64 = request.is_json and request.json and 'imageBase64' in request.json
        except Exception as e:
            # 如果不是JSON请求，忽略错误
            logger.debug(f"JSON检查失败（正常）: {e}")
            pass

        logger.info(f"has_image_file: {has_image_file}, has_base64: {has_base64}")

        if not has_image_file and not has_base64:
            return jsonify({
                'success': False,
                'error': '请提供图片文件或base64编码的图片'
            }), 400

        # 获取API密钥
        api_key = os.getenv('GROK_API_KEY')
        use_ai = bool(api_key)

        # 处理图片
        image_path = None
        temp_file = None

        if 'image' in request.files:
            # 处理文件上传
            file = request.files['image']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': '没有选择文件'
                }), 400

            # 保存临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            file.save(temp_file.name)
            image_path = temp_file.name

        elif has_base64:
            # 处理base64图片
            try:
                image_data = base64.b64decode(request.json['imageBase64'])
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                temp_file.write(image_data)
                temp_file.close()
                image_path = temp_file.name
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'base64解码失败: {str(e)}'
                }), 400

        # 识别书籍信息
        book_info = {}

        if use_ai and image_path:
            try:
                extractor = BookInfoExtractor(api_key)
                book_info = extractor.extract_book_info(image_path)
                logger.info(f"AI识别结果: {book_info}")
            except Exception as e:
                logger.error(f"AI识别失败: {str(e)}")
                # AI失败时，返回空的书籍信息，让用户手动输入
                book_info = {}

        # 清理临时文件
        if temp_file and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

        # 搜索图书信息
        book_detail_info = None
        if book_info.get('title'):
            # 首先尝试豆瓣搜索
            try:
                scraper = DoubanScraper()
                book_detail_info = scraper.search_book(
                    title=book_info['title'],
                    author=book_info.get('author'),
                    publisher=book_info.get('publisher')
                )
                logger.info(f"豆瓣搜索结果: {book_detail_info}")
            except Exception as e:
                logger.error(f"豆瓣搜索失败: {str(e)}")

            # 如果豆瓣搜索失败，使用备用API
            if not book_detail_info:
                try:
                    book_api = BookAPI()
                    book_detail_info = book_api.search_book(
                        title=book_info['title'],
                        author=book_info.get('author')
                    )
                    logger.info(f"备用API搜索结果: {book_detail_info}")
                except Exception as e:
                    logger.error(f"备用API搜索失败: {str(e)}")

        return jsonify({
            'success': True,
            'data': {
                'book_info': book_info,
                'douban_info': book_detail_info,  # 改名以保持兼容性
                'use_ai': use_ai
            }
        })

    except Exception as e:
        logger.error(f"识别书籍信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500

@app.route('/api/search-douban', methods=['POST'])
def search_douban():
    """手动搜索图书信息"""
    try:
        data = request.json
        if not data or not data.get('title'):
            return jsonify({
                'success': False,
                'error': '请提供书名'
            }), 400

        # 首先尝试豆瓣搜索
        book_info = None
        try:
            scraper = DoubanScraper()
            book_info = scraper.search_book(
                title=data['title'],
                author=data.get('author'),
                publisher=data.get('publisher')
            )
            logger.info(f"豆瓣搜索结果: {book_info}")
        except Exception as e:
            logger.error(f"豆瓣搜索失败: {str(e)}")

        # 如果豆瓣搜索失败，使用备用API
        if not book_info:
            try:
                book_api = BookAPI()
                book_info = book_api.search_book(
                    title=data['title'],
                    author=data.get('author')
                )
                logger.info(f"备用API搜索结果: {book_info}")
            except Exception as e:
                logger.error(f"备用API搜索失败: {str(e)}")

        return jsonify({
            'success': True,
            'data': book_info
        })

    except Exception as e:
        logger.error(f"搜索图书失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'搜索失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    logger.info(f"启动API服务，端口: {port}")
    logger.info(f"Grok API: {'已配置' if os.getenv('GROK_API_KEY') else '未配置'}")

    app.run(host='0.0.0.0', port=port, debug=debug)