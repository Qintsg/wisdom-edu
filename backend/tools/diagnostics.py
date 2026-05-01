"""
环境诊断模块
"""

import os
from common.neo4j_service import neo4j_service
from tools.common import BASE_DIR, COURSE_RESOURCES_DIR


def diagnose_env():
    """环境诊断"""
    print('=' * 50)
    print('环境诊断')
    print('=' * 50)

    print('\n[目录]')
    print(f'  BASE_DIR: {BASE_DIR}')
    print(f'  课程资源目录: {COURSE_RESOURCES_DIR} ({"✓" if COURSE_RESOURCES_DIR.exists() else "✗"})')
    media_dir = BASE_DIR / 'media'
    print(f'  media目录: {media_dir} ({"✓ 可写" if media_dir.exists() and os.access(media_dir, os.W_OK) else "✗"})')

    print('\n[配置文件]')
    config_path = BASE_DIR / 'config.ini'
    print(f'  config.ini: {"✓" if config_path.exists() else "✗ 缺失"}')

    print('\n[数据库]')
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print('  PostgreSQL: ✓ 连接正常')
    except Exception as e:
        print(f'  PostgreSQL: ✗ {e}')

    print(f'  Neo4j: {"✓ 可用" if neo4j_service.is_available else "✗ 不可用"}')

    print('\n[迁移状态]')
    try:
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('showmigrations', '--list', stdout=out)
        output = out.getvalue()
        unapplied = [l.strip() for l in output.split('\n') if '[ ]' in l]
        if unapplied:
            print(f'  ✗ {len(unapplied)} 个未应用的迁移:')
            for m in unapplied[:5]:
                print(f'    - {m}')
        else:
            print('  ✓ 所有迁移已应用')
    except Exception as e:
        print(f'  ✗ 无法检查迁移状态: {e}')

    print('\n[依赖包]')
    for pkg in ['pandas', 'openpyxl', 'torch', 'neo4j', 'langchain', 'requests']:
        try:
            __import__(pkg)
            print(f'  {pkg}: ✓')
        except ImportError:
            print(f'  {pkg}: ✗ 未安装')

    print('\n[API密钥]')
    llm_key = (
        os.environ.get('LLM_API_KEY')
        or os.environ.get('CUSTOM_LLM_API_KEY')
        or os.environ.get('DASHSCOPE_API_KEY')
        or os.environ.get('DEEPSEEK_API_KEY')
        or os.environ.get('ARK_API_KEY')
        or os.environ.get('DOUBAO_API_KEY')
        or os.environ.get('ZAI_API_KEY')
        or os.environ.get('ZHIPU_API_KEY')
        or os.environ.get('MOONSHOT_API_KEY')
        or os.environ.get('KIMI_API_KEY')
    )
    print(f'  LLM API Key: {"✓ 已配置" if llm_key else "✗ 未配置"}')
    print(f'  LLM_PROVIDER: {os.environ.get("LLM_PROVIDER", "deepseek") or "deepseek"}')
    print(f'  LLM_MODEL: {os.environ.get("LLM_MODEL", "deepseek-v4-flash") or "deepseek-v4-flash"}')
    print(f'  LLM_API_FORMAT: {os.environ.get("LLM_API_FORMAT", "openai-compatible") or "openai-compatible"}')

    print('\n[数据摘要]')
    try:
        from users.models import User
        from courses.models import Course
        from knowledge.models import KnowledgePoint
        from assessments.models import Question
        from exams.models import Exam

        print(f'  用户: {User.objects.count()} (学生: {User.objects.filter(role="student").count()}, '
              f'教师: {User.objects.filter(role="teacher").count()})')
        print(f'  课程: {Course.objects.count()}')
        print(f'  知识点: {KnowledgePoint.objects.count()}')
        print(f'  题目: {Question.objects.count()}')
        print(f'  考试: {Exam.objects.count()}')
    except Exception as e:
        print(f'  ✗ 查询失败: {e}')

    print('\n' + '=' * 50)
