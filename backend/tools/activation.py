"""
激活码生成模块
"""

from typing import List

from django.db import transaction
from users.models import User, ActivationCode


# 维护意图：生成激活码
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def generate_activation_codes(code_type: str = 'teacher', count: int = 1,
                               created_by_username: str = 'admin') -> List[str]:
    """生成激活码"""
    if code_type not in ('teacher', 'admin'):
        raise ValueError(f'无效的激活码类型: {code_type}，必须为 teacher 或 admin')

    creator = User.objects.filter(username=created_by_username).first()
    if not creator:
        raise ValueError(f'用户不存在: {created_by_username}')

    codes: List[str] = []
    with transaction.atomic():
        for _ in range(count):
            # 重试机制防止激活码碰撞
            for _attempt in range(3):
                code_str = ActivationCode.generate_code()
                if not ActivationCode.objects.filter(code=code_str).exists():
                    break
            code = ActivationCode.objects.create(
                code=code_str,
                code_type=code_type,
                created_by=creator,
            )
            codes.append(code.code)

    print('生成完成:')
    for c in codes:
        print(f'- {c}')
    return codes
