from __future__ import annotations

from courses.models import Course
from learning.models import LearningPath, NodeProgress
from users.models import User

from common.defense_demo_config import DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME

def get_course_defense_demo_config(course: Course | None) -> dict[str, object]:
    """
    读取课程上的演示预置配置。
    :param course: 课程对象。
    :return: 课程配置中的预置字典。
    """
    if not course or not isinstance(course.config, dict):
        return {}
    raw_config = course.config.get("defense_demo")
    return raw_config if isinstance(raw_config, dict) else {}


def is_defense_demo_primary_course(course: Course | None) -> bool:
    """
    判断课程是否为主演示课程。
    :param course: 课程对象。
    :return: True 表示主演示课程。
    """
    return get_course_defense_demo_config(course).get("mode") == "primary"


def is_defense_demo_student(user: User | None, course: Course | None) -> bool:
    """
    判断是否为演示专用学生账号。
    :param user: 当前用户对象。
    :param course: 当前课程对象。
    :return: True 表示应走预置链路。
    """
    return bool(
        user
        and getattr(user, "username", "") == DEFENSE_DEMO_PRIMARY_STUDENT_USERNAME
        and is_defense_demo_primary_course(course)
    )


def get_defense_demo_intro_payload(course: Course | None, point_id: int | None) -> dict[str, object] | None:
    """
    获取知识点介绍预置。
    :param course: 课程对象。
    :param point_id: 知识点 ID。
    :return: 预置介绍字典；不存在时返回 None。
    """
    if not point_id:
        return None

    point_map = get_course_defense_demo_config(course).get("point_intro_presets")
    if not isinstance(point_map, dict):
        return None

    payload = point_map.get(str(point_id))
    return payload if isinstance(payload, dict) else None


def get_defense_demo_resource_payload(progress: NodeProgress | None) -> dict[str, object] | None:
    """
    获取学习节点资源推荐预置。
    :param progress: 节点进度对象。
    :return: 资源推荐预置；不存在时返回 None。
    """
    if not progress or not isinstance(progress.extra_data, dict):
        return None
    payload = progress.extra_data.get("preset_resources")
    return payload if isinstance(payload, dict) else None


def get_defense_demo_stage_test_payload(progress: NodeProgress | None) -> dict[str, object] | None:
    """
    获取阶段测试固定反馈预置。
    :param progress: 节点进度对象。
    :return: 阶段测试预置；不存在时返回 None。
    """
    if not progress or not isinstance(progress.extra_data, dict):
        return None
    payload = progress.extra_data.get("preset_stage_test")
    return payload if isinstance(payload, dict) else None


def get_defense_demo_visible_order(path: LearningPath, user: User) -> int | None:
    """
    计算演示路径当前可见的最大节点顺序。
    :param path: 学习路径对象。
    :param user: 当前用户对象。
    :return: 最大可见顺序；不限制时返回 None。
    """
    config = get_course_defense_demo_config(path.course)
    visible_before_test_order = config.get("visible_before_test_order")
    if not isinstance(visible_before_test_order, int):
        return None

    stage_test_node = (
        path.nodes.filter(node_type="test").order_by("order_index", "id").first()
    )
    if not stage_test_node:
        return None

    progress = NodeProgress.objects.filter(node=stage_test_node, user=user).first()
    stage_result = None
    if progress and isinstance(progress.extra_data, dict):
        stage_result = progress.extra_data.get("stage_test_result")
    if isinstance(stage_result, dict) and stage_result.get("passed"):
        return None
    return visible_before_test_order
