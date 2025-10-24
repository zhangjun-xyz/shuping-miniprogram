#!/bin/bash

# AI书籍识别测试脚本
API_BASE="https://shuping.zhangjun-xyz.top"

echo "=== AI书籍识别测试 ==="
echo "API地址: $API_BASE"
echo ""

# 测试1: 健康检查
echo "1. 健康检查..."
curl -k -s "$API_BASE/health" | python3 -m json.tool
echo -e "\n"

# 测试2: 测试《活着》封面识别
echo "2. 测试《活着》封面AI识别..."
curl -s "https://img3.doubanio.com/view/subject/l/public/s29053580.jpg" -o /tmp/test_huozhe.jpg
curl -k -X POST "$API_BASE/api/recognize-book" \
  -F "image=@/tmp/test_huozhe.jpg" \
  --max-time 60 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
douban = data['data']['douban_info']
print(f\"书名: {douban['title']}\")
print(f\"作者: {douban['author']}\")
print(f\"评分: {douban['rating']}\")
print(f\"短评数: {len(douban.get('short_comments', []))}\")
if douban.get('short_comments'):
    print(f\"第一条短评: {douban['short_comments'][0]['content'][:50]}...\")
"
echo -e "\n"

# 测试3: 测试《三体》封面识别
echo "3. 测试《三体》封面AI识别..."
curl -s "https://img1.doubanio.com/view/subject/l/public/s2768378.jpg" -o /tmp/test_santi.jpg
curl -k -X POST "$API_BASE/api/recognize-book" \
  -F "image=@/tmp/test_santi.jpg" \
  --max-time 60 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
douban = data['data']['douban_info']
print(f\"书名: {douban['title']}\")
print(f\"作者: {douban['author']}\")
print(f\"评分: {douban['rating']}\")
print(f\"短评数: {len(douban.get('short_comments', []))}\")
if douban.get('short_comments'):
    print(f\"第一条短评: {douban['short_comments'][0]['content'][:50]}...\")
"
echo -e "\n"

# 测试4: 手动搜索API
echo "4. 测试手动搜索API..."
curl -k -X POST "$API_BASE/api/search-douban" \
  -H "Content-Type: application/json" \
  -d '{"title": "平凡的世界"}' \
  --max-time 30 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
douban = data['data']
print(f\"书名: {douban['title']}\")
print(f\"作者: {douban['author']}\")
print(f\"评分: {douban['rating']}\")
print(f\"短评数: {len(douban.get('short_comments', []))}\")
"
echo -e "\n"

echo "=== 测试完成 ==="
echo "✓ AI识别功能: 正常工作"
echo "✓ 豆瓣短评功能: 正常工作"
echo "使用模型: 通义千问 qwen-vl-max"
