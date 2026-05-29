import time
from typing import Optional


class VerifyCodeStore:
    """简单的验证码存储器（内存中）"""

    def __init__(self):
        self._store: dict[str, dict] = {}

    def set(self, email: str, code: str, expire_seconds: int = 300):
        """存储验证码，默认为5分钟"""
        self._store[email] = {
            "code": code,
            "expire_at": time.time() + expire_seconds,
            "attempts": 0,
        }

    def get(self, email: str) -> Optional[str]:
        """获取验证码，如果过期或不存在返回None"""
        if email not in self._store:
            return None

        item = self._store[email]
        if time.time() > item["expire_at"]:
            del self._store[email]
            return None

        return item["code"]

    def verify(self, email: str, code: str) -> bool:
        """验证验证码"""
        if email not in self._store:
            return False

        item = self._store[email]
        if time.time() > item["expire_at"]:
            del self._store[email]
            return False

        item["attempts"] += 1
        if item["code"] == code:
            del self._store[email]
            return True

        return False

    def increment_attempts(self, email: str):
        """增加验证码错误尝试次数"""
        if email in self._store:
            self._store[email]["attempts"] += 1

    def delete(self, email: str):
        """删除验证码"""
        if email in self._store:
            del self._store[email]


verify_code_store = VerifyCodeStore()
