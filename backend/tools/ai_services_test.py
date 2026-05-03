"""AI 服务测试。

包含知识追踪 (KT) 模型测试和大语言模型 (LLM) 服务测试。
从原 tests/ai_services_test.py 迁移而来。
"""


# 维护意图：测试知识追踪(KT)服务的预测功能
# 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
# 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
def test_kt_service():
    """测试知识追踪(KT)服务的预测功能。"""
    from ai_services.services import kt_service
    from assessments.models import AnswerHistory, Question

    print('开始测试知识追踪服务...')
    info = kt_service.get_model_info()
    print(f"模式: {info.get('prediction_mode', 'fusion')}, "
          f"可用: {info.get('is_available', False)}")

    history_records = list(
        AnswerHistory.objects.filter(question__is_visible=True)
        .select_related('question')
        .order_by('course_id', 'user_id', 'answered_at')[:20]
    )
    history = []
    course_id = 1
    user_id = 1

    if history_records:
        course_id = int(history_records[0].course_id)
        user_id = int(history_records[0].user_id)
        for record in AnswerHistory.objects.filter(
            course_id=course_id,
            user_id=user_id,
        ).order_by('answered_at')[:10]:
            history.append(
                {
                    'question_id': record.question_id,
                    'correct': 1 if record.is_correct else 0,
                    'knowledge_point_id': record.knowledge_point_id,
                    'timestamp': record.answered_at.isoformat() if record.answered_at else None,
                }
            )
    else:
        fallback_questions = list(
            Question.objects.filter(is_visible=True)
            .prefetch_related('knowledge_points')
            .order_by('course_id', 'id')[:3]
        )
        if fallback_questions:
            course_id = int(fallback_questions[0].course_id)
            for index, question in enumerate(fallback_questions):
                point_id = question.knowledge_points.values_list('id', flat=True).first()
                if point_id is None:
                    continue
                history.append(
                    {
                        'question_id': int(question.id),
                        'correct': 1 if index % 2 == 0 else 0,
                        'knowledge_point_id': int(point_id),
                    }
                )

    print(f"测试课程: course_id={course_id}, user_id={user_id}, history={len(history)}")
    result = kt_service.predict_mastery(
        user_id=user_id,
        course_id=course_id,
        answer_history=history
    )
    print(f"预测结果: {result.get('predictions', {})}")


# 维护意图：测试大语言模型(LLM)服务的推荐理由生成功能
# 边界说明：测试步骤保持显式，便于定位回归阶段和失败上下文。
# 风险说明：调整测试断言时，需保留失败上下文和可复现实例。
def test_llm_service():
    """测试大语言模型(LLM)服务的推荐理由生成功能。"""
    from ai_services.services import llm_service

    print('开始测试大模型服务...')
    print(f"模型: {getattr(llm_service, 'model_name', 'unknown')}, "
          f"可用: {getattr(llm_service, 'is_available', False)}")

    out = llm_service.generate_resource_reason(
        resource_info={'title': 'Spark入门教程', 'type': '视频'},
        student_mastery=0.45,
        point_name='Spark计算',
    )
    print(f"推荐理由: {out.get('reason', '')}")
