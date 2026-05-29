import json
import os
from typing import Optional

from app.settings import settings


def ensure_config_dir():
    """确保配置目录存在"""
    if not os.path.exists(settings.CONFIG_ROOT):
        os.makedirs(settings.CONFIG_ROOT)


def save_config(key: str, data: dict) -> bool:
    """保存配置到文件"""
    try:
        ensure_config_dir()
        file_path = os.path.join(settings.CONFIG_ROOT, f"{key}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False


def load_config(key: str) -> Optional[dict]:
    """从文件加载配置"""
    try:
        file_path = os.path.join(settings.CONFIG_ROOT, f"{key}.json")
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置失败: {e}")
        return None
