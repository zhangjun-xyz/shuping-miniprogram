#!/usr/bin/env python3
"""
快速启动开发服务器
用于本地测试微信小程序
"""

import os
import sys
from pathlib import Path

# 加载.env文件
def load_env():
    """加载.env文件中的环境变量"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 加载环境变量
load_env()

from api_server import app

def main():
    """启动开发服务器"""
    # 检查命令行参数
    port = 5002
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == '--port' and i + 1 < len(sys.argv):
                port = int(sys.argv[i + 1])
                break

    print("=" * 50)
    print("📚 书评助手 - 开发服务器")
    print("=" * 50)

    # 检查API密钥
    api_key = os.getenv('GROK_API_KEY')
    if api_key:
        print(f"✅ Grok API: 已配置")
    else:
        print("⚠️  Grok API: 未配置（将使用手动模式）")

    # 开发环境配置
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'

    print("\n🚀 启动开发服务器...")
    print(f"📱 小程序请配置API地址: http://localhost:{port}")
    print(f"🌐 API文档: http://localhost:{port}/health")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("=" * 50)

    try:
        # 启动Flask开发服务器
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")

if __name__ == '__main__':
    main()