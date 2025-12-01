"""
用户模块 - 序列化器

提供用户注册、登录、信息展示的序列化器
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User, HabitPreference, ActivationCode, ClassInvitation


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    class Meta:
        """声明用户基础信息的输出字段。"""
        model = User
        fields = ['id', 'username', 'email', 'role', 'avatar', 'phone',
                  'first_name', 'last_name', 'real_name', 'student_id', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    real_name = serializers.CharField(required=False, allow_blank=True)
    student_id = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        """声明注册接口允许写入的用户字段。"""
        model = User
        fields = ['username', 'password', 'email', 'role', 'real_name', 'student_id']

    @staticmethod
    def create(validated_data):
        """根据注册载荷创建用户账号。"""
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            role=validated_data.get('role', 'student'),
            real_name=validated_data.get('real_name', ''),
            student_id=validated_data.get('student_id', '')
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """自定义JWT Token序列化器"""

    @classmethod
    def get_token(cls, user):
        """在 JWT 中补充角色和用户名声明。"""
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token


class HabitPreferenceSerializer(serializers.ModelSerializer):
    """学习习惯偏好序列化器"""

    class Meta:
        """声明学习习惯偏好可读写字段。"""
        model = HabitPreference
        fields = ['preferred_resource', 'preferred_study_time', 'study_pace',
                  'study_duration', 'review_frequency', 'learning_style',
                  'accept_challenge', 'daily_goal_minutes', 'weekly_goal_days',
                  'preferences', 'updated_at']
        read_only_fields = ['updated_at']


class ProfileSerializer(serializers.Serializer):
    """学习者画像序列化器"""
    knowledge_mastery = serializers.ListField()
    ability_scores = serializers.DictField()
    habit_preferences = serializers.DictField()
    profile_summary = serializers.CharField()
    last_update = serializers.DateTimeField()


class ActivationCodeSerializer(serializers.ModelSerializer):
    """激活码序列化器"""
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True, default=None, allow_null=True
    )
    used_by_username = serializers.CharField(
        source='used_by.username', read_only=True, default=None, allow_null=True
    )

    class Meta:
        """声明激活码列表展示所需字段。"""
        model = ActivationCode
        fields = ['id', 'code', 'code_type', 'is_used', 'used_by_username',
                  'used_at', 'expires_at', 'remark', 'created_by_username', 'created_at']
        read_only_fields = ['id', 'code', 'is_used', 'used_at', 'created_at']


class ClassInvitationSerializer(serializers.ModelSerializer):
    """班级邀请码序列化器"""
    class_name = serializers.CharField(source='class_obj.name', read_only=True)
    course_name = serializers.CharField(
        source='class_obj.course.name', read_only=True, default=None, allow_null=True
    )
    created_by_username = serializers.CharField(
        source='created_by.username', read_only=True, default=None, allow_null=True
    )
    is_valid = serializers.SerializerMethodField()

    class Meta:
        """声明班级邀请码的管理端输出字段。"""
        model = ClassInvitation
        fields = ['id', 'code', 'class_obj', 'class_name', 'course_name',
                  'max_uses', 'use_count', 'expires_at', 'is_active',
                  'is_valid', 'created_by_username', 'created_at']
        read_only_fields = ['id', 'code', 'use_count', 'created_at']

    @staticmethod
    def get_is_valid(obj):
        """返回当前邀请码是否仍可使用。"""
        return obj.is_valid()
