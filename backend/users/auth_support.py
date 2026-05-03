"""认证接口的注册、登录与用户信息支撑逻辑。"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Protocol, cast

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import QuerySet

from courses.models import Class, Course, Enrollment
from .models import ActivationCode, User
from .serializers import UserRegisterSerializer


PHONE_PATTERN = re.compile(r"^1[3-9]\d{9}$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
USERNAME_PATTERN = re.compile(r"^[\w\u4e00-\u9fff]+$")
USERINFO_ALLOWED_FIELDS = ["username", "email", "phone", "real_name", "student_id"]


# 维护意图：认证后请求只需要 user 属性用于类型收窄
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class AuthenticatedRequest(Protocol):
    """认证后请求只需要 user 属性用于类型收窄。"""

    user: object


# 维护意图：收窄认证后 request.user 的类型
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def get_authenticated_user(request: AuthenticatedRequest) -> User:
    """收窄认证后 request.user 的类型。"""
    return cast(User, request.user)


# 维护意图：安全获取头像访问地址
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def get_avatar_url(user: User) -> str | None:
    """安全获取头像访问地址。"""
    avatar = user.avatar
    if not getattr(avatar, "name", ""):
        return None
    try:
        return str(avatar.url)
    except ValueError:
        return None


# 维护意图：执行注册校验、激活码消费与登录令牌生成
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def register_user(data: Mapping[str, object]) -> tuple[dict[str, object] | None, str | None, int]:
    """执行注册校验、激活码消费与登录令牌生成。"""
    serializer = UserRegisterSerializer(data=data)
    if not serializer.is_valid():
        return None, "注册失败: " + str(serializer.errors), 400

    duplicate_error = registration_duplicate_error(serializer.validated_data, data)
    if duplicate_error:
        return None, duplicate_error, 400

    role = serializer.validated_data.get("role", "student")
    if role in ["teacher", "admin"]:
        return register_privileged_user(serializer, data, role)

    user = serializer.save()
    return build_auth_payload(user), None, 201


# 维护意图：检查注册时的用户名、邮箱和手机号唯一性
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def registration_duplicate_error(validated_data: Mapping[str, object], data: Mapping[str, object]) -> str | None:
    """检查注册时的用户名、邮箱和手机号唯一性。"""
    if User.objects.filter(username=validated_data["username"]).exists():
        return "用户名已存在"
    email = validated_data.get("email")
    if email and User.objects.filter(email=email).exists():
        return "该邮箱已被注册"
    phone = data.get("phone")
    if phone and User.objects.filter(phone=phone).exists():
        return "该手机号已被注册"
    return None


# 维护意图：注册教师或管理员，并在同一事务内消费激活码
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def register_privileged_user(
    serializer: UserRegisterSerializer,
    data: Mapping[str, object],
    role: object,
) -> tuple[dict[str, object] | None, str | None, int]:
    """注册教师或管理员，并在同一事务内消费激活码。"""
    code_obj, activation_error = validate_activation_code(data.get("activation_code"), role)
    if activation_error or code_obj is None:
        return None, activation_error, 400

    with transaction.atomic():
        user = serializer.save()
        code_obj.use(user)
    return build_auth_payload(user), None, 201


# 维护意图：校验教师或管理员注册所需激活码
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def validate_activation_code(activation_code: object, role: object) -> tuple[ActivationCode | None, str | None]:
    """校验教师或管理员注册所需激活码。"""
    if not activation_code:
        return None, "教师或管理员注册需要提供激活码"
    try:
        code_obj = ActivationCode.objects.get(code=activation_code)
    except ActivationCode.DoesNotExist:
        return None, "激活码不存在"

    if not code_obj.is_valid():
        return None, "激活码无效或已过期"
    if code_obj.code_type != role:
        return None, f"此激活码不能用于{role}注册"
    return code_obj, None


# 维护意图：校验账号密码并生成登录令牌
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def authenticate_user_login(
    request: object,
    data: Mapping[str, object],
) -> tuple[dict[str, object] | None, str | None, int]:
    """校验账号密码并生成登录令牌。"""
    account = data.get("username") or data.get("account")
    password = data.get("password")
    if not account or not password:
        return None, "账号和密码不能为空", 400

    user = authenticate(request, username=account, password=password)
    if user is None:
        return None, "账号或密码错误", 401

    user = cast(User, user)
    if not user.is_active:
        return None, "账户已禁用", 401
    return build_auth_payload(user), None, 200


# 维护意图：构造登录和注册共用的令牌响应
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_auth_payload(user: User) -> dict[str, object]:
    """构造登录和注册共用的令牌响应。"""
    refresh = RefreshToken.for_user(user)
    return {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "token": str(refresh.access_token),
        "refresh": str(refresh),
    }


# 维护意图：组装当前用户资料、班级和课程上下文
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_userinfo_payload(user: User) -> dict[str, object]:
    """组装当前用户资料、班级和课程上下文。"""
    classes, courses = build_user_learning_context(user)
    return {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "email": user.email,
        "phone": user.phone,
        "real_name": user.real_name,
        "student_id": user.student_id,
        "avatar": get_avatar_url(user),
        "classes": classes,
        "courses": courses,
    }


# 维护意图：读取学生加入班级与教师授课班级，并去重课程列表
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_user_learning_context(user: User) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """读取学生加入班级与教师授课班级，并去重课程列表。"""
    classes: list[dict[str, object]] = []
    courses: list[dict[str, object]] = []
    course_ids_seen: set[int] = set()

    for enrollment in user_enrollments(user):
        class_payload, course_id, course_name = build_enrollment_class_payload(enrollment)
        classes.append(class_payload)
        append_unique_course(courses, course_ids_seen, course_id, course_name)

    if user.role == "teacher":
        for teaching_class in teaching_classes(user):
            class_payload, course_id, course_name = build_teaching_class_payload(teaching_class)
            classes.append(class_payload)
            append_unique_course(courses, course_ids_seen, course_id, course_name)
    return classes, courses


# 维护意图：读取用户加入班级关系，并预取班级绑定课程
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def user_enrollments(user: User) -> QuerySet[Enrollment]:
    """读取用户加入班级关系，并预取班级绑定课程。"""
    return (
        Enrollment.objects.filter(user=user)
        .select_related("class_obj", "class_obj__teacher", "class_obj__course")
        .prefetch_related("class_obj__class_courses__course")
    )


# 维护意图：序列化学生加入班级项，同时返回课程去重所需信息
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_enrollment_class_payload(enrollment: Enrollment) -> tuple[dict[str, object], int | None, str | None]:
    """序列化学生加入班级项，同时返回课程去重所需信息。"""
    class_obj = enrollment.class_obj
    course = resolve_class_course(class_obj)
    course_id = course.id if course else None
    course_name = course.name if course else None
    teacher_name = class_obj.teacher.username if class_obj.teacher else None
    teacher_real_name = class_obj.teacher.real_name if class_obj.teacher else None
    return {
        "class_id": class_obj.id,
        "class_name": class_obj.name,
        "course_id": course_id,
        "course_name": course_name,
        "teacher_name": teacher_real_name or teacher_name,
        "teacher_username": teacher_name,
        "student_count": class_obj.get_student_count(),
        "role": enrollment.role,
        "enrolled_at": enrollment.enrolled_at.isoformat(),
    }, course_id, course_name


# 维护意图：班级默认课程为空时，从有效的班级课程绑定中选择第一个兜底课程
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_class_course(class_obj: Class) -> Course | None:
    """班级默认课程为空时，从有效的班级课程绑定中选择第一个兜底课程。"""
    course = class_obj.course
    if course:
        return course
    linked_courses = [class_course.course for class_course in class_obj.class_courses.all() if class_course.is_active]
    return linked_courses[0] if linked_courses else None


# 维护意图：读取教师直接负责的班级
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def teaching_classes(user: User) -> QuerySet[Class]:
    """读取教师直接负责的班级。"""
    return Class.objects.filter(teacher=user).select_related("course")


# 维护意图：序列化教师授课班级项，同时返回课程去重所需信息
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_teaching_class_payload(class_obj: Class) -> tuple[dict[str, object], int | None, str | None]:
    """序列化教师授课班级项，同时返回课程去重所需信息。"""
    course = class_obj.course
    course_id = course.id if course else None
    course_name = course.name if course else None
    return {
        "class_id": class_obj.id,
        "class_name": class_obj.name,
        "course_id": course_id,
        "course_name": course_name,
        "role": "teacher",
        "enrolled_at": class_obj.created_at.isoformat(),
    }, course_id, course_name


# 维护意图：按课程 ID 去重追加当前用户可见课程
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def append_unique_course(
    courses: list[dict[str, object]],
    course_ids_seen: set[int],
    course_id: int | None,
    course_name: str | None,
) -> None:
    """按课程 ID 去重追加当前用户可见课程。"""
    if course_id and course_id not in course_ids_seen:
        course_ids_seen.add(course_id)
        courses.append({"course_id": course_id, "course_name": course_name})


# 维护意图：校验并更新当前用户资料
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def update_userinfo_payload(
    user: User,
    data: Mapping[str, object],
    files: Mapping[str, object],
) -> tuple[dict[str, object] | None, str | None]:
    """校验并更新当前用户资料。"""
    updated_fields: list[str] = []
    for field in USERINFO_ALLOWED_FIELDS:
        if field not in data:
            continue
        value = normalize_userinfo_value(field, data[field])
        validation_error = validate_userinfo_field(user, field, value)
        if validation_error:
            return None, validation_error
        setattr(user, field, value)
        updated_fields.append(field)

    avatar_file = files.get("avatar")
    if avatar_file:
        user.avatar = avatar_file
        updated_fields.append("avatar")

    if not updated_fields:
        return None, "没有可更新的字段"
    user.save()
    return {"updated_fields": updated_fields, "avatar": get_avatar_url(user)}, None


# 维护意图：将空字符串邮箱和手机号转成 NULL，兼容唯一索引
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def normalize_userinfo_value(field: str, value: object) -> object | None:
    """将空字符串邮箱和手机号转成 NULL，兼容唯一索引。"""
    if field in ("phone", "email") and value == "":
        return None
    return value


# 维护意图：按字段执行当前用户资料更新校验
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def validate_userinfo_field(user: User, field: str, value: object | None) -> str | None:
    """按字段执行当前用户资料更新校验。"""
    if field == "phone" and value:
        return validate_phone_value(user, value)
    if field == "email" and value:
        return validate_email_value(user, value)
    if field == "username" and value:
        return validate_username_value(user, value)
    return None


# 维护意图：校验中国手机号格式和唯一性
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def validate_phone_value(user: User, value: object) -> str | None:
    """校验中国手机号格式和唯一性。"""
    if not PHONE_PATTERN.match(str(value)):
        return "手机号格式不正确，请输入11位中国手机号"
    if User.objects.filter(phone=value).exclude(id=user.id).exists():
        return "该手机号已被其他用户使用"
    return None


# 维护意图：校验邮箱格式和唯一性
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def validate_email_value(user: User, value: object) -> str | None:
    """校验邮箱格式和唯一性。"""
    if not EMAIL_PATTERN.match(str(value)):
        return "邮箱格式不正确"
    if User.objects.filter(email=value).exclude(id=user.id).exists():
        return "该邮箱已被其他用户使用"
    return None


# 维护意图：校验用户名长度、字符集和唯一性
# 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def validate_username_value(user: User, value: object) -> str | None:
    """校验用户名长度、字符集和唯一性。"""
    username = str(value)
    if len(username) < 3:
        return "用户名至少3个字符"
    if len(username) > 30:
        return "用户名最多30个字符"
    if not USERNAME_PATTERN.match(username):
        return "用户名只能包含字母、数字、下划线或中文"
    if User.objects.filter(username=value).exclude(id=user.id).exists():
        return "该用户名已被使用"
    return None


# 维护意图：根据 refresh token 生成新的 access token
# 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
# 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
def refresh_access_token(refresh_token: object) -> tuple[dict[str, str] | None, str | None, int]:
    """根据 refresh token 生成新的 access token。"""
    if not refresh_token:
        return None, "刷新令牌不能为空", 400
    try:
        refresh = RefreshToken(refresh_token)
        return {"token": str(refresh.access_token), "refresh": str(refresh)}, None, 200
    except TokenError:
        return None, "刷新令牌无效或已过期", 401


# 维护意图：校验旧密码并保存新密码，返回错误消息或 None
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def change_user_password(user: User, data: Mapping[str, object]) -> str | None:
    """校验旧密码并保存新密码，返回错误消息或 None。"""
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    if not old_password or not new_password:
        return "旧密码和新密码不能为空"
    if not user.check_password(old_password):
        return "旧密码错误"
    if len(new_password) < 8:
        return "新密码长度不能少于8位"

    user.set_password(new_password)
    user.save()
    return None


# 维护意图：退出登录时尽力拉黑 refresh token，非法 token 不影响幂等退出
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def blacklist_refresh_token(refresh_token: object) -> None:
    """退出登录时尽力拉黑 refresh token，非法 token 不影响幂等退出。"""
    if not refresh_token:
        return
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return
