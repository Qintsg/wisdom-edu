"""
操作日志模块 - 中间件
Operation Logs Module - Middleware

自动记录API请求的操作日志，同时保存到数据库和日志文件。
支持DEBUG模式下的详细请求记录。

功能：
- 记录所有写操作（POST/PUT/PATCH/DELETE）到数据库
- 记录日志到文件系统便于运维查看
- DEBUG模式下记录详细的请求/响应/数据库操作信息
- 中文描述便于阅读理解
"""

import json
import re
import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.db import connection
from .models import OperationLog
from .descriptions import generate_operation_description
from .logging_setup import (
    DEBUG_LOG_DB_QUERIES,
    MODULE_DISPLAY,
    debug_logger,
    operation_logger,
)

class OperationLogMiddleware(MiddlewareMixin):
    """
    操作日志中间件

    核心功能：
    1. 自动记录POST/PUT/PATCH/DELETE请求（写操作）到数据库
    2. 同时将日志写入文件便于运维查看
    3. DEBUG模式下记录详细信息：
       - 完整请求内容（请求头、请求体）
       - 完整响应内容
       - 涉及的模块/API接口
       - 数据库操作查询语句
       - 外部服务调用信息
       - 请求处理耗时

    排除：
    - GET请求（读操作，可选开启）
    - 静态文件请求
    - 健康检查等系统接口
    """

    EXCLUDE_PATTERNS = [
        r"^/static/",
        r"^/media/",
        r"^/health/",
        r"^/__debug__/",
        r"^/admin/jsi18n/",
        r"^/favicon\.ico",
    ]

    PATH_MODULE_MAP = {
        "/api/auth/": "users",
        "/api/users/": "users",
        "/api/profile": "users",
        "/api/student/profile": "users",
        "/api/admin/activation": "users",
        "/api/teacher/invitations": "users",
        "/api/courses/": "courses",
        "/api/classes/": "courses",
        "/api/my-classes": "courses",
        "/api/teacher/classes/": "courses",
        "/api/teacher/courses/": "courses",
        "/api/knowledge": "knowledge",
        "/api/student/knowledge": "knowledge",
        "/api/teacher/knowledge": "knowledge",
        "/api/teacher/resources": "knowledge",
        "/api/teacher/questions": "exams",
        "/api/exams/": "exams",
        "/api/student/exams/": "exams",
        "/api/student/feedback/": "exams",
        "/api/assessments/": "assessments",
        "/api/learning/": "learning",
        "/api/student/learning-path": "learning",
        "/api/student/path-nodes/": "learning",
        "/api/ai/": "ai_services",
        "/api/student/ai/": "ai_services",
        "/api/logs/": "logs",
        "/api/admin/": "system",
        "/admin/": "system",
    }

    METHOD_ACTION_MAP = {
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
        "GET": "read",
    }

    def should_log(self, request):
        """
        判断是否需要记录日志

        Returns:
            bool: True表示需要记录，False表示跳过
        """
        for pattern in self.EXCLUDE_PATTERNS:
            if re.match(pattern, request.path):
                return False

        # 只记录写操作（可配置是否记录GET）
        if request.method == "GET":
            return False

        return True

    def should_debug_log(self, request):
        """
        判断是否需要记录DEBUG详细日志

        DEBUG模式下记录所有API请求的详细信息
        """
        if not settings.DEBUG:
            return False

        # 排除静态资源
        for pattern in self.EXCLUDE_PATTERNS:
            if re.match(pattern, request.path):
                return False

        # API请求都记录
        if request.path.startswith("/api/"):
            return True

        return False

    def process_request(self, request):
        """
        在处理请求之前保存请求体内容并记录开始时间

        这是解决"You cannot access body after reading from request's data stream"
        错误的关键步骤。因为DRF在读取request.data后，body流就不可再次读取了。
        """
        request._request_start_time = time.time()

        request._initial_queries = len(connection.queries) if settings.DEBUG else 0

        if self.should_log(request) or self.should_debug_log(request):
            try:
                if request.method in ["POST", "PUT", "PATCH"]:
                    request._cached_body = request.body
                else:
                    request._cached_body = None
            except Exception:
                request._cached_body = None

        return None

    def get_module(self, path):
        """
        根据路径获取模块名

        Args:
            path: 请求路径

        Returns:
            str: 模块名称
        """
        for prefix, module in self.PATH_MODULE_MAP.items():
            normalized_prefix = prefix[:-1] if prefix.endswith("/") else prefix
            if path == normalized_prefix or path.startswith(prefix):
                return module
        return "system"

    def get_action_type(self, request):
        """
        获取操作类型

        根据请求路径和方法判断具体的操作类型
        """
        path_lower = request.path.lower()

        # 特殊处理登录登出
        if "login" in path_lower:
            return "login"
        if "logout" in path_lower:
            return "logout"
        if "register" in path_lower:
            return "create"
        if "import" in path_lower:
            return "import"
        if "export" in path_lower:
            return "export"

        return self.METHOD_ACTION_MAP.get(request.method, "other")

    def get_client_ip(self, request):
        """
        获取客户端IP地址

        支持代理环境下的真实IP获取
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "未知")
        return ip

    def get_request_headers(self, request):
        """
        获取请求头信息（DEBUG模式使用）

        Returns:
            dict: 过滤后的请求头
        """
        headers = {}
        for key, value in request.META.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").title()
                # 过滤敏感信息
                if "authorization" in header_name.lower():
                    headers[header_name] = "******"
                else:
                    headers[header_name] = value

        # 添加Content-Type
        if "CONTENT_TYPE" in request.META:
            headers["Content-Type"] = request.META["CONTENT_TYPE"]

        return headers

    def get_request_params(self, request):
        """
        获取请求参数（脱敏处理）

        使用process_request中缓存的body内容，避免重复读取流导致的错误
        """
        params = {}

        # GET参数
        if request.GET:
            params["query"] = dict(request.GET)

        # POST/PUT/PATCH参数 - 使用缓存的body
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                cached_body = getattr(request, "_cached_body", None)
                content_type = getattr(request, "content_type", "") or request.META.get(
                    "CONTENT_TYPE", ""
                )

                if cached_body and "application/json" in content_type:
                    body_str = cached_body.decode("utf-8")
                    if body_str:
                        params["body"] = json.loads(body_str)
                elif request.POST:
                    params["body"] = dict(request.POST)
                else:
                    params["body"] = "[请求体已处理]"
            except (json.JSONDecodeError, UnicodeDecodeError, Exception):
                params["body"] = "[无法解析]"

        # 脱敏处理（移除密码等敏感字段）
        sensitive_fields = [
            "password",
            "token",
            "secret",
            "api_key",
            "activation_code",
            "code",
        ]
        self._mask_sensitive_data(params, sensitive_fields)

        return params

    def get_response_content(self, response):
        """
        获取响应内容（DEBUG模式使用）

        Returns:
            dict/str: 响应内容
        """
        try:
            if hasattr(response, "content"):
                # 安全读取响应体，避免对 None 或文本对象重复 decode。
                raw_content = getattr(response, "content", None)
                if isinstance(raw_content, bytes):
                    content = raw_content.decode("utf-8")
                elif isinstance(raw_content, str):
                    content = raw_content
                else:
                    return "[无法获取响应内容]"
                if response.get("Content-Type", "").startswith("application/json"):
                    return json.loads(content)
                # 限制响应内容长度
                if len(content) > 4000:
                    return content[:4000] + "...[已截断]"
                return content
        except Exception:
            pass
        return "[无法获取响应内容]"

    def get_db_queries(self, request):
        """
        获取请求期间执行的数据库查询（DEBUG模式使用）

        Returns:
            list: 数据库查询列表
        """
        if not settings.DEBUG or not DEBUG_LOG_DB_QUERIES:
            return []

        initial = getattr(request, "_initial_queries", 0)
        queries = connection.queries[initial:]

        # 格式化查询信息
        result = []
        for q in queries[:20]:  # 最多记录20条
            result.append(
                {
                    "sql": q.get("sql", "")[:500],  # 限制SQL长度
                    "time": q.get("time", "0"),
                }
            )

        if len(connection.queries) > initial + 20:
            result.append(
                {
                    "sql": f"...[还有{len(connection.queries) - initial - 20}条查询]",
                    "time": "0",
                }
            )

        return result

    def _mask_sensitive_data(self, data, fields):
        """
        递归脱敏处理

        Args:
            data: 要处理的数据
            fields: 敏感字段列表
        """
        if isinstance(data, dict):
            for key in data:
                if any(f in key.lower() for f in fields):
                    data[key] = "******"
                elif isinstance(data[key], (dict, list)):
                    self._mask_sensitive_data(data[key], fields)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._mask_sensitive_data(item, fields)

    def _log_debug_info(self, request, response):
        """
        记录DEBUG模式下的详细信息

        包含：请求详情、响应详情、数据库操作、耗时统计
        """
        if not self.should_debug_log(request):
            return

        start_time = getattr(request, "_request_start_time", time.time())
        elapsed_ms = (time.time() - start_time) * 1000

        username = "匿名用户"
        if hasattr(request, "user") and request.user.is_authenticated:
            username = request.user.username

        module = self.get_module(request.path)
        module_display = MODULE_DISPLAY.get(module, module)

        status_code = response.status_code
        client_ip = self.get_client_ip(request)
        if status_code < 400:
            debug_logger.info(
                '"%s %s" %s %.2fms user=%s module=%s ip=%s',
                request.method,
                request.path,
                status_code,
                elapsed_ms,
                username,
                module_display,
                client_ip,
            )
            return

        log_level = logging.ERROR if status_code >= 500 else logging.WARNING
        resp_content = self.get_response_content(response)
        response_msg = "-"
        if isinstance(resp_content, dict):
            response_msg = str(resp_content.get("msg", "-") or "-")[:300]
        elif resp_content is not None:
            response_msg = str(resp_content)[:300]

        debug_logger.log(
            log_level,
            '"%s %s" %s %.2fms user=%s module=%s ip=%s msg=%s',
            request.method,
            request.path,
            status_code,
            elapsed_ms,
            username,
            module_display,
            client_ip,
            response_msg,
        )

        params = self.get_request_params(request)
        if params:
            try:
                params_str = json.dumps(params, ensure_ascii=False)
            except Exception:
                params_str = str(params)
            debug_logger.log(log_level, "request_params=%s", params_str[:500])

        if DEBUG_LOG_DB_QUERIES:
            db_queries = self.get_db_queries(request)
            if db_queries:
                debug_logger.log(log_level, "db_queries=%s", len(db_queries))

    def process_response(self, request, response):
        """
        处理响应，记录日志到数据库和文件

        同时处理普通操作日志和DEBUG详细日志
        """
        self._log_debug_info(request, response)

        if not self.should_log(request):
            return response

        try:
            action_type = self.get_action_type(request)
            module = self.get_module(request.path)
            description = generate_operation_description(request, action_type, module)
            is_success = 200 <= response.status_code < 400
            client_ip = self.get_client_ip(request)

            username = "匿名用户"
            user = None
            if hasattr(request, "user") and request.user.is_authenticated:
                user = request.user
                username = request.user.username

            # 创建数据库日志记录
            OperationLog.objects.create(
                user=user,
                action_type=action_type,
                module=module,
                description=description,
                request_path=request.path,
                request_method=request.method,
                request_params=self.get_request_params(request),
                response_status=response.status_code,
                is_success=is_success,
                ip_address=client_ip,
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            )

            # 写入操作日志文件
            status_text = "成功" if is_success else "失败"
            log_message = (
                f"[{username}] {description} | "
                f"路径: {request.path} | "
                f"IP: {client_ip} | "
                f"状态: {response.status_code} ({status_text})"
            )

            if is_success:
                operation_logger.info(log_message)
            else:
                operation_logger.warning(log_message)

        except Exception as e:
            # 日志记录失败不影响正常请求，但记录错误以便调试
            logger = logging.getLogger(__name__)
            logger.warning(f"操作日志记录失败: {e}")

        return response
