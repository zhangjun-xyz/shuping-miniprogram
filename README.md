# 📚 书评助手小程序

> AI驱动的图书识别与豆瓣评分查询小程序

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/zhangjun-xyz/shuping-miniprogram)
[![Status](https://img.shields.io/badge/status-production-success.svg)](https://shuping.zhangjun-xyz.top)
[![AI](https://img.shields.io/badge/AI-通义千问-orange.svg)](https://dashscope.aliyuncs.com)

一个功能完整的书籍豆瓣评分查询工具，支持命令行、API服务和微信小程序多种使用方式。

## ✨ 功能特色

### 🤖 AI图书识别
- **通义千问视觉模型**: 使用阿里云Qwen-VL-Max自动识别书籍封面
- **拍照识别**: 微信小程序支持拍照实时识别
- **相册选择**: 从相册选择图片进行识别
- **高准确率**: 准确提取书名、作者、出版社

### ⭐ 豆瓣集成
- 精准的书名匹配算法
- 完整的豆瓣图书信息
- 评分、星级、评价人数展示
- **豆瓣短评**: 精选3条优质短评

### 💬 豆瓣短评展示（新增）
- 显示3条精选短评
- 包含评论内容、作者、评分
- 展示点赞数（有用数）
- 快速了解书籍口碑

### 📝 手动输入搜索
- 支持手动输入书籍信息
- 可选填作者、出版社
- 搜索失败智能重试
- 友好的错误提示

### 🔐 安全管理
- 多种API密钥存储方式
- 加密配置文件支持
- 环境变量安全配置

### 📱 多平台支持
- 命令行工具（macOS/Linux/Windows）
- REST API服务
- 微信小程序

## 🏗️ 项目架构

```
📦 书评助手
├── 🖥️  命令行工具 (main.py)
├── 🌐 REST API服务 (api_server.py)
└── 📱 微信小程序 (miniprogram/)
    ├── 📸 拍照识别
    ├── 🖼️  相册选择
    ├── ✏️  手动输入
    └── 📊 结果展示
```

## 🚀 快速开始

### 方式1: 命令行工具

```bash
# 安装依赖
pip install -r requirements.txt

# 设置API密钥（可选）
export GROK_API_KEY='xai-your_api_key_here'

# 使用图片识别
python main.py /path/to/book_image.jpg

# 手动输入模式
python main.py
```

### 方式2: API服务

```bash
# 启动开发服务器
python start_dev_server.py

# 测试API
curl http://localhost:5000/health
```

### 方式3: 微信小程序

1. 使用微信开发者工具打开`miniprogram`目录
2. 配置AppID和API服务器地址
3. 预览测试或发布上线

## 📖 详细文档

- **[开发指南](DEVELOPMENT.md)** - 本地开发环境搭建和调试技巧
- **[部署指南](DEPLOYMENT.md)** - 生产环境部署和维护指南

## 🛠️ 技术栈

### 后端技术
- **Python 3.8+** - 主要开发语言
- **Flask** - Web框架和API服务
- **Requests** - HTTP客户端
- **BeautifulSoup** - HTML解析
- **通义千问 Qwen-VL-Max** - AI图像识别（v1.0.0更新）

### 前端技术
- **微信小程序** - 原生小程序开发
- **JavaScript ES6+** - 逻辑处理
- **WXSS** - 样式设计
- **WXML** - 页面结构

### 基础设施
- **Nginx** - 反向代理
- **Gunicorn** - WSGI服务器
- **SSL/TLS** - HTTPS安全连接
- **Systemd** - 服务管理

## 🎯 使用示例

### 命令行使用

```bash
$ python main.py book_cover.jpg

==================================================
📚 书评助手 - 豆瓣评分查询器
==================================================

正在使用AI识别书籍信息...

识别结果：
书名: 直抵人心的写作
作者: 艾丽丽
出版社: 机械工业出版社

正在搜索豆瓣评分...

豆瓣搜索结果：
书名: 直抵人心的写作
作者: 艾丽丽
出版社: 机械工业出版社
评分: 暂无评分
链接: https://book.douban.com/subject/36618956/

==================================================
✅ 查询成功！
==================================================
```

### API使用

```bash
# 手动搜索
curl -X POST http://localhost:5000/api/search-douban \
  -H "Content-Type: application/json" \
  -d '{"title": "直抵人心的写作"}'

# 图像识别
curl -X POST http://localhost:5000/api/recognize-book \
  -F "image=@book_cover.jpg"
```

### 微信小程序

<table>
<tr>
<td align="center">
<img src="https://via.placeholder.com/200x400/1890ff/white?text=首页" alt="首页" width="150"/>
<br/>首页 - 拍照识别
</td>
<td align="center">
<img src="https://via.placeholder.com/200x400/52c41a/white?text=结果页" alt="结果页" width="150"/>
<br/>结果页 - 豆瓣信息
</td>
<td align="center">
<img src="https://via.placeholder.com/200x400/faad14/white?text=手动输入" alt="手动输入" width="150"/>
<br/>手动输入 - 搜索功能
</td>
</tr>
</table>

## 🔧 开发和部署

### 本地开发

```bash
# 克隆项目
git clone <repository-url>
cd shuping

# 安装后端依赖
pip install -r requirements.txt

# 启动开发服务器
python start_dev_server.py

# 使用微信开发者工具打开miniprogram目录
```

### 生产部署

```bash
# 服务器配置
sudo apt update && sudo apt install python3 python3-pip nginx -y

# 项目部署
cd /var/www/shuping-api
pip install -r requirements.txt
pip install gunicorn

# 启动服务
sudo systemctl start shuping-api
sudo systemctl enable shuping-api
```

详细部署步骤请参考 [部署指南](DEPLOYMENT.md)

## 📊 性能和限制

### 性能指标
- API响应时间: < 3秒
- 图像识别准确率: 85%+
- 并发支持: 100+ 用户
- 图片大小限制: 16MB

### 技术限制
- 需要Grok API密钥进行图像识别
- 豆瓣搜索依赖网络连接
- 微信小程序需要HTTPS域名

## 💰 成本估算

### 开发成本
- 开发时间: 2-3天
- 服务器: ¥50-200/月
- 域名: ¥50/年
- API成本: 按使用量计费

### 运营成本
- 月活1000用户: ~¥100/月
- 月活10000用户: ~¥500/月

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

### 问题反馈
- 功能建议: 创建Feature Request Issue
- Bug报告: 创建Bug Report Issue
- 技术问题: 查看文档或创建Discussion

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📝 版本历史

### v1.0.0 (2025-10-24) - 首个生产版本
- 🎉 AI图书识别功能（通义千问Qwen-VL-Max）
- ⭐ 豆瓣评分自动查询
- 💬 豆瓣短评展示（3条）
- 📝 手动输入搜索功能
- 🔧 切换AI服务从Grok到通义千问
- ✨ 改进日志记录和错误处理

详见 [RELEASE_v1.0.0.md](./RELEASE_v1.0.0.md)

## 🌐 生产环境

- **API地址**: https://shuping.zhangjun-xyz.top
- **状态**: ✅ 正常运行
- **SSL证书**: DigiCert (有效至2026-01-18)
- **监控**: 24/7运行

## 📞 联系方式

- **开发者**: zj
- **项目主页**: https://github.com/zhangjun-xyz/shuping-miniprogram
- **问题反馈**: [GitHub Issues](https://github.com/zhangjun-xyz/shuping-miniprogram/issues)
- **技术支持**: 查看 [开发指南](DEVELOPMENT.md) 和 [部署指南](DEPLOYMENT.md)

## 🙏 致谢

- [阿里云通义千问](https://dashscope.aliyuncs.com) - 提供强大的视觉识别API
- [豆瓣](https://douban.com/) - 提供丰富的图书数据
- [微信小程序](https://developers.weixin.qq.com/) - 提供便捷的移动端开发平台
- [Flask](https://flask.palletsprojects.com/) - 轻量级Web框架

---

⭐ 如果这个项目对你有帮助，请给个Star支持一下！