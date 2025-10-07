import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import time
import urllib.parse
import re


class DoubanScraper:
    """豆瓣图书搜索和评分获取"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://book.douban.com/',
        }

    def _is_title_match(self, search_title: str, found_title: str) -> bool:
        """判断书名是否匹配"""
        # 清理标题
        search_clean = search_title.strip().lower()
        found_clean = found_title.strip().lower()

        # 完全匹配
        if search_clean == found_clean:
            return True

        # 包含关系（搜索的标题完全在找到的标题中）
        if search_clean in found_clean:
            # 但要避免部分匹配导致的错误，比如"写作"匹配到"文学写作"
            # 检查是否是完整的书名
            if len(search_clean) >= len(found_clean) * 0.7:  # 至少占70%
                return True

        # 找到的标题在搜索标题中（可能用户输入了更长的标题）
        if found_clean in search_clean:
            if len(found_clean) >= len(search_clean) * 0.7:
                return True

        return False

    def search_book(self, title: str, author: str = None, publisher: str = None) -> Optional[Dict]:
        """搜索书籍并获取评分"""
        # 使用更通用的豆瓣搜索页面
        search_query = title
        search_url = f"https://www.douban.com/search?cat=1001&q={urllib.parse.quote(search_query)}"

        try:
            # 发送请求
            response = requests.get(search_url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找搜索结果 - 豆瓣搜索页面的结构
            items = soup.find_all('div', class_='result')[:5]  # 查看前5个结果

            for item in items:
                # 提取书籍链接和标题
                title_elem = item.find('h3')
                if title_elem:
                    # 获取完整的标题文本，去除多余空格和标签
                    found_title = title_elem.text.strip()
                    # 移除可能的前缀如 [书籍]
                    if '[书籍]' in found_title:
                        found_title = found_title.replace('[书籍]', '').strip()
                    # 移除可能的后缀标记
                    found_title = found_title.split('\n')[0].strip()

                    # 严格匹配：书名必须完全一致或非常相似
                    if self._is_title_match(title, found_title):
                        # 找到匹配的书籍，获取详情页链接
                        link_elem = item.find('a', href=True)
                        if link_elem:
                            # 处理豆瓣的跳转链接
                            href = link_elem['href']
                            if 'book.douban.com' in href:
                                # 提取实际的书籍链接
                                match = re.search(r'url=(.*?)&', href)
                                if match:
                                    book_url = urllib.parse.unquote(match.group(1))
                                else:
                                    book_url = href

                                # 访问书籍详情页获取完整信息
                                book_detail = self._get_book_detail(book_url)
                                if book_detail:
                                    # 再次验证书名是否匹配
                                    if self._is_title_match(title, book_detail.get('title', '')):
                                        return book_detail

            # 没有找到匹配的书籍
            print(f"未找到与《{title}》匹配的书籍")
            return None

        except Exception as e:
            print(f"搜索出错: {e}")

        # 备用方案：使用豆瓣API风格的搜索
        return self._search_via_api(title, author, publisher)

    def _extract_book_info(self, item, target_title: str, target_author: str, target_publisher: str) -> Optional[Dict]:
        """从搜索结果项中提取书籍信息"""
        try:
            # 提取标题
            title_elem = item.find('a', class_='title-text') or item.find('h3') or item.find('a', href=True)
            if not title_elem:
                return None

            title = title_elem.text.strip() if hasattr(title_elem, 'text') else ''

            # 提取评分
            rating_elem = item.find('span', class_='rating_nums') or item.find('span', class_='rating')
            rating = None
            if rating_elem:
                rating_text = rating_elem.text.strip()
                try:
                    rating = float(rating_text)
                except:
                    pass

            # 提取链接
            link = None
            if hasattr(title_elem, 'get'):
                link = title_elem.get('href')
                if link and not link.startswith('http'):
                    link = f"https://book.douban.com{link}"

            # 提取作者和出版社信息
            meta_elem = item.find('div', class_='meta') or item.find('p', class_='meta')
            author = ''
            publisher = ''
            if meta_elem:
                meta_text = meta_elem.text.strip()
                parts = meta_text.split('/')
                if len(parts) >= 1:
                    author = parts[0].strip()
                if len(parts) >= 3:
                    publisher = parts[-2].strip()

            # 检查是否匹配
            if target_title and target_title.lower() in title.lower():
                return {
                    'title': title,
                    'author': author,
                    'publisher': publisher,
                    'rating': rating,
                    'url': link
                }

        except Exception as e:
            print(f"解析项目出错: {e}")

        return None

    def _extract_first_result(self, item) -> Dict:
        """提取第一个搜索结果"""
        result = {
            'title': '未知',
            'author': '未知',
            'publisher': '未知',
            'rating': None,
            'url': None
        }

        try:
            title_elem = item.find('a', class_='title-text') or item.find('h3') or item.find('a', href=True)
            if title_elem:
                result['title'] = title_elem.text.strip()
                if hasattr(title_elem, 'get'):
                    result['url'] = title_elem.get('href')
                    if result['url'] and not result['url'].startswith('http'):
                        result['url'] = f"https://book.douban.com{result['url']}"

            rating_elem = item.find('span', class_='rating_nums') or item.find('span', class_='rating')
            if rating_elem:
                try:
                    result['rating'] = float(rating_elem.text.strip())
                except:
                    pass

            meta_elem = item.find('div', class_='meta') or item.find('p', class_='meta')
            if meta_elem:
                meta_text = meta_elem.text.strip()
                parts = meta_text.split('/')
                if len(parts) >= 1:
                    result['author'] = parts[0].strip()
                if len(parts) >= 3:
                    result['publisher'] = parts[-2].strip()

        except Exception as e:
            print(f"解析第一个结果出错: {e}")

        return result

    def _search_via_api(self, title: str, author: str, publisher: str) -> Optional[Dict]:
        """使用API风格的搜索（备用）"""
        try:
            # 构建搜索查询
            query = title
            if author:
                query += f" {author}"

            # 使用豆瓣的旧版搜索接口风格
            api_url = f"https://search.douban.com/book/subject_search?search_text={urllib.parse.quote(query)}"

            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找书籍信息
            result_items = soup.find_all('div', class_='result')

            for item in result_items[:3]:
                # 提取书籍详情页链接
                link_elem = item.find('a', class_='nbg') or item.find('a', href=True)
                if link_elem:
                    book_url = link_elem.get('href')
                    if book_url:
                        # 访问书籍详情页获取评分
                        book_info = self._get_book_detail(book_url)
                        if book_info:
                            return book_info

        except Exception as e:
            print(f"API搜索失败: {e}")

        return None

    def _get_book_detail(self, url: str) -> Optional[Dict]:
        """获取书籍详情页信息"""
        try:
            time.sleep(1)  # 避免请求过快

            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            result = {
                'url': url,
                'title': '未知',
                'author': '未知',
                'publisher': '未知',
                'rating': None
            }

            # 提取标题
            title_elem = soup.find('h1')
            if title_elem:
                result['title'] = title_elem.find('span').text.strip() if title_elem.find('span') else title_elem.text.strip()

            # 提取评分
            rating_elem = soup.find('strong', class_='ll rating_num') or soup.find('strong', property='v:average')
            if rating_elem:
                try:
                    result['rating'] = float(rating_elem.text.strip())
                except:
                    pass

            # 提取作者和出版社
            info_elem = soup.find('div', id='info')
            if info_elem:
                info_text = info_elem.text
                lines = info_text.split('\n')
                for line in lines:
                    if '作者' in line:
                        result['author'] = line.split(':')[-1].strip()
                    elif '出版社' in line:
                        result['publisher'] = line.split(':')[-1].strip()

            return result

        except Exception as e:
            print(f"获取详情页失败: {e}")
            return None