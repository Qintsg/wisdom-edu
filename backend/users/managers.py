"""用户模型管理器。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import UserManager as DjangoUserManager

if TYPE_CHECKING:
    from .models import User


def normalize_optional_unique_contact(value: object) -> str | None:
    """规整可选唯一联系方式，避免空字符串占用唯一索引。"""
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


class OptionalContactUserManager(DjangoUserManager):
    """让 create_user/create_superuser 遵守可选唯一字段的 NULL 语义。"""

    @classmethod
    def normalize_email(cls, email: object) -> str | None:
        """邮箱为空时保持 None，非空时沿用 Django 标准域名规范化。"""
        cleaned_email = normalize_optional_unique_contact(email)
        if cleaned_email is None:
            return None
        return super().normalize_email(cleaned_email) or None

    def _create_user_object(
        self,
        username: str,
        email: object,
        password: str | None,
        **extra_fields: object,
    ) -> User:
        """创建用户对象时同步规整手机号空值。"""
        extra_fields["phone"] = normalize_optional_unique_contact(extra_fields.get("phone"))
        return super()._create_user_object(username, email, password, **extra_fields)
