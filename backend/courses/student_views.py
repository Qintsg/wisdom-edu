"""
课程模块 - 学生接口

包含：课程列表、选课、班级加入/退出/查看
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.db import transaction

from common.responses import success_response, error_response, created_response, forbidden_response
from users.models import User, UserCourseContext
from .models import Course, Class, ClassCourse, Enrollment, Announcement
from .serializers import CourseSerializer, CourseSelectSerializer


# 维护意图：把班级发布课程收敛为学生端稳定可用的摘要
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _serialize_course_summary(course: Course) -> dict[str, object | None]:
    """把班级发布课程收敛为学生端稳定可用的摘要。"""
    return {
        'course_id': course.id,
        'course_name': course.name,
        'course_cover': course.cover.url if course.cover else None,
    }


# 维护意图：返回班级默认课程与已发布课程，避免旧班级只走默认课程时前端无课可选
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def _get_class_course_summaries(class_obj: Class) -> list[dict[str, object | None]]:
    """返回班级默认课程与已发布课程，避免旧班级只走默认课程时前端无课可选。"""
    summaries: list[dict[str, object | None]] = []
    seen_course_ids: set[int] = set()

    if class_obj.course_id and class_obj.course:
        summaries.append(_serialize_course_summary(class_obj.course))
        seen_course_ids.add(class_obj.course_id)

    class_courses = ClassCourse.objects.filter(
        class_obj=class_obj,
        is_active=True,
    ).select_related('course')
    for class_course in class_courses:
        if class_course.course_id in seen_course_ids:
            continue
        summaries.append(_serialize_course_summary(class_course.course))
        seen_course_ids.add(class_course.course_id)

    return summaries


# 维护意图：统一学生班级列表与加入班级后的响应结构
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def _serialize_student_class(enrollment: Enrollment) -> dict[str, object | None]:
    """统一学生班级列表与加入班级后的响应结构。"""
    class_obj = enrollment.class_obj
    courses = _get_class_course_summaries(class_obj)
    primary_course = courses[0] if courses else {}
    teacher = class_obj.teacher
    teacher_username = teacher.username if teacher else None
    teacher_real_name = teacher.real_name if teacher else None

    return {
        'class_id': class_obj.id,
        'class_name': class_obj.name,
        'description': class_obj.description or '',
        'teacher_name': teacher_real_name or teacher_username,
        'teacher_username': teacher_username,
        'student_count': class_obj.get_student_count(),
        'courses': courses,
        'course_id': primary_course.get('course_id'),
        'course_name': primary_course.get('course_name'),
        'enrolled_at': enrollment.enrolled_at.isoformat(),
    }


# 维护意图：获取用户课程列表 GET /api/courses 学生返回已选课程，教师返回教授的课程
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def course_list(request):
    """
    获取用户课程列表
    GET /api/courses
    
    学生返回已选课程，教师返回教授的课程
    """
    user = request.user
    
    if user.role == 'student':
        enrollments = Enrollment.objects.filter(user=user).select_related(
            'class_obj__course', 'class_obj__teacher'
        )
        courses = []
        for e in enrollments:
            for course_summary in _get_class_course_summaries(e.class_obj):
                courses.append({
                    'course_id': course_summary['course_id'],
                    'course_name': course_summary['course_name'],
                    'course_cover': course_summary['course_cover'],
                    'class_id': e.class_obj.id,
                    'class_name': e.class_obj.name,
                    'teacher_name': e.class_obj.teacher.username if e.class_obj.teacher else None,
                    'enrolled_at': e.enrolled_at.isoformat()
                })
    else:
        teaching_classes = Class.objects.filter(teacher=user).select_related('course')
        courses = []
        seen_courses = set()
        for c in teaching_classes:
            class_courses = ClassCourse.objects.filter(
                class_obj=c, is_active=True
            ).select_related('course')
            for cc in class_courses:
                if cc.course.id not in seen_courses:
                    seen_courses.add(cc.course.id)
                    courses.append({
                        'course_id': cc.course.id,
                        'course_name': cc.course.name,
                        'course_cover': cc.course.cover.url if cc.course.cover else None,
                        'class_id': c.id,
                        'class_name': c.name,
                        'student_count': Enrollment.objects.filter(class_obj=c).count()
                    })
    
    context = UserCourseContext.objects.filter(user=user).first()
    current_course_id = context.current_course_id if context else None
    
    return success_response(data={
        'courses': courses,
        'current_course_id': current_course_id
    })


# 维护意图：切换当前课程 POST /api/courses/select
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def course_select(request):
    """
    切换当前课程
    POST /api/courses/select
    """
    serializer = CourseSelectSerializer(data=request.data)
    if not serializer.is_valid():
        return error_response(msg=str(serializer.errors))
    
    course_id = serializer.validated_data['course_id']
    class_id = serializer.validated_data.get('class_id')
    
    # 验证课程存在
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return error_response(msg='课程不存在', code=404)
    
    # 验证用户权限
    user = request.user
    if user.role == 'student':
        enrollment = Enrollment.objects.filter(
            user=user,
        ).filter(
            Q(class_obj__course_id=course_id)
            | Q(class_obj__class_courses__course_id=course_id, class_obj__class_courses__is_active=True)
        ).select_related('class_obj').first()
        if not enrollment:
            return error_response(msg='您未选修该课程', code=403)
        class_obj = enrollment.class_obj
    else:
        # 教师验证
        class_obj = Class.objects.filter(
            Q(course_id=course_id)
            | Q(class_courses__course_id=course_id, class_courses__is_active=True),
            teacher=user,
        ).first()
        if not class_obj and not user.is_superuser:
            return error_response(msg='您未教授该课程', code=403)
        
        if class_id:
            class_obj = Class.objects.filter(id=class_id, teacher=user).first()
    
    # 更新用户课程上下文
    context, created = UserCourseContext.objects.get_or_create(user=user)
    context.current_course = course
    context.current_class = class_obj
    context.save()
    
    return success_response(data={
        'course_id': course.id,
        'course_name': course.name,
        'class_id': class_obj.id if class_obj else None,
        'class_name': class_obj.name if class_obj else None
    }, msg='课程切换成功')


# ========== 课程管理（教师/管理员） ==========


# 维护意图：学生通过邀请码加入班级 POST /api/student/classes/join 请求参数： - code: 邀请码（必填） 返回： - class_id: 班级ID - class_na。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_join_class(request):
    """
    学生通过邀请码加入班级
    POST /api/student/classes/join
    
    请求参数：
    - code: 邀请码（必填）
    
    返回：
    - class_id: 班级ID
    - class_name: 班级名称
    - course_id: 课程ID
    - course_name: 课程名称
    """
    from users.models import ClassInvitation
    
    user = request.user
    
    # 验证学生身份
    if user.role != 'student':
        return forbidden_response(msg='仅学生可以加入班级')
    
    code = request.data.get('code')
    
    if not code:
        return error_response(msg='请提供邀请码')
    
    # 确保code是字符串类型
    if not isinstance(code, str):
        return error_response(msg='邀请码格式错误')
    
    try:
        invitation = ClassInvitation.objects.select_related(
            'class_obj__teacher',
            'class_obj__course',
        ).get(code=code.strip().upper())
    except ClassInvitation.DoesNotExist:
        return error_response(msg='邀请码不存在', code=404)
    
    if not invitation.is_valid():
        return error_response(msg='邀请码无效或已过期')
    
    class_obj = invitation.class_obj
    if not class_obj.is_active:
        return error_response(msg='班级已停用，暂不能加入')
    
    # 检查是否已加入
    if Enrollment.objects.filter(user=user, class_obj=class_obj).exists():
        return error_response(msg='您已经加入了此班级')
    
    # 加入班级
    with transaction.atomic():
        enrollment = Enrollment.objects.create(
            user=user,
            class_obj=class_obj,
            role='student'
        )
        invitation.use()

    return success_response(
        data=_serialize_student_class(enrollment),
        msg='成功加入班级'
    )


# 维护意图：学生退出班级 DELETE /api/student/classes/{class_id}/leave
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def student_leave_class(request, class_id):
    """
    学生退出班级
    DELETE /api/student/classes/{class_id}/leave
    """
    user = request.user
    
    # 验证学生身份
    if user.role != 'student':
        return forbidden_response(msg='仅学生可以退出班级')
    
    try:
        enrollment = Enrollment.objects.get(user=user, class_obj_id=class_id)
    except Enrollment.DoesNotExist:
        return error_response(msg='您未加入此班级', code=404)
    
    enrollment.delete()
    return success_response(msg='已退出班级')


# 维护意图：获取学生班级列表 GET /api/student/classes 返回学生已加入的所有班级及其关联的课程
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_class_list(request):
    """
    获取学生班级列表
    GET /api/student/classes
    
    返回学生已加入的所有班级及其关联的课程
    """
    user = request.user
    
    # 验证学生身份
    if user.role != 'student':
        return forbidden_response(msg='仅学生可以访问此接口')
    
    enrollments = Enrollment.objects.filter(user=user).select_related(
        'class_obj__teacher', 'class_obj__course'
    )
    classes = [_serialize_student_class(enrollment) for enrollment in enrollments]
    
    return success_response(data={'classes': classes})


# 维护意图：获取班级详情（学生视角） GET /api/student/classes/{class_id} 返回班级的详细信息、课程列表和成员概况
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_class_detail(request, class_id):
    """
    获取班级详情（学生视角）
    GET /api/student/classes/{class_id}
    
    返回班级的详细信息、课程列表和成员概况
    """
    user = request.user
    
    # 验证学生身份
    if user.role != 'student':
        return forbidden_response(msg='仅学生可以访问此接口')
    
    # 验证学生是否加入了该班级
    try:
        enrollment = Enrollment.objects.get(user=user, class_obj_id=class_id)
    except Enrollment.DoesNotExist:
        return error_response(msg='您未加入此班级', code=404)
    
    class_obj = enrollment.class_obj
    
    courses = _get_class_course_summaries(class_obj)
    
    student_count = Enrollment.objects.filter(class_obj=class_obj).count()

    announcements = Announcement.objects.filter(class_obj=class_obj).order_by('-created_at')[:20]
    announcement_list = [{
        'id': a.id,
        'title': a.title,
        'content': a.content,
        'createdAt': a.created_at.strftime('%Y-%m-%d %H:%M') if a.created_at else None,
    } for a in announcements]

    return success_response(data={
        'class_id': class_obj.id,
        'class_name': class_obj.name,
        'description': class_obj.description or '',
        'teacher': {
            'user_id': class_obj.teacher.id,
            'username': class_obj.teacher.username
        } if class_obj.teacher else None,
        'courses': courses,
        'student_count': student_count,
        'enrolled_at': enrollment.enrolled_at.isoformat(),
        'created_at': class_obj.created_at.isoformat(),
        'announcements': announcement_list,
    })


# ============ 班级邀请码管理（教师）============
