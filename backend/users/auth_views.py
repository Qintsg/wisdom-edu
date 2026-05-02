"""
用户模块 - 认证与公共接口

包含：注册、登录、JWT令牌、密码管理、用户信息、健康检查
"""
from typing import cast
import re
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.db import transaction

from common.responses import success_response, created_response, error_response
from courses.models import Enrollment, Class, ClassCourse
from .models import User, ActivationCode
from .serializers import UserRegisterSerializer, CustomTokenObtainPairSerializer
from .auth_password_views import password_reset, password_reset_send


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义登录视图 已审查"""
    serializer_class = CustomTokenObtainPairSerializer


def _get_authenticated_user(request) -> User:
    """
    收窄认证后 request.user 的类型。
    :param request: DRF 请求对象。
    :return: 认证用户。
    """
    return cast(User, request.user)


def _get_avatar_url(user: User) -> str | None:
    """
    安全获取头像访问地址。
    :param user: 用户对象。
    :return: 头像 URL；不存在时返回 None。
    """
    avatar = user.avatar
    if not getattr(avatar, 'name', ''):
        return None
    try:
        return str(avatar.url)
    except ValueError:
        return None


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def register(request):
    """
    用户注册
    POST /api/auth/register
    
    请求参数：
    - username: 用户名（必填）
    - password: 密码（必填）
    - email: 邮箱（选填）
    - role: 角色，student/teacher/admin（默认student）
    - activation_code: 激活码（教师/管理员注册必填）
    - real_name: 真实姓名（选填）
    - student_id: 学号/工号（选填）
    """
    serializer = UserRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(
            msg='注册失败: ' + str(serializer.errors)
        )

    if User.objects.filter(username=serializer.validated_data['username']).exists():
        return error_response(msg='用户名已存在')

    email = serializer.validated_data.get('email')
    if email and User.objects.filter(email=email).exists():
        return error_response(msg='该邮箱已被注册')

    phone = request.data.get('phone')
    if phone and User.objects.filter(phone=phone).exists():
        return error_response(msg='该手机号已被注册')

    role = serializer.validated_data.get('role', 'student')

    if role in ['teacher', 'admin']:
        activation_code = request.data.get('activation_code')
        if not activation_code:
            return error_response(
                msg='教师或管理员注册需要提供激活码'
            )
        
        try:
            code_obj = ActivationCode.objects.get(code=activation_code)
        except ActivationCode.DoesNotExist:
            return error_response(msg='激活码不存在')

        if not code_obj.is_valid():
            return error_response(msg='激活码无效或已过期')

        if code_obj.code_type != role:
            return error_response(
                msg=f'此激活码不能用于{role}注册'
            )

        with transaction.atomic():
            user = serializer.save()
            code_obj.use(user)
    else:
        user = serializer.save()

    refresh = RefreshToken.for_user(user)

    return created_response(
        data={
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'token': str(refresh.access_token),
            'refresh': str(refresh)
        },
        msg='注册成功'
    )


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    """
    用户登录
    POST /api/auth/login
    
    支持使用用户名、邮箱或手机号登录
    """
    account = request.data.get('username') or request.data.get('account')
    password = request.data.get('password')

    if not account or not password:
        return error_response(msg='账号和密码不能为空')

    user = authenticate(request, username=account, password=password)

    if user is None:
        return error_response(msg='账号或密码错误', code=401)

    user = cast(User, user)

    if not user.is_active:
        return error_response(msg='账户已禁用', code=401)

    refresh = RefreshToken.for_user(user)

    return success_response(
        data={
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'token': str(refresh.access_token),
            'refresh': str(refresh)
        },
        msg='登录成功'
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def userinfo(request):
    """
    获取当前用户信息
    GET /api/auth/userinfo
    """
    user = _get_authenticated_user(request)

    # 同时查询 class_obj__teacher 和 class_obj__course 以优化查询
    # 注意：class.course 是默认课程外键，如果为空则尝试从 class_courses 获取
    enrollments = Enrollment.objects.filter(user=user).select_related(
        'class_obj', 
        'class_obj__teacher',
        'class_obj__course'
    ).prefetch_related('class_obj__class_courses__course')
    
    classes = []
    courses = []
    course_ids_seen = set()
    
    for e in enrollments:
        class_obj = e.class_obj

        # 默认课程为空时，从班级绑定课程中兜底选择第一个可用项。
        course = class_obj.course
        if not course:
            # 使用 prefetch_related 后，访问 class_courses 不会产生额外查询
            # 但注意：courses_list 属性内部是 filter(is_active=True)，这会触发新查询除非 prefetch 带 filter
            # 这里简化逻辑：直接遍历 prefetch 的结果
            linked_courses = [cc.course for cc in class_obj.class_courses.all() if cc.is_active]
            if linked_courses:
                course = linked_courses[0]

        course_id = course.id if course else None
        course_name = course.name if course else None

        teacher_name = class_obj.teacher.username if class_obj.teacher else None
        teacher_real_name = class_obj.teacher.real_name if class_obj.teacher else None

        classes.append({
            'class_id': class_obj.id,
            'class_name': class_obj.name,
            'course_id': course_id,
            'course_name': course_name,
            'teacher_name': teacher_real_name or teacher_name,
            'teacher_username': teacher_name,
            'student_count': class_obj.get_student_count(),
            'role': e.role,
            'enrolled_at': e.enrolled_at.isoformat()
        })
        if course_id and course_id not in course_ids_seen:
            course_ids_seen.add(course_id)
            courses.append({
                'course_id': course_id,
                'course_name': course_name
            })

    if user.role == 'teacher':
        teaching_classes = Class.objects.filter(teacher=user).select_related('course')
        for tc in teaching_classes:
            course = tc.course
            course_id = course.id if course else None
            course_name = course.name if course else None

            classes.append({
                'class_id': tc.id,
                'class_name': tc.name,
                'course_id': course_id,
                'course_name': course_name,
                'role': 'teacher',
                'enrolled_at': tc.created_at.isoformat()
            })
            if course_id and course_id not in course_ids_seen:
                course_ids_seen.add(course_id)
                courses.append({
                    'course_id': course_id,
                    'course_name': course_name
                })

    return success_response(
        data={
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'email': user.email,
            'phone': user.phone,
            'real_name': user.real_name,
            'student_id': user.student_id,
            'avatar': _get_avatar_url(user),
            'classes': classes,
            'courses': courses
        }
    )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_userinfo(request):
    """
    更新当前用户信息
    PUT /api/auth/userinfo/update
    
    可更新字段：email, phone, real_name, student_id, avatar
    email需要符合邮箱格式，phone需要符合中国手机号格式
    """
    user = _get_authenticated_user(request)
    
    allowed_fields = ['username', 'email', 'phone', 'real_name', 'student_id']
    updated_fields = []

    phone_pattern = re.compile(r'^1[3-9]\d{9}$')
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    for field in allowed_fields:
        if field in request.data:
            value = request.data[field]

            if field in ('phone', 'email') and value == '':
                value = None

            if field == 'phone' and value:
                if not phone_pattern.match(str(value)):
                    return error_response(msg='手机号格式不正确，请输入11位中国手机号')
                if User.objects.filter(phone=value).exclude(id=user.id).exists():
                    return error_response(msg='该手机号已被其他用户使用')

            if field == 'email' and value:
                if not email_pattern.match(str(value)):
                    return error_response(msg='邮箱格式不正确')
                if User.objects.filter(email=value).exclude(id=user.id).exists():
                    return error_response(msg='该邮箱已被其他用户使用')

            if field == 'username' and value:
                if len(value) < 3:
                    return error_response(msg='用户名至少3个字符')
                if len(value) > 30:
                    return error_response(msg='用户名最多30个字符')
                username_pattern = re.compile(r'^[\w\u4e00-\u9fff]+$')
                if not username_pattern.match(str(value)):
                    return error_response(msg='用户名只能包含字母、数字、下划线或中文')
                if User.objects.filter(username=value).exclude(id=user.id).exists():
                    return error_response(msg='该用户名已被使用')

            setattr(user, field, value)
            updated_fields.append(field)

    # 头像支持（multipart/form-data）
    avatar_file = request.FILES.get('avatar') if hasattr(request, 'FILES') else None
    if avatar_file:
        user.avatar = avatar_file
        updated_fields.append('avatar')
    
    if updated_fields:
        user.save()
        return success_response(
            data={
                'updated_fields': updated_fields,
                'avatar': _get_avatar_url(user)
            },
            msg='用户信息已更新'
        )
    
    return error_response(msg='没有可更新的字段')


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def token_refresh(request):
    """
    刷新JWT令牌
    POST /api/auth/token/refresh
    """
    refresh_token = request.data.get('refresh')

    if not refresh_token:
        return error_response(msg='刷新令牌不能为空')

    try:
        refresh = RefreshToken(refresh_token)
        new_access = str(refresh.access_token)

        # 如果配置了轮换刷新令牌
        new_refresh = str(refresh)

        return success_response(
            data={
                'token': new_access,
                'refresh': new_refresh
            },
            msg='令牌已刷新'
        )
    except TokenError:
        return error_response(msg='刷新令牌无效或已过期', code=401)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    修改密码
    POST /api/auth/password/change
    
    请求参数：
    - old_password: 旧密码（必填）
    - new_password: 新密码（必填，8位以上）
    """
    user = _get_authenticated_user(request)
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    
    if not old_password or not new_password:
        return error_response(msg='旧密码和新密码不能为空')
    
    if not user.check_password(old_password):
        return error_response(msg='旧密码错误')

    if len(new_password) < 8:
        return error_response(msg='新密码长度不能少于8位')

    user.set_password(new_password)
    user.save()
    
    return success_response(msg='密码修改成功')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    退出登录
    POST /api/auth/logout
    
    将refresh token加入黑名单，使其无法再用于刷新access token。
    客户端还需清除本地存储的Token。
    """
    refresh_token = request.data.get('refresh')
    if refresh_token:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass  # token无效也不影响退出
    return success_response(msg='退出成功')


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def health(_request):
    """
    健康检查端点
    GET /health/
    """
    return success_response(data={'status': 'healthy'})
