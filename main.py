#!/usr/bin/env python3
"""
书评助手 - 通过拍照获取书籍的豆瓣评分
MVP版本：支持处理本地图片文件
支持Grok API进行图片识别
"""

import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from book_extractor import BookInfoExtractor
from douban_scraper import DoubanScraper
from secure_api import SecureAPIManager


class BookRatingFinder:
    """书籍评分查询主程序"""

    def __init__(self, api_key: Optional[str] = None):
        self.use_vlm = api_key is not None
        if self.use_vlm:
            # 使用Grok API
            self.extractor = BookInfoExtractor(api_key)
        self.scraper = DoubanScraper()

    def process_image(self, image_path: str) -> dict:
        """处理图片并获取书籍评分"""
        result = {
            'success': False,
            'book_info': None,
            'douban_info': None,
            'error': None
        }

        # 检查文件是否存在
        if not Path(image_path).exists():
            result['error'] = f"图片文件不存在: {image_path}"
            return result

        try:
            # 步骤1：提取书籍信息
            if self.use_vlm:
                print("正在使用AI识别书籍信息...")
                book_info = self.extractor.extract_book_info(image_path)
            else:
                # 手动输入模式（当没有API key时）
                print("请手动输入书籍信息：")
                book_info = {
                    'title': input("书名: ").strip(),
                    'author': input("作者（可选）: ").strip() or None,
                    'publisher': input("出版社（可选）: ").strip() or None
                }

            result['book_info'] = book_info

            if not book_info.get('title'):
                result['error'] = "无法识别书籍标题"
                return result

            print(f"\n识别结果：")
            print(f"书名: {book_info.get('title', '未识别')}")
            print(f"作者: {book_info.get('author', '未识别')}")
            print(f"出版社: {book_info.get('publisher', '未识别')}")

            # 步骤2：搜索豆瓣获取评分
            print("\n正在搜索豆瓣评分...")
            douban_info = self.scraper.search_book(
                title=book_info['title'],
                author=book_info.get('author'),
                publisher=book_info.get('publisher')
            )

            if douban_info:
                result['douban_info'] = douban_info
                result['success'] = True

                print("\n豆瓣搜索结果：")
                print(f"书名: {douban_info.get('title', '未知')}")
                print(f"作者: {douban_info.get('author', '未知')}")
                print(f"出版社: {douban_info.get('publisher', '未知')}")

                if douban_info.get('rating'):
                    print(f"评分: ⭐ {douban_info['rating']}/10")
                else:
                    print("评分: 暂无评分")

                if douban_info.get('url'):
                    print(f"链接: {douban_info['url']}")
            else:
                result['error'] = "未找到对应的豆瓣图书"
                print("\n未找到对应的豆瓣图书信息")

        except Exception as e:
            result['error'] = f"处理过程中出错: {str(e)}"
            print(f"\n错误: {result['error']}")

        return result


def main():
    """主函数"""
    print("=" * 50)
    print("📚 书评助手 - 豆瓣评分查询器")
    print("=" * 50)

    # 加载环境变量
    load_dotenv()

    # 使用安全API管理器
    api_manager = SecureAPIManager()

    # 获取API密钥（优先级：环境变量 > 配置文件 > 用户输入）
    api_key = api_manager.get_api_key()

    # 如果没有API密钥，询问用户是否要配置
    if not api_key:
        print("\n⚠️  未检测到Grok API密钥")
        print("将使用手动输入模式识别书籍信息")
        print("如需使用AI自动识别，请配置Grok API密钥")

        use_api = input("\n是否要配置API密钥？(y/n): ").strip().lower()
        if use_api == 'y':
            api_key = api_manager.setup_api()

    # 创建查询器实例
    finder = BookRatingFinder(api_key)

    # 获取图片路径
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("\n请输入书籍图片路径:")
        print("（或直接拖拽图片文件到终端）")
        image_path = input().strip().strip('"').strip("'")

    # 处理图片
    print("\n开始处理...\n")
    result = finder.process_image(image_path)

    # 打印最终结果
    print("\n" + "=" * 50)
    if result['success']:
        print("✅ 查询成功！")
        if result['douban_info'] and result['douban_info'].get('rating'):
            print(f"豆瓣评分: ⭐ {result['douban_info']['rating']}/10")
    else:
        print("❌ 查询失败")
        if result['error']:
            print(f"错误信息: {result['error']}")

    print("=" * 50)


if __name__ == "__main__":
    main()