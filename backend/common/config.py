"""
配置读取模块

从config.ini文件读取业务配置参数。

使用示例：
    from common.config import get_config, get_config_int, get_config_bool
    
    page_size = get_config('pagination', 'default_page_size', '20')
    
    page_size = get_config_int('pagination', 'default_page_size', 20)
    
    enabled = get_config_bool('logging', 'operation_log_enabled', True)
"""
import configparser
from pathlib import Path
from django.conf import settings

# 配置文件路径
CONFIG_FILE = Path(settings.BASE_DIR) / 'config.ini'

# 全局配置解析器
_config = None


def _get_parser():
    """获取配置解析器（单例）"""
    global _config
    if _config is None:
        _config = configparser.ConfigParser()
        if CONFIG_FILE.exists():
            _config.read(CONFIG_FILE, encoding='utf-8')
    return _config


def get_config(section: str, key: str, default: str = '') -> str:
    """
    获取配置值（字符串）
    
    Args:
        section: 配置节名
        key: 配置键名
        default: 默认值
    
    Returns:
        配置值字符串
    """
    parser = _get_parser()
    try:
        return parser.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        return default


def get_config_int(section: str, key: str, default: int = 0) -> int:
    """
    获取配置值（整数）
    
    Args:
        section: 配置节名
        key: 配置键名
        default: 默认值
    
    Returns:
        配置值整数
    """
    value = get_config(section, key, str(default))
    try:
        return int(value)
    except ValueError:
        return default


def get_config_float(section: str, key: str, default: float = 0.0) -> float:
    """
    获取配置值（浮点数）
    
    Args:
        section: 配置节名
        key: 配置键名
        default: 默认值
    
    Returns:
        配置值浮点数
    """
    value = get_config(section, key, str(default))
    try:
        return float(value)
    except ValueError:
        return default


def get_config_bool(section: str, key: str, default: bool = False) -> bool:
    """
    获取配置值（布尔值）
    
    Args:
        section: 配置节名
        key: 配置键名
        default: 默认值
    
    Returns:
        配置值布尔值
    """
    value = get_config(section, key, str(default)).lower()
    if value in ('true', 'yes', '1', 'on'):
        return True
    elif value in ('false', 'no', '0', 'off'):
        return False
    return default


def get_config_list(
    section: str,
    key: str,
    default: list[str] | None = None,
    separator: str = ',',
) -> list[str]:
    """
    获取配置值（列表）
    
    Args:
        section: 配置节名
        key: 配置键名
        default: 默认值
        separator: 分隔符
    
    Returns:
        配置值列表
    """
    if default is None:
        default = []
    value = get_config(section, key, '')
    if not value:
        return default
    return [item.strip() for item in value.split(separator) if item.strip()]


def reload_config():
    """重新加载配置文件"""
    global _config
    _config = None
    _get_parser()


# 常用配置的快捷访问
class AppConfig:
    """应用配置快捷访问类"""
    
    # 认证配置
    @staticmethod
    def password_min_length() -> int:
        """返回密码最小长度要求。"""
        return get_config_int('authentication', 'password_min_length', 8)
    
    @staticmethod
    def password_require_uppercase() -> bool:
        """返回密码是否必须包含大写字母。"""
        return get_config_bool('authentication', 'password_require_uppercase', True)
    
    @staticmethod
    def password_require_numbers() -> bool:
        """返回密码是否必须包含数字。"""
        return get_config_bool('authentication', 'password_require_numbers', True)
    
    @staticmethod
    def password_require_special() -> bool:
        """返回密码是否必须包含特殊字符。"""
        return get_config_bool('authentication', 'password_require_special', False)
    
    # 分页配置
    @staticmethod
    def default_page_size() -> int:
        """返回分页接口的默认每页数量。"""
        return get_config_int('pagination', 'default_page_size', 20)
    
    @staticmethod
    def max_page_size() -> int:
        """返回分页接口允许的最大每页数量。"""
        return get_config_int('pagination', 'max_page_size', 100)

    # AI 服务配置
    @staticmethod
    def ai_api_timeout() -> int:
        """返回 AI 服务调用的默认超时时间（秒）。"""
        return get_config_int('ai_services', 'api_timeout', 120)

    @staticmethod
    def ai_feedback_enabled() -> bool:
        """返回 AI 反馈报告是否允许调用大模型。"""
        return get_config_bool('ai_services', 'ai_feedback_enabled', True)

    # LLM 配置
    @staticmethod
    def llm_provider() -> str:
        """返回默认的大模型提供方标识。"""
        return get_config('llm', 'provider', 'deepseek').strip().lower() or 'deepseek'

    @staticmethod
    def llm_model() -> str:
        """返回默认的大模型名称。"""
        return get_config('llm', 'model', 'deepseek-v4-pro').strip() or 'deepseek-v4-pro'

    @staticmethod
    def llm_api_format() -> str:
        """返回默认的兼容接口格式。"""
        return get_config('llm', 'api_format', 'openai-compatible').strip().lower() or 'openai-compatible'

    @staticmethod
    def llm_base_url() -> str:
        """返回配置文件中的统一 LLM 网关地址。"""
        return get_config('llm', 'base_url', '').strip()

    @staticmethod
    def llm_request_timeout() -> int:
        """返回 LLM 客户端调用超时时间（秒）。"""
        return get_config_int('llm', 'request_timeout_seconds', AppConfig.ai_api_timeout())

    @staticmethod
    def llm_max_retries() -> int:
        """返回 LLM 客户端的最大重试次数。"""
        return get_config_int('llm', 'max_retries', 2)

    # GraphRAG 配置
    @staticmethod
    def graphrag_embedder_provider() -> str:
        """返回 GraphRAG 的默认向量器提供方。"""
        return get_config('graphrag', 'embedder_provider', 'hash').strip().lower() or 'hash'

    @staticmethod
    def graphrag_sentence_model() -> str:
        """返回 GraphRAG 本地语义向量模型名称。"""
        return get_config(
            'graphrag',
            'sentence_model',
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
        ).strip() or 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

    @staticmethod
    def graphrag_vector_dimension() -> int:
        """返回 GraphRAG 向量维度。"""
        return get_config_int('graphrag', 'vector_dimension', 256)

    @staticmethod
    def graphrag_qdrant_path() -> str:
        """返回 GraphRAG 的 Qdrant 本地持久化目录。"""
        return get_config('graphrag', 'qdrant_path', 'runtime_logs/rag/qdrant').strip() or 'runtime_logs/rag/qdrant'
    
    # 知识图谱配置
    @staticmethod
    def mastery_threshold() -> float:
        """返回知识掌握度阈值。"""
        return get_config_float('knowledge', 'mastery_threshold', 0.6)
    
    # 激活码配置
    @staticmethod
    def activation_code_length() -> int:
        """返回激活码长度。"""
        return get_config_int('activation_code', 'code_length', 8)
    
    @staticmethod
    def activation_code_expiration_days() -> int:
        """返回激活码默认有效天数。"""
        return get_config_int('activation_code', 'default_expiration_days', 30)
    
    # 邀请码配置
    @staticmethod
    def invitation_code_length() -> int:
        """返回邀请码长度。"""
        return get_config_int('invitation_code', 'code_length', 6)
    
    @staticmethod
    def invitation_code_max_uses() -> int:
        """返回邀请码默认最大使用次数。"""
        return get_config_int('invitation_code', 'default_max_uses', 50)
    
    @staticmethod
    def invitation_code_expiration_days() -> int:
        """返回邀请码默认有效天数。"""
        return get_config_int('invitation_code', 'default_expiration_days', 7)
    
    # 考试配置
    @staticmethod
    def exam_default_duration() -> int:
        """返回考试默认时长（分钟）。"""
        return get_config_int('exam', 'default_duration_minutes', 60)
    
    @staticmethod
    def exam_pass_ratio() -> float:
        """返回考试默认通过比例。"""
        return get_config_float('exam', 'default_pass_ratio', 0.6)
    
    # 文件上传配置
    @staticmethod
    def max_file_size_mb() -> int:
        """返回上传文件大小上限（MB）。"""
        return get_config_int('file_upload', 'max_file_size_mb', 50)
    
    @staticmethod
    def allowed_image_formats() -> list:
        """返回允许上传的图片格式列表。"""
        return get_config_list('file_upload', 'allowed_image_formats', ['jpg', 'jpeg', 'png', 'gif', 'webp'])
    
    @staticmethod
    def allowed_document_formats() -> list:
        """返回允许上传的文档格式列表。"""
        return get_config_list('file_upload', 'allowed_document_formats', ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'md'])

    # 学习路径配置
    @staticmethod
    def max_path_nodes() -> int:
        """返回学习路径允许生成的最大节点数。"""
        return get_config_int('learning_path', 'max_nodes', 100)

    @staticmethod
    def path_test_interval() -> int:
        """返回学习路径中插入测试节点的间隔。"""
        return get_config_int('learning_path', 'test_interval', 3)
