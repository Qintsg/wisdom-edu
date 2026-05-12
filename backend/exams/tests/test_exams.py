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
from common.domain.utils import build_answer_display, decorate_question_options
from knowledge.models import KnowledgePoint


def _api_client(test_case: APITestCase) -> APIClient:
    """返回带 DRF 类型信息的测试客户端。"""
    return cast(APIClient, test_case.client)


def _model_id(instance: Exam | Question | FeedbackReport | KnowledgePoint) -> int:
    """统一读取测试模型主键。"""
    model_id = getattr(instance, 'id', None) or getattr(instance, 'pk', None)
    if model_id is None:
        raise AssertionError('测试对象缺少主键')
    return int(model_id)


class ExamCreatePayloadContractTests(SimpleTestCase):
    """教师端考试创建载荷兼容性回归测试。"""

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


class ExamPassLogicTests(APITestCase):
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


class AnswerDisplayTests(APITestCase):
    def test_true_false_answer_display_should_be_human_readable(self):
        options = decorate_question_options(
            None,
            'true_false',
            student_answer='false',
            correct_answer=True,
        )

        self.assertEqual(build_answer_display('false', 'true_false', options), 'B. 错误')
        self.assertEqual(build_answer_display(True, 'true_false', options), 'A. 正确')


class TeacherExamCreateContractTests(APITestCase):
    """验证教师端考试创建兼容公开文档中的载荷字段。"""

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


class ExamAsyncFeedbackTests(APITestCase):
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

    @patch('exams.reports.service.enqueue_feedback_report_on_commit')
    @patch('ai_services.services.kt.service.kt_service.predict_mastery')
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
