"""
考试模块 - 序列化器

提供考试、提交、反馈相关的序列化器
"""
from decimal import Decimal

from rest_framework import serializers
from application.teacher.contracts import normalize_exam_payload
from .models import Exam, ExamQuestion, ExamSubmission, FeedbackReport


# 维护意图：考试序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ExamSerializer(serializers.ModelSerializer):
    """考试序列化器"""
    
    # 维护意图：声明考试模型的基础序列化字段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """声明考试模型的基础序列化字段。"""
        model = Exam
        fields = ['id', 'course', 'title', 'description', 'exam_type',
                  'total_score', 'pass_score', 'duration', 'start_time',
                  'end_time', 'target_class', 'status', 'created_by',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


# 维护意图：考试详情序列化器（含题目，学生端不含答案）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ExamDetailSerializer(serializers.ModelSerializer):
    """考试详情序列化器（含题目，学生端不含答案）"""
    questions = serializers.SerializerMethodField()
    
    # 维护意图：声明考试详情的只读输出字段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """声明考试详情的只读输出字段。"""
        model = Exam
        fields = ['id', 'title', 'description', 'exam_type', 'total_score',
                  'pass_score', 'duration', 'start_time', 'end_time', 'questions']
    
    # 维护意图：按题目顺序输出学生端可见的题目摘要
    # 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
    # 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
    @staticmethod
    def get_questions(obj):
        """按题目顺序输出学生端可见的题目摘要。"""
        exam_questions = ExamQuestion.objects.filter(exam=obj).order_by('order')
        return [{
            'question_id': eq.question_id,
            'content': eq.question.content,
            'options': eq.question.options,
            'type': eq.question.question_type,
            'score': float(eq.score)
        } for eq in exam_questions]


# 维护意图：考试提交序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ExamSubmitSerializer(serializers.Serializer):
    """考试提交序列化器"""
    answers = serializers.DictField()


# 维护意图：考试提交记录序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ExamSubmissionSerializer(serializers.ModelSerializer):
    """考试提交记录序列化器"""
    
    # 维护意图：声明考试提交记录的基础输出字段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """声明考试提交记录的基础输出字段。"""
        model = ExamSubmission
        fields = ['id', 'exam', 'user', 'score', 'is_passed',
                  'graded_at', 'submitted_at']


# 维护意图：创建考试序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class ExamCreateSerializer(serializers.Serializer):
    """创建考试序列化器"""
    course_id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    questions = serializers.ListField(child=serializers.IntegerField(), required=False, default=[])
    total_score = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    pass_score = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    duration = serializers.IntegerField(required=False)
    start_time = serializers.DateTimeField(required=False)
    end_time = serializers.DateTimeField(required=False)
    target_class = serializers.IntegerField(required=False)
    exam_type = serializers.CharField(max_length=20, required=False)

    # 维护意图：在字段校验前统一兼容教师端考试载荷格式
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def to_internal_value(self, data):
        """在字段校验前统一兼容教师端考试载荷格式。"""
        normalized = normalize_exam_payload(data)
        return super().to_internal_value(normalized)

    # 维护意图：校验总分与及格分的边界关系
    # 边界说明：校验边界集中在这里，避免非法输入进入业务主流程。
    # 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
    def validate(self, attrs):
        """校验总分与及格分的边界关系。"""
        total_score = attrs.get('total_score', Decimal('100'))
        pass_score = attrs.get('pass_score', Decimal('60'))

        if total_score is None or total_score <= 0:
            raise serializers.ValidationError({'total_score': '总分必须大于0'})

        if pass_score is None or pass_score <= 0:
            raise serializers.ValidationError({'pass_score': '及格分必须大于0'})

        if pass_score > total_score:
            raise serializers.ValidationError({'pass_score': '及格分不能大于总分'})

        return attrs


# 维护意图：反馈报告序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class FeedbackReportSerializer(serializers.ModelSerializer):
    """反馈报告序列化器"""
    
    # 维护意图：声明反馈报告对外暴露的字段
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    class Meta:
        """声明反馈报告对外暴露的字段。"""
        model = FeedbackReport
        fields = ['id', 'exam', 'status', 'overview', 'analysis',
                  'recommendations', 'next_tasks', 'conclusion',
                  'generated_at']


# 维护意图：反馈报告生成序列化器
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class FeedbackGenerateSerializer(serializers.Serializer):
    """反馈报告生成序列化器"""
    exam_id = serializers.IntegerField()
    force = serializers.BooleanField(required=False, default=False)
