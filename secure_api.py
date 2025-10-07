"""
API密钥安全管理模块
支持多种安全存储方式
"""
import os
import json
import getpass
from pathlib import Path
from typing import Optional, Dict
import base64


class SecureAPIManager:
    """安全管理API密钥"""

    def __init__(self):
        self.config_dir = Path.home() / '.shuping'
        self.config_file = self.config_dir / 'config.json'
        self.encrypted_config = self.config_dir / '.credentials'

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(exist_ok=True, mode=0o700)  # 仅用户可读写

    def _simple_encrypt(self, text: str, key: str) -> str:
        """简单的XOR加密（用于基本保护）"""
        # 注意：这只是基本保护，对于生产环境建议使用更强的加密
        key_bytes = key.encode()
        text_bytes = text.encode()
        encrypted = []

        for i, byte in enumerate(text_bytes):
            key_byte = key_bytes[i % len(key_bytes)]
            encrypted.append(byte ^ key_byte)

        return base64.b64encode(bytes(encrypted)).decode()

    def _simple_decrypt(self, encrypted_text: str, key: str) -> str:
        """简单的XOR解密"""
        key_bytes = key.encode()
        encrypted_bytes = base64.b64decode(encrypted_text)
        decrypted = []

        for i, byte in enumerate(encrypted_bytes):
            key_byte = key_bytes[i % len(key_bytes)]
            decrypted.append(byte ^ key_byte)

        return bytes(decrypted).decode()

    def save_api_key(self, api_key: str, provider: str = 'grok') -> bool:
        """保存API密钥"""
        self._ensure_config_dir()

        try:
            # 方案1：加密存储到文件
            master_key = getpass.getpass("请设置主密码（用于加密API密钥）: ")
            confirm_key = getpass.getpass("请确认主密码: ")

            if master_key != confirm_key:
                print("密码不匹配！")
                return False

            encrypted_key = self._simple_encrypt(api_key, master_key)

            config = {
                'provider': provider,
                'encrypted_key': encrypted_key,
                'hint': '使用主密码解密'
            }

            with open(self.encrypted_config, 'w', encoding='utf-8') as f:
                json.dump(config, f)

            # 设置文件权限为仅用户可读
            self.encrypted_config.chmod(0o600)

            print(f"✅ API密钥已安全保存")
            return True

        except Exception as e:
            print(f"保存失败: {e}")
            return False

    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        # 优先级顺序：
        # 1. 环境变量
        # 2. 加密配置文件
        # 3. 提示用户输入

        # 1. 检查环境变量
        env_key = os.getenv('GROK_API_KEY')
        if env_key:
            return env_key

        # 2. 从加密文件读取
        if self.encrypted_config.exists():
            try:
                with open(self.encrypted_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                master_key = getpass.getpass("请输入主密码: ")
                api_key = self._simple_decrypt(config['encrypted_key'], master_key)
                return api_key

            except Exception as e:
                print(f"读取配置失败: {e}")

        # 3. 提示用户输入
        return None

    def setup_api(self) -> Optional[str]:
        """设置API密钥的交互式流程"""
        print("\n📝 API密钥设置")
        print("-" * 40)
        print("请选择配置方式：")
        print("1. 输入并加密保存（推荐）")
        print("2. 使用环境变量（临时）")
        print("3. 每次手动输入")
        print("4. 查看配置说明")

        choice = input("\n请选择 (1-4): ").strip()

        if choice == '1':
            api_key = getpass.getpass("请输入Grok API密钥: ")
            if self.save_api_key(api_key):
                return api_key
        elif choice == '2':
            print("\n请在终端运行：")
            print("export GROK_API_KEY='your-api-key-here'")
            print("\n或添加到 ~/.bashrc 或 ~/.zshrc 文件中")
            return None
        elif choice == '3':
            return getpass.getpass("请输入Grok API密钥: ")
        elif choice == '4':
            self.show_security_tips()
            return self.setup_api()

        return None

    def show_security_tips(self):
        """显示安全提示"""
        print("\n🔐 API密钥安全最佳实践：")
        print("-" * 40)
        print("1. 永远不要将API密钥硬编码在代码中")
        print("2. 不要将API密钥提交到Git仓库")
        print("3. 使用环境变量或加密配置文件")
        print("4. 定期轮换API密钥")
        print("5. 限制API密钥的权限范围")
        print("\n推荐方案：")
        print("• 开发环境：使用加密配置文件")
        print("• 生产环境：使用环境变量或密钥管理服务")
        print("-" * 40)