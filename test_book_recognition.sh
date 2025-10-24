#!/bin/bash

# 书籍识别API测试脚本
API_BASE="http://118.178.127.189"

echo "=== 书籍识别API测试 ==="
echo "API地址: $API_BASE"
echo

# 测试1: 健康检查
echo "1. 健康检查..."
curl -s "$API_BASE/health" | python3 -m json.tool
echo -e "\n"

# 测试2: 使用图片URL测试 - 《活着》
echo "2. 测试《活着》封面识别..."
curl -X POST "$API_BASE/api/recognize-book" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://img3.doubanio.com/view/subject/l/public/s29053580.jpg"
  }' | python3 -m json.tool
echo -e "\n"

# 测试3: 使用图片URL测试 - 《三体》
echo "3. 测试《三体》封面识别..."
curl -X POST "$API_BASE/api/recognize-book" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://img1.doubanio.com/view/subject/l/public/s2768378.jpg"
  }' | python3 -m json.tool
echo -e "\n"

# 测试4: 使用图片URL测试 - 《平凡的世界》
echo "4. 测试《平凡的世界》封面识别..."
curl -X POST "$API_BASE/api/recognize-book" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://img2.doubanio.com/view/subject/l/public/s1144911.jpg"
  }' | python3 -m json.tool
echo -e "\n"

# 测试5: 使用图片URL测试 - 《百年孤独》
echo "5. 测试《百年孤独》封面识别..."
curl -X POST "$API_BASE/api/recognize-book" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://img3.doubanio.com/view/subject/l/public/s6384944.jpg"
  }' | python3 -m json.tool
echo -e "\n"

echo "=== 测试完成 ==="
echo "如果某个测试失败，可以单独运行对应的curl命令进行调试"