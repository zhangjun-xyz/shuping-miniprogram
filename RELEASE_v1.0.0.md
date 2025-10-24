# 书评助手小程序 v1.0.0 发布说明

## 🎉 版本信息
- **版本号**: v1.0.0
- **发布日期**: 2025-10-24
- **状态**: 生产环境已部署

## ✨ 核心功能

### 1. AI图书识别 🤖
- 使用通义千问 Qwen-VL-Max 视觉模型
- 拍照或相册选择书籍封面图片
- 自动识别书名、作者、出版社
- 识别准确率高，响应速度快

### 2. 豆瓣评分查询 ⭐
- 自动获取豆瓣图书评分
- 显示评分、评价人数
- 展示书籍详细信息
- 提供豆瓣链接跳转

### 3. 豆瓣短评展示 💬
- 显示3条精选豆瓣短评
- 包含评论内容、作者、评分
- 显示有用数（点赞数）
- 帮助用户快速了解书籍口碑

### 4. 手动输入搜索 📝
- 支持手动输入书名搜索
- 可选填作者、出版社信息
- 提供搜索失败后的重试功能

## 🔧 技术栈

### 后端
- **框架**: Flask 2.3.2
- **AI模型**: 阿里云通义千问 Qwen-VL-Max
- **数据源**: 豆瓣图书、Open Library、Google Books
- **部署**: 阿里云ECS + Nginx + Gunicorn
- **环境**: Python 3.8

### 前端
- **平台**: 微信小程序
- **API域名**: https://shuping.zhangjun-xyz.top

## 📋 主要文件说明

### 后端核心文件
- `api_server.py` - Flask API服务器，处理所有API请求
- `book_extractor.py` - AI书籍信息提取器（通义千问）
- `douban_scraper.py` - 豆瓣图书信息爬虫（含短评功能）
- `book_api.py` - 备用图书API（Open Library、Google Books）

### 小程序核心文件
- `miniprogram/pages/index/` - 首页（拍照/选图/手动输入）
- `miniprogram/pages/result/` - 结果展示页（评分+短评）
- `miniprogram/app.js` - 全局配置（API地址）

### 配置文件
- `.env` - 环境变量配置（API密钥）
- `requirements.txt` - Python依赖包
- `gunicorn.conf.py` - Gunicorn配置

### 部署脚本
- `deploy-china.sh` - 阿里云/腾讯云部署脚本
- `test_ai_recognition.sh` - AI识别功能测试脚本

## 🚀 部署信息

### 生产环境
- **服务器**: 阿里云ECS (Ubuntu 20.04)
- **域名**: https://shuping.zhangjun-xyz.top
- **SSL证书**: DigiCert (有效期至2026-01-18)
- **API状态**: ✅ 正常运行
- **AI服务**: ✅ 通义千问已接入
- **豆瓣爬虫**: ✅ 正常工作

### API端点
- `GET /health` - 健康检查
- `POST /api/recognize-book` - AI图书识别
- `POST /api/search-douban` - 手动搜索豆瓣

## 📝 更新日志

### v1.0.0 (2025-10-24)

#### 新增功能
- ✅ AI图书识别（通义千问Qwen-VL-Max）
- ✅ 豆瓣评分自动查询
- ✅ 豆瓣短评展示（3条）
- ✅ 手动输入搜索功能
- ✅ 搜索失败重试功能

#### 技术优化
- ✅ 从Grok API迁移到通义千问API（解决网络访问问题）
- ✅ 添加环境变量加载（python-dotenv）
- ✅ 改进日志记录（从print到logging）
- ✅ 修复API端点URL重复问题
- ✅ 多策略豆瓣信息获取（提高成功率）
- ✅ 备用API支持（Open Library、Google Books）

#### Bug修复
- ✅ 修复AI识别功能失败问题
- ✅ 修复环境变量未加载导致API密钥丢失
- ✅ 修复服务器无法访问国际API的问题

## 🧪 测试验证

所有核心功能已通过测试：
- ✅ AI识别《活着》- 成功（评分9.4，3条短评）
- ✅ AI识别《三体》- 成功（评分8.9，3条短评）
- ✅ 手动搜索功能 - 正常
- ✅ 健康检查API - 正常
- ✅ HTTPS访问 - 正常

## 📦 依赖包版本

```
Flask==2.3.2
Flask-CORS==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
python-dotenv==1.0.1
Pillow==9.5.0
gunicorn==20.1.0
```

## 🔒 安全说明

- API密钥存储在`.env`文件（已加入.gitignore）
- 生产环境使用HTTPS加密传输
- CORS配置限制访问来源
- 文件上传大小限制16MB

## 📱 小程序信息

- **小程序名称**: 书评助手
- **AppID**: (待填写)
- **服务类目**: 图书/阅读
- **待审核**: 需要在微信开发者工具中上传代码

## 🔮 后续规划

### v1.1.0 计划
- [ ] 添加用户收藏功能
- [ ] 书籍阅读进度记录
- [ ] 个人书评发布
- [ ] 推荐算法优化

### v1.2.0 计划
- [ ] 社区功能（书友交流）
- [ ] 读书笔记
- [ ] 阅读统计分析

## 🙏 致谢

- **AI服务**: 阿里云通义千问
- **数据来源**: 豆瓣读书、Open Library、Google Books API
- **云服务**: 阿里云ECS

---

**项目地址**: (待添加GitHub链接)
**问题反馈**: (待添加Issues链接)
**开发者**: zj
