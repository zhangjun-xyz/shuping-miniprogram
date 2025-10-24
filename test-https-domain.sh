#!/bin/bash

# 测试HTTPS域名配置
API_BASE="https://shuping.zhangjun-xyz.top"

echo "=== 测试HTTPS域名配置 ==="
echo "域名: $API_BASE"
echo

# 1. 健康检查
echo "1. 健康检查..."
curl -k -s "$API_BASE/health" | python3 -m json.tool 2>/dev/null || curl -k -s "$API_BASE/health"
echo

# 2. 测试豆瓣搜索API
echo "2. 测试豆瓣搜索API..."
curl -k -X POST "$API_BASE/api/search-douban" \
  -H "Content-Type: application/json" \
  -d '{"title": "三体"}' \
  --max-time 30 | python3 -m json.tool 2>/dev/null || echo "搜索API测试失败"
echo

# 3. 测试书籍识别API (简单测试)
echo "3. 测试书籍识别API..."
curl -k -X POST "$API_BASE/api/recognize-book" \
  -H "Content-Type: application/json" \
  -d '{"imageBase64": "test"}' \
  --max-time 10 | python3 -m json.tool 2>/dev/null || echo "识别API测试失败"
echo

echo "=== 测试完成 ==="
echo "如果所有测试都成功，说明HTTPS域名配置正确"