#!/usr/bin/env python3
"""
获取《直抵人心的写作》的豆瓣评分
"""

import requests
from bs4 import BeautifulSoup
import time


def get_book_rating():
    """直接访问书籍详情页获取评分"""
    # 从搜索结果中得到的书籍链接
    book_url = "https://book.douban.com/subject/36618956/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    print("=" * 60)
    print("📚 《直抵人心的写作》豆瓣信息查询")
    print("=" * 60)

    try:
        response = requests.get(book_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取书籍信息
        result = {
            'title': '直抵人心的写作',
            'url': book_url
        }

        # 提取评分
        rating_elem = soup.find('strong', class_='ll rating_num') or \
                     soup.find('strong', property='v:average')
        if rating_elem:
            result['rating'] = rating_elem.text.strip()
        else:
            # 可能暂无评分
            no_rating = soup.find('div', class_='rating_sum')
            if no_rating and '暂无' in no_rating.text:
                result['rating'] = '暂无评分'

        # 提取评价人数
        rating_people = soup.find('span', property='v:votes')
        if rating_people:
            result['rating_people'] = rating_people.text.strip()

        # 提取详细信息
        info_elem = soup.find('div', id='info')
        if info_elem:
            info_text = info_elem.text
            lines = info_text.split('\n')
            for line in lines:
                if '作者' in line:
                    result['author'] = line.split(':')[-1].strip()
                elif '出版社' in line:
                    result['publisher'] = line.split(':')[-1].strip()
                elif '出版年' in line:
                    result['publish_year'] = line.split(':')[-1].strip()
                elif '页数' in line:
                    result['pages'] = line.split(':')[-1].strip()
                elif 'ISBN' in line:
                    result['isbn'] = line.split(':')[-1].strip()

        # 提取简介
        intro_elem = soup.find('div', class_='intro')
        if intro_elem:
            intro_text = intro_elem.text.strip()
            result['intro'] = intro_text[:200] + '...' if len(intro_text) > 200 else intro_text

        # 显示结果
        print(f"\n书名: {result.get('title')}")
        print(f"作者: {result.get('author', '未知')}")
        print(f"出版社: {result.get('publisher', '未知')}")
        print(f"出版年: {result.get('publish_year', '未知')}")

        print("\n" + "-" * 60)
        if result.get('rating') and result['rating'] != '暂无评分':
            print(f"⭐ 豆瓣评分: {result['rating']}/10")
            if result.get('rating_people'):
                print(f"评价人数: {result['rating_people']}人")
        else:
            print("📊 评分: 暂无评分（可能是新书）")

        print("-" * 60)

        if result.get('intro'):
            print(f"\n简介:\n{result['intro']}")

        print(f"\n📖 详情页: {book_url}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
    except Exception as e:
        print(f"解析错误: {e}")

    return None


if __name__ == "__main__":
    get_book_rating()