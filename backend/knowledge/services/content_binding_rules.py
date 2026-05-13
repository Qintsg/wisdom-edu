#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
课程内容绑定规则。
@Project : wisdom-edu
@File : content_binding_rules.py
@Author : Qintsg
@Date : 2026-05-13 11:25
'''

from __future__ import annotations

import re


NORMALIZE_PATTERN = re.compile(r"[^\w]+", re.UNICODE)
TYPO_REPLACEMENTS = (
    ("罗辑", "逻辑"),
    ("kedoids", "kmedoids"),
)
GENERIC_POINT_NAMES = frozenset(
    {
        "Hadoop",
        "HDFS",
        "MapReduce",
        "Hive",
        "Spark",
        "线性回归",
        "逻辑回归",
        "罗辑回归模型原理",
        "决策树",
        "聚类",
        "推荐系统",
    }
)
FORCE_RULE_POINT_NAMES = frozenset(
    {
        "HDFS基本操作",
        "梯度下降",
        "模型优化方法",
        "PySpark线性回归应用",
        "PySpark罗辑回归应用",
        "PySpark随机森林应用",
        "PySpark聚类应用",
        "PySpark推荐应用",
        "PySpark文本处理应用",
    }
)

BIG_DATA_BINDING_RULES: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("大数据概念和影响",), ("大数据基本概念", "大数据应用")),
    (("四个v", "variety", "volume", "velocity", "value", "信息化浪潮", "大数据发展", "大数据时代", "大数据概念"), ("大数据基本概念",)),
    (("大数据分析可以", "人类的决策", "大数据影响", "大数据应用", "典型应用场景"), ("大数据应用",)),
    (("大数据关键技术", "流计算", "数据存储和管理", "计算模式"), ("大数据关键技术",)),
    (("hadoop的两大核心", "两大核心"), ("HDFS", "MapReduce")),
    (
        (
            "mapreduce在扩展性和多框架支持等方面的不足",
            "资源管理框架",
            "扩展性和多框架",
            "hadoop项目结构",
            "hadoop2",
            "yarn",
        ),
        ("Hadoop项目结构", "Hadoop发展与演变"),
    ),
    (("linux基础",), ("Hadoop安装与使用",)),
    (("hbase", "bigtable", "nosql", "region"), ("NoSql数据库",)),
    (("hdfs命令", "查看某个目录", "删除文件", "显示文件内容"), ("HDFS基本操作",)),
    (("namenode", "datanode", "数据节点", "名称节点", "块概念", "主从", "类似的框架"), ("HDFS工作原理",)),
    (("hdfs",), ("HDFS",)),
    (("wordcount", "map和reduce", "partitioner", "reducer阶段", "mapreduce工作流程"), ("MapReduce工作原理",)),
    (("mapreduce应用",), ("MapReduce应用",)),
    (("mapreduce",), ("MapReduce",)),
    (("hadoop",), ("Hadoop",)),
    (("云计算", "云数据库", "数据中心"), ("云数据库",)),
    (("hiveql", "hive基础操作", "hive基本操作"), ("Hive基本操作",)),
    (("hive工作原理", "hive执行引擎", "hive主要由", "hdfs文件系统"), ("Hive工作原理",)),
    (("hive", "数据仓库"), ("Hive",)),
    (("spark sql基本操作", "dataframe", "distinct", "printschema"), ("Spark SQL基本操作",)),
    (("spark sql",), ("Spark SQL原理与特征",)),
    (("rdd", "spark工作原理", "缓存rdd"), ("Spark工作原理",)),
    (("pyspark机器学习自然语言处理与推荐系统",), ("PySpark文本处理应用", "PySpark推荐应用")),
    (("机器学习概述", "机器学习"), ("大数据智能分析挖掘",)),
    (("梯度下降", "学习率", "优化算法"), ("梯度下降",)),
    (("pyspark中实现线性回归", "pyspark线性回归"), ("PySpark线性回归应用",)),
    (("最小二乘", "线性回归模型", "决定系数"), ("线性回归模型原理",)),
    (("线性回归",), ("线性回归",)),
    (("混淆矩阵", "准确率", "auc", "f1 score", "precision", "recall", "评价指标"), ("模型评价指标",)),
    (("正则化", "欠拟合", "泛化", "优化方法"), ("模型优化方法",)),
    (("pyspark中主要用于解决分类", "pyspark逻辑回归", "pyspark罗辑回归"), ("PySpark罗辑回归应用",)),
    (("逻辑回归模型", "罗辑回归模型", "sigmoid", "分类模型"), ("罗辑回归模型原理",)),
    (("逻辑回归", "罗辑回归"), ("逻辑回归",)),
    (("pyspark随机森林", "pyspark中随机森林", "pyspark构建随机森林", "pyspark决策树和随机森林"), ("PySpark随机森林应用",)),
    (("随机森林",), ("随机森林方法原理",)),
    (("决策树算法", "叶节点", "连续特征", "决策树"), ("决策树算法原理",)),
    (("k-medoids", "kmedoids", "异常值"), ("k-medoids算法原理",)),
    (("k-means", "kmeans", "簇中心"), ("kmeans算法原理",)),
    (("层次聚类", "dendrogram", "树状图"), ("层次聚类方法原理",)),
    (("轮廓系数", "聚类评价", "聚类分析", "无监督学习", "聚类"), ("聚类",)),
    (("pyspark聚类",), ("PySpark聚类应用",)),
    (("潜在因子", "als"), ("基于潜在因子的推荐方法",)),
    (("pyspark推荐", "推荐数据"), ("PySpark推荐应用",)),
    (("协同过滤", "usercf", "itemcf", "推荐算法", "推荐数据", "推荐概念"), ("推荐系统",)),
    (("数值特征向量", "tf-idf", "word2vec", "词袋", "文本向量"), ("文本向量表示",)),
    (("stop words", "停用词", "文本处理", "自然语言", "nlp"), ("PySpark文本处理应用",)),
    (("spark",), ("Spark",)),
)


def normalize_binding_text(value: object) -> str:
    """
    规整用于匹配的文本。
    :param value: 原始标题、题干或知识点名称。
    :return: 去除标点空白后的统一小写文本。
    """
    normalized = NORMALIZE_PATTERN.sub("", str(value or "").lower())
    for old_text, new_text in TYPO_REPLACEMENTS:
        normalized = normalized.replace(old_text, new_text)
    return normalized
