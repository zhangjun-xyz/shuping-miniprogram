# 书评助手微信小程序部署指南

## 📋 项目概述

书评助手是一个微信小程序，可以通过拍照或选择图片自动识别书籍信息，并查询豆瓣评分。

### 技术架构
- **前端**: 微信小程序
- **后端**: Flask API服务
- **AI识别**: Grok Vision API
- **数据源**: 豆瓣图书

## 🚀 推荐部署方案

### ⭐ 方案一：Vercel部署（推荐 - 免费）

#### 优势
- ✅ 完全免费
- ✅ 自动HTTPS
- ✅ 全球CDN
- ✅ 无需服务器管理
- ✅ 自动部署

#### 1.1 准备Git仓库

```bash
cd /Users/zj/workspace/open/claude/shuping
git init
git add .
git commit -m "Initial commit: 书评助手小程序"
```

#### 1.2 推送到GitHub

```bash
# 在GitHub创建新仓库：shuping-miniprogram
git remote add origin https://github.com/你的用户名/shuping-miniprogram.git
git branch -M main
git push -u origin main
```

#### 1.3 Vercel部署

1. **访问 [vercel.com](https://vercel.com/)**
2. **用GitHub账号登录**
3. **点击"New Project"**
4. **选择GitHub仓库：shuping-miniprogram**
5. **配置环境变量：**
   - `GROK_API_KEY`: `你的Grok API密钥`
   - `FLASK_ENV`: `production`
6. **点击"Deploy"**

#### 1.4 获取API地址

部署成功后，Vercel会提供HTTPS地址：
```
https://shuping-miniprogram-你的用户名.vercel.app
```

### 🚄 方案二：Railway部署（推荐）

#### 优势
- ✅ 支持数据库
- ✅ 自动HTTPS
- ✅ 简单部署
- ✅ 合理定价

#### 2.1 Railway部署

```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录
railway login

# 初始化项目
railway init

# 设置环境变量
railway variables set GROK_API_KEY=你的密钥
railway variables set FLASK_ENV=production

# 部署
railway up
```

## 📱 小程序发布配置

### 3.1 更新API地址

部署完成后，更新小程序中的API地址：

```javascript
// miniprogram/app.js
App({
  globalData: {
    // 生产环境API地址（替换为你的实际域名）
    apiBaseUrl: 'https://你的域名.vercel.app',
    userInfo: null
  },
  // ...
})
```

### 3.2 配置服务器域名

在微信公众平台配置合法域名：

1. **登录 [微信公众平台](https://mp.weixin.qq.com/)**
2. **进入小程序管理后台**
3. **开发 → 开发管理 → 开发设置**
4. **服务器域名配置：**
   - `request合法域名`: `https://你的域名.vercel.app`
   - `uploadFile合法域名`: `https://你的域名.vercel.app`

### 3.3 上传小程序代码

1. **在微信开发者工具中点击"上传"**
2. **填写版本号和项目备注**
3. **点击"上传"**

### 3.4 提交审核

1. **登录微信公众平台**
2. **版本管理 → 开发版本**
3. **点击"提交审核"**
4. **填写审核信息**
5. **等待审核通过（通常1-7天）**

## ⚡ 快速部署指南

### 最简部署步骤（推荐新手）

```bash
# 1. 推送代码到GitHub
git init
git add .
git commit -m "Deploy shuping miniprogram"
git remote add origin https://github.com/你的用户名/shuping-miniprogram.git
git push -u origin main

# 2. 访问 vercel.com 并连接GitHub仓库
# 3. 添加环境变量 GROK_API_KEY
# 4. 点击部署

# 5. 更新小程序API地址并发布
```

### 部署验证清单

- [ ] ✅ 后端API正常响应
- [ ] ✅ HTTPS证书有效
- [ ] ✅ 环境变量配置正确
- [ ] ✅ 小程序网络请求正常
- [ ] ✅ 图片上传功能正常
- [ ] ✅ AI识别功能正常
- [ ] ✅ 豆瓣搜索功能正常

### 🌐 方案三：传统VPS部署

### 1. 后端API部署

#### 1.1 服务器准备
推荐使用以下云服务商：
- 阿里云ECS
- 腾讯云CVM
- AWS EC2
- DigitalOcean

最低配置：
- CPU: 1核
- 内存: 1GB
- 存储: 20GB
- 系统: Ubuntu 20.04 LTS

#### 1.2 环境配置

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv nginx -y

# 创建项目目录
sudo mkdir /var/www/shuping-api
sudo chown $USER:$USER /var/www/shuping-api
cd /var/www/shuping-api

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 上传代码（将本地文件上传到服务器）
# scp -r shuping/* user@your-server:/var/www/shuping-api/

# 安装依赖
pip install -r requirements.txt
pip install gunicorn
```

#### 1.3 配置环境变量

```bash
# 创建环境变量文件
cat > .env << EOF
GROK_API_KEY=xai-your_api_key_here
FLASK_ENV=production
PORT=5000
EOF
```

#### 1.4 配置Gunicorn

```bash
# 创建Gunicorn配置文件
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
preload_app = True
EOF
```

#### 1.5 配置Nginx

```bash
# 创建Nginx配置
sudo cat > /etc/nginx/sites-available/shuping-api << EOF
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
EOF

# 启用站点
sudo ln -s /etc/nginx/sites-available/shuping-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 1.6 配置系统服务

```bash
# 创建systemd服务文件
sudo cat > /etc/systemd/system/shuping-api.service << EOF
[Unit]
Description=Shuping API Service
After=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=/var/www/shuping-api
Environment=PATH=/var/www/shuping-api/venv/bin
ExecStart=/var/www/shuping-api/venv/bin/gunicorn -c gunicorn.conf.py api_server:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable shuping-api
sudo systemctl start shuping-api

# 检查状态
sudo systemctl status shuping-api
```

#### 1.7 配置HTTPS（推荐）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 验证自动续期
sudo certbot renew --dry-run
```

### 2. 微信小程序部署

#### 2.1 开发者工具准备

1. 下载并安装[微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 在[微信公众平台](https://mp.weixin.qq.com/)注册小程序账号
3. 获取AppID

#### 2.2 配置小程序

1. 打开微信开发者工具
2. 导入项目，选择`miniprogram`目录
3. 输入AppID

#### 2.3 修改API地址

编辑`miniprogram/app.js`：

```javascript
App({
  globalData: {
    // 修改为你的API服务器地址
    apiBaseUrl: 'https://your-domain.com',  // 注意使用HTTPS
    userInfo: null
  },
  // ...
})
```

#### 2.4 配置服务器域名

在微信公众平台管理后台：
1. 进入"开发" -> "开发管理" -> "开发设置"
2. 在"服务器域名"中添加：
   - request合法域名：`https://your-domain.com`
   - uploadFile合法域名：`https://your-domain.com`

#### 2.5 测试和发布

1. 在开发者工具中点击"预览"，用手机扫码测试
2. 测试完成后点击"上传"
3. 在微信公众平台提交审核
4. 审核通过后发布

## 🧪 测试指南

### 后端API测试

```bash
# 测试健康检查
curl https://your-domain.com/health

# 测试手动搜索
curl -X POST https://your-domain.com/api/search-douban \
  -H "Content-Type: application/json" \
  -d '{"title": "直抵人心的写作"}'

# 测试图片识别（需要上传图片文件）
curl -X POST https://your-domain.com/api/recognize-book \
  -F "image=@/path/to/book/image.jpg"
```

### 小程序测试

1. **拍照功能测试**
   - 点击"拍照识别"
   - 拍摄书籍封面
   - 检查识别结果

2. **相册选择测试**
   - 点击"相册选择"
   - 选择书籍图片
   - 检查识别结果

3. **手动输入测试**
   - 点击"手动输入"
   - 输入书籍信息
   - 检查搜索结果

## 🔧 故障排除

### 常见问题

#### 1. API请求失败
- 检查服务器是否运行：`sudo systemctl status shuping-api`
- 检查日志：`sudo journalctl -u shuping-api -f`
- 检查Nginx配置：`sudo nginx -t`

#### 2. 图片上传失败
- 检查文件大小限制（最大16MB）
- 检查Nginx配置中的`client_max_body_size`
- 检查磁盘空间：`df -h`

#### 3. Grok API调用失败
- 验证API密钥是否正确
- 检查API额度是否充足
- 检查网络连接

#### 4. 小程序无法上传图片
- 确认服务器域名已在微信公众平台配置
- 检查HTTPS证书是否有效
- 验证API接口返回格式

### 日志查看

```bash
# 查看API服务日志
sudo journalctl -u shuping-api -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 查看应用日志
tail -f /var/www/shuping-api/app.log
```

## 📊 监控和维护

### 性能监控

1. **服务器监控**
   ```bash
   # 安装htop
   sudo apt install htop

   # 监控资源使用
   htop
   ```

2. **API监控**
   - 使用Prometheus + Grafana
   - 配置健康检查接口监控
   - 设置告警通知

### 定期维护

1. **系统更新**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

2. **SSL证书续期**
   ```bash
   sudo certbot renew
   ```

3. **日志清理**
   ```bash
   sudo journalctl --vacuum-time=30d
   ```

4. **备份数据**
   - 定期备份代码和配置文件
   - 备份SSL证书

## 🔒 安全建议

1. **服务器安全**
   - 配置防火墙（只开放22, 80, 443端口）
   - 定期更新系统
   - 使用强密码或密钥登录

2. **API安全**
   - 使用HTTPS
   - 配置请求频率限制
   - 验证上传文件类型和大小

3. **小程序安全**
   - 不在客户端存储敏感信息
   - 验证服务器返回数据
   - 使用安全的API调用

## 💰 成本估算

### 服务器成本（每月）
- 云服务器: ¥50-200
- 域名: ¥10-50/年
- SSL证书: 免费（Let's Encrypt）

### API成本
- Grok API: 根据使用量计费
- 豆瓣爬取: 免费（需遵守robots.txt）

### 总计
预估每月成本：¥100-300（取决于用户量）

## 📞 技术支持

如果遇到问题，可以：
1. 查看日志文件分析错误
2. 检查配置文件是否正确
3. 验证网络连接和域名解析
4. 联系技术支持