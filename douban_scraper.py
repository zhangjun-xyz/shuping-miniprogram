import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import time
import urllib.parse
import re


class DoubanScraper:
    """最强健版豆瓣图书搜索"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.douban.com/',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search_book(self, title: str, author: str = None, publisher: str = None, include_comments: bool = False) -> Optional[Dict]:
        """
        搜索书籍信息，使用多种策略

        Args:
            title: 书名
            author: 作者（可选）
            publisher: 出版社（可选）
            include_comments: 是否包含短评（默认False，提升性能）
        """

        print(f"开始搜索书籍: {title}")

        # 策略1: 豆瓣搜索
        result = self._search_douban_web(title, author)
        if result:
            # 只在明确要求时才获取短评
            if include_comments and result.get('url'):
                result['short_comments'] = self._get_short_comments(result['url'])
            return result

        # 策略2: 豆瓣读书直接搜索
        result = self._search_douban_book(title, author)
        if result:
            # 只在明确要求时才获取短评
            if include_comments and result.get('url'):
                result['short_comments'] = self._get_short_comments(result['url'])
            return result

        # 策略3: 返回基础信息（确保有返回值）
        return self._create_fallback_result(title, author, publisher)

    def _search_douban_web(self, title: str, author: str = None) -> Optional[Dict]:
        """通过豆瓣搜索页面查找"""
        try:
            query = title.strip()
            search_url = f"https://www.douban.com/search?cat=1001&q={urllib.parse.quote(query)}"

            print(f"尝试访问: {search_url}")

            # 重试机制
            max_retries = 2
            response = None
            for attempt in range(max_retries):
                try:
                    response = self.session.get(search_url, timeout=30)
                    print(f"响应状态: {response.status_code}")
                    if response.status_code == 200:
                        break
                except Exception as e:
                    print(f"第{attempt + 1}次尝试失败: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2)

            if not response or response.status_code != 200:
                print(f"搜索请求失败: {response.status_code if response else 'No response'}")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # 多策略查找结果
            book_info = self._extract_with_multiple_strategies(soup, title, author)
            if book_info:
                return book_info

        except Exception as e:
            print(f"豆瓣搜索异常: {e}")

        return None

    def _extract_with_multiple_strategies(self, soup, title: str, author: str = None) -> Optional[Dict]:
        """使用多种策略提取书籍信息"""

        # 策略1: 查找标准div.result结构
        results = soup.find_all('div', class_='result')
        if results:
            print(f"策略1: 找到 {len(results)} 个div.result")
            for result in results[:3]:
                book_info = self._extract_from_standard_result(result, title)
                if book_info:
                    return book_info

        # 策略2: 查找所有包含book.douban.com的链接
        print("策略2: 查找书籍链接")
        all_links = soup.find_all('a', href=True)
        book_links = []

        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()

            # 检查是否是书籍链接
            if 'book.douban.com/subject' in href or 'link2' in href:
                # 检查文本是否包含目标书名
                if self._text_contains_title(text, title):
                    book_links.append((link, text, href))

        if book_links:
            print(f"找到 {len(book_links)} 个潜在书籍链接")
            for link, text, href in book_links[:3]:
                book_info = self._extract_from_link_context(link, title, author)
                if book_info:
                    return book_info

        # 策略3: 正则表达式查找
        print("策略3: 正则表达式查找")
        page_text = soup.get_text()
        if title in page_text:
            # 使用正则查找可能的链接
            pattern = rf'(https://book\.douban\.com/subject/\d+/)'
            matches = re.findall(pattern, response.text if hasattr(self, 'response') else str(soup))
            if matches:
                return {
                    'title': title,
                    'author': author or '',
                    'publisher': '',
                    'rating': None,
                    'url': matches[0],
                    'source': 'regex_match'
                }

        return None

    def _extract_from_standard_result(self, result_elem, target_title: str) -> Optional[Dict]:
        """从标准div.result结构提取信息"""
        try:
            content_div = result_elem.find('div', class_='content')
            if not content_div:
                return None

            title_div = content_div.find('div', class_='title')
            if not title_div:
                return None

            h3_elem = title_div.find('h3')
            if not h3_elem:
                return None

            title_link = h3_elem.find('a', href=True)
            if not title_link:
                return None

            found_title = title_link.get_text(strip=True)
            clean_title = found_title.replace('[书籍]', '').strip()
            clean_title = re.sub(r'\s+', ' ', clean_title)

            if self._is_title_match(target_title, clean_title):
                link_url = title_link.get('href')

                # 处理跳转链接
                if link_url and 'link2' in link_url:
                    match = re.search(r'url=([^&]+)', link_url)
                    if match:
                        real_url = urllib.parse.unquote(match.group(1))
                        link_url = real_url

                # 提取评分和作者信息
                rating = None
                author = ''
                publisher = ''

                rating_div = title_div.find('div', class_='rating-info')
                if rating_div:
                    rating_elem = rating_div.find('span', class_='rating_nums')
                    if rating_elem:
                        try:
                            rating = float(rating_elem.get_text(strip=True))
                        except:
                            pass

                    subject_cast = rating_div.find('span', class_='subject-cast')
                    if subject_cast:
                        cast_text = subject_cast.get_text(strip=True)
                        parts = [p.strip() for p in cast_text.split('/')]
                        if len(parts) >= 1:
                            author = parts[0]
                        if len(parts) >= 2:
                            publisher = parts[1]

                return {
                    'title': clean_title,
                    'author': author,
                    'publisher': publisher,
                    'rating': rating,
                    'url': link_url or '',
                    'source': 'douban'
                }

        except Exception as e:
            print(f"标准结构提取失败: {e}")

        return None

    def _extract_from_link_context(self, link, target_title: str, author: str = None) -> Optional[Dict]:
        """从链接上下文提取信息"""
        try:
            text = link.get_text(strip=True)
            href = link.get('href')

            # 处理跳转链接
            if 'link2' in href:
                match = re.search(r'url=([^&]+)', href)
                if match:
                    real_url = urllib.parse.unquote(match.group(1))
                    href = real_url

            # 清理标题
            clean_title = text.replace('[书籍]', '').strip()

            if self._is_title_match(target_title, clean_title):
                # 尝试从父元素获取更多信息
                rating = None
                author_info = ''
                publisher_info = ''

                # 向上查找包含评分的元素
                parent = link.parent
                for _ in range(3):
                    if parent:
                        rating_elem = parent.find('span', class_='rating_nums')
                        if rating_elem:
                            try:
                                rating = float(rating_elem.get_text(strip=True))
                                break
                            except:
                                pass

                        cast_elem = parent.find('span', class_='subject-cast')
                        if cast_elem:
                            cast_text = cast_elem.get_text(strip=True)
                            parts = [p.strip() for p in cast_text.split('/')]
                            if len(parts) >= 1:
                                author_info = parts[0]
                            if len(parts) >= 2:
                                publisher_info = parts[1]
                            break

                        parent = parent.parent

                return {
                    'title': clean_title,
                    'author': author_info or author or '',
                    'publisher': publisher_info,
                    'rating': rating,
                    'url': href,
                    'source': 'link_context'
                }

        except Exception as e:
            print(f"链接上下文提取失败: {e}")

        return None

    def _text_contains_title(self, text: str, title: str) -> bool:
        """检查文本是否包含标题"""
        text_clean = text.replace('[书籍]', '').strip().lower()
        title_clean = title.strip().lower()
        return title_clean in text_clean or text_clean in title_clean

    def _search_douban_book(self, title: str, author: str = None) -> Optional[Dict]:
        """通过豆瓣读书页面搜索"""
        try:
            query = urllib.parse.quote(title)
            book_search_url = f"https://book.douban.com/subject_search?search_text={query}"

            print(f"尝试豆瓣读书搜索: {book_search_url}")

            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = self.session.get(book_search_url, timeout=30)
                    break
                except Exception as e:
                    print(f"豆瓣读书第{attempt + 1}次尝试失败: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                books = soup.find_all('li', class_='subject-item') or soup.find_all('div', class_='pic')
                print(f"豆瓣读书找到 {len(books)} 个结果")

                for book in books[:3]:
                    book_info = self._extract_book_detail(book, title)
                    if book_info:
                        return book_info

        except Exception as e:
            print(f"豆瓣读书搜索异常: {e}")

        return None

    def _extract_book_detail(self, book_elem, target_title: str) -> Optional[Dict]:
        """从豆瓣读书页面提取书籍详情"""
        try:
            title_link = book_elem.find('a', href=True)
            if not title_link:
                return None

            found_title = title_link.get_text(strip=True)
            clean_title = found_title.strip()

            if self._is_title_match(target_title, clean_title):
                book_url = title_link.get('href', '')

                if book_url and not book_url.startswith('http'):
                    book_url = 'https://book.douban.com' + book_url

                return {
                    'title': clean_title,
                    'author': '',
                    'publisher': '',
                    'rating': None,
                    'url': book_url,
                    'source': 'douban_book'
                }

        except Exception as e:
            print(f"提取豆瓣读书详情失败: {e}")

        return None

    def _is_title_match(self, search_title: str, found_title: str) -> bool:
        """判断标题是否匹配"""
        search_clean = search_title.strip().lower()
        found_clean = found_title.strip().lower()

        for mark in ['[书籍]', '(豆瓣)', '（豆瓣）']:
            found_clean = found_clean.replace(mark.lower(), '').strip()

        if search_clean == found_clean:
            return True

        if search_clean in found_clean or found_clean in search_clean:
            min_len = min(len(search_clean), len(found_clean))
            max_len = max(len(search_clean), len(found_clean))
            if min_len / max_len >= 0.7:
                return True

        return False

    def _create_fallback_result(self, title: str, author: str = None, publisher: str = None) -> Dict:
        """创建兜底结果，确保总有返回值"""
        return {
            'title': title,
            'author': author or '',
            'publisher': publisher or '',
            'rating': None,
            'url': f"https://www.douban.com/search?cat=1001&q={urllib.parse.quote(title)}",
            'source': 'fallback',
            'note': '豆瓣搜索暂时不可用，已记录书籍信息'
        }

    def _get_short_comments(self, book_url: str, limit: int = 3) -> list:
        """
        从豆瓣书籍页面获取短评

        Args:
            book_url: 豆瓣书籍详情页URL
            limit: 获取的短评数量，默认3条

        Returns:
            短评列表，每条短评包含: content(内容), author(作者), rating(评分), useful_count(有用数)
        """
        try:
            print(f"开始获取短评: {book_url}")

            # 确保URL是有效的豆瓣书籍页面
            if not book_url or 'book.douban.com/subject' not in book_url:
                print("无效的豆瓣书籍URL")
                return []

            # 请求书籍详情页
            response = self.session.get(book_url, timeout=15)
            if response.status_code != 200:
                print(f"获取书籍页面失败: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            comments = []

            # 查找短评区域 - 豆瓣的短评通常在 id="comments-section" 或 class="comment-item"
            comment_items = soup.find_all('div', class_='comment-item') or \
                           soup.find_all('li', class_='comment-item') or \
                           soup.find_all('div', class_='comment')

            print(f"找到 {len(comment_items)} 条评论")

            for item in comment_items[:limit]:
                try:
                    # 提取评论内容
                    comment_content = None
                    content_elem = item.find('span', class_='short') or \
                                  item.find('p', class_='comment-content') or \
                                  item.find('div', class_='comment-content')

                    if content_elem:
                        comment_content = content_elem.get_text(strip=True)

                    if not comment_content:
                        continue

                    # 提取作者
                    author = ''
                    author_elem = item.find('a', class_='name') or \
                                 item.find('span', class_='comment-info') or \
                                 item.find('a', href=re.compile(r'/people/'))
                    if author_elem:
                        author = author_elem.get_text(strip=True)

                    # 提取评分
                    rating = None
                    rating_elem = item.find('span', class_=re.compile(r'allstar\d+rating'))
                    if rating_elem:
                        rating_class = rating_elem.get('class', [])
                        for cls in rating_class:
                            if 'allstar' in cls:
                                # allstar50rating -> 5星, allstar40rating -> 4星
                                match = re.search(r'allstar(\d)0rating', cls)
                                if match:
                                    rating = int(match.group(1))
                                    break

                    # 提取"有用"数
                    useful_count = 0
                    useful_elem = item.find('span', class_='vote-count') or \
                                 item.find('span', class_='votes')
                    if useful_elem:
                        try:
                            useful_count = int(useful_elem.get_text(strip=True))
                        except:
                            pass

                    comments.append({
                        'content': comment_content,
                        'author': author,
                        'rating': rating,
                        'useful_count': useful_count
                    })

                except Exception as e:
                    print(f"解析单条评论失败: {e}")
                    continue

            print(f"成功提取 {len(comments)} 条短评")
            return comments

        except Exception as e:
            print(f"获取短评失败: {e}")
            return []