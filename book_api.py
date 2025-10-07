import requests
import urllib.parse
from typing import Optional, Dict


class BookAPI:
    """图书信息API - 使用开放的图书数据源"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def search_book(self, title: str, author: str = None) -> Optional[Dict]:
        """搜索图书信息"""

        # 优先使用Open Library API
        result = self._search_open_library(title, author)
        if result:
            return result

        # 备用：使用Google Books API
        result = self._search_google_books(title, author)
        if result:
            return result

        return None

    def _search_open_library(self, title: str, author: str = None) -> Optional[Dict]:
        """使用Open Library API搜索"""
        try:
            # 构建搜索查询
            query = title
            if author:
                query += f" {author}"

            url = f"https://openlibrary.org/search.json?title={urllib.parse.quote(query)}&limit=5"

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('docs'):
                book = data['docs'][0]  # 取第一个结果

                return {
                    'title': book.get('title', ''),
                    'author': ', '.join(book.get('author_name', [])) if book.get('author_name') else '',
                    'publisher': ', '.join(book.get('publisher', [])) if book.get('publisher') else '',
                    'publish_year': book.get('first_publish_year'),
                    'isbn': book.get('isbn', [None])[0] if book.get('isbn') else None,
                    'rating': None,  # Open Library 没有评分
                    'url': f"https://openlibrary.org{book.get('key', '')}" if book.get('key') else None,
                    'source': 'Open Library'
                }

        except Exception as e:
            print(f"Open Library搜索失败: {e}")

        return None

    def _search_google_books(self, title: str, author: str = None) -> Optional[Dict]:
        """使用Google Books API搜索"""
        try:
            # 构建搜索查询
            query = f"intitle:{title}"
            if author:
                query += f"+inauthor:{author}"

            url = f"https://www.googleapis.com/books/v1/volumes?q={urllib.parse.quote(query)}&maxResults=5"

            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('items'):
                book = data['items'][0]['volumeInfo']  # 取第一个结果

                return {
                    'title': book.get('title', ''),
                    'author': ', '.join(book.get('authors', [])) if book.get('authors') else '',
                    'publisher': book.get('publisher', ''),
                    'publish_year': book.get('publishedDate', '').split('-')[0] if book.get('publishedDate') else None,
                    'isbn': None,
                    'rating': book.get('averageRating'),
                    'url': book.get('infoLink'),
                    'source': 'Google Books'
                }

        except Exception as e:
            print(f"Google Books搜索失败: {e}")

        return None