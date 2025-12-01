"""
AI服务模块
提供大模型调用、评分计算、路径规划、知识追踪等服务

LLMService: 大模型调用服务（支持通义千问、DeepSeek等）
ScoringService: 评分计算服务
PathService: 学习路径服务
KnowledgeTracingService: 知识追踪服务（支持 DKT、MEFKT 模型融合预测）
"""
from ai_services.services.llm_service import LLMService, llm_service
from ai_services.services.scoring_service import ScoringService
from ai_services.services.path_service import PathService
from ai_services.services.kt_service import KnowledgeTracingService, kt_service

__all__ = [
    'LLMService', 
    'llm_service',
    'ScoringService', 
    'PathService',
    'KnowledgeTracingService',
    'kt_service',
]
