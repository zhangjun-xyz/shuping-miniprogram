#!/bin/bash

# 书评助手 - 腾讯云/阿里云/华为云部署脚本
# 适用于 Ubuntu 20.04 系统

echo "===== 书评助手部署脚本 ====="
echo "开始部署..."

# 1. 更新系统
echo "1. 更新系统..."
sudo apt update && sudo apt upgrade -y

# 2. 安装必要软件
echo "2. 安装必要软件..."
sudo apt install -y python3 python3-pip python3-venv nginx git curl

# 3. 安装Node.js (用于前端工具)
echo "3. 安装Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 4. 创建项目目录
echo "4. 创建项目目录..."
sudo mkdir -p /var/www/shuping-api
sudo chown $USER:$USER /var/www/shuping-api
cd /var/www/shuping-api

# 5. 克隆项目代码（你需要先将代码推送到GitHub）
echo "5. 获取项目代码..."
# git clone https://github.com/你的用户名/shuping-miniprogram.git .
echo "请手动上传代码文件到此目录"

# 6. 创建Python虚拟环境
echo "6. 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 7. 安装Python依赖
echo "7. 安装Python依赖..."
cat > requirements.txt << EOF
Flask==2.3.2
Flask-CORS==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
python-dotenv==1.0.0
Pillow==9.5.0
gunicorn==20.1.0
EOF

pip install -r requirements.txt

# 8. 配置环境变量
echo "8. 配置环境变量..."
cat > .env << EOF
GROK_API_KEY=你的Grok_API密钥
FLASK_ENV=production
PORT=5000
EOF

echo "请编辑 .env 文件，填入你的真实API密钥"

# 9. 配置Gunicorn
echo "9. 配置Gunicorn..."
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

# 10. 配置Nginx
echo "10. 配置Nginx..."
sudo cat > /etc/nginx/sites-available/shuping-api << EOF
server {
    listen 80;
    server_name \$server_name;  # 替换为你的域名或IP

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

# 启用Nginx站点
sudo ln -sf /etc/nginx/sites-available/shuping-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 11. 配置系统服务
echo "11. 配置系统服务..."
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

echo "===== 部署完成 ====="
echo ""
echo "接下来的步骤："
echo "1. 编辑 /var/www/shuping-api/.env 文件，填入Grok API密钥"
echo "2. 上传项目代码到 /var/www/shuping-api/"
echo "3. 运行: sudo systemctl start shuping-api"
echo "4. 检查状态: sudo systemctl status shuping-api"
echo "5. 配置域名或使用IP地址访问"
echo ""
echo "默认访问地址：http://你的服务器IP/"