"""
课程模块教师接口兼容入口。

具体实现按课程、班级、邀请码、学生画像和公告职责拆分，保留旧导入路径。
"""
from users.models import User

from .models import Announcement, Class, ClassCourse, Course, Enrollment
from .serializers import CourseSerializer
from .teacher_announcement_views import announcement_detail, class_announcements
from .teacher_class_views import (
    class_courses,
    class_create,
    class_delete,
    class_publish_course,
    class_unpublish_course,
    class_update,
    my_classes,
    teacher_class_progress,
)
from .teacher_course_helpers import (
    COURSE_CONFIG_DEFAULTS,
    extract_course_archive as _extract_course_archive,
    resolve_archive_root as _resolve_archive_root,
)
from .teacher_course_views import (
    course_create,
    course_delete,
    course_search,
    course_update,
    get_course_settings,
    my_created_courses,
    teacher_course_cover_upload,
    teacher_course_statistics,
    update_course_settings,
)
from .teacher_invitation_views import (
    delete_class_invitation,
    generate_class_invitation,
    list_class_invitations,
)
from .teacher_student_views import (
    class_students,
    get_class_student_profiles,
    remove_student_from_class,
)


__all__ = [
    'Announcement',
    'COURSE_CONFIG_DEFAULTS',
    'Class',
    'ClassCourse',
    'Course',
    'CourseSerializer',
    'Enrollment',
    'User',
    '_extract_course_archive',
    '_resolve_archive_root',
    'announcement_detail',
    'class_announcements',
    'class_courses',
    'class_create',
    'class_delete',
    'class_publish_course',
    'class_students',
    'class_unpublish_course',
    'class_update',
    'course_create',
    'course_delete',
    'course_search',
    'course_update',
    'delete_class_invitation',
    'generate_class_invitation',
    'get_class_student_profiles',
    'get_course_settings',
    'list_class_invitations',
    'my_classes',
    'my_created_courses',
    'remove_student_from_class',
    'teacher_class_progress',
    'teacher_course_cover_upload',
    'teacher_course_statistics',
    'update_course_settings',
]
