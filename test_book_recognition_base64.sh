#!/bin/bash

# 书籍识别API测试脚本 (Base64方式)
API_BASE="http://118.178.127.189"
TEMP_DIR="/tmp/book_covers"

echo "=== 书籍识别API测试 (Base64方式) ==="
echo "API地址: $API_BASE"
echo

# 创建临时目录
mkdir -p "$TEMP_DIR"

# 测试书籍列表
declare -A books=(
    ["活着"]="https://img3.doubanio.com/view/subject/l/public/s29053580.jpg"
    ["三体"]="https://img1.doubanio.com/view/subject/l/public/s2768378.jpg"
    ["平凡的世界"]="https://img2.doubanio.com/view/subject/l/public/s1144911.jpg"
    ["百年孤独"]="https://img3.doubanio.com/view/subject/l/public/s6384944.jpg"
)

# 函数：下载图片并转换为base64
download_and_convert() {
    local book_name=$1
    local image_url=$2
    local temp_file="$TEMP_DIR/${book_name}.jpg"

    echo "下载 ${book_name} 封面..."
    if curl -s -o "$temp_file" "$image_url"; then
        echo "转换为base64..."
        local base64_data=$(base64 -i "$temp_file")
        echo "$base64_data"
    else
        echo "下载失败"
        return 1
    fi
}

# 函数：测试书籍识别
test_book_recognition() {
    local book_name=$1
    local image_url=$2

    echo "=== 测试《${book_name}》封面识别 ==="

    local base64_data=$(download_and_convert "$book_name" "$image_url")

    if [ $? -eq 0 ] && [ -n "$base64_data" ]; then
        echo "发送识别请求..."
        curl -X POST "$API_BASE/api/recognize-book" \
          -H "Content-Type: application/json" \
          -d "{\"imageBase64\": \"$base64_data\"}" \
          --max-time 30 | python3 -m json.tool
    else
        echo "❌ 无法获取图片数据"
    fi

    echo -e "\n"
}

# 健康检查
echo "1. 健康检查..."
curl -s "$API_BASE/health" | python3 -m json.tool
echo -e "\n"

# 测试每本书
counter=2
for book_name in "${!books[@]}"; do
    echo "$counter. 开始测试《$book_name》..."
    test_book_recognition "$book_name" "${books[$book_name]}"
    ((counter++))
done

# 清理临时文件
rm -rf "$TEMP_DIR"

echo "=== 测试完成 ==="