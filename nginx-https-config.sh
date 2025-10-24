#!/bin/bash

# 更新Nginx配置文件以支持HTTPS域名
echo "更新Nginx配置以支持HTTPS域名 shuping.zhangjun-xyz.top"

# 创建新的Nginx配置
cat > /etc/nginx/sites-available/shuping-api << 'EOF'
server {
    listen 80;
    server_name shuping.zhangjun-xyz.top;

    # 重定向HTTP到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name shuping.zhangjun-xyz.top;

    # SSL证书配置
    ssl_certificate /ssl/cert.pem;
    ssl_certificate_key /ssl/cert.key;

    # SSL配置优化
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # CORS配置
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE";
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";

    # 处理OPTIONS请求
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
        add_header Access-Control-Max-Age 1728000;
        add_header Content-Type 'text/plain; charset=utf-8';
        add_header Content-Length 0;
        return 204;
    }

    # API代理配置
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 健康检查接口
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态文件缓存（如果有的话）
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 检查Nginx配置语法
echo "检查Nginx配置语法..."
nginx -t

if [ $? -eq 0 ]; then
    echo "Nginx配置语法正确"

    # 重新加载Nginx配置
    echo "重新加载Nginx配置..."
    systemctl reload nginx

    echo "配置完成！"
    echo "现在可以通过以下地址访问："
    echo "- https://shuping.zhangjun-xyz.top/health"
    echo "- https://shuping.zhangjun-xyz.top/api/recognize-book"
    echo "- https://shuping.zhangjun-xyz.top/api/search-douban"
else
    echo "❌ Nginx配置语法错误，请检查"
fi

# 显示服务状态
echo -e "\n=== 服务状态 ==="
systemctl status nginx --no-pager
echo -e "\n=== API服务状态 ==="
systemctl status shuping-api --no-pager