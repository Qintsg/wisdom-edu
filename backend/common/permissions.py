"""
自定义权限类

提供基于角色的访问控制权限
"""
from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """仅学生可访问"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'


class IsTeacher(permissions.BasePermission):
    """仅教师可访问"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsAdmin(permissions.BasePermission):
    """仅管理员可访问（包括超级用户）"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser)


class IsTeacherOrAdmin(permissions.BasePermission):
    """教师或管理员可访问"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['teacher', 'admin']


class IsOwnerOrTeacher(permissions.BasePermission):
    """仅本人或教师可访问"""

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['teacher', 'admin']:
            return True

        # 检查对象是否有 user 字段
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'user_id'):
            return obj.user_id == request.user.id

        return False


class IsEnrolledInCourse(permissions.BasePermission):
    """检查用户是否已选修该课程"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        course_id = request.query_params.get('course_id') or request.data.get('course_id')
        if not course_id:
            return True  # 如果没有 course_id，让视图处理

        # 教师和管理员可以访问其教授的课程
        if request.user.role in ['teacher', 'admin']:
            from courses.models import Class

            return Class.objects.filter(
                course_id=course_id,
                teacher=request.user
            ).exists()

        # 学生需要检查选课记录
        from courses.models import Enrollment

        return Enrollment.objects.filter(
            user=request.user,
            class_obj__course_id=course_id
        ).exists()


__all__ = [
    'IsStudent',
    'IsTeacher',
    'IsAdmin',
    'IsTeacherOrAdmin',
    'IsOwnerOrTeacher',
    'IsEnrolledInCourse',
]
