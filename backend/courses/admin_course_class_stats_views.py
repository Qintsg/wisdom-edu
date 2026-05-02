"""课程模块 - 管理端课程与班级详情统计接口。"""

from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdmin
from common.responses import error_response, success_response
from .models import Class, ClassCourse, Course, Enrollment


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_course_statistics(_request, course_id):
    """管理端 - 课程统计。"""
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg='课程不存在', code=404)

    class_count = ClassCourse.objects.filter(course=course).count()
    class_ids = ClassCourse.objects.filter(course=course).values_list('class_obj_id', flat=True)
    student_count = Enrollment.objects.filter(
        class_obj__in=Class.objects.filter(id__in=class_ids)
    ).values('user_id').distinct().count()

    return success_response(data={
        'class_count': class_count,
        'student_count': student_count,
        'avg_score': 85.5,  # 模拟数据，后续需对接 ScoreService。
        'completion_rate': '78%'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_class_statistics(_request, class_id):
    """获取班级统计数据。"""
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg='班级不存在', code=404)

    student_count = Enrollment.objects.filter(class_obj=class_obj).count()
    course_count = ClassCourse.objects.filter(class_obj=class_obj).count()

    return success_response(data={
        'class_id': class_obj.id,
        'class_name': class_obj.name,
        'student_count': student_count,
        'course_count': course_count,
    })
