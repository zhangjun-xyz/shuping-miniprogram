# 书评助手微信小程序开发指南

## 🏗️ 项目结构

```
shuping/
├── api_server.py              # Flask API服务器
├── book_extractor.py          # Grok API图像识别
├── douban_scraper.py          # 豆瓣搜索爬虫
├── secure_api.py              # API密钥安全管理
├── main.py                    # 原始命令行工具
├── requirements.txt           # Python依赖
├── DEPLOYMENT.md              # 部署指南
├── DEVELOPMENT.md             # 开发指南（本文件）
└── miniprogram/               # 微信小程序代码
    ├── app.js                 # 小程序入口
    ├── app.json               # 全局配置
    ├── app.wxss               # 全局样式
    ├── sitemap.json           # 站点地图
    ├── project.config.json    # 项目配置
    └── pages/                 # 页面目录
        ├── index/             # 首页
        │   ├── index.js
        │   ├── index.json
        │   ├── index.wxml
        │   └── index.wxss
        └── result/            # 结果页
            ├── result.js
            ├── result.json
            ├── result.wxml
            └── result.wxss
```

## 🛠️ 本地开发环境搭建

### 1. 后端开发环境

#### 1.1 安装依赖

```bash
cd shuping
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 1.2 配置环境变量

```bash
# 创建.env文件
echo "GROK_API_KEY=xai-your_api_key_here" > .env
echo "FLASK_ENV=development" >> .env
```

#### 1.3 启动开发服务器

```bash
# 直接运行
python api_server.py

# 或使用Flask开发服务器
export FLASK_APP=api_server.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

#### 1.4 测试API接口

```bash
# 健康检查
curl http://localhost:5000/health

# 手动搜索测试
curl -X POST http://localhost:5000/api/search-douban \
  -H "Content-Type: application/json" \
  -d '{"title": "直抵人心的写作"}'

# 图片识别测试（需要图片文件）
curl -X POST http://localhost:5000/api/recognize-book \
  -F "image=@test_image.jpg"
```

### 2. 前端开发环境

#### 2.1 微信开发者工具配置

1. 下载[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 创建新项目，导入`miniprogram`目录
3. 不使用云服务，选择JavaScript语言

#### 2.2 本地调试配置

修改`miniprogram/app.js`中的API地址：

```javascript
App({
  globalData: {
    // 本地开发环境
    apiBaseUrl: 'http://localhost:5000',
    userInfo: null
  },
  // ...
})
```

**注意**：微信小程序要求使用HTTPS，本地开发需要：

1. 在微信开发者工具中开启"不校验合法域名"
2. 或配置本地HTTPS服务

#### 2.3 本地HTTPS配置（可选）

```bash
# 安装mkcert生成本地证书
# macOS
brew install mkcert
mkcert -install
mkcert localhost 127.0.0.1

# 使用nginx配置HTTPS代理
# 安装nginx
brew install nginx

# 配置nginx.conf
cat > /usr/local/etc/nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    server {
        listen 443 ssl;
        server_name localhost;

        ssl_certificate localhost+1.pem;
        ssl_certificate_key localhost+1-key.pem;

        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
        }
    }
}
EOF

# 启动nginx
nginx
```

## 🔧 开发工具和技巧

### 1. 后端开发

#### 1.1 代码热重载

使用Flask开发模式自动重载：

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python api_server.py
```

#### 1.2 调试技巧

在代码中添加调试日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 在函数中添加
logger.info(f"处理请求: {request.json}")
logger.debug(f"识别结果: {book_info}")
```

#### 1.3 API测试脚本

创建`test_api.py`：

```python
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_health():
    response = requests.get(f'{BASE_URL}/health')
    print(f"健康检查: {response.json()}")

def test_search(title):
    response = requests.post(f'{BASE_URL}/api/search-douban',
                           json={'title': title})
    print(f"搜索结果: {response.json()}")

def test_image_recognition(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(f'{BASE_URL}/api/recognize-book',
                               files={'image': f})
    print(f"识别结果: {response.json()}")

if __name__ == '__main__':
    test_health()
    test_search('直抵人心的写作')
    # test_image_recognition('test.jpg')
```

### 2. 前端开发

#### 2.1 小程序调试

1. **console调试**：在代码中使用`console.log()`
2. **断点调试**：在开发者工具中设置断点
3. **网络调试**：查看Network面板的请求

#### 2.2 样式开发技巧

```css
/* 使用CSS变量 */
:root {
  --primary-color: #1890ff;
  --border-radius: 8rpx;
}

.btn-primary {
  background-color: var(--primary-color);
  border-radius: var(--border-radius);
}

/* 响应式设计 */
@media (max-width: 750rpx) {
  .container {
    padding: 20rpx;
  }
}
```

#### 2.3 数据模拟

开发时可以模拟API响应：

```javascript
// 在页面js文件中
mockApiResponse: function() {
  return {
    success: true,
    data: {
      book_info: {
        title: '测试书籍',
        author: '测试作者',
        publisher: '测试出版社'
      },
      douban_info: {
        title: '测试书籍',
        rating: '8.5',
        url: 'https://book.douban.com/test'
      }
    }
  }
}
```

## 🧪 测试策略

### 1. 后端测试

#### 1.1 单元测试

创建`tests/test_api.py`：

```python
import unittest
import json
from api_server import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')

    def test_search_douban(self):
        response = self.app.post('/api/search-douban',
                                json={'title': '测试'})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

#### 1.2 集成测试

测试完整的图片识别流程：

```python
def test_image_recognition_flow():
    # 1. 上传图片
    # 2. 调用Grok API
    # 3. 搜索豆瓣
    # 4. 返回结果
    pass
```

### 2. 前端测试

#### 2.1 功能测试清单

- [ ] 拍照功能正常
- [ ] 相册选择正常
- [ ] 图片上传成功
- [ ] 识别结果显示
- [ ] 豆瓣信息展示
- [ ] 手动输入搜索
- [ ] 错误处理
- [ ] 页面跳转
- [ ] 分享功能

#### 2.2 兼容性测试

测试不同设备和微信版本：
- iPhone (iOS 14+)
- Android (Android 8+)
- 微信版本 7.0+

## 🚀 性能优化

### 1. 后端优化

#### 1.1 缓存策略

```python
from functools import lru_cache
import redis

# 内存缓存
@lru_cache(maxsize=100)
def search_douban_cached(title):
    # 缓存搜索结果
    pass

# Redis缓存
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_result(key):
    result = redis_client.get(key)
    if result:
        return json.loads(result)
    return None

def set_cached_result(key, data, expire=3600):
    redis_client.setex(key, expire, json.dumps(data))
```

#### 1.2 异步处理

```python
import asyncio
import aiohttp

async def async_grok_request(image_data):
    async with aiohttp.ClientSession() as session:
        async with session.post(grok_url, data=image_data) as response:
            return await response.json()
```

### 2. 前端优化

#### 2.1 图片压缩

```javascript
// 上传前压缩图片
compressImage: function(filePath) {
  return new Promise((resolve, reject) => {
    wx.compressImage({
      src: filePath,
      quality: 80,
      success: resolve,
      fail: reject
    })
  })
}
```

#### 2.2 请求优化

```javascript
// 请求缓存
const requestCache = new Map()

request: function(options) {
  const cacheKey = JSON.stringify(options)

  if (requestCache.has(cacheKey)) {
    return Promise.resolve(requestCache.get(cacheKey))
  }

  return wx.request(options).then(result => {
    requestCache.set(cacheKey, result)
    return result
  })
}
```

## 🐛 常见问题解决

### 1. API相关问题

#### 1.1 CORS问题

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://servicewechat.com'])
```

#### 1.2 请求超时

```python
# 增加超时时间
response = requests.post(url, timeout=60)

# 异步处理长时间任务
from threading import Thread

def async_process(image_path):
    # 长时间处理
    pass

thread = Thread(target=async_process, args=(image_path,))
thread.start()
```

### 2. 小程序相关问题

#### 2.1 图片上传失败

```javascript
wx.uploadFile({
  url: apiUrl,
  filePath: imagePath,
  name: 'image',
  timeout: 60000,  // 增加超时时间
  success: (res) => {
    if (res.statusCode !== 200) {
      console.error('上传失败:', res)
    }
  },
  fail: (error) => {
    console.error('上传错误:', error)
    // 重试机制
    this.retryUpload(imagePath)
  }
})
```

#### 2.2 页面数据传递

```javascript
// 使用全局数据
getApp().globalData.bookResult = result

// 或使用事件通信
// 发送事件
this.triggerEvent('bookFound', result)

// 监听事件
this.onBookFound = function(e) {
  console.log(e.detail)
}
```

## 📚 学习资源

### 1. 微信小程序
- [官方文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [API参考](https://developers.weixin.qq.com/miniprogram/dev/api/)

### 2. Flask开发
- [Flask官方文档](https://flask.palletsprojects.com/)
- [Flask-RESTful](https://flask-restful.readthedocs.io/)

### 3. Python相关
- [Requests库](https://requests.readthedocs.io/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## 🎯 开发最佳实践

### 1. 代码规范

- 使用一致的命名规范
- 添加必要的注释
- 保持函数简洁
- 处理异常情况

### 2. 版本控制

```bash
# .gitignore
.env
*.pyc
__pycache__/
node_modules/
.DS_Store
```

### 3. 安全考虑

- API密钥不提交到代码库
- 验证用户输入
- 防止SQL注入
- 使用HTTPS

### 4. 监控和日志

```python
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# 记录API调用
@app.before_request
def log_request():
    logging.info(f"Request: {request.method} {request.url}")

@app.after_request
def log_response(response):
    logging.info(f"Response: {response.status_code}")
    return response
```

## 🔄 持续集成

### 1. GitHub Actions

创建`.github/workflows/ci.yml`：

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run tests
      run: |
        python -m pytest tests/
```

### 2. 自动部署

```yaml
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Deploy to server
      run: |
        # 部署脚本
        echo "Deploying to production..."
```

这份开发指南提供了完整的本地开发环境搭建、调试技巧、测试策略和最佳实践，帮助你高效地开发和维护书评助手微信小程序。