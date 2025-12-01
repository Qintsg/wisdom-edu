"""
评分服务模块

提供测评和考试的评分功能，包括：
- 客观题自动评分
- 知识点掌握度更新
- 能力分数计算
"""
import logging
from typing import Dict, Any, List
from decimal import Decimal

logger = logging.getLogger(__name__)


class ScoringService:
    """
    评分服务类
    
    提供测评和考试的自动评分功能
    """
    
    @staticmethod
    def score_objective_question(
        question_type: str,
        correct_answer: Any,
        student_answer: Any,
        full_score: float = 1.0
    ) -> float:
        """
        对客观题进行评分
        
        Args:
            question_type: 题目类型
            correct_answer: 正确答案
            student_answer: 学生答案
            full_score: 满分
        
        Returns:
            得分
        """
        if student_answer is None:
            return 0.0
        
        if question_type == 'single_choice':
            # 单选题：完全匹配得满分
            if ScoringService._normalize_answer(student_answer) == ScoringService._normalize_answer(correct_answer):
                return full_score
            return 0.0
        
        elif question_type == 'multiple_choice':
            # 多选题：完全匹配得满分，部分匹配得部分分
            correct_set = set(ScoringService._normalize_list(correct_answer))
            student_set = set(ScoringService._normalize_list(student_answer))
            
            if correct_set == student_set:
                return full_score
            elif student_set.issubset(correct_set) and len(student_set) > 0:
                # 选对部分，给部分分
                return full_score * len(student_set) / len(correct_set) * 0.5
            return 0.0
        
        elif question_type == 'true_false':
            # 判断题
            correct_bool = ScoringService._to_bool(correct_answer)
            student_bool = ScoringService._to_bool(student_answer)
            if correct_bool == student_bool:
                return full_score
            return 0.0
        
        elif question_type == 'fill_blank':
            # 填空题：简单匹配
            if ScoringService._normalize_answer(student_answer) == ScoringService._normalize_answer(correct_answer):
                return full_score
            return 0.0
        
        else:
            # 主观题需要人工评分
            logger.warning(f"题型 {question_type} 需要人工评分")
            return 0.0
    
    @staticmethod
    def _normalize_answer(answer: Any) -> str:
        """标准化答案格式"""
        if isinstance(answer, dict):
            answer = answer.get('answer', '')
        return str(answer).strip().upper()
    
    @staticmethod
    def _normalize_list(answer: Any) -> List[str]:
        """标准化列表答案"""
        if isinstance(answer, dict):
            answer = answer.get('answers', answer.get('answer', []))
        if isinstance(answer, str):
            answer = [a.strip() for a in answer.split(',')]
        if isinstance(answer, list):
            return [str(a).strip().upper() for a in answer]
        return [str(answer).strip().upper()]
    
    @staticmethod
    def _to_bool(value: Any) -> bool:
        """转换为布尔值"""
        if isinstance(value, bool):
            return value
        if isinstance(value, dict):
            value = value.get('answer', value)
        s = str(value).strip().lower()
        return s in ('true', '1', 'yes', '对', '正确', 't')
    
    @staticmethod
    def score_exam(
        exam, 
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        对考试进行评分
        
        Args:
            exam: Exam模型实例
            answers: 学生答案 {question_id: answer}
        
        Returns:
            评分结果
        """
        from exams.models import ExamQuestion
        
        total_score = 0.0
        earned_score = 0.0
        mistakes = []
        point_stats = {}  # 按知识点统计
        
        exam_questions = ExamQuestion.objects.filter(
            exam=exam
        ).select_related('question').prefetch_related('question__knowledge_points')
        
        for eq in exam_questions:
            question = eq.question
            question_score = float(eq.score)
            total_score += question_score
            
            student_answer = answers.get(str(question.id))
            correct_answer = question.answer
            
            score = ScoringService.score_objective_question(
                question.question_type,
                correct_answer,
                student_answer,
                question_score
            )
            
            earned_score += score
            
            if score < question_score:
                mistakes.append({
                    'question_id': question.id,
                    'correct_answer': correct_answer,
                    'student_answer': student_answer,
                    'analysis': getattr(question, 'analysis', '') or ''
                })
            
            # 更新知识点统计
            for point in question.knowledge_points.all():
                if point.id not in point_stats:
                    point_stats[point.id] = {
                        'point_id': point.id,
                        'point_name': point.name,
                        'total': 0,
                        'correct': 0
                    }
                point_stats[point.id]['total'] += 1
                if score >= question_score:
                    point_stats[point.id]['correct'] += 1
        
        is_passed = earned_score >= float(exam.pass_score)
        
        return {
            'score': round(earned_score, 2),
            'total_score': round(total_score, 2),
            'is_passed': is_passed,
            'accuracy': round(earned_score / total_score, 3) if total_score > 0 else 0,
            'mistakes': mistakes,
            'point_stats': list(point_stats.values())
        }
    
    @staticmethod
    def update_mastery(
        user, 
        course, 
        point_stats: List[Dict]
    ):
        """
        根据答题情况更新知识点掌握度
        
        Args:
            user: User实例
            course: Course实例
            point_stats: 知识点统计数据
        """
        from knowledge.models import KnowledgeMastery
        
        for stat in point_stats:
            point_id = stat['point_id']
            accuracy = stat['correct'] / stat['total'] if stat['total'] > 0 else 0
            
            mastery, created = KnowledgeMastery.objects.get_or_create(
                user=user,
                knowledge_point_id=point_id,
                defaults={
                    'course': course,
                    'mastery_rate': Decimal(str(accuracy))
                }
            )
            
            if not created:
                # 使用指数移动平均更新掌握度
                alpha = 0.3  # 新数据权重
                old_rate = float(mastery.mastery_rate)
                new_rate = alpha * accuracy + (1 - alpha) * old_rate
                mastery.mastery_rate = Decimal(str(min(1.0, new_rate)))
                mastery.save()
                
                logger.debug(
                    f"用户 {user.username} 知识点 {point_id} "
                    f"掌握度更新: {old_rate:.2f} -> {new_rate:.2f}"
                )
    
    @staticmethod
    def calculate_ability_score(
        answers: Dict[str, str], 
        questions: List
    ) -> Dict[str, float]:
        """
        计算能力测评得分
        
        根据问卷答案计算各维度能力得分
        
        Args:
            answers: 答案 {question_id: option_value}
            questions: SurveyQuestion列表
        
        Returns:
            各维度得分
        """
        dimension_scores = {}
        dimension_counts = {}
        
        for q in questions:
            answer_value = answers.get(str(q.id))
            if not answer_value:
                continue
            
            # 查找选项得分
            score = 0
            for option in q.options:
                if option.get('value') == answer_value:
                    score = option.get('score', 0)
                    break
            
            # 按维度累计
            dimension = '综合能力'  # 默认维度
            if dimension not in dimension_scores:
                dimension_scores[dimension] = 0
                dimension_counts[dimension] = 0
            
            dimension_scores[dimension] += score
            dimension_counts[dimension] += 1
        
        # 计算平均分（标准化到100分制）
        result = {}
        for dim, total in dimension_scores.items():
            count = dimension_counts[dim]
            if count > 0:
                # 假设每题满分5分，转换为100分制
                avg = total / count
                result[dim] = round(avg / 5 * 100, 1)
        
        return result
