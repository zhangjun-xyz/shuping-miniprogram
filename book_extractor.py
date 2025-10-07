import base64
import requests
from typing import Dict
import json


class BookInfoExtractor:
    """使用Grok API从书籍图片中提取信息"""

    def __init__(self, api_key: str):
        """
        初始化提取器
        支持xAI Grok API
        """
        self.api_key = api_key

        # Grok API配置
        if api_key.startswith('xai-'):
            self.api_base_url = "https://api.x.ai"
            # 使用最新的Grok视觉模型 (2024年12月版本)
            self.model = "grok-2-vision-1212"  # 最新的视觉模型
        else:
            # 兼容其他API
            self.api_base_url = "https://api.openai.com"
            self.model = "gpt-4-vision-preview"

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def extract_book_info(self, image_path: str) -> Dict[str, str]:
        """从书籍图片中提取信息"""
        base64_image = self.encode_image(image_path)

        # 构建更精确的提示词
        system_prompt = """你是一个专业的中文图书信息识别专家。
请仔细观察图片，准确识别并提取以下信息：
1. 书名（完整的中文书名，不要添加任何标点符号）
2. 作者（如果有多个作者，用逗号分隔）
3. 出版社（完整的出版社名称）

注意：
- 仔细区分相似的汉字，如"抵"和"男"
- 书名通常是最大最醒目的文字
- 作者名通常在书名下方或封面某处
- 出版社通常在封面底部

请以纯JSON格式返回，不要添加任何额外的文字或markdown标记。"""

        user_prompt = """请识别这本书的信息。
这是一本中文书籍的封面照片。
请仔细观察并返回JSON格式：
{
  "title": "书名",
  "author": "作者",
  "publisher": "出版社"
}"""

        # API请求
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"  # 使用高分辨率模式
                            }
                        }
                    ]
                }
            ],
            "temperature": 0,  # 降低温度以获得更准确的结果
            "max_tokens": 500,
            "top_p": 0.1  # 降低随机性
        }

        try:
            response = requests.post(
                f"{self.api_base_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            content = result['choices'][0]['message']['content']

            # 打印原始响应以便调试
            print(f"AI原始响应: {content}")

            # 清理响应内容
            content = content.strip()

            # 移除可能的markdown代码块标记
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]

            content = content.strip()

            # 尝试解析JSON
            try:
                book_info = json.loads(content)

                # 清理返回的数据
                if 'title' in book_info:
                    book_info['title'] = book_info['title'].strip().strip('"').strip()
                if 'author' in book_info:
                    book_info['author'] = book_info['author'].strip().strip('"').strip()
                if 'publisher' in book_info:
                    book_info['publisher'] = book_info['publisher'].strip().strip('"').strip()

                return book_info

            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试从文本中提取
                print(f"JSON解析失败，尝试文本解析")
                return self._parse_text_response(content)

        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"错误详情: {e.response.text}")
            return {}

    def _parse_text_response(self, content: str) -> Dict[str, str]:
        """从非JSON格式的文本响应中提取信息"""
        result = {}
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if '书名' in line or 'title' in line.lower() or '标题' in line:
                # 提取书名
                if '：' in line:
                    result['title'] = line.split('：', 1)[-1].strip().strip('"').strip()
                elif ':' in line:
                    result['title'] = line.split(':', 1)[-1].strip().strip('"').strip()
                elif '》' in line and '《' in line:
                    # 提取书名号中的内容
                    start = line.find('《')
                    end = line.find('》')
                    if start != -1 and end != -1:
                        result['title'] = line[start+1:end]

            elif '作者' in line or 'author' in line.lower():
                if '：' in line:
                    result['author'] = line.split('：', 1)[-1].strip().strip('"').strip()
                elif ':' in line:
                    result['author'] = line.split(':', 1)[-1].strip().strip('"').strip()

            elif '出版社' in line or 'publisher' in line.lower():
                if '：' in line:
                    result['publisher'] = line.split('：', 1)[-1].strip().strip('"').strip()
                elif ':' in line:
                    result['publisher'] = line.split(':', 1)[-1].strip().strip('"').strip()

        return result