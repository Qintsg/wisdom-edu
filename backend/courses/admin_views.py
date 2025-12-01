"""
课程模块 - 管理员接口

包含：课程/班级管理、教师分配、统计报表
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.db import models
from common.responses import success_response, error_response, created_response
from common.permissions import IsAdmin
from users.models import User
from .models import Course, Class, ClassCourse, Enrollment


def _parse_pagination_params(query_params):
    """
    统一解析分页参数。
    课程列表与班级列表共享同一套分页边界，避免重复维护默认值与兜底逻辑。
    """
    try:
        page = max(1, int(query_params.get('page', 1)))
        page_size = min(max(1, int(query_params.get('page_size', 20))), 100)
    except (ValueError, TypeError):
        return 1, 20

    return page, page_size


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_course_list(request):
    """
    管理端 - 获取所有课程列表
    GET /api/admin/courses
    """
    keyword = request.query_params.get('keyword', '')
    page, page_size = _parse_pagination_params(request.query_params)

    courses = Course.objects.all().order_by('-created_at')
    if keyword:
        courses = courses.filter(name__icontains=keyword)

    total = courses.count()
    start = (page - 1) * page_size
    courses = courses.select_related('created_by')[start:start + page_size]

    data = []
    for course in courses:
        student_count = Enrollment.objects.filter(
            class_obj__in=Class.objects.filter(
                id__in=ClassCourse.objects.filter(course=course).values_list('class_obj_id', flat=True)
            )
        ).values('user_id').distinct().count()

        data.append({
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'teacher_id': course.created_by_id,
            'teacher_name': course.created_by.username if course.created_by else None,
            'student_count': student_count,
            'status': 'published' if course.is_public else 'draft',
            'is_public': course.is_public,
            'created_at': course.created_at.isoformat(),
        })

    return success_response(data={
        'total': total,
        'courses': data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_class_list(request):
    """
    管理端 - 获取所有班级列表
    GET /api/admin/classes
    """
    keyword = request.query_params.get('keyword', '')
    course_id = request.query_params.get('course_id')
    page, page_size = _parse_pagination_params(request.query_params)

    classes = Class.objects.all().order_by('-created_at')
    if keyword:
        classes = classes.filter(name__icontains=keyword)
    if course_id:
        classes = classes.filter(class_courses__course_id=course_id, class_courses__is_active=True).distinct()

    total = classes.count()

    # 优化查询：
    # 1. 预统计学生人数（仅统计role='student'）
    # 2. 预加载关联的课程信息
    # 3. 预加载教师信息
    classes = classes.annotate(
        student_count=Count('enrollments', filter=Q(enrollments__role='student'), distinct=True)
    ).select_related('teacher').prefetch_related(
        'class_courses__course'
    )

    start = (page - 1) * page_size
    classes = classes[start:start + page_size]

    data = []
    for cls in classes:
        active_courses = [
            cc.course.name 
            for cc in cls.class_courses.all() 
            if cc.is_active
        ]

        teacher_name = None
        if cls.teacher:
            teacher_name = cls.teacher.real_name or cls.teacher.username

        data.append({
            'id': cls.id,
            'name': cls.name,
            'course': ', '.join(active_courses) if active_courses else '未关联课程',
            'teacher_name': teacher_name,
            'student_count': getattr(cls, 'student_count', 0),
            'is_active': cls.is_active,
            'created_at': cls.created_at.isoformat(),
        })

    return success_response(data={
        'total': total,
        'classes': data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_class_create(request):
    """
    管理端 - 创建班级
    POST /api/admin/classes/create
    """
    name = request.data.get('name')
    teacher_id = request.data.get('teacher_id')
    course_id = request.data.get('course_id')

    if not name:
        return error_response(msg='班级名称不能为空')

    teacher = None
    if teacher_id:
        try:
            teacher_id = int(teacher_id)
            teacher = User.objects.get(id=teacher_id)
        except (ValueError, TypeError):
            teacher = None
        except User.DoesNotExist:
            pass

    cls = Class.objects.create(
        name=name,
        teacher=teacher,
        is_active=True
    )

    if course_id:
        try:
            course_id_int = int(course_id)
            course = Course.objects.get(id=course_id_int)
            ClassCourse.objects.create(class_obj=cls, course=course, is_active=True)
            cls.course = course  # 向后兼容，设置默认课程
            cls.save()
        except (ValueError, TypeError):
            pass
        except Course.DoesNotExist:
            pass

    return created_response(data={'id': cls.id, 'name': cls.name}, msg='班级创建成功')


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_class_detail(request, class_id):
    """
    管理端 - 获取/更新/删除班级
    """
    try:
        cls = Class.objects.select_related('teacher').get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg='班级不存在', code=404)

    if request.method == 'GET':
        course_ids = list(ClassCourse.objects.filter(class_obj=cls, is_active=True).values_list('course_id', flat=True))
        return success_response(data={
            'id': cls.id,
            'name': cls.name,
            'description': cls.description,
            'teacher_id': cls.teacher.id if cls.teacher else None,
            'teacher_name': cls.teacher.username if cls.teacher else None,
            'course_ids': course_ids,
            'is_active': cls.is_active,
            'student_count': Enrollment.objects.filter(class_obj=cls).count(),
            'created_at': cls.created_at.isoformat()
        })

    elif request.method == 'DELETE':
        cls.delete()
        return success_response(msg='班级已删除')

    name = request.data.get('name')
    teacher_id = request.data.get('teacher_id')
    course_ids = request.data.get('course_ids')

    if name:
        cls.name = name
    if teacher_id:
        try:
            teacher = User.objects.get(id=teacher_id)
            cls.teacher = teacher
        except User.DoesNotExist:
            pass

    if course_ids is not None:
        # 兼容字符串输入，逗号分隔。
        if isinstance(course_ids, str):
            course_ids = [cid.strip() for cid in course_ids.split(',') if cid.strip()]

        ClassCourse.objects.filter(class_obj=cls).delete()
        for cid in course_ids:
            try:
                cid_int = int(cid)
            except (TypeError, ValueError):
                continue

            try:
                c = Course.objects.get(id=cid_int)
                ClassCourse.objects.create(class_obj=cls, course=c, is_active=True)
            except Course.DoesNotExist:
                continue

    cls.save()
    return success_response(msg='班级更新成功')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_class_students(request, class_id):
    """
    管理端 - 获取班级学生列表
    GET /api/admin/classes/{class_id}/students
    """
    try:
        cls = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg='班级不存在', code=404)

    enrollments = Enrollment.objects.filter(class_obj=cls).select_related('user')
    students = []
    for e in enrollments:
        students.append({
            'id': e.user.id,
            'username': e.user.username,
            'real_name': e.user.real_name,
            'joined_at': e.enrolled_at.isoformat()
        })

    return success_response(data={'students': students, 'total': len(students)})


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_class_add_students(request, class_id):
    """
    管理端 - 批量添加学生到班级
    POST /api/admin/classes/{class_id}/students/add
    """
    try:
        cls = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg='班级不存在', code=404)

    student_ids = request.data.get('student_ids', [])
    if not student_ids:
        return error_response(msg='学生ID列表不能为空')

    added_count = 0
    for uid in student_ids:
        try:
            student = User.objects.get(id=uid)
            if not Enrollment.objects.filter(user=student, class_obj=cls).exists():
                Enrollment.objects.create(user=student, class_obj=cls)
                added_count += 1
        except User.DoesNotExist:
            continue

    return success_response(msg=f'成功添加 {added_count} 名学生')


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_class_remove_student(_request, class_id, student_id):
    """
    管理端 - 从班级移除学生
    DELETE /api/admin/classes/{class_id}/students/{student_id}
    """
    try:
        enrollment = Enrollment.objects.get(class_obj_id=class_id, user_id=student_id)
        enrollment.delete()
        return success_response(msg='学生已移出班级')
    except Enrollment.DoesNotExist:
        return error_response(msg='该学生不在班级中', code=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_overview(_request):
    """
    管理端 - 获取系统统计概览
    GET /api/admin/statistics/overview
    """
    user_count = User.objects.filter(is_active=True).count()
    course_count = Course.objects.count()
    class_count = Class.objects.count()
    student_count = User.objects.filter(role='student', is_active=True).count()
    teacher_count = User.objects.filter(role='teacher', is_active=True).count()
    admin_count = User.objects.filter(role='admin', is_active=True).count()

    return success_response(data={
        'userCount': user_count,
        'courseCount': course_count,
        'classCount': class_count,
        'studentCount': student_count,
        'teacherCount': teacher_count,
        'onlineRate': '99.9%',
        'roleDistribution': {
            'student': student_count,
            'teacher': teacher_count,
            'admin': admin_count,
        },
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_course_create(request):
    """
    管理端 - 创建课程
    POST /api/admin/courses/create
    """
    name = request.data.get('name') or request.data.get('course_name')
    description = request.data.get('description') or request.data.get('course_description', '')
    teacher_id = request.data.get('teacher_id')

    if not name:
        return error_response(msg='课程名称不能为空')

    teacher = None
    if teacher_id:
        try:
            teacher_id = int(teacher_id)
            teacher = User.objects.get(id=teacher_id, role__in=['teacher', 'admin'])
        except User.DoesNotExist:
            return error_response(msg='指定教师不存在', code=404)
        except (ValueError, TypeError):
            return error_response(msg='教师ID格式错误')

    course = Course.objects.create(
        name=name,
        description=description,
        created_by=teacher if teacher else request.user
    )

    return created_response(data={
        'course_id': course.id,
        'name': course.name
    }, msg='课程创建成功')


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_course_detail(request, course_id):
    """
    管理端 - 获取/更新/删除课程详情
    GET /api/admin/courses/{course_id}
    PUT /api/admin/courses/{course_id}
    DELETE /api/admin/courses/{course_id}
    """
    try:
        course = Course.objects.select_related('created_by').get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg='课程不存在', code=404)

    if request.method == 'GET':
        return success_response(data={
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'teacher_id': course.created_by.id if course.created_by else None,
            'teacher_name': course.created_by.username if course.created_by else None,
            'is_public': course.is_public,
            'created_at': course.created_at.isoformat(),
            'updated_at': course.updated_at.isoformat(),
            'student_count': Enrollment.objects.filter(
                class_obj__in=Class.objects.filter(
                    id__in=ClassCourse.objects.filter(course=course).values_list('class_obj_id', flat=True)
                )
            ).values('user_id').distinct().count()
        })

    elif request.method == 'DELETE':
        course.delete()
        return success_response(msg='课程已删除')

    name = request.data.get('name') or request.data.get('course_name')
    description = request.data.get('description') or request.data.get('course_description')
    teacher_id = request.data.get('teacher_id')

    if name:
        course.name = name
    if description is not None:
        course.description = description

    if teacher_id:
        try:
            teacher_id = int(teacher_id)
            teacher = User.objects.get(id=teacher_id)
            course.created_by = teacher
        except (ValueError, TypeError):
            pass  # 保持原值，避免因格式导致500
        except User.DoesNotExist:
            pass  # 忽略无效的教师ID

    course.save()
    return success_response(msg='课程更新成功')


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_course_assign_teacher(request, course_id):
    """
    管理端 - 分配课程教师
    POST /api/admin/courses/{course_id}/assign-teacher
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg='课程不存在', code=404)

    teacher_id = request.data.get('teacher_id')
    if not teacher_id:
        return error_response(msg='必须指定教师ID')

    try:
        teacher_id = int(teacher_id)
    except (ValueError, TypeError):
        return error_response(msg='教师ID格式错误')

    try:
        teacher = User.objects.get(id=teacher_id)
        teacher_role = getattr(teacher, 'role', '')
        teacher_is_superuser = bool(getattr(teacher, 'is_superuser', False))
        if teacher_role not in ['teacher', 'admin'] and not teacher_is_superuser:
            return error_response(msg='该用户不是教师')
    except User.DoesNotExist:
        return error_response(msg='教师用户不存在', code=404)

    course.created_by = teacher
    course.save()

    return success_response(msg='教师分配成功')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_course_statistics(_request, course_id):
    """
    管理端 - 课程统计
    GET /api/admin/courses/{course_id}/statistics
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg='课程不存在', code=404)

    class_count = ClassCourse.objects.filter(course=course).count()

    student_count = Enrollment.objects.filter(
        class_obj__in=Class.objects.filter(
            id__in=ClassCourse.objects.filter(course=course).values_list('class_obj_id', flat=True)
        )
    ).values('user_id').distinct().count()

    return success_response(data={
        'class_count': class_count,
        'student_count': student_count,
        'avg_score': 85.5,  # 模拟数据，后续需对接 ScoreService。
        'completion_rate': '78%'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_users(request):
    """
    用户增长趋势 / 活跃度统计
    GET /api/admin/statistics/users
    """
    from django.db.models.functions import TruncDate
    from datetime import timedelta
    from django.utils import timezone as tz

    days = int(request.query_params.get('days', 30))
    since = tz.now() - timedelta(days=days)

    daily_reg = (
        User.objects.filter(date_joined__gte=since)
        .annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    role_dist = User.objects.values('role').annotate(count=Count('id'))

    return success_response(data={
        'total_users': User.objects.count(),
        'daily_registrations': list(daily_reg),
        'role_distribution': list(role_dist),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_courses(_request):
    """
    课程使用情况统计
    GET /api/admin/statistics/courses
    """
    total_courses = Course.objects.count()
    total_classes = Class.objects.count()
    total_enrollments = Enrollment.objects.count()

    top_courses = (
        ClassCourse.objects.values('course__name')
        .annotate(
            class_count=Count('class_obj', distinct=True),
            student_count=Count('class_obj__enrollments', distinct=True),
        )
        .order_by('-student_count')[:10]
    )

    return success_response(data={
        'total_courses': total_courses,
        'total_classes': total_classes,
        'total_enrollments': total_enrollments,
        'top_courses': list(top_courses),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_learning(_request):
    """
    整体学习统计
    GET /api/admin/statistics/learning
    """
    from learning.models import NodeProgress
    from assessments.models import AnswerHistory

    total_records = NodeProgress.objects.count()
    total_answers = AnswerHistory.objects.count()
    correct_answers = AnswerHistory.objects.filter(is_correct=True).count()

    return success_response(data={
        'total_learning_records': total_records,
        'total_answers': total_answers,
        'correct_answers': correct_answers,
        'accuracy': round(correct_answers / total_answers * 100, 1) if total_answers > 0 else 0,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_exams(_request):
    """
    考试统计
    GET /api/admin/statistics/exams
    """
    from exams.models import Exam, ExamSubmission

    total_exams = Exam.objects.count()
    total_submissions = ExamSubmission.objects.count()
    avg_score = ExamSubmission.objects.aggregate(avg=models.Avg('score'))['avg']

    return success_response(data={
        'total_exams': total_exams,
        'total_submissions': total_submissions,
        'average_score': round(float(avg_score), 1) if avg_score else 0,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_active_users(request):
    """
    活跃用户排行
    GET /api/admin/statistics/active-users
    """
    from logs.models import OperationLog
    from datetime import timedelta
    from django.utils import timezone as tz

    days = int(request.query_params.get('days', 7))
    since = tz.now() - timedelta(days=days)

    active = (
        OperationLog.objects.filter(created_at__gte=since, user__isnull=False)
        .values('user__id', 'user__username', 'user__real_name')
        .annotate(action_count=Count('id'))
        .order_by('-action_count')[:20]
    )

    return success_response(data={'active_users': list(active), 'days': days})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_report(_request):
    """
    系统运行综合报告
    GET /api/admin/statistics/report
    """
    from logs.models import OperationLog
    from exams.models import Exam, ExamSubmission
    from assessments.models import AnswerHistory

    return success_response(data={
        'users': {
            'total': User.objects.count(),
            'students': User.objects.filter(role='student').count(),
            'teachers': User.objects.filter(role='teacher').count(),
            'admins': User.objects.filter(role='admin').count(),
        },
        'courses': {
            'total': Course.objects.count(),
            'classes': Class.objects.count(),
            'enrollments': Enrollment.objects.count(),
        },
        'exams': {
            'total': Exam.objects.count(),
            'submissions': ExamSubmission.objects.count(),
        },
        'answers': {
            'total': AnswerHistory.objects.count(),
        },
        'logs': {
            'total_operations': OperationLog.objects.count(),
        },
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_statistics_export(_request):
    """
    导出统计数据为 CSV
    GET /api/admin/statistics/export
    """
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="statistics.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['指标', '数值'])
    writer.writerow(['总用户数', User.objects.count()])
    writer.writerow(['学生数', User.objects.filter(role='student').count()])
    writer.writerow(['教师数', User.objects.filter(role='teacher').count()])
    writer.writerow(['课程数', Course.objects.count()])
    writer.writerow(['班级数', Class.objects.count()])
    writer.writerow(['选课人次', Enrollment.objects.count()])

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_class_assign_teacher(request, class_id):
    """
    为班级分配教师
    POST /api/admin/classes/{class_id}/assign-teacher
    """
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return error_response(msg='班级不存在', code=404)

    teacher_id = request.data.get('teacher_id')
    if not teacher_id:
        return error_response(msg='请提供教师ID')

    try:
        teacher = User.objects.get(id=teacher_id)
        if getattr(teacher, 'role', '') not in ['teacher', 'admin']:
            return error_response(msg='该用户不是教师')
    except User.DoesNotExist:
        return error_response(msg='教师不存在', code=404)

    class_obj.teacher = teacher
    class_obj.save()
    return success_response(msg=f'已将 {teacher.username} 分配为班级 {class_obj.name} 的教师')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_class_statistics(_request, class_id):
    """
    获取班级统计数据
    GET /api/admin/classes/{class_id}/statistics
    """
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