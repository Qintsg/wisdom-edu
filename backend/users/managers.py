"""用户模型管理器。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import UserManager as DjangoUserManager

if TYPE_CHECKING:
    from .models import User


# 维护意图：规整可选唯一联系方式，避免空字符串占用唯一索引
# 边界说明：该逻辑服务 User manager，接口层仍保留字段级业务校验。
# 风险说明：调整 email/phone 唯一约束时，需要同步管理端创建与导入逻辑。
def normalize_optional_unique_contact(value: object) -> str | None:
    """规整可选唯一联系方式，避免空字符串占用唯一索引。"""
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


# 维护意图：让 create_user/create_superuser 遵守可选唯一字段的 NULL 语义
# 边界说明：只覆盖 email/phone 空值规范化，不改变 Django 用户权限默认值。
# 风险说明：Django UserManager 签名变化时，需要同步该薄封装。
class OptionalContactUserManager(DjangoUserManager):
    """让 create_user/create_superuser 遵守可选唯一字段的 NULL 语义。"""

    # 维护意图：邮箱为空时保持 None，非空时沿用 Django 标准域名规范化
    # 边界说明：BaseUserManager 默认把 None 转成空字符串，这里只修正该行为。
    # 风险说明：外部依赖空字符串邮箱的代码需要改为兼容 None。
    @classmethod
    def normalize_email(cls, email: object) -> str | None:
        """邮箱为空时保持 None，非空时沿用 Django 标准域名规范化。"""
        cleaned_email = normalize_optional_unique_contact(email)
        if cleaned_email is None:
            return None
        return super().normalize_email(cleaned_email) or None

    # 维护意图：创建用户对象时同步规整手机号空值
    # 边界说明：保持保存行为仍由 Django UserManager 的 _create_user 负责。
    # 风险说明：新增可选唯一联系方式时，应在这里统一规整。
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
