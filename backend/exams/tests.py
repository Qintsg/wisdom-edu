"""考试模块核心接口与反馈逻辑测试。"""

from unittest.mock import patch
from typing import cast

from django.test import SimpleTestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework.response import Response

from application.teacher.contracts import normalize_exam_payload
from users.models import User
from courses.models import Course
from assessments.models import Question
from exams.models import Exam, ExamQuestion, ExamSubmission, FeedbackReport
from exams.serializers import ExamCreateSerializer
from common.utils import build_answer_display, decorate_question_options
from knowledge.models import KnowledgePoint


# 维护意图：返回带 DRF 类型信息的测试客户端
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _api_client(test_case: APITestCase) -> APIClient:
    """返回带 DRF 类型信息的测试客户端。"""
    return cast(APIClient, test_case.client)


# 维护意图：统一读取测试模型主键
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _model_id(instance: Exam | Question | FeedbackReport | KnowledgePoint) -> int:
    """统一读取测试模型主键。"""
    model_id = getattr(instance, 'id', None) or getattr(instance, 'pk', None)
    if model_id is None:
        raise AssertionError('测试对象缺少主键')
    return int(model_id)


# 维护意图：教师端考试创建载荷兼容性回归测试
# 边界说明：不触碰数据库，只验证请求规范化和序列化器字段语义。
# 风险说明：调整教师端考试创建契约时，需同步回归脚本与 API 文档。
class ExamCreatePayloadContractTests(SimpleTestCase):
    """教师端考试创建载荷兼容性回归测试。"""

    # 维护意图：缺省时间和班级字段不应被规整为 None 后触发 DRF 校验错误
    # 边界说明：覆盖前端或脚本省略可选字段的兼容入口。
    # 风险说明：若这些字段改为必填，需要同步此测试和公开接口契约。
    def test_optional_schedule_and_class_fields_should_remain_absent(self):
        """缺省时间和班级字段不应被规整为 None 后触发 DRF 校验错误。"""
        raw_payload = {
            'course_id': 1,
            'title': '缺省时间考试',
            'questions': [1],
        }

        normalized = normalize_exam_payload(raw_payload)
        serializer = ExamCreateSerializer(data=raw_payload)

        self.assertNotIn('start_time', normalized)
        self.assertNotIn('end_time', normalized)
        self.assertNotIn('target_class', normalized)
        self.assertTrue(serializer.is_valid(), serializer.errors)


# 维护意图：ExamPassLogicTests
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ExamPassLogicTests(APITestCase):
    # 维护意图：构造考试通过逻辑所需的基础题目与用户数据
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def setUp(self):
        """构造考试通过逻辑所需的基础题目与用户数据。"""
        self.student = User.objects.create_user(
            username='stu1',
            password='pass123456',
            role='student',
        )
        self.teacher = User.objects.create_user(
            username='tea1',
            password='pass123456',
            role='teacher',
        )
        self.course = Course.objects.create(
            name='测试课程',
            created_by=self.teacher,
        )

        self.question = Question.objects.create(
            course=self.course,
            content='1+1=?',
            question_type='single_choice',
            options=[
                {'label': 'A', 'content': '2'},
                {'label': 'B', 'content': '3'},
            ],
            answer={'answer': 'A'},
            score=10,
            is_visible=True,
            created_by=self.teacher,
        )

    # 维护意图：create exam
    # 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
    # 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
    def _create_exam(self, pass_score=60, total_score=100):
        exam = Exam.objects.create(
            course=self.course,
            title='单元测试',
            exam_type='chapter',
            status='published',
            pass_score=pass_score,
            total_score=total_score,
            created_by=self.teacher,
        )
        ExamQuestion.objects.create(
            exam=exam,
            question=self.question,
            score=10,
            order=0,
        )
        return exam

    # 维护意图：低于及格线时必须判定为未通过
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_exam_submit_low_score_should_not_pass(self):
        """低于及格线时必须判定为未通过。"""
        exam = self._create_exam()
        api_client = _api_client(self)
        api_client.force_authenticate(user=self.student)

        resp = cast(Response, api_client.post(
            f'/api/student/exams/{_model_id(exam)}/submit',
            {'answers': {str(_model_id(self.question)): 'B'}},
            format='json',
        ))

        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data['data']['passed'])

        submission = ExamSubmission.objects.get(exam=exam, user=self.student)
        self.assertFalse(submission.is_passed)

    # 维护意图：pass_score 无效(<=0)时，结果页应使用兜底阈值，不能恒通过
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_exam_result_should_use_fallback_threshold_when_pass_score_invalid(self):
        """pass_score 无效(<=0)时，结果页应使用兜底阈值，不能恒通过。"""
        exam = self._create_exam(pass_score=0)
        ExamSubmission.objects.create(
            exam=exam,
            user=self.student,
            answers={str(_model_id(self.question)): 'B'},
            score=10,
            is_passed=True,  # 模拟历史错误数据
        )

        api_client = _api_client(self)
        api_client.force_authenticate(user=self.student)
        resp = cast(Response, api_client.get(f'/api/student/exams/{_model_id(exam)}/result'))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['data']['pass_score'], 60.0)
        self.assertFalse(resp.data['data']['passed'])

    # 维护意图：test exam submit should use question accuracy and normalized score
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_exam_submit_should_use_question_accuracy_and_normalized_score(self):
        exam = Exam.objects.create(
            course=self.course,
            title='八题测试',
            exam_type='chapter',
            status='published',
            pass_score=60,
            total_score=100,
            created_by=self.teacher,
        )
        question_ids = []
        for index in range(8):
            question = Question.objects.create(
                course=self.course,
                content=f'题目{index + 1}',
                question_type='single_choice',
                options=[
                    {'label': 'A', 'content': '正确'},
                    {'label': 'B', 'content': '错误'},
                ],
                answer={'answer': 'A'},
                score=1,
                is_visible=True,
                created_by=self.teacher,
            )
            question_ids.append(_model_id(question))
            ExamQuestion.objects.create(exam=exam, question=question, score=1, order=index)

        answers = {str(qid): ('A' if index == 0 else 'B') for index, qid in enumerate(question_ids)}

        api_client = _api_client(self)
        api_client.force_authenticate(user=self.student)
        submit_resp = cast(Response, api_client.post(
            f'/api/student/exams/{_model_id(exam)}/submit',
            {'answers': answers},
            format='json',
        ))
        self.assertEqual(submit_resp.status_code, 200)
        self.assertEqual(submit_resp.data['data']['accuracy'], 12.5)
        self.assertEqual(submit_resp.data['data']['score'], 12.5)

        result_resp = cast(Response, api_client.get(f'/api/student/exams/{_model_id(exam)}/result'))
        self.assertEqual(result_resp.status_code, 200)
        self.assertEqual(result_resp.data['data']['accuracy'], 12.5)
        self.assertEqual(result_resp.data['data']['correct_count'], 1)
        self.assertEqual(len(result_resp.data['data']['question_details']), 8)


# 维护意图：AnswerDisplayTests
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class AnswerDisplayTests(APITestCase):
    # 维护意图：test true false answer display should be human readable
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_true_false_answer_display_should_be_human_readable(self):
        options = decorate_question_options(
            None,
            'true_false',
            student_answer='false',
            correct_answer=True,
        )

        self.assertEqual(build_answer_display('false', 'true_false', options), 'B. 错误')
        self.assertEqual(build_answer_display(True, 'true_false', options), 'A. 正确')


# 维护意图：验证教师端考试创建兼容公开文档中的载荷字段
# 边界说明：只覆盖请求契约归一，不依赖回归脚本或浏览器流程。
# 风险说明：教师端作业字段调整时，需要同步 OpenAPI、前端与回归脚本。
class TeacherExamCreateContractTests(APITestCase):
    """验证教师端考试创建兼容公开文档中的载荷字段。"""

    # 维护意图：构造教师、课程与可加入试卷的题目
    # 边界说明：创建接口本身负责写入 Exam 与 ExamQuestion。
    # 风险说明：权限或题库模型变化时，需要同步测试数据构造。
    def setUp(self):
        """构造教师、课程与可加入试卷的题目。"""
        self.teacher = User.objects.create_user(
            username='contract_teacher',
            password='pass123456',
            role='teacher',
        )
        self.course = Course.objects.create(
            name='契约测试课程',
            created_by=self.teacher,
        )
        self.question = Question.objects.create(
            course=self.course,
            content='契约测试题目',
            question_type='single_choice',
            options=[
                {'label': 'A', 'content': '正确'},
                {'label': 'B', 'content': '错误'},
            ],
            answer={'answer': 'A'},
            score=10,
            is_visible=True,
            created_by=self.teacher,
        )
        _api_client(self).force_authenticate(user=self.teacher)

    # 维护意图：question_ids/class_id 兼容字段不应被 None 可选字段阻断
    # 边界说明：省略 start_time/end_time/class_id 是教师端快速创建作业的合法形态。
    # 风险说明：若未来要求发布时间必填，应同步回归脚本和文档。
    def test_create_exam_should_accept_documented_question_ids_without_optional_times(self):
        """question_ids 兼容字段不应被 None 可选字段阻断。"""
        response = cast(Response, _api_client(self).post(
            '/api/teacher/exams/create',
            {
                'course_id': self.course.id,
                'title': '契约测试作业',
                'type': 'chapter',
                'question_ids': [self.question.id],
            },
            format='json',
        ))

        self.assertEqual(response.status_code, 200)
        exam = Exam.objects.get(id=response.data['data']['exam_id'])
        self.assertEqual(exam.exam_type, 'chapter')
        self.assertTrue(ExamQuestion.objects.filter(exam=exam, question=self.question).exists())


# 维护意图：ExamAsyncFeedbackTests
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ExamAsyncFeedbackTests(APITestCase):
    # 维护意图：构造异步反馈测试所需的课程、题目与考试上下文
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def setUp(self):
        """构造异步反馈测试所需的课程、题目与考试上下文。"""
        self.student = User.objects.create_user(
            username='async_student',
            password='pass123456',
            role='student',
        )
        self.teacher = User.objects.create_user(
            username='async_teacher',
            password='pass123456',
            role='teacher',
        )
        self.course = Course.objects.create(
            name='异步反馈课程',
            created_by=self.teacher,
        )
        self.point = KnowledgePoint.objects.create(
            course=self.course,
            name='异步反馈知识点',
        )
        self.question = Question.objects.create(
            course=self.course,
            content='异步反馈题目',
            question_type='single_choice',
            options=[
                {'label': 'A', 'content': '正确'},
                {'label': 'B', 'content': '错误'},
            ],
            answer={'answer': 'A'},
            score=10,
            is_visible=True,
            created_by=self.teacher,
        )
        self.question.knowledge_points.add(self.point)
        self.exam = Exam.objects.create(
            course=self.course,
            title='异步反馈考试',
            exam_type='chapter',
            status='published',
            pass_score=60,
            total_score=100,
            created_by=self.teacher,
        )
        ExamQuestion.objects.create(
            exam=self.exam,
            question=self.question,
            score=10,
            order=0,
        )
        _api_client(self).force_authenticate(user=self.student)

    # 维护意图：test submit should create pending report and enqueue worker
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    @patch('exams.report_service.enqueue_feedback_report_on_commit')
    @patch('ai_services.services.kt_service.kt_service.predict_mastery')
    def test_submit_should_create_pending_report_and_enqueue_worker(self, mock_predict_mastery, mock_enqueue):
        mock_predict_mastery.return_value = {
            'predictions': {_model_id(self.point): 0.66},
            'confidence': 0.72,
            'model_type': 'builtin',
        }

        response = cast(Response, _api_client(self).post(
            f'/api/student/exams/{_model_id(self.exam)}/submit',
            {'answers': {str(_model_id(self.question)): 'A'}},
            format='json',
        ))

        self.assertEqual(response.status_code, 200)
        payload = response.data['data']
        self.assertEqual(payload['feedback_report']['status'], 'pending')

        report = FeedbackReport.objects.get(exam=self.exam, user=self.student)
        self.assertEqual(report.status, 'pending')
        self.assertEqual(report.overview['kt_analysis']['answer_count'], 1)
        mock_enqueue.assert_called_once_with(_model_id(report), force=True)

    # 维护意图：test get feedback should return pending state
    # 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
    # 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
    def test_get_feedback_should_return_pending_state(self):
        submission = ExamSubmission.objects.create(
            exam=self.exam,
            user=self.student,
            answers={str(_model_id(self.question)): 'A'},
            score=100,
            is_passed=True,
        )
        FeedbackReport.objects.create(
            user=self.student,
            exam=self.exam,
            exam_submission=submission,
            status='pending',
            overview={
                'score': 100,
                'total_score': 100,
                'passed': True,
                'correct_count': 1,
                'total_count': 1,
                'total_questions': 1,
                'accuracy': 100,
                'summary': '',
                'knowledge_gaps': [],
            },
        )

        response = cast(Response, _api_client(self).get(f'/api/student/feedback/{_model_id(self.exam)}'))

        self.assertEqual(response.status_code, 200)
        payload = response.data['data']
        self.assertEqual(payload['status'], 'pending')
        self.assertTrue(payload['pending'])
        self.assertEqual(len(payload['question_details']), 1)
