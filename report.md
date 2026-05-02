# 🌸 屎山代码分析报告 🌸

## 📑 目录

- [糟糕指数](#overall-score)
- [评分指标详情](#metrics-details)
- [最屎代码排行榜](#problem-files)
- [诊断结论](#conclusion)

![Score](https://img.shields.io/badge/Score-90%25-brightgreen)

## 糟糕指数 {#overall-score}

| 指标摘要 | 评分 |
|------|-------|
| **糟糕指数** | **89.56/100** |
| 屎山等级 | 🌸 偶有异味 |

> 清新宜人，初闻像早晨的露珠

### 📊 统计信息

| 指标 | 数值 |
|--------|-------|
| 总文件数 | 471 |
| 已跳过 | 85373 |
| 耗时 | 14252ms |

### 📋 项目概览

| 指标 | 数值 |
|--------|-------|
| 总代码行数 | 57513 |
| 总注释行数 | 3521 |
| 整体注释比例 | 6.1% |
| 平均文件大小 | 149 行 |
| 最大文件 | `frontend\scripts\browser-audit.mjs` (880) |

#### 语言分布

| 语言 | 文件数 |
|:-----|------:|
| Python | 400 |
| TypeScript | 49 |
| JavaScript | 22 |

## 评分指标详情 {#metrics-details}

| 指标摘要 | 评分 | Min | Max | Median | 状态 |
|:-----|------:|------:|------:|------:|:------:|
| 循环复杂度 | 5.13% | 0.0% | 64.5% | 0.0% | ✓✓ |
| 认知复杂度 | 6.40% | 0.0% | 55.7% | 0.0% | ✓✓ |
| 嵌套深度 | 0.42% | 0.0% | 20.0% | 0.0% | ✓✓ |
| 函数长度 | 5.43% | 0.0% | 75.9% | 0.0% | ✓✓ |
| 文件长度 | 0.56% | 0.0% | 48.2% | 0.0% | ✓✓ |
| 参数数量 | 7.16% | 0.0% | 98.5% | 0.0% | ✓✓ |
| 代码重复 | 3.20% | 0.0% | 94.2% | 0.0% | ✓✓ |
| 结构分析 | 0.98% | 0.0% | 16.0% | 0.0% | ✓✓ |
| 错误处理 | 17.96% | 0.0% | 98.8% | 0.0% | ✓✓ |
| 注释比例 | 78.10% | 0.0% | 100.0% | 100.0% | ! |
| 命名规范 | 16.63% | 0.0% | 100.0% | 0.0% | ✓✓ |

## 最屎代码排行榜 {#problem-files}

### 1. backend\knowledge\teacher_resource_views.py

**糟糕指数: 23.51**

> 行数: 284 总计, 248 代码, 0 注释 | 函数: 6 | 类: 0

**问题**: 🔄 复杂度问题: 6, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `resource_update` | L157-226 | 70 | 24 | 2 | 2 | ✓ |
| `resource_list` | L31-83 | 53 | 18 | 3 | 1 | ✓ |
| `resource_create` | L88-152 | 65 | 18 | 2 | 1 | ✓ |
| `resource_upload` | L245-266 | 22 | 4 | 1 | 1 | ✓ |
| `resource_link_knowledge` | L271-283 | 13 | 3 | 1 | 2 | ✓ |
| `resource_delete` | L231-240 | 10 | 2 | 1 | 2 | ✓ |

**全部问题 (10)**

- 🔄 `resource_list()` L31: 复杂度: 18
- 🔄 `resource_create()` L88: 复杂度: 18
- 🔄 `resource_update()` L157: 复杂度: 24
- 🔄 `resource_list()` L31: 认知复杂度: 24
- 🔄 `resource_create()` L88: 认知复杂度: 22
- 🔄 `resource_update()` L157: 认知复杂度: 28
- 📏 `resource_list()` L31: 53 代码量
- 📏 `resource_create()` L88: 65 代码量
- 📏 `resource_update()` L157: 70 代码量
- 🏗️ `resource_list()` L31: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 11.5, 最大: 24
- 认知复杂度: 平均: 14.8, 最大: 28
- 嵌套深度: 平均: 1.7, 最大: 3
- 函数长度: 平均: 38.8 行, 最大: 70 行
- 文件长度: 248 代码量 (284 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 1 个结构问题
- 错误处理: 1/26 个错误被忽略 (3.8%)
- 注释比例: 0.0% (0/248)
- 命名规范: 无命名违规

### 2. backend\users\admin_user_management_views.py

**糟糕指数: 23.47**

> 行数: 327 总计, 282 代码, 0 注释 | 函数: 12 | 类: 0

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 1, 📋 重复问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `admin_user_import` | L229-282 | 54 | 21 | 3 | 1 | ✓ |
| `admin_user_update` | L120-141 | 22 | 9 | 2 | 2 | ✓ |
| `admin_user_export` | L287-311 | 25 | 9 | 1 | 1 | ✓ |
| `admin_user_list` | L25-66 | 42 | 8 | 1 | 1 | ✓ |
| `admin_user_detail` | L71-90 | 20 | 8 | 1 | 2 | ✓ |
| `admin_user_create` | L95-115 | 21 | 5 | 1 | 1 | ✓ |
| `admin_user_reset_password` | L162-183 | 22 | 4 | 1 | 2 | ✓ |
| `admin_user_delete` | L146-157 | 12 | 3 | 1 | 2 | ✓ |
| `admin_user_disable` | L188-198 | 11 | 3 | 1 | 2 | ✓ |
| `admin_user_enable` | L203-211 | 9 | 2 | 1 | 2 | ✓ |
| `admin_user_batch_delete` | L216-224 | 9 | 2 | 1 | 1 | ✓ |
| `admin_user_template` | L316-326 | 11 | 1 | 0 | 1 | ✓ |

**全部问题 (11)**

- 🔄 `admin_user_import()` L229: 复杂度: 21
- 🔄 `admin_user_update()` L120: 认知复杂度: 13
- 🔄 `admin_user_import()` L229: 认知复杂度: 27
- 📏 `admin_user_import()` L229: 54 代码量
- 📋 `admin_user_delete()` L146: 重复模式: admin_user_delete, admin_user_disable
- 📋 `admin_user_enable()` L203: 重复模式: admin_user_enable, admin_user_batch_delete
- 🏗️ `admin_user_import()` L229: 中等嵌套: 3
- ❌ L156: 未处理的易出错调用
- ❌ L223: 忽略了错误返回值
- ❌ L296: 未处理的易出错调用
- ❌ L321: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 21
- 认知复杂度: 平均: 8.6, 最大: 27
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 21.5 行, 最大: 54 行
- 文件长度: 282 代码量 (327 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 16.7% 重复 (2/12)
- 结构分析: 1 个结构问题
- 错误处理: 4/30 个错误被忽略 (13.3%)
- 注释比例: 0.0% (0/282)
- 命名规范: 无命名违规

### 3. backend\users\auth_views.py

**糟糕指数: 23.08**

> 行数: 424 总计, 337 代码, 9 注释 | 函数: 10 | 类: 1

**问题**: 🔄 复杂度问题: 7, ⚠️ 其他问题: 4, 🏗️ 结构问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `update_userinfo` | L266-331 | 66 | 22 | 4 | 1 | ✓ |
| `userinfo` | L170-261 | 92 | 17 | 3 | 1 | ✓ |
| `register` | L55-125 | 71 | 13 | 2 | 1 | ✓ |
| `login` | L131-165 | 35 | 6 | 1 | 1 | ✓ |
| `change_password` | L367-392 | 26 | 5 | 1 | 1 | ✓ |
| `_get_avatar_url` | L37-49 | 13 | 3 | 1 | 1 | ✓ |
| `token_refresh` | L337-362 | 26 | 3 | 1 | 1 | ✓ |
| `logout` | L397-412 | 16 | 3 | 2 | 1 | ✓ |
| `_get_authenticated_user` | L28-34 | 7 | 1 | 0 | 1 | ✓ |
| `health` | L418-423 | 6 | 1 | 0 | 1 | ✓ |

**全部问题 (14)**

- 🔄 `register()` L55: 复杂度: 13
- 🔄 `userinfo()` L170: 复杂度: 17
- 🔄 `update_userinfo()` L266: 复杂度: 22
- 🔄 `register()` L55: 认知复杂度: 17
- 🔄 `userinfo()` L170: 认知复杂度: 23
- 🔄 `update_userinfo()` L266: 认知复杂度: 30
- 🔄 `update_userinfo()` L266: 嵌套深度: 4
- 📏 `register()` L55: 71 代码量
- 📏 `userinfo()` L170: 92 代码量
- 📏 `update_userinfo()` L266: 66 代码量
- 🏗️ `userinfo()` L170: 中等嵌套: 3
- 🏗️ `update_userinfo()` L266: 中等嵌套: 4
- 🏷️ `_get_authenticated_user()` L28: "_get_authenticated_user" - snake_case
- 🏷️ `_get_avatar_url()` L37: "_get_avatar_url" - snake_case

**详情**:
- 循环复杂度: 平均: 7.4, 最大: 22
- 认知复杂度: 平均: 10.4, 最大: 30
- 嵌套深度: 平均: 1.5, 最大: 4
- 函数长度: 平均: 35.8 行, 最大: 92 行
- 文件长度: 337 代码量 (424 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 2 个结构问题
- 错误处理: 0/12 个错误被忽略 (0.0%)
- 注释比例: 2.7% (9/337)
- 命名规范: 发现 2 个违规

### 4. backend\courses\teacher_course_views.py

**糟糕指数: 22.79**

> 行数: 266 总计, 236 代码, 0 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 5, ⚠️ 其他问题: 1, 📋 重复问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `course_create` | L54-118 | 65 | 18 | 4 | 1 | ✓ |
| `course_update` | L123-156 | 34 | 12 | 2 | 2 | ✓ |
| `teacher_course_cover_upload` | L183-205 | 23 | 8 | 2 | 2 | ✓ |
| `update_course_settings` | L242-265 | 24 | 8 | 1 | 2 | ✓ |
| `course_search` | L23-49 | 27 | 5 | 1 | 1 | ✓ |
| `course_delete` | L169-178 | 10 | 5 | 1 | 2 | ✓ |
| `get_course_settings` | L225-237 | 13 | 5 | 1 | 2 | ✓ |
| `teacher_course_statistics` | L210-220 | 11 | 4 | 1 | 2 | ✓ |
| `my_created_courses` | L161-164 | 4 | 1 | 0 | 1 | ✓ |

**全部问题 (11)**

- 🔄 `course_create()` L54: 复杂度: 18
- 🔄 `course_update()` L123: 复杂度: 12
- 🔄 `course_create()` L54: 认知复杂度: 26
- 🔄 `course_update()` L123: 认知复杂度: 16
- 🔄 `course_create()` L54: 嵌套深度: 4
- 📏 `course_create()` L54: 65 代码量
- 📋 `teacher_course_statistics()` L210: 重复模式: teacher_course_statistics, get_course_settings
- 🏗️ `course_create()` L54: 中等嵌套: 4
- ❌ L177: 未处理的易出错调用
- ❌ L199: 未处理的易出错调用
- ❌ L201: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.3, 最大: 18
- 认知复杂度: 平均: 10.2, 最大: 26
- 嵌套深度: 平均: 1.4, 最大: 4
- 函数长度: 平均: 23.4 行, 最大: 65 行
- 文件长度: 236 代码量 (266 总计)
- 参数数量: 平均: 1.7, 最大: 2
- 代码重复: 11.1% 重复 (1/9)
- 结构分析: 1 个结构问题
- 错误处理: 3/18 个错误被忽略 (16.7%)
- 注释比例: 0.0% (0/236)
- 命名规范: 无命名违规

### 5. backend\ai_services\services\student_graph_rag_service.py

**糟糕指数: 22.17**

> 行数: 495 总计, 432 代码, 1 注释 | 函数: 13 | 类: 2

**问题**: 🔄 复杂度问题: 6, ⚠️ 其他问题: 4, 🏗️ 结构问题: 3, ❌ 错误处理问题: 19, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ask` | L379-491 | 113 | 14 | 3 | 5 | ✓ |
| `search_points` | L271-377 | 107 | 13 | 3 | 5 | ✓ |
| `_match_points_by_query_text` | L81-120 | 40 | 9 | 2 | 4 | ✓ |
| `_extract_matched_point_ids` | L160-183 | 24 | 9 | 3 | 2 | ✓ |
| `_extract_first_search_point_id` | L193-209 | 17 | 8 | 1 | 2 | ✓ |
| `_build_search_item` | L235-269 | 35 | 7 | 2 | 3 | ✓ |
| `_build_graph_answer_payload` | L211-233 | 23 | 6 | 0 | 4 | ✓ |
| `_resolve_point_from_ids` | L122-146 | 25 | 4 | 2 | 3 | ✓ |
| `_has_course_rag_result` | L185-191 | 7 | 3 | 1 | 2 | ✓ |
| `_extract_text_list` | L148-158 | 11 | 2 | 1 | 3 | ✓ |
| `to_dict` | L52-63 | 12 | 1 | 0 | 1 | ✓ |
| `_normalize_match_text` | L69-73 | 5 | 1 | 0 | 2 | ✓ |
| `_is_graph_structure_question` | L75-79 | 5 | 1 | 0 | 2 | ✓ |

**全部问题 (40)**

- 🔄 `search_points()` L271: 复杂度: 13
- 🔄 `ask()` L379: 复杂度: 14
- 🔄 `_match_points_by_query_text()` L81: 认知复杂度: 13
- 🔄 `_extract_matched_point_ids()` L160: 认知复杂度: 15
- 🔄 `search_points()` L271: 认知复杂度: 19
- 🔄 `ask()` L379: 认知复杂度: 20
- 📏 `search_points()` L271: 107 代码量
- 📏 `ask()` L379: 113 代码量
- 🏗️ `_extract_matched_point_ids()` L160: 中等嵌套: 3
- 🏗️ `search_points()` L271: 中等嵌套: 3
- 🏗️ `ask()` L379: 中等嵌套: 3
- ❌ L226: 未处理的易出错调用
- ❌ L227: 未处理的易出错调用
- ❌ L228: 未处理的易出错调用
- ❌ L251: 未处理的易出错调用
- ❌ L252: 未处理的易出错调用
- ❌ L253: 未处理的易出错调用
- ❌ L256: 未处理的易出错调用
- ❌ L257: 未处理的易出错调用
- ❌ L258: 未处理的易出错调用
- ❌ L297: 未处理的易出错调用
- ❌ L299: 未处理的易出错调用
- ❌ L319: 未处理的易出错调用
- ❌ L324: 未处理的易出错调用
- ❌ L325: 未处理的易出错调用
- ❌ L327: 未处理的易出错调用
- ❌ L331: 未处理的易出错调用
- ❌ L332: 未处理的易出错调用
- ❌ L334: 未处理的易出错调用
- ❌ L489: 未处理的易出错调用
- 🏷️ `_normalize_match_text()` L69: "_normalize_match_text" - snake_case
- 🏷️ `_is_graph_structure_question()` L75: "_is_graph_structure_question" - snake_case
- 🏷️ `_match_points_by_query_text()` L81: "_match_points_by_query_text" - snake_case
- 🏷️ `_resolve_point_from_ids()` L122: "_resolve_point_from_ids" - snake_case
- 🏷️ `_extract_text_list()` L148: "_extract_text_list" - snake_case
- 🏷️ `_extract_matched_point_ids()` L160: "_extract_matched_point_ids" - snake_case
- 🏷️ `_has_course_rag_result()` L185: "_has_course_rag_result" - snake_case
- 🏷️ `_extract_first_search_point_id()` L193: "_extract_first_search_point_id" - snake_case
- 🏷️ `_build_graph_answer_payload()` L211: "_build_graph_answer_payload" - snake_case
- 🏷️ `_build_search_item()` L235: "_build_search_item" - snake_case

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 14
- 认知复杂度: 平均: 8.8, 最大: 20
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 32.6 行, 最大: 113 行
- 文件长度: 432 代码量 (495 总计)
- 参数数量: 平均: 2.9, 最大: 5
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 3 个结构问题
- 错误处理: 19/28 个错误被忽略 (67.9%)
- 注释比例: 0.2% (1/432)
- 命名规范: 发现 10 个违规

### 6. backend\learning\student_rag_views.py

**糟糕指数: 21.19**

> 行数: 110 总计, 88 代码, 6 注释 | 函数: 1 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_ai_resources` | L21-109 | 89 | 14 | 1 | 2 | ✓ |

**全部问题 (7)**

- 🔄 `get_ai_resources()` L21: 复杂度: 14
- 🔄 `get_ai_resources()` L21: 认知复杂度: 16
- 📏 `get_ai_resources()` L21: 89 代码量
- ❌ L48: 未处理的易出错调用
- ❌ L49: 未处理的易出错调用
- ❌ L106: 未处理的易出错调用
- ❌ L107: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 14.0, 最大: 14
- 认知复杂度: 平均: 16.0, 最大: 16
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 89.0 行, 最大: 89 行
- 文件长度: 88 代码量 (110 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 4/5 个错误被忽略 (80.0%)
- 注释比例: 6.8% (6/88)
- 命名规范: 无命名违规

### 7. backend\tools\dkt_training.py

**糟糕指数: 21.03**

> 行数: 227 总计, 197 代码, 2 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 4, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `train_dkt` | L116-177 | 62 | 14 | 2 | 12 | ✓ |
| `dkt_status` | L180-214 | 35 | 8 | 2 | 0 | ✓ |
| `train_dkt_v2` | L79-113 | 35 | 5 | 1 | 12 | ✓ |
| `train_public_dataset_baseline` | L43-76 | 34 | 3 | 1 | 7 | ✓ |

**全部问题 (6)**

- 🔄 `train_dkt()` L116: 复杂度: 14
- 🔄 `train_dkt()` L116: 认知复杂度: 18
- 📏 `train_dkt()` L116: 62 代码量
- 📏 `train_public_dataset_baseline()` L43: 7 参数数量
- 📏 `train_dkt_v2()` L79: 12 参数数量
- 📏 `train_dkt()` L116: 12 参数数量

**详情**:
- 循环复杂度: 平均: 7.5, 最大: 14
- 认知复杂度: 平均: 10.5, 最大: 18
- 嵌套深度: 平均: 1.5, 最大: 2
- 函数长度: 平均: 41.5 行, 最大: 62 行
- 文件长度: 197 代码量 (227 总计)
- 参数数量: 平均: 7.8, 最大: 12
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 1.0% (2/197)
- 命名规范: 无命名违规

### 8. backend\tools\exam_sets.py

**糟糕指数: 20.78**

> 行数: 328 总计, 270 代码, 2 注释 | 函数: 10 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 2, 🏗️ 结构问题: 2, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_exam_sets` | L221-327 | 107 | 16 | 3 | 4 | ✓ |
| `_extract_row_content` | L67-84 | 18 | 9 | 2 | 2 | ✓ |
| `_load_matched_questions` | L136-180 | 45 | 8 | 3 | 5 | ✓ |
| `_bind_question_knowledge_points` | L109-133 | 25 | 5 | 2 | 4 | ✓ |
| `_match_question` | L196-218 | 23 | 5 | 2 | 2 | ✓ |
| `_build_exam_title` | L55-64 | 10 | 4 | 0 | 1 | ✓ |
| `_collect_question_knowledge_point_names` | L183-193 | 11 | 3 | 2 | 1 | ✓ |
| `_resolve_homework_path` | L35-43 | 9 | 2 | 1 | 1 | ✓ |
| `_resolve_knowledge_point` | L87-106 | 20 | 2 | 1 | 3 | ✓ |
| `_collect_excel_files` | L46-52 | 7 | 1 | 0 | 1 | ✓ |

**全部问题 (18)**

- 🔄 `import_exam_sets()` L221: 复杂度: 16
- 🔄 `_extract_row_content()` L67: 认知复杂度: 13
- 🔄 `_load_matched_questions()` L136: 认知复杂度: 14
- 🔄 `import_exam_sets()` L221: 认知复杂度: 22
- 📏 `import_exam_sets()` L221: 107 代码量
- 🏗️ `_load_matched_questions()` L136: 中等嵌套: 3
- 🏗️ `import_exam_sets()` L221: 中等嵌套: 3
- ❌ L174: 未处理的易出错调用
- ❌ L312: 未处理的易出错调用
- 🏷️ `_resolve_homework_path()` L35: "_resolve_homework_path" - snake_case
- 🏷️ `_collect_excel_files()` L46: "_collect_excel_files" - snake_case
- 🏷️ `_build_exam_title()` L55: "_build_exam_title" - snake_case
- 🏷️ `_extract_row_content()` L67: "_extract_row_content" - snake_case
- 🏷️ `_resolve_knowledge_point()` L87: "_resolve_knowledge_point" - snake_case
- 🏷️ `_bind_question_knowledge_points()` L109: "_bind_question_knowledge_points" - snake_case
- 🏷️ `_load_matched_questions()` L136: "_load_matched_questions" - snake_case
- 🏷️ `_collect_question_knowledge_point_names()` L183: "_collect_question_knowledge_point_names" - snake_case
- 🏷️ `_match_question()` L196: "_match_question" - snake_case

**详情**:
- 循环复杂度: 平均: 5.5, 最大: 16
- 认知复杂度: 平均: 8.7, 最大: 22
- 嵌套深度: 平均: 1.6, 最大: 3
- 函数长度: 平均: 27.5 行, 最大: 107 行
- 文件长度: 270 代码量 (328 总计)
- 参数数量: 平均: 2.4, 最大: 5
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 2 个结构问题
- 错误处理: 2/8 个错误被忽略 (25.0%)
- 注释比例: 0.7% (2/270)
- 命名规范: 发现 9 个违规

### 9. backend\common\defense_demo_stage.py

**糟糕指数: 20.76**

> 行数: 285 总计, 269 代码, 0 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 3, ❌ 错误处理问题: 9, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_ensure_warmup_stage_submission_and_feedback` | L56-178 | 123 | 12 | 2 | 4 | ✓ |
| `_build_demo_stage_test_result` | L181-284 | 104 | 7 | 1 | 4 | ✓ |
| `_build_stage_feedback_payload` | L26-53 | 28 | 1 | 0 | 1 | ✓ |

**全部问题 (16)**

- 🔄 `_ensure_warmup_stage_submission_and_feedback()` L56: 复杂度: 12
- 🔄 `_ensure_warmup_stage_submission_and_feedback()` L56: 认知复杂度: 16
- 📏 `_ensure_warmup_stage_submission_and_feedback()` L56: 123 代码量
- 📏 `_build_demo_stage_test_result()` L181: 104 代码量
- ❌ L168: 未处理的易出错调用
- ❌ L169: 未处理的易出错调用
- ❌ L172: 未处理的易出错调用
- ❌ L173: 未处理的易出错调用
- ❌ L174: 未处理的易出错调用
- ❌ L175: 未处理的易出错调用
- ❌ L257: 未处理的易出错调用
- ❌ L258: 未处理的易出错调用
- ❌ L280: 未处理的易出错调用
- 🏷️ `_build_stage_feedback_payload()` L26: "_build_stage_feedback_payload" - snake_case
- 🏷️ `_ensure_warmup_stage_submission_and_feedback()` L56: "_ensure_warmup_stage_submission_and_feedback" - snake_case
- 🏷️ `_build_demo_stage_test_result()` L181: "_build_demo_stage_test_result" - snake_case

**详情**:
- 循环复杂度: 平均: 6.7, 最大: 12
- 认知复杂度: 平均: 8.7, 最大: 16
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 85.0 行, 最大: 123 行
- 文件长度: 269 代码量 (285 总计)
- 参数数量: 平均: 3.0, 最大: 4
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 9/14 个错误被忽略 (64.3%)
- 注释比例: 0.0% (0/269)
- 命名规范: 发现 3 个违规

### 10. backend\tools\dkt_synthetic_support.py

**糟糕指数: 20.73**

> 行数: 385 总计, 348 代码, 2 注释 | 函数: 14 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 8, 🏗️ 结构问题: 1, ❌ 错误处理问题: 6, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_sampling_weights` | L209-247 | 39 | 15 | 2 | 8 | ✓ |
| `choose_focus_kp` | L250-277 | 28 | 8 | 2 | 6 | ✓ |
| `compute_interaction_outcome` | L280-324 | 45 | 7 | 1 | 10 | ✓ |
| `build_children_map` | L32-42 | 11 | 5 | 3 | 2 | ✓ |
| `calculate_kp_depth` | L45-75 | 31 | 5 | 1 | 5 | ✓ |
| `apply_session_gap_decay` | L186-206 | 21 | 5 | 2 | 8 | ✓ |
| `update_mastery_after_interaction` | L327-364 | 38 | 5 | 2 | 9 | ✓ |
| `compute_kp_difficulty` | L78-123 | 46 | 4 | 1 | 7 | ✓ |
| `build_kp_profile` | L126-166 | 41 | 3 | 0 | 6 | ✓ |
| `sample_sequence_length` | L367-384 | 18 | 3 | 1 | 4 | ✓ |
| `mean_or_default` | L24-29 | 6 | 2 | 1 | 2 | ✓ |
| `initialize_mastery_levels` | L169-183 | 15 | 2 | 1 | 3 | ✓ |
| `clamp_value` | L13-15 | 3 | 1 | 0 | 3 | ✓ |
| `sigmoid` | L18-21 | 4 | 1 | 0 | 1 | ✓ |

**全部问题 (16)**

- 🔄 `build_sampling_weights()` L209: 复杂度: 15
- 🔄 `build_sampling_weights()` L209: 认知复杂度: 19
- 📏 `compute_kp_difficulty()` L78: 7 参数数量
- 📏 `build_kp_profile()` L126: 6 参数数量
- 📏 `apply_session_gap_decay()` L186: 8 参数数量
- 📏 `build_sampling_weights()` L209: 8 参数数量
- 📏 `choose_focus_kp()` L250: 6 参数数量
- 📏 `compute_interaction_outcome()` L280: 10 参数数量
- 📏 `update_mastery_after_interaction()` L327: 9 参数数量
- 🏗️ `build_children_map()` L32: 中等嵌套: 3
- ❌ L155: 未处理的易出错调用
- ❌ L160: 未处理的易出错调用
- ❌ L162: 未处理的易出错调用
- ❌ L225: 未处理的易出错调用
- ❌ L264: 未处理的易出错调用
- ❌ L296: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 15
- 认知复杂度: 平均: 7.1, 最大: 19
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 24.7 行, 最大: 46 行
- 文件长度: 348 代码量 (385 总计)
- 参数数量: 平均: 5.3, 最大: 10
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 1 个结构问题
- 错误处理: 6/25 个错误被忽略 (24.0%)
- 注释比例: 0.6% (2/348)
- 命名规范: 无命名违规

### 11. backend\tools\dkt_sequences.py

**糟糕指数: 20.33**

> 行数: 248 总计, 203 代码, 2 注释 | 函数: 13 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 2, 🏗️ 结构问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_load_csv_sequences` | L138-175 | 38 | 15 | 2 | 1 | ✓ |
| `_build_onehot_batch` | L13-28 | 16 | 7 | 3 | 5 | ✓ |
| `_evaluate_dkt_auc` | L83-111 | 29 | 7 | 3 | 8 | ✓ |
| `_chunk_sequences` | L185-197 | 13 | 4 | 3 | 2 | ✓ |
| `_build_next_step_targets` | L31-52 | 22 | 3 | 2 | 3 | ✓ |
| `_gather_next_step_outputs` | L55-80 | 26 | 3 | 1 | 3 | ✓ |
| `_load_three_line_sequences` | L114-127 | 14 | 3 | 1 | 1 | ✓ |
| `_find_first_matching_key` | L130-135 | 6 | 3 | 2 | 2 | ✓ |
| `_build_batch_loss` | L215-222 | 8 | 3 | 1 | 3 | ✓ |
| `_train_dkt_epoch` | L225-247 | 23 | 3 | 2 | 9 | ✓ |
| `_load_sequences_from_path` | L178-182 | 5 | 2 | 1 | 1 | ✓ |
| `_split_train_test_indices` | L205-212 | 8 | 2 | 1 | 1 | ✓ |
| `_load_chunked_sequences_from_path` | L200-202 | 3 | 1 | 0 | 2 | ✓ |

**全部问题 (19)**

- 🔄 `_load_csv_sequences()` L138: 复杂度: 15
- 🔄 `_build_onehot_batch()` L13: 认知复杂度: 13
- 🔄 `_evaluate_dkt_auc()` L83: 认知复杂度: 13
- 🔄 `_load_csv_sequences()` L138: 认知复杂度: 19
- 📏 `_evaluate_dkt_auc()` L83: 8 参数数量
- 📏 `_train_dkt_epoch()` L225: 9 参数数量
- 🏗️ `_build_onehot_batch()` L13: 中等嵌套: 3
- 🏗️ `_evaluate_dkt_auc()` L83: 中等嵌套: 3
- 🏗️ `_chunk_sequences()` L185: 中等嵌套: 3
- 🏷️ `_build_onehot_batch()` L13: "_build_onehot_batch" - snake_case
- 🏷️ `_build_next_step_targets()` L31: "_build_next_step_targets" - snake_case
- 🏷️ `_gather_next_step_outputs()` L55: "_gather_next_step_outputs" - snake_case
- 🏷️ `_evaluate_dkt_auc()` L83: "_evaluate_dkt_auc" - snake_case
- 🏷️ `_load_three_line_sequences()` L114: "_load_three_line_sequences" - snake_case
- 🏷️ `_find_first_matching_key()` L130: "_find_first_matching_key" - snake_case
- 🏷️ `_load_csv_sequences()` L138: "_load_csv_sequences" - snake_case
- 🏷️ `_load_sequences_from_path()` L178: "_load_sequences_from_path" - snake_case
- 🏷️ `_chunk_sequences()` L185: "_chunk_sequences" - snake_case
- 🏷️ `_load_chunked_sequences_from_path()` L200: "_load_chunked_sequences_from_path" - snake_case

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 15
- 认知复杂度: 平均: 7.7, 最大: 19
- 嵌套深度: 平均: 1.7, 最大: 3
- 函数长度: 平均: 16.2 行, 最大: 38 行
- 文件长度: 203 代码量 (248 总计)
- 参数数量: 平均: 3.2, 最大: 9
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 3 个结构问题
- 错误处理: 0/6 个错误被忽略 (0.0%)
- 注释比例: 1.0% (2/203)
- 命名规范: 发现 13 个违规

### 12. backend\exams\student_exam_views.py

**糟糕指数: 20.30**

> 行数: 109 总计, 95 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `exam_list` | L18-71 | 54 | 17 | 2 | 1 | ✓ |
| `exam_detail` | L76-108 | 33 | 7 | 2 | 2 | ✓ |

**全部问题 (4)**

- 🔄 `exam_list()` L18: 复杂度: 17
- 🔄 `exam_list()` L18: 认知复杂度: 21
- 📏 `exam_list()` L18: 54 代码量
- ❌ L97: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 12.0, 最大: 17
- 认知复杂度: 平均: 16.0, 最大: 21
- 嵌套深度: 平均: 2.0, 最大: 2
- 函数长度: 平均: 43.5 行, 最大: 54 行
- 文件长度: 95 代码量 (109 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 0.0% (0/95)
- 命名规范: 无命名违规

### 13. backend\platform_ai\llm\agent_support.py

**糟糕指数: 20.25**

> 行数: 205 总计, 175 代码, 0 注释 | 函数: 6 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 2, ❌ 错误处理问题: 12, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_course_graphrag_payload` | L93-157 | 65 | 16 | 2 | 4 | ✓ |
| `parse_json_payload` | L17-37 | 21 | 10 | 2 | 1 | ✓ |
| `extract_agent_message_text` | L189-204 | 16 | 9 | 2 | 1 | ✓ |
| `trim_graph_sources` | L40-61 | 22 | 7 | 2 | 2 | ✓ |
| `build_lookup_course_context_payload` | L160-186 | 27 | 7 | 1 | 2 | ✓ |
| `build_point_graphrag_payload` | L64-90 | 27 | 5 | 1 | 2 | ✓ |

**全部问题 (17)**

- 🔄 `build_course_graphrag_payload()` L93: 复杂度: 16
- 🔄 `parse_json_payload()` L17: 认知复杂度: 14
- 🔄 `build_course_graphrag_payload()` L93: 认知复杂度: 20
- 🔄 `extract_agent_message_text()` L189: 认知复杂度: 13
- 📏 `build_course_graphrag_payload()` L93: 65 代码量
- ❌ L51: 未处理的易出错调用
- ❌ L52: 未处理的易出错调用
- ❌ L53: 未处理的易出错调用
- ❌ L54: 未处理的易出错调用
- ❌ L55: 未处理的易出错调用
- ❌ L56: 未处理的易出错调用
- ❌ L83: 未处理的易出错调用
- ❌ L88: 未处理的易出错调用
- ❌ L150: 未处理的易出错调用
- ❌ L153: 未处理的易出错调用
- ❌ L154: 未处理的易出错调用
- ❌ L200: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 9.0, 最大: 16
- 认知复杂度: 平均: 12.3, 最大: 20
- 嵌套深度: 平均: 1.7, 最大: 2
- 函数长度: 平均: 29.7 行, 最大: 65 行
- 文件长度: 175 代码量 (205 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 12/18 个错误被忽略 (66.7%)
- 注释比例: 0.0% (0/175)
- 命名规范: 无命名违规

### 14. backend\tools\resources.py

**糟糕指数: 19.94**

> 行数: 105 总计, 83 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_resources_json` | L13-68 | 56 | 14 | 4 | 4 | ✓ |
| `delete_link_resources` | L71-104 | 34 | 6 | 1 | 2 | ✓ |

**全部问题 (7)**

- 🔄 `import_resources_json()` L13: 复杂度: 14
- 🔄 `import_resources_json()` L13: 认知复杂度: 22
- 🔄 `import_resources_json()` L13: 嵌套深度: 4
- 📏 `import_resources_json()` L13: 56 代码量
- 🏗️ `import_resources_json()` L13: 中等嵌套: 4
- ❌ L62: 未处理的易出错调用
- ❌ L103: 忽略了错误返回值

**详情**:
- 循环复杂度: 平均: 10.0, 最大: 14
- 认知复杂度: 平均: 15.0, 最大: 22
- 嵌套深度: 平均: 2.5, 最大: 4
- 函数长度: 平均: 45.0 行, 最大: 56 行
- 文件长度: 83 代码量 (105 总计)
- 参数数量: 平均: 3.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 1 个结构问题
- 错误处理: 2/12 个错误被忽略 (16.7%)
- 注释比例: 0.0% (0/83)
- 命名规范: 无命名违规

### 15. backend\knowledge\map_views.py

**糟糕指数: 19.75**

> 行数: 384 总计, 342 代码, 0 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 8, ⚠️ 其他问题: 3, 🏗️ 结构问题: 3, ❌ 错误处理问题: 34, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_knowledge_point_detail` | L174-227 | 54 | 12 | 2 | 2 | ✓ |
| `get_knowledge_map` | L62-121 | 60 | 11 | 3 | 1 | ✓ |
| `_build_postgresql_knowledge_map_payload` | L19-57 | 39 | 10 | 0 | 2 | ✓ |
| `_build_resource_payload` | L137-169 | 33 | 10 | 4 | 2 | ✓ |
| `get_knowledge_points_list` | L273-319 | 47 | 10 | 2 | 1 | ✓ |
| `update_knowledge_mastery` | L352-383 | 32 | 10 | 3 | 1 | ✓ |
| `get_knowledge_mastery` | L324-347 | 24 | 7 | 1 | 1 | ✓ |
| `get_knowledge_relations` | L232-268 | 37 | 4 | 1 | 1 | ✓ |
| `_postgresql_point_relations` | L124-134 | 11 | 1 | 0 | 1 | ✓ |

**全部问题 (50)**

- 🔄 `get_knowledge_map()` L62: 复杂度: 11
- 🔄 `get_knowledge_point_detail()` L174: 复杂度: 12
- 🔄 `get_knowledge_map()` L62: 认知复杂度: 17
- 🔄 `_build_resource_payload()` L137: 认知复杂度: 18
- 🔄 `get_knowledge_point_detail()` L174: 认知复杂度: 16
- 🔄 `get_knowledge_points_list()` L273: 认知复杂度: 14
- 🔄 `update_knowledge_mastery()` L352: 认知复杂度: 16
- 🔄 `_build_resource_payload()` L137: 嵌套深度: 4
- 📏 `get_knowledge_map()` L62: 60 代码量
- 📏 `get_knowledge_point_detail()` L174: 54 代码量
- 🏗️ `get_knowledge_map()` L62: 中等嵌套: 3
- 🏗️ `_build_resource_payload()` L137: 中等嵌套: 4
- 🏗️ `update_knowledge_mastery()` L352: 中等嵌套: 3
- ❌ L27: 未处理的易出错调用
- ❌ L54: 未处理的易出错调用
- ❌ L83: 未处理的易出错调用
- ❌ L89: 未处理的易出错调用
- ❌ L90: 未处理的易出错调用
- ❌ L91: 未处理的易出错调用
- ❌ L92: 未处理的易出错调用
- ❌ L93: 未处理的易出错调用
- ❌ L94: 未处理的易出错调用
- ❌ L95: 未处理的易出错调用
- ❌ L96: 未处理的易出错调用
- ❌ L97: 未处理的易出错调用
- ❌ L98: 未处理的易出错调用
- ❌ L99: 未处理的易出错调用
- ❌ L105: 未处理的易出错调用
- ❌ L106: 未处理的易出错调用
- ❌ L107: 未处理的易出错调用
- ❌ L109: 未处理的易出错调用
- ❌ L118: 未处理的易出错调用
- ❌ L224: 未处理的易出错调用
- ❌ L225: 未处理的易出错调用
- ❌ L226: 未处理的易出错调用
- ❌ L242: 未处理的易出错调用
- ❌ L243: 未处理的易出错调用
- ❌ L244: 未处理的易出错调用
- ❌ L245: 未处理的易出错调用
- ❌ L246: 未处理的易出错调用
- ❌ L247: 未处理的易出错调用
- ❌ L288: 未处理的易出错调用
- ❌ L289: 未处理的易出错调用
- ❌ L290: 未处理的易出错调用
- ❌ L291: 未处理的易出错调用
- ❌ L292: 未处理的易出错调用
- ❌ L293: 未处理的易出错调用
- 🏷️ `_build_postgresql_knowledge_map_payload()` L19: "_build_postgresql_knowledge_map_payload" - snake_case
- 🏷️ `_postgresql_point_relations()` L124: "_postgresql_point_relations" - snake_case
- 🏷️ `_build_resource_payload()` L137: "_build_resource_payload" - snake_case

**详情**:
- 循环复杂度: 平均: 8.3, 最大: 12
- 认知复杂度: 平均: 11.9, 最大: 18
- 嵌套深度: 平均: 1.8, 最大: 4
- 函数长度: 平均: 37.4 行, 最大: 60 行
- 文件长度: 342 代码量 (384 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 3 个结构问题
- 错误处理: 34/43 个错误被忽略 (79.1%)
- 注释比例: 0.0% (0/342)
- 命名规范: 发现 3 个违规

### 16. backend\ai_services\services\path_generation_support.py

**糟糕指数: 19.73**

> 行数: 356 总计, 314 代码, 0 注释 | 函数: 8 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 5, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_linked_pending_batch` | L43-91 | 49 | 13 | 3 | 5 | ✓ |
| `sync_course_mastery` | L94-169 | 76 | 8 | 2 | 3 | ✓ |
| `_build_pending_nodes` | L206-261 | 56 | 6 | 1 | 8 | ✓ |
| `attach_resources_to_created_nodes` | L345-355 | 11 | 4 | 2 | 2 | ✓ |
| `_build_test_node` | L264-291 | 28 | 3 | 1 | 3 | ✓ |
| `_build_completed_nodes` | L172-203 | 32 | 2 | 1 | 4 | ✓ |
| `build_generation_plan` | L294-342 | 49 | 2 | 1 | 8 | ✓ |
| `load_course_point_ids` | L32-40 | 9 | 1 | 0 | 1 | ✓ |

**全部问题 (11)**

- 🔄 `build_linked_pending_batch()` L43: 复杂度: 13
- 🔄 `build_linked_pending_batch()` L43: 认知复杂度: 19
- 📏 `sync_course_mastery()` L94: 76 代码量
- 📏 `_build_pending_nodes()` L206: 56 代码量
- 📏 `_build_pending_nodes()` L206: 8 参数数量
- 📏 `build_generation_plan()` L294: 8 参数数量
- 🏗️ `build_linked_pending_batch()` L43: 中等嵌套: 3
- ❌ L60: 未处理的易出错调用
- 🏷️ `_build_completed_nodes()` L172: "_build_completed_nodes" - snake_case
- 🏷️ `_build_pending_nodes()` L206: "_build_pending_nodes" - snake_case
- 🏷️ `_build_test_node()` L264: "_build_test_node" - snake_case

**详情**:
- 循环复杂度: 平均: 4.9, 最大: 13
- 认知复杂度: 平均: 7.6, 最大: 19
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 38.8 行, 最大: 76 行
- 文件长度: 314 代码量 (356 总计)
- 参数数量: 平均: 4.3, 最大: 8
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 0.0% (0/314)
- 命名规范: 发现 3 个违规

### 17. backend\ai_services\services\dkt_inference.py

**糟糕指数: 19.71**

> 行数: 301 总计, 264 代码, 0 注释 | 函数: 9 | 类: 1

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `load_model` | L54-134 | 81 | 16 | 2 | 5 | ✓ |
| `_predict_legacy` | L146-198 | 53 | 10 | 3 | 3 | ✓ |
| `auto_load_model` | L279-300 | 22 | 8 | 2 | 0 | ✓ |
| `_predict_public_slot_adapter` | L200-243 | 44 | 5 | 2 | 4 | ✓ |
| `predict` | L245-258 | 14 | 4 | 2 | 4 | ✓ |
| `_build_public_slot_bundle` | L136-144 | 9 | 2 | 1 | 2 | ✓ |
| `__init__` | L36-47 | 12 | 1 | 0 | 1 | ✗ |
| `is_loaded` | L50-52 | 3 | 1 | 0 | 1 | ✓ |
| `get_info` | L260-273 | 14 | 1 | 0 | 1 | ✓ |

**全部问题 (14)**

- 🔄 `load_model()` L54: 复杂度: 16
- 🔄 `load_model()` L54: 认知复杂度: 20
- 🔄 `_predict_legacy()` L146: 认知复杂度: 16
- 📏 `load_model()` L54: 81 代码量
- 📏 `_predict_legacy()` L146: 53 代码量
- 🏗️ `_predict_legacy()` L146: 中等嵌套: 3
- ❌ L87: 未处理的易出错调用
- ❌ L88: 未处理的易出错调用
- ❌ L271: 未处理的易出错调用
- ❌ L272: 未处理的易出错调用
- 🏷️ `__init__()` L36: "__init__" - snake_case
- 🏷️ `_build_public_slot_bundle()` L136: "_build_public_slot_bundle" - snake_case
- 🏷️ `_predict_legacy()` L146: "_predict_legacy" - snake_case
- 🏷️ `_predict_public_slot_adapter()` L200: "_predict_public_slot_adapter" - snake_case

**详情**:
- 循环复杂度: 平均: 5.3, 最大: 16
- 认知复杂度: 平均: 8.0, 最大: 20
- 嵌套深度: 平均: 1.3, 最大: 3
- 函数长度: 平均: 28.0 行, 最大: 81 行
- 文件长度: 264 代码量 (301 总计)
- 参数数量: 平均: 2.3, 最大: 5
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 4/8 个错误被忽略 (50.0%)
- 注释比例: 0.0% (0/264)
- 命名规范: 发现 4 个违规

### 18. backend\learning\node_detail_support.py

**糟糕指数: 19.50**

> 行数: 265 总计, 236 代码, 0 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 2, 📋 重复问题: 1, 🏗️ 结构问题: 2, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `refresh_node_exam_mastery` | L182-264 | 83 | 13 | 3 | 7 | ✓ |
| `build_node_detail_payload` | L49-72 | 24 | 6 | 1 | 3 | ✓ |
| `update_node_exam_progress` | L128-145 | 18 | 6 | 2 | 4 | ✓ |
| `persist_node_exam_histories` | L148-179 | 32 | 5 | 2 | 5 | ✓ |
| `ensure_progress_baseline` | L31-46 | 16 | 4 | 3 | 2 | ✓ |
| `mark_node_resource_completed` | L75-91 | 17 | 3 | 1 | 2 | ✓ |
| `build_node_exam_context` | L94-115 | 22 | 3 | 0 | 2 | ✓ |
| `load_node_for_user` | L23-28 | 6 | 2 | 1 | 3 | ✓ |
| `upsert_node_exam_submission` | L118-125 | 8 | 1 | 0 | 5 | ✓ |

**全部问题 (8)**

- 🔄 `refresh_node_exam_mastery()` L182: 复杂度: 13
- 🔄 `refresh_node_exam_mastery()` L182: 认知复杂度: 19
- 📏 `refresh_node_exam_mastery()` L182: 83 代码量
- 📏 `refresh_node_exam_mastery()` L182: 7 参数数量
- 📋 `load_node_for_user()` L23: 重复模式: load_node_for_user, mark_node_resource_completed
- 🏗️ `ensure_progress_baseline()` L31: 中等嵌套: 3
- 🏗️ `refresh_node_exam_mastery()` L182: 中等嵌套: 3
- ❌ L160: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 13
- 认知复杂度: 平均: 7.7, 最大: 19
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 25.1 行, 最大: 83 行
- 文件长度: 236 代码量 (265 总计)
- 参数数量: 平均: 3.7, 最大: 7
- 代码重复: 11.1% 重复 (1/9)
- 结构分析: 2 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 0.0% (0/236)
- 命名规范: 无命名违规

### 19. backend\tools\cli_menu.py

**糟糕指数: 19.26**

> 行数: 344 总计, 310 代码, 2 注释 | 函数: 11 | 类: 0

**问题**: 🔄 复杂度问题: 6, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_handle_kt_menu_choice` | L227-274 | 48 | 19 | 1 | 1 | ✓ |
| `_handle_data_menu_choice` | L117-161 | 45 | 15 | 2 | 1 | ✓ |
| `_handle_graphrag_and_demo_menu_choice` | L277-306 | 30 | 15 | 2 | 1 | ✓ |
| `_handle_neo4j_menu_choice` | L184-204 | 21 | 7 | 1 | 1 | ✓ |
| `_handle_database_menu_choice` | L164-181 | 18 | 6 | 1 | 1 | ✓ |
| `_handle_api_and_service_menu_choice` | L207-224 | 18 | 6 | 1 | 1 | ✓ |
| `_handle_menu_choice` | L319-330 | 12 | 4 | 2 | 1 | ✓ |
| `show_menu` | L333-343 | 11 | 4 | 3 | 0 | ✓ |
| `_render_menu` | L93-100 | 8 | 2 | 1 | 0 | ✓ |
| `_parse_optional_course_id` | L103-106 | 4 | 2 | 0 | 1 | ✓ |
| `_prompt_yes_no` | L109-114 | 6 | 2 | 1 | 2 | ✓ |

**全部问题 (17)**

- 🔄 `_handle_data_menu_choice()` L117: 复杂度: 15
- 🔄 `_handle_kt_menu_choice()` L227: 复杂度: 19
- 🔄 `_handle_graphrag_and_demo_menu_choice()` L277: 复杂度: 15
- 🔄 `_handle_data_menu_choice()` L117: 认知复杂度: 19
- 🔄 `_handle_kt_menu_choice()` L227: 认知复杂度: 21
- 🔄 `_handle_graphrag_and_demo_menu_choice()` L277: 认知复杂度: 19
- 🏗️ `show_menu()` L333: 中等嵌套: 3
- 🏷️ `_render_menu()` L93: "_render_menu" - snake_case
- 🏷️ `_parse_optional_course_id()` L103: "_parse_optional_course_id" - snake_case
- 🏷️ `_prompt_yes_no()` L109: "_prompt_yes_no" - snake_case
- 🏷️ `_handle_data_menu_choice()` L117: "_handle_data_menu_choice" - snake_case
- 🏷️ `_handle_database_menu_choice()` L164: "_handle_database_menu_choice" - snake_case
- 🏷️ `_handle_neo4j_menu_choice()` L184: "_handle_neo4j_menu_choice" - snake_case
- 🏷️ `_handle_api_and_service_menu_choice()` L207: "_handle_api_and_service_menu_choice" - snake_case
- 🏷️ `_handle_kt_menu_choice()` L227: "_handle_kt_menu_choice" - snake_case
- 🏷️ `_handle_graphrag_and_demo_menu_choice()` L277: "_handle_graphrag_and_demo_menu_choice" - snake_case
- 🏷️ `_handle_menu_choice()` L319: "_handle_menu_choice" - snake_case

**详情**:
- 循环复杂度: 平均: 7.5, 最大: 19
- 认知复杂度: 平均: 10.2, 最大: 21
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 20.1 行, 最大: 48 行
- 文件长度: 310 代码量 (344 总计)
- 参数数量: 平均: 0.9, 最大: 2
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.6% (2/310)
- 命名规范: 发现 10 个违规

### 20. backend\tools\api_regression_helpers.py

**糟糕指数: 19.23**

> 行数: 237 总计, 184 代码, 24 注释 | 函数: 7 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 🏷️ 命名问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_exam_answers` | L99-135 | 37 | 16 | 3 | 1 | ✓ |
| `_pick_first_id` | L170-194 | 25 | 7 | 2 | 3 | ✓ |
| `_record` | L29-62 | 34 | 5 | 1 | 6 | ✓ |
| `_blob` | L67-94 | 28 | 5 | 1 | 5 | ✓ |
| `_run_document_checks` | L201-236 | 36 | 3 | 1 | 2 | ✓ |
| `_load_documented_paths` | L140-154 | 15 | 2 | 1 | 0 | ✓ |
| `_build_auth_headers` | L159-165 | 7 | 2 | 0 | 1 | ✓ |

**全部问题 (15)**

- 🔄 `_build_exam_answers()` L99: 复杂度: 16
- 🔄 `_build_exam_answers()` L99: 认知复杂度: 22
- 📏 `_record()` L29: 6 参数数量
- 🏗️ `_build_exam_answers()` L99: 中等嵌套: 3
- ❌ L114: 未处理的易出错调用
- ❌ L127: 未处理的易出错调用
- ❌ L128: 未处理的易出错调用
- ❌ L129: 未处理的易出错调用
- 🏷️ `_record()` L29: "_record" - snake_case
- 🏷️ `_blob()` L67: "_blob" - snake_case
- 🏷️ `_build_exam_answers()` L99: "_build_exam_answers" - snake_case
- 🏷️ `_load_documented_paths()` L140: "_load_documented_paths" - snake_case
- 🏷️ `_build_auth_headers()` L159: "_build_auth_headers" - snake_case
- 🏷️ `_pick_first_id()` L170: "_pick_first_id" - snake_case
- 🏷️ `_run_document_checks()` L201: "_run_document_checks" - snake_case

**详情**:
- 循环复杂度: 平均: 5.7, 最大: 16
- 认知复杂度: 平均: 8.3, 最大: 22
- 嵌套深度: 平均: 1.3, 最大: 3
- 函数长度: 平均: 26.0 行, 最大: 37 行
- 文件长度: 184 代码量 (237 总计)
- 参数数量: 平均: 2.6, 最大: 6
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 1 个结构问题
- 错误处理: 4/9 个错误被忽略 (44.4%)
- 注释比例: 13.0% (24/184)
- 命名规范: 发现 7 个违规

### 21. backend\ai_services\services\mefkt_runtime_support.py

**糟糕指数: 18.98**

> 行数: 510 总计, 449 代码, 2 注释 | 函数: 12 | 类: 5

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 8, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_pairwise_graph_weight` | L305-326 | 22 | 9 | 2 | 7 | ✓ |
| `load_runtime_source_data` | L76-131 | 56 | 7 | 2 | 1 | ✓ |
| `_collect_question_feature_entry` | L156-204 | 49 | 5 | 0 | 4 | ✓ |
| `build_graph_statistics` | L329-385 | 57 | 5 | 3 | 3 | ✓ |
| `prepare_question_features` | L236-302 | 67 | 3 | 2 | 4 | ✓ |
| `_build_single_feature_row` | L424-464 | 41 | 3 | 0 | 9 | ✓ |
| `_build_chapter_norm_map` | L145-153 | 9 | 2 | 0 | 2 | ✓ |
| `build_runtime_feature_rows` | L467-509 | 43 | 2 | 1 | 7 | ✓ |
| `_build_feature_sources` | L134-142 | 9 | 1 | 0 | 1 | ✓ |
| `_normalize_question_feature_scales` | L207-233 | 27 | 1 | 0 | 10 | ✓ |
| `_build_neighbor_difficulty_tensor` | L388-398 | 11 | 1 | 0 | 2 | ✓ |
| `_build_relation_stats_matrix` | L401-421 | 21 | 1 | 0 | 2 | ✓ |

**全部问题 (19)**

- 🔄 `_pairwise_graph_weight()` L305: 认知复杂度: 13
- 📏 `load_runtime_source_data()` L76: 56 代码量
- 📏 `prepare_question_features()` L236: 67 代码量
- 📏 `build_graph_statistics()` L329: 57 代码量
- 📏 `_normalize_question_feature_scales()` L207: 10 参数数量
- 📏 `_pairwise_graph_weight()` L305: 7 参数数量
- 📏 `_build_single_feature_row()` L424: 9 参数数量
- 📏 `build_runtime_feature_rows()` L467: 7 参数数量
- 🏗️ `build_graph_statistics()` L329: 中等嵌套: 3
- ❌ L173: 未处理的易出错调用
- ❌ L456: 未处理的易出错调用
- 🏷️ `_build_feature_sources()` L134: "_build_feature_sources" - snake_case
- 🏷️ `_build_chapter_norm_map()` L145: "_build_chapter_norm_map" - snake_case
- 🏷️ `_collect_question_feature_entry()` L156: "_collect_question_feature_entry" - snake_case
- 🏷️ `_normalize_question_feature_scales()` L207: "_normalize_question_feature_scales" - snake_case
- 🏷️ `_pairwise_graph_weight()` L305: "_pairwise_graph_weight" - snake_case
- 🏷️ `_build_neighbor_difficulty_tensor()` L388: "_build_neighbor_difficulty_tensor" - snake_case
- 🏷️ `_build_relation_stats_matrix()` L401: "_build_relation_stats_matrix" - snake_case
- 🏷️ `_build_single_feature_row()` L424: "_build_single_feature_row" - snake_case

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 9
- 认知复杂度: 平均: 5.0, 最大: 13
- 嵌套深度: 平均: 0.8, 最大: 3
- 函数长度: 平均: 34.3 行, 最大: 67 行
- 文件长度: 449 代码量 (510 总计)
- 参数数量: 平均: 4.3, 最大: 10
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 1 个结构问题
- 错误处理: 2/8 个错误被忽略 (25.0%)
- 注释比例: 0.4% (2/449)
- 命名规范: 发现 8 个违规

### 22. backend\tools\question_import_support.py

**糟糕指数: 18.85**

> 行数: 484 总计, 409 代码, 2 注释 | 函数: 22 | 类: 4

**问题**: 🔄 复杂度问题: 7, ⚠️ 其他问题: 2, 🏗️ 结构问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_excel_question_payload` | L351-394 | 44 | 20 | 1 | 3 | ✓ |
| `extract_question_content` | L184-193 | 10 | 9 | 2 | 2 | ✓ |
| `match_knowledge_point_by_topic` | L207-227 | 21 | 9 | 3 | 2 | ✓ |
| `build_json_question_payload` | L280-297 | 18 | 9 | 1 | 1 | ✓ |
| `_build_excel_answer` | L315-328 | 14 | 9 | 2 | 2 | ✓ |
| `strip_import_answer_payload` | L132-150 | 19 | 7 | 3 | 1 | ✓ |
| `iter_excel_question_payloads` | L444-472 | 29 | 7 | 3 | 3 | ✓ |
| `clean_question_options` | L163-181 | 19 | 6 | 2 | 1 | ✓ |
| `_build_excel_options` | L300-312 | 13 | 6 | 2 | 2 | ✓ |
| `_normalize_true_false_options` | L331-348 | 18 | 6 | 2 | 2 | ✓ |
| `open_question_bank_workbook` | L414-441 | 28 | 6 | 2 | 2 | ✓ |
| `load_question_json_source` | L263-277 | 15 | 5 | 2 | 1 | ✓ |
| `normalize_question_answer` | L153-160 | 8 | 4 | 1 | 1 | ✓ |
| `normalize_knowledge_point_names` | L196-204 | 9 | 4 | 1 | 1 | ✓ |
| `link_question_knowledge_points` | L240-260 | 21 | 4 | 2 | 4 | ✓ |
| `record_import` | L74-78 | 5 | 2 | 1 | 2 | ✓ |
| `_validate_question_json_payload` | L107-111 | 5 | 2 | 1 | 1 | ✓ |
| `_row_get` | L114-119 | 6 | 2 | 1 | 2 | ✓ |
| `strip_import_text` | L122-129 | 8 | 2 | 1 | 1 | ✓ |
| `resolve_filename_knowledge_point` | L475-483 | 9 | 2 | 1 | 2 | ✓ |
| `build_question_import_context` | L230-237 | 8 | 1 | 0 | 1 | ✓ |
| `create_question_from_payload` | L397-411 | 15 | 1 | 0 | 2 | ✓ |

**全部问题 (15)**

- 🔄 `build_excel_question_payload()` L351: 复杂度: 20
- 🔄 `strip_import_answer_payload()` L132: 认知复杂度: 13
- 🔄 `extract_question_content()` L184: 认知复杂度: 13
- 🔄 `match_knowledge_point_by_topic()` L207: 认知复杂度: 15
- 🔄 `_build_excel_answer()` L315: 认知复杂度: 13
- 🔄 `build_excel_question_payload()` L351: 认知复杂度: 22
- 🔄 `iter_excel_question_payloads()` L444: 认知复杂度: 13
- 🏗️ `strip_import_answer_payload()` L132: 中等嵌套: 3
- 🏗️ `match_knowledge_point_by_topic()` L207: 中等嵌套: 3
- 🏗️ `iter_excel_question_payloads()` L444: 中等嵌套: 3
- 🏷️ `_validate_question_json_payload()` L107: "_validate_question_json_payload" - snake_case
- 🏷️ `_row_get()` L114: "_row_get" - snake_case
- 🏷️ `_build_excel_options()` L300: "_build_excel_options" - snake_case
- 🏷️ `_build_excel_answer()` L315: "_build_excel_answer" - snake_case
- 🏷️ `_normalize_true_false_options()` L331: "_normalize_true_false_options" - snake_case

**详情**:
- 循环复杂度: 平均: 5.6, 最大: 20
- 认知复杂度: 平均: 8.7, 最大: 22
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 15.5 行, 最大: 44 行
- 文件长度: 409 代码量 (484 总计)
- 参数数量: 平均: 1.8, 最大: 4
- 代码重复: 0.0% 重复 (0/22)
- 结构分析: 3 个结构问题
- 错误处理: 0/16 个错误被忽略 (0.0%)
- 注释比例: 0.5% (2/409)
- 命名规范: 发现 5 个违规

### 23. backend\knowledge\teacher_question_views.py

**糟糕指数: 18.72**

> 行数: 343 总计, 299 代码, 0 注释 | 函数: 10 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `question_detail` | L75-135 | 61 | 19 | 3 | 2 | ✓ |
| `question_update` | L177-201 | 25 | 11 | 2 | 2 | ✓ |
| `question_export` | L267-291 | 25 | 9 | 1 | 1 | ✓ |
| `question_list` | L35-70 | 36 | 8 | 1 | 1 | ✓ |
| `question_create` | L140-172 | 33 | 8 | 1 | 1 | ✓ |
| `question_import` | L237-262 | 26 | 6 | 2 | 1 | ✓ |
| `question_batch_delete` | L220-232 | 13 | 4 | 2 | 1 | ✓ |
| `question_link_knowledge` | L330-342 | 13 | 3 | 1 | 2 | ✓ |
| `question_delete` | L206-215 | 10 | 2 | 1 | 2 | ✓ |
| `question_template` | L296-325 | 30 | 1 | 0 | 1 | ✓ |

**全部问题 (8)**

- 🔄 `question_detail()` L75: 复杂度: 19
- 🔄 `question_update()` L177: 复杂度: 11
- 🔄 `question_detail()` L75: 认知复杂度: 25
- 🔄 `question_update()` L177: 认知复杂度: 15
- 📏 `question_detail()` L75: 61 代码量
- 🏗️ `question_detail()` L75: 中等嵌套: 3
- ❌ L211: 未处理的易出错调用
- ❌ L228: 忽略了错误返回值

**详情**:
- 循环复杂度: 平均: 7.1, 最大: 19
- 认知复杂度: 平均: 9.9, 最大: 25
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 27.2 行, 最大: 61 行
- 文件长度: 299 代码量 (343 总计)
- 参数数量: 平均: 1.4, 最大: 2
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 1 个结构问题
- 错误处理: 2/20 个错误被忽略 (10.0%)
- 注释比例: 0.0% (0/299)
- 命名规范: 无命名违规

### 24. frontend\scripts\browser-audit.mjs

**糟糕指数: 18.42**

> 行数: 880 总计, 779 代码, 0 注释 | 函数: 38 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 🏗️ 结构问题: 2, ❌ 错误处理问题: 13, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `parseArgs` | L16-34 | 19 | 7 | 2 | 1 | ✗ |
| `prepareDemoScenario` | L508-563 | 56 | 7 | 2 | 3 | ✗ |
| `buildRoutes` | L176-218 | 43 | 6 | 2 | 2 | ✗ |
| `simulateDemoScenario` | L565-629 | 64 | 6 | 3 | 3 | ✗ |
| `main` | L854-874 | 21 | 5 | 4 | 0 | ✗ |
| `ensureInitialAssessments` | L380-407 | 28 | 4 | 1 | 2 | ✗ |
| `prepareDefenseDemoScenario` | L631-677 | 47 | 4 | 2 | 3 | ✗ |
| `resolveStudentContext` | L103-146 | 38 | 3 | 1 | 2 | ✗ |
| `resolveDefenseCourseContext` | L148-174 | 26 | 3 | 1 | 2 | ✗ |
| `openTeacherImportCourseFlow` | L314-346 | 33 | 3 | 2 | 4 | ✗ |
| `waitForFeedbackReady` | L444-453 | 8 | 3 | 2 | 2 | ✗ |
| `prepareStableStudent` | L470-494 | 23 | 3 | 2 | 2 | ✗ |
| `simulateDefenseDemoScenario` | L679-777 | 97 | 3 | 1 | 3 | ✗ |
| `auditRole` | L779-807 | 29 | 3 | 1 | 2 | ✗ |
| `readJson` | L45-52 | 8 | 2 | 0 | 1 | ✗ |
| `loginApi` | L54-69 | 15 | 2 | 1 | 3 | ✗ |
| `ensureBackendReady` | L71-81 | 11 | 2 | 1 | 1 | ✗ |
| `apiJson` | L90-101 | 11 | 2 | 1 | 3 | ✗ |
| `pickOptionValue` | L348-353 | 6 | 2 | 1 | 0 | ✗ |
| `ensureNeo4jKnowledgeMap` | L461-468 | 8 | 2 | 1 | 2 | ✗ |
| `runAuditScenario` | L809-852 | 44 | 2 | 1 | 2 | ✗ |
| `ensureDir` | L36-38 | 3 | 1 | 0 | 1 | ✗ |
| `writeJson` | L40-43 | 4 | 1 | 0 | 2 | ✗ |
| `createAuthedClient` | L83-88 | 6 | 1 | 0 | 2 | ✗ |
| `slugifyRoute` | L220-222 | 3 | 1 | 0 | 1 | ✗ |
| `createBrowserSession` | L224-268 | 16 | 1 | 0 | 2 | ✗ |
| `captureRoute` | L270-279 | 10 | 1 | 0 | 4 | ✗ |
| `captureCurrentPage` | L281-288 | 8 | 1 | 0 | 3 | ✗ |
| `resolveDefenseDemoArchivePath` | L290-292 | 3 | 1 | 0 | 1 | ✗ |
| `ensureDefenseArchiveExists` | L294-298 | 5 | 1 | 0 | 1 | ✗ |
| `buildDefenseStageTestAnswers` | L300-312 | 6 | 1 | 0 | 2 | ✗ |
| `buildSurveyAnswers` | L355-360 | 2 | 1 | 0 | 0 | ✗ |
| `buildKnowledgeAnswers` | L362-378 | 2 | 1 | 0 | 0 | ✗ |
| `ensureProfileAndPath` | L409-415 | 5 | 1 | 0 | 2 | ✗ |
| `fetchExamList` | L417-420 | 4 | 1 | 0 | 2 | ✗ |
| `submitExamWithGeneratedAnswers` | L422-442 | 8 | 1 | 0 | 3 | ✗ |
| `refreshLearningPath` | L455-459 | 4 | 1 | 0 | 2 | ✗ |
| `prepareTriggerStudent` | L496-506 | 10 | 1 | 0 | 2 | ✗ |

**全部问题 (16)**

- 🔄 `main()` L854: 嵌套深度: 4
- 🏗️ `simulateDemoScenario()` L565: 中等嵌套: 3
- 🏗️ `main()` L854: 中等嵌套: 4
- ❌ L37: 未处理的易出错调用
- ❌ L42: 未处理的易出错调用
- ❌ L237: 未处理的易出错调用
- ❌ L296: 未处理的易出错调用
- ❌ L344: 未处理的易出错调用
- ❌ L557: 未处理的易出错调用
- ❌ L623: 未处理的易出错调用
- ❌ L671: 未处理的易出错调用
- ❌ L701: 未处理的易出错调用
- ❌ L720: 未处理的易出错调用
- ❌ L772: 未处理的易出错调用
- ❌ L806: 未处理的易出错调用
- ❌ L872: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 7
- 认知复杂度: 平均: 4.1, 最大: 13
- 嵌套深度: 平均: 0.8, 最大: 4
- 函数长度: 平均: 19.3 行, 最大: 97 行
- 文件长度: 779 代码量 (880 总计)
- 参数数量: 平均: 1.9, 最大: 4
- 代码重复: 2.6% 重复 (1/38)
- 结构分析: 2 个结构问题
- 错误处理: 13/21 个错误被忽略 (61.9%)
- 注释比例: 0.0% (0/779)
- 命名规范: 无命名违规

### 25. backend\exams\teacher_exam_management_views.py

**糟糕指数: 18.42**

> 行数: 403 总计, 336 代码, 0 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 4, 🏗️ 结构问题: 3, ❌ 错误处理问题: 5, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `exam_update` | L214-278 | 65 | 17 | 3 | 2 | ✓ |
| `exam_publish` | L125-152 | 28 | 8 | 2 | 2 | ✓ |
| `exam_teacher_detail` | L157-209 | 53 | 8 | 1 | 2 | ✓ |
| `teacher_exam_add_questions` | L341-370 | 30 | 8 | 3 | 2 | ✓ |
| `exam_create` | L66-120 | 55 | 7 | 3 | 1 | ✓ |
| `exam_delete` | L283-307 | 25 | 5 | 1 | 2 | ✓ |
| `exam_unpublish` | L312-336 | 25 | 5 | 1 | 2 | ✓ |
| `teacher_exam_remove_questions` | L375-389 | 15 | 4 | 1 | 2 | ✓ |
| `exam_manage_list` | L28-61 | 34 | 3 | 1 | 1 | ✓ |

**全部问题 (15)**

- 🔄 `exam_update()` L214: 复杂度: 17
- 🔄 `exam_create()` L66: 认知复杂度: 13
- 🔄 `exam_update()` L214: 认知复杂度: 23
- 🔄 `teacher_exam_add_questions()` L341: 认知复杂度: 14
- 📏 `exam_create()` L66: 55 代码量
- 📏 `exam_teacher_detail()` L157: 53 代码量
- 📏 `exam_update()` L214: 65 代码量
- 🏗️ `exam_create()` L66: 中等嵌套: 3
- 🏗️ `exam_update()` L214: 中等嵌套: 3
- 🏗️ `teacher_exam_add_questions()` L341: 中等嵌套: 3
- ❌ L75: 未处理的易出错调用
- ❌ L76: 未处理的易出错调用
- ❌ L179: 未处理的易出错调用
- ❌ L305: 未处理的易出错调用
- ❌ L386: 忽略了错误返回值

**详情**:
- 循环复杂度: 平均: 7.2, 最大: 17
- 认知复杂度: 平均: 10.8, 最大: 23
- 嵌套深度: 平均: 1.8, 最大: 3
- 函数长度: 平均: 36.7 行, 最大: 65 行
- 文件长度: 336 代码量 (403 总计)
- 参数数量: 平均: 1.8, 最大: 2
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 3 个结构问题
- 错误处理: 5/27 个错误被忽略 (18.5%)
- 注释比例: 0.0% (0/336)
- 命名规范: 无命名违规

### 26. backend\platform_ai\rag\student_point_path_mixin.py

**糟糕指数: 18.42**

> 行数: 198 总计, 173 代码, 0 注释 | 函数: 6 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 2, ❌ 错误处理问题: 5, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `explain_knowledge_point` | L80-163 | 84 | 14 | 1 | 5 | ✓ |
| `build_path_context` | L37-52 | 16 | 5 | 0 | 4 | ✓ |
| `build_point_support_payload` | L54-78 | 25 | 4 | 1 | 3 | ✓ |
| `plan_learning_path` | L165-197 | 33 | 4 | 1 | 6 | ✓ |
| `_find_point` | L19-27 | 9 | 3 | 1 | 4 | ✓ |
| `_estimate_point_difficulty` | L29-35 | 7 | 3 | 1 | 2 | ✓ |

**全部问题 (11)**

- 🔄 `explain_knowledge_point()` L80: 复杂度: 14
- 🔄 `explain_knowledge_point()` L80: 认知复杂度: 16
- 📏 `explain_knowledge_point()` L80: 84 代码量
- 📏 `plan_learning_path()` L165: 6 参数数量
- ❌ L48: 未处理的易出错调用
- ❌ L73: 未处理的易出错调用
- ❌ L144: 未处理的易出错调用
- ❌ L184: 未处理的易出错调用
- ❌ L186: 未处理的易出错调用
- 🏷️ `_find_point()` L19: "_find_point" - snake_case
- 🏷️ `_estimate_point_difficulty()` L29: "_estimate_point_difficulty" - snake_case

**详情**:
- 循环复杂度: 平均: 5.5, 最大: 14
- 认知复杂度: 平均: 7.2, 最大: 16
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 29.0 行, 最大: 84 行
- 文件长度: 173 代码量 (198 总计)
- 参数数量: 平均: 4.0, 最大: 6
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 5/7 个错误被忽略 (71.4%)
- 注释比例: 0.0% (0/173)
- 命名规范: 发现 2 个违规

### 27. backend\exams\report_service.py

**糟糕指数: 18.33**

> 行数: 418 总计, 366 代码, 2 注释 | 函数: 12 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 9, 📝 注释问题: 1, 🏷️ 命名问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_feedback_report_sync` | L301-417 | 117 | 9 | 1 | 2 | ✓ |
| `_refresh_kt_analysis` | L135-189 | 55 | 7 | 4 | 4 | ✓ |
| `_build_detailed_mistakes` | L192-223 | 32 | 6 | 1 | 2 | ✓ |
| `_persist_failed_report` | L282-298 | 17 | 6 | 0 | 2 | ✓ |
| `_build_answer_history_records` | L104-132 | 29 | 4 | 2 | 2 | ✓ |
| `enqueue_feedback_report` | L47-60 | 14 | 3 | 2 | 2 | ✓ |
| `_run_feedback_generation` | L73-86 | 14 | 2 | 2 | 2 | ✓ |
| `_extract_habit_preferences` | L226-242 | 17 | 2 | 1 | 1 | ✓ |
| `_normalize_llm_list` | L245-253 | 9 | 2 | 0 | 2 | ✓ |
| `_save_llm_call_log` | L256-279 | 24 | 2 | 1 | 5 | ✓ |
| `enqueue_feedback_report_on_commit` | L63-70 | 8 | 1 | 0 | 2 | ✓ |
| `_load_report_with_dependencies` | L89-101 | 13 | 1 | 0 | 1 | ✓ |

**全部问题 (23)**

- 🔄 `_refresh_kt_analysis()` L135: 认知复杂度: 15
- 🔄 `_refresh_kt_analysis()` L135: 嵌套深度: 4
- 📏 `_refresh_kt_analysis()` L135: 55 代码量
- 📏 `generate_feedback_report_sync()` L301: 117 代码量
- 🏗️ `_refresh_kt_analysis()` L135: 中等嵌套: 4
- ❌ L175: 未处理的易出错调用
- ❌ L176: 未处理的易出错调用
- ❌ L177: 未处理的易出错调用
- ❌ L214: 未处理的易出错调用
- ❌ L215: 未处理的易出错调用
- ❌ L216: 未处理的易出错调用
- ❌ L217: 未处理的易出错调用
- ❌ L218: 未处理的易出错调用
- ❌ L271: 未处理的易出错调用
- 🏷️ `_run_feedback_generation()` L73: "_run_feedback_generation" - snake_case
- 🏷️ `_load_report_with_dependencies()` L89: "_load_report_with_dependencies" - snake_case
- 🏷️ `_build_answer_history_records()` L104: "_build_answer_history_records" - snake_case
- 🏷️ `_refresh_kt_analysis()` L135: "_refresh_kt_analysis" - snake_case
- 🏷️ `_build_detailed_mistakes()` L192: "_build_detailed_mistakes" - snake_case
- 🏷️ `_extract_habit_preferences()` L226: "_extract_habit_preferences" - snake_case
- 🏷️ `_normalize_llm_list()` L245: "_normalize_llm_list" - snake_case
- 🏷️ `_save_llm_call_log()` L256: "_save_llm_call_log" - snake_case
- 🏷️ `_persist_failed_report()` L282: "_persist_failed_report" - snake_case

**详情**:
- 循环复杂度: 平均: 3.8, 最大: 9
- 认知复杂度: 平均: 6.1, 最大: 15
- 嵌套深度: 平均: 1.2, 最大: 4
- 函数长度: 平均: 29.1 行, 最大: 117 行
- 文件长度: 366 代码量 (418 总计)
- 参数数量: 平均: 2.3, 最大: 5
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 1 个结构问题
- 错误处理: 9/15 个错误被忽略 (60.0%)
- 注释比例: 0.5% (2/366)
- 命名规范: 发现 9 个违规

### 28. backend\tools\mefkt_public_data.py

**糟糕指数: 18.26**

> 行数: 316 总计, 268 代码, 2 注释 | 函数: 14 | 类: 1

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 1, 🏗️ 结构问题: 3, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_load_csv_sequences` | L74-114 | 41 | 15 | 2 | 1 | ✓ |
| `_build_public_bundle` | L224-266 | 43 | 8 | 2 | 2 | ✓ |
| `_chunk_public_sequences` | L124-136 | 13 | 7 | 3 | 2 | ✓ |
| `_evaluate_sequence_model` | L294-315 | 22 | 7 | 3 | 4 | ✓ |
| `_estimate_public_time_proxy` | L167-180 | 14 | 6 | 3 | 2 | ✓ |
| `_load_three_line_sequences` | L59-71 | 13 | 4 | 2 | 1 | ✓ |
| `_build_transition_matrices` | L139-153 | 15 | 4 | 2 | 2 | ✓ |
| `_estimate_public_difficulty` | L156-164 | 9 | 4 | 2 | 3 | ✓ |
| `_normalize_tensor` | L48-56 | 9 | 3 | 1 | 2 | ✓ |
| `_relative_to_project` | L39-45 | 7 | 2 | 1 | 1 | ✓ |
| `_load_public_sequences` | L117-121 | 5 | 2 | 1 | 1 | ✓ |
| `_build_public_features` | L183-221 | 39 | 2 | 1 | 6 | ✓ |
| `_collate_batch` | L269-281 | 13 | 2 | 1 | 1 | ✓ |
| `_split_sequences` | L284-291 | 8 | 2 | 1 | 3 | ✓ |

**全部问题 (19)**

- 🔄 `_load_csv_sequences()` L74: 复杂度: 15
- 🔄 `_load_csv_sequences()` L74: 认知复杂度: 19
- 🔄 `_chunk_public_sequences()` L124: 认知复杂度: 13
- 🔄 `_evaluate_sequence_model()` L294: 认知复杂度: 13
- 📏 `_build_public_features()` L183: 6 参数数量
- 🏗️ `_chunk_public_sequences()` L124: 中等嵌套: 3
- 🏗️ `_estimate_public_time_proxy()` L167: 中等嵌套: 3
- 🏗️ `_evaluate_sequence_model()` L294: 中等嵌套: 3
- ❌ L104: 未处理的易出错调用
- 🏷️ `_relative_to_project()` L39: "_relative_to_project" - snake_case
- 🏷️ `_normalize_tensor()` L48: "_normalize_tensor" - snake_case
- 🏷️ `_load_three_line_sequences()` L59: "_load_three_line_sequences" - snake_case
- 🏷️ `_load_csv_sequences()` L74: "_load_csv_sequences" - snake_case
- 🏷️ `_load_public_sequences()` L117: "_load_public_sequences" - snake_case
- 🏷️ `_chunk_public_sequences()` L124: "_chunk_public_sequences" - snake_case
- 🏷️ `_build_transition_matrices()` L139: "_build_transition_matrices" - snake_case
- 🏷️ `_estimate_public_difficulty()` L156: "_estimate_public_difficulty" - snake_case
- 🏷️ `_estimate_public_time_proxy()` L167: "_estimate_public_time_proxy" - snake_case
- 🏷️ `_build_public_features()` L183: "_build_public_features" - snake_case

**详情**:
- 循环复杂度: 平均: 4.9, 最大: 15
- 认知复杂度: 平均: 8.4, 最大: 19
- 嵌套深度: 平均: 1.8, 最大: 3
- 函数长度: 平均: 17.9 行, 最大: 43 行
- 文件长度: 268 代码量 (316 总计)
- 参数数量: 平均: 2.2, 最大: 6
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 3 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 0.7% (2/268)
- 命名规范: 发现 14 个违规

### 29. backend\common\neo4j_crud.py

**糟糕指数: 18.17**

> 行数: 239 总计, 216 代码, 0 注释 | 函数: 8 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 📋 重复问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `sync_single_point` | L14-56 | 43 | 14 | 2 | 2 | ✓ |
| `has_course_graphrag_projection` | L160-179 | 20 | 5 | 2 | 2 | ✓ |
| `delete_point_neo4j` | L58-75 | 18 | 4 | 2 | 2 | ✓ |
| `sync_single_relation` | L77-108 | 32 | 4 | 2 | 2 | ✓ |
| `delete_relation_neo4j` | L110-131 | 22 | 4 | 2 | 3 | ✓ |
| `clear_course_graph` | L133-158 | 26 | 4 | 2 | 2 | ✓ |
| `sync_course_graphrag_projection` | L181-238 | 22 | 3 | 1 | 4 | ✓ |
| `_sync_projection_tx` | L195-230 | 36 | 3 | 1 | 1 | ✗ |

**全部问题 (5)**

- 🔄 `sync_single_point()` L14: 复杂度: 14
- 🔄 `sync_single_point()` L14: 认知复杂度: 18
- 📋 `delete_point_neo4j()` L58: 重复模式: delete_point_neo4j, delete_relation_neo4j
- 📋 `clear_course_graph()` L133: 重复模式: clear_course_graph, has_course_graphrag_projection
- 🏷️ `_sync_projection_tx()` L195: "_sync_projection_tx" - snake_case

**详情**:
- 循环复杂度: 平均: 5.1, 最大: 14
- 认知复杂度: 平均: 8.6, 最大: 18
- 嵌套深度: 平均: 1.8, 最大: 2
- 函数长度: 平均: 27.4 行, 最大: 43 行
- 文件长度: 216 代码量 (239 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 25.0% 重复 (2/8)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/216)
- 命名规范: 发现 1 个违规

### 30. backend\tools\questions.py

**糟糕指数: 18.11**

> 行数: 208 总计, 178 代码, 3 注释 | 函数: 5 | 类: 0

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 3, 📋 重复问题: 1, 🏗️ 结构问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_questions_json` | L82-152 | 71 | 11 | 3 | 4 | ✓ |
| `import_question_bank` | L155-207 | 53 | 7 | 3 | 3 | ✓ |
| `_print_json_import_summary` | L58-67 | 10 | 4 | 1 | 2 | ✓ |
| `_print_excel_import_summary` | L70-79 | 10 | 4 | 1 | 1 | ✓ |
| `_build_result_payload` | L36-55 | 20 | 1 | 0 | 5 | ✓ |

**全部问题 (11)**

- 🔄 `import_questions_json()` L82: 复杂度: 11
- 🔄 `import_questions_json()` L82: 认知复杂度: 17
- 🔄 `import_question_bank()` L155: 认知复杂度: 13
- 📏 `import_questions_json()` L82: 71 代码量
- 📏 `import_question_bank()` L155: 53 代码量
- 📋 `_print_json_import_summary()` L58: 重复模式: _print_json_import_summary, _print_excel_import_summary
- 🏗️ `import_questions_json()` L82: 中等嵌套: 3
- 🏗️ `import_question_bank()` L155: 中等嵌套: 3
- 🏷️ `_build_result_payload()` L36: "_build_result_payload" - snake_case
- 🏷️ `_print_json_import_summary()` L58: "_print_json_import_summary" - snake_case
- 🏷️ `_print_excel_import_summary()` L70: "_print_excel_import_summary" - snake_case

**详情**:
- 循环复杂度: 平均: 5.4, 最大: 11
- 认知复杂度: 平均: 8.6, 最大: 17
- 嵌套深度: 平均: 1.6, 最大: 3
- 函数长度: 平均: 32.8 行, 最大: 71 行
- 文件长度: 178 代码量 (208 总计)
- 参数数量: 平均: 3.0, 最大: 5
- 代码重复: 20.0% 重复 (1/5)
- 结构分析: 2 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 1.7% (3/178)
- 命名规范: 发现 3 个违规

### 31. backend\platform_ai\rag\runtime_graph_query_support.py

**糟糕指数: 18.11**

> 行数: 203 总计, 179 代码, 0 注释 | 函数: 6 | 类: 0

**问题**: 🔄 复杂度问题: 8, ⚠️ 其他问题: 1, ❌ 错误处理问题: 9, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_tools_query_context` | L147-202 | 56 | 16 | 2 | 1 | ✓ |
| `build_tool_line` | L61-82 | 22 | 14 | 2 | 1 | ✓ |
| `build_tool_source` | L85-114 | 30 | 14 | 1 | 1 | ✓ |
| `build_graph_record_item` | L20-58 | 39 | 12 | 1 | 1 | ✓ |
| `build_semantic_only_query_context` | L130-144 | 15 | 4 | 0 | 2 | ✓ |
| `build_empty_query_context` | L117-127 | 11 | 1 | 0 | 0 | ✓ |

**全部问题 (18)**

- 🔄 `build_graph_record_item()` L20: 复杂度: 12
- 🔄 `build_tool_line()` L61: 复杂度: 14
- 🔄 `build_tool_source()` L85: 复杂度: 14
- 🔄 `build_tools_query_context()` L147: 复杂度: 16
- 🔄 `build_graph_record_item()` L20: 认知复杂度: 14
- 🔄 `build_tool_line()` L61: 认知复杂度: 18
- 🔄 `build_tool_source()` L85: 认知复杂度: 16
- 🔄 `build_tools_query_context()` L147: 认知复杂度: 20
- 📏 `build_tools_query_context()` L147: 56 代码量
- ❌ L96: 未处理的易出错调用
- ❌ L105: 未处理的易出错调用
- ❌ L106: 未处理的易出错调用
- ❌ L107: 未处理的易出错调用
- ❌ L108: 未处理的易出错调用
- ❌ L109: 未处理的易出错调用
- ❌ L110: 未处理的易出错调用
- ❌ L111: 未处理的易出错调用
- ❌ L173: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 10.2, 最大: 16
- 认知复杂度: 平均: 12.2, 最大: 20
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 28.8 行, 最大: 56 行
- 文件长度: 179 代码量 (203 总计)
- 参数数量: 平均: 1.0, 最大: 2
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 9/30 个错误被忽略 (30.0%)
- 注释比例: 0.0% (0/179)
- 命名规范: 无命名违规

### 32. backend\users\profile_generation.py

**糟糕指数: 18.00**

> 行数: 278 总计, 245 代码, 0 注释 | 函数: 9 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_profile_text` | L204-255 | 52 | 9 | 1 | 7 | ✓ |
| `generate_profile_for_course` | L36-151 | 116 | 7 | 3 | 3 | ✓ |
| `_refresh_mastery_with_kt` | L164-201 | 38 | 6 | 2 | 2 | ✓ |
| `_resolve_course_name` | L154-161 | 8 | 2 | 1 | 1 | ✓ |
| `_record_profile_llm_log` | L258-277 | 20 | 2 | 1 | 5 | ✓ |
| `get_knowledge_mastery` | L23-24 | 2 | 1 | 0 | 2 | ✓ |
| `get_ability_scores` | L26-27 | 2 | 1 | 0 | 2 | ✓ |
| `get_habit_preferences` | L29-30 | 2 | 1 | 0 | 1 | ✓ |
| `_build_cached_profile_result` | L32-33 | 2 | 1 | 0 | 2 | ✓ |

**全部问题 (14)**

- 🔄 `generate_profile_for_course()` L36: 认知复杂度: 13
- 📏 `generate_profile_for_course()` L36: 116 代码量
- 📏 `_build_profile_text()` L204: 52 代码量
- 📏 `_build_profile_text()` L204: 7 参数数量
- 🏗️ `generate_profile_for_course()` L36: 中等嵌套: 3
- ❌ L108: 未处理的易出错调用
- ❌ L236: 未处理的易出错调用
- ❌ L238: 未处理的易出错调用
- ❌ L269: 未处理的易出错调用
- 🏷️ `_build_cached_profile_result()` L32: "_build_cached_profile_result" - snake_case
- 🏷️ `_resolve_course_name()` L154: "_resolve_course_name" - snake_case
- 🏷️ `_refresh_mastery_with_kt()` L164: "_refresh_mastery_with_kt" - snake_case
- 🏷️ `_build_profile_text()` L204: "_build_profile_text" - snake_case
- 🏷️ `_record_profile_llm_log()` L258: "_record_profile_llm_log" - snake_case

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 9
- 认知复杂度: 平均: 5.1, 最大: 13
- 嵌套深度: 平均: 0.9, 最大: 3
- 函数长度: 平均: 26.9 行, 最大: 116 行
- 文件长度: 245 代码量 (278 总计)
- 参数数量: 平均: 2.8, 最大: 7
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 4/7 个错误被忽略 (57.1%)
- 注释比例: 0.0% (0/245)
- 命名规范: 发现 5 个违规

### 33. backend\tools\api_smoke.py

**糟糕指数: 17.99**

> 行数: 216 总计, 183 代码, 9 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `student_flow_smoke` | L110-209 | 100 | 15 | 3 | 5 | ✓ |
| `api_smoke` | L19-107 | 89 | 14 | 2 | 5 | ✓ |
| `test_business_logic` | L212-215 | 4 | 1 | 0 | 0 | ✓ |

**全部问题 (7)**

- 🔄 `api_smoke()` L19: 复杂度: 14
- 🔄 `student_flow_smoke()` L110: 复杂度: 15
- 🔄 `api_smoke()` L19: 认知复杂度: 18
- 🔄 `student_flow_smoke()` L110: 认知复杂度: 21
- 📏 `api_smoke()` L19: 89 代码量
- 📏 `student_flow_smoke()` L110: 100 代码量
- 🏗️ `student_flow_smoke()` L110: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 10.0, 最大: 15
- 认知复杂度: 平均: 13.3, 最大: 21
- 嵌套深度: 平均: 1.7, 最大: 3
- 函数长度: 平均: 64.3 行, 最大: 100 行
- 文件长度: 183 代码量 (216 总计)
- 参数数量: 平均: 3.3, 最大: 5
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 1 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 4.9% (9/183)
- 命名规范: 无命名违规

### 34. backend\assessments\habit_views.py

**糟糕指数: 17.69**

> 行数: 265 总计, 222 代码, 0 注释 | 函数: 14 | 类: 0

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 7, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_resolve_habit_field` | L171-192 | 22 | 17 | 1 | 1 | ✓ |
| `_normalize_habit_answer` | L195-204 | 10 | 7 | 1 | 2 | ✓ |
| `_map_habit_responses` | L132-154 | 23 | 5 | 2 | 1 | ✓ |
| `submit_habit_survey` | L55-79 | 25 | 4 | 2 | 1 | ✓ |
| `_seed_default_habit_questions` | L93-106 | 14 | 3 | 2 | 0 | ✓ |
| `_normalize_response_items` | L157-168 | 12 | 3 | 1 | 1 | ✓ |
| `get_habit_survey` | L32-50 | 19 | 2 | 1 | 1 | ✓ |
| `_get_or_create_habit_questions` | L82-90 | 9 | 2 | 1 | 1 | ✓ |
| `_mark_habit_assessment_done` | L236-245 | 10 | 2 | 1 | 2 | ✓ |
| `_habit_question_queryset` | L109-114 | 6 | 1 | 0 | 1 | ✓ |
| `_serialize_habit_questions` | L117-129 | 13 | 1 | 0 | 1 | ✓ |
| `_save_habit_preference` | L207-228 | 22 | 1 | 0 | 3 | ✓ |
| `_study_duration_bucket` | L231-233 | 3 | 1 | 0 | 1 | ✓ |
| `_create_missing_course_assessment_statuses` | L248-264 | 17 | 1 | 0 | 1 | ✓ |

**全部问题 (19)**

- 🔄 `_resolve_habit_field()` L171: 复杂度: 17
- 🔄 `_resolve_habit_field()` L171: 认知复杂度: 19
- ❌ L217: 未处理的易出错调用
- ❌ L218: 未处理的易出错调用
- ❌ L219: 未处理的易出错调用
- ❌ L221: 未处理的易出错调用
- ❌ L222: 未处理的易出错调用
- ❌ L223: 未处理的易出错调用
- ❌ L225: 未处理的易出错调用
- 🏷️ `_get_or_create_habit_questions()` L82: "_get_or_create_habit_questions" - snake_case
- 🏷️ `_seed_default_habit_questions()` L93: "_seed_default_habit_questions" - snake_case
- 🏷️ `_habit_question_queryset()` L109: "_habit_question_queryset" - snake_case
- 🏷️ `_serialize_habit_questions()` L117: "_serialize_habit_questions" - snake_case
- 🏷️ `_map_habit_responses()` L132: "_map_habit_responses" - snake_case
- 🏷️ `_normalize_response_items()` L157: "_normalize_response_items" - snake_case
- 🏷️ `_resolve_habit_field()` L171: "_resolve_habit_field" - snake_case
- 🏷️ `_normalize_habit_answer()` L195: "_normalize_habit_answer" - snake_case
- 🏷️ `_save_habit_preference()` L207: "_save_habit_preference" - snake_case
- 🏷️ `_study_duration_bucket()` L231: "_study_duration_bucket" - snake_case

**详情**:
- 循环复杂度: 平均: 3.6, 最大: 17
- 认知复杂度: 平均: 5.3, 最大: 19
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 14.6 行, 最大: 25 行
- 文件长度: 222 代码量 (265 总计)
- 参数数量: 平均: 1.2, 最大: 3
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 7/14 个错误被忽略 (50.0%)
- 注释比例: 0.0% (0/222)
- 命名规范: 发现 12 个违规

### 35. backend\learning\stage_test_submission.py

**糟糕指数: 17.68**

> 行数: 523 总计, 468 代码, 0 注释 | 函数: 20 | 类: 0

**问题**: ⚠️ 其他问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 11, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_mistake_detail` | L251-268 | 18 | 7 | 0 | 2 | ✓ |
| `_update_standard_node_status` | L387-400 | 14 | 5 | 1 | 2 | ✓ |
| `_fallback_mastery_update` | L488-515 | 28 | 5 | 3 | 3 | ✓ |
| `_build_single_question_detail` | L178-236 | 59 | 4 | 0 | 5 | ✓ |
| `_apply_demo_mastery` | L320-340 | 21 | 4 | 2 | 3 | ✓ |
| `submit_stage_test_answers` | L40-75 | 36 | 3 | 1 | 3 | ✓ |
| `_question_ids_from_answers` | L120-128 | 9 | 3 | 2 | 1 | ✓ |
| `_submit_standard_stage_test` | L349-384 | 36 | 3 | 1 | 6 | ✓ |
| `_apply_stage_kt_predictions` | L461-485 | 25 | 3 | 2 | 3 | ✓ |
| `_evaluate_stage_test` | L78-117 | 40 | 2 | 0 | 3 | ✓ |
| `_build_question_details` | L155-175 | 21 | 2 | 1 | 5 | ✓ |
| `_submit_demo_stage_test` | L271-303 | 33 | 2 | 1 | 7 | ✓ |
| `_update_demo_node_status` | L306-317 | 12 | 2 | 1 | 4 | ✓ |
| `_demo_feedback_report` | L343-346 | 4 | 2 | 0 | 1 | ✓ |
| `_update_mastery_from_kt_or_fallback` | L403-421 | 19 | 2 | 1 | 3 | ✓ |
| `_predict_stage_mastery` | L424-458 | 35 | 2 | 0 | 3 | ✓ |
| `_question_map` | L131-139 | 9 | 1 | 0 | 2 | ✓ |
| `_grade_questions` | L142-152 | 11 | 1 | 0 | 2 | ✓ |
| `_build_detailed_mistakes` | L239-248 | 10 | 1 | 0 | 2 | ✓ |
| `_refresh_learning_path` | L518-522 | 5 | 1 | 0 | 2 | ✓ |

**全部问题 (25)**

- 📏 `_build_single_question_detail()` L178: 59 代码量
- 📏 `_submit_demo_stage_test()` L271: 7 参数数量
- 📏 `_submit_standard_stage_test()` L349: 6 参数数量
- 🏗️ `_fallback_mastery_update()` L488: 中等嵌套: 3
- ❌ L201: 未处理的易出错调用
- ❌ L228: 未处理的易出错调用
- ❌ L234: 未处理的易出错调用
- ❌ L235: 未处理的易出错调用
- ❌ L245: 未处理的易出错调用
- ❌ L262: 未处理的易出错调用
- ❌ L263: 未处理的易出错调用
- ❌ L264: 未处理的易出错调用
- ❌ L265: 未处理的易出错调用
- ❌ L266: 未处理的易出错调用
- ❌ L267: 未处理的易出错调用
- 🏷️ `_evaluate_stage_test()` L78: "_evaluate_stage_test" - snake_case
- 🏷️ `_question_ids_from_answers()` L120: "_question_ids_from_answers" - snake_case
- 🏷️ `_question_map()` L131: "_question_map" - snake_case
- 🏷️ `_grade_questions()` L142: "_grade_questions" - snake_case
- 🏷️ `_build_question_details()` L155: "_build_question_details" - snake_case
- 🏷️ `_build_single_question_detail()` L178: "_build_single_question_detail" - snake_case
- 🏷️ `_build_detailed_mistakes()` L239: "_build_detailed_mistakes" - snake_case
- 🏷️ `_mistake_detail()` L251: "_mistake_detail" - snake_case
- 🏷️ `_submit_demo_stage_test()` L271: "_submit_demo_stage_test" - snake_case
- 🏷️ `_update_demo_node_status()` L306: "_update_demo_node_status" - snake_case

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 7
- 认知复杂度: 平均: 4.3, 最大: 11
- 嵌套深度: 平均: 0.8, 最大: 3
- 函数长度: 平均: 22.3 行, 最大: 59 行
- 文件长度: 468 代码量 (523 总计)
- 参数数量: 平均: 3.1, 最大: 7
- 代码重复: 5.0% 重复 (1/20)
- 结构分析: 1 个结构问题
- 错误处理: 11/19 个错误被忽略 (57.9%)
- 注释比例: 0.0% (0/468)
- 命名规范: 发现 19 个违规

### 36. backend\tools\knowledge_import_support.py

**糟糕指数: 17.60**

> 行数: 361 总计, 310 代码, 0 注释 | 函数: 13 | 类: 0

**问题**: 🔄 复杂度问题: 6, ⚠️ 其他问题: 4, 🏗️ 结构问题: 3, ❌ 错误处理问题: 8, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `parse_hierarchical_knowledge_excel` | L78-152 | 75 | 15 | 3 | 2 | ✓ |
| `validate_import_json_payload` | L11-32 | 22 | 14 | 2 | 2 | ✓ |
| `parse_flat_knowledge_excel` | L182-235 | 54 | 9 | 3 | 1 | ✓ |
| `append_relation_edges` | L155-179 | 25 | 8 | 3 | 5 | ✓ |
| `upsert_course_knowledge_edges` | L317-342 | 26 | 8 | 2 | 4 | ✓ |
| `patch_existing_point_from_node` | L301-314 | 14 | 7 | 2 | 2 | ✓ |
| `upsert_course_knowledge_nodes` | L261-298 | 38 | 6 | 2 | 2 | ✓ |
| `parse_knowledge_excel` | L45-66 | 22 | 5 | 1 | 1 | ✓ |
| `read_knowledge_import_source` | L35-42 | 8 | 4 | 1 | 1 | ✓ |
| `resolve_hierarchical_header_row` | L69-75 | 7 | 3 | 2 | 1 | ✓ |
| `build_course_point_maps` | L238-248 | 11 | 3 | 1 | 1 | ✓ |
| `sync_knowledge_graph_copy` | L345-360 | 16 | 3 | 2 | 1 | ✓ |
| `write_tmp_knowledge_json` | L251-258 | 8 | 1 | 0 | 1 | ✓ |

**全部问题 (19)**

- 🔄 `validate_import_json_payload()` L11: 复杂度: 14
- 🔄 `parse_hierarchical_knowledge_excel()` L78: 复杂度: 15
- 🔄 `validate_import_json_payload()` L11: 认知复杂度: 18
- 🔄 `parse_hierarchical_knowledge_excel()` L78: 认知复杂度: 21
- 🔄 `append_relation_edges()` L155: 认知复杂度: 14
- 🔄 `parse_flat_knowledge_excel()` L182: 认知复杂度: 15
- 📏 `parse_hierarchical_knowledge_excel()` L78: 75 代码量
- 📏 `parse_flat_knowledge_excel()` L182: 54 代码量
- 🏗️ `parse_hierarchical_knowledge_excel()` L78: 中等嵌套: 3
- 🏗️ `append_relation_edges()` L155: 中等嵌套: 3
- 🏗️ `parse_flat_knowledge_excel()` L182: 中等嵌套: 3
- ❌ L135: 未处理的易出错调用
- ❌ L137: 未处理的易出错调用
- ❌ L138: 未处理的易出错调用
- ❌ L139: 未处理的易出错调用
- ❌ L140: 未处理的易出错调用
- ❌ L218: 未处理的易出错调用
- ❌ L219: 未处理的易出错调用
- ❌ L296: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 6.6, 最大: 15
- 认知复杂度: 平均: 10.3, 最大: 21
- 嵌套深度: 平均: 1.8, 最大: 3
- 函数长度: 平均: 25.1 行, 最大: 75 行
- 文件长度: 310 代码量 (361 总计)
- 参数数量: 平均: 1.8, 最大: 5
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 3 个结构问题
- 错误处理: 8/36 个错误被忽略 (22.2%)
- 注释比例: 0.0% (0/310)
- 命名规范: 无命名违规

### 37. backend\platform_ai\mcp\resources.py

**糟糕指数: 17.44**

> 行数: 433 总计, 359 代码, 0 注释 | 函数: 18 | 类: 3

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 5, 📋 重复问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `search_internal_resources` | L159-229 | 71 | 14 | 3 | 5 | ✓ |
| `_search_with_exa` | L294-372 | 79 | 13 | 2 | 6 | ✓ |
| `_enrich_with_firecrawl` | L384-429 | 46 | 10 | 1 | 2 | ✓ |
| `search_external_resources` | L231-261 | 31 | 7 | 2 | 6 | ✓ |
| `_guess_resource_type` | L80-91 | 12 | 6 | 1 | 2 | ✓ |
| `_mastery_stage` | L53-64 | 12 | 5 | 1 | 1 | ✓ |
| `_resource_id` | L44-50 | 7 | 3 | 1 | 1 | ✓ |
| `_external_search_enabled` | L263-270 | 8 | 3 | 0 | 1 | ✓ |
| `_firecrawl_enabled` | L272-279 | 8 | 3 | 0 | 1 | ✓ |
| `_extract_exa_snippet` | L374-382 | 9 | 3 | 2 | 2 | ✓ |
| `_coerce_text` | L38-41 | 4 | 2 | 0 | 1 | ✓ |
| `_is_valid_http_url` | L67-71 | 5 | 2 | 0 | 1 | ✓ |
| `_truncate_text` | L94-100 | 7 | 2 | 1 | 2 | ✓ |
| `__init__` | L154-157 | 4 | 2 | 0 | 2 | ✓ |
| `_build_search_query` | L281-292 | 12 | 2 | 0 | 4 | ✓ |
| `_domain_from_url` | L74-77 | 4 | 1 | 0 | 1 | ✓ |
| `resource_id` | L112-115 | 4 | 1 | 0 | 1 | ✓ |
| `to_response` | L131-148 | 18 | 1 | 0 | 1 | ✓ |

**全部问题 (21)**

- 🔄 `search_internal_resources()` L159: 复杂度: 14
- 🔄 `_search_with_exa()` L294: 复杂度: 13
- 🔄 `search_internal_resources()` L159: 认知复杂度: 20
- 🔄 `_search_with_exa()` L294: 认知复杂度: 17
- 📏 `search_internal_resources()` L159: 71 代码量
- 📏 `_search_with_exa()` L294: 79 代码量
- 📏 `search_external_resources()` L231: 6 参数数量
- 📏 `_search_with_exa()` L294: 6 参数数量
- 📋 `_truncate_text()` L94: 重复模式: _truncate_text, _extract_exa_snippet
- 🏗️ `search_internal_resources()` L159: 中等嵌套: 3
- ❌ L218: 未处理的易出错调用
- 🏷️ `_coerce_text()` L38: "_coerce_text" - snake_case
- 🏷️ `_resource_id()` L44: "_resource_id" - snake_case
- 🏷️ `_mastery_stage()` L53: "_mastery_stage" - snake_case
- 🏷️ `_is_valid_http_url()` L67: "_is_valid_http_url" - snake_case
- 🏷️ `_domain_from_url()` L74: "_domain_from_url" - snake_case
- 🏷️ `_guess_resource_type()` L80: "_guess_resource_type" - snake_case
- 🏷️ `_truncate_text()` L94: "_truncate_text" - snake_case
- 🏷️ `__init__()` L154: "__init__" - snake_case
- 🏷️ `_external_search_enabled()` L263: "_external_search_enabled" - snake_case
- 🏷️ `_firecrawl_enabled()` L272: "_firecrawl_enabled" - snake_case

**详情**:
- 循环复杂度: 平均: 4.4, 最大: 14
- 认知复杂度: 平均: 6.0, 最大: 20
- 嵌套深度: 平均: 0.8, 最大: 3
- 函数长度: 平均: 18.9 行, 最大: 79 行
- 文件长度: 359 代码量 (433 总计)
- 参数数量: 平均: 2.2, 最大: 6
- 代码重复: 5.6% 重复 (1/18)
- 结构分析: 1 个结构问题
- 错误处理: 1/18 个错误被忽略 (5.6%)
- 注释比例: 0.0% (0/359)
- 命名规范: 发现 14 个违规

### 38. backend\assessments\status_profile_views.py

**糟糕指数: 17.42**

> 行数: 129 总计, 108 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_assessment_status` | L21-86 | 66 | 13 | 2 | 1 | ✓ |
| `generate_course_profile` | L91-128 | 38 | 6 | 1 | 1 | ✓ |

**全部问题 (7)**

- 🔄 `get_assessment_status()` L21: 复杂度: 13
- 🔄 `get_assessment_status()` L21: 认知复杂度: 17
- 📏 `get_assessment_status()` L21: 66 代码量
- ❌ L117: 未处理的易出错调用
- ❌ L122: 未处理的易出错调用
- ❌ L123: 未处理的易出错调用
- ❌ L124: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 9.5, 最大: 13
- 认知复杂度: 平均: 12.5, 最大: 17
- 嵌套深度: 平均: 1.5, 最大: 2
- 函数长度: 平均: 52.0 行, 最大: 66 行
- 文件长度: 108 代码量 (129 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 4/8 个错误被忽略 (50.0%)
- 注释比例: 0.0% (0/108)
- 命名规范: 无命名违规

### 39. backend\tools\cli_parser.py

**糟糕指数: 17.32**

> 行数: 368 总计, 317 代码, 2 注释 | 函数: 8 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_dispatch_import_commands` | L229-261 | 33 | 15 | 1 | 1 | ✓ |
| `_dispatch_data_admin_commands` | L264-292 | 29 | 13 | 1 | 1 | ✓ |
| `_dispatch_test_commands` | L295-317 | 23 | 10 | 1 | 1 | ✓ |
| `_dispatch_training_commands` | L320-352 | 33 | 8 | 1 | 1 | ✓ |
| `dispatch_command` | L363-367 | 5 | 3 | 2 | 1 | ✓ |
| `_parse_model_filters` | L222-226 | 5 | 2 | 1 | 1 | ✓ |
| `_add_json_import_args` | L44-49 | 6 | 1 | 0 | 1 | ✓ |
| `build_parser` | L52-219 | 168 | 1 | 0 | 0 | ✓ |

**全部问题 (12)**

- 🔄 `_dispatch_import_commands()` L229: 复杂度: 15
- 🔄 `_dispatch_data_admin_commands()` L264: 复杂度: 13
- 🔄 `_dispatch_import_commands()` L229: 认知复杂度: 17
- 🔄 `_dispatch_data_admin_commands()` L264: 认知复杂度: 15
- 📏 `build_parser()` L52: 168 代码量
- 🏗️ L1: 导入过多: 24
- 🏷️ `_add_json_import_args()` L44: "_add_json_import_args" - snake_case
- 🏷️ `_parse_model_filters()` L222: "_parse_model_filters" - snake_case
- 🏷️ `_dispatch_import_commands()` L229: "_dispatch_import_commands" - snake_case
- 🏷️ `_dispatch_data_admin_commands()` L264: "_dispatch_data_admin_commands" - snake_case
- 🏷️ `_dispatch_test_commands()` L295: "_dispatch_test_commands" - snake_case
- 🏷️ `_dispatch_training_commands()` L320: "_dispatch_training_commands" - snake_case

**详情**:
- 循环复杂度: 平均: 6.6, 最大: 15
- 认知复杂度: 平均: 8.4, 最大: 17
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 37.8 行, 最大: 168 行
- 文件长度: 317 代码量 (368 总计)
- 参数数量: 平均: 0.9, 最大: 1
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.6% (2/317)
- 命名规范: 发现 6 个违规

### 40. backend\assessments\knowledge_assessment_logic.py

**糟糕指数: 17.08**

> 行数: 332 总计, 291 代码, 0 注释 | 函数: 9 | 类: 1

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 2, 📋 重复问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_feedback_report_payload` | L279-296 | 18 | 11 | 1 | 1 | ✓ |
| `is_answer_correct` | L65-88 | 24 | 9 | 1 | 3 | ✓ |
| `evaluate_knowledge_answers` | L167-235 | 69 | 7 | 3 | 4 | ✓ |
| `blend_mastery_with_kt` | L238-276 | 39 | 6 | 2 | 5 | ✓ |
| `normalize_bool_answer` | L44-55 | 12 | 5 | 1 | 1 | ✓ |
| `build_answer_history_models` | L125-164 | 40 | 4 | 1 | 7 | ✓ |
| `resolve_correct_answer_payload` | L58-62 | 5 | 2 | 1 | 1 | ✓ |
| `build_question_detail_payload` | L91-122 | 32 | 1 | 0 | 5 | ✓ |
| `build_empty_knowledge_result` | L299-317 | 19 | 1 | 0 | 3 | ✓ |

**全部问题 (9)**

- 🔄 `build_feedback_report_payload()` L279: 复杂度: 11
- 🔄 `evaluate_knowledge_answers()` L167: 认知复杂度: 13
- 🔄 `build_feedback_report_payload()` L279: 认知复杂度: 13
- 📏 `evaluate_knowledge_answers()` L167: 69 代码量
- 📏 `build_answer_history_models()` L125: 7 参数数量
- 📋 `build_question_detail_payload()` L91: 重复模式: build_question_detail_payload, build_empty_knowledge_result
- 🏗️ `evaluate_knowledge_answers()` L167: 中等嵌套: 3
- ❌ L288: 未处理的易出错调用
- ❌ L290: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.1, 最大: 11
- 认知复杂度: 平均: 7.3, 最大: 13
- 嵌套深度: 平均: 1.1, 最大: 3
- 函数长度: 平均: 28.7 行, 最大: 69 行
- 文件长度: 291 代码量 (332 总计)
- 参数数量: 平均: 3.3, 最大: 7
- 代码重复: 11.1% 重复 (1/9)
- 结构分析: 1 个结构问题
- 错误处理: 2/7 个错误被忽略 (28.6%)
- 注释比例: 0.0% (0/291)
- 命名规范: 无命名违规

### 41. backend\ai_services\student_ai_chat_views.py

**糟糕指数: 17.07**

> 行数: 140 总计, 121 代码, 0 注释 | 函数: 5 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 📋 重复问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_chat_response` | L19-67 | 49 | 11 | 2 | 6 | ✓ |
| `ai_chat` | L72-92 | 21 | 7 | 1 | 1 | ✓ |
| `ai_graph_rag_search` | L104-119 | 16 | 6 | 1 | 1 | ✓ |
| `ai_graph_rag_ask` | L124-139 | 16 | 6 | 1 | 1 | ✓ |
| `ai_knowledge_graph_query` | L97-99 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `build_chat_response()` L19: 复杂度: 11
- 🔄 `build_chat_response()` L19: 认知复杂度: 15
- 📏 `build_chat_response()` L19: 6 参数数量
- 📋 `ai_graph_rag_search()` L104: 重复模式: ai_graph_rag_search, ai_graph_rag_ask

**详情**:
- 循环复杂度: 平均: 6.2, 最大: 11
- 认知复杂度: 平均: 8.2, 最大: 15
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 21.0 行, 最大: 49 行
- 文件长度: 121 代码量 (140 总计)
- 参数数量: 平均: 2.0, 最大: 6
- 代码重复: 20.0% 重复 (1/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/12 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/121)
- 命名规范: 无命名违规

### 42. backend\platform_ai\rag\runtime_search_mixin.py

**糟糕指数: 16.98**

> 行数: 226 总计, 206 代码, 0 注释 | 函数: 6 | 类: 1

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `search_points` | L180-225 | 46 | 11 | 4 | 4 | ✓ |
| `_search_qdrant_only` | L89-121 | 33 | 10 | 1 | 4 | ✓ |
| `_format_retriever_record` | L45-62 | 18 | 9 | 0 | 2 | ✓ |
| `_parse_items` | L64-87 | 24 | 9 | 2 | 2 | ✓ |
| `search_documents` | L123-178 | 56 | 9 | 1 | 5 | ✓ |
| `_retrieval_query` | L25-43 | 19 | 1 | 0 | 1 | ✓ |

**全部问题 (13)**

- 🔄 `search_points()` L180: 复杂度: 11
- 🔄 `_parse_items()` L64: 认知复杂度: 13
- 🔄 `search_points()` L180: 认知复杂度: 19
- 🔄 `search_points()` L180: 嵌套深度: 4
- 📏 `search_documents()` L123: 56 代码量
- 🏗️ `search_points()` L180: 中等嵌套: 4
- ❌ L220: 未处理的易出错调用
- ❌ L221: 未处理的易出错调用
- ❌ L222: 未处理的易出错调用
- 🏷️ `_retrieval_query()` L25: "_retrieval_query" - snake_case
- 🏷️ `_format_retriever_record()` L45: "_format_retriever_record" - snake_case
- 🏷️ `_parse_items()` L64: "_parse_items" - snake_case
- 🏷️ `_search_qdrant_only()` L89: "_search_qdrant_only" - snake_case

**详情**:
- 循环复杂度: 平均: 8.2, 最大: 11
- 认知复杂度: 平均: 10.8, 最大: 19
- 嵌套深度: 平均: 1.3, 最大: 4
- 函数长度: 平均: 32.7 行, 最大: 56 行
- 文件长度: 206 代码量 (226 总计)
- 参数数量: 平均: 3.0, 最大: 5
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 1 个结构问题
- 错误处理: 3/24 个错误被忽略 (12.5%)
- 注释比例: 0.0% (0/206)
- 命名规范: 发现 4 个违规

### 43. backend\common\defense_demo_assessment_state.py

**糟糕指数: 16.96**

> 行数: 229 总计, 195 代码, 10 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_demo_student_answer` | L96-145 | 50 | 11 | 3 | 2 | ✓ |
| `_seed_demo_practice_histories` | L148-228 | 81 | 7 | 2 | 4 | ✓ |
| `_ensure_demo_assessment_state` | L34-93 | 60 | 1 | 0 | 4 | ✓ |

**全部问题 (12)**

- 🔄 `_build_demo_student_answer()` L96: 复杂度: 11
- 🔄 `_build_demo_student_answer()` L96: 认知复杂度: 17
- 📏 `_ensure_demo_assessment_state()` L34: 60 代码量
- 📏 `_seed_demo_practice_histories()` L148: 81 代码量
- 🏗️ `_build_demo_student_answer()` L96: 中等嵌套: 3
- ❌ L112: 未处理的易出错调用
- ❌ L114: 未处理的易出错调用
- ❌ L134: 未处理的易出错调用
- ❌ L205: 未处理的易出错调用
- 🏷️ `_ensure_demo_assessment_state()` L34: "_ensure_demo_assessment_state" - snake_case
- 🏷️ `_build_demo_student_answer()` L96: "_build_demo_student_answer" - snake_case
- 🏷️ `_seed_demo_practice_histories()` L148: "_seed_demo_practice_histories" - snake_case

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 11
- 认知复杂度: 平均: 9.7, 最大: 17
- 嵌套深度: 平均: 1.7, 最大: 3
- 函数长度: 平均: 63.7 行, 最大: 81 行
- 文件长度: 195 代码量 (229 总计)
- 参数数量: 平均: 3.3, 最大: 4
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 1 个结构问题
- 错误处理: 4/8 个错误被忽略 (50.0%)
- 注释比例: 5.1% (10/195)
- 命名规范: 发现 3 个违规

### 44. backend\common\defense_demo_assessment_support.py

**糟糕指数: 16.87**

> 行数: 334 总计, 304 代码, 0 注释 | 函数: 8 | 类: 1

**问题**: ⚠️ 其他问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_load_demo_assessment_defaults` | L36-116 | 81 | 7 | 1 | 1 | ✓ |
| `_build_demo_mastery_map` | L211-229 | 19 | 6 | 3 | 2 | ✓ |
| `_upsert_demo_assessment_feedback` | L292-333 | 42 | 4 | 0 | 7 | ✓ |
| `_ensure_demo_knowledge_assessment` | L152-180 | 29 | 3 | 1 | 2 | ✓ |
| `_refresh_demo_answer_histories` | L183-208 | 26 | 3 | 1 | 5 | ✓ |
| `_persist_demo_mastery_records` | L232-245 | 14 | 2 | 1 | 4 | ✓ |
| `_upsert_demo_assessment_result` | L248-289 | 42 | 2 | 0 | 9 | ✓ |
| `_seed_demo_profile_state` | L119-149 | 31 | 1 | 0 | 3 | ✓ |

**全部问题 (14)**

- 📏 `_load_demo_assessment_defaults()` L36: 81 代码量
- 📏 `_upsert_demo_assessment_result()` L248: 9 参数数量
- 📏 `_upsert_demo_assessment_feedback()` L292: 7 参数数量
- 🏗️ `_build_demo_mastery_map()` L211: 中等嵌套: 3
- ❌ L173: 未处理的易出错调用
- ❌ L279: 未处理的易出错调用
- 🏷️ `_load_demo_assessment_defaults()` L36: "_load_demo_assessment_defaults" - snake_case
- 🏷️ `_seed_demo_profile_state()` L119: "_seed_demo_profile_state" - snake_case
- 🏷️ `_ensure_demo_knowledge_assessment()` L152: "_ensure_demo_knowledge_assessment" - snake_case
- 🏷️ `_refresh_demo_answer_histories()` L183: "_refresh_demo_answer_histories" - snake_case
- 🏷️ `_build_demo_mastery_map()` L211: "_build_demo_mastery_map" - snake_case
- 🏷️ `_persist_demo_mastery_records()` L232: "_persist_demo_mastery_records" - snake_case
- 🏷️ `_upsert_demo_assessment_result()` L248: "_upsert_demo_assessment_result" - snake_case
- 🏷️ `_upsert_demo_assessment_feedback()` L292: "_upsert_demo_assessment_feedback" - snake_case

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 7
- 认知复杂度: 平均: 5.3, 最大: 12
- 嵌套深度: 平均: 0.9, 最大: 3
- 函数长度: 平均: 35.5 行, 最大: 81 行
- 文件长度: 304 代码量 (334 总计)
- 参数数量: 平均: 4.1, 最大: 9
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 2/10 个错误被忽略 (20.0%)
- 注释比例: 0.0% (0/304)
- 命名规范: 发现 8 个违规

### 45. backend\assessments\knowledge_views.py

**糟糕指数: 16.75**

> 行数: 286 总计, 253 代码, 0 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_knowledge_result` | L229-285 | 57 | 11 | 2 | 1 | ✓ |
| `submit_knowledge_assessment` | L127-224 | 98 | 9 | 2 | 1 | ✓ |
| `get_knowledge_assessment` | L51-122 | 72 | 7 | 2 | 1 | ✓ |

**全部问题 (10)**

- 🔄 `get_knowledge_result()` L229: 复杂度: 11
- 🔄 `submit_knowledge_assessment()` L127: 认知复杂度: 13
- 🔄 `get_knowledge_result()` L229: 认知复杂度: 15
- 📏 `get_knowledge_assessment()` L51: 72 代码量
- 📏 `submit_knowledge_assessment()` L127: 98 代码量
- 📏 `get_knowledge_result()` L229: 57 代码量
- ❌ L276: 未处理的易出错调用
- ❌ L277: 未处理的易出错调用
- ❌ L278: 未处理的易出错调用
- ❌ L280: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 9.0, 最大: 11
- 认知复杂度: 平均: 13.0, 最大: 15
- 嵌套深度: 平均: 2.0, 最大: 2
- 函数长度: 平均: 75.7 行, 最大: 98 行
- 文件长度: 253 代码量 (286 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 4/12 个错误被忽略 (33.3%)
- 注释比例: 0.0% (0/253)
- 命名规范: 无命名违规

### 46. backend\ai_services\services\web_search_service.py

**糟糕指数: 16.51**

> 行数: 279 总计, 232 代码, 0 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_search_with_provider` | L141-189 | 49 | 12 | 2 | 4 | ✗ |
| `search_learning_resources` | L192-278 | 87 | 10 | 3 | 3 | ✓ |
| `_resolve_result_url` | L107-138 | 32 | 9 | 2 | 2 | ✗ |
| `_guess_resource_type` | L67-76 | 10 | 4 | 1 | 2 | ✗ |
| `_normalize_candidate_url` | L59-64 | 6 | 3 | 1 | 1 | ✗ |
| `_clean_html_text` | L51-56 | 6 | 2 | 1 | 1 | ✗ |
| `_is_accessible_url` | L79-93 | 15 | 2 | 1 | 2 | ✗ |
| `_matches_expected_domain` | L101-104 | 4 | 2 | 0 | 2 | ✗ |
| `_is_search_engine_url` | L96-98 | 3 | 1 | 0 | 1 | ✗ |

**全部问题 (17)**

- 🔄 `_search_with_provider()` L141: 复杂度: 12
- 🔄 `_resolve_result_url()` L107: 认知复杂度: 13
- 🔄 `_search_with_provider()` L141: 认知复杂度: 16
- 🔄 `search_learning_resources()` L192: 认知复杂度: 16
- 📏 `search_learning_resources()` L192: 87 代码量
- 🏗️ `search_learning_resources()` L192: 中等嵌套: 3
- ❌ L89: 未处理的易出错调用
- ❌ L128: 未处理的易出错调用
- ❌ L248: 未处理的易出错调用
- 🏷️ `_clean_html_text()` L51: "_clean_html_text" - snake_case
- 🏷️ `_normalize_candidate_url()` L59: "_normalize_candidate_url" - snake_case
- 🏷️ `_guess_resource_type()` L67: "_guess_resource_type" - snake_case
- 🏷️ `_is_accessible_url()` L79: "_is_accessible_url" - snake_case
- 🏷️ `_is_search_engine_url()` L96: "_is_search_engine_url" - snake_case
- 🏷️ `_matches_expected_domain()` L101: "_matches_expected_domain" - snake_case
- 🏷️ `_resolve_result_url()` L107: "_resolve_result_url" - snake_case
- 🏷️ `_search_with_provider()` L141: "_search_with_provider" - snake_case

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 12
- 认知复杂度: 平均: 7.4, 最大: 16
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 23.6 行, 最大: 87 行
- 文件长度: 232 代码量 (279 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 3/6 个错误被忽略 (50.0%)
- 注释比例: 0.0% (0/232)
- 命名规范: 发现 8 个违规

### 47. backend\models\MEFKT\attribute.py

**糟糕指数: 16.18**

> 行数: 198 总计, 176 代码, 0 注释 | 函数: 3 | 类: 2

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `forward` | L103-194 | 92 | 9 | 2 | 9 | ✓ |
| `_build_default_relation_stats` | L73-101 | 29 | 3 | 1 | 4 | ✓ |
| `__init__` | L26-71 | 46 | 2 | 0 | 5 | ✓ |

**全部问题 (5)**

- 🔄 `forward()` L103: 认知复杂度: 13
- 📏 `forward()` L103: 92 代码量
- 📏 `forward()` L103: 9 参数数量
- 🏷️ `__init__()` L26: "__init__" - snake_case
- 🏷️ `_build_default_relation_stats()` L73: "_build_default_relation_stats" - snake_case

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 9
- 认知复杂度: 平均: 6.7, 最大: 13
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 55.7 行, 最大: 92 行
- 文件长度: 176 代码量 (198 总计)
- 参数数量: 平均: 6.0, 最大: 9
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/176)
- 命名规范: 发现 2 个违规

### 48. backend\exams\report_service_support.py

**糟糕指数: 16.07**

> 行数: 182 总计, 164 代码, 0 注释 | 函数: 4 | 类: 2

**问题**: ⚠️ 其他问题: 3, ❌ 错误处理问题: 4, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_report_generation_context` | L39-90 | 52 | 7 | 0 | 10 | ✓ |
| `normalize_llm_feedback` | L93-117 | 25 | 5 | 1 | 3 | ✓ |
| `apply_completed_report` | L154-181 | 28 | 5 | 0 | 5 | ✓ |
| `build_report_overview` | L120-151 | 32 | 2 | 0 | 12 | ✓ |

**全部问题 (7)**

- 📏 `build_report_generation_context()` L39: 52 代码量
- 📏 `build_report_generation_context()` L39: 10 参数数量
- 📏 `build_report_overview()` L120: 12 参数数量
- ❌ L106: 未处理的易出错调用
- ❌ L150: 未处理的易出错调用
- ❌ L171: 未处理的易出错调用
- ❌ L172: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 7
- 认知复杂度: 平均: 5.3, 最大: 7
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 34.3 行, 最大: 52 行
- 文件长度: 164 代码量 (182 总计)
- 参数数量: 平均: 7.5, 最大: 12
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 4/6 个错误被忽略 (66.7%)
- 注释比例: 0.0% (0/164)
- 命名规范: 无命名违规

### 49. backend\logs\middleware.py

**糟糕指数: 15.93**

> 行数: 483 总计, 392 代码, 17 注释 | 函数: 13 | 类: 1

**问题**: 🔄 复杂度问题: 6, ⚠️ 其他问题: 3, 🏗️ 结构问题: 5, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_log_debug_info` | L356-422 | 67 | 13 | 2 | 3 | ✓ |
| `get_request_params` | L233-275 | 43 | 9 | 4 | 2 | ✓ |
| `_mask_sensitive_data` | L337-354 | 18 | 8 | 3 | 3 | ✓ |
| `get_response_content` | L277-302 | 26 | 7 | 3 | 2 | ✓ |
| `process_response` | L424-482 | 59 | 7 | 2 | 3 | ✓ |
| `process_request` | L137-157 | 21 | 6 | 3 | 2 | ✓ |
| `get_action_type` | L175-195 | 21 | 6 | 1 | 2 | ✓ |
| `should_debug_log` | L117-135 | 19 | 5 | 2 | 2 | ✓ |
| `get_module` | L159-173 | 15 | 5 | 2 | 2 | ✓ |
| `get_request_headers` | L210-231 | 22 | 5 | 3 | 2 | ✓ |
| `get_db_queries` | L304-335 | 32 | 5 | 1 | 2 | ✓ |
| `should_log` | L100-115 | 16 | 4 | 2 | 2 | ✓ |
| `get_client_ip` | L197-208 | 12 | 2 | 1 | 2 | ✓ |

**全部问题 (19)**

- 🔄 `_log_debug_info()` L356: 复杂度: 13
- 🔄 `get_request_params()` L233: 认知复杂度: 17
- 🔄 `get_response_content()` L277: 认知复杂度: 13
- 🔄 `_mask_sensitive_data()` L337: 认知复杂度: 14
- 🔄 `_log_debug_info()` L356: 认知复杂度: 17
- 🔄 `get_request_params()` L233: 嵌套深度: 4
- 📏 `_log_debug_info()` L356: 67 代码量
- 📏 `process_response()` L424: 59 代码量
- 🏗️ `process_request()` L137: 中等嵌套: 3
- 🏗️ `get_request_headers()` L210: 中等嵌套: 3
- 🏗️ `get_request_params()` L233: 中等嵌套: 4
- 🏗️ `get_response_content()` L277: 中等嵌套: 3
- 🏗️ `_mask_sensitive_data()` L337: 中等嵌套: 3
- ❌ L294: 未处理的易出错调用
- ❌ L322: 未处理的易出错调用
- ❌ L323: 未处理的易出错调用
- ❌ L449: 未处理的易出错调用
- 🏷️ `_mask_sensitive_data()` L337: "_mask_sensitive_data" - snake_case
- 🏷️ `_log_debug_info()` L356: "_log_debug_info" - snake_case

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 13
- 认知复杂度: 平均: 10.8, 最大: 17
- 嵌套深度: 平均: 2.2, 最大: 4
- 函数长度: 平均: 28.5 行, 最大: 67 行
- 文件长度: 392 代码量 (483 总计)
- 参数数量: 平均: 2.2, 最大: 3
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 5 个结构问题
- 错误处理: 4/13 个错误被忽略 (30.8%)
- 注释比例: 4.3% (17/392)
- 命名规范: 发现 2 个违规

### 50. backend\common\defense_demo_assessment_questions.py

**糟糕指数: 15.90**

> 行数: 265 总计, 235 代码, 7 注释 | 函数: 3 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_planned_answer_value` | L156-195 | 40 | 8 | 1 | 2 | ✓ |
| `_build_assessment_report_payload` | L198-264 | 67 | 7 | 2 | 2 | ✓ |
| `_ensure_demo_assessment_questions` | L18-153 | 136 | 3 | 1 | 3 | ✓ |

**全部问题 (8)**

- 📏 `_ensure_demo_assessment_questions()` L18: 136 代码量
- 📏 `_build_assessment_report_payload()` L198: 67 代码量
- ❌ L176: 未处理的易出错调用
- ❌ L178: 未处理的易出错调用
- ❌ L190: 未处理的易出错调用
- 🏷️ `_ensure_demo_assessment_questions()` L18: "_ensure_demo_assessment_questions" - snake_case
- 🏷️ `_build_planned_answer_value()` L156: "_build_planned_answer_value" - snake_case
- 🏷️ `_build_assessment_report_payload()` L198: "_build_assessment_report_payload" - snake_case

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 8
- 认知复杂度: 平均: 8.7, 最大: 11
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 81.0 行, 最大: 136 行
- 文件长度: 235 代码量 (265 总计)
- 参数数量: 平均: 2.3, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 3/4 个错误被忽略 (75.0%)
- 注释比例: 3.0% (7/235)
- 命名规范: 发现 3 个违规

### 51. backend\tools\mefkt_training.py

**糟糕指数: 15.66**

> 行数: 181 总计, 155 代码, 2 注释 | 函数: 7 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 7, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `train_mefkt_v2` | L60-102 | 43 | 5 | 1 | 17 | ✓ |
| `build_training_bundle` | L105-128 | 24 | 3 | 1 | 3 | ✓ |
| `resolve_mefkt_output_path` | L131-137 | 7 | 3 | 1 | 2 | ✓ |
| `mefkt_status` | L150-171 | 22 | 2 | 1 | 0 | ✓ |
| `_train_mefkt_bundle` | L24-57 | 34 | 1 | 0 | 13 | ✓ |
| `print_training_result` | L140-147 | 8 | 1 | 0 | 1 | ✓ |
| `print_mefkt_status` | L174-177 | 4 | 1 | 0 | 1 | ✓ |

**全部问题 (10)**

- 📏 `_train_mefkt_bundle()` L24: 13 参数数量
- 📏 `train_mefkt_v2()` L60: 17 参数数量
- ❌ L164: 未处理的易出错调用
- ❌ L165: 未处理的易出错调用
- ❌ L166: 未处理的易出错调用
- ❌ L167: 未处理的易出错调用
- ❌ L168: 未处理的易出错调用
- ❌ L169: 未处理的易出错调用
- ❌ L170: 未处理的易出错调用
- 🏷️ `_train_mefkt_bundle()` L24: "_train_mefkt_bundle" - snake_case

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 5
- 认知复杂度: 平均: 3.4, 最大: 7
- 嵌套深度: 平均: 0.6, 最大: 1
- 函数长度: 平均: 20.3 行, 最大: 43 行
- 文件长度: 155 代码量 (181 总计)
- 参数数量: 平均: 5.3, 最大: 17
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 7/7 个错误被忽略 (100.0%)
- 注释比例: 1.3% (2/155)
- 命名规范: 发现 1 个违规

### 52. backend\tools\bootstrap_support.py

**糟糕指数: 15.48**

> 行数: 340 总计, 288 代码, 2 注释 | 函数: 14 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_bundle_question_assets` | L158-206 | 49 | 12 | 3 | 4 | ✓ |
| `import_media_resources` | L81-127 | 47 | 7 | 2 | 7 | ✓ |
| `collect_batch_candidates` | L307-339 | 27 | 7 | 2 | 2 | ✓ |
| `finalize_bootstrap_course` | L259-275 | 17 | 6 | 2 | 3 | ✓ |
| `resolve_batch_resource_root` | L285-304 | 20 | 6 | 1 | 0 | ✓ |
| `import_bundle_knowledge_assets` | L130-155 | 26 | 5 | 2 | 4 | ✓ |
| `import_bundle_media_assets` | L228-256 | 29 | 4 | 2 | 4 | ✓ |
| `copy_to_media` | L47-63 | 17 | 3 | 2 | 2 | ✓ |
| `import_bundle_resource_assets` | L209-225 | 17 | 3 | 1 | 4 | ✓ |
| `enqueue` | L320-325 | 6 | 3 | 1 | 2 | ✗ |
| `ensure_teacher` | L26-31 | 6 | 2 | 1 | 1 | ✓ |
| `ensure_course_record` | L34-44 | 11 | 2 | 1 | 2 | ✓ |
| `resolve_resources_root` | L278-282 | 5 | 2 | 1 | 1 | ✓ |
| `bundle_has_importable_assets` | L66-78 | 13 | 1 | 0 | 1 | ✓ |

**全部问题 (5)**

- 🔄 `import_bundle_question_assets()` L158: 复杂度: 12
- 🔄 `import_bundle_question_assets()` L158: 认知复杂度: 18
- 📏 `import_media_resources()` L81: 7 参数数量
- 🏗️ `import_bundle_question_assets()` L158: 中等嵌套: 3
- ❌ L114: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 12
- 认知复杂度: 平均: 7.5, 最大: 18
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 20.7 行, 最大: 49 行
- 文件长度: 288 代码量 (340 总计)
- 参数数量: 平均: 2.6, 最大: 7
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 1 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 0.7% (2/288)
- 命名规范: 无命名违规

### 53. backend\tools\demo_course_archive.py

**糟糕指数: 15.39**

> 行数: 98 总计, 73 代码, 3 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_demo_course_archive` | L48-97 | 50 | 12 | 4 | 2 | ✓ |
| `_resolve_output_path` | L33-45 | 13 | 3 | 1 | 1 | ✓ |
| `_copy_file_to_dir` | L21-30 | 10 | 2 | 0 | 3 | ✓ |

**全部问题 (7)**

- 🔄 `generate_demo_course_archive()` L48: 复杂度: 12
- 🔄 `generate_demo_course_archive()` L48: 认知复杂度: 20
- 🔄 `generate_demo_course_archive()` L48: 嵌套深度: 4
- 🏗️ `generate_demo_course_archive()` L48: 中等嵌套: 4
- ❌ L92: 未处理的易出错调用
- 🏷️ `_copy_file_to_dir()` L21: "_copy_file_to_dir" - snake_case
- 🏷️ `_resolve_output_path()` L33: "_resolve_output_path" - snake_case

**详情**:
- 循环复杂度: 平均: 5.7, 最大: 12
- 认知复杂度: 平均: 9.0, 最大: 20
- 嵌套深度: 平均: 1.7, 最大: 4
- 函数长度: 平均: 24.3 行, 最大: 50 行
- 文件长度: 73 代码量 (98 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 1 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 4.1% (3/73)
- 命名规范: 发现 2 个违规

### 54. backend\knowledge\services.py

**糟糕指数: 15.39**

> 行数: 101 总计, 81 代码, 0 注释 | 函数: 2 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_or_generate_point_intro` | L38-100 | 63 | 14 | 1 | 1 | ✓ |
| `build_intro_fallback` | L24-35 | 12 | 4 | 0 | 1 | ✓ |

**全部问题 (5)**

- 🔄 `get_or_generate_point_intro()` L38: 复杂度: 14
- 🔄 `get_or_generate_point_intro()` L38: 认知复杂度: 16
- 📏 `get_or_generate_point_intro()` L38: 63 代码量
- ❌ L95: 未处理的易出错调用
- ❌ L97: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 9.0, 最大: 14
- 认知复杂度: 平均: 10.0, 最大: 16
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 37.5 行, 最大: 63 行
- 文件长度: 81 代码量 (101 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 2/5 个错误被忽略 (40.0%)
- 注释比例: 0.0% (0/81)
- 命名规范: 无命名违规

### 55. backend\wisdom_edu_api\settings_ai.py

**糟糕指数: 15.38**

> 行数: 209 总计, 193 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_load_llm_settings` | L130-208 | 79 | 15 | 1 | 5 | ✓ |
| `_load_graph_and_resource_settings` | L60-127 | 68 | 4 | 0 | 3 | ✓ |
| `_int_setting` | L16-28 | 13 | 2 | 1 | 5 | ✓ |
| `load_ai_settings` | L31-57 | 27 | 1 | 0 | 5 | ✓ |

**全部问题 (7)**

- 🔄 `_load_llm_settings()` L130: 复杂度: 15
- 🔄 `_load_llm_settings()` L130: 认知复杂度: 17
- 📏 `_load_graph_and_resource_settings()` L60: 68 代码量
- 📏 `_load_llm_settings()` L130: 79 代码量
- 🏷️ `_int_setting()` L16: "_int_setting" - snake_case
- 🏷️ `_load_graph_and_resource_settings()` L60: "_load_graph_and_resource_settings" - snake_case
- 🏷️ `_load_llm_settings()` L130: "_load_llm_settings" - snake_case

**详情**:
- 循环复杂度: 平均: 5.5, 最大: 15
- 认知复杂度: 平均: 6.5, 最大: 17
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 46.8 行, 最大: 79 行
- 文件长度: 193 代码量 (209 总计)
- 参数数量: 平均: 4.5, 最大: 5
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/193)
- 命名规范: 发现 3 个违规

### 56. backend\platform_ai\rag\corpus_builder.py

**糟糕指数: 15.32**

> 行数: 442 总计, 397 代码, 0 注释 | 函数: 19 | 类: 1

**问题**: ⚠️ 其他问题: 3, 📋 重复问题: 1, 🏗️ 结构问题: 3, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_point_summary` | L69-83 | 15 | 7 | 0 | 2 | ✓ |
| `_build_community_records` | L343-415 | 73 | 6 | 2 | 1 | ✓ |
| `_populate_resources` | L218-264 | 47 | 5 | 3 | 1 | ✓ |
| `_populate_questions` | L267-314 | 48 | 5 | 3 | 1 | ✓ |
| `_link_chapter_members` | L317-331 | 15 | 5 | 3 | 1 | ✓ |
| `_populate_knowledge_relations` | L197-215 | 19 | 4 | 2 | 1 | ✓ |
| `remember_chapter_member` | L29-34 | 6 | 3 | 0 | 3 | ✓ |
| `_resource_summary` | L86-96 | 11 | 3 | 0 | 3 | ✓ |
| `_question_summary` | L99-109 | 11 | 3 | 0 | 2 | ✓ |
| `_populate_points` | L133-166 | 34 | 3 | 1 | 2 | ✓ |
| `_detect_communities` | L334-340 | 7 | 3 | 1 | 1 | ✓ |
| `_populate_chapters` | L169-194 | 26 | 2 | 1 | 1 | ✓ |
| `add_entity` | L36-40 | 5 | 1 | 0 | 3 | ✓ |
| `add_relationship` | L42-61 | 20 | 1 | 0 | 6 | ✓ |
| `_join_nonempty` | L64-66 | 3 | 1 | 0 | 1 | ✓ |
| `_published_points` | L112-116 | 5 | 1 | 0 | 1 | ✓ |
| `_visible_resources` | L119-121 | 3 | 1 | 0 | 1 | ✓ |
| `_visible_questions` | L124-130 | 7 | 1 | 0 | 1 | ✓ |
| `build_course_graph_payload` | L418-438 | 21 | 1 | 0 | 1 | ✓ |

**全部问题 (17)**

- 📏 `_build_community_records()` L343: 73 代码量
- 📏 `add_relationship()` L42: 6 参数数量
- 📋 `_populate_resources()` L218: 重复模式: _populate_resources, _populate_questions
- 🏗️ `_populate_resources()` L218: 中等嵌套: 3
- 🏗️ `_populate_questions()` L267: 中等嵌套: 3
- 🏗️ `_link_chapter_members()` L317: 中等嵌套: 3
- ❌ L173: 未处理的易出错调用
- 🏷️ `_join_nonempty()` L64: "_join_nonempty" - snake_case
- 🏷️ `_point_summary()` L69: "_point_summary" - snake_case
- 🏷️ `_resource_summary()` L86: "_resource_summary" - snake_case
- 🏷️ `_question_summary()` L99: "_question_summary" - snake_case
- 🏷️ `_published_points()` L112: "_published_points" - snake_case
- 🏷️ `_visible_resources()` L119: "_visible_resources" - snake_case
- 🏷️ `_visible_questions()` L124: "_visible_questions" - snake_case
- 🏷️ `_populate_points()` L133: "_populate_points" - snake_case
- 🏷️ `_populate_chapters()` L169: "_populate_chapters" - snake_case
- 🏷️ `_populate_knowledge_relations()` L197: "_populate_knowledge_relations" - snake_case

**详情**:
- 循环复杂度: 平均: 2.9, 最大: 7
- 认知复杂度: 平均: 4.6, 最大: 11
- 嵌套深度: 平均: 0.8, 最大: 3
- 函数长度: 平均: 19.8 行, 最大: 73 行
- 文件长度: 397 代码量 (442 总计)
- 参数数量: 平均: 1.7, 最大: 6
- 代码重复: 5.3% 重复 (1/19)
- 结构分析: 3 个结构问题
- 错误处理: 1/2 个错误被忽略 (50.0%)
- 注释比例: 0.0% (0/397)
- 命名规范: 发现 15 个违规

### 57. backend\ai_services\services\llm_response_mixin.py

**糟糕指数: 15.31**

> 行数: 360 总计, 325 代码, 0 注释 | 函数: 13 | 类: 1

**问题**: ⚠️ 其他问题: 6, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_agent_json_call` | L89-123 | 35 | 5 | 1 | 6 | ✓ |
| `_try_agent_structured_call` | L232-262 | 31 | 5 | 1 | 5 | ✓ |
| `_attempt_llm_json_response` | L137-159 | 23 | 4 | 1 | 5 | ✓ |
| `_run_llm_json_call` | L161-209 | 49 | 4 | 2 | 7 | ✓ |
| `_prepare_structured_call` | L213-230 | 18 | 4 | 1 | 3 | ✓ |
| `_call_with_fallback` | L289-338 | 50 | 4 | 1 | 6 | ✓ |
| `_apply_temperature_override` | L69-75 | 7 | 3 | 1 | 2 | ✓ |
| `_restore_temperature` | L63-66 | 4 | 2 | 1 | 2 | ✓ |
| `_repair_json_response` | L39-60 | 22 | 1 | 0 | 4 | ✓ |
| `_finalize_success_response` | L79-87 | 9 | 1 | 0 | 4 | ✓ |
| `_invoke_llm_messages` | L125-135 | 11 | 1 | 0 | 3 | ✓ |
| `_run_model_structured_call` | L264-287 | 24 | 1 | 1 | 8 | ✓ |
| `call_with_fallback` | L340-355 | 16 | 1 | 0 | 6 | ✓ |

**全部问题 (17)**

- 📏 `_run_agent_json_call()` L89: 6 参数数量
- 📏 `_run_llm_json_call()` L161: 7 参数数量
- 📏 `_run_model_structured_call()` L264: 8 参数数量
- 📏 `_call_with_fallback()` L289: 6 参数数量
- 📏 `call_with_fallback()` L340: 6 参数数量
- ❌ L147: 未处理的易出错调用
- ❌ L157: 未处理的易出错调用
- 🏷️ `_repair_json_response()` L39: "_repair_json_response" - snake_case
- 🏷️ `_restore_temperature()` L63: "_restore_temperature" - snake_case
- 🏷️ `_apply_temperature_override()` L69: "_apply_temperature_override" - snake_case
- 🏷️ `_finalize_success_response()` L79: "_finalize_success_response" - snake_case
- 🏷️ `_run_agent_json_call()` L89: "_run_agent_json_call" - snake_case
- 🏷️ `_invoke_llm_messages()` L125: "_invoke_llm_messages" - snake_case
- 🏷️ `_attempt_llm_json_response()` L137: "_attempt_llm_json_response" - snake_case
- 🏷️ `_run_llm_json_call()` L161: "_run_llm_json_call" - snake_case
- 🏷️ `_prepare_structured_call()` L213: "_prepare_structured_call" - snake_case
- 🏷️ `_try_agent_structured_call()` L232: "_try_agent_structured_call" - snake_case

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 5
- 认知复杂度: 平均: 4.3, 最大: 8
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 23.0 行, 最大: 50 行
- 文件长度: 325 代码量 (360 总计)
- 参数数量: 平均: 4.7, 最大: 8
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 2/2 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/325)
- 命名规范: 发现 12 个违规

### 58. backend\tools\dkt_training_support.py

**糟糕指数: 15.28**

> 行数: 320 总计, 277 代码, 2 注释 | 函数: 14 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `run_public_baseline_training_loop` | L109-154 | 46 | 7 | 2 | 7 | ✓ |
| `run_course_training_loop` | L157-210 | 54 | 7 | 3 | 13 | ✓ |
| `run_status_probe` | L294-319 | 26 | 7 | 1 | 3 | ✓ |
| `prepare_public_baseline_training` | L75-106 | 32 | 4 | 1 | 3 | ✓ |
| `resolve_status_model_path` | L254-266 | 13 | 4 | 1 | 0 | ✓ |
| `import_torch_modules` | L54-64 | 11 | 3 | 2 | 1 | ✓ |
| `print_status_model_info` | L285-291 | 7 | 3 | 1 | 2 | ✓ |
| `to_project_relative_path` | L41-46 | 6 | 2 | 1 | 1 | ✓ |
| `build_status_probe_context` | L269-275 | 7 | 2 | 0 | 0 | ✓ |
| `count_training_sequences` | L278-282 | 5 | 2 | 1 | 1 | ✓ |
| `write_runtime_metadata` | L35-38 | 4 | 1 | 0 | 1 | ✓ |
| `state_dict_to_cpu` | L49-51 | 3 | 1 | 0 | 1 | ✓ |
| `load_dkt_model_class` | L67-72 | 6 | 1 | 0 | 0 | ✓ |
| `build_public_runtime_metadata` | L213-251 | 39 | 1 | 0 | 11 | ✓ |

**全部问题 (7)**

- 🔄 `run_course_training_loop()` L157: 认知复杂度: 13
- 📏 `run_course_training_loop()` L157: 54 代码量
- 📏 `run_public_baseline_training_loop()` L109: 7 参数数量
- 📏 `run_course_training_loop()` L157: 13 参数数量
- 📏 `build_public_runtime_metadata()` L213: 11 参数数量
- 🏗️ `run_course_training_loop()` L157: 中等嵌套: 3
- ❌ L239: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.2, 最大: 7
- 认知复杂度: 平均: 5.1, 最大: 13
- 嵌套深度: 平均: 0.9, 最大: 3
- 函数长度: 平均: 18.5 行, 最大: 54 行
- 文件长度: 277 代码量 (320 总计)
- 参数数量: 平均: 3.1, 最大: 13
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 1 个结构问题
- 错误处理: 1/6 个错误被忽略 (16.7%)
- 注释比例: 0.7% (2/277)
- 命名规范: 无命名违规

### 59. backend\platform_ai\rag\runtime.py

**糟糕指数: 15.13**

> 行数: 440 总计, 405 代码, 2 注释 | 函数: 11 | 类: 1

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 5, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `invoke_with_tools` | L336-414 | 79 | 11 | 3 | 5 | ✓ |
| `_heuristic_tool_calls` | L224-289 | 66 | 10 | 1 | 2 | ✓ |
| `_normalize_invoke_input` | L72-100 | 29 | 9 | 2 | 1 | ✓ |
| `invoke` | L291-321 | 31 | 5 | 1 | 6 | ✓ |
| `_response_format_hint` | L103-109 | 7 | 4 | 1 | 1 | ✓ |
| `_fallback_cypher_from_prompt` | L135-221 | 87 | 4 | 1 | 2 | ✓ |
| `_build_target_match` | L112-132 | 21 | 3 | 1 | 5 | ✓ |
| `_extract_line_value` | L58-61 | 4 | 2 | 0 | 2 | ✓ |
| `_extract_user_question` | L64-69 | 6 | 2 | 1 | 1 | ✓ |
| `__init__` | L51-55 | 5 | 1 | 0 | 1 | ✗ |
| `ainvoke` | L323-334 | 12 | 1 | 0 | 4 | ✓ |

**全部问题 (16)**

- 🔄 `invoke_with_tools()` L336: 复杂度: 11
- 🔄 `_normalize_invoke_input()` L72: 认知复杂度: 13
- 🔄 `invoke_with_tools()` L336: 认知复杂度: 17
- 📏 `_fallback_cypher_from_prompt()` L135: 87 代码量
- 📏 `_heuristic_tool_calls()` L224: 66 代码量
- 📏 `invoke_with_tools()` L336: 79 代码量
- 📏 `invoke()` L291: 6 参数数量
- 🏗️ `invoke_with_tools()` L336: 中等嵌套: 3
- 🏷️ `__init__()` L51: "__init__" - snake_case
- 🏷️ `_extract_line_value()` L58: "_extract_line_value" - snake_case
- 🏷️ `_extract_user_question()` L64: "_extract_user_question" - snake_case
- 🏷️ `_normalize_invoke_input()` L72: "_normalize_invoke_input" - snake_case
- 🏷️ `_response_format_hint()` L103: "_response_format_hint" - snake_case
- 🏷️ `_build_target_match()` L112: "_build_target_match" - snake_case
- 🏷️ `_fallback_cypher_from_prompt()` L135: "_fallback_cypher_from_prompt" - snake_case
- 🏷️ `_heuristic_tool_calls()` L224: "_heuristic_tool_calls" - snake_case

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 11
- 认知复杂度: 平均: 6.7, 最大: 17
- 嵌套深度: 平均: 1.0, 最大: 3
- 函数长度: 平均: 31.5 行, 最大: 87 行
- 文件长度: 405 代码量 (440 总计)
- 参数数量: 平均: 2.7, 最大: 6
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 1 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 0.5% (2/405)
- 命名规范: 发现 8 个违规

### 60. backend\platform_ai\rag\student_context_mixin.py

**糟糕指数: 15.01**

> 行数: 182 总计, 157 代码, 0 注释 | 函数: 5 | 类: 1

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_drift_context` | L101-150 | 50 | 12 | 3 | 4 | ✓ |
| `_build_local_context` | L16-76 | 61 | 10 | 2 | 5 | ✓ |
| `_build_global_context` | L78-99 | 22 | 5 | 2 | 3 | ✓ |
| `_compose_query_context` | L152-176 | 25 | 4 | 1 | 5 | ✓ |
| `_humanize_document_title` | L178-181 | 4 | 1 | 0 | 2 | ✓ |

**全部问题 (11)**

- 🔄 `_build_drift_context()` L101: 复杂度: 12
- 🔄 `_build_local_context()` L16: 认知复杂度: 14
- 🔄 `_build_drift_context()` L101: 认知复杂度: 18
- 📏 `_build_local_context()` L16: 61 代码量
- 🏗️ `_build_drift_context()` L101: 中等嵌套: 3
- ❌ L112: 未处理的易出错调用
- 🏷️ `_build_local_context()` L16: "_build_local_context" - snake_case
- 🏷️ `_build_global_context()` L78: "_build_global_context" - snake_case
- 🏷️ `_build_drift_context()` L101: "_build_drift_context" - snake_case
- 🏷️ `_compose_query_context()` L152: "_compose_query_context" - snake_case
- 🏷️ `_humanize_document_title()` L178: "_humanize_document_title" - snake_case

**详情**:
- 循环复杂度: 平均: 6.4, 最大: 12
- 认知复杂度: 平均: 9.6, 最大: 18
- 嵌套深度: 平均: 1.6, 最大: 3
- 函数长度: 平均: 32.4 行, 最大: 61 行
- 文件长度: 157 代码量 (182 总计)
- 参数数量: 平均: 3.8, 最大: 5
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 1 个结构问题
- 错误处理: 1/12 个错误被忽略 (8.3%)
- 注释比例: 0.0% (0/157)
- 命名规范: 发现 5 个违规

### 61. backend\platform_ai\llm\agent.py

**糟糕指数: 15.01**

> 行数: 262 总计, 234 代码, 0 注释 | 函数: 11 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_get_model` | L66-99 | 34 | 9 | 2 | 1 | ✓ |
| `_get_agent` | L157-181 | 25 | 5 | 1 | 1 | ✓ |
| `invoke_json` | L183-202 | 20 | 5 | 1 | 4 | ✓ |
| `get_agent_service` | L206-237 | 32 | 4 | 1 | 11 | ✓ |
| `get_default_agent_service` | L240-261 | 22 | 4 | 0 | 0 | ✓ |
| `__init__` | L32-59 | 28 | 2 | 0 | 12 | ✓ |
| `_get_tools` | L101-155 | 19 | 2 | 1 | 1 | ✓ |
| `lookup_course_context` | L110-115 | 6 | 2 | 1 | 2 | ✓ |
| `summarize_mastery` | L134-149 | 16 | 2 | 0 | 2 | ✓ |
| `is_available` | L62-64 | 3 | 1 | 0 | 1 | ✓ |
| `query_course_graphrag` | L118-131 | 14 | 1 | 0 | 4 | ✓ |

**全部问题 (7)**

- 🔄 `_get_model()` L66: 认知复杂度: 13
- 📏 `__init__()` L32: 12 参数数量
- 📏 `get_agent_service()` L206: 11 参数数量
- 🏷️ `__init__()` L32: "__init__" - snake_case
- 🏷️ `_get_model()` L66: "_get_model" - snake_case
- 🏷️ `_get_tools()` L101: "_get_tools" - snake_case
- 🏷️ `_get_agent()` L157: "_get_agent" - snake_case

**详情**:
- 循环复杂度: 平均: 3.4, 最大: 9
- 认知复杂度: 平均: 4.6, 最大: 13
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 19.9 行, 最大: 34 行
- 文件长度: 234 代码量 (262 总计)
- 参数数量: 平均: 3.5, 最大: 12
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/234)
- 命名规范: 发现 4 个违规

### 62. backend\tools\db_seed_support.py

**糟糕指数: 14.88**

> 行数: 386 总计, 342 代码, 0 注释 | 函数: 13 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 3, 🏗️ 结构问题: 2, ❌ 错误处理问题: 38, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_seed_course_content` | L32-103 | 72 | 10 | 2 | 3 | ✓ |
| `_attach_students_to_classes` | L246-285 | 40 | 8 | 2 | 4 | ✓ |
| `sync_seeded_courses` | L370-385 | 16 | 6 | 3 | 1 | ✓ |
| `_seed_courses` | L167-191 | 25 | 5 | 2 | 3 | ✓ |
| `_seed_classes` | L194-221 | 28 | 5 | 3 | 4 | ✓ |
| `_resolve_big_data_context` | L224-243 | 20 | 4 | 1 | 2 | ✓ |
| `_seed_class_invitations` | L296-314 | 19 | 4 | 2 | 3 | ✓ |
| `_seed_survey_questions` | L317-345 | 29 | 4 | 1 | 2 | ✓ |
| `_seed_user_accounts` | L114-151 | 38 | 3 | 1 | 1 | ✓ |
| `_seed_student_demo_state` | L288-293 | 6 | 3 | 1 | 2 | ✓ |
| `_seed_activation_codes` | L154-164 | 11 | 2 | 1 | 2 | ✓ |
| `_create_user` | L106-111 | 6 | 1 | 0 | 3 | ✓ |
| `seed_database_from_testdata` | L348-367 | 20 | 1 | 0 | 1 | ✓ |

**全部问题 (52)**

- 🔄 `_seed_course_content()` L32: 认知复杂度: 14
- 📏 `_seed_course_content()` L32: 72 代码量
- 🏗️ `_seed_classes()` L194: 中等嵌套: 3
- 🏗️ `sync_seeded_courses()` L370: 中等嵌套: 3
- ❌ L44: 未处理的易出错调用
- ❌ L45: 未处理的易出错调用
- ❌ L46: 未处理的易出错调用
- ❌ L52: 未处理的易出错调用
- ❌ L70: 未处理的易出错调用
- ❌ L72: 未处理的易出错调用
- ❌ L73: 未处理的易出错调用
- ❌ L89: 未处理的易出错调用
- ❌ L90: 未处理的易出错调用
- ❌ L91: 未处理的易出错调用
- ❌ L92: 未处理的易出错调用
- ❌ L93: 未处理的易出错调用
- ❌ L94: 未处理的易出错调用
- ❌ L95: 未处理的易出错调用
- ❌ L128: 未处理的易出错调用
- ❌ L140: 未处理的易出错调用
- ❌ L156: 未处理的易出错调用
- ❌ L162: 未处理的易出错调用
- ❌ L174: 未处理的易出错调用
- ❌ L180: 未处理的易出错调用
- ❌ L182: 未处理的易出错调用
- ❌ L183: 未处理的易出错调用
- ❌ L202: 未处理的易出错调用
- ❌ L208: 未处理的易出错调用
- ❌ L210: 未处理的易出错调用
- ❌ L214: 未处理的易出错调用
- ❌ L302: 未处理的易出错调用
- ❌ L312: 未处理的易出错调用
- ❌ L320: 未处理的易出错调用
- ❌ L326: 未处理的易出错调用
- ❌ L327: 未处理的易出错调用
- ❌ L328: 未处理的易出错调用
- ❌ L329: 未处理的易出错调用
- ❌ L333: 未处理的易出错调用
- ❌ L339: 未处理的易出错调用
- ❌ L340: 未处理的易出错调用
- ❌ L341: 未处理的易出错调用
- ❌ L342: 未处理的易出错调用
- 🏷️ `_seed_course_content()` L32: "_seed_course_content" - snake_case
- 🏷️ `_create_user()` L106: "_create_user" - snake_case
- 🏷️ `_seed_user_accounts()` L114: "_seed_user_accounts" - snake_case
- 🏷️ `_seed_activation_codes()` L154: "_seed_activation_codes" - snake_case
- 🏷️ `_seed_courses()` L167: "_seed_courses" - snake_case
- 🏷️ `_seed_classes()` L194: "_seed_classes" - snake_case
- 🏷️ `_resolve_big_data_context()` L224: "_resolve_big_data_context" - snake_case
- 🏷️ `_attach_students_to_classes()` L246: "_attach_students_to_classes" - snake_case
- 🏷️ `_seed_student_demo_state()` L288: "_seed_student_demo_state" - snake_case
- 🏷️ `_seed_class_invitations()` L296: "_seed_class_invitations" - snake_case

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 10
- 认知复杂度: 平均: 7.2, 最大: 14
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 25.4 行, 最大: 72 行
- 文件长度: 342 代码量 (386 总计)
- 参数数量: 平均: 2.4, 最大: 4
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 2 个结构问题
- 错误处理: 38/55 个错误被忽略 (69.1%)
- 注释比例: 0.0% (0/342)
- 命名规范: 发现 11 个违规

### 63. backend\tools\ai_services_test.py

**糟糕指数: 14.77**

> 行数: 85 总计, 73 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_kt_service` | L8-68 | 61 | 9 | 4 | 0 | ✓ |
| `test_llm_service` | L71-84 | 14 | 1 | 0 | 0 | ✓ |

**全部问题 (8)**

- 🔄 `test_kt_service()` L8: 认知复杂度: 17
- 🔄 `test_kt_service()` L8: 嵌套深度: 4
- 📏 `test_kt_service()` L8: 61 代码量
- 🏗️ `test_kt_service()` L8: 中等嵌套: 4
- ❌ L15: 未处理的易出错调用
- ❌ L16: 未处理的易出错调用
- ❌ L68: 未处理的易出错调用
- ❌ L84: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 9
- 认知复杂度: 平均: 9.0, 最大: 17
- 嵌套深度: 平均: 2.0, 最大: 4
- 函数长度: 平均: 37.5 行, 最大: 61 行
- 文件长度: 73 代码量 (85 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 未发现函数
- 结构分析: 1 个结构问题
- 错误处理: 4/4 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/73)
- 命名规范: 无命名违规

### 64. backend\ai_services\services\kt_prediction_stats.py

**糟糕指数: 14.59**

> 行数: 203 总计, 176 代码, 0 注释 | 函数: 7 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 5, 📝 注释问题: 1, 🏷️ 命名问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_calculate_point_mastery` | L90-160 | 71 | 10 | 3 | 3 | ✓ |
| `_extract_prediction_map` | L59-77 | 19 | 5 | 2 | 1 | ✓ |
| `_attach_prediction_metadata` | L15-33 | 19 | 4 | 0 | 3 | ✓ |
| `_estimate_stat_confidence` | L35-56 | 22 | 4 | 1 | 4 | ✓ |
| `_coerce_int_identifier` | L80-88 | 9 | 3 | 1 | 2 | ✓ |
| `_get_default_prediction` | L188-202 | 15 | 3 | 2 | 2 | ✓ |
| `_prepare_input_data` | L163-186 | 24 | 1 | 0 | 1 | ✓ |

**全部问题 (15)**

- 🔄 `_calculate_point_mastery()` L90: 认知复杂度: 16
- 📏 `_calculate_point_mastery()` L90: 71 代码量
- 🏗️ `_calculate_point_mastery()` L90: 中等嵌套: 3
- ❌ L28: 未处理的易出错调用
- ❌ L30: 未处理的易出错调用
- ❌ L45: 未处理的易出错调用
- ❌ L47: 未处理的易出错调用
- ❌ L171: 未处理的易出错调用
- 🏷️ `_attach_prediction_metadata()` L15: "_attach_prediction_metadata" - snake_case
- 🏷️ `_estimate_stat_confidence()` L35: "_estimate_stat_confidence" - snake_case
- 🏷️ `_extract_prediction_map()` L59: "_extract_prediction_map" - snake_case
- 🏷️ `_coerce_int_identifier()` L80: "_coerce_int_identifier" - snake_case
- 🏷️ `_calculate_point_mastery()` L90: "_calculate_point_mastery" - snake_case
- 🏷️ `_prepare_input_data()` L163: "_prepare_input_data" - snake_case
- 🏷️ `_get_default_prediction()` L188: "_get_default_prediction" - snake_case

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 10
- 认知复杂度: 平均: 6.9, 最大: 16
- 嵌套深度: 平均: 1.3, 最大: 3
- 函数长度: 平均: 25.6 行, 最大: 71 行
- 文件长度: 176 代码量 (203 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 1 个结构问题
- 错误处理: 5/11 个错误被忽略 (45.5%)
- 注释比例: 0.0% (0/176)
- 命名规范: 发现 7 个违规

### 65. backend\exams\student_submission_support.py

**糟糕指数: 14.41**

> 行数: 339 总计, 304 代码, 0 注释 | 函数: 8 | 类: 2

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `refresh_exam_kt_analysis` | L210-279 | 70 | 7 | 4 | 3 | ✓ |
| `upsert_exam_submission_record` | L90-126 | 37 | 6 | 1 | 4 | ✓ |
| `sync_result_submission_snapshot` | L329-338 | 10 | 5 | 1 | 2 | ✓ |
| `build_answer_history_batch` | L129-182 | 54 | 4 | 2 | 4 | ✓ |
| `build_exam_submission_context` | L49-87 | 39 | 2 | 0 | 2 | ✓ |
| `persist_answer_histories` | L185-190 | 6 | 2 | 1 | 1 | ✓ |
| `capture_mastery_snapshot_from_records` | L193-207 | 15 | 1 | 0 | 3 | ✓ |
| `build_submission_feedback_state` | L282-326 | 45 | 1 | 0 | 6 | ✓ |

**全部问题 (9)**

- 🔄 `refresh_exam_kt_analysis()` L210: 认知复杂度: 15
- 🔄 `refresh_exam_kt_analysis()` L210: 嵌套深度: 4
- 📏 `build_answer_history_batch()` L129: 54 代码量
- 📏 `refresh_exam_kt_analysis()` L210: 70 代码量
- 📏 `build_submission_feedback_state()` L282: 6 参数数量
- 🏗️ `refresh_exam_kt_analysis()` L210: 中等嵌套: 4
- ❌ L204: 未处理的易出错调用
- ❌ L258: 未处理的易出错调用
- ❌ L259: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 7
- 认知复杂度: 平均: 5.8, 最大: 15
- 嵌套深度: 平均: 1.1, 最大: 4
- 函数长度: 平均: 34.5 行, 最大: 70 行
- 文件长度: 304 代码量 (339 总计)
- 参数数量: 平均: 3.1, 最大: 6
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 3/10 个错误被忽略 (30.0%)
- 注释比例: 0.0% (0/304)
- 命名规范: 无命名违规

### 66. backend\ai_services\services\kt_service.py

**糟糕指数: 14.20**

> 行数: 295 总计, 255 代码, 0 注释 | 函数: 8 | 类: 1

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 7, 📝 注释问题: 1, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__init__` | L73-133 | 61 | 8 | 1 | 6 | ✓ |
| `is_available` | L202-230 | 29 | 6 | 2 | 1 | ✓ |
| `_load_runtime_info` | L268-284 | 17 | 5 | 2 | 2 | ✓ |
| `_resolve_backend_path` | L49-59 | 11 | 4 | 1 | 1 | ✓ |
| `_resolve_enabled_models` | L135-156 | 22 | 4 | 2 | 2 | ✓ |
| `_normalize_weights` | L177-199 | 23 | 4 | 2 | 1 | ✓ |
| `get_model_info` | L232-266 | 35 | 4 | 1 | 1 | ✓ |
| `_load_fusion_weights` | L158-175 | 18 | 3 | 2 | 1 | ✓ |

**全部问题 (15)**

- 📏 `__init__()` L73: 61 代码量
- 📏 `__init__()` L73: 6 参数数量
- ❌ L240: 未处理的易出错调用
- ❌ L241: 未处理的易出错调用
- ❌ L242: 未处理的易出错调用
- ❌ L243: 未处理的易出错调用
- ❌ L244: 未处理的易出错调用
- ❌ L245: 未处理的易出错调用
- ❌ L259: 未处理的易出错调用
- 🏷️ `_resolve_backend_path()` L49: "_resolve_backend_path" - snake_case
- 🏷️ `__init__()` L73: "__init__" - snake_case
- 🏷️ `_resolve_enabled_models()` L135: "_resolve_enabled_models" - snake_case
- 🏷️ `_load_fusion_weights()` L158: "_load_fusion_weights" - snake_case
- 🏷️ `_normalize_weights()` L177: "_normalize_weights" - snake_case
- 🏷️ `_load_runtime_info()` L268: "_load_runtime_info" - snake_case

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 8
- 认知复杂度: 平均: 8.0, 最大: 10
- 嵌套深度: 平均: 1.6, 最大: 2
- 函数长度: 平均: 27.0 行, 最大: 61 行
- 文件长度: 255 代码量 (295 总计)
- 参数数量: 平均: 1.9, 最大: 6
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 7/9 个错误被忽略 (77.8%)
- 注释比例: 0.0% (0/255)
- 命名规范: 发现 6 个违规

### 67. backend\platform_ai\rag\student_resource_mixin.py

**糟糕指数: 14.04**

> 行数: 327 总计, 289 代码, 0 注释 | 函数: 13 | 类: 2

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, ❌ 错误处理问题: 6, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_parse_internal_llm_result` | L256-279 | 24 | 8 | 2 | 3 | ✓ |
| `_parse_external_llm_result` | L300-326 | 27 | 7 | 2 | 3 | ✓ |
| `_select_internal_resources` | L145-177 | 33 | 4 | 1 | 5 | ✓ |
| `_serialize_available_resources` | L239-253 | 15 | 4 | 0 | 2 | ✓ |
| `recommend_node_resources` | L35-45 | 11 | 3 | 0 | 2 | ✓ |
| `_build_internal_resources` | L112-143 | 32 | 3 | 2 | 5 | ✓ |
| `_build_external_resources` | L179-213 | 35 | 3 | 1 | 4 | ✓ |
| `_recommend_node_resources` | L66-97 | 32 | 2 | 1 | 2 | ✓ |
| `recommend_resources_for_node` | L47-64 | 18 | 1 | 0 | 6 | ✓ |
| `_search_internal_candidates` | L99-110 | 12 | 1 | 0 | 3 | ✓ |
| `_resource_map` | L216-224 | 9 | 1 | 0 | 1 | ✓ |
| `_ordered_resources` | L227-236 | 10 | 1 | 0 | 2 | ✓ |
| `_fallback_internal_selection` | L282-297 | 16 | 1 | 0 | 3 | ✓ |

**全部问题 (18)**

- 📏 `recommend_resources_for_node()` L47: 6 参数数量
- 📋 `recommend_node_resources()` L35: 重复模式: recommend_node_resources, recommend_resources_for_node
- ❌ L276: 未处理的易出错调用
- ❌ L277: 未处理的易出错调用
- ❌ L316: 未处理的易出错调用
- ❌ L317: 未处理的易出错调用
- ❌ L318: 未处理的易出错调用
- ❌ L319: 未处理的易出错调用
- 🏷️ `_recommend_node_resources()` L66: "_recommend_node_resources" - snake_case
- 🏷️ `_search_internal_candidates()` L99: "_search_internal_candidates" - snake_case
- 🏷️ `_build_internal_resources()` L112: "_build_internal_resources" - snake_case
- 🏷️ `_select_internal_resources()` L145: "_select_internal_resources" - snake_case
- 🏷️ `_build_external_resources()` L179: "_build_external_resources" - snake_case
- 🏷️ `_resource_map()` L216: "_resource_map" - snake_case
- 🏷️ `_ordered_resources()` L227: "_ordered_resources" - snake_case
- 🏷️ `_serialize_available_resources()` L239: "_serialize_available_resources" - snake_case
- 🏷️ `_parse_internal_llm_result()` L256: "_parse_internal_llm_result" - snake_case
- 🏷️ `_fallback_internal_selection()` L282: "_fallback_internal_selection" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 8
- 认知复杂度: 平均: 4.4, 最大: 12
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 21.1 行, 最大: 35 行
- 文件长度: 289 代码量 (327 总计)
- 参数数量: 平均: 3.2, 最大: 6
- 代码重复: 7.7% 重复 (1/13)
- 结构分析: 0 个结构问题
- 错误处理: 6/14 个错误被忽略 (42.9%)
- 注释比例: 0.0% (0/289)
- 命名规范: 发现 11 个违规

### 68. backend\tools\dkt_data_access.py

**糟糕指数: 13.99**

> 行数: 164 总计, 128 代码, 2 注释 | 函数: 7 | 类: 0

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `export_training_data` | L119-163 | 45 | 12 | 2 | 3 | ✓ |
| `_get_kp_metadata` | L69-116 | 48 | 9 | 1 | 1 | ✓ |
| `_get_kp_prerequisites` | L55-66 | 12 | 3 | 1 | 1 | ✓ |
| `_get_num_kp` | L22-30 | 9 | 2 | 1 | 1 | ✓ |
| `_get_kp_mapping` | L33-44 | 12 | 2 | 1 | 1 | ✓ |
| `_setup_django` | L14-19 | 6 | 1 | 0 | 0 | ✓ |
| `_get_first_course_with_kps` | L47-52 | 6 | 1 | 0 | 0 | ✓ |

**全部问题 (12)**

- 🔄 `export_training_data()` L119: 复杂度: 12
- 🔄 `export_training_data()` L119: 认知复杂度: 16
- ❌ L114: 未处理的易出错调用
- ❌ L155: 未处理的易出错调用
- ❌ L156: 未处理的易出错调用
- ❌ L157: 未处理的易出错调用
- 🏷️ `_setup_django()` L14: "_setup_django" - snake_case
- 🏷️ `_get_num_kp()` L22: "_get_num_kp" - snake_case
- 🏷️ `_get_kp_mapping()` L33: "_get_kp_mapping" - snake_case
- 🏷️ `_get_first_course_with_kps()` L47: "_get_first_course_with_kps" - snake_case
- 🏷️ `_get_kp_prerequisites()` L55: "_get_kp_prerequisites" - snake_case
- 🏷️ `_get_kp_metadata()` L69: "_get_kp_metadata" - snake_case

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 12
- 认知复杂度: 平均: 6.0, 最大: 16
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 19.7 行, 最大: 48 行
- 文件长度: 128 代码量 (164 总计)
- 参数数量: 平均: 1.0, 最大: 3
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 4/6 个错误被忽略 (66.7%)
- 注释比例: 1.6% (2/128)
- 命名规范: 发现 6 个违规

### 69. backend\ai_services\services\kt_model_runtime.py

**糟糕指数: 13.96**

> 行数: 193 总计, 170 代码, 0 注释 | 函数: 4 | 类: 1

**问题**: ⚠️ 其他问题: 3, 📋 重复问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_predict_with_dkt` | L80-135 | 56 | 4 | 2 | 4 | ✓ |
| `_predict_with_mefkt` | L137-192 | 56 | 4 | 2 | 4 | ✓ |
| `_load_course_knowledge_point_ids` | L20-42 | 23 | 3 | 1 | 2 | ✓ |
| `_run_model_prediction` | L44-78 | 35 | 3 | 1 | 5 | ✓ |

**全部问题 (7)**

- 📏 `_predict_with_dkt()` L80: 56 代码量
- 📏 `_predict_with_mefkt()` L137: 56 代码量
- 📋 `_predict_with_dkt()` L80: 重复模式: _predict_with_dkt, _predict_with_mefkt
- 🏷️ `_load_course_knowledge_point_ids()` L20: "_load_course_knowledge_point_ids" - snake_case
- 🏷️ `_run_model_prediction()` L44: "_run_model_prediction" - snake_case
- 🏷️ `_predict_with_dkt()` L80: "_predict_with_dkt" - snake_case
- 🏷️ `_predict_with_mefkt()` L137: "_predict_with_mefkt" - snake_case

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 4
- 认知复杂度: 平均: 6.5, 最大: 8
- 嵌套深度: 平均: 1.5, 最大: 2
- 函数长度: 平均: 42.5 行, 最大: 56 行
- 文件长度: 170 代码量 (193 总计)
- 参数数量: 平均: 3.8, 最大: 5
- 代码重复: 25.0% 重复 (1/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/170)
- 命名规范: 发现 4 个违规

### 70. backend\ai_services\student_ai_profile_views.py

**糟糕指数: 13.92**

> 行数: 323 总计, 283 代码, 0 注释 | 函数: 11 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 7, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ai_feedback_report` | L123-174 | 52 | 14 | 2 | 1 | ✓ |
| `ai_resource_reason` | L76-118 | 43 | 13 | 3 | 1 | ✓ |
| `ai_profile_analysis` | L49-71 | 23 | 9 | 1 | 1 | ✓ |
| `ai_refresh_profile` | L202-215 | 14 | 5 | 1 | 1 | ✓ |
| `ai_refresh_learning_path` | L220-260 | 41 | 5 | 1 | 1 | ✓ |
| `ai_time_scheduling` | L285-302 | 18 | 5 | 1 | 1 | ✓ |
| `ai_analysis_compare` | L307-322 | 16 | 5 | 1 | 1 | ✓ |
| `ai_learning_advice` | L179-197 | 19 | 4 | 1 | 1 | ✓ |
| `ai_key_points_reminder` | L265-280 | 16 | 4 | 1 | 1 | ✓ |
| `_build_habit_data` | L26-31 | 6 | 2 | 1 | 1 | ✗ |
| `_build_mastery_data` | L34-44 | 11 | 2 | 0 | 2 | ✗ |

**全部问题 (15)**

- 🔄 `ai_resource_reason()` L76: 复杂度: 13
- 🔄 `ai_feedback_report()` L123: 复杂度: 14
- 🔄 `ai_resource_reason()` L76: 认知复杂度: 19
- 🔄 `ai_feedback_report()` L123: 认知复杂度: 18
- 📏 `ai_feedback_report()` L123: 52 代码量
- 🏗️ `ai_resource_reason()` L76: 中等嵌套: 3
- ❌ L69: 未处理的易出错调用
- ❌ L111: 未处理的易出错调用
- ❌ L193: 未处理的易出错调用
- ❌ L194: 未处理的易出错调用
- ❌ L195: 未处理的易出错调用
- ❌ L196: 未处理的易出错调用
- ❌ L213: 未处理的易出错调用
- 🏷️ `_build_habit_data()` L26: "_build_habit_data" - snake_case
- 🏷️ `_build_mastery_data()` L34: "_build_mastery_data" - snake_case

**详情**:
- 循环复杂度: 平均: 6.2, 最大: 14
- 认知复杂度: 平均: 8.5, 最大: 19
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 23.5 行, 最大: 52 行
- 文件长度: 283 代码量 (323 总计)
- 参数数量: 平均: 1.1, 最大: 2
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 1 个结构问题
- 错误处理: 7/33 个错误被忽略 (21.2%)
- 注释比例: 0.0% (0/283)
- 命名规范: 发现 2 个违规

### 71. backend\courses\admin_statistics_views.py

**糟糕指数: 13.80**

> 行数: 190 总计, 160 代码, 0 注释 | 函数: 8 | 类: 0

**问题**: 📋 重复问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `admin_statistics_learning` | L98-109 | 12 | 2 | 0 | 1 | ✓ |
| `admin_statistics_exams` | L114-124 | 11 | 2 | 0 | 1 | ✓ |
| `admin_statistics_overview` | L28-49 | 22 | 1 | 0 | 1 | ✓ |
| `admin_statistics_users` | L54-72 | 19 | 1 | 0 | 1 | ✓ |
| `admin_statistics_courses` | L77-93 | 17 | 1 | 0 | 1 | ✓ |
| `admin_statistics_active_users` | L129-140 | 12 | 1 | 0 | 1 | ✓ |
| `admin_statistics_report` | L145-169 | 25 | 1 | 0 | 1 | ✓ |
| `admin_statistics_export` | L174-189 | 16 | 1 | 0 | 1 | ✓ |

**全部问题 (3)**

- 📋 `admin_statistics_courses()` L77: 重复模式: admin_statistics_courses, admin_statistics_learning, admin_statistics_exams
- 📋 `admin_statistics_active_users()` L129: 重复模式: admin_statistics_active_users, admin_statistics_export
- ❌ L178: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.3, 最大: 2
- 认知复杂度: 平均: 1.3, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 16.8 行, 最大: 25 行
- 文件长度: 160 代码量 (190 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 37.5% 重复 (3/8)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 0.0% (0/160)
- 命名规范: 无命名违规

### 72. backend\tools\db_demo_preset_support.py

**糟糕指数: 13.80**

> 行数: 312 总计, 276 代码, 0 注释 | 函数: 9 | 类: 2

**问题**: ⚠️ 其他问题: 3, ❌ 错误处理问题: 6, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_student1_answer_value` | L156-179 | 24 | 10 | 1 | 2 | ✓ |
| `rebuild_student1_path` | L249-311 | 63 | 4 | 2 | 7 | ✓ |
| `load_student1_demo_course_data` | L91-109 | 19 | 2 | 0 | 1 | ✓ |
| `sync_student1_initial_assessment` | L131-153 | 23 | 2 | 1 | 2 | ✓ |
| `build_student1_demo_defaults` | L31-88 | 58 | 1 | 0 | 0 | ✓ |
| `reset_course_demo_state` | L112-128 | 17 | 1 | 0 | 2 | ✓ |
| `apply_student1_static_state` | L182-201 | 20 | 1 | 0 | 3 | ✓ |
| `build_mastery_payload` | L204-213 | 10 | 1 | 0 | 3 | ✓ |
| `build_student1_feedback_defaults` | L216-246 | 31 | 1 | 0 | 5 | ✓ |

**全部问题 (9)**

- 📏 `build_student1_demo_defaults()` L31: 58 代码量
- 📏 `rebuild_student1_path()` L249: 63 代码量
- 📏 `rebuild_student1_path()` L249: 7 参数数量
- ❌ L146: 未处理的易出错调用
- ❌ L165: 未处理的易出错调用
- ❌ L167: 未处理的易出错调用
- ❌ L210: 未处理的易出错调用
- ❌ L272: 未处理的易出错调用
- ❌ L302: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 10
- 认知复杂度: 平均: 3.4, 最大: 12
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 29.4 行, 最大: 63 行
- 文件长度: 276 代码量 (312 总计)
- 参数数量: 平均: 2.8, 最大: 7
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 6/17 个错误被忽略 (35.3%)
- 注释比例: 0.0% (0/276)
- 命名规范: 无命名违规

### 73. backend\platform_ai\rag\student_retrieval_mixin.py

**糟糕指数: 13.68**

> 行数: 200 总计, 181 代码, 0 注释 | 函数: 12 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 3, ❌ 错误处理问题: 7, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_rank_documents` | L145-172 | 28 | 9 | 3 | 6 | ✓ |
| `_entity_score` | L75-96 | 22 | 8 | 3 | 4 | ✓ |
| `_collect_neighbor_ids` | L111-124 | 14 | 8 | 2 | 4 | ✓ |
| `_rank_community_reports` | L174-199 | 26 | 7 | 2 | 5 | ✓ |
| `_relationship_lines` | L126-143 | 18 | 6 | 2 | 4 | ✓ |
| `_merge_sources` | L62-73 | 12 | 5 | 3 | 2 | ✓ |
| `_extract_point_ids` | L23-32 | 10 | 4 | 2 | 2 | ✓ |
| `_rank_entities` | L98-109 | 12 | 4 | 2 | 5 | ✓ |
| `_document_excerpt` | L14-21 | 8 | 3 | 1 | 3 | ✓ |
| `_source_from_document` | L34-43 | 10 | 2 | 0 | 4 | ✓ |
| `_source_from_report` | L45-56 | 12 | 2 | 0 | 3 | ✓ |
| `_source_from_graphrag_hit` | L58-60 | 3 | 1 | 0 | 3 | ✓ |

**全部问题 (23)**

- 🔄 `_entity_score()` L75: 认知复杂度: 14
- 🔄 `_rank_documents()` L145: 认知复杂度: 15
- 📏 `_rank_documents()` L145: 6 参数数量
- 🏗️ `_merge_sources()` L62: 中等嵌套: 3
- 🏗️ `_entity_score()` L75: 中等嵌套: 3
- 🏗️ `_rank_documents()` L145: 中等嵌套: 3
- ❌ L37: 未处理的易出错调用
- ❌ L39: 未处理的易出错调用
- ❌ L40: 未处理的易出错调用
- ❌ L51: 未处理的易出错调用
- ❌ L107: 未处理的易出错调用
- ❌ L189: 未处理的易出错调用
- ❌ L197: 未处理的易出错调用
- 🏷️ `_document_excerpt()` L14: "_document_excerpt" - snake_case
- 🏷️ `_extract_point_ids()` L23: "_extract_point_ids" - snake_case
- 🏷️ `_source_from_document()` L34: "_source_from_document" - snake_case
- 🏷️ `_source_from_report()` L45: "_source_from_report" - snake_case
- 🏷️ `_source_from_graphrag_hit()` L58: "_source_from_graphrag_hit" - snake_case
- 🏷️ `_merge_sources()` L62: "_merge_sources" - snake_case
- 🏷️ `_entity_score()` L75: "_entity_score" - snake_case
- 🏷️ `_rank_entities()` L98: "_rank_entities" - snake_case
- 🏷️ `_collect_neighbor_ids()` L111: "_collect_neighbor_ids" - snake_case
- 🏷️ `_relationship_lines()` L126: "_relationship_lines" - snake_case

**详情**:
- 循环复杂度: 平均: 4.9, 最大: 9
- 认知复杂度: 平均: 8.3, 最大: 15
- 嵌套深度: 平均: 1.7, 最大: 3
- 函数长度: 平均: 14.6 行, 最大: 28 行
- 文件长度: 181 代码量 (200 总计)
- 参数数量: 平均: 3.8, 最大: 6
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 3 个结构问题
- 错误处理: 7/39 个错误被忽略 (17.9%)
- 注释比例: 0.0% (0/181)
- 命名规范: 发现 12 个违规

### 74. backend\courses\admin_views.py

**糟糕指数: 13.68**

> 行数: 468 总计, 384 代码, 8 注释 | 函数: 12 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 4, 🏗️ 结构问题: 2, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `admin_class_detail` | L181-240 | 60 | 14 | 3 | 2 | ✓ |
| `admin_course_detail` | L350-403 | 54 | 13 | 2 | 2 | ✓ |
| `admin_class_create` | L136-176 | 41 | 8 | 2 | 1 | ✓ |
| `admin_course_create` | L314-345 | 32 | 8 | 2 | 1 | ✓ |
| `admin_class_list` | L76-131 | 56 | 7 | 2 | 1 | ✓ |
| `admin_course_assign_teacher` | L408-439 | 32 | 7 | 2 | 2 | ✓ |
| `admin_class_add_students` | L270-294 | 25 | 6 | 3 | 2 | ✓ |
| `admin_course_list` | L32-71 | 40 | 5 | 1 | 1 | ✓ |
| `admin_class_assign_teacher` | L444-467 | 24 | 5 | 2 | 2 | ✓ |
| `admin_class_students` | L245-265 | 21 | 3 | 1 | 2 | ✓ |
| `_parse_pagination_params` | L16-27 | 12 | 2 | 1 | 1 | ✓ |
| `admin_class_remove_student` | L299-309 | 11 | 2 | 1 | 3 | ✓ |

**全部问题 (12)**

- 🔄 `admin_class_detail()` L181: 复杂度: 14
- 🔄 `admin_course_detail()` L350: 复杂度: 13
- 🔄 `admin_class_detail()` L181: 认知复杂度: 20
- 🔄 `admin_course_detail()` L350: 认知复杂度: 17
- 📏 `admin_class_list()` L76: 56 代码量
- 📏 `admin_class_detail()` L181: 60 代码量
- 📏 `admin_course_detail()` L350: 54 代码量
- 🏗️ `admin_class_detail()` L181: 中等嵌套: 3
- 🏗️ `admin_class_add_students()` L270: 中等嵌套: 3
- ❌ L205: 未处理的易出错调用
- ❌ L306: 未处理的易出错调用
- ❌ L380: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 6.7, 最大: 14
- 认知复杂度: 平均: 10.3, 最大: 20
- 嵌套深度: 平均: 1.8, 最大: 3
- 函数长度: 平均: 34.0 行, 最大: 60 行
- 文件长度: 384 代码量 (468 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 2 个结构问题
- 错误处理: 3/45 个错误被忽略 (6.7%)
- 注释比例: 2.1% (8/384)
- 命名规范: 发现 1 个违规

### 75. backend\ai_services\services\llm_resource_support.py

**糟糕指数: 13.68**

> 行数: 223 总计, 200 代码, 0 注释 | 函数: 5 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 3, 🏗️ 结构问题: 2, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_internal_resources_prompt` | L102-174 | 73 | 11 | 3 | 5 | ✓ |
| `normalize_external_resource_result` | L79-99 | 21 | 6 | 3 | 4 | ✓ |
| `build_external_resources_prompt` | L8-76 | 69 | 4 | 1 | 5 | ✓ |
| `normalize_internal_resource_result` | L177-182 | 6 | 2 | 0 | 2 | ✓ |
| `build_stage_question_prompt` | L185-222 | 38 | 1 | 0 | 3 | ✓ |

**全部问题 (8)**

- 🔄 `build_internal_resources_prompt()` L102: 复杂度: 11
- 🔄 `build_internal_resources_prompt()` L102: 认知复杂度: 17
- 📏 `build_external_resources_prompt()` L8: 69 代码量
- 📏 `build_internal_resources_prompt()` L102: 73 代码量
- 🏗️ `normalize_external_resource_result()` L79: 中等嵌套: 3
- 🏗️ `build_internal_resources_prompt()` L102: 中等嵌套: 3
- ❌ L114: 未处理的易出错调用
- ❌ L168: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 11
- 认知复杂度: 平均: 7.6, 最大: 17
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 41.4 行, 最大: 73 行
- 文件长度: 200 代码量 (223 总计)
- 参数数量: 平均: 3.8, 最大: 5
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 2 个结构问题
- 错误处理: 2/7 个错误被忽略 (28.6%)
- 注释比例: 0.0% (0/200)
- 命名规范: 无命名违规

### 76. backend\common\course_utils.py

**糟糕指数: 13.66**

> 行数: 74 总计, 54 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: 🔄 复杂度问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `resolve_course_id` | L29-70 | 42 | 12 | 3 | 1 | ✓ |
| `validate_course_exists` | L14-26 | 13 | 2 | 1 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `resolve_course_id()` L29: 复杂度: 12
- 🔄 `resolve_course_id()` L29: 认知复杂度: 18
- 🏗️ `resolve_course_id()` L29: 中等嵌套: 3
- ❌ L39: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.0, 最大: 12
- 认知复杂度: 平均: 11.0, 最大: 18
- 嵌套深度: 平均: 2.0, 最大: 3
- 函数长度: 平均: 27.5 行, 最大: 42 行
- 文件长度: 54 代码量 (74 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 1 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 0.0% (0/54)
- 命名规范: 无命名违规

### 77. backend\knowledge\teacher_point_views.py

**糟糕指数: 13.62**

> 行数: 171 总计, 147 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 8, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `knowledge_point_update` | L115-152 | 38 | 12 | 1 | 2 | ✓ |
| `knowledge_point_create` | L63-110 | 48 | 10 | 3 | 1 | ✓ |
| `knowledge_point_list` | L26-58 | 33 | 4 | 1 | 1 | ✓ |
| `knowledge_point_delete` | L157-170 | 14 | 2 | 1 | 2 | ✓ |

**全部问题 (12)**

- 🔄 `knowledge_point_update()` L115: 复杂度: 12
- 🔄 `knowledge_point_create()` L63: 认知复杂度: 16
- 🔄 `knowledge_point_update()` L115: 认知复杂度: 14
- 🏗️ `knowledge_point_create()` L63: 中等嵌套: 3
- ❌ L36: 未处理的易出错调用
- ❌ L37: 未处理的易出错调用
- ❌ L38: 未处理的易出错调用
- ❌ L39: 未处理的易出错调用
- ❌ L40: 未处理的易出错调用
- ❌ L41: 未处理的易出错调用
- ❌ L94: 未处理的易出错调用
- ❌ L168: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.0, 最大: 12
- 认知复杂度: 平均: 10.0, 最大: 16
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 33.3 行, 最大: 48 行
- 文件长度: 147 代码量 (171 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 1 个结构问题
- 错误处理: 8/18 个错误被忽略 (44.4%)
- 注释比例: 0.0% (0/147)
- 命名规范: 无命名违规

### 78. backend\tools\dkt_synthetic.py

**糟糕指数: 13.54**

> 行数: 256 总计, 222 代码, 2 注释 | 函数: 8 | 类: 0

**问题**: ⚠️ 其他问题: 4, ❌ 错误处理问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_simulate_student_sequence` | L116-206 | 91 | 5 | 2 | 6 | ✓ |
| `generate_synthetic_data` | L209-255 | 47 | 5 | 2 | 6 | ✓ |
| `_sample_student_profile` | L61-101 | 41 | 3 | 1 | 1 | ✓ |
| `_build_kp_profiles` | L43-58 | 16 | 2 | 1 | 3 | ✓ |
| `_clamp` | L31-32 | 2 | 1 | 0 | 3 | ✗ |
| `_sigmoid` | L35-36 | 2 | 1 | 0 | 1 | ✗ |
| `_mean` | L39-40 | 2 | 1 | 0 | 2 | ✗ |
| `_choose_focus_kp` | L104-113 | 10 | 1 | 0 | 6 | ✓ |

**全部问题 (14)**

- 📏 `_simulate_student_sequence()` L116: 91 代码量
- 📏 `_choose_focus_kp()` L104: 6 参数数量
- 📏 `_simulate_student_sequence()` L116: 6 参数数量
- 📏 `generate_synthetic_data()` L209: 6 参数数量
- ❌ L244: 未处理的易出错调用
- ❌ L245: 未处理的易出错调用
- ❌ L246: 未处理的易出错调用
- 🏷️ `_clamp()` L31: "_clamp" - snake_case
- 🏷️ `_sigmoid()` L35: "_sigmoid" - snake_case
- 🏷️ `_mean()` L39: "_mean" - snake_case
- 🏷️ `_build_kp_profiles()` L43: "_build_kp_profiles" - snake_case
- 🏷️ `_sample_student_profile()` L61: "_sample_student_profile" - snake_case
- 🏷️ `_choose_focus_kp()` L104: "_choose_focus_kp" - snake_case
- 🏷️ `_simulate_student_sequence()` L116: "_simulate_student_sequence" - snake_case

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 5
- 认知复杂度: 平均: 3.9, 最大: 9
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 26.4 行, 最大: 91 行
- 文件长度: 222 代码量 (256 总计)
- 参数数量: 平均: 3.5, 最大: 6
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 3/5 个错误被忽略 (60.0%)
- 注释比例: 0.9% (2/222)
- 命名规范: 发现 7 个违规

### 79. backend\tools\testing.py

**糟糕指数: 13.28**

> 行数: 244 总计, 184 代码, 8 注释 | 函数: 8 | 类: 1

**问题**: 🔄 复杂度问题: 4, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_resolve_course_id` | L158-205 | 48 | 13 | 2 | 3 | ✓ |
| `_load_testdata` | L209-243 | 35 | 10 | 4 | 0 | ✓ |
| `_login` | L121-154 | 34 | 8 | 1 | 3 | ✓ |
| `_print_checks` | L44-71 | 28 | 6 | 2 | 2 | ✓ |
| `_status_flag` | L27-31 | 5 | 4 | 1 | 1 | ✓ |
| `_extract_data` | L99-117 | 19 | 3 | 1 | 1 | ✓ |
| `_supports_unicode_output` | L21-24 | 4 | 2 | 0 | 0 | ✓ |
| `_request` | L75-96 | 22 | 2 | 1 | 2 | ✓ |

**全部问题 (13)**

- 🔄 `_resolve_course_id()` L158: 复杂度: 13
- 🔄 `_resolve_course_id()` L158: 认知复杂度: 17
- 🔄 `_load_testdata()` L209: 认知复杂度: 18
- 🔄 `_load_testdata()` L209: 嵌套深度: 4
- 🏗️ `_load_testdata()` L209: 中等嵌套: 4
- 🏷️ `_supports_unicode_output()` L21: "_supports_unicode_output" - snake_case
- 🏷️ `_status_flag()` L27: "_status_flag" - snake_case
- 🏷️ `_print_checks()` L44: "_print_checks" - snake_case
- 🏷️ `_request()` L75: "_request" - snake_case
- 🏷️ `_extract_data()` L99: "_extract_data" - snake_case
- 🏷️ `_login()` L121: "_login" - snake_case
- 🏷️ `_resolve_course_id()` L158: "_resolve_course_id" - snake_case
- 🏷️ `_load_testdata()` L209: "_load_testdata" - snake_case

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 13
- 认知复杂度: 平均: 9.0, 最大: 18
- 嵌套深度: 平均: 1.5, 最大: 4
- 函数长度: 平均: 24.4 行, 最大: 48 行
- 文件长度: 184 代码量 (244 总计)
- 参数数量: 平均: 1.5, 最大: 3
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 0/5 个错误被忽略 (0.0%)
- 注释比例: 4.3% (8/184)
- 命名规范: 发现 8 个违规

### 80. backend\ai_services\services\path_service.py

**糟糕指数: 13.10**

> 行数: 264 总计, 212 代码, 11 注释 | 函数: 4 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_path` | L37-170 | 134 | 9 | 3 | 4 | ✓ |
| `get_path_progress` | L236-263 | 28 | 4 | 0 | 2 | ✓ |
| `unlock_next_node` | L172-194 | 23 | 2 | 1 | 2 | ✓ |
| `insert_remedial_node` | L196-234 | 39 | 2 | 1 | 4 | ✓ |

**全部问题 (5)**

- 🔄 `generate_path()` L37: 认知复杂度: 15
- 📏 `generate_path()` L37: 134 代码量
- 🏗️ `generate_path()` L37: 中等嵌套: 3
- ❌ L111: 未处理的易出错调用
- ❌ L167: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 9
- 认知复杂度: 平均: 6.8, 最大: 15
- 嵌套深度: 平均: 1.3, 最大: 3
- 函数长度: 平均: 56.0 行, 最大: 134 行
- 文件长度: 212 代码量 (264 总计)
- 参数数量: 平均: 3.0, 最大: 4
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 1 个结构问题
- 错误处理: 2/4 个错误被忽略 (50.0%)
- 注释比例: 5.2% (11/212)
- 命名规范: 无命名违规

### 81. backend\courses\teacher_student_views.py

**糟糕指数: 13.00**

> 行数: 96 总计, 82 代码, 0 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_class_student_profiles` | L52-95 | 44 | 13 | 2 | 2 | ✓ |
| `class_students` | L15-28 | 14 | 5 | 1 | 2 | ✓ |
| `remove_student_from_class` | L33-47 | 15 | 5 | 1 | 3 | ✓ |

**全部问题 (4)**

- 🔄 `get_class_student_profiles()` L52: 复杂度: 13
- 🔄 `get_class_student_profiles()` L52: 认知复杂度: 17
- ❌ L46: 未处理的易出错调用
- ❌ L93: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.7, 最大: 13
- 认知复杂度: 平均: 10.3, 最大: 17
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 24.3 行, 最大: 44 行
- 文件长度: 82 代码量 (96 总计)
- 参数数量: 平均: 2.3, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 2/8 个错误被忽略 (25.0%)
- 注释比例: 0.0% (0/82)
- 命名规范: 无命名违规

### 82. backend\users\services.py

**糟糕指数: 12.97**

> 行数: 389 总计, 317 代码, 2 注释 | 函数: 13 | 类: 1

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_habit_preferences` | L89-115 | 27 | 12 | 1 | 1 | ✓ |
| `update_mastery_from_answers` | L209-276 | 68 | 9 | 3 | 3 | ✓ |
| `get_knowledge_mastery` | L37-65 | 29 | 8 | 1 | 2 | ✓ |
| `get_profile_summary` | L117-147 | 31 | 7 | 1 | 2 | ✓ |
| `_build_cached_profile_result` | L167-187 | 21 | 6 | 1 | 2 | ✓ |
| `_derive_strength_points` | L150-165 | 16 | 5 | 1 | 1 | ✓ |
| `check_assessment_status` | L309-358 | 50 | 5 | 2 | 2 | ✓ |
| `get_ability_scores` | L67-87 | 21 | 4 | 2 | 2 | ✓ |
| `__init__` | L28-35 | 8 | 1 | 0 | 2 | ✓ |
| `get_full_profile` | L189-207 | 19 | 1 | 0 | 2 | ✓ |
| `get_profile_history` | L278-307 | 30 | 1 | 0 | 3 | ✓ |
| `generate_profile_for_course` | L360-375 | 16 | 1 | 0 | 3 | ✓ |
| `get_learner_profile_service` | L378-388 | 11 | 1 | 0 | 1 | ✓ |

**全部问题 (11)**

- 🔄 `get_habit_preferences()` L89: 复杂度: 12
- 🔄 `get_habit_preferences()` L89: 认知复杂度: 14
- 🔄 `update_mastery_from_answers()` L209: 认知复杂度: 15
- 📏 `update_mastery_from_answers()` L209: 68 代码量
- 🏗️ `update_mastery_from_answers()` L209: 中等嵌套: 3
- ❌ L153: 未处理的易出错调用
- ❌ L161: 未处理的易出错调用
- ❌ L263: 未处理的易出错调用
- 🏷️ `__init__()` L28: "__init__" - snake_case
- 🏷️ `_derive_strength_points()` L150: "_derive_strength_points" - snake_case
- 🏷️ `_build_cached_profile_result()` L167: "_build_cached_profile_result" - snake_case

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 12
- 认知复杂度: 平均: 6.5, 最大: 15
- 嵌套深度: 平均: 0.9, 最大: 3
- 函数长度: 平均: 26.7 行, 最大: 68 行
- 文件长度: 317 代码量 (389 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 1 个结构问题
- 错误处理: 3/6 个错误被忽略 (50.0%)
- 注释比例: 0.6% (2/317)
- 命名规范: 发现 3 个违规

### 83. backend\tools\api_regression_student_learning.py

**糟糕指数: 12.96**

> 行数: 273 总计, 259 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_student_path_checks` | L158-272 | 115 | 7 | 3 | 5 | ✓ |
| `_run_student_knowledge_checks` | L41-127 | 87 | 2 | 1 | 4 | ✓ |
| `_run_student_assessment_checks` | L130-155 | 26 | 2 | 1 | 4 | ✓ |
| `_run_student_learning_checks` | L11-38 | 28 | 1 | 0 | 5 | ✓ |

**全部问题 (8)**

- 🔄 `_run_student_path_checks()` L158: 认知复杂度: 13
- 📏 `_run_student_knowledge_checks()` L41: 87 代码量
- 📏 `_run_student_path_checks()` L158: 115 代码量
- 🏗️ `_run_student_path_checks()` L158: 中等嵌套: 3
- 🏷️ `_run_student_learning_checks()` L11: "_run_student_learning_checks" - snake_case
- 🏷️ `_run_student_knowledge_checks()` L41: "_run_student_knowledge_checks" - snake_case
- 🏷️ `_run_student_assessment_checks()` L130: "_run_student_assessment_checks" - snake_case
- 🏷️ `_run_student_path_checks()` L158: "_run_student_path_checks" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 7
- 认知复杂度: 平均: 5.5, 最大: 13
- 嵌套深度: 平均: 1.3, 最大: 3
- 函数长度: 平均: 64.0 行, 最大: 115 行
- 文件长度: 259 代码量 (273 总计)
- 参数数量: 平均: 4.5, 最大: 5
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 1 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/259)
- 命名规范: 发现 4 个违规

### 84. backend\courses\teacher_invitation_views.py

**糟糕指数: 12.84**

> 行数: 99 总计, 86 代码, 0 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_class_invitation` | L21-68 | 48 | 14 | 2 | 1 | ✓ |
| `list_class_invitations` | L73-83 | 11 | 5 | 1 | 2 | ✓ |
| `delete_class_invitation` | L88-98 | 11 | 4 | 1 | 2 | ✓ |

**全部问题 (3)**

- 🔄 `generate_class_invitation()` L21: 复杂度: 14
- 🔄 `generate_class_invitation()` L21: 认知复杂度: 18
- ❌ L97: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.7, 最大: 14
- 认知复杂度: 平均: 10.3, 最大: 18
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 23.3 行, 最大: 48 行
- 文件长度: 86 代码量 (99 总计)
- 参数数量: 平均: 1.7, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 1/8 个错误被忽略 (12.5%)
- 注释比例: 0.0% (0/86)
- 命名规范: 无命名违规

### 85. backend\courses\student_views.py

**糟糕指数: 12.83**

> 行数: 353 总计, 272 代码, 14 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `course_list` | L73-124 | 52 | 10 | 4 | 1 | ✓ |
| `course_select` | L129-183 | 55 | 10 | 2 | 1 | ✓ |
| `student_join_class` | L191-253 | 63 | 9 | 1 | 1 | ✓ |
| `_serialize_student_class` | L48-68 | 21 | 6 | 0 | 1 | ✓ |
| `student_class_detail` | L303-349 | 47 | 6 | 1 | 2 | ✓ |
| `_get_class_course_summaries` | L26-45 | 20 | 5 | 2 | 1 | ✓ |
| `student_leave_class` | L258-275 | 18 | 3 | 1 | 2 | ✓ |
| `_serialize_course_summary` | L17-23 | 7 | 2 | 0 | 1 | ✓ |
| `student_class_list` | L280-298 | 19 | 2 | 1 | 1 | ✓ |

**全部问题 (13)**

- 🔄 `course_list()` L73: 认知复杂度: 18
- 🔄 `course_select()` L129: 认知复杂度: 14
- 🔄 `course_list()` L73: 嵌套深度: 4
- 📏 `course_list()` L73: 52 代码量
- 📏 `course_select()` L129: 55 代码量
- 📏 `student_join_class()` L191: 63 代码量
- 🏗️ `course_list()` L73: 中等嵌套: 4
- ❌ L65: 未处理的易出错调用
- ❌ L66: 未处理的易出错调用
- ❌ L274: 未处理的易出错调用
- 🏷️ `_serialize_course_summary()` L17: "_serialize_course_summary" - snake_case
- 🏷️ `_get_class_course_summaries()` L26: "_get_class_course_summaries" - snake_case
- 🏷️ `_serialize_student_class()` L48: "_serialize_student_class" - snake_case

**详情**:
- 循环复杂度: 平均: 5.9, 最大: 10
- 认知复杂度: 平均: 8.6, 最大: 18
- 嵌套深度: 平均: 1.3, 最大: 4
- 函数长度: 平均: 33.6 行, 最大: 63 行
- 文件长度: 272 代码量 (353 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 3/10 个错误被忽略 (30.0%)
- 注释比例: 5.1% (14/272)
- 命名规范: 发现 3 个违规

### 86. backend\common\question_options.py

**糟糕指数: 12.80**

> 行数: 308 总计, 245 代码, 0 注释 | 函数: 20 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, 📋 重复问题: 2, ❌ 错误处理问题: 5, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_answer_display` | L223-253 | 31 | 10 | 2 | 3 | ✓ |
| `format_option_display` | L209-220 | 12 | 7 | 0 | 1 | ✓ |
| `serialize_answer_payload` | L275-295 | 21 | 7 | 2 | 2 | ✓ |
| `normalize_dict_option` | L119-129 | 11 | 6 | 0 | 3 | ✓ |
| `clean_display_text` | L14-31 | 18 | 5 | 2 | 1 | ✓ |
| `true_false_alias_tokens` | L66-75 | 10 | 4 | 1 | 2 | ✓ |
| `normalize_question_options` | L78-96 | 19 | 4 | 2 | 2 | ✓ |
| `joined_answer_values` | L265-272 | 8 | 4 | 2 | 1 | ✓ |
| `answer_tokens` | L34-48 | 15 | 3 | 2 | 2 | ✓ |
| `answer_values` | L51-58 | 8 | 3 | 1 | 1 | ✓ |
| `default_true_false_options` | L99-106 | 8 | 3 | 1 | 2 | ✓ |
| `normalize_single_option` | L109-116 | 8 | 3 | 1 | 2 | ✓ |
| `normalize_text_option` | L132-137 | 6 | 3 | 0 | 3 | ✓ |
| `first_truthy_option_field` | L140-146 | 7 | 3 | 2 | 2 | ✓ |
| `option_tokens` | L159-171 | 13 | 3 | 2 | 1 | ✓ |
| `display_token_variants` | L61-63 | 3 | 1 | 0 | 1 | ✓ |
| `option_payload` | L149-156 | 8 | 1 | 0 | 3 | ✓ |
| `option_token_values` | L174-181 | 8 | 1 | 0 | 1 | ✓ |
| `decorate_question_options` | L184-206 | 23 | 1 | 0 | 4 | ✓ |
| `matched_option_displays` | L256-262 | 7 | 1 | 0 | 2 | ✓ |

**全部问题 (8)**

- 🔄 `build_answer_display()` L223: 认知复杂度: 14
- 📋 `answer_values()` L51: 重复模式: answer_values, normalize_single_option
- 📋 `option_tokens()` L159: 重复模式: option_tokens, joined_answer_values
- ❌ L177: 未处理的易出错调用
- ❌ L178: 未处理的易出错调用
- ❌ L179: 未处理的易出错调用
- ❌ L180: 未处理的易出错调用
- ❌ L218: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.6, 最大: 10
- 认知复杂度: 平均: 5.7, 最大: 14
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 12.2 行, 最大: 31 行
- 文件长度: 245 代码量 (308 总计)
- 参数数量: 平均: 1.9, 最大: 4
- 代码重复: 10.0% 重复 (2/20)
- 结构分析: 0 个结构问题
- 错误处理: 5/8 个错误被忽略 (62.5%)
- 注释比例: 0.0% (0/245)
- 命名规范: 无命名违规

### 87. backend\platform_ai\rag\runtime_models.py

**糟糕指数: 12.76**

> 行数: 383 总计, 316 代码, 2 注释 | 函数: 20 | 类: 6

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `run` | L328-382 | 55 | 9 | 2 | 5 | ✗ |
| `_message_history_text` | L153-174 | 22 | 8 | 2 | 1 | ✓ |
| `_vector_point_ids` | L210-226 | 17 | 6 | 4 | 1 | ✓ |
| `embed_query` | L248-271 | 24 | 6 | 1 | 2 | ✓ |
| `_coerce_int_list` | L132-145 | 14 | 5 | 2 | 1 | ✓ |
| `_dedupe_strings` | L192-202 | 11 | 4 | 2 | 1 | ✓ |
| `_resolve_delegate` | L288-300 | 13 | 4 | 1 | 1 | ✓ |
| `embed_query` | L302-312 | 11 | 3 | 1 | 2 | ✓ |
| `_coerce_string` | L119-121 | 3 | 2 | 0 | 1 | ✓ |
| `_coerce_int` | L124-129 | 6 | 2 | 1 | 2 | ✓ |
| `_qdrant_point_id` | L229-234 | 6 | 2 | 1 | 1 | ✓ |
| `as_dict` | L50-60 | 11 | 1 | 0 | 1 | ✓ |
| `as_source` | L80-91 | 12 | 1 | 0 | 2 | ✓ |
| `as_dict` | L106-116 | 11 | 1 | 0 | 1 | ✓ |
| `_escape_cypher_string` | L148-150 | 3 | 1 | 0 | 1 | ✓ |
| `_query_tool_parameters` | L177-189 | 13 | 1 | 0 | 1 | ✓ |
| `_compact_excerpt` | L204-207 | 4 | 1 | 0 | 2 | ✓ |
| `__init__` | L244-246 | 3 | 1 | 0 | 2 | ✗ |
| `__init__` | L281-286 | 6 | 1 | 0 | 3 | ✗ |
| `__init__` | L324-326 | 3 | 1 | 0 | 2 | ✗ |

**全部问题 (18)**

- 🔄 `_vector_point_ids()` L210: 认知复杂度: 14
- 🔄 `run()` L328: 认知复杂度: 13
- 🔄 `_vector_point_ids()` L210: 嵌套深度: 4
- 📏 `run()` L328: 55 代码量
- 🏗️ `_vector_point_ids()` L210: 中等嵌套: 4
- ❌ L215: 未处理的易出错调用
- ❌ L216: 未处理的易出错调用
- ❌ L356: 未处理的易出错调用
- 🏷️ `_coerce_string()` L119: "_coerce_string" - snake_case
- 🏷️ `_coerce_int()` L124: "_coerce_int" - snake_case
- 🏷️ `_coerce_int_list()` L132: "_coerce_int_list" - snake_case
- 🏷️ `_escape_cypher_string()` L148: "_escape_cypher_string" - snake_case
- 🏷️ `_message_history_text()` L153: "_message_history_text" - snake_case
- 🏷️ `_query_tool_parameters()` L177: "_query_tool_parameters" - snake_case
- 🏷️ `_dedupe_strings()` L192: "_dedupe_strings" - snake_case
- 🏷️ `_compact_excerpt()` L204: "_compact_excerpt" - snake_case
- 🏷️ `_vector_point_ids()` L210: "_vector_point_ids" - snake_case
- 🏷️ `_qdrant_point_id()` L229: "_qdrant_point_id" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 9
- 认知复杂度: 平均: 4.7, 最大: 14
- 嵌套深度: 平均: 0.8, 最大: 4
- 函数长度: 平均: 12.4 行, 最大: 55 行
- 文件长度: 316 代码量 (383 总计)
- 参数数量: 平均: 1.6, 最大: 5
- 代码重复: 0.0% 重复 (0/20)
- 结构分析: 1 个结构问题
- 错误处理: 3/15 个错误被忽略 (20.0%)
- 注释比例: 0.6% (2/316)
- 命名规范: 发现 14 个违规

### 88. backend\knowledge\resource_views.py

**糟糕指数: 12.68**

> 行数: 120 总计, 105 代码, 0 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_student_resources` | L13-73 | 61 | 15 | 1 | 1 | ✓ |
| `knowledge_point_resources` | L78-96 | 19 | 4 | 1 | 2 | ✓ |
| `knowledge_search` | L101-119 | 19 | 4 | 1 | 1 | ✓ |

**全部问题 (3)**

- 🔄 `get_student_resources()` L13: 复杂度: 15
- 🔄 `get_student_resources()` L13: 认知复杂度: 17
- 📏 `get_student_resources()` L13: 61 代码量

**详情**:
- 循环复杂度: 平均: 7.7, 最大: 15
- 认知复杂度: 平均: 9.7, 最大: 17
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 33.0 行, 最大: 61 行
- 文件长度: 105 代码量 (120 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/9 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/105)
- 命名规范: 无命名违规

### 89. backend\tools\api_regression_teacher.py

**糟糕指数: 12.58**

> 行数: 343 总计, 299 代码, 0 注释 | 函数: 14 | 类: 1

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_response_id` | L328-342 | 15 | 7 | 2 | 3 | ✓ |
| `_create_question` | L129-164 | 36 | 3 | 1 | 2 | ✓ |
| `_create_exam` | L206-243 | 38 | 3 | 1 | 1 | ✓ |
| `_run_teacher_list_checks` | L270-280 | 11 | 3 | 1 | 1 | ✓ |
| `_run_teacher_regression` | L34-66 | 33 | 2 | 1 | 6 | ✓ |
| `_run_teacher_mutation_checks` | L75-82 | 8 | 2 | 1 | 1 | ✓ |
| `_create_course` | L85-109 | 25 | 2 | 1 | 1 | ✓ |
| `_create_class` | L167-190 | 24 | 2 | 1 | 1 | ✓ |
| `_publish_and_unpublish_exam` | L246-267 | 22 | 2 | 1 | 2 | ✓ |
| `_run_teacher_read_checks` | L69-72 | 4 | 1 | 0 | 1 | ✓ |
| `_create_knowledge_point` | L112-126 | 15 | 1 | 0 | 1 | ✓ |
| `_create_invitation` | L193-203 | 11 | 1 | 0 | 1 | ✓ |
| `_record_get` | L283-298 | 16 | 1 | 0 | 4 | ✓ |
| `_record_request` | L301-325 | 25 | 1 | 0 | 8 | ✓ |

**全部问题 (12)**

- 📏 `_run_teacher_regression()` L34: 6 参数数量
- 📏 `_record_request()` L301: 8 参数数量
- 🏷️ `_run_teacher_regression()` L34: "_run_teacher_regression" - snake_case
- 🏷️ `_run_teacher_read_checks()` L69: "_run_teacher_read_checks" - snake_case
- 🏷️ `_run_teacher_mutation_checks()` L75: "_run_teacher_mutation_checks" - snake_case
- 🏷️ `_create_course()` L85: "_create_course" - snake_case
- 🏷️ `_create_knowledge_point()` L112: "_create_knowledge_point" - snake_case
- 🏷️ `_create_question()` L129: "_create_question" - snake_case
- 🏷️ `_create_class()` L167: "_create_class" - snake_case
- 🏷️ `_create_invitation()` L193: "_create_invitation" - snake_case
- 🏷️ `_create_exam()` L206: "_create_exam" - snake_case
- 🏷️ `_publish_and_unpublish_exam()` L246: "_publish_and_unpublish_exam" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 7
- 认知复杂度: 平均: 3.6, 最大: 11
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 20.2 行, 最大: 38 行
- 文件长度: 299 代码量 (343 总计)
- 参数数量: 平均: 2.4, 最大: 8
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/299)
- 命名规范: 发现 14 个违规

### 90. backend\users\admin_profile_views.py

**糟糕指数: 12.41**

> 行数: 115 总计, 99 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `admin_get_all_student_profiles` | L19-68 | 50 | 11 | 2 | 1 | ✓ |
| `admin_student_profile_detail` | L73-114 | 42 | 8 | 1 | 2 | ✓ |

**全部问题 (3)**

- 🔄 `admin_get_all_student_profiles()` L19: 复杂度: 11
- 🔄 `admin_get_all_student_profiles()` L19: 认知复杂度: 15
- ❌ L65: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 9.5, 最大: 11
- 认知复杂度: 平均: 12.5, 最大: 15
- 嵌套深度: 平均: 1.5, 最大: 2
- 函数长度: 平均: 46.0 行, 最大: 50 行
- 文件长度: 99 代码量 (115 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 0.0% (0/99)
- 命名规范: 无命名违规

### 91. backend\ai_services\services\kt_prediction_modes.py

**糟糕指数: 12.29**

> 行数: 302 总计, 265 代码, 0 注释 | 函数: 8 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `predict_mastery` | L22-69 | 48 | 9 | 2 | 5 | ✓ |
| `_ensemble_predict` | L104-156 | 53 | 6 | 2 | 5 | ✓ |
| `_fuse_predictions` | L206-231 | 26 | 6 | 3 | 2 | ✓ |
| `_fusion_predict` | L158-204 | 47 | 4 | 1 | 5 | ✓ |
| `batch_predict` | L251-270 | 20 | 4 | 1 | 2 | ✓ |
| `_single_model_predict` | L71-102 | 32 | 3 | 1 | 5 | ✓ |
| `get_learning_recommendations` | L272-301 | 30 | 3 | 1 | 5 | ✓ |
| `_builtin_prediction` | L233-249 | 17 | 1 | 0 | 5 | ✓ |

**全部问题 (11)**

- 🔄 `predict_mastery()` L22: 认知复杂度: 13
- 📏 `_ensemble_predict()` L104: 53 代码量
- 🏗️ `_fuse_predictions()` L206: 中等嵌套: 3
- ❌ L42: 未处理的易出错调用
- ❌ L127: 未处理的易出错调用
- ❌ L181: 未处理的易出错调用
- 🏷️ `_single_model_predict()` L71: "_single_model_predict" - snake_case
- 🏷️ `_ensemble_predict()` L104: "_ensemble_predict" - snake_case
- 🏷️ `_fusion_predict()` L158: "_fusion_predict" - snake_case
- 🏷️ `_fuse_predictions()` L206: "_fuse_predictions" - snake_case
- 🏷️ `_builtin_prediction()` L233: "_builtin_prediction" - snake_case

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 9
- 认知复杂度: 平均: 7.3, 最大: 13
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 34.1 行, 最大: 53 行
- 文件长度: 265 代码量 (302 总计)
- 参数数量: 平均: 4.3, 最大: 5
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 3/8 个错误被忽略 (37.5%)
- 注释比例: 0.0% (0/265)
- 命名规范: 发现 5 个违规

### 92. backend\users\test_models.py

**糟糕指数: 12.23**

> 行数: 166 总计, 143 代码, 0 注释 | 函数: 13 | 类: 3

**问题**: 📋 重复问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_create_student` | L14-25 | 12 | 1 | 0 | 1 | ✓ |
| `test_create_teacher` | L27-37 | 11 | 1 | 0 | 1 | ✓ |
| `test_create_admin` | L39-48 | 10 | 1 | 0 | 1 | ✓ |
| `setUp` | L54-61 | 8 | 1 | 0 | 1 | ✓ |
| `test_generate_code` | L63-67 | 5 | 1 | 0 | 1 | ✓ |
| `test_create_activation_code` | L69-77 | 9 | 1 | 0 | 1 | ✓ |
| `test_use_activation_code` | L79-95 | 17 | 1 | 0 | 1 | ✓ |
| `test_cannot_reuse_activation_code` | L97-105 | 9 | 1 | 0 | 1 | ✓ |
| `setUp` | L111-126 | 16 | 1 | 0 | 1 | ✓ |
| `test_generate_code` | L128-132 | 5 | 1 | 0 | 1 | ✓ |
| `test_create_invitation` | L134-142 | 9 | 1 | 0 | 1 | ✓ |
| `test_use_invitation` | L144-152 | 9 | 1 | 0 | 1 | ✓ |
| `test_invitation_max_uses` | L154-165 | 12 | 1 | 0 | 1 | ✓ |

**全部问题 (4)**

- 📋 `test_create_student()` L14: 重复模式: test_create_student, test_create_teacher, test_create_admin, setUp, test_cannot_reuse_activation_code, test_invitation_max_uses
- 📋 `test_create_activation_code()` L69: 重复模式: test_create_activation_code, test_create_invitation, test_use_invitation
- 🏷️ `setUp()` L54: "setUp" - snake_case
- 🏷️ `setUp()` L111: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 10.2 行, 最大: 17 行
- 文件长度: 143 代码量 (166 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 53.8% 重复 (7/13)
- 结构分析: 0 个结构问题
- 错误处理: 0/8 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/143)
- 命名规范: 发现 2 个违规

### 93. backend\learning\serializers.py

**糟糕指数: 11.95**

> 行数: 117 总计, 98 代码, 0 注释 | 函数: 6 | 类: 4

**问题**: 📋 重复问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_progress` | L75-94 | 20 | 6 | 2 | 2 | ✗ |
| `get_mastery_before` | L96-105 | 10 | 6 | 2 | 2 | ✗ |
| `get_mastery_after` | L107-116 | 10 | 6 | 2 | 2 | ✗ |
| `get_resources` | L55-63 | 9 | 3 | 0 | 1 | ✗ |
| `get_tasks_count` | L20-21 | 2 | 2 | 0 | 1 | ✗ |
| `get_exercises` | L66-73 | 8 | 2 | 1 | 1 | ✗ |

**全部问题 (1)**

- 📋 `get_progress()` L75: 重复模式: get_progress, get_mastery_before, get_mastery_after

**详情**:
- 循环复杂度: 平均: 4.2, 最大: 6
- 认知复杂度: 平均: 6.5, 最大: 10
- 嵌套深度: 平均: 1.2, 最大: 2
- 函数长度: 平均: 9.8 行, 最大: 20 行
- 文件长度: 98 代码量 (117 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 33.3% 重复 (2/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/98)
- 命名规范: 无命名违规

### 94. backend\tools\api_regression_student_exam_ai.py

**糟糕指数: 11.95**

> 行数: 241 总计, 231 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: ⚠️ 其他问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_student_exam_checks` | L11-131 | 121 | 5 | 1 | 4 | ✓ |
| `_run_student_ai_kt_checks` | L134-240 | 107 | 3 | 1 | 5 | ✓ |

**全部问题 (4)**

- 📏 `_run_student_exam_checks()` L11: 121 代码量
- 📏 `_run_student_ai_kt_checks()` L134: 107 代码量
- 🏷️ `_run_student_exam_checks()` L11: "_run_student_exam_checks" - snake_case
- 🏷️ `_run_student_ai_kt_checks()` L134: "_run_student_ai_kt_checks" - snake_case

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 5
- 认知复杂度: 平均: 6.0, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 114.0 行, 最大: 121 行
- 文件长度: 231 代码量 (241 总计)
- 参数数量: 平均: 4.5, 最大: 5
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/231)
- 命名规范: 发现 2 个违规

### 95. backend\tools\api_regression_student_basics.py

**糟糕指数: 11.94**

> 行数: 139 总计, 131 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_student_basic_checks` | L11-138 | 128 | 2 | 1 | 4 | ✓ |

**全部问题 (2)**

- 📏 `_run_student_basic_checks()` L11: 128 代码量
- 🏷️ `_run_student_basic_checks()` L11: "_run_student_basic_checks" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 128.0 行, 最大: 128 行
- 文件长度: 131 代码量 (139 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/131)
- 命名规范: 发现 1 个违规

### 96. backend\ai_services\test_student_rag_context.py

**糟糕指数: 11.94**

> 行数: 235 总计, 213 代码, 0 注释 | 函数: 6 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 2, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_build_path_context_should_expose_multi_mode_sources` | L38-53 | 16 | 1 | 0 | 2 | ✓ |
| `test_answer_graph_question_should_fallback_to_graph_context_when_llm_unavailable` | L57-73 | 17 | 1 | 0 | 3 | ✓ |
| `test_local_context_should_merge_vector_hits_into_sources` | L77-105 | 29 | 1 | 0 | 3 | ✓ |
| `test_answer_graph_question_should_merge_graph_query_sources` | L110-149 | 40 | 1 | 0 | 4 | ✓ |
| `test_build_point_support_payload_should_include_graph_query_summary` | L153-189 | 37 | 1 | 0 | 3 | ✓ |
| `test_answer_course_question_should_merge_course_level_graph_sources` | L194-234 | 41 | 1 | 0 | 4 | ✓ |

**全部问题 (2)**

- 📋 `test_build_path_context_should_expose_multi_mode_sources()` L38: 重复模式: test_build_path_context_should_expose_multi_mode_sources, test_answer_graph_question_should_fallback_to_graph_context_when_llm_unavailable
- 📋 `test_answer_graph_question_should_merge_graph_query_sources()` L110: 重复模式: test_answer_graph_question_should_merge_graph_query_sources, test_answer_course_question_should_merge_course_level_graph_sources

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 30.0 行, 最大: 41 行
- 文件长度: 213 代码量 (235 总计)
- 参数数量: 平均: 3.2, 最大: 4
- 代码重复: 33.3% 重复 (2/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/213)
- 命名规范: 无命名违规

### 97. backend\knowledge\teacher_map_support.py

**糟糕指数: 11.81**

> 行数: 126 总计, 109 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 3, 🏗️ 结构问题: 2, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `persist_imported_knowledge_map` | L94-125 | 32 | 9 | 3 | 3 | ✓ |
| `parse_imported_knowledge_map` | L58-91 | 34 | 8 | 4 | 1 | ✓ |
| `update_existing_graph_nodes` | L12-35 | 24 | 5 | 2 | 2 | ✓ |
| `rebuild_graph_relations` | L38-55 | 18 | 5 | 2 | 2 | ✓ |

**全部问题 (8)**

- 🔄 `parse_imported_knowledge_map()` L58: 认知复杂度: 16
- 🔄 `persist_imported_knowledge_map()` L94: 认知复杂度: 15
- 🔄 `parse_imported_knowledge_map()` L58: 嵌套深度: 4
- 🏗️ `parse_imported_knowledge_map()` L58: 中等嵌套: 4
- 🏗️ `persist_imported_knowledge_map()` L94: 中等嵌套: 3
- ❌ L74: 未处理的易出错调用
- ❌ L75: 未处理的易出错调用
- ❌ L76: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 6.8, 最大: 9
- 认知复杂度: 平均: 12.3, 最大: 16
- 嵌套深度: 平均: 2.8, 最大: 4
- 函数长度: 平均: 27.0 行, 最大: 34 行
- 文件长度: 109 代码量 (126 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 2 个结构问题
- 错误处理: 3/22 个错误被忽略 (13.6%)
- 注释比例: 0.0% (0/109)
- 命名规范: 无命名违规

### 98. backend\platform_ai\rag\runtime_materialization_mixin.py

**糟糕指数: 11.81**

> 行数: 257 总计, 229 代码, 0 注释 | 函数: 13 | 类: 1

**问题**: 🔄 复杂度问题: 1, ❌ 错误处理问题: 17, 📝 注释问题: 1, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_projection_from_graph` | L119-160 | 42 | 10 | 2 | 2 | ✓ |
| `_embedder` | L70-84 | 15 | 6 | 1 | 1 | ✓ |
| `_vector_points` | L162-195 | 34 | 5 | 2 | 3 | ✓ |
| `materialize_course_payload` | L197-234 | 38 | 5 | 1 | 3 | ✓ |
| `ensure_materialized` | L236-244 | 9 | 5 | 1 | 3 | ✓ |
| `_build_chunks` | L94-117 | 24 | 4 | 1 | 2 | ✓ |
| `clear_course_payload` | L246-256 | 11 | 3 | 1 | 2 | ✓ |
| `_vector_dimension` | L44-49 | 6 | 2 | 1 | 1 | ✓ |
| `qdrant_directory` | L51-56 | 6 | 2 | 1 | 1 | ✓ |
| `_qdrant` | L62-68 | 7 | 2 | 1 | 1 | ✓ |
| `_collection_exists` | L86-92 | 7 | 2 | 1 | 2 | ✓ |
| `__init__` | L38-42 | 5 | 1 | 0 | 1 | ✗ |
| `collection_name` | L58-60 | 3 | 1 | 0 | 2 | ✓ |

**全部问题 (26)**

- 🔄 `_projection_from_graph()` L119: 认知复杂度: 14
- ❌ L108: 未处理的易出错调用
- ❌ L109: 未处理的易出错调用
- ❌ L110: 未处理的易出错调用
- ❌ L111: 未处理的易出错调用
- ❌ L130: 未处理的易出错调用
- ❌ L131: 未处理的易出错调用
- ❌ L132: 未处理的易出错调用
- ❌ L133: 未处理的易出错调用
- ❌ L134: 未处理的易出错调用
- ❌ L135: 未处理的易出错调用
- ❌ L136: 未处理的易出错调用
- ❌ L138: 未处理的易出错调用
- ❌ L140: 未处理的易出错调用
- ❌ L181: 未处理的易出错调用
- ❌ L182: 未处理的易出错调用
- ❌ L183: 未处理的易出错调用
- ❌ L184: 未处理的易出错调用
- 🏷️ `__init__()` L38: "__init__" - snake_case
- 🏷️ `_vector_dimension()` L44: "_vector_dimension" - snake_case
- 🏷️ `_qdrant()` L62: "_qdrant" - snake_case
- 🏷️ `_embedder()` L70: "_embedder" - snake_case
- 🏷️ `_collection_exists()` L86: "_collection_exists" - snake_case
- 🏷️ `_build_chunks()` L94: "_build_chunks" - snake_case
- 🏷️ `_projection_from_graph()` L119: "_projection_from_graph" - snake_case
- 🏷️ `_vector_points()` L162: "_vector_points" - snake_case

**详情**:
- 循环复杂度: 平均: 3.7, 最大: 10
- 认知复杂度: 平均: 5.7, 最大: 14
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 15.9 行, 最大: 42 行
- 文件长度: 229 代码量 (257 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 17/30 个错误被忽略 (56.7%)
- 注释比例: 0.0% (0/229)
- 命名规范: 发现 8 个违规

### 99. backend\common\defense_demo_path.py

**糟糕指数: 11.81**

> 行数: 385 总计, 351 代码, 0 注释 | 函数: 13 | 类: 0

**问题**: ⚠️ 其他问题: 5, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_complete_study_progress` | L320-349 | 30 | 7 | 1 | 5 | ✓ |
| `_complete_stage_progress` | L352-384 | 33 | 7 | 1 | 5 | ✓ |
| `_apply_demo_progress_payload` | L219-238 | 20 | 5 | 1 | 4 | ✓ |
| `_collect_mastery_change` | L305-317 | 13 | 5 | 1 | 3 | ✓ |
| `_apply_completed_statuses` | L271-286 | 16 | 4 | 2 | 1 | ✓ |
| `_mastery_maps_from_result` | L289-302 | 14 | 4 | 2 | 1 | ✓ |
| `_ensure_demo_learning_path` | L16-52 | 37 | 2 | 1 | 6 | ✓ |
| `_sync_demo_nodes` | L140-166 | 27 | 2 | 1 | 6 | ✓ |
| `_upsert_demo_node` | L169-205 | 37 | 2 | 0 | 6 | ✓ |
| `_apply_completed_stage_result` | L241-268 | 28 | 2 | 1 | 5 | ✓ |
| `_upsert_demo_path` | L55-65 | 11 | 1 | 0 | 2 | ✓ |
| `_demo_node_specs` | L68-137 | 70 | 1 | 0 | 1 | ✓ |
| `_progress_defaults` | L208-216 | 9 | 1 | 0 | 0 | ✓ |

**全部问题 (16)**

- 📏 `_demo_node_specs()` L68: 70 代码量
- 📏 `_ensure_demo_learning_path()` L16: 6 参数数量
- 📏 `_sync_demo_nodes()` L140: 6 参数数量
- 📏 `_upsert_demo_node()` L169: 6 参数数量
- ❌ L232: 未处理的易出错调用
- ❌ L335: 未处理的易出错调用
- 🏷️ `_ensure_demo_learning_path()` L16: "_ensure_demo_learning_path" - snake_case
- 🏷️ `_upsert_demo_path()` L55: "_upsert_demo_path" - snake_case
- 🏷️ `_demo_node_specs()` L68: "_demo_node_specs" - snake_case
- 🏷️ `_sync_demo_nodes()` L140: "_sync_demo_nodes" - snake_case
- 🏷️ `_upsert_demo_node()` L169: "_upsert_demo_node" - snake_case
- 🏷️ `_progress_defaults()` L208: "_progress_defaults" - snake_case
- 🏷️ `_apply_demo_progress_payload()` L219: "_apply_demo_progress_payload" - snake_case
- 🏷️ `_apply_completed_stage_result()` L241: "_apply_completed_stage_result" - snake_case
- 🏷️ `_apply_completed_statuses()` L271: "_apply_completed_statuses" - snake_case
- 🏷️ `_mastery_maps_from_result()` L289: "_mastery_maps_from_result" - snake_case

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 7
- 认知复杂度: 平均: 5.0, 最大: 9
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 26.5 行, 最大: 70 行
- 文件长度: 351 代码量 (385 总计)
- 参数数量: 平均: 3.5, 最大: 6
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 2/12 个错误被忽略 (16.7%)
- 注释比例: 0.0% (0/351)
- 命名规范: 发现 13 个违规

### 100. backend\tools\common.py

**糟糕指数: 11.80**

> 行数: 210 总计, 168 代码, 4 注释 | 函数: 9 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_course_asset_bundle` | L106-197 | 92 | 14 | 3 | 2 | ✓ |
| `clean_nan` | L81-90 | 10 | 5 | 1 | 1 | ✓ |
| `safe_float` | L93-103 | 11 | 5 | 2 | 2 | ✓ |
| `list_courses` | L200-209 | 10 | 5 | 1 | 1 | ✓ |
| `split_multi_values` | L43-46 | 4 | 3 | 0 | 1 | ✓ |
| `find_first_file` | L49-55 | 7 | 3 | 2 | 2 | ✓ |
| `load_json` | L64-70 | 7 | 3 | 1 | 1 | ✓ |
| `resolve_path` | L58-61 | 4 | 2 | 0 | 1 | ✓ |
| `get_course` | L73-78 | 6 | 2 | 1 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `build_course_asset_bundle()` L106: 复杂度: 14
- 🔄 `build_course_asset_bundle()` L106: 认知复杂度: 20
- 📏 `build_course_asset_bundle()` L106: 92 代码量
- 🏗️ `build_course_asset_bundle()` L106: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 14
- 认知复杂度: 平均: 7.1, 最大: 20
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 16.8 行, 最大: 92 行
- 文件长度: 168 代码量 (210 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 2.4% (4/168)
- 命名规范: 无命名违规

### 101. backend\learning\path_views.py

**糟糕指数: 11.79**

> 行数: 134 总计, 110 代码, 1 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_learning_path` | L22-86 | 65 | 14 | 2 | 1 | ✓ |
| `adjust_learning_path` | L91-124 | 34 | 5 | 1 | 1 | ✓ |
| `generate_initial_path` | L127-133 | 7 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- 🔄 `get_learning_path()` L22: 复杂度: 14
- 🔄 `get_learning_path()` L22: 认知复杂度: 18
- 📏 `get_learning_path()` L22: 65 代码量

**详情**:
- 循环复杂度: 平均: 6.7, 最大: 14
- 认知复杂度: 平均: 8.7, 最大: 18
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 35.3 行, 最大: 65 行
- 文件长度: 110 代码量 (134 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 0.9% (1/110)
- 命名规范: 无命名违规

### 102. backend\common\neo4j_queries.py

**糟糕指数: 11.67**

> 行数: 266 总计, 246 代码, 0 注释 | 函数: 8 | 类: 1

**问题**: 📋 重复问题: 2, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `find_learning_path` | L56-88 | 33 | 6 | 2 | 3 | ✓ |
| `get_knowledge_map` | L112-160 | 49 | 5 | 2 | 3 | ✓ |
| `get_knowledge_point_neo4j` | L162-211 | 50 | 5 | 3 | 2 | ✓ |
| `get_knowledge_points_neo4j` | L213-239 | 27 | 4 | 2 | 2 | ✓ |
| `get_knowledge_relations_neo4j` | L241-265 | 25 | 4 | 2 | 2 | ✓ |
| `get_graph_stats` | L90-110 | 21 | 3 | 2 | 2 | ✓ |
| `get_prerequisites` | L14-33 | 20 | 2 | 1 | 3 | ✓ |
| `get_dependents` | L35-54 | 20 | 2 | 1 | 3 | ✓ |

**全部问题 (3)**

- 📋 `get_prerequisites()` L14: 重复模式: get_prerequisites, get_dependents
- 📋 `get_knowledge_points_neo4j()` L213: 重复模式: get_knowledge_points_neo4j, get_knowledge_relations_neo4j
- 🏗️ `get_knowledge_point_neo4j()` L162: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 3.9, 最大: 6
- 认知复杂度: 平均: 7.6, 最大: 11
- 嵌套深度: 平均: 1.9, 最大: 3
- 函数长度: 平均: 30.6 行, 最大: 50 行
- 文件长度: 246 代码量 (266 总计)
- 参数数量: 平均: 2.5, 最大: 3
- 代码重复: 25.0% 重复 (2/8)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/246)
- 命名规范: 无命名违规

### 103. backend\tools\db_management.py

**糟糕指数: 11.61**

> 行数: 201 总计, 161 代码, 0 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `pg_bootstrap` | L158-200 | 43 | 8 | 2 | 4 | ✓ |
| `clear_database` | L56-132 | 77 | 5 | 2 | 1 | ✓ |
| `create_test_data` | L135-155 | 21 | 4 | 1 | 0 | ✓ |
| `django_check` | L39-53 | 15 | 2 | 1 | 1 | ✓ |
| `db_check` | L17-36 | 20 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 📏 `clear_database()` L56: 77 代码量
- ❌ L129: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 8
- 认知复杂度: 平均: 6.4, 最大: 12
- 嵌套深度: 平均: 1.2, 最大: 2
- 函数长度: 平均: 35.2 行, 最大: 77 行
- 文件长度: 161 代码量 (201 总计)
- 参数数量: 平均: 1.4, 最大: 4
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/161)
- 命名规范: 无命名违规

### 104. backend\platform_ai\rag\runtime_graph_query_mixin.py

**糟糕指数: 11.51**

> 行数: 359 总计, 329 代码, 0 注释 | 函数: 13 | 类: 1

**问题**: ⚠️ 其他问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_available_tools` | L243-287 | 45 | 6 | 2 | 7 | ✓ |
| `_text2cypher_tool_result` | L168-224 | 57 | 5 | 1 | 5 | ✓ |
| `query_graph` | L323-358 | 36 | 5 | 1 | 6 | ✓ |
| `_graph_query_examples` | L50-91 | 42 | 3 | 0 | 4 | ✓ |
| `_semantic_tool_result` | L128-166 | 39 | 2 | 0 | 5 | ✓ |
| `_graph_query_schema` | L34-48 | 15 | 1 | 0 | 1 | ✓ |
| `_text2cypher_prompt` | L93-122 | 30 | 1 | 0 | 1 | ✓ |
| `_graph_record_formatter` | L124-126 | 3 | 1 | 0 | 2 | ✓ |
| `_graph_tools_system_instruction` | L226-233 | 8 | 1 | 0 | 1 | ✓ |
| `_tool_line` | L235-237 | 3 | 1 | 0 | 2 | ✓ |
| `_tool_source` | L239-241 | 3 | 1 | 0 | 2 | ✓ |
| `_query_graph_semantic_only` | L289-304 | 16 | 1 | 0 | 5 | ✓ |
| `_query_graph_with_tools` | L306-321 | 16 | 1 | 0 | 4 | ✓ |

**全部问题 (13)**

- 📏 `_text2cypher_tool_result()` L168: 57 代码量
- 📏 `_build_available_tools()` L243: 7 参数数量
- 📏 `query_graph()` L323: 6 参数数量
- 🏷️ `_graph_query_schema()` L34: "_graph_query_schema" - snake_case
- 🏷️ `_graph_query_examples()` L50: "_graph_query_examples" - snake_case
- 🏷️ `_text2cypher_prompt()` L93: "_text2cypher_prompt" - snake_case
- 🏷️ `_graph_record_formatter()` L124: "_graph_record_formatter" - snake_case
- 🏷️ `_semantic_tool_result()` L128: "_semantic_tool_result" - snake_case
- 🏷️ `_text2cypher_tool_result()` L168: "_text2cypher_tool_result" - snake_case
- 🏷️ `_graph_tools_system_instruction()` L226: "_graph_tools_system_instruction" - snake_case
- 🏷️ `_tool_line()` L235: "_tool_line" - snake_case
- 🏷️ `_tool_source()` L239: "_tool_source" - snake_case
- 🏷️ `_build_available_tools()` L243: "_build_available_tools" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 6
- 认知复杂度: 平均: 2.8, 最大: 10
- 嵌套深度: 平均: 0.3, 最大: 2
- 函数长度: 平均: 24.1 行, 最大: 57 行
- 文件长度: 329 代码量 (359 总计)
- 参数数量: 平均: 3.5, 最大: 7
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/329)
- 命名规范: 发现 12 个违规

### 105. backend\assessments\knowledge_generation.py

**糟糕指数: 11.35**

> 行数: 102 总计, 86 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `async_generate_after_assessment` | L25-101 | 77 | 8 | 2 | 4 | ✓ |

**全部问题 (1)**

- 📏 `async_generate_after_assessment()` L25: 77 代码量

**详情**:
- 循环复杂度: 平均: 8.0, 最大: 8
- 认知复杂度: 平均: 12.0, 最大: 12
- 嵌套深度: 平均: 2.0, 最大: 2
- 函数长度: 平均: 77.0 行, 最大: 77 行
- 文件长度: 86 代码量 (102 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/86)
- 命名规范: 无命名违规

### 106. backend\ai_services\services\mefkt_legacy_runtime.py

**糟糕指数: 11.27**

> 行数: 354 总计, 310 代码, 0 注释 | 函数: 14 | 类: 1

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_legacy_state` | L156-203 | 48 | 7 | 1 | 5 | ✓ |
| `build_question_online_state` | L121-153 | 33 | 6 | 0 | 5 | ✓ |
| `load_mefkt_state` | L54-90 | 37 | 5 | 1 | 3 | ✓ |
| `resolve_backend_path` | L41-51 | 11 | 4 | 1 | 2 | ✓ |
| `load_metadata_payload` | L100-109 | 10 | 4 | 1 | 2 | ✓ |
| `build_history_tensors_legacy` | L261-287 | 27 | 4 | 2 | 2 | ✓ |
| `resolve_metadata_path` | L93-97 | 5 | 3 | 0 | 3 | ✓ |
| `is_question_online_checkpoint` | L112-118 | 7 | 3 | 0 | 2 | ✓ |
| `predict_legacy_mastery` | L211-258 | 48 | 3 | 1 | 5 | ✓ |
| `resolve_legacy_target_ids` | L290-304 | 15 | 3 | 1 | 3 | ✓ |
| `cast_tensor_state` | L206-208 | 3 | 2 | 0 | 1 | ✓ |
| `predict_legacy_candidates` | L317-346 | 30 | 2 | 1 | 8 | ✓ |
| `empty_legacy_prediction` | L307-314 | 8 | 1 | 0 | 0 | ✓ |
| `legacy_confidence` | L349-353 | 5 | 1 | 0 | 3 | ✓ |

**全部问题 (4)**

- 📏 `predict_legacy_candidates()` L317: 8 参数数量
- ❌ L141: 未处理的易出错调用
- ❌ L149: 未处理的易出错调用
- ❌ L302: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.4, 最大: 7
- 认知复杂度: 平均: 4.7, 最大: 9
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 20.5 行, 最大: 48 行
- 文件长度: 310 代码量 (354 总计)
- 参数数量: 平均: 3.1, 最大: 8
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 3/15 个错误被忽略 (20.0%)
- 注释比例: 0.0% (0/310)
- 命名规范: 无命名违规

### 107. backend\ai_services\services\llm_profile_path_support.py

**糟糕指数: 11.23**

> 行数: 337 总计, 288 代码, 0 注释 | 函数: 14 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 23, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_path_constraints_text` | L153-191 | 39 | 7 | 1 | 1 | ✓ |
| `summarize_path_strengths_and_weaknesses` | L130-150 | 21 | 6 | 0 | 1 | ✓ |
| `build_profile_course_context` | L7-20 | 14 | 5 | 1 | 2 | ✓ |
| `summarize_mastery_distribution` | L33-46 | 14 | 5 | 1 | 1 | ✓ |
| `build_path_prompt` | L194-241 | 48 | 5 | 0 | 5 | ✓ |
| `build_path_fallback` | L244-272 | 29 | 5 | 0 | 1 | ✓ |
| `resolve_learning_stage` | L275-285 | 11 | 5 | 1 | 1 | ✓ |
| `build_profile_prompt` | L67-117 | 51 | 4 | 0 | 6 | ✓ |
| `build_resource_reason_prompt` | L288-316 | 29 | 4 | 0 | 4 | ✓ |
| `build_resource_reason_fallback` | L319-336 | 18 | 3 | 0 | 3 | ✓ |
| `format_mastery_lines` | L23-30 | 8 | 2 | 0 | 1 | ✓ |
| `identify_weaknesses` | L49-55 | 7 | 2 | 0 | 1 | ✓ |
| `identify_strengths` | L58-64 | 7 | 2 | 0 | 1 | ✓ |
| `build_profile_fallback` | L120-127 | 8 | 1 | 0 | 1 | ✓ |

**全部问题 (25)**

- 📏 `build_profile_prompt()` L67: 51 代码量
- 📏 `build_profile_prompt()` L67: 6 参数数量
- ❌ L27: 未处理的易出错调用
- ❌ L40: 未处理的易出错调用
- ❌ L52: 未处理的易出错调用
- ❌ L54: 未处理的易出错调用
- ❌ L61: 未处理的易出错调用
- ❌ L136: 未处理的易出错调用
- ❌ L141: 未处理的易出错调用
- ❌ L143: 未处理的易出错调用
- ❌ L146: 未处理的易出错调用
- ❌ L157: 未处理的易出错调用
- ❌ L172: 未处理的易出错调用
- ❌ L174: 未处理的易出错调用
- ❌ L176: 未处理的易出错调用
- ❌ L181: 未处理的易出错调用
- ❌ L189: 未处理的易出错调用
- ❌ L249: 未处理的易出错调用
- ❌ L255: 未处理的易出错调用
- ❌ L256: 未处理的易出错调用
- ❌ L257: 未处理的易出错调用
- ❌ L302: 未处理的易出错调用
- ❌ L303: 未处理的易出错调用
- ❌ L304: 未处理的易出错调用
- ❌ L333: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 7
- 认知复杂度: 平均: 4.6, 最大: 9
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 21.7 行, 最大: 51 行
- 文件长度: 288 代码量 (337 总计)
- 参数数量: 平均: 2.1, 最大: 6
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 23/31 个错误被忽略 (74.2%)
- 注释比例: 0.0% (0/288)
- 命名规范: 无命名违规

### 108. backend\assessments\assessment_helpers.py

**糟糕指数: 11.20**

> 行数: 184 总计, 151 代码, 0 注释 | 函数: 12 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `format_option_display` | L72-76 | 5 | 7 | 0 | 1 | ✓ |
| `get_question_title` | L93-102 | 10 | 5 | 1 | 1 | ✓ |
| `extract_answer_payload` | L53-59 | 7 | 3 | 2 | 1 | ✓ |
| `calculate_initial_mastery_baseline` | L39-50 | 12 | 2 | 1 | 2 | ✓ |
| `persist_mastery_snapshot` | L110-139 | 30 | 2 | 1 | 4 | ✓ |
| `upsert_knowledge_assessment_result` | L142-183 | 42 | 2 | 0 | 10 | ✓ |
| `get_authenticated_user` | L30-36 | 7 | 1 | 0 | 1 | ✓ |
| `answer_tokens_for` | L62-64 | 3 | 1 | 0 | 2 | ✓ |
| `option_tokens_for` | L67-69 | 3 | 1 | 0 | 1 | ✓ |
| `build_answer_display_value` | L79-85 | 7 | 1 | 0 | 3 | ✓ |
| `clean_text` | L88-90 | 3 | 1 | 0 | 1 | ✓ |
| `normalize_options` | L105-107 | 3 | 1 | 0 | 2 | ✓ |

**全部问题 (1)**

- 📏 `upsert_knowledge_assessment_result()` L142: 10 参数数量

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 7
- 认知复杂度: 平均: 3.1, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 11.0 行, 最大: 42 行
- 文件长度: 151 代码量 (184 总计)
- 参数数量: 平均: 2.4, 最大: 10
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 0/5 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/151)
- 命名规范: 无命名违规

### 109. backend\common\grading.py

**糟糕指数: 11.18**

> 行数: 257 总计, 213 代码, 0 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_normalized_score_map` | L112-153 | 42 | 10 | 1 | 3 | ✓ |
| `score_questions` | L156-234 | 79 | 9 | 3 | 3 | ✓ |
| `check_answer` | L77-109 | 33 | 8 | 2 | 3 | ✓ |
| `_normalize_option_values` | L46-64 | 19 | 7 | 2 | 1 | ✓ |
| `extract_answer_value` | L22-34 | 13 | 5 | 2 | 1 | ✓ |
| `_normalize_text_answer` | L37-43 | 7 | 4 | 1 | 1 | ✓ |
| `_normalize_boolean_answer` | L67-74 | 8 | 3 | 1 | 1 | ✓ |
| `calculate_mastery` | L9-19 | 11 | 2 | 1 | 2 | ✓ |
| `grade_exam` | L237-246 | 10 | 1 | 0 | 3 | ✓ |

**全部问题 (7)**

- 🔄 `score_questions()` L156: 认知复杂度: 15
- 📏 `score_questions()` L156: 79 代码量
- 🏗️ `score_questions()` L156: 中等嵌套: 3
- ❌ L30: 未处理的易出错调用
- 🏷️ `_normalize_text_answer()` L37: "_normalize_text_answer" - snake_case
- 🏷️ `_normalize_option_values()` L46: "_normalize_option_values" - snake_case
- 🏷️ `_normalize_boolean_answer()` L67: "_normalize_boolean_answer" - snake_case

**详情**:
- 循环复杂度: 平均: 5.4, 最大: 10
- 认知复杂度: 平均: 8.3, 最大: 15
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 24.7 行, 最大: 79 行
- 文件长度: 213 代码量 (257 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 0.0% (0/213)
- 命名规范: 发现 3 个违规

### 110. backend\tools\activation.py

**糟糕指数: 11.07**

> 行数: 40 总计, 31 代码, 1 注释 | 函数: 1 | 类: 0

**问题**: 🔄 复杂度问题: 2, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_activation_codes` | L11-39 | 29 | 8 | 4 | 3 | ✓ |

**全部问题 (3)**

- 🔄 `generate_activation_codes()` L11: 认知复杂度: 16
- 🔄 `generate_activation_codes()` L11: 嵌套深度: 4
- 🏗️ `generate_activation_codes()` L11: 中等嵌套: 4

**详情**:
- 循环复杂度: 平均: 8.0, 最大: 8
- 认知复杂度: 平均: 16.0, 最大: 16
- 嵌套深度: 平均: 4.0, 最大: 4
- 函数长度: 平均: 29.0 行, 最大: 29 行
- 文件长度: 31 代码量 (40 总计)
- 参数数量: 平均: 3.0, 最大: 3
- 代码重复: 未发现函数
- 结构分析: 1 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 3.2% (1/31)
- 命名规范: 无命名违规

### 111. backend\ai_services\services\llm_service.py

**糟糕指数: 11.03**

> 行数: 483 总计, 418 代码, 6 注释 | 函数: 24 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_detect_provider` | L191-237 | 47 | 11 | 1 | 1 | ✓ |
| `_resolve_extra_body` | L239-257 | 19 | 8 | 2 | 1 | ✓ |
| `_create_llm_client` | L323-360 | 38 | 8 | 1 | 4 | ✓ |
| `resolve_llm_proxy_for_base_url` | L55-63 | 9 | 7 | 1 | 1 | ✓ |
| `_get_llm_for_policy` | L401-441 | 41 | 7 | 1 | 3 | ✓ |
| `__init__` | L83-117 | 35 | 6 | 1 | 3 | ✓ |
| `_get_llm` | L362-399 | 38 | 6 | 3 | 1 | ✓ |
| `_truncate_prompt` | L265-282 | 18 | 5 | 1 | 3 | ✓ |
| `_should_use_agent_service` | L468-478 | 11 | 5 | 1 | 2 | ✓ |
| `_resolve_execution_policy` | L284-316 | 33 | 4 | 1 | 2 | ✓ |
| `_read_runtime_setting` | L47-52 | 6 | 3 | 1 | 1 | ✓ |
| `_provider_from_model_name` | L173-180 | 8 | 3 | 2 | 2 | ✓ |
| `_first_non_empty_setting` | L183-189 | 7 | 3 | 2 | 2 | ✓ |
| `_get_agent_service` | L443-465 | 23 | 3 | 1 | 1 | ✓ |
| `provider_name` | L120-122 | 3 | 2 | 0 | 1 | ✓ |
| `resolved_api_key` | L125-127 | 3 | 2 | 0 | 1 | ✓ |
| `resolved_base_url` | L130-132 | 3 | 2 | 0 | 1 | ✓ |
| `api_format` | L135-137 | 3 | 2 | 0 | 1 | ✓ |
| `resolved_proxy_url` | L145-147 | 3 | 2 | 0 | 1 | ✓ |
| `_read_setting` | L140-142 | 3 | 1 | 0 | 1 | ✓ |
| `resolved_extra_body` | L150-152 | 3 | 1 | 0 | 1 | ✓ |
| `_normalize_provider_name` | L155-170 | 16 | 1 | 0 | 2 | ✓ |
| `_clamp_positive_int` | L260-262 | 3 | 1 | 0 | 2 | ✓ |
| `is_available` | L319-321 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (14)**

- 🔄 `_detect_provider()` L191: 复杂度: 11
- 🔄 `_detect_provider()` L191: 认知复杂度: 13
- 🏗️ `_get_llm()` L362: 中等嵌套: 3
- ❌ L221: 未处理的易出错调用
- 🏷️ `_read_runtime_setting()` L47: "_read_runtime_setting" - snake_case
- 🏷️ `__init__()` L83: "__init__" - snake_case
- 🏷️ `_read_setting()` L140: "_read_setting" - snake_case
- 🏷️ `_normalize_provider_name()` L155: "_normalize_provider_name" - snake_case
- 🏷️ `_provider_from_model_name()` L173: "_provider_from_model_name" - snake_case
- 🏷️ `_first_non_empty_setting()` L183: "_first_non_empty_setting" - snake_case
- 🏷️ `_detect_provider()` L191: "_detect_provider" - snake_case
- 🏷️ `_resolve_extra_body()` L239: "_resolve_extra_body" - snake_case
- 🏷️ `_clamp_positive_int()` L260: "_clamp_positive_int" - snake_case
- 🏷️ `_truncate_prompt()` L265: "_truncate_prompt" - snake_case

**详情**:
- 循环复杂度: 平均: 3.9, 最大: 11
- 认知复杂度: 平均: 5.5, 最大: 13
- 嵌套深度: 平均: 0.8, 最大: 3
- 函数长度: 平均: 15.7 行, 最大: 47 行
- 文件长度: 418 代码量 (483 总计)
- 参数数量: 平均: 1.6, 最大: 4
- 代码重复: 4.2% 重复 (1/24)
- 结构分析: 1 个结构问题
- 错误处理: 1/6 个错误被忽略 (16.7%)
- 注释比例: 1.4% (6/418)
- 命名规范: 发现 16 个违规

### 112. backend\ai_services\test_student_rag_base.py

**糟糕指数: 10.80**

> 行数: 174 总计, 168 代码, 0 注释 | 函数: 1 | 类: 1

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L37-173 | 137 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 📏 `setUp()` L37: 137 代码量
- 🏷️ `setUp()` L37: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 137.0 行, 最大: 137 行
- 文件长度: 168 代码量 (174 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/168)
- 命名规范: 发现 1 个违规

### 113. backend\tools\api_regression_cleanup.py

**糟糕指数: 10.78**

> 行数: 144 总计, 117 代码, 0 注释 | 函数: 7 | 类: 2

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `cleanup_regression_entities` | L38-44 | 7 | 3 | 1 | 1 | ✓ |
| `build_actions_from_templates` | L88-108 | 21 | 3 | 2 | 4 | ✓ |
| `build_cleanup_actions` | L47-52 | 6 | 1 | 0 | 1 | ✓ |
| `teacher_cleanup_actions` | L55-69 | 15 | 1 | 0 | 1 | ✓ |
| `admin_cleanup_actions` | L72-85 | 14 | 1 | 0 | 1 | ✓ |
| `record_cleanup_action` | L111-120 | 10 | 1 | 0 | 2 | ✓ |
| `_cleanup_regression_entities` | L123-143 | 21 | 1 | 0 | 7 | ✓ |

**全部问题 (3)**

- 📏 `_cleanup_regression_entities()` L123: 7 参数数量
- 📋 `teacher_cleanup_actions()` L55: 重复模式: teacher_cleanup_actions, admin_cleanup_actions
- 🏷️ `_cleanup_regression_entities()` L123: "_cleanup_regression_entities" - snake_case

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 3
- 认知复杂度: 平均: 2.4, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 13.4 行, 最大: 21 行
- 文件长度: 117 代码量 (144 总计)
- 参数数量: 平均: 2.4, 最大: 7
- 代码重复: 14.3% 重复 (1/7)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/117)
- 命名规范: 发现 1 个违规

### 114. backend\learning\dashboard_views.py

**糟糕指数: 10.77**

> 行数: 108 总计, 85 代码, 6 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `student_dashboard` | L17-107 | 91 | 10 | 1 | 1 | ✓ |

**全部问题 (1)**

- 📏 `student_dashboard()` L17: 91 代码量

**详情**:
- 循环复杂度: 平均: 10.0, 最大: 10
- 认知复杂度: 平均: 12.0, 最大: 12
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 91.0 行, 最大: 91 行
- 文件长度: 85 代码量 (108 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 7.1% (6/85)
- 命名规范: 无命名违规

### 115. backend\common\neo4j_sync.py

**糟糕指数: 10.73**

> 行数: 221 总计, 202 代码, 0 注释 | 函数: 5 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `sync_knowledge_graph` | L14-110 | 50 | 13 | 1 | 2 | ✓ |
| `_sync_tx` | L52-98 | 47 | 4 | 2 | 1 | ✗ |
| `clear_all` | L112-135 | 24 | 4 | 1 | 1 | ✓ |
| `import_test_data` | L137-204 | 68 | 4 | 2 | 2 | ✓ |
| `get_all_courses` | L206-220 | 15 | 2 | 1 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `sync_knowledge_graph()` L14: 复杂度: 13
- 🔄 `sync_knowledge_graph()` L14: 认知复杂度: 15
- 📏 `import_test_data()` L137: 68 代码量
- 🏷️ `_sync_tx()` L52: "_sync_tx" - snake_case

**详情**:
- 循环复杂度: 平均: 5.4, 最大: 13
- 认知复杂度: 平均: 8.2, 最大: 15
- 嵌套深度: 平均: 1.4, 最大: 2
- 函数长度: 平均: 40.8 行, 最大: 68 行
- 文件长度: 202 代码量 (221 总计)
- 参数数量: 平均: 1.4, 最大: 2
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/13 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/202)
- 命名规范: 发现 1 个违规

### 116. backend\users\test_class_api.py

**糟糕指数: 10.73**

> 行数: 202 总计, 167 代码, 0 注释 | 函数: 10 | 类: 2

**问题**: 📋 重复问题: 2, ❌ 错误处理问题: 7, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L15-35 | 21 | 1 | 0 | 1 | ✓ |
| `test_generate_invitation` | L37-45 | 9 | 1 | 0 | 1 | ✓ |
| `test_student_join_class` | L47-68 | 22 | 1 | 0 | 1 | ✓ |
| `test_cannot_join_class_twice` | L70-88 | 19 | 1 | 0 | 1 | ✓ |
| `test_join_class_returns_published_course_without_default_course` | L90-115 | 26 | 1 | 0 | 1 | ✓ |
| `test_my_classes` | L117-129 | 13 | 1 | 0 | 1 | ✓ |
| `test_leave_class` | L131-146 | 16 | 1 | 0 | 1 | ✓ |
| `setUp` | L152-179 | 28 | 1 | 0 | 1 | ✓ |
| `test_get_class_students` | L181-187 | 7 | 1 | 0 | 1 | ✓ |
| `test_remove_student_from_class` | L189-201 | 13 | 1 | 0 | 1 | ✓ |

**全部问题 (11)**

- 📋 `test_student_join_class()` L47: 重复模式: test_student_join_class, test_cannot_join_class_twice
- 📋 `test_my_classes()` L117: 重复模式: test_my_classes, test_remove_student_from_class
- ❌ L49: 未处理的易出错调用
- ❌ L72: 未处理的易出错调用
- ❌ L78: 未处理的易出错调用
- ❌ L96: 未处理的易出错调用
- ❌ L101: 未处理的易出错调用
- ❌ L119: 未处理的易出错调用
- ❌ L133: 未处理的易出错调用
- 🏷️ `setUp()` L15: "setUp" - snake_case
- 🏷️ `setUp()` L152: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 17.4 行, 最大: 28 行
- 文件长度: 167 代码量 (202 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 20.0% 重复 (2/10)
- 结构分析: 0 个结构问题
- 错误处理: 7/22 个错误被忽略 (31.8%)
- 注释比例: 0.0% (0/167)
- 命名规范: 发现 2 个违规

### 117. backend\learning\path_rules.py

**糟糕指数: 10.69**

> 行数: 121 总计, 96 代码, 0 注释 | 函数: 6 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `topological_mastery_order` | L67-101 | 35 | 12 | 3 | 4 | ✓ |
| `apply_prerequisite_caps` | L36-54 | 19 | 5 | 2 | 3 | ✓ |
| `partition_points_for_path` | L104-120 | 17 | 4 | 2 | 3 | ✓ |
| `is_auto_completable` | L57-64 | 8 | 3 | 1 | 3 | ✗ |
| `build_prerequisite_maps` | L27-33 | 7 | 2 | 1 | 1 | ✗ |
| `load_course_points` | L21-24 | 4 | 1 | 0 | 1 | ✗ |

**全部问题 (4)**

- 🔄 `topological_mastery_order()` L67: 复杂度: 12
- 🔄 `topological_mastery_order()` L67: 认知复杂度: 18
- 🏗️ `topological_mastery_order()` L67: 中等嵌套: 3
- ❌ L93: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 12
- 认知复杂度: 平均: 7.5, 最大: 18
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 15.0 行, 最大: 35 行
- 文件长度: 96 代码量 (121 总计)
- 参数数量: 平均: 2.5, 最大: 4
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 1 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 0.0% (0/96)
- 命名规范: 无命名违规

### 118. backend\courses\teacher_workspace_views.py

**糟糕指数: 10.68**

> 行数: 102 总计, 87 代码, 0 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `class_create` | L33-70 | 38 | 9 | 4 | 1 | ✓ |
| `course_workspace` | L18-28 | 11 | 5 | 1 | 2 | ✓ |
| `my_classes` | L75-101 | 27 | 5 | 1 | 1 | ✓ |

**全部问题 (3)**

- 🔄 `class_create()` L33: 认知复杂度: 17
- 🔄 `class_create()` L33: 嵌套深度: 4
- 🏗️ `class_create()` L33: 中等嵌套: 4

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 9
- 认知复杂度: 平均: 10.3, 最大: 17
- 嵌套深度: 平均: 2.0, 最大: 4
- 函数长度: 平均: 25.3 行, 最大: 38 行
- 文件长度: 87 代码量 (102 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 1 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/87)
- 命名规范: 无命名违规

### 119. backend\assessments\knowledge_generation_support.py

**糟糕指数: 10.67**

> 行数: 133 总计, 112 代码, 0 注释 | 函数: 7 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 7, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `upsert_assessment_feedback_report` | L85-132 | 48 | 10 | 1 | 4 | ✓ |
| `load_assessment_result_snapshot` | L53-66 | 14 | 4 | 1 | 2 | ✓ |
| `resolve_async_generation_context` | L10-21 | 12 | 2 | 1 | 2 | ✓ |
| `build_assessment_mistake_payload` | L38-50 | 13 | 2 | 0 | 1 | ✓ |
| `update_generation_status` | L24-35 | 12 | 1 | 0 | 4 | ✓ |
| `refresh_learning_path_for_assessment` | L69-75 | 7 | 1 | 0 | 2 | ✓ |
| `refresh_learner_profile_for_assessment` | L78-82 | 5 | 1 | 0 | 2 | ✓ |

**全部问题 (7)**

- ❌ L65: 未处理的易出错调用
- ❌ L123: 未处理的易出错调用
- ❌ L124: 未处理的易出错调用
- ❌ L126: 未处理的易出错调用
- ❌ L127: 未处理的易出错调用
- ❌ L128: 未处理的易出错调用
- ❌ L129: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 10
- 认知复杂度: 平均: 3.9, 最大: 12
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 15.9 行, 最大: 48 行
- 文件长度: 112 代码量 (133 总计)
- 参数数量: 平均: 2.4, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 7/11 个错误被忽略 (63.6%)
- 注释比例: 0.0% (0/112)
- 命名规范: 无命名违规

### 120. backend\ai_services\services\scoring_service.py

**糟糕指数: 10.64**

> 行数: 278 总计, 216 代码, 15 注释 | 函数: 7 | 类: 1

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 3, 🏗️ 结构问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `score_objective_question` | L24-80 | 57 | 12 | 2 | 4 | ✓ |
| `score_exam` | L111-183 | 73 | 8 | 3 | 2 | ✓ |
| `calculate_ability_score` | L228-277 | 50 | 8 | 3 | 2 | ✓ |
| `_normalize_list` | L90-98 | 9 | 4 | 1 | 1 | ✓ |
| `update_mastery` | L186-225 | 40 | 4 | 2 | 3 | ✓ |
| `_to_bool` | L101-108 | 8 | 3 | 1 | 1 | ✓ |
| `_normalize_answer` | L83-87 | 5 | 2 | 1 | 1 | ✓ |

**全部问题 (11)**

- 🔄 `score_objective_question()` L24: 复杂度: 12
- 🔄 `score_objective_question()` L24: 认知复杂度: 16
- 🔄 `score_exam()` L111: 认知复杂度: 14
- 🔄 `calculate_ability_score()` L228: 认知复杂度: 14
- 📏 `score_objective_question()` L24: 57 代码量
- 📏 `score_exam()` L111: 73 代码量
- 🏗️ `score_exam()` L111: 中等嵌套: 3
- 🏗️ `calculate_ability_score()` L228: 中等嵌套: 3
- 🏷️ `_normalize_answer()` L83: "_normalize_answer" - snake_case
- 🏷️ `_normalize_list()` L90: "_normalize_list" - snake_case
- 🏷️ `_to_bool()` L101: "_to_bool" - snake_case

**详情**:
- 循环复杂度: 平均: 5.9, 最大: 12
- 认知复杂度: 平均: 9.6, 最大: 16
- 嵌套深度: 平均: 1.9, 最大: 3
- 函数长度: 平均: 34.6 行, 最大: 73 行
- 文件长度: 216 代码量 (278 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 2 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 6.9% (15/216)
- 命名规范: 发现 3 个违规

### 121. backend\users\student_profile_support.py

**糟糕指数: 10.38**

> 行数: 279 总计, 235 代码, 0 注释 | 函数: 17 | 类: 1

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 7, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_profile_summary_payload` | L169-181 | 13 | 11 | 1 | 2 | ✓ |
| `build_student_profile_payload` | L26-46 | 21 | 5 | 1 | 2 | ✓ |
| `build_ability_scores` | L65-75 | 11 | 5 | 1 | 2 | ✓ |
| `ability_tags` | L109-136 | 28 | 5 | 1 | 1 | ✓ |
| `build_knowledge_mastery_payload` | L49-62 | 14 | 4 | 1 | 2 | ✓ |
| `habit_resource_tags` | L139-147 | 9 | 4 | 1 | 1 | ✓ |
| `habit_time_and_pace_tags` | L150-166 | 17 | 4 | 1 | 1 | ✓ |
| `build_habit_preferences` | L78-93 | 16 | 3 | 1 | 1 | ✓ |
| `parse_profile_history_limit` | L202-207 | 6 | 3 | 1 | 1 | ✓ |
| `snapshot_profile_summary` | L228-237 | 10 | 3 | 1 | 1 | ✓ |
| `build_learner_tags` | L96-106 | 11 | 2 | 1 | 2 | ✓ |
| `build_profile_refresh_payload` | L184-199 | 16 | 2 | 1 | 2 | ✓ |
| `build_export_mastery_list` | L257-266 | 10 | 2 | 0 | 1 | ✓ |
| `build_export_ability_scores` | L269-272 | 4 | 2 | 0 | 1 | ✓ |
| `build_export_habit_preferences` | L275-278 | 4 | 2 | 0 | 1 | ✓ |
| `build_profile_history_payload` | L210-225 | 16 | 1 | 0 | 3 | ✓ |
| `build_profile_export_response` | L240-254 | 15 | 1 | 0 | 1 | ✓ |

**全部问题 (9)**

- 🔄 `build_profile_summary_payload()` L169: 复杂度: 11
- 🔄 `build_profile_summary_payload()` L169: 认知复杂度: 13
- ❌ L164: 未处理的易出错调用
- ❌ L190: 未处理的易出错调用
- ❌ L193: 未处理的易出错调用
- ❌ L194: 未处理的易出错调用
- ❌ L195: 未处理的易出错调用
- ❌ L196: 未处理的易出错调用
- ❌ L197: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 11
- 认知复杂度: 平均: 4.9, 最大: 13
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 13.0 行, 最大: 28 行
- 文件长度: 235 代码量 (279 总计)
- 参数数量: 平均: 1.5, 最大: 3
- 代码重复: 0.0% 重复 (0/17)
- 结构分析: 0 个结构问题
- 错误处理: 7/9 个错误被忽略 (77.8%)
- 注释比例: 0.0% (0/235)
- 命名规范: 无命名违规

### 122. backend\learning\stage_test_results.py

**糟糕指数: 10.24**

> 行数: 115 总计, 105 代码, 0 注释 | 函数: 3 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `persist_stage_progress` | L17-54 | 38 | 3 | 1 | 9 | ✓ |
| `stage_response_payload` | L57-83 | 27 | 1 | 0 | 5 | ✓ |
| `_stored_stage_result` | L86-114 | 29 | 1 | 0 | 6 | ✓ |

**全部问题 (3)**

- 📏 `persist_stage_progress()` L17: 9 参数数量
- 📏 `_stored_stage_result()` L86: 6 参数数量
- 🏷️ `_stored_stage_result()` L86: "_stored_stage_result" - snake_case

**详情**:
- 循环复杂度: 平均: 1.7, 最大: 3
- 认知复杂度: 平均: 2.3, 最大: 5
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 31.3 行, 最大: 38 行
- 文件长度: 105 代码量 (115 总计)
- 参数数量: 平均: 6.7, 最大: 9
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/105)
- 命名规范: 发现 1 个违规

### 123. backend\tools\mefkt_training_support.py

**糟糕指数: 10.24**

> 行数: 375 总计, 341 代码, 0 注释 | 函数: 10 | 类: 3

**问题**: ⚠️ 其他问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `train_sequence_predictor` | L224-262 | 39 | 4 | 2 | 4 | ✓ |
| `pretrain_mefkt_embedding` | L144-177 | 34 | 3 | 1 | 3 | ✓ |
| `run_sequence_epoch` | L265-299 | 35 | 3 | 2 | 5 | ✓ |
| `write_mefkt_metadata` | L71-74 | 4 | 1 | 0 | 2 | ✓ |
| `train_mefkt_bundle` | L77-112 | 36 | 1 | 0 | 4 | ✓ |
| `build_mefkt_components` | L115-141 | 27 | 1 | 0 | 2 | ✓ |
| `run_pretrain_epoch` | L180-221 | 42 | 1 | 0 | 9 | ✓ |
| `cpu_state_dict` | L302-304 | 3 | 1 | 0 | 1 | ✓ |
| `build_mefkt_metadata` | L307-352 | 46 | 1 | 0 | 6 | ✓ |
| `save_mefkt_checkpoint` | L355-374 | 20 | 1 | 0 | 5 | ✓ |

**全部问题 (2)**

- 📏 `run_pretrain_epoch()` L180: 9 参数数量
- 📏 `build_mefkt_metadata()` L307: 6 参数数量

**详情**:
- 循环复杂度: 平均: 1.7, 最大: 4
- 认知复杂度: 平均: 2.7, 最大: 8
- 嵌套深度: 平均: 0.5, 最大: 2
- 函数长度: 平均: 28.6 行, 最大: 46 行
- 文件长度: 341 代码量 (375 总计)
- 参数数量: 平均: 4.1, 最大: 9
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/341)
- 命名规范: 无命名违规

### 124. backend\tools\db_demo_preset_assessment.py

**糟糕指数: 10.14**

> 行数: 246 总计, 215 代码, 0 注释 | 函数: 8 | 类: 1

**问题**: ⚠️ 其他问题: 3, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `persist_student1_question_answer` | L96-148 | 53 | 5 | 0 | 4 | ✓ |
| `build_student1_assessment_attempt` | L41-93 | 53 | 4 | 1 | 6 | ✓ |
| `update_student1_point_stats` | L151-161 | 11 | 3 | 2 | 3 | ✓ |
| `calculate_initial_mastery_baseline` | L26-38 | 13 | 2 | 1 | 4 | ✓ |
| `build_student1_mastery_map` | L164-183 | 20 | 2 | 1 | 5 | ✓ |
| `persist_student1_mastery` | L215-236 | 22 | 2 | 1 | 5 | ✓ |
| `persist_student1_assessment_result` | L186-212 | 27 | 1 | 0 | 4 | ✓ |
| `weakest_point_names` | L239-245 | 7 | 1 | 0 | 1 | ✓ |

**全部问题 (5)**

- 📏 `build_student1_assessment_attempt()` L41: 53 代码量
- 📏 `persist_student1_question_answer()` L96: 53 代码量
- 📏 `build_student1_assessment_attempt()` L41: 6 参数数量
- ❌ L140: 未处理的易出错调用
- ❌ L233: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 5
- 认知复杂度: 平均: 4.0, 最大: 7
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 25.8 行, 最大: 53 行
- 文件长度: 215 代码量 (246 总计)
- 参数数量: 平均: 4.0, 最大: 6
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 2/2 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/215)
- 命名规范: 无命名违规

### 125. backend\platform_ai\rag\student_answer_support.py

**糟糕指数: 10.00**

> 行数: 458 总计, 386 代码, 0 注释 | 函数: 22 | 类: 5

**问题**: ⚠️ 其他问题: 4, ❌ 错误处理问题: 6, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_point_name_map` | L88-98 | 11 | 5 | 2 | 1 | ✓ |
| `_entity_knowledge_point_id` | L101-110 | 10 | 4 | 1 | 1 | ✓ |
| `build_graph_fallback_answer` | L261-277 | 17 | 4 | 0 | 2 | ✓ |
| `build_course_graph_focus` | L113-126 | 14 | 3 | 0 | 2 | ✓ |
| `build_course_fallback_answer` | L280-299 | 20 | 3 | 0 | 2 | ✓ |
| `build_graph_answer_prompt` | L302-334 | 33 | 3 | 0 | 3 | ✓ |
| `resolve_course_answer_candidates` | L198-216 | 19 | 2 | 1 | 4 | ✓ |
| `query_graph_bundle` | L238-258 | 21 | 2 | 1 | 6 | ✓ |
| `build_course_answer_prompt` | L337-372 | 36 | 2 | 0 | 3 | ✓ |
| `call_llm_answer` | L375-391 | 17 | 2 | 1 | 4 | ✓ |
| `graph_answer_without_llm` | L394-401 | 8 | 2 | 0 | 1 | ✓ |
| `graph_answer_with_llm` | L419-431 | 13 | 2 | 0 | 2 | ✓ |
| `call_with_fallback` | L33-40 | 8 | 1 | 0 | 4 | ✓ |
| `query_graph` | L46-55 | 10 | 1 | 0 | 6 | ✓ |
| `combine_answer_context` | L129-141 | 13 | 1 | 0 | 2 | ✓ |
| `build_graph_answer_evidence` | L144-162 | 19 | 1 | 0 | 4 | ✓ |
| `build_course_answer_evidence` | L165-195 | 31 | 1 | 0 | 6 | ✓ |
| `_append_missing_point_names` | L219-230 | 12 | 1 | 0 | 3 | ✓ |
| `extract_source_titles` | L233-235 | 3 | 1 | 0 | 2 | ✓ |
| `course_answer_without_llm` | L404-416 | 13 | 1 | 0 | 2 | ✓ |
| `course_answer_with_llm` | L434-448 | 15 | 1 | 0 | 3 | ✓ |
| `normalize_answer_sources` | L451-457 | 7 | 1 | 0 | 3 | ✓ |

**全部问题 (9)**

- 📏 `query_graph()` L46: 6 参数数量
- 📏 `build_course_answer_evidence()` L165: 6 参数数量
- 📏 `query_graph_bundle()` L238: 6 参数数量
- ❌ L137: 未处理的易出错调用
- ❌ L138: 未处理的易出错调用
- ❌ L426: 未处理的易出错调用
- ❌ L430: 未处理的易出错调用
- ❌ L442: 未处理的易出错调用
- ❌ L446: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 5
- 认知复杂度: 平均: 2.5, 最大: 9
- 嵌套深度: 平均: 0.3, 最大: 2
- 函数长度: 平均: 15.9 行, 最大: 36 行
- 文件长度: 386 代码量 (458 总计)
- 参数数量: 平均: 3.0, 最大: 6
- 代码重复: 0.0% 重复 (0/22)
- 结构分析: 0 个结构问题
- 错误处理: 6/14 个错误被忽略 (42.9%)
- 注释比例: 0.0% (0/386)
- 命名规范: 发现 2 个违规

### 126. backend\courses\teacher_class_views.py

**糟糕指数: 9.98**

> 行数: 181 总计, 158 代码, 0 注释 | 函数: 8 | 类: 0

**问题**: 🔄 复杂度问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `class_update` | L55-85 | 31 | 11 | 2 | 2 | ✓ |
| `class_publish_course` | L101-122 | 22 | 9 | 1 | 2 | ✓ |
| `class_create` | L17-36 | 20 | 6 | 4 | 1 | ✓ |
| `teacher_class_progress` | L162-180 | 19 | 6 | 1 | 2 | ✓ |
| `class_unpublish_course` | L127-141 | 15 | 5 | 1 | 3 | ✓ |
| `class_delete` | L41-50 | 10 | 4 | 1 | 2 | ✓ |
| `class_courses` | L146-157 | 12 | 3 | 1 | 2 | ✓ |
| `my_classes` | L90-96 | 7 | 2 | 1 | 1 | ✓ |

**全部问题 (6)**

- 🔄 `class_update()` L55: 复杂度: 11
- 🔄 `class_create()` L17: 认知复杂度: 14
- 🔄 `class_update()` L55: 认知复杂度: 15
- 🔄 `class_create()` L17: 嵌套深度: 4
- 🏗️ `class_create()` L17: 中等嵌套: 4
- ❌ L49: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.8, 最大: 11
- 认知复杂度: 平均: 8.8, 最大: 15
- 嵌套深度: 平均: 1.5, 最大: 4
- 函数长度: 平均: 17.0 行, 最大: 31 行
- 文件长度: 158 代码量 (181 总计)
- 参数数量: 平均: 1.9, 最大: 3
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 1/15 个错误被忽略 (6.7%)
- 注释比例: 0.0% (0/158)
- 命名规范: 无命名违规

### 127. frontend\src\views\student\useLearningPath.js

**糟糕指数: 9.86**

> 行数: 313 总计, 287 代码, 0 注释 | 函数: 11 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `loadLearningPath` | L76-134 | 55 | 8 | 2 | 0 | ✗ |
| `refreshPath` | L241-267 | 27 | 7 | 1 | 0 | ✗ |
| `handleCompleteNode` | L160-189 | 30 | 5 | 1 | 1 | ✗ |
| `handleSkipNode` | L215-235 | 21 | 4 | 1 | 1 | ✗ |
| `startLearning` | L141-158 | 18 | 3 | 1 | 1 | ✗ |
| `resolveLiveNode` | L136-139 | 3 | 2 | 1 | 1 | ✗ |
| `reviewNode` | L191-201 | 11 | 2 | 1 | 1 | ✗ |
| `viewTestReport` | L203-213 | 11 | 2 | 1 | 1 | ✗ |
| `useLearningPath` | L21-312 | 72 | 1 | 0 | 0 | ✗ |
| `selectNode` | L58-74 | 3 | 1 | 0 | 1 | ✗ |
| `goToAssessment` | L237-239 | 3 | 1 | 0 | 0 | ✗ |

**全部问题 (1)**

- 📋 `startLearning()` L141: 重复模式: startLearning, reviewNode, viewTestReport

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 8
- 认知复杂度: 平均: 4.9, 最大: 12
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 23.1 行, 最大: 72 行
- 文件长度: 287 代码量 (313 总计)
- 参数数量: 平均: 0.6, 最大: 1
- 代码重复: 18.2% 重复 (2/11)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/287)
- 命名规范: 无命名违规

### 128. backend\ai_services\test_student_ai_multicourse.py

**糟糕指数: 9.80**

> 行数: 358 总计, 316 代码, 0 注释 | 函数: 14 | 类: 4

**问题**: ⚠️ 其他问题: 3, 📋 重复问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `post` | L231-256 | 26 | 2 | 1 | 5 | ✓ |
| `setUp` | L37-74 | 38 | 1 | 0 | 1 | ✓ |
| `test_graph_rag_search_should_only_return_points_from_selected_course` | L76-87 | 12 | 1 | 0 | 1 | ✓ |
| `test_graph_rag_search_should_surface_runtime_supporting_sources` | L90-110 | 21 | 1 | 0 | 2 | ✓ |
| `test_graph_rag_search_should_match_point_names_inside_full_sentence` | L112-122 | 11 | 1 | 0 | 1 | ✓ |
| `test_graph_rag_ask_should_route_structure_question_without_point` | L125-155 | 31 | 1 | 0 | 2 | ✓ |
| `test_graph_rag_ask_endpoint_should_surface_runtime_modes` | L158-192 | 35 | 1 | 0 | 2 | ✓ |
| `test_ai_resource_reason_should_reject_cross_course_resource_requests` | L194-207 | 14 | 1 | 0 | 1 | ✓ |
| `__init__` | L213-214 | 2 | 1 | 0 | 2 | ✗ |
| `raise_for_status` | L216-217 | 2 | 1 | 0 | 1 | ✓ |
| `json` | L219-222 | 4 | 1 | 0 | 1 | ✓ |
| `__init__` | L228-229 | 2 | 1 | 0 | 1 | ✗ |
| `test_external_resource_mcp_should_search_exa_and_enrich_with_firecrawl` | L276-298 | 23 | 1 | 0 | 1 | ✓ |
| `test_node_resource_recommendation_should_prefer_mcp_external_results` | L303-357 | 55 | 1 | 0 | 4 | ✓ |

**全部问题 (9)**

- 📏 `test_node_resource_recommendation_should_prefer_mcp_external_results()` L303: 55 代码量
- 📋 `test_graph_rag_search_should_only_return_points_from_selected_course()` L76: 重复模式: test_graph_rag_search_should_only_return_points_from_selected_course, test_graph_rag_search_should_surface_runtime_supporting_sources
- 📋 `test_graph_rag_search_should_match_point_names_inside_full_sentence()` L112: 重复模式: test_graph_rag_search_should_match_point_names_inside_full_sentence, test_graph_rag_ask_should_route_structure_question_without_point
- ❌ L231: 未处理的易出错调用
- 🏷️ `setUp()` L37: "setUp" - snake_case
- 🏷️ `__init__()` L213: "__init__" - snake_case
- 🏷️ `__init__()` L228: "__init__" - snake_case
- 🏷️ L210: "_MCPStubResponse" - PascalCase
- 🏷️ L225: "_MCPStubSession" - PascalCase

**详情**:
- 循环复杂度: 平均: 1.1, 最大: 2
- 认知复杂度: 平均: 1.2, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 19.7 行, 最大: 55 行
- 文件长度: 316 代码量 (358 总计)
- 参数数量: 平均: 1.8, 最大: 5
- 代码重复: 14.3% 重复 (2/14)
- 结构分析: 0 个结构问题
- 错误处理: 1/8 个错误被忽略 (12.5%)
- 注释比例: 0.0% (0/316)
- 命名规范: 发现 5 个违规

### 129. backend\learning\stage_test_feedback.py

**糟糕指数: 9.78**

> 行数: 87 总计, 74 代码, 0 注释 | 函数: 3 | 类: 0

**问题**: ❌ 错误处理问题: 11, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_normalize_feedback_report` | L44-68 | 25 | 9 | 1 | 1 | ✓ |
| `build_feedback_report` | L16-41 | 26 | 2 | 1 | 3 | ✓ |
| `fallback_feedback_report` | L71-86 | 16 | 1 | 0 | 1 | ✓ |

**全部问题 (12)**

- ❌ L47: 未处理的易出错调用
- ❌ L51: 未处理的易出错调用
- ❌ L52: 未处理的易出错调用
- ❌ L54: 未处理的易出错调用
- ❌ L55: 未处理的易出错调用
- ❌ L57: 未处理的易出错调用
- ❌ L58: 未处理的易出错调用
- ❌ L60: 未处理的易出错调用
- ❌ L61: 未处理的易出错调用
- ❌ L63: 未处理的易出错调用
- ❌ L64: 未处理的易出错调用
- 🏷️ `_normalize_feedback_report()` L44: "_normalize_feedback_report" - snake_case

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 9
- 认知复杂度: 平均: 5.3, 最大: 11
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 22.3 行, 最大: 26 行
- 文件长度: 74 代码量 (87 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 11/13 个错误被忽略 (84.6%)
- 注释比例: 0.0% (0/74)
- 命名规范: 发现 1 个违规

### 130. backend\common\neo4j_base.py

**糟糕指数: 9.72**

> 行数: 157 总计, 123 代码, 0 注释 | 函数: 11 | 类: 4

**问题**: 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_check_connection` | L76-104 | 29 | 6 | 3 | 1 | ✓ |
| `reset_connection_state` | L48-57 | 10 | 3 | 2 | 1 | ✓ |
| `_get_driver` | L120-134 | 15 | 3 | 1 | 1 | ✓ |
| `_warn_fallback` | L59-67 | 9 | 2 | 1 | 2 | ✓ |
| `is_available` | L70-74 | 5 | 2 | 1 | 1 | ✓ |
| `_ensure_available` | L106-111 | 6 | 2 | 1 | 1 | ✓ |
| `close` | L151-156 | 6 | 2 | 1 | 1 | ✓ |
| `__init__` | L43-46 | 4 | 1 | 0 | 1 | ✓ |
| `_build_query` | L114-118 | 5 | 1 | 0 | 1 | ✓ |
| `get_driver` | L136-138 | 3 | 1 | 0 | 1 | ✓ |
| `_resolve_point_course_id` | L141-149 | 9 | 1 | 0 | 1 | ✓ |

**全部问题 (12)**

- 🏗️ `_check_connection()` L76: 中等嵌套: 3
- ❌ L53: 未处理的易出错调用
- ❌ L100: 未处理的易出错调用
- ❌ L151: 未处理的易出错调用
- ❌ L155: 未处理的易出错调用
- 🏷️ `__init__()` L43: "__init__" - snake_case
- 🏷️ `_warn_fallback()` L59: "_warn_fallback" - snake_case
- 🏷️ `_check_connection()` L76: "_check_connection" - snake_case
- 🏷️ `_ensure_available()` L106: "_ensure_available" - snake_case
- 🏷️ `_build_query()` L114: "_build_query" - snake_case
- 🏷️ `_get_driver()` L120: "_get_driver" - snake_case
- 🏷️ `_resolve_point_course_id()` L141: "_resolve_point_course_id" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 6
- 认知复杂度: 平均: 4.0, 最大: 12
- 嵌套深度: 平均: 0.9, 最大: 3
- 函数长度: 平均: 9.2 行, 最大: 29 行
- 文件长度: 123 代码量 (157 总计)
- 参数数量: 平均: 1.1, 最大: 2
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 1 个结构问题
- 错误处理: 4/4 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/123)
- 命名规范: 发现 7 个违规

### 131. backend\ai_services\services\mefkt_runtime.py

**糟糕指数: 9.68**

> 行数: 184 总计, 152 代码, 2 注释 | 函数: 10 | 类: 1

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_sorted_history_records` | L71-79 | 9 | 5 | 1 | 1 | ✓ |
| `_append_history_outcome` | L82-96 | 15 | 5 | 1 | 5 | ✓ |
| `_parse_timestamp` | L58-68 | 11 | 4 | 1 | 1 | ✓ |
| `_normalize_values` | L114-122 | 9 | 3 | 1 | 2 | ✓ |
| `_coerce_float` | L42-47 | 6 | 2 | 1 | 2 | ✓ |
| `_coerce_int` | L50-55 | 6 | 2 | 1 | 2 | ✓ |
| `_difficulty_to_score` | L130-136 | 7 | 2 | 0 | 1 | ✓ |
| `build_course_runtime_bundle` | L139-183 | 45 | 2 | 1 | 1 | ✓ |
| `_move_bundle_tensors_to_device` | L99-111 | 13 | 1 | 0 | 2 | ✓ |
| `_clamp` | L125-127 | 3 | 1 | 0 | 3 | ✓ |

**全部问题 (11)**

- ❌ L75: 未处理的易出错调用
- ❌ L136: 未处理的易出错调用
- 🏷️ `_coerce_float()` L42: "_coerce_float" - snake_case
- 🏷️ `_coerce_int()` L50: "_coerce_int" - snake_case
- 🏷️ `_parse_timestamp()` L58: "_parse_timestamp" - snake_case
- 🏷️ `_build_sorted_history_records()` L71: "_build_sorted_history_records" - snake_case
- 🏷️ `_append_history_outcome()` L82: "_append_history_outcome" - snake_case
- 🏷️ `_move_bundle_tensors_to_device()` L99: "_move_bundle_tensors_to_device" - snake_case
- 🏷️ `_normalize_values()` L114: "_normalize_values" - snake_case
- 🏷️ `_clamp()` L125: "_clamp" - snake_case
- 🏷️ `_difficulty_to_score()` L130: "_difficulty_to_score" - snake_case

**详情**:
- 循环复杂度: 平均: 2.7, 最大: 5
- 认知复杂度: 平均: 4.1, 最大: 7
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 12.4 行, 最大: 45 行
- 文件长度: 152 代码量 (184 总计)
- 参数数量: 平均: 2.0, 最大: 5
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 2/3 个错误被忽略 (66.7%)
- 注释比例: 1.3% (2/152)
- 命名规范: 发现 9 个违规

### 132. backend\tools\api_regression_admin_support.py

**糟糕指数: 9.63**

> 行数: 335 总计, 317 代码, 0 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 5, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `run_admin_activation_flow` | L176-201 | 26 | 7 | 1 | 3 | ✓ |
| `run_admin_class_flow` | L252-334 | 83 | 6 | 1 | 6 | ✓ |
| `run_admin_user_flow` | L91-173 | 83 | 5 | 1 | 4 | ✓ |
| `run_admin_course_flow` | L204-249 | 46 | 5 | 1 | 4 | ✓ |
| `run_admin_read_checks` | L11-88 | 78 | 1 | 0 | 3 | ✓ |

**全部问题 (4)**

- 📏 `run_admin_read_checks()` L11: 78 代码量
- 📏 `run_admin_user_flow()` L91: 83 代码量
- 📏 `run_admin_class_flow()` L252: 83 代码量
- 📏 `run_admin_class_flow()` L252: 6 参数数量

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 7
- 认知复杂度: 平均: 6.4, 最大: 9
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 63.2 行, 最大: 83 行
- 文件长度: 317 代码量 (335 总计)
- 参数数量: 平均: 4.0, 最大: 6
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/5 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/317)
- 命名规范: 无命名违规

### 133. backend\models\DKT\KnowledgeTracing\data\dataloader.py

**糟糕指数: 9.63**

> 行数: 66 总计, 49 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 📋 重复问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_loader` | L39-50 | 12 | 2 | 1 | 1 | ✓ |
| `__getattr__` | L60-65 | 6 | 2 | 1 | 1 | ✓ |
| `get_train_loader` | L23-28 | 6 | 1 | 0 | 1 | ✓ |
| `get_test_loader` | L31-36 | 6 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 📋 `get_train_loader()` L23: 重复模式: get_train_loader, get_test_loader
- 🏷️ `__getattr__()` L60: "__getattr__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 2
- 认知复杂度: 平均: 2.5, 最大: 4
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 7.5 行, 最大: 12 行
- 文件长度: 49 代码量 (66 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 25.0% 重复 (1/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/49)
- 命名规范: 发现 1 个违规

### 134. backend\learning\stage_test_selection.py

**糟糕指数: 9.53**

> 行数: 262 总计, 222 代码, 0 注释 | 函数: 16 | 类: 0

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_stage_knowledge_point_ids` | L40-63 | 24 | 4 | 1 | 1 | ✓ |
| `_pick_stage_questions_with_llm` | L145-167 | 23 | 4 | 2 | 3 | ✓ |
| `_serialize_stage_options` | L252-261 | 10 | 4 | 0 | 1 | ✓ |
| `_questions_from_bank` | L104-120 | 17 | 3 | 1 | 3 | ✓ |
| `_stage_test_result` | L194-199 | 6 | 3 | 1 | 1 | ✓ |
| `build_stage_test_payload` | L19-37 | 19 | 2 | 1 | 2 | ✓ |
| `_select_stage_questions` | L66-75 | 10 | 2 | 1 | 3 | ✓ |
| `_resolve_stage_exam` | L78-91 | 14 | 2 | 1 | 2 | ✓ |
| `_knowledge_point_names` | L183-191 | 9 | 2 | 0 | 1 | ✓ |
| `_serialize_stage_question` | L230-249 | 20 | 2 | 1 | 3 | ✓ |
| `_questions_from_exam` | L94-101 | 8 | 1 | 0 | 1 | ✓ |
| `_candidate_questions` | L123-133 | 11 | 1 | 0 | 2 | ✓ |
| `_course_questions` | L136-142 | 7 | 1 | 0 | 1 | ✓ |
| `_candidate_info` | L170-180 | 11 | 1 | 0 | 1 | ✓ |
| `_empty_stage_test_payload` | L202-211 | 10 | 1 | 0 | 2 | ✓ |
| `_serialize_stage_questions` | L214-227 | 14 | 1 | 0 | 2 | ✓ |

**全部问题 (15)**

- 📋 `build_stage_test_payload()` L19: 重复模式: build_stage_test_payload, _questions_from_bank
- ❌ L241: 未处理的易出错调用
- ❌ L256: 未处理的易出错调用
- ❌ L257: 未处理的易出错调用
- ❌ L258: 未处理的易出错调用
- 🏷️ `_stage_knowledge_point_ids()` L40: "_stage_knowledge_point_ids" - snake_case
- 🏷️ `_select_stage_questions()` L66: "_select_stage_questions" - snake_case
- 🏷️ `_resolve_stage_exam()` L78: "_resolve_stage_exam" - snake_case
- 🏷️ `_questions_from_exam()` L94: "_questions_from_exam" - snake_case
- 🏷️ `_questions_from_bank()` L104: "_questions_from_bank" - snake_case
- 🏷️ `_candidate_questions()` L123: "_candidate_questions" - snake_case
- 🏷️ `_course_questions()` L136: "_course_questions" - snake_case
- 🏷️ `_pick_stage_questions_with_llm()` L145: "_pick_stage_questions_with_llm" - snake_case
- 🏷️ `_candidate_info()` L170: "_candidate_info" - snake_case
- 🏷️ `_knowledge_point_names()` L183: "_knowledge_point_names" - snake_case

**详情**:
- 循环复杂度: 平均: 2.1, 最大: 4
- 认知复杂度: 平均: 3.3, 最大: 8
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 13.3 行, 最大: 24 行
- 文件长度: 222 代码量 (262 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 6.3% 重复 (1/16)
- 结构分析: 0 个结构问题
- 错误处理: 4/5 个错误被忽略 (80.0%)
- 注释比例: 0.0% (0/222)
- 命名规范: 发现 15 个违规

### 135. backend\common\defense_demo_content.py

**糟糕指数: 9.51**

> 行数: 332 总计, 313 代码, 0 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_ensure_demo_resources` | L69-162 | 94 | 6 | 2 | 3 | ✓ |
| `_ensure_demo_stage_test` | L165-259 | 95 | 5 | 1 | 3 | ✓ |
| `_ensure_demo_points` | L14-66 | 53 | 3 | 1 | 1 | ✓ |
| `_build_point_intro_payloads` | L262-297 | 36 | 2 | 1 | 1 | ✓ |
| `_build_ai_demo_query_payloads` | L300-331 | 32 | 1 | 0 | 1 | ✓ |

**全部问题 (8)**

- 📏 `_ensure_demo_points()` L14: 53 代码量
- 📏 `_ensure_demo_resources()` L69: 94 代码量
- 📏 `_ensure_demo_stage_test()` L165: 95 代码量
- 🏷️ `_ensure_demo_points()` L14: "_ensure_demo_points" - snake_case
- 🏷️ `_ensure_demo_resources()` L69: "_ensure_demo_resources" - snake_case
- 🏷️ `_ensure_demo_stage_test()` L165: "_ensure_demo_stage_test" - snake_case
- 🏷️ `_build_point_intro_payloads()` L262: "_build_point_intro_payloads" - snake_case
- 🏷️ `_build_ai_demo_query_payloads()` L300: "_build_ai_demo_query_payloads" - snake_case

**详情**:
- 循环复杂度: 平均: 3.4, 最大: 6
- 认知复杂度: 平均: 5.4, 最大: 10
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 62.0 行, 最大: 95 行
- 文件长度: 313 代码量 (332 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/313)
- 命名规范: 发现 5 个违规

### 136. backend\logs\descriptions.py

**糟糕指数: 9.44**

> 行数: 104 总计, 83 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_operation_description` | L57-92 | 36 | 12 | 1 | 3 | ✓ |
| `_match_fixed_description` | L95-100 | 6 | 3 | 2 | 2 | ✓ |
| `_contains_with_method` | L20-22 | 3 | 2 | 0 | 2 | ✓ |
| `_contains` | L15-17 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (5)**

- 🔄 `generate_operation_description()` L57: 复杂度: 12
- 🔄 `generate_operation_description()` L57: 认知复杂度: 14
- 🏷️ `_contains()` L15: "_contains" - snake_case
- 🏷️ `_contains_with_method()` L20: "_contains_with_method" - snake_case
- 🏷️ `_match_fixed_description()` L95: "_match_fixed_description" - snake_case

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 12
- 认知复杂度: 平均: 6.0, 最大: 14
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 12.0 行, 最大: 36 行
- 文件长度: 83 代码量 (104 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/83)
- 命名规范: 发现 3 个违规

### 137. backend\platform_ai\rag\student_index_mixin.py

**糟糕指数: 9.32**

> 行数: 121 总计, 103 代码, 0 注释 | 函数: 10 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_index` | L16-40 | 25 | 6 | 2 | 4 | ✓ |
| `_entity_to_communities` | L106-120 | 15 | 6 | 3 | 2 | ✓ |
| `_ensure_index` | L42-51 | 10 | 4 | 2 | 3 | ✓ |
| `_entity_map` | L88-95 | 8 | 3 | 2 | 2 | ✓ |
| `_community_lookup` | L97-104 | 8 | 3 | 2 | 2 | ✓ |
| `_entity_list` | L53-58 | 6 | 2 | 1 | 2 | ✓ |
| `_relationship_list` | L60-65 | 6 | 2 | 1 | 2 | ✓ |
| `_document_list` | L67-72 | 6 | 2 | 1 | 2 | ✓ |
| `_community_list` | L74-79 | 6 | 2 | 1 | 2 | ✓ |
| `_community_report_list` | L81-86 | 6 | 2 | 1 | 2 | ✓ |

**全部问题 (11)**

- 📋 `_entity_map()` L88: 重复模式: _entity_map, _community_lookup
- 🏗️ `_entity_to_communities()` L106: 中等嵌套: 3
- 🏷️ `_ensure_index()` L42: "_ensure_index" - snake_case
- 🏷️ `_entity_list()` L53: "_entity_list" - snake_case
- 🏷️ `_relationship_list()` L60: "_relationship_list" - snake_case
- 🏷️ `_document_list()` L67: "_document_list" - snake_case
- 🏷️ `_community_list()` L74: "_community_list" - snake_case
- 🏷️ `_community_report_list()` L81: "_community_report_list" - snake_case
- 🏷️ `_entity_map()` L88: "_entity_map" - snake_case
- 🏷️ `_community_lookup()` L97: "_community_lookup" - snake_case
- 🏷️ `_entity_to_communities()` L106: "_entity_to_communities" - snake_case

**详情**:
- 循环复杂度: 平均: 3.2, 最大: 6
- 认知复杂度: 平均: 6.4, 最大: 12
- 嵌套深度: 平均: 1.6, 最大: 3
- 函数长度: 平均: 9.6 行, 最大: 25 行
- 文件长度: 103 代码量 (121 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 10.0% 重复 (1/10)
- 结构分析: 1 个结构问题
- 错误处理: 0/11 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/103)
- 命名规范: 发现 9 个违规

### 138. backend\users\teacher_profile_support.py

**糟糕指数: 9.24**

> 行数: 167 总计, 137 代码, 0 注释 | 函数: 11 | 类: 0

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `resolve_profile_course_id` | L21-39 | 19 | 4 | 1 | 2 | ✓ |
| `ensure_teacher_can_view_student` | L42-54 | 13 | 3 | 1 | 3 | ✓ |
| `_build_ability_scores` | L90-95 | 6 | 3 | 1 | 2 | ✓ |
| `_average_history_mastery` | L130-134 | 5 | 3 | 1 | 1 | ✓ |
| `resolve_student_for_teacher_profile` | L13-18 | 6 | 2 | 1 | 1 | ✓ |
| `_build_habit_preferences` | L98-110 | 13 | 2 | 1 | 1 | ✓ |
| `_build_answer_stats` | L137-148 | 12 | 2 | 0 | 2 | ✓ |
| `build_profile_refresh_payload` | L151-166 | 16 | 2 | 1 | 2 | ✓ |
| `build_student_profile_payload` | L57-70 | 14 | 1 | 0 | 2 | ✓ |
| `_build_mastery_list` | L73-87 | 15 | 1 | 0 | 2 | ✓ |
| `_build_profile_history` | L113-127 | 15 | 1 | 0 | 2 | ✓ |

**全部问题 (11)**

- 📋 `_build_mastery_list()` L73: 重复模式: _build_mastery_list, _build_profile_history
- ❌ L157: 未处理的易出错调用
- ❌ L159: 未处理的易出错调用
- ❌ L160: 未处理的易出错调用
- ❌ L161: 未处理的易出错调用
- 🏷️ `_build_mastery_list()` L73: "_build_mastery_list" - snake_case
- 🏷️ `_build_ability_scores()` L90: "_build_ability_scores" - snake_case
- 🏷️ `_build_habit_preferences()` L98: "_build_habit_preferences" - snake_case
- 🏷️ `_build_profile_history()` L113: "_build_profile_history" - snake_case
- 🏷️ `_average_history_mastery()` L130: "_average_history_mastery" - snake_case
- 🏷️ `_build_answer_stats()` L137: "_build_answer_stats" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 4
- 认知复杂度: 平均: 3.5, 最大: 6
- 嵌套深度: 平均: 0.6, 最大: 1
- 函数长度: 平均: 12.2 行, 最大: 19 行
- 文件长度: 137 代码量 (167 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 9.1% 重复 (1/11)
- 结构分析: 0 个结构问题
- 错误处理: 4/6 个错误被忽略 (66.7%)
- 注释比例: 0.0% (0/137)
- 命名规范: 发现 6 个违规

### 139. backend\ai_services\test_kt_models.py

**糟糕指数: 9.17**

> 行数: 434 总计, 387 代码, 2 注释 | 函数: 10 | 类: 3

**问题**: ⚠️ 其他问题: 3, 📋 重复问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_mefkt_predictor_should_load_checkpoint_and_return_predictions` | L54-113 | 60 | 3 | 2 | 1 | ✓ |
| `test_mefkt_predictor_should_support_question_online_runtime` | L115-243 | 129 | 3 | 2 | 1 | ✓ |
| `test_predict_mastery_should_degrade_gracefully_on_model_name_error` | L271-300 | 30 | 2 | 1 | 1 | ✓ |
| `test_predict_mastery_should_return_course_defaults_without_history` | L302-326 | 25 | 2 | 1 | 1 | ✓ |
| `test_kt_service_model_info_should_expose_mefkt_config` | L37-52 | 16 | 1 | 0 | 1 | ✓ |
| `test_mefkt_perceived_distance_should_increase_with_longer_gap` | L245-265 | 21 | 1 | 0 | 1 | ✓ |
| `setUp` | L332-381 | 50 | 1 | 0 | 1 | ✓ |
| `_profile` | L383-397 | 15 | 1 | 0 | 3 | ✓ |
| `test_kp_profile_should_reflect_prerequisite_depth_and_item_difficulty` | L399-405 | 7 | 1 | 0 | 1 | ✓ |
| `test_simulated_sequences_should_show_ability_gap_and_revisits` | L407-433 | 27 | 1 | 0 | 1 | ✓ |

**全部问题 (6)**

- 📏 `test_mefkt_predictor_should_load_checkpoint_and_return_predictions()` L54: 60 代码量
- 📏 `test_mefkt_predictor_should_support_question_online_runtime()` L115: 129 代码量
- 📋 `test_mefkt_predictor_should_load_checkpoint_and_return_predictions()` L54: 重复模式: test_mefkt_predictor_should_load_checkpoint_and_return_predictions, test_simulated_sequences_should_show_ability_gap_and_revisits
- 🏗️ L1: 导入过多: 32
- 🏷️ `setUp()` L332: "setUp" - snake_case
- 🏷️ `_profile()` L383: "_profile" - snake_case

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 3
- 认知复杂度: 平均: 2.8, 最大: 7
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 38.0 行, 最大: 129 行
- 文件长度: 387 代码量 (434 总计)
- 参数数量: 平均: 1.2, 最大: 3
- 代码重复: 10.0% 重复 (1/10)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.5% (2/387)
- 命名规范: 发现 2 个违规

### 140. backend\tools\rebuild_demo_support.py

**糟糕指数: 9.13**

> 行数: 185 总计, 162 代码, 0 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `print_assistant_demo_queries` | L94-118 | 25 | 10 | 2 | 1 | ✓ |
| `sync_demo_course_runtime` | L37-51 | 15 | 3 | 1 | 2 | ✓ |
| `assert_demo_graph_ready` | L54-62 | 9 | 3 | 1 | 3 | ✓ |
| `print_demo_user_statuses` | L151-176 | 26 | 3 | 2 | 2 | ✓ |
| `iter_demo_usernames` | L24-29 | 6 | 2 | 1 | 0 | ✓ |
| `print_demo_course_summary` | L65-91 | 27 | 2 | 1 | 5 | ✓ |
| `_user_course_status` | L121-148 | 28 | 2 | 0 | 3 | ✓ |
| `load_demo_course` | L32-34 | 3 | 1 | 0 | 1 | ✓ |
| `print_demo_followup_hint` | L179-184 | 6 | 1 | 0 | 0 | ✓ |

**全部问题 (4)**

- 🔄 `print_assistant_demo_queries()` L94: 认知复杂度: 14
- ❌ L97: 未处理的易出错调用
- ❌ L102: 未处理的易出错调用
- 🏷️ `_user_course_status()` L121: "_user_course_status" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 10
- 认知复杂度: 平均: 4.8, 最大: 14
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 16.1 行, 最大: 28 行
- 文件长度: 162 代码量 (185 总计)
- 参数数量: 平均: 1.9, 最大: 5
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 2/11 个错误被忽略 (18.2%)
- 注释比例: 0.0% (0/162)
- 命名规范: 发现 1 个违规

### 141. backend\ai_services\kt_views.py

**糟糕指数: 9.00**

> 行数: 97 总计, 82 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 📋 重复问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `kt_predict` | L20-43 | 24 | 4 | 1 | 1 | ✓ |
| `kt_recommendations` | L74-96 | 23 | 4 | 1 | 1 | ✓ |
| `kt_batch_predict` | L55-69 | 15 | 3 | 1 | 1 | ✓ |
| `kt_model_info` | L48-50 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- 📋 `kt_predict()` L20: 重复模式: kt_predict, kt_recommendations

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 4
- 认知复杂度: 平均: 4.5, 最大: 6
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 16.3 行, 最大: 24 行
- 文件长度: 82 代码量 (97 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 25.0% 重复 (1/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/82)
- 命名规范: 无命名违规

### 142. backend\exams\student_helpers.py

**糟糕指数: 8.99**

> 行数: 289 总计, 244 代码, 0 注释 | 函数: 16 | 类: 2

**问题**: ❌ 错误处理问题: 9, 📝 注释问题: 1, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_feedback_overview` | L244-258 | 15 | 10 | 0 | 1 | ✓ |
| `normalize_feedback_payload` | L142-171 | 30 | 8 | 0 | 2 | ✓ |
| `_extract_list_analysis` | L207-218 | 12 | 6 | 1 | 1 | ✓ |
| `resolve_pass_threshold` | L73-94 | 22 | 5 | 2 | 1 | ✓ |
| `_extract_analysis_text_and_gaps` | L194-204 | 11 | 5 | 1 | 1 | ✓ |
| `build_exam_score_map` | L97-102 | 6 | 4 | 0 | 2 | ✓ |
| `_normalize_feedback_text` | L179-191 | 13 | 4 | 1 | 2 | ✓ |
| `build_submission_feedback_snapshot` | L266-288 | 23 | 4 | 0 | 1 | ✓ |
| `build_question_detail` | L105-129 | 25 | 3 | 0 | 3 | ✓ |
| `build_exam_question_details` | L132-139 | 8 | 3 | 1 | 3 | ✓ |
| `_apply_question_detail_stats` | L227-241 | 15 | 3 | 1 | 2 | ✓ |
| `snapshot_mastery_for_points` | L50-57 | 8 | 2 | 1 | 3 | ✓ |
| `_normalized_overview` | L174-176 | 3 | 2 | 0 | 1 | ✓ |
| `build_mastery_change_payload` | L60-70 | 11 | 1 | 0 | 2 | ✓ |
| `_clean_text_list` | L221-224 | 4 | 1 | 0 | 1 | ✓ |
| `build_feedback_report_ref` | L261-263 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (15)**

- ❌ L66: 未处理的易出错调用
- ❌ L67: 未处理的易出错调用
- ❌ L68: 未处理的易出错调用
- ❌ L69: 未处理的易出错调用
- ❌ L125: 未处理的易出错调用
- ❌ L127: 未处理的易出错调用
- ❌ L128: 未处理的易出错调用
- ❌ L138: 未处理的易出错调用
- ❌ L213: 未处理的易出错调用
- 🏷️ `_normalized_overview()` L174: "_normalized_overview" - snake_case
- 🏷️ `_normalize_feedback_text()` L179: "_normalize_feedback_text" - snake_case
- 🏷️ `_extract_analysis_text_and_gaps()` L194: "_extract_analysis_text_and_gaps" - snake_case
- 🏷️ `_extract_list_analysis()` L207: "_extract_list_analysis" - snake_case
- 🏷️ `_clean_text_list()` L221: "_clean_text_list" - snake_case
- 🏷️ `_apply_question_detail_stats()` L227: "_apply_question_detail_stats" - snake_case

**详情**:
- 循环复杂度: 平均: 3.9, 最大: 10
- 认知复杂度: 平均: 4.9, 最大: 10
- 嵌套深度: 平均: 0.5, 最大: 2
- 函数长度: 平均: 13.1 行, 最大: 30 行
- 文件长度: 244 代码量 (289 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/16)
- 结构分析: 0 个结构问题
- 错误处理: 9/20 个错误被忽略 (45.0%)
- 注释比例: 0.0% (0/244)
- 命名规范: 发现 6 个违规

### 143. backend\ai_services\consumers.py

**糟糕指数: 8.92**

> 行数: 75 总计, 59 代码, 1 注释 | 函数: 3 | 类: 1

**问题**: 🔄 复杂度问题: 1, ❌ 错误处理问题: 5, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `receive_json` | L35-74 | 40 | 9 | 2 | 2 | ✓ |
| `connect` | L26-33 | 8 | 3 | 1 | 1 | ✓ |
| `_split_reply_chunks` | L13-20 | 8 | 2 | 1 | 2 | ✓ |

**全部问题 (7)**

- 🔄 `receive_json()` L35: 认知复杂度: 13
- ❌ L26: 未处理的易出错调用
- ❌ L32: 未处理的易出错调用
- ❌ L66: 未处理的易出错调用
- ❌ L67: 未处理的易出错调用
- ❌ L68: 未处理的易出错调用
- 🏷️ `_split_reply_chunks()` L13: "_split_reply_chunks" - snake_case

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 9
- 认知复杂度: 平均: 7.3, 最大: 13
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 18.7 行, 最大: 40 行
- 文件长度: 59 代码量 (75 总计)
- 参数数量: 平均: 1.7, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 5/13 个错误被忽略 (38.5%)
- 注释比例: 1.7% (1/59)
- 命名规范: 发现 1 个违规

### 144. backend\common\errors.py

**糟糕指数: 8.91**

> 行数: 132 总计, 109 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_flatten_error_messages` | L36-60 | 25 | 9 | 3 | 1 | ✓ |
| `custom_exception_handler` | L63-104 | 42 | 5 | 1 | 2 | ✓ |
| `_normalize_error_detail` | L17-33 | 17 | 4 | 1 | 1 | ✓ |
| `get_error_message` | L107-128 | 22 | 3 | 2 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `_flatten_error_messages()` L36: 认知复杂度: 15
- 🏗️ `_flatten_error_messages()` L36: 中等嵌套: 3
- 🏷️ `_normalize_error_detail()` L17: "_normalize_error_detail" - snake_case
- 🏷️ `_flatten_error_messages()` L36: "_flatten_error_messages" - snake_case

**详情**:
- 循环复杂度: 平均: 5.3, 最大: 9
- 认知复杂度: 平均: 8.8, 最大: 15
- 嵌套深度: 平均: 1.8, 最大: 3
- 函数长度: 平均: 26.5 行, 最大: 42 行
- 文件长度: 109 代码量 (132 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 1 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/109)
- 命名规范: 发现 2 个违规

### 145. frontend\src\views\teacher\useTeacherResourceManage.js

**糟糕指数: 8.77**

> 行数: 339 总计, 300 代码, 0 注释 | 函数: 19 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `submitForm` | L137-178 | 41 | 7 | 2 | 0 | ✗ |
| `submitImport` | L215-242 | 28 | 4 | 1 | 0 | ✗ |
| `ensureCourseId` | L55-61 | 7 | 3 | 1 | 0 | ✗ |
| `deleteResource` | L188-204 | 17 | 3 | 1 | 1 | ✗ |
| `fetchResources` | L244-270 | 27 | 3 | 1 | 0 | ✗ |
| `fetchKnowledgePoints` | L272-286 | 15 | 3 | 1 | 0 | ✗ |
| `beforeFileUpload` | L67-77 | 11 | 2 | 1 | 1 | ✗ |
| `editResource` | L109-131 | 23 | 2 | 0 | 1 | ✗ |
| `previewResource` | L180-186 | 7 | 2 | 1 | 1 | ✗ |
| `useTeacherResourceManage` | L25-338 | 82 | 1 | 0 | 0 | ✗ |
| `resetResourceForm` | L63-65 | 3 | 1 | 0 | 0 | ✗ |
| `handleSearch` | L79-82 | 4 | 1 | 0 | 0 | ✗ |
| `handleResourcePageSizeChange` | L84-88 | 5 | 1 | 0 | 1 | ✗ |
| `handleResourcePageChange` | L90-93 | 4 | 1 | 0 | 1 | ✗ |
| `resetSearch` | L95-100 | 6 | 1 | 0 | 0 | ✗ |
| `showCreateDialog` | L102-107 | 6 | 1 | 0 | 0 | ✗ |
| `handleFileChange` | L133-135 | 3 | 1 | 0 | 1 | ✗ |
| `showImportDialog` | L206-209 | 4 | 1 | 0 | 0 | ✗ |
| `handleImportFile` | L211-213 | 3 | 1 | 0 | 1 | ✗ |

**全部问题 (2)**

- 📋 `resetSearch()` L95: 重复模式: resetSearch, showCreateDialog
- ❌ L182: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.1, 最大: 7
- 认知复杂度: 平均: 3.0, 最大: 11
- 嵌套深度: 平均: 0.5, 最大: 2
- 函数长度: 平均: 15.6 行, 最大: 82 行
- 文件长度: 300 代码量 (339 总计)
- 参数数量: 平均: 0.4, 最大: 1
- 代码重复: 5.3% 重复 (1/19)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/300)
- 命名规范: 无命名违规

### 146. backend\knowledge\teacher_relation_views.py

**糟糕指数: 8.73**

> 行数: 114 总计, 94 代码, 0 注释 | 函数: 3 | 类: 0

**问题**: ❌ 错误处理问题: 7, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `knowledge_relation_create` | L64-97 | 34 | 9 | 1 | 1 | ✓ |
| `knowledge_relation_list` | L25-59 | 35 | 4 | 1 | 1 | ✓ |
| `knowledge_relation_delete` | L102-113 | 12 | 2 | 1 | 2 | ✓ |

**全部问题 (7)**

- ❌ L35: 未处理的易出错调用
- ❌ L36: 未处理的易出错调用
- ❌ L37: 未处理的易出错调用
- ❌ L38: 未处理的易出错调用
- ❌ L39: 未处理的易出错调用
- ❌ L40: 未处理的易出错调用
- ❌ L111: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 9
- 认知复杂度: 平均: 7.0, 最大: 11
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 27.0 行, 最大: 35 行
- 文件长度: 94 代码量 (114 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 7/13 个错误被忽略 (53.8%)
- 注释比例: 0.0% (0/94)
- 命名规范: 无命名违规

### 147. backend\ai_services\services\mefkt_question_online.py

**糟糕指数: 8.68**

> 行数: 374 总计, 325 代码, 0 注释 | 函数: 14 | 类: 2

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_resolve_target_point_ids` | L196-203 | 8 | 4 | 1 | 1 | ✓ |
| `_points_from_answer_history` | L206-218 | 13 | 4 | 2 | 1 | ✓ |
| `_aggregate_point_predictions` | L301-318 | 18 | 3 | 2 | 3 | ✓ |
| `_point_probabilities` | L321-340 | 20 | 3 | 1 | 3 | ✓ |
| `predict_question_online` | L49-83 | 35 | 2 | 1 | 1 | ✓ |
| `_build_online_model_bundle` | L86-114 | 29 | 2 | 1 | 1 | ✓ |
| `_build_fused_question_embedding` | L117-157 | 41 | 2 | 0 | 1 | ✓ |
| `_encode_fused_embedding` | L160-188 | 29 | 2 | 1 | 5 | ✓ |
| `_predict_candidate_questions` | L245-282 | 38 | 2 | 1 | 4 | ✓ |
| `_metadata_int` | L191-193 | 3 | 1 | 0 | 3 | ✓ |
| `_resolve_candidate_question_indices` | L221-232 | 12 | 1 | 0 | 2 | ✓ |
| `_empty_question_online_response` | L235-242 | 8 | 1 | 0 | 0 | ✓ |
| `_build_per_question_predictions` | L285-298 | 14 | 1 | 0 | 3 | ✓ |
| `_question_online_response` | L343-373 | 31 | 1 | 0 | 4 | ✓ |

**全部问题 (13)**

- ❌ L216: 未处理的易出错调用
- ❌ L230: 未处理的易出错调用
- ❌ L330: 未处理的易出错调用
- 🏷️ `_build_online_model_bundle()` L86: "_build_online_model_bundle" - snake_case
- 🏷️ `_build_fused_question_embedding()` L117: "_build_fused_question_embedding" - snake_case
- 🏷️ `_encode_fused_embedding()` L160: "_encode_fused_embedding" - snake_case
- 🏷️ `_metadata_int()` L191: "_metadata_int" - snake_case
- 🏷️ `_resolve_target_point_ids()` L196: "_resolve_target_point_ids" - snake_case
- 🏷️ `_points_from_answer_history()` L206: "_points_from_answer_history" - snake_case
- 🏷️ `_resolve_candidate_question_indices()` L221: "_resolve_candidate_question_indices" - snake_case
- 🏷️ `_empty_question_online_response()` L235: "_empty_question_online_response" - snake_case
- 🏷️ `_predict_candidate_questions()` L245: "_predict_candidate_questions" - snake_case
- 🏷️ `_build_per_question_predictions()` L285: "_build_per_question_predictions" - snake_case

**详情**:
- 循环复杂度: 平均: 2.1, 最大: 4
- 认知复杂度: 平均: 3.5, 最大: 8
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 21.4 行, 最大: 41 行
- 文件长度: 325 代码量 (374 总计)
- 参数数量: 平均: 2.3, 最大: 5
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 3/11 个错误被忽略 (27.3%)
- 注释比例: 0.0% (0/325)
- 命名规范: 发现 13 个违规

### 148. frontend\src\components\knowledge\useKnowledgeGraphD3.js

**糟糕指数: 8.48**

> 行数: 381 总计, 331 代码, 0 注释 | 函数: 14 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getMasteryColor` | L65-71 | 7 | 5 | 1 | 1 | ✗ |
| `handleNodeClick` | L116-138 | 23 | 4 | 1 | 1 | ✗ |
| `fitView` | L88-106 | 19 | 3 | 1 | 0 | ✗ |
| `cleanupGraph` | L83-86 | 4 | 2 | 1 | 0 | ✗ |
| `renderGraph` | L140-270 | 83 | 2 | 1 | 0 | ✗ |
| `updateNodeData` | L288-296 | 5 | 2 | 1 | 0 | ✗ |
| `deleteNode` | L298-305 | 6 | 2 | 1 | 0 | ✗ |
| `useKnowledgeGraphD3` | L16-380 | 73 | 1 | 0 | 2 | ✗ |
| `syncLocalGraph` | L73-76 | 2 | 1 | 0 | 0 | ✗ |
| `stopSimulation` | L78-81 | 4 | 1 | 0 | 0 | ✗ |
| `zoomIn` | L108-110 | 3 | 1 | 0 | 0 | ✗ |
| `zoomOut` | L112-114 | 3 | 1 | 0 | 0 | ✗ |
| `addNode` | L272-286 | 15 | 1 | 0 | 0 | ✗ |
| `saveGraph` | L307-326 | 4 | 1 | 0 | 0 | ✗ |

**全部问题 (2)**

- 📋 `updateNodeData()` L288: 重复模式: updateNodeData, deleteNode
- ❌ L85: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.9, 最大: 5
- 认知复杂度: 平均: 2.9, 最大: 7
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 17.9 行, 最大: 83 行
- 文件长度: 331 代码量 (381 总计)
- 参数数量: 平均: 0.3, 最大: 2
- 代码重复: 7.1% 重复 (1/14)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/331)
- 命名规范: 无命名违规

### 149. backend\models\MEFKT\sequence.py

**糟糕指数: 8.43**

> 行数: 201 总计, 179 代码, 0 注释 | 函数: 4 | 类: 1

**问题**: ⚠️ 其他问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `forward` | L147-197 | 51 | 4 | 2 | 4 | ✓ |
| `predict_candidate` | L80-145 | 66 | 3 | 1 | 5 | ✓ |
| `__init__` | L15-49 | 35 | 2 | 1 | 6 | ✓ |
| `_perceived_distance` | L51-78 | 28 | 1 | 0 | 3 | ✓ |

**全部问题 (5)**

- 📏 `predict_candidate()` L80: 66 代码量
- 📏 `forward()` L147: 51 代码量
- 📏 `__init__()` L15: 6 参数数量
- 🏷️ `__init__()` L15: "__init__" - snake_case
- 🏷️ `_perceived_distance()` L51: "_perceived_distance" - snake_case

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 4
- 认知复杂度: 平均: 4.5, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 45.0 行, 最大: 66 行
- 文件长度: 179 代码量 (201 总计)
- 参数数量: 平均: 4.5, 最大: 6
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/179)
- 命名规范: 发现 2 个违规

### 150. backend\exams\student_submission_views.py

**糟糕指数: 8.40**

> 行数: 180 总计, 162 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `exam_submit` | L33-115 | 83 | 9 | 2 | 2 | ✓ |
| `exam_statistics` | L164-179 | 16 | 5 | 1 | 2 | ✓ |
| `exam_result` | L120-147 | 28 | 3 | 1 | 2 | ✓ |
| `exam_save_draft` | L152-159 | 8 | 2 | 1 | 2 | ✓ |

**全部问题 (3)**

- 🔄 `exam_submit()` L33: 认知复杂度: 13
- 📏 `exam_submit()` L33: 83 代码量
- ❌ L158: 忽略了错误返回值

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 9
- 认知复杂度: 平均: 7.3, 最大: 13
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 33.8 行, 最大: 83 行
- 文件长度: 162 代码量 (180 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 0.0% (0/162)
- 命名规范: 无命名违规

### 151. backend\learning\path_adjustment.py

**糟糕指数: 8.37**

> 行数: 395 总计, 336 代码, 0 注释 | 函数: 19 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_create_path_nodes_with_resources` | L305-319 | 15 | 5 | 2 | 2 | ✓ |
| `_update_mastery_from_answer_history` | L59-92 | 34 | 4 | 2 | 2 | ✓ |
| `insert_remediation_nodes` | L41-56 | 16 | 3 | 2 | 1 | ✓ |
| `_build_kt_history` | L95-113 | 19 | 3 | 1 | 2 | ✓ |
| `_apply_kt_predictions` | L116-140 | 25 | 3 | 2 | 3 | ✓ |
| `_make_path_node_batch` | L227-254 | 28 | 3 | 2 | 5 | ✓ |
| `_make_study_node` | L257-275 | 19 | 3 | 0 | 4 | ✓ |
| `_ensure_active_path_node` | L322-329 | 8 | 3 | 1 | 1 | ✓ |
| `_serialize_refreshed_nodes` | L332-350 | 19 | 3 | 0 | 1 | ✓ |
| `_insert_remediation_node_if_missing` | L353-378 | 26 | 3 | 1 | 2 | ✓ |
| `refresh_learning_path_from_mastery` | L22-38 | 17 | 2 | 1 | 3 | ✓ |
| `_make_test_node` | L278-302 | 25 | 2 | 1 | 3 | ✓ |
| `_serialize_legacy_adjusted_nodes` | L381-394 | 14 | 2 | 0 | 1 | ✓ |
| `_rebuild_locked_path_nodes` | L143-167 | 25 | 1 | 0 | 3 | ✓ |
| `_preserved_path_nodes` | L170-173 | 4 | 1 | 0 | 1 | ✓ |
| `_build_replacement_nodes` | L176-199 | 24 | 1 | 0 | 5 | ✓ |
| `_course_mastery_map` | L202-207 | 6 | 1 | 0 | 2 | ✓ |
| `_remaining_course_points` | L210-219 | 10 | 1 | 0 | 2 | ✓ |
| `_next_order_index` | L222-224 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (11)**

- ❌ L366: 未处理的易出错调用
- 🏷️ `_update_mastery_from_answer_history()` L59: "_update_mastery_from_answer_history" - snake_case
- 🏷️ `_build_kt_history()` L95: "_build_kt_history" - snake_case
- 🏷️ `_apply_kt_predictions()` L116: "_apply_kt_predictions" - snake_case
- 🏷️ `_rebuild_locked_path_nodes()` L143: "_rebuild_locked_path_nodes" - snake_case
- 🏷️ `_preserved_path_nodes()` L170: "_preserved_path_nodes" - snake_case
- 🏷️ `_build_replacement_nodes()` L176: "_build_replacement_nodes" - snake_case
- 🏷️ `_course_mastery_map()` L202: "_course_mastery_map" - snake_case
- 🏷️ `_remaining_course_points()` L210: "_remaining_course_points" - snake_case
- 🏷️ `_next_order_index()` L222: "_next_order_index" - snake_case
- 🏷️ `_make_path_node_batch()` L227: "_make_path_node_batch" - snake_case

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 5
- 认知复杂度: 平均: 3.9, 最大: 9
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 17.7 行, 最大: 34 行
- 文件长度: 336 代码量 (395 总计)
- 参数数量: 平均: 2.3, 最大: 5
- 代码重复: 0.0% 重复 (0/19)
- 结构分析: 0 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 0.0% (0/336)
- 命名规范: 发现 17 个违规

### 152. backend\ai_services\test_llm_service.py

**糟糕指数: 8.30**

> 行数: 371 总计, 308 代码, 0 注释 | 函数: 16 | 类: 5

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 2, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_facade_graphrag_llm_should_instantiate_without_legacy_warning` | L337-346 | 10 | 2 | 1 | 1 | ✓ |
| `test_facade_graphrag_llm_should_accept_v2_message_lists` | L348-370 | 23 | 2 | 1 | 1 | ✓ |
| `test_llm_service_should_resolve_explicit_doubao_provider` | L46-55 | 10 | 1 | 0 | 1 | ✓ |
| `test_llm_service_should_resolve_custom_gateway_fields` | L66-75 | 10 | 1 | 0 | 1 | ✓ |
| `test_llm_service_should_attach_https_proxy_to_chat_client` | L88-102 | 15 | 1 | 0 | 2 | ✓ |
| `test_llm_service_should_default_deepseek_v4_to_non_thinking_mode` | L116-135 | 20 | 1 | 0 | 2 | ✓ |
| `test_external_resource_recommendation_should_enable_provider_web_search` | L149-178 | 30 | 1 | 0 | 2 | ✓ |
| `test_llm_json_parser_should_ignore_think_blocks` | L180-188 | 9 | 1 | 0 | 1 | ✓ |
| `_build_service` | L195-200 | 6 | 1 | 0 | 0 | ✗ |
| `test_call_with_fallback_should_skip_agent_for_profile_analysis` | L202-220 | 19 | 1 | 0 | 1 | ✓ |
| `test_call_with_fallback_should_only_use_agent_for_explicit_agent_calls` | L222-238 | 17 | 1 | 0 | 1 | ✓ |
| `_build_service` | L245-250 | 6 | 1 | 0 | 0 | ✗ |
| `test_call_with_fallback_should_fast_fail_graph_rag_calls_without_repair` | L252-276 | 25 | 1 | 0 | 1 | ✓ |
| `test_call_with_fallback_should_keep_repair_for_profile_analysis` | L278-293 | 16 | 1 | 0 | 1 | ✓ |
| `test_chat_policy_should_fast_fail_like_other_interactive_routes` | L295-304 | 10 | 1 | 0 | 1 | ✓ |
| `test_agent_service_should_forward_proxy_to_chat_openai` | L321-331 | 11 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- 📋 `test_llm_service_should_attach_https_proxy_to_chat_client()` L88: 重复模式: test_llm_service_should_attach_https_proxy_to_chat_client, test_llm_service_should_default_deepseek_v4_to_non_thinking_mode
- 📋 `test_call_with_fallback_should_only_use_agent_for_explicit_agent_calls()` L222: 重复模式: test_call_with_fallback_should_only_use_agent_for_explicit_agent_calls, test_call_with_fallback_should_keep_repair_for_profile_analysis, test_facade_graphrag_llm_should_accept_v2_message_lists
- 🏗️ L1: 导入过多: 31

**详情**:
- 循环复杂度: 平均: 1.1, 最大: 2
- 认知复杂度: 平均: 1.4, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 14.8 行, 最大: 30 行
- 文件长度: 308 代码量 (371 总计)
- 参数数量: 平均: 1.1, 最大: 2
- 代码重复: 18.8% 重复 (3/16)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/308)
- 命名规范: 发现 2 个违规

### 153. backend\ai_services\services\mefkt_inference.py

**糟糕指数: 8.27**

> 行数: 227 总计, 199 代码, 2 注释 | 函数: 12 | 类: 1

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 7, 📝 注释问题: 1, 🏷️ 命名问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_resolve_runtime_history_index` | L90-105 | 16 | 4 | 2 | 3 | ✓ |
| `predict` | L181-199 | 19 | 4 | 2 | 4 | ✓ |
| `_build_history_tensors_runtime` | L107-133 | 27 | 3 | 2 | 3 | ✓ |
| `is_loaded` | L49-51 | 3 | 2 | 0 | 1 | ✓ |
| `load_model` | L53-63 | 11 | 2 | 1 | 3 | ✓ |
| `_build_course_runtime_bundle` | L82-88 | 7 | 2 | 1 | 2 | ✓ |
| `_predict_question_online` | L150-179 | 30 | 2 | 0 | 4 | ✓ |
| `__init__` | L32-46 | 15 | 1 | 0 | 1 | ✗ |
| `_apply_loaded_state` | L65-80 | 16 | 1 | 0 | 2 | ✓ |
| `_predict_legacy` | L135-148 | 14 | 1 | 0 | 3 | ✓ |
| `get_info` | L201-216 | 16 | 1 | 0 | 1 | ✓ |
| `auto_load_model` | L222-226 | 5 | 1 | 0 | 0 | ✓ |

**全部问题 (14)**

- ❌ L209: 未处理的易出错调用
- ❌ L210: 未处理的易出错调用
- ❌ L211: 未处理的易出错调用
- ❌ L212: 未处理的易出错调用
- ❌ L213: 未处理的易出错调用
- ❌ L214: 未处理的易出错调用
- ❌ L215: 未处理的易出错调用
- 🏷️ `__init__()` L32: "__init__" - snake_case
- 🏷️ `_apply_loaded_state()` L65: "_apply_loaded_state" - snake_case
- 🏷️ `_build_course_runtime_bundle()` L82: "_build_course_runtime_bundle" - snake_case
- 🏷️ `_resolve_runtime_history_index()` L90: "_resolve_runtime_history_index" - snake_case
- 🏷️ `_build_history_tensors_runtime()` L107: "_build_history_tensors_runtime" - snake_case
- 🏷️ `_predict_legacy()` L135: "_predict_legacy" - snake_case
- 🏷️ `_predict_question_online()` L150: "_predict_question_online" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 4
- 认知复杂度: 平均: 3.3, 最大: 8
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 14.9 行, 最大: 30 行
- 文件长度: 199 代码量 (227 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 7/10 个错误被忽略 (70.0%)
- 注释比例: 1.0% (2/199)
- 命名规范: 发现 7 个违规

### 154. backend\ai_services\services\llm_feedback_kt_support.py

**糟糕指数: 8.23**

> 行数: 307 总计, 260 代码, 0 注释 | 函数: 11 | 类: 5

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 9, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_kt_analysis_prompt` | L230-267 | 38 | 6 | 0 | 1 | ✓ |
| `classify_feedback_performance` | L80-120 | 41 | 5 | 1 | 1 | ✓ |
| `build_kt_analysis_fallback` | L270-294 | 25 | 5 | 0 | 1 | ✓ |
| `build_feedback_report_prompt` | L123-156 | 34 | 3 | 0 | 1 | ✓ |
| `summarize_kt_predictions` | L181-209 | 29 | 3 | 0 | 2 | ✓ |
| `readable_point_name` | L212-215 | 4 | 3 | 0 | 2 | ✓ |
| `summarize_answer_trend` | L218-227 | 10 | 3 | 1 | 1 | ✓ |
| `accuracy` | L31-33 | 3 | 2 | 0 | 1 | ✓ |
| `build_mistake_points` | L65-77 | 13 | 2 | 1 | 1 | ✓ |
| `build_feedback_report_fallback` | L159-178 | 20 | 2 | 0 | 1 | ✓ |
| `build_weak_point_analysis` | L297-306 | 10 | 2 | 1 | 2 | ✓ |

**全部问题 (10)**

- 📋 `build_mistake_points()` L65: 重复模式: build_mistake_points, build_weak_point_analysis
- ❌ L70: 未处理的易出错调用
- ❌ L71: 未处理的易出错调用
- ❌ L72: 未处理的易出错调用
- ❌ L73: 未处理的易出错调用
- ❌ L74: 未处理的易出错调用
- ❌ L131: 未处理的易出错调用
- ❌ L132: 未处理的易出错调用
- ❌ L163: 未处理的易出错调用
- ❌ L170: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 6
- 认知复杂度: 平均: 4.0, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 20.6 行, 最大: 41 行
- 文件长度: 260 代码量 (307 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 9.1% 重复 (1/11)
- 结构分析: 0 个结构问题
- 错误处理: 9/18 个错误被忽略 (50.0%)
- 注释比例: 0.0% (0/260)
- 命名规范: 无命名违规

### 155. backend\assessments\ability_views.py

**糟糕指数: 8.20**

> 行数: 367 总计, 311 代码, 0 注释 | 函数: 20 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_normalize_answer_map` | L169-184 | 16 | 5 | 1 | 1 | ✓ |
| `_is_question_answer_correct` | L222-236 | 15 | 4 | 1 | 2 | ✓ |
| `_score_global_survey` | L239-262 | 24 | 4 | 2 | 1 | ✓ |
| `_save_ability_result` | L318-347 | 30 | 4 | 1 | 5 | ✓ |
| `_resolve_default_course_id` | L350-357 | 8 | 4 | 1 | 1 | ✓ |
| `submit_ability_assessment` | L70-102 | 33 | 3 | 1 | 1 | ✓ |
| `_score_course_assessment` | L208-219 | 12 | 3 | 2 | 2 | ✓ |
| `_answer_question_ids` | L265-273 | 9 | 3 | 2 | 1 | ✓ |
| `_survey_option_score` | L276-287 | 12 | 3 | 2 | 2 | ✓ |
| `get_ability_assessment` | L54-65 | 12 | 2 | 1 | 1 | ✓ |
| `_get_course_ability_assessment` | L105-113 | 9 | 2 | 1 | 1 | ✓ |
| `_get_or_create_global_ability_questions` | L116-128 | 13 | 2 | 1 | 0 | ✓ |
| `_score_ability_answers` | L187-205 | 19 | 2 | 1 | 2 | ✓ |
| `_add_dimension_score` | L290-300 | 11 | 2 | 1 | 4 | ✓ |
| `_build_ability_analysis` | L303-310 | 8 | 2 | 0 | 1 | ✓ |
| `_percentage` | L313-315 | 3 | 2 | 0 | 2 | ✓ |
| `_mark_ability_assessment_done` | L360-366 | 7 | 2 | 1 | 2 | ✓ |
| `retake_ability_assessment` | L44-49 | 6 | 1 | 0 | 1 | ✓ |
| `_serialize_survey_payload` | L131-148 | 18 | 1 | 0 | 1 | ✓ |
| `_serialize_assessment_payload` | L151-166 | 16 | 1 | 0 | 1 | ✓ |

**全部问题 (12)**

- ❌ L217: 未处理的易出错调用
- ❌ L225: 未处理的易出错调用
- 🏷️ `_get_course_ability_assessment()` L105: "_get_course_ability_assessment" - snake_case
- 🏷️ `_get_or_create_global_ability_questions()` L116: "_get_or_create_global_ability_questions" - snake_case
- 🏷️ `_serialize_survey_payload()` L131: "_serialize_survey_payload" - snake_case
- 🏷️ `_serialize_assessment_payload()` L151: "_serialize_assessment_payload" - snake_case
- 🏷️ `_normalize_answer_map()` L169: "_normalize_answer_map" - snake_case
- 🏷️ `_score_ability_answers()` L187: "_score_ability_answers" - snake_case
- 🏷️ `_score_course_assessment()` L208: "_score_course_assessment" - snake_case
- 🏷️ `_is_question_answer_correct()` L222: "_is_question_answer_correct" - snake_case
- 🏷️ `_score_global_survey()` L239: "_score_global_survey" - snake_case
- 🏷️ `_answer_question_ids()` L265: "_answer_question_ids" - snake_case

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 5
- 认知复杂度: 平均: 4.5, 最大: 8
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 14.1 行, 最大: 33 行
- 文件长度: 311 代码量 (367 总计)
- 参数数量: 平均: 1.6, 最大: 5
- 代码重复: 5.0% 重复 (1/20)
- 结构分析: 0 个结构问题
- 错误处理: 2/8 个错误被忽略 (25.0%)
- 注释比例: 0.0% (0/311)
- 命名规范: 发现 17 个违规

### 156. frontend\src\views\student\useTaskLearning.js

**糟糕指数: 8.19**

> 行数: 413 总计, 378 代码, 1 注释 | 函数: 19 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `resolveTemplateElement` | L41-47 | 7 | 4 | 1 | 1 | ✗ |
| `loadNodeData` | L123-143 | 21 | 4 | 1 | 0 | ✗ |
| `selectResource` | L183-196 | 14 | 4 | 1 | 1 | ✗ |
| `loadStageTest` | L219-237 | 19 | 4 | 1 | 0 | ✗ |
| `submitStageTestAnswers` | L239-268 | 24 | 4 | 1 | 0 | ✗ |
| `loadNodeIntro` | L159-176 | 18 | 3 | 1 | 0 | ✗ |
| `startQuiz` | L279-291 | 13 | 3 | 1 | 0 | ✗ |
| `sendChat` | L299-326 | 28 | 3 | 1 | 0 | ✗ |
| `loadAIResources` | L145-157 | 13 | 2 | 0 | 0 | ✗ |
| `goBack` | L178-181 | 4 | 2 | 0 | 0 | ✗ |
| `completeTask` | L198-207 | 10 | 2 | 0 | 0 | ✗ |
| `loadNodeExam` | L209-217 | 9 | 2 | 0 | 0 | ✗ |
| `scrollChat` | L293-297 | 5 | 2 | 1 | 0 | ✗ |
| `scrollStageTestCardIntoView` | L328-333 | 6 | 2 | 1 | 0 | ✗ |
| `useTaskLearning` | L49-412 | 100 | 1 | 0 | 0 | ✗ |
| `retryStageTest` | L270-273 | 4 | 1 | 0 | 0 | ✗ |
| `resetNodeQuizResult` | L275-277 | 3 | 1 | 0 | 0 | ✗ |
| `openFullAssistant` | L335-341 | 7 | 1 | 0 | 0 | ✗ |
| `formatMessage` | L343-343 | 1 | 1 | 0 | 1 | ✗ |

**全部问题 (1)**

- ❌ L185: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 4
- 认知复杂度: 平均: 3.5, 最大: 6
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 16.1 行, 最大: 100 行
- 文件长度: 378 代码量 (413 总计)
- 参数数量: 平均: 0.2, 最大: 1
- 代码重复: 0.0% 重复 (0/19)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 0.3% (1/378)
- 命名规范: 无命名违规

### 157. backend\logs\views.py

**糟糕指数: 8.13**

> 行数: 329 总计, 242 代码, 21 注释 | 函数: 10 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_apply_log_filters` | L42-79 | 38 | 11 | 2 | 2 | ✓ |
| `list_operation_logs` | L89-146 | 58 | 8 | 2 | 1 | ✓ |
| `export_logs` | L261-302 | 42 | 7 | 1 | 1 | ✓ |
| `get_operation_log_detail` | L151-166 | 16 | 3 | 1 | 2 | ✓ |
| `clean_expired_logs` | L307-328 | 22 | 3 | 1 | 1 | ✓ |
| `is_admin` | L82-84 | 3 | 2 | 0 | 1 | ✓ |
| `get_log_statistics` | L171-211 | 41 | 2 | 1 | 1 | ✓ |
| `get_log_filter_options` | L216-228 | 13 | 2 | 1 | 1 | ✓ |
| `get_log_modules` | L233-242 | 10 | 2 | 1 | 1 | ✓ |
| `get_log_actions` | L247-256 | 10 | 2 | 1 | 1 | ✓ |

**全部问题 (9)**

- 🔄 `_apply_log_filters()` L42: 复杂度: 11
- 🔄 `_apply_log_filters()` L42: 认知复杂度: 15
- 📏 `list_operation_logs()` L89: 58 代码量
- ❌ L281: 未处理的易出错调用
- ❌ L293: 未处理的易出错调用
- ❌ L294: 未处理的易出错调用
- ❌ L323: 忽略了错误返回值
- 🏷️ `_apply_log_filters()` L42: "_apply_log_filters" - snake_case
- 🏷️ L35: "_AdminCapableUser" - PascalCase

**详情**:
- 循环复杂度: 平均: 4.2, 最大: 11
- 认知复杂度: 平均: 6.4, 最大: 15
- 嵌套深度: 平均: 1.1, 最大: 2
- 函数长度: 平均: 25.3 行, 最大: 58 行
- 文件长度: 242 代码量 (329 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 4/17 个错误被忽略 (23.5%)
- 注释比例: 8.7% (21/242)
- 命名规范: 发现 2 个违规

### 158. backend\ai_services\student_rag_views.py

**糟糕指数: 8.08**

> 行数: 93 总计, 79 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ai_node_intro` | L54-92 | 39 | 10 | 1 | 1 | ✓ |
| `ai_path_planning` | L26-49 | 24 | 4 | 1 | 1 | ✓ |

**全部问题 (1)**

- ❌ L44: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.0, 最大: 10
- 认知复杂度: 平均: 9.0, 最大: 12
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 31.5 行, 最大: 39 行
- 文件长度: 79 代码量 (93 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 0.0% (0/79)
- 命名规范: 无命名违规

### 159. backend\ai_services\services\llm_profile_path_mixin.py

**糟糕指数: 8.00**

> 行数: 133 总计, 115 代码, 0 注释 | 函数: 5 | 类: 1

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `plan_learning_path` | L54-88 | 35 | 2 | 1 | 6 | ✓ |
| `analyze_profile` | L20-52 | 33 | 1 | 0 | 7 | ✓ |
| `generate_resource_reason` | L90-122 | 33 | 1 | 0 | 5 | ✓ |
| `_identify_weakness` | L125-127 | 3 | 1 | 0 | 1 | ✓ |
| `_identify_strength` | L130-132 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (4)**

- 📏 `analyze_profile()` L20: 7 参数数量
- 📏 `plan_learning_path()` L54: 6 参数数量
- 🏷️ `_identify_weakness()` L125: "_identify_weakness" - snake_case
- 🏷️ `_identify_strength()` L130: "_identify_strength" - snake_case

**详情**:
- 循环复杂度: 平均: 1.2, 最大: 2
- 认知复杂度: 平均: 1.6, 最大: 4
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 21.4 行, 最大: 35 行
- 文件长度: 115 代码量 (133 总计)
- 参数数量: 平均: 4.0, 最大: 7
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/115)
- 命名规范: 发现 2 个违规

### 160. backend\knowledge\serializers.py

**糟糕指数: 8.00**

> 行数: 189 总计, 150 代码, 4 注释 | 函数: 6 | 类: 8

**问题**: 📋 重复问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_resources` | L75-103 | 29 | 6 | 3 | 1 | ✓ |
| `get_mastery_rate` | L39-48 | 10 | 4 | 1 | 2 | ✓ |
| `get_format` | L144-150 | 7 | 4 | 1 | 1 | ✓ |
| `get_duration_display` | L153-162 | 10 | 3 | 2 | 1 | ✓ |
| `get_prerequisites` | L51-60 | 10 | 1 | 0 | 1 | ✓ |
| `get_postrequisites` | L63-72 | 10 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 📋 `get_prerequisites()` L51: 重复模式: get_prerequisites, get_postrequisites
- 🏗️ `get_resources()` L75: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 3.2, 最大: 6
- 认知复杂度: 平均: 5.5, 最大: 12
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 12.7 行, 最大: 29 行
- 文件长度: 150 代码量 (189 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 16.7% 重复 (1/6)
- 结构分析: 1 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 2.7% (4/150)
- 命名规范: 无命名违规

### 161. backend\users\admin_activation_views.py

**糟糕指数: 7.92**

> 行数: 214 总计, 180 代码, 0 注释 | 函数: 7 | 类: 0

**问题**: 🔄 复杂度问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_activation_code` | L19-57 | 39 | 9 | 2 | 1 | ✓ |
| `activation_code_export` | L187-213 | 27 | 8 | 1 | 1 | ✓ |
| `delete_activation_code` | L102-125 | 24 | 7 | 1 | 2 | ✓ |
| `list_activation_codes` | L62-97 | 36 | 6 | 1 | 1 | ✓ |
| `activation_code_detail` | L130-148 | 19 | 6 | 1 | 2 | ✓ |
| `activation_code_validate` | L165-182 | 18 | 4 | 1 | 1 | ✓ |
| `activation_code_batch_delete` | L153-160 | 8 | 2 | 1 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `generate_activation_code()` L19: 认知复杂度: 13
- ❌ L124: 未处理的易出错调用
- ❌ L159: 忽略了错误返回值
- ❌ L196: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 9
- 认知复杂度: 平均: 8.3, 最大: 13
- 嵌套深度: 平均: 1.1, 最大: 2
- 函数长度: 平均: 24.4 行, 最大: 39 行
- 文件长度: 180 代码量 (214 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 3/16 个错误被忽略 (18.8%)
- 注释比例: 0.0% (0/180)
- 命名规范: 无命名违规

### 162. backend\tools\diagnostics.py

**糟糕指数: 7.85**

> 行数: 195 总计, 147 代码, 3 注释 | 函数: 14 | 类: 0

**问题**: ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_print_llm_section` | L131-142 | 12 | 5 | 0 | 0 | ✓ |
| `_print_migration_section` | L92-107 | 16 | 4 | 1 | 0 | ✓ |
| `_print_directory_section` | L53-61 | 9 | 3 | 0 | 0 | ✓ |
| `_print_database_section` | L72-81 | 10 | 3 | 1 | 0 | ✓ |
| `_first_configured_env` | L145-151 | 7 | 3 | 2 | 1 | ✓ |
| `_check_postgres` | L84-89 | 6 | 2 | 1 | 0 | ✓ |
| `_print_dependency_section` | L123-128 | 6 | 2 | 1 | 1 | ✓ |
| `_print_data_summary_section` | L154-170 | 17 | 2 | 1 | 0 | ✓ |
| `_mark` | L192-194 | 3 | 2 | 0 | 2 | ✓ |
| `diagnose_env` | L33-43 | 11 | 1 | 0 | 0 | ✓ |
| `_print_header` | L46-50 | 5 | 1 | 0 | 1 | ✓ |
| `_print_config_section` | L64-69 | 6 | 1 | 0 | 0 | ✓ |
| `_get_unapplied_migrations` | L110-120 | 11 | 1 | 0 | 0 | ✓ |
| `_collect_data_summary` | L173-189 | 17 | 1 | 0 | 0 | ✓ |

**全部问题 (14)**

- ❌ L89: 未处理的易出错调用
- ❌ L137: 未处理的易出错调用
- ❌ L138: 未处理的易出错调用
- ❌ L141: 未处理的易出错调用
- 🏷️ `_print_header()` L46: "_print_header" - snake_case
- 🏷️ `_print_directory_section()` L53: "_print_directory_section" - snake_case
- 🏷️ `_print_config_section()` L64: "_print_config_section" - snake_case
- 🏷️ `_print_database_section()` L72: "_print_database_section" - snake_case
- 🏷️ `_check_postgres()` L84: "_check_postgres" - snake_case
- 🏷️ `_print_migration_section()` L92: "_print_migration_section" - snake_case
- 🏷️ `_get_unapplied_migrations()` L110: "_get_unapplied_migrations" - snake_case
- 🏷️ `_print_dependency_section()` L123: "_print_dependency_section" - snake_case
- 🏷️ `_print_llm_section()` L131: "_print_llm_section" - snake_case
- 🏷️ `_first_configured_env()` L145: "_first_configured_env" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 5
- 认知复杂度: 平均: 3.2, 最大: 7
- 嵌套深度: 平均: 0.5, 最大: 2
- 函数长度: 平均: 9.7 行, 最大: 17 行
- 文件长度: 147 代码量 (195 总计)
- 参数数量: 平均: 0.4, 最大: 2
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 4/6 个错误被忽略 (66.7%)
- 注释比例: 2.0% (3/147)
- 命名规范: 发现 13 个违规

### 163. backend\wisdom_edu_api\settings.py

**糟糕指数: 7.79**

> 行数: 447 总计, 343 代码, 44 注释 | 函数: 6 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📋 重复问题: 1, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_config_json_dict` | L68-77 | 10 | 4 | 1 | 3 | ✓ |
| `_config_bool` | L48-55 | 8 | 3 | 1 | 3 | ✓ |
| `_env_config_bool` | L58-65 | 8 | 3 | 1 | 4 | ✓ |
| `_config_value` | L32-37 | 6 | 2 | 1 | 3 | ✓ |
| `_config_int` | L40-45 | 6 | 2 | 1 | 3 | ✓ |
| `_env_csv_list` | L80-85 | 6 | 2 | 1 | 2 | ✓ |

**全部问题 (7)**

- 📋 `_config_bool()` L48: 重复模式: _config_bool, _env_config_bool
- 🏷️ `_config_value()` L32: "_config_value" - snake_case
- 🏷️ `_config_int()` L40: "_config_int" - snake_case
- 🏷️ `_config_bool()` L48: "_config_bool" - snake_case
- 🏷️ `_env_config_bool()` L58: "_env_config_bool" - snake_case
- 🏷️ `_config_json_dict()` L68: "_config_json_dict" - snake_case
- 🏷️ `_env_csv_list()` L80: "_env_csv_list" - snake_case

**详情**:
- 循环复杂度: 平均: 2.7, 最大: 4
- 认知复杂度: 平均: 4.7, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 7.3 行, 最大: 10 行
- 文件长度: 343 代码量 (447 总计)
- 参数数量: 平均: 3.0, 最大: 4
- 代码重复: 16.7% 重复 (1/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/5 个错误被忽略 (0.0%)
- 注释比例: 12.8% (44/343)
- 命名规范: 发现 6 个违规

### 164. backend\ai_services\services\llm_resource_mixin.py

**糟糕指数: 7.73**

> 行数: 128 总计, 112 代码, 0 注释 | 函数: 3 | 类: 1

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `select_stage_test_questions` | L97-127 | 31 | 4 | 1 | 4 | ✓ |
| `recommend_internal_resources` | L62-95 | 34 | 2 | 1 | 6 | ✓ |
| `recommend_external_resources` | L16-60 | 45 | 1 | 0 | 7 | ✓ |

**全部问题 (2)**

- 📏 `recommend_external_resources()` L16: 7 参数数量
- 📏 `recommend_internal_resources()` L62: 6 参数数量

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 4
- 认知复杂度: 平均: 3.7, 最大: 6
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 36.7 行, 最大: 45 行
- 文件长度: 112 代码量 (128 总计)
- 参数数量: 平均: 5.7, 最大: 7
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/112)
- 命名规范: 无命名违规

### 165. backend\exams\teacher_helpers.py

**糟糕指数: 7.58**

> 行数: 144 总计, 111 代码, 0 注释 | 函数: 8 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_validate_exam_scores` | L21-38 | 18 | 6 | 1 | 2 | ✓ |
| `_normalize_choice_answer_set` | L58-75 | 18 | 5 | 1 | 1 | ✓ |
| `_ensure_teacher_exam_access` | L102-117 | 16 | 5 | 1 | 4 | ✓ |
| `_parse_pagination` | L41-55 | 15 | 2 | 1 | 4 | ✓ |
| `_get_exam_or_404` | L78-84 | 7 | 2 | 1 | 1 | ✓ |
| `_get_owned_exam_or_404` | L87-93 | 7 | 2 | 1 | 2 | ✓ |
| `_get_teacher_course_ids` | L96-99 | 4 | 1 | 0 | 1 | ✓ |
| `_build_exam_question_rows` | L120-131 | 12 | 1 | 0 | 3 | ✓ |

**全部问题 (9)**

- ❌ L62: 未处理的易出错调用
- 🏷️ `_validate_exam_scores()` L21: "_validate_exam_scores" - snake_case
- 🏷️ `_parse_pagination()` L41: "_parse_pagination" - snake_case
- 🏷️ `_normalize_choice_answer_set()` L58: "_normalize_choice_answer_set" - snake_case
- 🏷️ `_get_exam_or_404()` L78: "_get_exam_or_404" - snake_case
- 🏷️ `_get_owned_exam_or_404()` L87: "_get_owned_exam_or_404" - snake_case
- 🏷️ `_get_teacher_course_ids()` L96: "_get_teacher_course_ids" - snake_case
- 🏷️ `_ensure_teacher_exam_access()` L102: "_ensure_teacher_exam_access" - snake_case
- 🏷️ `_build_exam_question_rows()` L120: "_build_exam_question_rows" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 6
- 认知复杂度: 平均: 4.5, 最大: 8
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 12.1 行, 最大: 18 行
- 文件长度: 111 代码量 (144 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 0.0% (0/111)
- 命名规范: 发现 8 个违规

### 166. backend\common\responses.py

**糟糕指数: 7.58**

> 行数: 101 总计, 78 代码, 0 注释 | 函数: 7 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `api_response` | L10-46 | 37 | 8 | 1 | 6 | ✓ |
| `success_response` | L49-51 | 3 | 1 | 0 | 2 | ✓ |
| `created_response` | L54-56 | 3 | 1 | 0 | 2 | ✓ |
| `error_response` | L59-74 | 16 | 1 | 0 | 5 | ✓ |
| `not_found_response` | L77-79 | 3 | 1 | 0 | 1 | ✓ |
| `unauthorized_response` | L82-84 | 3 | 1 | 0 | 1 | ✓ |
| `forbidden_response` | L87-89 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- 📏 `api_response()` L10: 6 参数数量

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 8
- 认知复杂度: 平均: 2.3, 最大: 10
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 9.7 行, 最大: 37 行
- 文件长度: 78 代码量 (101 总计)
- 参数数量: 平均: 2.6, 最大: 6
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/78)
- 命名规范: 无命名违规

### 167. backend\common\defense_demo_accounts.py

**糟糕指数: 7.51**

> 行数: 191 总计, 174 代码, 2 注释 | 函数: 6 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_ensure_class` | L115-144 | 30 | 3 | 2 | 3 | ✓ |
| `_ensure_user` | L18-49 | 32 | 2 | 0 | 6 | ✓ |
| `ensure_defense_demo_accounts` | L71-112 | 42 | 2 | 1 | 0 | ✓ |
| `_ensure_course_only_demo_students` | L169-190 | 22 | 2 | 1 | 2 | ✓ |
| `_ensure_course` | L52-68 | 17 | 1 | 0 | 2 | ✓ |
| `_reset_course_only_student_state` | L147-166 | 20 | 1 | 0 | 2 | ✓ |

**全部问题 (6)**

- 📏 `_ensure_user()` L18: 6 参数数量
- 🏷️ `_ensure_user()` L18: "_ensure_user" - snake_case
- 🏷️ `_ensure_course()` L52: "_ensure_course" - snake_case
- 🏷️ `_ensure_class()` L115: "_ensure_class" - snake_case
- 🏷️ `_reset_course_only_student_state()` L147: "_reset_course_only_student_state" - snake_case
- 🏷️ `_ensure_course_only_demo_students()` L169: "_ensure_course_only_demo_students" - snake_case

**详情**:
- 循环复杂度: 平均: 1.8, 最大: 3
- 认知复杂度: 平均: 3.2, 最大: 7
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 27.2 行, 最大: 42 行
- 文件长度: 174 代码量 (191 总计)
- 参数数量: 平均: 2.5, 最大: 6
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/12 个错误被忽略 (0.0%)
- 注释比例: 1.1% (2/174)
- 命名规范: 发现 5 个违规

### 168. backend\learning\view_helpers.py

**糟糕指数: 7.40**

> 行数: 171 总计, 146 代码, 0 注释 | 函数: 9 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_exam_score_map` | L57-70 | 14 | 4 | 0 | 2 | ✓ |
| `_serialize_path_nodes` | L73-102 | 30 | 4 | 1 | 2 | ✓ |
| `_coerce_string_list` | L19-27 | 9 | 2 | 1 | 1 | ✓ |
| `_path_node_sort_key` | L30-37 | 8 | 2 | 0 | 1 | ✓ |
| `_clean_text_for_llm` | L40-54 | 15 | 2 | 1 | 2 | ✓ |
| `_snapshot_mastery_for_points` | L105-125 | 21 | 2 | 1 | 3 | ✓ |
| `_average_mastery` | L128-138 | 11 | 2 | 1 | 1 | ✓ |
| `_build_mastery_change_payload` | L141-170 | 30 | 2 | 1 | 2 | ✓ |
| `_get_authenticated_user` | L10-16 | 7 | 1 | 0 | 1 | ✓ |

**全部问题 (10)**

- ❌ L162: 未处理的易出错调用
- 🏷️ `_get_authenticated_user()` L10: "_get_authenticated_user" - snake_case
- 🏷️ `_coerce_string_list()` L19: "_coerce_string_list" - snake_case
- 🏷️ `_path_node_sort_key()` L30: "_path_node_sort_key" - snake_case
- 🏷️ `_clean_text_for_llm()` L40: "_clean_text_for_llm" - snake_case
- 🏷️ `_build_exam_score_map()` L57: "_build_exam_score_map" - snake_case
- 🏷️ `_serialize_path_nodes()` L73: "_serialize_path_nodes" - snake_case
- 🏷️ `_snapshot_mastery_for_points()` L105: "_snapshot_mastery_for_points" - snake_case
- 🏷️ `_average_mastery()` L128: "_average_mastery" - snake_case
- 🏷️ `_build_mastery_change_payload()` L141: "_build_mastery_change_payload" - snake_case

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 4
- 认知复杂度: 平均: 3.7, 最大: 6
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 16.1 行, 最大: 30 行
- 文件长度: 146 代码量 (171 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 0.0% (0/146)
- 命名规范: 发现 9 个违规

### 169. backend\ai_services\services\dkt_inference_support.py

**糟糕指数: 7.39**

> 行数: 201 总计, 168 代码, 0 注释 | 函数: 10 | 类: 1

**问题**: 🔄 复杂度问题: 3, 🏗️ 结构问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_public_slot_bundle` | L68-108 | 41 | 9 | 2 | 2 | ✓ |
| `collect_public_slot_target_kp_ids` | L146-169 | 24 | 9 | 3 | 3 | ✓ |
| `build_public_slot_input_sequence` | L172-200 | 29 | 8 | 3 | 3 | ✓ |
| `build_legacy_input_sequence` | L123-143 | 21 | 6 | 2 | 3 | ✓ |
| `resolve_backend_path` | L13-23 | 11 | 4 | 1 | 1 | ✓ |
| `collect_legacy_target_kp_ids` | L111-120 | 10 | 4 | 2 | 2 | ✓ |
| `coerce_optional_int` | L34-41 | 8 | 3 | 1 | 1 | ✓ |
| `resolve_metadata_path` | L26-31 | 6 | 2 | 1 | 2 | ✓ |
| `load_global_kp_mapping` | L53-58 | 6 | 1 | 0 | 0 | ✓ |
| `stable_slot_index` | L61-65 | 5 | 1 | 0 | 2 | ✓ |

**全部问题 (5)**

- 🔄 `build_public_slot_bundle()` L68: 认知复杂度: 13
- 🔄 `collect_public_slot_target_kp_ids()` L146: 认知复杂度: 15
- 🔄 `build_public_slot_input_sequence()` L172: 认知复杂度: 14
- 🏗️ `collect_public_slot_target_kp_ids()` L146: 中等嵌套: 3
- 🏗️ `build_public_slot_input_sequence()` L172: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 9
- 认知复杂度: 平均: 7.7, 最大: 15
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 16.1 行, 最大: 41 行
- 文件长度: 168 代码量 (201 总计)
- 参数数量: 平均: 1.9, 最大: 3
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 2 个结构问题
- 错误处理: 0/13 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/168)
- 命名规范: 无命名违规

### 170. backend\courses\teacher_announcement_views.py

**糟糕指数: 7.26**

> 行数: 68 总计, 56 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `class_announcements` | L15-42 | 28 | 9 | 1 | 2 | ✓ |
| `announcement_detail` | L47-67 | 21 | 6 | 1 | 2 | ✓ |

**全部问题 (1)**

- ❌ L57: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.5, 最大: 9
- 认知复杂度: 平均: 9.5, 最大: 11
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 24.5 行, 最大: 28 行
- 文件长度: 56 代码量 (68 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/8 个错误被忽略 (12.5%)
- 注释比例: 0.0% (0/56)
- 命名规范: 无命名违规

### 171. backend\courses\teacher_course_helpers.py

**糟糕指数: 7.25**

> 行数: 43 总计, 35 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `extract_course_archive` | L22-33 | 12 | 5 | 2 | 1 | ✓ |
| `resolve_archive_root` | L36-42 | 7 | 4 | 1 | 1 | ✓ |

**全部问题 (2)**

- ❌ L28: 未处理的易出错调用
- ❌ L30: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 5
- 认知复杂度: 平均: 7.5, 最大: 9
- 嵌套深度: 平均: 1.5, 最大: 2
- 函数长度: 平均: 9.5 行, 最大: 12 行
- 文件长度: 35 代码量 (43 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 2/2 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/35)
- 命名规范: 无命名违规

### 172. backend\tools\knowledge.py

**糟糕指数: 7.17**

> 行数: 144 总计, 118 代码, 0 注释 | 函数: 7 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_knowledge_map` | L71-101 | 31 | 7 | 1 | 3 | ✓ |
| `import_knowledge` | L34-68 | 35 | 5 | 2 | 4 | ✓ |
| `export_knowledge_map` | L119-143 | 25 | 3 | 0 | 2 | ✓ |
| `validate_json` | L28-31 | 4 | 1 | 0 | 2 | ✓ |
| `_parse_knowledge_excel` | L104-106 | 3 | 1 | 0 | 1 | ✓ |
| `_parse_hierarchical_excel` | L109-111 | 3 | 1 | 0 | 2 | ✓ |
| `_parse_flat_excel` | L114-116 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (5)**

- ❌ L99: 未处理的易出错调用
- ❌ L100: 未处理的易出错调用
- 🏷️ `_parse_knowledge_excel()` L104: "_parse_knowledge_excel" - snake_case
- 🏷️ `_parse_hierarchical_excel()` L109: "_parse_hierarchical_excel" - snake_case
- 🏷️ `_parse_flat_excel()` L114: "_parse_flat_excel" - snake_case

**详情**:
- 循环复杂度: 平均: 2.7, 最大: 7
- 认知复杂度: 平均: 3.6, 最大: 9
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 14.9 行, 最大: 35 行
- 文件长度: 118 代码量 (144 总计)
- 参数数量: 平均: 2.1, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 2/9 个错误被忽略 (22.2%)
- 注释比例: 0.0% (0/118)
- 命名规范: 发现 3 个违规

### 173. backend\ai_services\student_rag_support.py

**糟糕指数: 7.15**

> 行数: 188 总计, 155 代码, 0 注释 | 函数: 12 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_path_constraints` | L48-54 | 7 | 4 | 1 | 3 | ✓ |
| `demo_intro_payload` | L125-130 | 6 | 3 | 1 | 2 | ✓ |
| `merge_intro_payload` | L175-182 | 8 | 3 | 1 | 2 | ✓ |
| `resolve_course` | L23-28 | 6 | 2 | 1 | 1 | ✓ |
| `plan_student_path` | L57-96 | 40 | 2 | 1 | 5 | ✓ |
| `log_path_planning_call` | L99-114 | 16 | 2 | 0 | 5 | ✓ |
| `resolve_intro_point` | L117-122 | 6 | 2 | 1 | 3 | ✓ |
| `node_intro_cache_key` | L133-135 | 3 | 2 | 0 | 4 | ✓ |
| `cached_node_intro` | L138-141 | 4 | 2 | 0 | 1 | ✓ |
| `build_node_intro_payload` | L144-172 | 29 | 2 | 1 | 5 | ✓ |
| `build_mastery_data` | L31-45 | 15 | 1 | 0 | 2 | ✓ |
| `cache_node_intro` | L185-187 | 3 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- ❌ L94: 未处理的易出错调用
- ❌ L95: 未处理的易出错调用
- ❌ L108: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 4
- 认知复杂度: 平均: 3.3, 最大: 6
- 嵌套深度: 平均: 0.6, 最大: 1
- 函数长度: 平均: 11.9 行, 最大: 40 行
- 文件长度: 155 代码量 (188 总计)
- 参数数量: 平均: 2.9, 最大: 5
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 3/7 个错误被忽略 (42.9%)
- 注释比例: 0.0% (0/155)
- 命名规范: 无命名违规

### 174. backend\knowledge\teacher_map_views.py

**糟糕指数: 7.12**

> 行数: 188 总计, 155 代码, 0 注释 | 函数: 6 | 类: 0

**问题**: 🔄 复杂度问题: 2, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `knowledge_map_import` | L61-101 | 41 | 11 | 1 | 1 | ✓ |
| `knowledge_graph_save` | L34-56 | 23 | 5 | 1 | 1 | ✓ |
| `knowledge_map_publish` | L106-124 | 19 | 4 | 1 | 1 | ✓ |
| `knowledge_map_export` | L142-167 | 26 | 3 | 1 | 1 | ✓ |
| `knowledge_map_build_rag_index` | L129-137 | 9 | 2 | 1 | 1 | ✓ |
| `knowledge_map_template` | L172-187 | 16 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 🔄 `knowledge_map_import()` L61: 复杂度: 11
- 🔄 `knowledge_map_import()` L61: 认知复杂度: 13

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 11
- 认知复杂度: 平均: 6.0, 最大: 13
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 22.3 行, 最大: 41 行
- 文件长度: 155 代码量 (188 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/155)
- 命名规范: 无命名违规

### 175. backend\common\defense_demo_progress.py

**糟糕指数: 7.11**

> 行数: 188 总计, 159 代码, 0 注释 | 函数: 11 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_coerce_mastery_after_map` | L75-91 | 17 | 8 | 2 | 1 | ✓ |
| `_question_options` | L50-63 | 14 | 4 | 2 | 1 | ✓ |
| `_activate_next_locked_node` | L13-26 | 14 | 3 | 1 | 1 | ✓ |
| `_as_object_dict` | L66-72 | 7 | 2 | 0 | 1 | ✓ |
| `_average_snapshot` | L94-102 | 9 | 2 | 1 | 1 | ✓ |
| `_build_mastery_change_payload` | L127-152 | 26 | 2 | 1 | 3 | ✓ |
| `advance_defense_demo_path` | L155-166 | 12 | 2 | 0 | 3 | ✓ |
| `_set_related_knowledge_points` | L29-37 | 9 | 1 | 0 | 2 | ✓ |
| `_question_knowledge_points` | L40-47 | 8 | 1 | 0 | 1 | ✓ |
| `_capture_mastery_snapshot` | L105-124 | 20 | 1 | 0 | 3 | ✓ |
| `complete_defense_demo_stage_test` | L169-187 | 19 | 1 | 0 | 3 | ✓ |

**全部问题 (9)**

- 🏷️ `_activate_next_locked_node()` L13: "_activate_next_locked_node" - snake_case
- 🏷️ `_set_related_knowledge_points()` L29: "_set_related_knowledge_points" - snake_case
- 🏷️ `_question_knowledge_points()` L40: "_question_knowledge_points" - snake_case
- 🏷️ `_question_options()` L50: "_question_options" - snake_case
- 🏷️ `_as_object_dict()` L66: "_as_object_dict" - snake_case
- 🏷️ `_coerce_mastery_after_map()` L75: "_coerce_mastery_after_map" - snake_case
- 🏷️ `_average_snapshot()` L94: "_average_snapshot" - snake_case
- 🏷️ `_capture_mastery_snapshot()` L105: "_capture_mastery_snapshot" - snake_case
- 🏷️ `_build_mastery_change_payload()` L127: "_build_mastery_change_payload" - snake_case

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 8
- 认知复杂度: 平均: 3.7, 最大: 12
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 14.1 行, 最大: 26 行
- 文件长度: 159 代码量 (188 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/159)
- 命名规范: 发现 9 个违规

### 176. backend\tools\db_demo_preset.py

**糟糕指数: 7.10**

> 行数: 183 总计, 159 代码, 0 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `preset_student1_demo_data` | L39-104 | 66 | 5 | 1 | 2 | ✓ |
| `preset_student1_demo_course_state` | L166-182 | 17 | 4 | 1 | 1 | ✓ |
| `persist_student1_profile_and_feedback` | L107-141 | 35 | 2 | 0 | 6 | ✓ |
| `print_student1_preset_result` | L144-155 | 12 | 1 | 0 | 4 | ✓ |
| `_preset_student1_demo_data` | L158-163 | 6 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- 📏 `preset_student1_demo_data()` L39: 66 代码量
- 📏 `persist_student1_profile_and_feedback()` L107: 6 参数数量
- 🏷️ `_preset_student1_demo_data()` L158: "_preset_student1_demo_data" - snake_case

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 5
- 认知复杂度: 平均: 3.4, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 27.2 行, 最大: 66 行
- 文件长度: 159 代码量 (183 总计)
- 参数数量: 平均: 3.0, 最大: 6
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/159)
- 命名规范: 发现 1 个违规

### 177. backend\common\views.py

**糟糕指数: 6.99**

> 行数: 96 总计, 86 代码, 1 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_menu` | L10-95 | 86 | 6 | 1 | 1 | ✓ |

**全部问题 (1)**

- 📏 `get_menu()` L10: 86 代码量

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 6
- 认知复杂度: 平均: 8.0, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 86.0 行, 最大: 86 行
- 文件长度: 86 代码量 (96 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 1.2% (1/86)
- 命名规范: 无命名违规

### 178. backend\tools\neo4j_tools.py

**糟糕指数: 6.95**

> 行数: 144 总计, 108 代码, 1 注释 | 函数: 7 | 类: 0

**问题**: 📋 重复问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `neo4j_clear` | L60-80 | 21 | 6 | 2 | 2 | ✓ |
| `import_neo4j_test_data` | L100-122 | 23 | 5 | 1 | 0 | ✓ |
| `neo4j_status` | L30-40 | 11 | 4 | 1 | 0 | ✓ |
| `clear_neo4j_data` | L125-143 | 19 | 4 | 2 | 1 | ✓ |
| `sync_neo4j` | L14-27 | 14 | 3 | 1 | 1 | ✓ |
| `neo4j_sync_all` | L43-57 | 15 | 3 | 1 | 0 | ✓ |
| `test_neo4j_connection` | L85-97 | 13 | 3 | 1 | 0 | ✓ |

**全部问题 (1)**

- 📋 `neo4j_status()` L30: 重复模式: neo4j_status, test_neo4j_connection

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 6
- 认知复杂度: 平均: 6.6, 最大: 10
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 16.6 行, 最大: 23 行
- 文件长度: 108 代码量 (144 总计)
- 参数数量: 平均: 0.6, 最大: 2
- 代码重复: 14.3% 重复 (1/7)
- 结构分析: 0 个结构问题
- 错误处理: 0/17 个错误被忽略 (0.0%)
- 注释比例: 0.9% (1/108)
- 命名规范: 无命名违规

### 179. backend\exams\student_feedback_views.py

**糟糕指数: 6.81**

> 行数: 87 总计, 73 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_feedback_report` | L20-71 | 52 | 9 | 1 | 1 | ✓ |
| `get_feedback_report` | L76-86 | 11 | 4 | 1 | 2 | ✓ |

**全部问题 (1)**

- 📏 `generate_feedback_report()` L20: 52 代码量

**详情**:
- 循环复杂度: 平均: 6.5, 最大: 9
- 认知复杂度: 平均: 8.5, 最大: 11
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 31.5 行, 最大: 52 行
- 文件长度: 73 代码量 (87 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/6 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/73)
- 命名规范: 无命名违规

### 180. frontend\src\views\student\useExamTaking.js

**糟糕指数: 6.77**

> 行数: 260 总计, 230 代码, 0 注释 | 函数: 15 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `restoreProgress` | L50-68 | 19 | 6 | 2 | 0 | ✗ |
| `submitExam` | L180-204 | 25 | 5 | 1 | 0 | ✗ |
| `loadExamData` | L75-104 | 29 | 4 | 1 | 0 | ✗ |
| `submitCurrentAnswers` | L161-178 | 18 | 3 | 1 | 0 | ✗ |
| `isAnswered` | L36-40 | 5 | 2 | 1 | 1 | ✗ |
| `startTimer` | L106-119 | 4 | 2 | 1 | 0 | ✗ |
| `prevQuestion` | L121-123 | 3 | 2 | 1 | 0 | ✗ |
| `nextQuestion` | L125-131 | 7 | 2 | 1 | 0 | ✗ |
| `navigateToFeedback` | L148-159 | 12 | 2 | 1 | 0 | ✗ |
| `forceSubmitExam` | L206-218 | 13 | 2 | 0 | 0 | ✗ |
| `handleBeforeUnload` | L220-227 | 8 | 2 | 1 | 1 | ✗ |
| `useExamTaking` | L18-259 | 57 | 1 | 0 | 0 | ✗ |
| `clearProgress` | L70-73 | 4 | 1 | 0 | 0 | ✗ |
| `goToQuestion` | L133-135 | 3 | 1 | 0 | 1 | ✗ |
| `buildAnswersDict` | L137-146 | 4 | 1 | 0 | 0 | ✗ |

**全部问题 (1)**

- ❌ L47: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 6
- 认知复杂度: 平均: 3.9, 最大: 10
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 14.1 行, 最大: 57 行
- 文件长度: 230 代码量 (260 总计)
- 参数数量: 平均: 0.2, 最大: 1
- 代码重复: 0.0% 重复 (0/15)
- 结构分析: 0 个结构问题
- 错误处理: 1/2 个错误被忽略 (50.0%)
- 注释比例: 0.0% (0/230)
- 命名规范: 无命名违规

### 181. frontend\src\api\index.ts

**糟糕指数: 6.72**

> 行数: 331 总计, 291 代码, 4 注释 | 函数: 12 | 类: 0

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `tryRefreshToken` | L279-317 | 39 | 9 | 3 | 0 | ✗ |
| `handleUnauthorizedResponse` | L175-220 | 35 | 7 | 1 | 3 | ✗ |
| `refreshTokenAndReplayRequest` | L222-270 | 49 | 5 | 1 | 2 | ✗ |
| `delay` | L38-40 | 2 | 1 | 0 | 1 | ✗ |
| `notifyError` | L42-44 | 3 | 1 | 0 | 1 | ✗ |
| `isAuthEntryRequest` | L46-55 | 9 | 1 | 0 | 1 | ✗ |
| `onTokenRefreshed` | L57-60 | 3 | 1 | 0 | 1 | ✗ |
| `onTokenRefreshFailed` | L62-65 | 3 | 1 | 0 | 1 | ✗ |
| `addRefreshSubscriber` | L67-69 | 3 | 1 | 0 | 1 | ✗ |
| `clearAuthTokens` | L272-277 | 6 | 1 | 0 | 0 | ✗ |
| `resetTokenRefreshState` | L319-324 | 6 | 1 | 0 | 0 | ✗ |
| `setLoggingOut` | L326-328 | 3 | 1 | 0 | 1 | ✗ |

**全部问题 (2)**

- 🏗️ `tryRefreshToken()` L279: 中等嵌套: 3
- ❌ L217: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 9
- 认知复杂度: 平均: 3.3, 最大: 15
- 嵌套深度: 平均: 0.4, 最大: 3
- 函数长度: 平均: 13.4 行, 最大: 49 行
- 文件长度: 291 代码量 (331 总计)
- 参数数量: 平均: 1.0, 最大: 3
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 1 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 1.4% (4/291)
- 命名规范: 无命名违规

### 182. backend\tools\bootstrap.py

**糟糕指数: 6.71**

> 行数: 140 总计, 118 代码, 4 注释 | 函数: 2 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_course_resources` | L101-139 | 39 | 5 | 2 | 1 | ✓ |
| `bootstrap_course_assets` | L32-95 | 64 | 2 | 1 | 6 | ✓ |

**全部问题 (2)**

- 📏 `bootstrap_course_assets()` L32: 64 代码量
- 📏 `bootstrap_course_assets()` L32: 6 参数数量

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 5
- 认知复杂度: 平均: 6.5, 最大: 9
- 嵌套深度: 平均: 1.5, 最大: 2
- 函数长度: 平均: 51.5 行, 最大: 64 行
- 文件长度: 118 代码量 (140 总计)
- 参数数量: 平均: 3.5, 最大: 6
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 3.4% (4/118)
- 命名规范: 无命名违规

### 183. backend\exams\teacher_question_views.py

**糟糕指数: 6.62**

> 行数: 164 总计, 129 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `question_list` | L16-61 | 46 | 8 | 1 | 1 | ✓ |
| `question_update` | L109-138 | 30 | 8 | 2 | 2 | ✓ |
| `question_delete` | L143-155 | 13 | 5 | 1 | 2 | ✓ |
| `question_create` | L66-104 | 39 | 4 | 1 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 8
- 认知复杂度: 平均: 8.8, 最大: 12
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 32.0 行, 最大: 46 行
- 文件长度: 129 代码量 (164 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 1/21 个错误被忽略 (4.8%)
- 注释比例: 0.0% (0/129)
- 命名规范: 无命名违规

### 184. backend\tools\api_regression_student.py

**糟糕指数: 6.62**

> 行数: 50 总计, 44 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_student_regression` | L16-49 | 34 | 1 | 0 | 5 | ✓ |

**全部问题 (1)**

- 🏷️ `_run_student_regression()` L16: "_run_student_regression" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 34.0 行, 最大: 34 行
- 文件长度: 44 代码量 (50 总计)
- 参数数量: 平均: 5.0, 最大: 5
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/44)
- 命名规范: 发现 1 个违规

### 185. backend\exams\tests.py

**糟糕指数: 6.59**

> 行数: 288 总计, 252 代码, 1 注释 | 函数: 11 | 类: 3

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_model_id` | L22-27 | 6 | 3 | 1 | 1 | ✓ |
| `test_exam_submit_should_use_question_accuracy_and_normalized_score` | L117-162 | 46 | 3 | 1 | 1 | ✗ |
| `_api_client` | L17-19 | 3 | 1 | 0 | 1 | ✓ |
| `setUp` | L31-60 | 30 | 1 | 0 | 1 | ✓ |
| `_create_exam` | L62-78 | 17 | 1 | 0 | 3 | ✗ |
| `test_exam_submit_low_score_should_not_pass` | L80-96 | 17 | 1 | 0 | 1 | ✓ |
| `test_exam_result_should_use_fallback_threshold_when_pass_score_invalid` | L98-115 | 18 | 1 | 0 | 1 | ✓ |
| `test_true_false_answer_display_should_be_human_readable` | L166-175 | 10 | 1 | 0 | 1 | ✗ |
| `setUp` | L179-228 | 50 | 1 | 0 | 1 | ✓ |
| `test_submit_should_create_pending_report_and_enqueue_worker` | L232-253 | 22 | 1 | 0 | 3 | ✗ |
| `test_get_feedback_should_return_pending_state` | L255-287 | 33 | 1 | 0 | 1 | ✗ |

**全部问题 (10)**

- 📋 `test_exam_submit_low_score_should_not_pass()` L80: 重复模式: test_exam_submit_low_score_should_not_pass, test_submit_should_create_pending_report_and_enqueue_worker
- ❌ L72: 未处理的易出错调用
- ❌ L101: 未处理的易出错调用
- ❌ L222: 未处理的易出错调用
- ❌ L263: 未处理的易出错调用
- 🏷️ `_api_client()` L17: "_api_client" - snake_case
- 🏷️ `_model_id()` L22: "_model_id" - snake_case
- 🏷️ `setUp()` L31: "setUp" - snake_case
- 🏷️ `_create_exam()` L62: "_create_exam" - snake_case
- 🏷️ `setUp()` L179: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 3
- 认知复杂度: 平均: 1.7, 最大: 5
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 22.9 行, 最大: 50 行
- 文件长度: 252 代码量 (288 总计)
- 参数数量: 平均: 1.4, 最大: 3
- 代码重复: 9.1% 重复 (1/11)
- 结构分析: 0 个结构问题
- 错误处理: 4/23 个错误被忽略 (17.4%)
- 注释比例: 0.4% (1/252)
- 命名规范: 发现 5 个违规

### 186. backend\exams\teacher_result_views.py

**糟糕指数: 6.58**

> 行数: 213 总计, 172 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `exam_student_detail` | L70-110 | 41 | 6 | 1 | 3 | ✓ |
| `teacher_exam_export` | L170-203 | 34 | 6 | 1 | 2 | ✓ |
| `exam_analysis` | L115-165 | 51 | 4 | 1 | 2 | ✓ |
| `exam_results` | L32-65 | 34 | 3 | 1 | 2 | ✓ |

**全部问题 (2)**

- 📏 `exam_analysis()` L115: 51 代码量
- ❌ L189: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 6
- 认知复杂度: 平均: 6.8, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 40.0 行, 最大: 51 行
- 文件长度: 172 代码量 (213 总计)
- 参数数量: 平均: 2.3, 最大: 3
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 0.0% (0/172)
- 命名规范: 无命名违规

### 187. backend\tools\excel_templates.py

**糟糕指数: 6.45**

> 行数: 84 总计, 74 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_template` | L13-83 | 71 | 6 | 1 | 2 | ✓ |

**全部问题 (1)**

- 📏 `generate_template()` L13: 71 代码量

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 6
- 认知复杂度: 平均: 8.0, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 71.0 行, 最大: 71 行
- 文件长度: 74 代码量 (84 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/74)
- 命名规范: 无命名违规

### 188. frontend\src\views\teacher\knowledgeManageModels.js

**糟糕指数: 6.45**

> 行数: 118 总计, 101 代码, 0 注释 | 函数: 13 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `normalizeText` | L1-5 | 5 | 3 | 1 | 1 | ✗ |
| `normalizeIdentifier` | L7-10 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeNumber` | L12-15 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeListFromPayload` | L17-17 | 1 | 2 | 0 | 1 | ✗ |
| `normalizeSearchKeyword` | L19-21 | 3 | 1 | 0 | 1 | ✗ |
| `buildDefaultKnowledgePoint` | L23-30 | 8 | 1 | 0 | 0 | ✗ |
| `normalizeKnowledgePoint` | L32-40 | 9 | 1 | 0 | 1 | ✗ |
| `buildDefaultKnowledgeRelation` | L42-49 | 8 | 1 | 0 | 0 | ✗ |
| `normalizeKnowledgeRelation` | L51-59 | 9 | 1 | 0 | 1 | ✗ |
| `normalizeKnowledgePointListPayload` | L61-64 | 3 | 1 | 0 | 1 | ✗ |
| `normalizeKnowledgeRelationListPayload` | L66-69 | 3 | 1 | 0 | 1 | ✗ |
| `normalizeRagIndexBuildResult` | L71-76 | 5 | 1 | 0 | 1 | ✗ |
| `buildKnowledgeTree` | L78-117 | 6 | 1 | 0 | 1 | ✗ |

**全部问题 (1)**

- ❌ L97: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 3
- 认知复杂度: 平均: 1.5, 最大: 5
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 5.2 行, 最大: 9 行
- 文件长度: 101 代码量 (118 总计)
- 参数数量: 平均: 0.8, 最大: 1
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/101)
- 命名规范: 无命名违规

### 189. frontend\src\views\student\useStudentKnowledgeMap.js

**糟糕指数: 6.45**

> 行数: 124 总计, 112 代码, 0 注释 | 函数: 7 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `fetchKnowledgeMap` | L43-64 | 22 | 3 | 1 | 0 | ✗ |
| `loadPointDetail` | L66-75 | 10 | 2 | 0 | 1 | ✗ |
| `handleNodeClick` | L77-80 | 4 | 2 | 1 | 1 | ✗ |
| `handleTreeNodeClick` | L82-84 | 3 | 2 | 1 | 1 | ✗ |
| `openResource` | L86-92 | 7 | 2 | 1 | 1 | ✗ |
| `goToLearning` | L94-102 | 9 | 2 | 1 | 0 | ✗ |
| `useStudentKnowledgeMap` | L14-123 | 35 | 1 | 0 | 0 | ✗ |

**全部问题 (1)**

- ❌ L88: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 3
- 认知复杂度: 平均: 3.4, 最大: 5
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 12.9 行, 最大: 35 行
- 文件长度: 112 代码量 (124 总计)
- 参数数量: 平均: 0.6, 最大: 1
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/112)
- 命名规范: 无命名违规

### 190. frontend\src\views\student\knowledgeMapModels.js

**糟糕指数: 6.45**

> 行数: 203 总计, 176 代码, 0 注释 | 函数: 17 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getMasteryColor` | L197-202 | 6 | 4 | 1 | 1 | ✗ |
| `normalizeText` | L3-7 | 5 | 3 | 1 | 1 | ✗ |
| `normalizeRate` | L16-22 | 7 | 3 | 1 | 1 | ✗ |
| `normalizeIdentifier` | L9-12 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeListFromPayload` | L14-14 | 1 | 2 | 0 | 1 | ✗ |
| `normalizeGraphRagSource` | L91-104 | 14 | 2 | 1 | 1 | ✗ |
| `normalizeTagList` | L24-29 | 5 | 1 | 0 | 1 | ✗ |
| `buildDefaultKnowledgeNode` | L31-42 | 12 | 1 | 0 | 0 | ✗ |
| `normalizeKnowledgeNode` | L44-56 | 13 | 1 | 0 | 1 | ✗ |
| `buildDefaultKnowledgeEdge` | L58-63 | 6 | 1 | 0 | 0 | ✗ |
| `normalizeKnowledgeEdge` | L65-76 | 12 | 1 | 0 | 1 | ✗ |
| `normalizeRelatedKnowledgePoint` | L78-81 | 4 | 1 | 0 | 1 | ✗ |
| `normalizeKnowledgeResource` | L83-89 | 7 | 1 | 0 | 1 | ✗ |
| `buildDefaultPointDetail` | L106-121 | 16 | 1 | 0 | 0 | ✗ |
| `normalizePointDetail` | L123-147 | 21 | 1 | 0 | 1 | ✗ |
| `buildKnowledgeTree` | L149-185 | 5 | 1 | 0 | 1 | ✗ |
| `normalizeKnowledgeMapPayload` | L187-195 | 7 | 1 | 0 | 1 | ✗ |

**全部问题 (1)**

- ❌ L165: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 4
- 认知复杂度: 平均: 2.1, 最大: 6
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 8.5 行, 最大: 21 行
- 文件长度: 176 代码量 (203 总计)
- 参数数量: 平均: 0.8, 最大: 1
- 代码重复: 0.0% 重复 (0/17)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/176)
- 命名规范: 无命名违规

### 191. backend\models\MEFKT\graph.py

**糟糕指数: 6.45**

> 行数: 149 总计, 122 代码, 0 注释 | 函数: 7 | 类: 2

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `load_compatible_state` | L30-56 | 27 | 4 | 2 | 2 | ✓ |
| `normalize_dense_adjacency` | L10-27 | 18 | 1 | 0 | 1 | ✓ |
| `__init__` | L62-70 | 9 | 1 | 0 | 3 | ✓ |
| `forward` | L72-81 | 10 | 1 | 0 | 3 | ✓ |
| `__init__` | L87-98 | 12 | 1 | 0 | 4 | ✓ |
| `encode` | L100-111 | 12 | 1 | 0 | 3 | ✓ |
| `contrastive_loss` | L113-140 | 28 | 1 | 0 | 3 | ✓ |

**全部问题 (3)**

- ❌ L100: 未处理的易出错调用
- 🏷️ `__init__()` L62: "__init__" - snake_case
- 🏷️ `__init__()` L87: "__init__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 4
- 认知复杂度: 平均: 2.0, 最大: 8
- 嵌套深度: 平均: 0.3, 最大: 2
- 函数长度: 平均: 16.6 行, 最大: 28 行
- 文件长度: 122 代码量 (149 总计)
- 参数数量: 平均: 2.7, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 0.0% (0/122)
- 命名规范: 发现 2 个违规

### 192. backend\models\DKT\KnowledgeTracing\data\readdata.py

**糟糕指数: 6.44**

> 行数: 75 总计, 57 代码, 8 注释 | 函数: 6 | 类: 1

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_load_split_data` | L24-55 | 32 | 4 | 2 | 2 | ✓ |
| `__getattr__` | L65-74 | 10 | 2 | 1 | 2 | ✓ |
| `__init__` | L11-18 | 8 | 1 | 0 | 4 | ✓ |
| `_parse_int_sequence` | L20-22 | 3 | 1 | 0 | 2 | ✓ |
| `get_train_data` | L57-59 | 3 | 1 | 0 | 1 | ✓ |
| `get_test_data` | L61-63 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (5)**

- ❌ L28: 未处理的易出错调用
- 🏷️ `__init__()` L11: "__init__" - snake_case
- 🏷️ `_parse_int_sequence()` L20: "_parse_int_sequence" - snake_case
- 🏷️ `_load_split_data()` L24: "_load_split_data" - snake_case
- 🏷️ `__getattr__()` L65: "__getattr__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.7, 最大: 4
- 认知复杂度: 平均: 2.7, 最大: 8
- 嵌套深度: 平均: 0.5, 最大: 2
- 函数长度: 平均: 9.8 行, 最大: 32 行
- 文件长度: 57 代码量 (75 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 14.0% (8/57)
- 命名规范: 发现 4 个违规

### 193. backend\common\defense_demo_environment.py

**糟糕指数: 6.43**

> 行数: 127 总计, 115 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ensure_defense_demo_environment` | L36-126 | 91 | 4 | 1 | 1 | ✓ |

**全部问题 (1)**

- 📏 `ensure_defense_demo_environment()` L36: 91 代码量

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 6.0, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 91.0 行, 最大: 91 行
- 文件长度: 115 代码量 (127 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/115)
- 命名规范: 无命名违规

### 194. backend\exams\student_initial_assessment_support.py

**糟糕指数: 6.36**

> 行数: 300 总计, 255 代码, 0 注释 | 函数: 13 | 类: 3

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `score_initial_assessment` | L102-145 | 44 | 4 | 1 | 4 | ✓ |
| `apply_kt_initial_mastery` | L200-235 | 36 | 4 | 2 | 4 | ✓ |
| `create_initial_answer_history` | L148-165 | 18 | 3 | 1 | 1 | ✓ |
| `update_question_stats` | L168-177 | 10 | 3 | 2 | 3 | ✓ |
| `update_rule_based_mastery` | L180-197 | 18 | 3 | 1 | 3 | ✓ |
| `persist_kt_predictions` | L255-282 | 28 | 3 | 2 | 4 | ✓ |
| `select_initial_questions` | L58-70 | 13 | 2 | 1 | 1 | ✓ |
| `parse_answer_question_ids` | L87-92 | 6 | 2 | 1 | 1 | ✓ |
| `build_initial_kt_history` | L238-252 | 15 | 2 | 0 | 2 | ✓ |
| `serialize_initial_questions` | L73-84 | 12 | 1 | 0 | 1 | ✓ |
| `load_answered_questions` | L95-99 | 5 | 1 | 0 | 1 | ✓ |
| `mark_initial_assessment_done` | L285-289 | 5 | 1 | 0 | 2 | ✓ |
| `build_initial_assessment_result` | L292-299 | 8 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- ❌ L152: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 4
- 认知复杂度: 平均: 4.0, 最大: 8
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 16.8 行, 最大: 44 行
- 文件长度: 255 代码量 (300 总计)
- 参数数量: 平均: 2.2, 最大: 4
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 0.0% (0/255)
- 命名规范: 无命名违规

### 195. frontend\src\api\backend.ts

**糟糕指数: 6.36**

> 行数: 109 总计, 61 代码, 36 注释 | 函数: 6 | 类: 0

**问题**: 📋 重复问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `toBackendAbsoluteUrl` | L51-64 | 14 | 6 | 1 | 1 | ✗ |
| `getRuntimeBackendOrigin` | L27-35 | 9 | 3 | 1 | 0 | ✓ |
| `getCurrentWebSocketBaseUrl` | L71-84 | 14 | 3 | 1 | 0 | ✓ |
| `buildBackendWebSocketUrl` | L92-108 | 12 | 3 | 0 | 2 | ✗ |
| `normalizeBackendOrigin` | L16-18 | 3 | 1 | 0 | 1 | ✓ |
| `isAbsoluteUrl` | L42-44 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- 📋 `getRuntimeBackendOrigin()` L27: 重复模式: getRuntimeBackendOrigin, getCurrentWebSocketBaseUrl

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 6
- 认知复杂度: 平均: 3.8, 最大: 8
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 9.2 行, 最大: 14 行
- 文件长度: 61 代码量 (109 总计)
- 参数数量: 平均: 0.8, 最大: 2
- 代码重复: 16.7% 重复 (1/6)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 59.0% (36/61)
- 命名规范: 无命名违规

### 196. backend\ai_services\services\llm_feedback_kt_mixin.py

**糟糕指数: 6.32**

> 行数: 103 总计, 86 代码, 0 注释 | 函数: 2 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_feedback_report` | L23-69 | 47 | 2 | 1 | 6 | ✓ |
| `analyze_knowledge_tracing_result` | L71-102 | 32 | 1 | 0 | 5 | ✓ |

**全部问题 (1)**

- 📏 `generate_feedback_report()` L23: 6 参数数量

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 2
- 认知复杂度: 平均: 2.5, 最大: 4
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 39.5 行, 最大: 47 行
- 文件长度: 86 代码量 (103 总计)
- 参数数量: 平均: 5.5, 最大: 6
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/86)
- 命名规范: 无命名违规

### 197. backend\learning\tests.py

**糟糕指数: 6.30**

> 行数: 321 总计, 297 代码, 0 注释 | 函数: 7 | 类: 3

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 5, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L68-124 | 57 | 2 | 1 | 1 | ✓ |
| `test_stage_test_should_return_100_point_scale_and_question_details` | L128-167 | 40 | 2 | 0 | 3 | ✓ |
| `test_refresh_learning_path_should_reinsert_low_mastery_completed_point` | L284-320 | 37 | 2 | 0 | 2 | ✓ |
| `setUp` | L17-50 | 34 | 1 | 0 | 1 | ✓ |
| `test_complete_external_resource_should_accept_string_identifier` | L52-62 | 11 | 1 | 0 | 1 | ✓ |
| `setUp` | L173-252 | 80 | 1 | 0 | 1 | ✓ |
| `test_refresh_learning_path_should_preserve_current_context` | L256-281 | 26 | 1 | 0 | 3 | ✓ |

**全部问题 (10)**

- 📏 `setUp()` L68: 57 代码量
- 📏 `setUp()` L173: 80 代码量
- ❌ L227: 未处理的易出错调用
- ❌ L233: 未处理的易出错调用
- ❌ L239: 未处理的易出错调用
- ❌ L245: 未处理的易出错调用
- ❌ L317: 未处理的易出错调用
- 🏷️ `setUp()` L17: "setUp" - snake_case
- 🏷️ `setUp()` L68: "setUp" - snake_case
- 🏷️ `setUp()` L173: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 2
- 认知复杂度: 平均: 1.7, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 40.7 行, 最大: 80 行
- 文件长度: 297 代码量 (321 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 5/28 个错误被忽略 (17.9%)
- 注释比例: 0.0% (0/297)
- 命名规范: 发现 3 个违规

### 198. backend\tools\survey.py

**糟糕指数: 6.26**

> 行数: 226 总计, 179 代码, 0 注释 | 函数: 14 | 类: 4

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_survey_questions` | L54-78 | 25 | 4 | 1 | 3 | ✓ |
| `persist_survey_questions` | L132-151 | 20 | 4 | 3 | 4 | ✓ |
| `resolve_option_score` | L202-214 | 13 | 4 | 1 | 3 | ✓ |
| `find_first_matching_column` | L104-111 | 8 | 3 | 2 | 2 | ✓ |
| `find_named_column` | L123-129 | 7 | 3 | 2 | 2 | ✓ |
| `create_question_from_row` | L154-181 | 28 | 3 | 1 | 5 | ✓ |
| `build_survey_options` | L184-199 | 16 | 3 | 2 | 2 | ✓ |
| `resolve_dimension` | L217-220 | 4 | 3 | 0 | 2 | ✓ |
| `import_pandas` | L81-88 | 8 | 2 | 1 | 0 | ✓ |
| `resolve_survey_columns` | L91-101 | 11 | 2 | 0 | 1 | ✓ |
| `resolve_option_columns` | L114-120 | 7 | 2 | 1 | 2 | ✓ |
| `iterrows` | L26-27 | 2 | 1 | 0 | 1 | ✓ |
| `read_excel` | L33-34 | 2 | 1 | 0 | 2 | ✓ |
| `import_ability_scale` | L223-225 | 3 | 1 | 0 | 2 | ✓ |

**全部问题 (2)**

- 🏗️ `persist_survey_questions()` L132: 中等嵌套: 3
- ❌ L171: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 4
- 认知复杂度: 平均: 4.6, 最大: 10
- 嵌套深度: 平均: 1.0, 最大: 3
- 函数长度: 平均: 11.0 行, 最大: 28 行
- 文件长度: 179 代码量 (226 总计)
- 参数数量: 平均: 2.2, 最大: 5
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 1 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 0.0% (0/179)
- 命名规范: 无命名违规

### 199. frontend\src\views\teacher\useTeacherExamManage.js

**糟糕指数: 6.14**

> 行数: 424 总计, 391 代码, 0 注释 | 函数: 29 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `submitExam` | L278-318 | 41 | 5 | 1 | 0 | ✗ |
| `resolvePublishClassId` | L320-338 | 18 | 5 | 1 | 0 | ✗ |
| `normalizeListFromPayload` | L54-62 | 8 | 4 | 0 | 3 | ✗ |
| `publishExam` | L340-353 | 14 | 4 | 1 | 1 | ✗ |
| `normalizeIdentifier` | L27-32 | 6 | 3 | 1 | 1 | ✗ |
| `formatDateTime` | L34-38 | 5 | 3 | 1 | 1 | ✗ |
| `mapExamStatus` | L74-78 | 5 | 3 | 1 | 1 | ✗ |
| `normalizeExamSummary` | L85-108 | 24 | 3 | 0 | 2 | ✗ |
| `ensureCourseId` | L193-198 | 6 | 3 | 1 | 0 | ✗ |
| `loadExams` | L200-219 | 19 | 3 | 1 | 0 | ✗ |
| `loadQuestionList` | L229-244 | 15 | 3 | 1 | 0 | ✗ |
| `unpublishExam` | L355-364 | 10 | 3 | 1 | 1 | ✗ |
| `deleteExam` | L366-378 | 13 | 3 | 1 | 1 | ✗ |
| `normalizeText` | L17-20 | 4 | 2 | 1 | 1 | ✗ |
| `normalizeNumber` | L22-25 | 4 | 2 | 0 | 1 | ✗ |
| `normalizePaginatedList` | L64-68 | 5 | 2 | 0 | 3 | ✗ |
| `sanitizeQuestionPreview` | L80-83 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeClassSummary` | L110-116 | 7 | 2 | 0 | 2 | ✗ |
| `normalizeQuestionSummary` | L118-132 | 15 | 2 | 0 | 2 | ✗ |
| `normalizeExamDetail` | L134-152 | 18 | 2 | 0 | 1 | ✗ |
| `loadClasses` | L221-227 | 6 | 2 | 0 | 0 | ✗ |
| `viewExam` | L246-257 | 12 | 2 | 0 | 1 | ✗ |
| `buildDefaultExamDetail` | L40-52 | 13 | 1 | 0 | 0 | ✗ |
| `examTypeLabel` | L70-70 | 1 | 1 | 0 | 1 | ✗ |
| `questionTypeName` | L71-71 | 1 | 1 | 0 | 1 | ✗ |
| `questionTagType` | L72-72 | 1 | 1 | 0 | 1 | ✗ |
| `useTeacherExamManage` | L154-423 | 69 | 1 | 0 | 0 | ✗ |
| `editExam` | L259-272 | 14 | 1 | 0 | 1 | ✗ |
| `resetCreateForm` | L274-276 | 3 | 1 | 0 | 0 | ✗ |

**全部问题 (3)**

- 📋 `normalizeListFromPayload()` L54: 重复模式: normalizeListFromPayload, normalizePaginatedList
- 📋 `mapExamStatus()` L74: 重复模式: mapExamStatus, ensureCourseId
- 📋 `normalizeExamSummary()` L85: 重复模式: normalizeExamSummary, normalizeExamDetail

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 5
- 认知复杂度: 平均: 3.2, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 12.4 行, 最大: 69 行
- 文件长度: 391 代码量 (424 总计)
- 参数数量: 平均: 0.9, 最大: 3
- 代码重复: 10.3% 重复 (3/29)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/391)
- 命名规范: 无命名违规

### 200. frontend\src\views\student\taskLearningModels.js

**糟糕指数: 5.96**

> 行数: 308 总计, 270 代码, 0 注释 | 函数: 34 | 类: 0

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `formatStageAnswer` | L293-307 | 13 | 10 | 2 | 1 | ✗ |
| `normalizeBoolean` | L21-30 | 10 | 6 | 2 | 1 | ✗ |
| `formatDuration` | L49-58 | 10 | 5 | 1 | 1 | ✗ |
| `normalizeResourcePayload` | L162-185 | 24 | 4 | 0 | 1 | ✗ |
| `normalizeText` | L3-7 | 5 | 3 | 1 | 1 | ✗ |
| `normalizeNumber` | L11-14 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeNullableNumber` | L16-19 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeObjectFromPayload` | L32-34 | 3 | 2 | 0 | 1 | ✗ |
| `normalizeListFromPayload` | L36-36 | 1 | 2 | 0 | 1 | ✗ |
| `normalizePercentValue` | L44-47 | 4 | 2 | 0 | 1 | ✗ |
| `isEmptyStageAnswer` | L60-63 | 4 | 2 | 1 | 1 | ✗ |
| `normalizeDifficultyLevel` | L131-134 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeStageTestResultPayload` | L256-274 | 19 | 2 | 1 | 1 | ✗ |
| `normalizeIdentifier` | L9-9 | 1 | 1 | 0 | 1 | ✗ |
| `normalizeStringList` | L38-42 | 4 | 1 | 0 | 1 | ✗ |
| `buildDefaultTaskModel` | L65-71 | 7 | 1 | 0 | 0 | ✗ |
| `buildDefaultResourceModel` | L73-85 | 13 | 1 | 0 | 0 | ✗ |
| `buildDefaultNodeIntroModel` | L87-92 | 6 | 1 | 0 | 0 | ✗ |
| `buildDefaultNodeExamModel` | L94-99 | 6 | 1 | 0 | 0 | ✗ |
| `buildDefaultNodeQuizResultModel` | L101-105 | 5 | 1 | 0 | 0 | ✗ |
| `buildDefaultStageFeedbackReportModel` | L107-114 | 8 | 1 | 0 | 0 | ✗ |
| `buildDefaultStageTestResultModel` | L116-129 | 14 | 1 | 0 | 0 | ✗ |
| `normalizeTaskPayload` | L136-145 | 10 | 1 | 0 | 3 | ✗ |
| `normalizeNodeIntroPayload` | L147-155 | 9 | 1 | 0 | 1 | ✗ |
| `normalizeResourceType` | L157-160 | 4 | 1 | 0 | 1 | ✗ |
| `normalizeNodeExamPayload` | L187-196 | 10 | 1 | 0 | 1 | ✗ |
| `normalizeStageQuestionOptionPayload` | L198-207 | 10 | 1 | 0 | 2 | ✗ |
| `normalizeStageQuestionPayload` | L209-219 | 10 | 1 | 0 | 1 | ✗ |
| `normalizeStageFeedbackReportPayload` | L221-231 | 11 | 1 | 0 | 1 | ✗ |
| `normalizeStageMasteryChangePayload` | L233-241 | 9 | 1 | 0 | 1 | ✗ |
| `normalizeStageMistakePayload` | L243-254 | 12 | 1 | 0 | 1 | ✗ |
| `buildStageTestAnswers` | L276-281 | 2 | 1 | 0 | 1 | ✗ |
| `getDifficultyTagType` | L283-286 | 4 | 1 | 0 | 1 | ✗ |
| `getDifficultyLabel` | L288-291 | 4 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.9, 最大: 10
- 认知复杂度: 平均: 2.4, 最大: 14
- 嵌套深度: 平均: 0.2, 最大: 2
- 函数长度: 平均: 7.8 行, 最大: 24 行
- 文件长度: 270 代码量 (308 总计)
- 参数数量: 平均: 0.9, 最大: 3
- 代码重复: 0.0% 重复 (0/34)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/270)
- 命名规范: 无命名违规

### 201. backend\users\teacher_views.py

**糟糕指数: 5.90**

> 行数: 78 总计, 60 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_student_profile_detail` | L23-51 | 29 | 5 | 1 | 2 | ✓ |
| `teacher_refresh_student_profile` | L56-77 | 22 | 5 | 1 | 2 | ✓ |

**全部问题 (1)**

- ❌ L42: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 5
- 认知复杂度: 平均: 7.0, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 25.5 行, 最大: 29 行
- 文件长度: 60 代码量 (78 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/2 个错误被忽略 (50.0%)
- 注释比例: 0.0% (0/60)
- 命名规范: 无命名违规

### 202. backend\platform_ai\rag\student_utils.py

**糟糕指数: 5.77**

> 行数: 193 总计, 154 代码, 0 注释 | 函数: 15 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `to_int` | L18-34 | 17 | 7 | 2 | 2 | ✓ |
| `to_float` | L37-51 | 15 | 6 | 2 | 2 | ✓ |
| `humanize_document_title` | L146-160 | 15 | 6 | 1 | 1 | ✓ |
| `bundle_query_modes` | L107-120 | 14 | 5 | 2 | 2 | ✓ |
| `ordered_unique` | L59-72 | 14 | 4 | 2 | 2 | ✓ |
| `bundle_sources` | L88-97 | 10 | 4 | 2 | 1 | ✓ |
| `bundle_mode` | L100-104 | 5 | 3 | 1 | 2 | ✓ |
| `normalize_nonempty_string` | L75-78 | 4 | 2 | 0 | 1 | ✓ |
| `normalize_positive_int` | L81-85 | 5 | 2 | 1 | 1 | ✓ |
| `bundle_positive_ints` | L123-128 | 6 | 2 | 1 | 2 | ✓ |
| `append_internal_resource` | L163-183 | 21 | 2 | 0 | 5 | ✓ |
| `model_pk` | L54-56 | 3 | 1 | 0 | 1 | ✓ |
| `dedupe_strings` | L131-133 | 3 | 1 | 0 | 1 | ✓ |
| `dedupe_ints` | L136-138 | 3 | 1 | 0 | 1 | ✓ |
| `sanitize_answer_text` | L141-143 | 3 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.1, 最大: 7
- 认知复杂度: 平均: 5.0, 最大: 11
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 9.2 行, 最大: 21 行
- 文件长度: 154 代码量 (193 总计)
- 参数数量: 平均: 1.7, 最大: 5
- 代码重复: 0.0% 重复 (0/15)
- 结构分析: 0 个结构问题
- 错误处理: 0/6 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/154)
- 命名规范: 无命名违规

### 203. backend\tools\api_regression_admin.py

**糟糕指数: 5.77**

> 行数: 88 总计, 66 代码, 10 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 2, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_admin_regression` | L24-82 | 59 | 2 | 1 | 5 | ✓ |

**全部问题 (2)**

- 📏 `_run_admin_regression()` L24: 59 代码量
- 🏷️ `_run_admin_regression()` L24: "_run_admin_regression" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 59.0 行, 最大: 59 行
- 文件长度: 66 代码量 (88 总计)
- 参数数量: 平均: 5.0, 最大: 5
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 15.2% (10/66)
- 命名规范: 发现 1 个违规

### 204. backend\users\admin_helpers.py

**糟糕指数: 5.67**

> 行数: 24 总计, 18 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_parse_pagination` | L10-23 | 14 | 2 | 1 | 4 | ✓ |

**全部问题 (1)**

- 🏷️ `_parse_pagination()` L10: "_parse_pagination" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 14.0 行, 最大: 14 行
- 文件长度: 18 代码量 (24 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/18)
- 命名规范: 发现 1 个违规

### 205. backend\users\backends.py

**糟糕指数: 5.64**

> 行数: 64 总计, 49 代码, 3 注释 | 函数: 1 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `authenticate` | L26-63 | 38 | 8 | 1 | 4 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 8.0, 最大: 8
- 认知复杂度: 平均: 10.0, 最大: 10
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 38.0 行, 最大: 38 行
- 文件长度: 49 代码量 (64 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 6.1% (3/49)
- 命名规范: 无命名违规

### 206. backend\exams\student_artifact_views.py

**糟糕指数: 5.54**

> 行数: 83 总计, 66 代码, 0 注释 | 函数: 3 | 类: 0

**问题**: ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `exam_download` | L58-82 | 25 | 6 | 1 | 2 | ✓ |
| `exam_answer_sheet` | L20-37 | 18 | 4 | 1 | 2 | ✓ |
| `exam_retake` | L42-53 | 12 | 3 | 1 | 2 | ✓ |

**全部问题 (2)**

- ❌ L52: 未处理的易出错调用
- ❌ L71: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 6
- 认知复杂度: 平均: 6.3, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 18.3 行, 最大: 25 行
- 文件长度: 66 代码量 (83 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 2/6 个错误被忽略 (33.3%)
- 注释比例: 0.0% (0/66)
- 命名规范: 无命名违规

### 207. backend\users\test_profile.py

**糟糕指数: 5.48**

> 行数: 116 总计, 97 代码, 0 注释 | 函数: 5 | 类: 2

**问题**: ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L20-26 | 7 | 1 | 0 | 1 | ✓ |
| `test_update_habit_preference` | L28-40 | 13 | 1 | 0 | 1 | ✓ |
| `test_get_profile` | L42-50 | 9 | 1 | 0 | 1 | ✓ |
| `setUp` | L56-91 | 36 | 1 | 0 | 1 | ✓ |
| `test_generate_profile_for_course_should_reuse_cached_summary` | L95-115 | 21 | 1 | 0 | 3 | ✓ |

**全部问题 (4)**

- ❌ L78: 未处理的易出错调用
- ❌ L84: 未处理的易出错调用
- 🏷️ `setUp()` L20: "setUp" - snake_case
- 🏷️ `setUp()` L56: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 17.2 行, 最大: 36 行
- 文件长度: 97 代码量 (116 总计)
- 参数数量: 平均: 1.4, 最大: 3
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 2/7 个错误被忽略 (28.6%)
- 注释比例: 0.0% (0/97)
- 命名规范: 发现 2 个违规

### 208. backend\ai_services\services\llm_response_support.py

**糟糕指数: 5.47**

> 行数: 146 总计, 116 代码, 0 注释 | 函数: 12 | 类: 0

**问题**: 📋 重复问题: 1, 🏗️ 结构问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `format_input_data` | L10-24 | 15 | 5 | 3 | 2 | ✓ |
| `merge_missing_fields` | L108-114 | 7 | 5 | 2 | 2 | ✓ |
| `clean_response_list` | L135-145 | 11 | 5 | 3 | 1 | ✓ |
| `parse_json_response` | L39-53 | 15 | 4 | 1 | 1 | ✓ |
| `coerce_message_text` | L84-95 | 12 | 4 | 1 | 1 | ✓ |
| `parse_json_object` | L56-62 | 7 | 3 | 1 | 1 | ✓ |
| `parse_fenced_json` | L65-72 | 8 | 3 | 2 | 1 | ✓ |
| `parse_embedded_json` | L75-81 | 7 | 3 | 1 | 1 | ✓ |
| `clean_response_value` | L126-132 | 7 | 3 | 1 | 1 | ✓ |
| `strip_reasoning_blocks` | L27-36 | 10 | 2 | 1 | 1 | ✓ |
| `build_retry_prompt` | L98-105 | 8 | 2 | 1 | 2 | ✓ |
| `post_process_response` | L117-123 | 7 | 2 | 0 | 2 | ✓ |

**全部问题 (3)**

- 📋 `merge_missing_fields()` L108: 重复模式: merge_missing_fields, clean_response_list
- 🏗️ `format_input_data()` L10: 中等嵌套: 3
- 🏗️ `clean_response_list()` L135: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 3.4, 最大: 5
- 认知复杂度: 平均: 6.3, 最大: 11
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 9.5 行, 最大: 15 行
- 文件长度: 116 代码量 (146 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 8.3% 重复 (1/12)
- 结构分析: 2 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/116)
- 命名规范: 无命名违规

### 209. backend\tools\course_cleanup.py

**糟糕指数: 5.34**

> 行数: 42 总计, 34 代码, 2 注释 | 函数: 1 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `delete_course_with_cleanup` | L11-42 | 32 | 4 | 2 | 2 | ✓ |

**全部问题 (1)**

- ❌ L26: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 8.0, 最大: 8
- 嵌套深度: 平均: 2.0, 最大: 2
- 函数长度: 平均: 32.0 行, 最大: 32 行
- 文件长度: 34 代码量 (42 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 5.9% (2/34)
- 命名规范: 无命名违规

### 210. backend\models\DKT\KnowledgeTracing\evaluation\eval.py

**糟糕指数: 5.34**

> 行数: 163 总计, 112 代码, 24 注释 | 函数: 9 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 2, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_epoch` | L104-126 | 23 | 5 | 4 | 2 | ✓ |
| `forward` | L72-86 | 15 | 4 | 3 | 3 | ✓ |
| `train_epoch` | L89-101 | 13 | 2 | 1 | 4 | ✓ |
| `train` | L129-134 | 6 | 2 | 1 | 4 | ✓ |
| `test` | L137-149 | 13 | 2 | 1 | 2 | ✓ |
| `__getattr__` | L157-162 | 6 | 2 | 1 | 1 | ✓ |
| `performance` | L15-43 | 29 | 1 | 0 | 2 | ✓ |
| `_extract_student_predictions` | L46-62 | 17 | 1 | 0 | 3 | ✓ |
| `__init__` | L68-70 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (7)**

- 🔄 `test_epoch()` L104: 认知复杂度: 13
- 🔄 `test_epoch()` L104: 嵌套深度: 4
- 🏗️ `forward()` L72: 中等嵌套: 3
- 🏗️ `test_epoch()` L104: 中等嵌套: 4
- 🏷️ `_extract_student_predictions()` L46: "_extract_student_predictions" - snake_case
- 🏷️ `__init__()` L68: "__init__" - snake_case
- 🏷️ `__getattr__()` L157: "__getattr__" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 5
- 认知复杂度: 平均: 4.7, 最大: 13
- 嵌套深度: 平均: 1.2, 最大: 4
- 函数长度: 平均: 13.9 行, 最大: 29 行
- 文件长度: 112 代码量 (163 总计)
- 参数数量: 平均: 2.4, 最大: 4
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 2 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 21.4% (24/112)
- 命名规范: 发现 3 个违规

### 211. backend\learning\node_progress_views.py

**糟糕指数: 5.25**

> 行数: 298 总计, 238 代码, 8 注释 | 函数: 8 | 类: 0

**问题**: ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_ai_resources` | L192-236 | 45 | 8 | 1 | 2 | ✓ |
| `get_learning_progress` | L15-64 | 50 | 6 | 1 | 1 | ✓ |
| `start_learning_node` | L69-95 | 27 | 4 | 1 | 2 | ✓ |
| `complete_path_node` | L100-135 | 36 | 4 | 2 | 2 | ✓ |
| `get_node_exams` | L241-266 | 26 | 4 | 1 | 2 | ✓ |
| `skip_path_node` | L140-169 | 30 | 3 | 1 | 2 | ✓ |
| `pause_node_resource` | L271-297 | 27 | 3 | 1 | 3 | ✓ |
| `get_node_resources` | L174-187 | 14 | 2 | 1 | 2 | ✓ |

**全部问题 (2)**

- ❌ L232: 未处理的易出错调用
- ❌ L233: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 8
- 认知复杂度: 平均: 6.5, 最大: 10
- 嵌套深度: 平均: 1.1, 最大: 2
- 函数长度: 平均: 31.9 行, 最大: 50 行
- 文件长度: 238 代码量 (298 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 2/10 个错误被忽略 (20.0%)
- 注释比例: 3.4% (8/238)
- 命名规范: 无命名违规

### 212. frontend\src\views\student\feedbackReportModels.js

**糟糕指数: 5.23**

> 行数: 180 总计, 163 代码, 0 注释 | 函数: 14 | 类: 0

**问题**: 📋 重复问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `formatAnswer` | L170-179 | 10 | 8 | 2 | 1 | ✗ |
| `normalizeText` | L11-19 | 9 | 4 | 1 | 1 | ✗ |
| `normalizeIdentifier` | L26-31 | 6 | 3 | 1 | 1 | ✗ |
| `normalizeTaskText` | L121-128 | 8 | 3 | 1 | 1 | ✗ |
| `normalizeAiFeedbackPayload` | L139-168 | 26 | 3 | 0 | 1 | ✗ |
| `normalizeNumber` | L21-24 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeListFromPayload` | L33-35 | 3 | 2 | 0 | 1 | ✗ |
| `normalizeQuestionDetails` | L90-95 | 5 | 2 | 0 | 1 | ✗ |
| `normalizeExamResultPayload` | L97-119 | 22 | 2 | 0 | 1 | ✗ |
| `buildDefaultExamResult` | L37-48 | 12 | 1 | 0 | 0 | ✗ |
| `buildDefaultAiAnalysis` | L50-59 | 10 | 1 | 0 | 0 | ✗ |
| `normalizeReviewOption` | L61-72 | 12 | 1 | 0 | 2 | ✗ |
| `normalizeQuestionDetail` | L74-88 | 12 | 1 | 0 | 2 | ✗ |
| `normalizeMasteryChange` | L130-137 | 8 | 1 | 0 | 2 | ✗ |

**全部问题 (1)**

- 📋 `normalizeReviewOption()` L61: 重复模式: normalizeReviewOption, normalizeQuestionDetails

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 8
- 认知复杂度: 平均: 3.1, 最大: 12
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 10.5 行, 最大: 26 行
- 文件长度: 163 代码量 (180 总计)
- 参数数量: 平均: 1.1, 最大: 2
- 代码重复: 7.1% 重复 (1/14)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/163)
- 命名规范: 无命名违规

### 213. frontend\src\stores\user.ts

**糟糕指数: 5.16**

> 行数: 330 总计, 188 代码, 98 注释 | 函数: 13 | 类: 0

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `init` | L277-299 | 23 | 5 | 2 | 0 | ✓ |
| `fetchMenu` | L262-271 | 10 | 4 | 0 | 0 | ✓ |
| `getStorage` | L21-25 | 5 | 3 | 1 | 0 | ✗ |
| `login` | L123-141 | 19 | 3 | 0 | 1 | ✓ |
| `fetchUserInfo` | L195-213 | 19 | 3 | 1 | 0 | ✓ |
| `buildSessionPayload` | L58-69 | 12 | 2 | 0 | 1 | ✗ |
| `applySessionPayload` | L75-93 | 19 | 2 | 1 | 2 | ✗ |
| `register` | L148-164 | 17 | 2 | 0 | 1 | ✓ |
| `updateProfile` | L220-234 | 15 | 2 | 0 | 1 | ✓ |
| `setToken` | L239-248 | 10 | 2 | 1 | 2 | ✓ |
| `clearPersistedAuthState` | L46-52 | 3 | 1 | 0 | 0 | ✗ |
| `logout` | L170-188 | 14 | 1 | 0 | 0 | ✓ |
| `setUserInfo` | L253-256 | 4 | 1 | 0 | 1 | ✓ |

**全部问题 (3)**

- 📋 `login()` L123: 重复模式: login, register
- ❌ L90: 未处理的易出错调用
- ❌ L255: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 5
- 认知复杂度: 平均: 3.3, 最大: 9
- 嵌套深度: 平均: 0.5, 最大: 2
- 函数长度: 平均: 13.1 行, 最大: 23 行
- 文件长度: 188 代码量 (330 总计)
- 参数数量: 平均: 0.7, 最大: 2
- 代码重复: 7.7% 重复 (1/13)
- 结构分析: 0 个结构问题
- 错误处理: 2/6 个错误被忽略 (33.3%)
- 注释比例: 52.1% (98/188)
- 命名规范: 无命名违规

### 214. backend\exams\teacher_result_support.py

**糟糕指数: 5.13**

> 行数: 154 总计, 129 代码, 0 注释 | 函数: 11 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_score_bucket` | L88-98 | 11 | 5 | 1 | 1 | ✓ |
| `is_teacher_answer_correct` | L54-66 | 13 | 3 | 1 | 3 | ✓ |
| `build_single_question_analysis` | L113-137 | 25 | 3 | 0 | 3 | ✓ |
| `is_teacher_analysis_answer_correct` | L140-148 | 9 | 3 | 1 | 3 | ✓ |
| `build_submission_result` | L9-19 | 11 | 2 | 0 | 1 | ✓ |
| `build_teacher_question_detail` | L22-44 | 23 | 2 | 0 | 2 | ✓ |
| `extract_question_answer` | L47-51 | 5 | 2 | 1 | 1 | ✓ |
| `build_score_distribution` | L74-85 | 12 | 2 | 1 | 1 | ✓ |
| `truncate_question_content` | L151-153 | 3 | 2 | 0 | 1 | ✓ |
| `normalized_answer_text` | L69-71 | 3 | 1 | 0 | 1 | ✓ |
| `build_question_analysis` | L101-110 | 10 | 1 | 0 | 2 | ✓ |

**全部问题 (1)**

- ❌ L126: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 5
- 认知复杂度: 平均: 3.3, 最大: 7
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 11.4 行, 最大: 25 行
- 文件长度: 129 代码量 (154 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 0.0% (0/129)
- 命名规范: 发现 1 个违规

### 215. backend\knowledge\teacher_helpers.py

**糟糕指数: 5.06**

> 行数: 130 总计, 98 代码, 0 注释 | 函数: 10 | 类: 2

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `parse_pagination` | L47-67 | 21 | 4 | 3 | 4 | ✓ |
| `require_point_ids` | L78-90 | 13 | 4 | 1 | 1 | ✓ |
| `extract_question_answer_text` | L101-110 | 10 | 4 | 1 | 1 | ✓ |
| `refresh_course_rag_index` | L121-129 | 9 | 2 | 1 | 1 | ✓ |
| `set` | L31-32 | 2 | 1 | 0 | 2 | ✓ |
| `add` | L38-39 | 2 | 1 | 0 | 2 | ✓ |
| `bad_request` | L42-44 | 3 | 1 | 0 | 1 | ✓ |
| `replace_knowledge_points` | L70-75 | 6 | 1 | 0 | 2 | ✓ |
| `link_knowledge_points` | L93-98 | 6 | 1 | 0 | 2 | ✓ |
| `build_csv_download_response` | L113-118 | 6 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 🏗️ `parse_pagination()` L47: 中等嵌套: 3
- ❌ L117: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 4
- 认知复杂度: 平均: 3.2, 最大: 10
- 嵌套深度: 平均: 0.6, 最大: 3
- 函数长度: 平均: 7.8 行, 最大: 21 行
- 文件长度: 98 代码量 (130 总计)
- 参数数量: 平均: 1.7, 最大: 4
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 1 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 0.0% (0/98)
- 命名规范: 无命名违规

### 216. backend\common\defense_demo_config.py

**糟糕指数: 5.00**

> 行数: 148 总计, 144 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_get_demo_assessment_preset` | L138-147 | 10 | 2 | 1 | 1 | ✓ |

**全部问题 (1)**

- 🏷️ `_get_demo_assessment_preset()` L138: "_get_demo_assessment_preset" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 10.0 行, 最大: 10 行
- 文件长度: 144 代码量 (148 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/144)
- 命名规范: 发现 1 个违规

### 217. backend\tools\api_regression.py

**糟糕指数: 5.00**

> 行数: 84 总计, 69 代码, 2 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `api_regression` | L21-84 | 64 | 6 | 1 | 3 | ✓ |

**全部问题 (1)**

- 📏 `api_regression()` L21: 64 代码量

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 6
- 认知复杂度: 平均: 8.0, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 64.0 行, 最大: 64 行
- 文件长度: 69 代码量 (84 总计)
- 参数数量: 平均: 3.0, 最大: 3
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 2.9% (2/69)
- 命名规范: 无命名违规

### 218. frontend\src\stores\course.ts

**糟糕指数: 4.94**

> 行数: 343 总计, 220 代码, 84 注释 | 函数: 17 | 类: 4

**问题**: ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `fetchCourses` | L113-139 | 26 | 6 | 1 | 1 | ✓ |
| `ensureCourse` | L276-303 | 27 | 6 | 1 | 1 | ✓ |
| `normalizeIdentifier` | L44-53 | 10 | 4 | 1 | 1 | ✗ |
| `init` | L181-198 | 18 | 4 | 2 | 0 | ✓ |
| `updateCourse` | L204-220 | 16 | 4 | 2 | 1 | ✓ |
| `normalizeText` | L55-57 | 3 | 2 | 0 | 1 | ✗ |
| `normalizeCourse` | L60-72 | 13 | 2 | 1 | 1 | ✗ |
| `selectCourse` | L146-156 | 11 | 2 | 0 | 1 | ✓ |
| `addCourse` | L226-231 | 6 | 2 | 1 | 1 | ✓ |
| `removeCourse` | L237-243 | 6 | 2 | 1 | 1 | ✓ |
| `switchCourse` | L260-269 | 9 | 2 | 1 | 2 | ✓ |
| `requireCourseId` | L310-316 | 7 | 2 | 1 | 1 | ✓ |
| `isRecord` | L40-42 | 3 | 1 | 0 | 1 | ✗ |
| `invalidateCoursesCache` | L88-90 | 3 | 1 | 0 | 0 | ✗ |
| `selectClass` | L163-165 | 3 | 1 | 0 | 1 | ✓ |
| `clearSelection` | L171-175 | 5 | 1 | 0 | 0 | ✓ |
| `setCurrentCourse` | L250-252 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- ❌ L155: 未处理的易出错调用
- ❌ L217: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 6
- 认知复杂度: 平均: 3.9, 最大: 8
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 9.9 行, 最大: 27 行
- 文件长度: 220 代码量 (343 总计)
- 参数数量: 平均: 0.9, 最大: 2
- 代码重复: 0.0% 重复 (0/17)
- 结构分析: 0 个结构问题
- 错误处理: 2/3 个错误被忽略 (66.7%)
- 注释比例: 38.2% (84/220)
- 命名规范: 无命名违规

### 219. backend\assessments\tests.py

**糟糕指数: 4.83**

> 行数: 165 总计, 149 代码, 0 注释 | 函数: 4 | 类: 2

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L16-56 | 41 | 1 | 0 | 1 | ✓ |
| `test_submit_ability_assessment_should_not_fabricate_dimension_scores` | L58-73 | 16 | 1 | 0 | 1 | ✓ |
| `setUp` | L79-133 | 55 | 1 | 0 | 1 | ✓ |
| `test_knowledge_assessment_should_keep_mastery_conservative_and_respect_prerequisite` | L136-164 | 29 | 1 | 0 | 2 | ✓ |

**全部问题 (5)**

- 📏 `setUp()` L79: 55 代码量
- ❌ L51: 未处理的易出错调用
- ❌ L103: 未处理的易出错调用
- 🏷️ `setUp()` L16: "setUp" - snake_case
- 🏷️ `setUp()` L79: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 35.3 行, 最大: 55 行
- 文件长度: 149 代码量 (165 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 2/18 个错误被忽略 (11.1%)
- 注释比例: 0.0% (0/149)
- 命名规范: 发现 2 个违规

### 220. backend\assessments\serializers.py

**糟糕指数: 4.73**

> 行数: 144 总计, 110 代码, 0 注释 | 函数: 8 | 类: 8

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_clean_options` | L20-31 | 12 | 7 | 2 | 1 | ✓ |
| `_clean_html` | L12-17 | 6 | 3 | 1 | 1 | ✓ |
| `get_points` | L47-49 | 3 | 1 | 0 | 1 | ✓ |
| `to_representation` | L51-57 | 7 | 1 | 0 | 2 | ✓ |
| `get_points` | L71-73 | 3 | 1 | 0 | 1 | ✓ |
| `get_points` | L88-91 | 4 | 1 | 0 | 1 | ✓ |
| `get_points` | L114-116 | 3 | 1 | 0 | 1 | ✓ |
| `to_representation` | L118-123 | 6 | 1 | 0 | 2 | ✓ |

**全部问题 (2)**

- 🏷️ `_clean_html()` L12: "_clean_html" - snake_case
- 🏷️ `_clean_options()` L20: "_clean_options" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 7
- 认知复杂度: 平均: 2.8, 最大: 11
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 5.5 行, 最大: 12 行
- 文件长度: 110 代码量 (144 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 0/5 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/110)
- 命名规范: 发现 2 个违规

### 221. frontend\src\views\teacher\useTeacherQuestionList.js

**糟糕指数: 4.70**

> 行数: 338 总计, 300 代码, 0 注释 | 函数: 17 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `saveQuestion` | L215-266 | 47 | 8 | 1 | 0 | ✗ |
| `loadQuestions` | L82-114 | 33 | 6 | 1 | 0 | ✗ |
| `handleImportFile` | L131-158 | 28 | 4 | 1 | 1 | ✗ |
| `ensureCourseId` | L64-70 | 7 | 3 | 1 | 0 | ✗ |
| `loadKnowledgePoints` | L116-129 | 14 | 3 | 1 | 0 | ✗ |
| `deleteQuestion` | L268-279 | 12 | 3 | 1 | 1 | ✗ |
| `editQuestion` | L184-207 | 24 | 2 | 0 | 1 | ✗ |
| `useTeacherQuestionList` | L27-337 | 74 | 1 | 0 | 0 | ✗ |
| `resetQuestionForm` | L72-74 | 3 | 1 | 0 | 0 | ✗ |
| `openCreateDialog` | L76-80 | 5 | 1 | 0 | 0 | ✗ |
| `handleQuestionSearch` | L160-163 | 4 | 1 | 0 | 0 | ✗ |
| `handleQuestionPageSizeChange` | L165-169 | 5 | 1 | 0 | 1 | ✗ |
| `handleQuestionPageChange` | L171-174 | 4 | 1 | 0 | 1 | ✗ |
| `addOption` | L176-178 | 3 | 1 | 0 | 0 | ✗ |
| `removeOption` | L180-182 | 3 | 1 | 0 | 1 | ✗ |
| `closeCreateDialog` | L209-213 | 5 | 1 | 0 | 0 | ✗ |
| `initializeQuestionPage` | L281-284 | 4 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 8
- 认知复杂度: 平均: 3.0, 最大: 10
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 16.2 行, 最大: 74 行
- 文件长度: 300 代码量 (338 总计)
- 参数数量: 平均: 0.4, 最大: 1
- 代码重复: 0.0% 重复 (0/17)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/300)
- 命名规范: 无命名违规

### 222. backend\platform_ai\rag\corpus_utils.py

**糟糕指数: 4.69**

> 行数: 57 总计, 44 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_safe_resource_url` | L33-42 | 10 | 4 | 2 | 1 | ✓ |
| `_top_themes` | L45-50 | 6 | 3 | 1 | 2 | ✓ |
| `tokenize` | L26-30 | 5 | 2 | 1 | 1 | ✓ |
| `_chapter_entity_id` | L53-56 | 4 | 2 | 0 | 1 | ✓ |

**全部问题 (3)**

- 🏷️ `_safe_resource_url()` L33: "_safe_resource_url" - snake_case
- 🏷️ `_top_themes()` L45: "_top_themes" - snake_case
- 🏷️ `_chapter_entity_id()` L53: "_chapter_entity_id" - snake_case

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 4
- 认知复杂度: 平均: 4.8, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 6.3 行, 最大: 10 行
- 文件长度: 44 代码量 (57 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/44)
- 命名规范: 发现 3 个违规

### 223. backend\users\test_auth_api.py

**糟糕指数: 4.60**

> 行数: 175 总计, 147 代码, 0 注释 | 函数: 11 | 类: 2

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_list_activation_codes` | L161-174 | 14 | 2 | 1 | 1 | ✓ |
| `test_register_student` | L14-24 | 11 | 1 | 0 | 1 | ✓ |
| `test_register_teacher_without_activation_code` | L26-34 | 9 | 1 | 0 | 1 | ✓ |
| `test_register_teacher_with_activation_code` | L36-59 | 24 | 1 | 0 | 1 | ✓ |
| `test_login` | L61-73 | 13 | 1 | 0 | 1 | ✓ |
| `test_login_wrong_password` | L75-86 | 12 | 1 | 0 | 1 | ✓ |
| `test_userinfo` | L88-100 | 13 | 1 | 0 | 1 | ✓ |
| `test_update_userinfo` | L102-121 | 20 | 1 | 0 | 1 | ✓ |
| `setUp` | L127-138 | 12 | 1 | 0 | 1 | ✓ |
| `test_generate_activation_code_as_admin` | L140-149 | 10 | 1 | 0 | 1 | ✓ |
| `test_generate_activation_code_as_student` | L151-159 | 9 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 📋 `test_login()` L61: 重复模式: test_login, test_login_wrong_password
- ❌ L166: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.1, 最大: 2
- 认知复杂度: 平均: 1.3, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 13.4 行, 最大: 24 行
- 文件长度: 147 代码量 (175 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 9.1% 重复 (1/11)
- 结构分析: 0 个结构问题
- 错误处理: 1/12 个错误被忽略 (8.3%)
- 注释比例: 0.0% (0/147)
- 命名规范: 发现 1 个违规

### 224. backend\ai_services\test_student_rag_runtime.py

**糟糕指数: 4.60**

> 行数: 180 总计, 159 代码, 0 注释 | 函数: 7 | 类: 1

**问题**: ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_runtime_materialization_should_write_qdrant_points` | L40-112 | 57 | 1 | 1 | 4 | ✓ |
| `__init__` | L51-53 | 3 | 1 | 0 | 1 | ✗ |
| `collection_exists` | L55-58 | 4 | 1 | 0 | 2 | ✓ |
| `create_collection` | L60-63 | 4 | 1 | 0 | 4 | ✓ |
| `upsert` | L65-69 | 5 | 1 | 0 | 4 | ✓ |
| `test_recommend_resources_for_node_should_return_internal_course_resources` | L115-138 | 24 | 1 | 0 | 2 | ✓ |
| `test_recommend_resources_for_node_should_fallback_to_course_local_resources` | L141-179 | 39 | 1 | 0 | 2 | ✓ |

**全部问题 (2)**

- 📏 `test_runtime_materialization_should_write_qdrant_points()` L40: 57 代码量
- 🏷️ `__init__()` L51: "__init__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.3, 最大: 3
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 19.4 行, 最大: 57 行
- 文件长度: 159 代码量 (180 总计)
- 参数数量: 平均: 2.7, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/159)
- 命名规范: 发现 1 个违规

### 225. backend\common\logging_utils.py

**糟糕指数: 4.46**

> 行数: 137 总计, 122 代码, 1 注释 | 函数: 4 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_log_message` | L122-131 | 10 | 4 | 2 | 2 | ✓ |
| `_normalize_log_value` | L102-111 | 10 | 3 | 1 | 2 | ✓ |
| `_humanize_event` | L114-119 | 6 | 3 | 1 | 1 | ✓ |
| `log_event` | L134-136 | 3 | 1 | 0 | 4 | ✓ |

**全部问题 (2)**

- 🏷️ `_normalize_log_value()` L102: "_normalize_log_value" - snake_case
- 🏷️ `_humanize_event()` L114: "_humanize_event" - snake_case

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 4
- 认知复杂度: 平均: 4.8, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 7.3 行, 最大: 10 行
- 文件长度: 122 代码量 (137 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 0.8% (1/122)
- 命名规范: 发现 2 个违规

### 226. backend\platform_ai\rag\resource_utils.py

**糟糕指数: 4.42**

> 行数: 175 总计, 141 代码, 0 注释 | 函数: 8 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ascii_resource_terms` | L71-91 | 21 | 7 | 2 | 1 | ✓ |
| `point_resource_match_terms` | L94-115 | 22 | 7 | 2 | 1 | ✓ |
| `score_resource_point_match` | L118-143 | 26 | 5 | 2 | 2 | ✓ |
| `resource_rank_key` | L146-162 | 17 | 5 | 0 | 2 | ✓ |
| `safe_resource_url` | L24-40 | 17 | 4 | 1 | 1 | ✓ |
| `dedupe_resource_terms` | L53-68 | 16 | 4 | 2 | 1 | ✓ |
| `coerce_resource_text` | L14-21 | 8 | 2 | 0 | 1 | ✓ |
| `normalize_resource_match_text` | L43-50 | 8 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.4, 最大: 7
- 认知复杂度: 平均: 6.6, 最大: 11
- 嵌套深度: 平均: 1.1, 最大: 2
- 函数长度: 平均: 16.9 行, 最大: 26 行
- 文件长度: 141 代码量 (175 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/141)
- 命名规范: 无命名违规

### 227. backend\platform_ai\rag\student_dependencies.py

**糟糕指数: 4.38**

> 行数: 22 总计, 16 代码, 0 注释 | 函数: 3 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_runtime` | L8-11 | 4 | 1 | 0 | 1 | ✓ |
| `_llm_facade` | L13-16 | 4 | 1 | 0 | 1 | ✓ |
| `_resource_mcp_service` | L18-21 | 4 | 1 | 0 | 1 | ✓ |

**全部问题 (3)**

- 🏷️ `_runtime()` L8: "_runtime" - snake_case
- 🏷️ `_llm_facade()` L13: "_llm_facade" - snake_case
- 🏷️ `_resource_mcp_service()` L18: "_resource_mcp_service" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.0 行, 最大: 4 行
- 文件长度: 16 代码量 (22 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/16)
- 命名规范: 发现 3 个违规

### 228. backend\common\defense_demo_public.py

**糟糕指数: 4.27**

> 行数: 111 总计, 91 代码, 0 注释 | 函数: 7 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_defense_demo_visible_order` | L86-110 | 25 | 7 | 1 | 2 | ✓ |
| `get_course_defense_demo_config` | L9-18 | 10 | 4 | 1 | 1 | ✓ |
| `get_defense_demo_intro_payload` | L44-59 | 16 | 4 | 1 | 2 | ✓ |
| `get_defense_demo_resource_payload` | L62-71 | 10 | 4 | 1 | 1 | ✓ |
| `get_defense_demo_stage_test_payload` | L74-83 | 10 | 4 | 1 | 1 | ✓ |
| `is_defense_demo_student` | L30-41 | 12 | 3 | 0 | 2 | ✓ |
| `is_defense_demo_primary_course` | L21-27 | 7 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- ❌ L108: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.9, 最大: 7
- 认知复杂度: 平均: 5.3, 最大: 9
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 12.9 行, 最大: 25 行
- 文件长度: 91 代码量 (111 总计)
- 参数数量: 平均: 1.4, 最大: 2
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 1/9 个错误被忽略 (11.1%)
- 注释比例: 0.0% (0/91)
- 命名规范: 无命名违规

### 229. backend\users\models.py

**糟糕指数: 4.22**

> 行数: 437 总计, 390 代码, 2 注释 | 函数: 14 | 类: 5

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `is_valid` | L252-262 | 11 | 6 | 1 | 1 | ✓ |
| `is_valid` | L172-178 | 7 | 4 | 1 | 1 | ✓ |
| `is_admin` | L90-92 | 3 | 2 | 0 | 1 | ✓ |
| `__str__` | L163-165 | 3 | 2 | 0 | 1 | ✗ |
| `use` | L180-188 | 9 | 2 | 1 | 2 | ✓ |
| `__str__` | L434-436 | 3 | 2 | 0 | 1 | ✗ |
| `__str__` | L76-77 | 2 | 1 | 0 | 1 | ✗ |
| `is_teacher` | L80-82 | 3 | 1 | 0 | 1 | ✓ |
| `is_student` | L85-87 | 3 | 1 | 0 | 1 | ✓ |
| `generate_code` | L168-170 | 3 | 1 | 0 | 0 | ✓ |
| `__str__` | L244-245 | 2 | 1 | 0 | 1 | ✗ |
| `generate_code` | L248-250 | 3 | 1 | 0 | 0 | ✓ |
| `use` | L264-267 | 4 | 1 | 0 | 1 | ✓ |
| `__str__` | L394-395 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (5)**

- 🏷️ `__str__()` L76: "__str__" - snake_case
- 🏷️ `__str__()` L163: "__str__" - snake_case
- 🏷️ `__str__()` L244: "__str__" - snake_case
- 🏷️ `__str__()` L394: "__str__" - snake_case
- 🏷️ `__str__()` L434: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.9, 最大: 6
- 认知复杂度: 平均: 2.3, 最大: 8
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 4.1 行, 最大: 11 行
- 文件长度: 390 代码量 (437 总计)
- 参数数量: 平均: 0.9, 最大: 2
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.5% (2/390)
- 命名规范: 发现 5 个违规

### 230. backend\platform_ai\rag\runtime_proxies.py

**糟糕指数: 4.17**

> 行数: 21 总计, 11 代码, 0 注释 | 函数: 2 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__getattr__` | L7-10 | 4 | 1 | 0 | 2 | ✗ |
| `FacadeGraphRAGLLM` | L16-20 | 5 | 1 | 0 | 0 | ✓ |

**全部问题 (2)**

- 🏷️ `__getattr__()` L7: "__getattr__" - snake_case
- 🏷️ `FacadeGraphRAGLLM()` L16: "FacadeGraphRAGLLM" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.5 行, 最大: 5 行
- 文件长度: 11 代码量 (21 总计)
- 参数数量: 平均: 1.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/11)
- 命名规范: 发现 2 个违规

### 231. frontend\src\views\teacher\questionListModels.js

**糟糕指数: 4.14**

> 行数: 191 总计, 162 代码, 0 注释 | 函数: 22 | 类: 0

**问题**: 📋 重复问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `normalizeText` | L31-35 | 5 | 3 | 1 | 1 | ✗ |
| `getDifficultyTagType` | L180-184 | 5 | 3 | 1 | 1 | ✗ |
| `normalizeNumber` | L39-42 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeListFromPayload` | L44-44 | 1 | 2 | 0 | 1 | ✗ |
| `normalizeQuestionOptionTextList` | L50-61 | 6 | 2 | 0 | 1 | ✗ |
| `normalizeQuestionAnswerText` | L74-79 | 6 | 2 | 1 | 1 | ✗ |
| `resolveKnowledgePointText` | L118-126 | 8 | 2 | 1 | 3 | ✗ |
| `normalizeQuestionRecord` | L128-150 | 23 | 2 | 0 | 2 | ✗ |
| `formatScoreText` | L186-190 | 5 | 2 | 0 | 1 | ✗ |
| `normalizeIdentifier` | L37-37 | 1 | 1 | 0 | 1 | ✗ |
| `normalizeQuestionType` | L46-46 | 1 | 1 | 0 | 1 | ✗ |
| `normalizeDifficulty` | L48-48 | 1 | 1 | 0 | 1 | ✗ |
| `normalizeQuestionPointIdList` | L63-72 | 4 | 1 | 0 | 1 | ✗ |
| `buildDefaultKnowledgePointOption` | L81-84 | 4 | 1 | 0 | 0 | ✗ |
| `buildDefaultQuestionRecord` | L86-99 | 14 | 1 | 0 | 0 | ✗ |
| `normalizeKnowledgePointOption` | L101-105 | 5 | 1 | 0 | 1 | ✗ |
| `extractKnowledgePointNameList` | L107-116 | 4 | 1 | 0 | 1 | ✗ |
| `normalizeQuestionListPayload` | L152-156 | 4 | 1 | 0 | 2 | ✗ |
| `normalizeKnowledgePointListPayload` | L158-161 | 3 | 1 | 0 | 1 | ✗ |
| `buildDefaultQuestionForm` | L163-172 | 10 | 1 | 0 | 0 | ✗ |
| `supportsOptions` | L174-176 | 3 | 1 | 0 | 1 | ✗ |
| `getOptionLabel` | L178-178 | 1 | 1 | 0 | 1 | ✗ |

**全部问题 (2)**

- 📋 `normalizeText()` L31: 重复模式: normalizeText, getDifficultyTagType
- 📋 `normalizeQuestionPointIdList()` L63: 重复模式: normalizeQuestionPointIdList, extractKnowledgePointNameList

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 3
- 认知复杂度: 平均: 1.9, 最大: 5
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 5.4 行, 最大: 23 行
- 文件长度: 162 代码量 (191 总计)
- 参数数量: 平均: 1.0, 最大: 3
- 代码重复: 9.1% 重复 (2/22)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/162)
- 命名规范: 无命名违规

### 232. backend\models\MEFKT\fusion.py

**糟糕指数: 4.01**

> 行数: 36 总计, 25 代码, 0 注释 | 函数: 2 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__init__` | L12-22 | 11 | 1 | 0 | 4 | ✓ |
| `forward` | L24-32 | 9 | 1 | 0 | 3 | ✓ |

**全部问题 (1)**

- 🏷️ `__init__()` L12: "__init__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 10.0 行, 最大: 11 行
- 文件长度: 25 代码量 (36 总计)
- 参数数量: 平均: 3.5, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/25)
- 命名规范: 发现 1 个违规

### 233. backend\platform_ai\rag\student_answer_mixin.py

**糟糕指数: 3.98**

> 行数: 110 总计, 98 代码, 0 注释 | 函数: 2 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `answer_graph_question` | L29-64 | 36 | 2 | 1 | 4 | ✓ |
| `answer_course_question` | L66-109 | 44 | 2 | 1 | 4 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 40.0 行, 最大: 44 行
- 文件长度: 98 代码量 (110 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/98)
- 命名规范: 无命名违规

### 234. backend\common\tests.py

**糟糕指数: 3.96**

> 行数: 156 总计, 141 代码, 0 注释 | 函数: 5 | 类: 1

**问题**: ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_course_only_students_should_stay_enrolled_without_primary_course_traces` | L131-155 | 25 | 2 | 1 | 1 | ✓ |
| `setUp` | L24-35 | 12 | 1 | 0 | 1 | ✓ |
| `test_warmup_student_should_receive_full_preset_journey` | L37-68 | 32 | 1 | 0 | 1 | ✓ |
| `test_reseeding_should_not_duplicate_demo_histories_or_paths` | L70-114 | 45 | 1 | 0 | 1 | ✓ |
| `test_primary_course_should_include_ai_demo_queries` | L116-129 | 14 | 1 | 0 | 1 | ✓ |

**全部问题 (3)**

- ❌ L122: 未处理的易出错调用
- ❌ L125: 未处理的易出错调用
- 🏷️ `setUp()` L24: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.2, 最大: 2
- 认知复杂度: 平均: 1.6, 最大: 4
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 25.6 行, 最大: 45 行
- 文件长度: 141 代码量 (156 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 2/17 个错误被忽略 (11.8%)
- 注释比例: 0.0% (0/141)
- 命名规范: 发现 1 个违规

### 235. frontend\src\api\student\ai.ts

**糟糕指数: 3.85**

> 行数: 217 总计, 73 代码, 127 注释 | 函数: 16 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `createStudentAIChatSocket` | L200-204 | 5 | 2 | 0 | 0 | ✗ |
| `getAIProfileAnalysis` | L17-22 | 6 | 1 | 0 | 2 | ✗ |
| `getAIPathPlanning` | L32-38 | 7 | 1 | 0 | 3 | ✗ |
| `getAIResourceReason` | L49-51 | 3 | 1 | 0 | 1 | ✗ |
| `getAIFeedbackReport` | L62-64 | 3 | 1 | 0 | 1 | ✗ |
| `getKnowledgeTracking` | L75-77 | 3 | 1 | 0 | 1 | ✗ |
| `getAILearningAdvice` | L85-89 | 5 | 1 | 0 | 1 | ✗ |
| `refreshProfile` | L97-101 | 5 | 1 | 0 | 1 | ✗ |
| `refreshLearningPath` | L109-113 | 5 | 1 | 0 | 1 | ✗ |
| `getAIKeyPointsReminder` | L122-127 | 6 | 1 | 0 | 2 | ✗ |
| `getAITimeScheduling` | L136-141 | 6 | 1 | 0 | 2 | ✗ |
| `compareAIAnalysis` | L152-156 | 5 | 1 | 0 | 4 | ✗ |
| `aiChat` | L168-170 | 3 | 1 | 0 | 1 | ✗ |
| `searchGraphRAG` | L180-182 | 3 | 1 | 0 | 1 | ✗ |
| `askGraphRAG` | L192-194 | 3 | 1 | 0 | 1 | ✗ |
| `getAINodeIntro` | L214-216 | 3 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.1, 最大: 2
- 认知复杂度: 平均: 1.1, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.4 行, 最大: 7 行
- 文件长度: 73 代码量 (217 总计)
- 参数数量: 平均: 1.4, 最大: 4
- 代码重复: 0.0% 重复 (0/16)
- 结构分析: 0 个结构问题
- 错误处理: 0/15 个错误被忽略 (0.0%)
- 注释比例: 174.0% (127/73)
- 命名规范: 无命名违规

### 236. backend\application\teacher\contracts.py

**糟糕指数: 3.78**

> 行数: 76 总计, 63 代码, 0 注释 | 函数: 5 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `first_present` | L8-19 | 12 | 6 | 2 | 3 | ✓ |
| `normalize_question_point_ids` | L68-75 | 8 | 3 | 1 | 1 | ✓ |
| `normalize_course_payload` | L22-37 | 16 | 2 | 1 | 1 | ✓ |
| `normalize_exam_payload` | L50-65 | 16 | 2 | 0 | 1 | ✓ |
| `normalize_class_payload` | L40-47 | 8 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 6
- 认知复杂度: 平均: 4.4, 最大: 10
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 12.0 行, 最大: 16 行
- 文件长度: 63 代码量 (76 总计)
- 参数数量: 平均: 1.4, 最大: 3
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/63)
- 命名规范: 无命名违规

### 237. backend\users\serializers.py

**糟糕指数: 3.77**

> 行数: 122 总计, 98 代码, 0 注释 | 函数: 3 | 类: 7

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `create` | L35-45 | 11 | 1 | 0 | 1 | ✓ |
| `get_token` | L52-57 | 6 | 1 | 0 | 2 | ✓ |
| `get_is_valid` | L119-121 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- ❌ L35: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 6.7 行, 最大: 11 行
- 文件长度: 98 代码量 (122 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 0.0% (0/98)
- 命名规范: 无命名违规

### 238. backend\logs\logging_setup.py

**糟糕指数: 3.75**

> 行数: 131 总计, 106 代码, 0 注释 | 函数: 3 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_debug_logger` | L88-117 | 30 | 5 | 1 | 0 | ✓ |
| `_build_operation_logger` | L71-85 | 15 | 3 | 1 | 0 | ✓ |
| `format` | L63-68 | 6 | 1 | 0 | 2 | ✓ |

**全部问题 (2)**

- 🏷️ `_build_operation_logger()` L71: "_build_operation_logger" - snake_case
- 🏷️ `_build_debug_logger()` L88: "_build_debug_logger" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 5
- 认知复杂度: 平均: 4.3, 最大: 7
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 17.0 行, 最大: 30 行
- 文件长度: 106 代码量 (131 总计)
- 参数数量: 平均: 0.7, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/106)
- 命名规范: 发现 2 个违规

### 239. backend\assessments\question_models.py

**糟糕指数: 3.75**

> 行数: 70 总计, 56 代码, 0 注释 | 函数: 2 | 类: 2

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__str__` | L42-43 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L68-69 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (2)**

- 🏷️ `__str__()` L42: "__str__" - snake_case
- 🏷️ `__str__()` L68: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 2.0 行, 最大: 2 行
- 文件长度: 56 代码量 (70 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/56)
- 命名规范: 发现 2 个违规

### 240. backend\assessments\history_models.py

**糟糕指数: 3.75**

> 行数: 79 总计, 60 代码, 0 注释 | 函数: 3 | 类: 3

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__str__` | L30-32 | 3 | 2 | 0 | 1 | ✗ |
| `__str__` | L54-55 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L77-78 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (3)**

- 🏷️ `__str__()` L30: "__str__" - snake_case
- 🏷️ `__str__()` L54: "__str__" - snake_case
- 🏷️ `__str__()` L77: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.3, 最大: 2
- 认知复杂度: 平均: 1.3, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 2.3 行, 最大: 3 行
- 文件长度: 60 代码量 (79 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/60)
- 命名规范: 发现 3 个违规

### 241. backend\ai_services\models.py

**糟糕指数: 3.75**

> 行数: 92 总计, 84 代码, 0 注释 | 函数: 1 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__str__` | L89-91 | 3 | 2 | 0 | 1 | ✗ |

**全部问题 (1)**

- 🏷️ `__str__()` L89: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 2.0, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.0 行, 最大: 3 行
- 文件长度: 84 代码量 (92 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/84)
- 命名规范: 发现 1 个违规

### 242. backend\courses\models.py

**糟糕指数: 3.73**

> 行数: 271 总计, 229 代码, 2 注释 | 函数: 9 | 类: 5

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `can_edit` | L73-88 | 16 | 6 | 1 | 2 | ✓ |
| `get_manageable_courses` | L91-99 | 9 | 3 | 1 | 2 | ✓ |
| `__str__` | L70-71 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L145-146 | 2 | 1 | 0 | 1 | ✗ |
| `get_student_count` | L148-150 | 3 | 1 | 0 | 1 | ✓ |
| `courses_list` | L153-155 | 3 | 1 | 0 | 1 | ✓ |
| `__str__` | L193-194 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L234-235 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L269-270 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (5)**

- 🏷️ `__str__()` L70: "__str__" - snake_case
- 🏷️ `__str__()` L145: "__str__" - snake_case
- 🏷️ `__str__()` L193: "__str__" - snake_case
- 🏷️ `__str__()` L234: "__str__" - snake_case
- 🏷️ `__str__()` L269: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.8, 最大: 6
- 认知复杂度: 平均: 2.2, 最大: 8
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 4.6 行, 最大: 16 行
- 文件长度: 229 代码量 (271 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.9% (2/229)
- 命名规范: 发现 5 个违规

### 243. frontend\src\views\student\useProfileView.js

**糟糕指数: 3.60**

> 行数: 327 总计, 298 代码, 0 注释 | 函数: 9 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `loadProfileData` | L158-189 | 32 | 6 | 1 | 0 | ✗ |
| `loadAISuggestions` | L191-221 | 31 | 4 | 1 | 0 | ✗ |
| `refreshAISuggestions` | L223-242 | 20 | 3 | 1 | 0 | ✗ |
| `refreshProfile` | L244-262 | 19 | 3 | 1 | 0 | ✗ |
| `disposeMasteryChart` | L105-110 | 6 | 2 | 1 | 0 | ✗ |
| `initMasteryChart` | L112-156 | 34 | 2 | 1 | 0 | ✗ |
| `handleResize` | L264-266 | 3 | 2 | 1 | 0 | ✗ |
| `useProfileView` | L21-326 | 76 | 1 | 0 | 0 | ✗ |
| `resetProfileState` | L98-103 | 6 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.7, 最大: 6
- 认知复杂度: 平均: 4.2, 最大: 8
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 25.2 行, 最大: 76 行
- 文件长度: 298 代码量 (327 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/298)
- 命名规范: 无命名违规

### 244. backend\application\teacher\workspace.py

**糟糕指数: 3.51**

> 行数: 58 总计, 51 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_course_workspace` | L13-57 | 45 | 4 | 0 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 45.0 行, 最大: 45 行
- 文件长度: 51 代码量 (58 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/51)
- 命名规范: 无命名违规

### 245. backend\assessments\assessment_models.py

**糟糕指数: 3.50**

> 行数: 111 总计, 82 代码, 0 注释 | 函数: 5 | 类: 5

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `is_all_done` | L89-91 | 3 | 3 | 0 | 1 | ✓ |
| `__str__` | L31-32 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L64-65 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L85-86 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L109-110 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (4)**

- 🏷️ `__str__()` L31: "__str__" - snake_case
- 🏷️ `__str__()` L64: "__str__" - snake_case
- 🏷️ `__str__()` L85: "__str__" - snake_case
- 🏷️ `__str__()` L109: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 3
- 认知复杂度: 平均: 1.4, 最大: 3
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 2.2 行, 最大: 3 行
- 文件长度: 82 代码量 (111 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/82)
- 命名规范: 发现 4 个违规

### 246. backend\tools.py

**糟糕指数: 3.48**

> 行数: 34 总计, 23 代码, 1 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_load_cli_main` | L27-30 | 4 | 1 | 0 | 0 | ✓ |

**全部问题 (1)**

- 🏷️ `_load_cli_main()` L27: "_load_cli_main" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.0 行, 最大: 4 行
- 文件长度: 23 代码量 (34 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 4.3% (1/23)
- 命名规范: 发现 1 个违规

### 247. backend\users\student_views.py

**糟糕指数: 3.46**

> 行数: 149 总计, 125 代码, 0 注释 | 函数: 6 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `update_student_profile` | L64-84 | 21 | 3 | 1 | 1 | ✓ |
| `profile_compare` | L114-138 | 25 | 3 | 1 | 1 | ✓ |
| `update_habit_preference` | L46-59 | 14 | 2 | 1 | 1 | ✓ |
| `get_profile_history` | L89-109 | 21 | 2 | 1 | 1 | ✓ |
| `get_profile` | L31-41 | 11 | 1 | 0 | 1 | ✓ |
| `profile_export` | L143-148 | 6 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- ❌ L107: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 3
- 认知复杂度: 平均: 3.3, 最大: 5
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 16.3 行, 最大: 25 行
- 文件长度: 125 代码量 (149 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 1/6 个错误被忽略 (16.7%)
- 注释比例: 0.0% (0/125)
- 命名规范: 无命名违规

### 248. backend\ai_services\test_web_search.py

**糟糕指数: 3.36**

> 行数: 120 总计, 103 代码, 1 注释 | 函数: 3 | 类: 1

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `side_effect` | L91-106 | 16 | 3 | 1 | 4 | ✓ |
| `test_search_with_baidu_should_resolve_redirect_and_filter_domain` | L38-76 | 39 | 1 | 0 | 2 | ✓ |
| `test_search_learning_resources_should_use_configured_engines_in_order` | L82-119 | 22 | 1 | 0 | 3 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.7, 最大: 3
- 认知复杂度: 平均: 2.3, 最大: 5
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 25.7 行, 最大: 39 行
- 文件长度: 103 代码量 (120 总计)
- 参数数量: 平均: 3.0, 最大: 4
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 1.0% (1/103)
- 命名规范: 无命名违规

### 249. backend\knowledge\models.py

**糟糕指数: 3.34**

> 行数: 333 总计, 291 代码, 1 注释 | 函数: 8 | 类: 5

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_tags_list` | L128-132 | 5 | 2 | 1 | 1 | ✓ |
| `__str__` | L117-118 | 2 | 1 | 0 | 1 | ✗ |
| `get_prerequisites` | L120-122 | 3 | 1 | 0 | 1 | ✓ |
| `get_dependents` | L124-126 | 3 | 1 | 0 | 1 | ✓ |
| `__str__` | L183-184 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L247-248 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L294-295 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L331-332 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (5)**

- 🏷️ `__str__()` L117: "__str__" - snake_case
- 🏷️ `__str__()` L183: "__str__" - snake_case
- 🏷️ `__str__()` L247: "__str__" - snake_case
- 🏷️ `__str__()` L294: "__str__" - snake_case
- 🏷️ `__str__()` L331: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.1, 最大: 2
- 认知复杂度: 平均: 1.4, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 2.6 行, 最大: 5 行
- 文件长度: 291 代码量 (333 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.3% (1/291)
- 命名规范: 发现 5 个违规

### 250. backend\exams\models.py

**糟糕指数: 3.33**

> 行数: 234 总计, 202 代码, 0 注释 | 函数: 5 | 类: 4

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `score_percent` | L157-161 | 5 | 3 | 1 | 1 | ✓ |
| `__str__` | L230-233 | 4 | 2 | 1 | 1 | ✗ |
| `__str__` | L96-97 | 2 | 1 | 0 | 1 | ✗ |
| `question_count` | L100-102 | 3 | 1 | 0 | 1 | ✓ |
| `__str__` | L153-154 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (3)**

- 🏷️ `__str__()` L96: "__str__" - snake_case
- 🏷️ `__str__()` L153: "__str__" - snake_case
- 🏷️ `__str__()` L230: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 3
- 认知复杂度: 平均: 2.4, 最大: 5
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 3.2 行, 最大: 5 行
- 文件长度: 202 代码量 (234 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/202)
- 命名规范: 发现 3 个违规

### 251. backend\platform_ai\kt\torch_device.py

**糟糕指数: 3.33**

> 行数: 63 总计, 50 代码, 0 注释 | 函数: 2 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `resolve_torch_device` | L35-63 | 29 | 5 | 1 | 1 | ✓ |
| `_parse_bool_env` | L27-32 | 6 | 2 | 1 | 2 | ✓ |

**全部问题 (1)**

- 🏷️ `_parse_bool_env()` L27: "_parse_bool_env" - snake_case

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 5
- 认知复杂度: 平均: 5.5, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 17.5 行, 最大: 29 行
- 文件长度: 50 代码量 (63 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/50)
- 命名规范: 发现 1 个违规

### 252. backend\exams\score_policy.py

**糟糕指数: 3.32**

> 行数: 69 总计, 48 代码, 0 注释 | 函数: 5 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `sum_exam_question_scores` | L20-29 | 10 | 4 | 2 | 1 | ✓ |
| `sync_exam_totals` | L39-52 | 14 | 4 | 1 | 3 | ✓ |
| `sync_course_exam_totals` | L55-68 | 14 | 3 | 1 | 2 | ✓ |
| `_to_decimal` | L16-17 | 2 | 2 | 0 | 1 | ✗ |
| `compute_exam_pass_score` | L32-36 | 5 | 2 | 0 | 2 | ✓ |

**全部问题 (1)**

- 🏷️ `_to_decimal()` L16: "_to_decimal" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 4
- 认知复杂度: 平均: 4.6, 最大: 8
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 9.0 行, 最大: 14 行
- 文件长度: 48 代码量 (69 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/48)
- 命名规范: 发现 1 个违规

### 253. frontend\src\views\student\profileModels.js

**糟糕指数: 3.28**

> 行数: 141 总计, 120 代码, 0 注释 | 函数: 16 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `normalizeBoolean` | L12-20 | 9 | 6 | 2 | 1 | ✗ |
| `getProgressColor` | L125-130 | 6 | 4 | 1 | 1 | ✗ |
| `normalizeText` | L1-5 | 5 | 3 | 1 | 1 | ✗ |
| `normalizeTextList` | L28-37 | 9 | 3 | 1 | 1 | ✗ |
| `wrapAxisLabel` | L132-140 | 9 | 3 | 1 | 1 | ✗ |
| `normalizeNumber` | L7-10 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeListFromPayload` | L22-22 | 1 | 2 | 0 | 1 | ✗ |
| `normalizeObjectFromPayload` | L24-26 | 3 | 2 | 0 | 1 | ✗ |
| `normalizePercentageValue` | L39-43 | 5 | 2 | 0 | 1 | ✗ |
| `normalizeAssessmentReadyState` | L110-123 | 11 | 2 | 0 | 2 | ✗ |
| `buildDefaultProfileSnapshot` | L45-52 | 8 | 1 | 0 | 0 | ✗ |
| `getAbilityName` | L54-68 | 15 | 1 | 0 | 1 | ✗ |
| `normalizeAbilityEntry` | L70-73 | 4 | 1 | 0 | 2 | ✗ |
| `normalizeKnowledgeMasteryEntry` | L75-79 | 5 | 1 | 0 | 1 | ✗ |
| `normalizeProfilePayload` | L81-98 | 15 | 1 | 0 | 1 | ✗ |
| `normalizeProfileSuggestionList` | L100-108 | 9 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 6
- 认知复杂度: 平均: 2.9, 最大: 10
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 7.4 行, 最大: 15 行
- 文件长度: 120 代码量 (141 总计)
- 参数数量: 平均: 1.1, 最大: 2
- 代码重复: 0.0% 重复 (0/16)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/120)
- 命名规范: 无命名违规

### 254. backend\learning\models.py

**糟糕指数: 3.28**

> 行数: 243 总计, 221 代码, 1 注释 | 函数: 5 | 类: 3

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `mastery_improvement` | L238-242 | 5 | 3 | 1 | 1 | ✓ |
| `progress_percent` | L59-65 | 7 | 2 | 1 | 1 | ✓ |
| `__str__` | L55-56 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L174-175 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L234-235 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (3)**

- 🏷️ `__str__()` L55: "__str__" - snake_case
- 🏷️ `__str__()` L174: "__str__" - snake_case
- 🏷️ `__str__()` L234: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 3
- 认知复杂度: 平均: 2.4, 最大: 5
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 3.6 行, 最大: 7 行
- 文件长度: 221 代码量 (243 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.5% (1/221)
- 命名规范: 发现 3 个违规

### 255. backend\learning\node_detail_views.py

**糟糕指数: 3.23**

> 行数: 122 总计, 103 代码, 1 注释 | 函数: 3 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `submit_node_exam` | L60-121 | 62 | 5 | 1 | 3 | ✓ |
| `get_path_node_detail` | L22-36 | 15 | 2 | 1 | 2 | ✓ |
| `complete_node_resource` | L41-55 | 15 | 2 | 1 | 3 | ✓ |

**全部问题 (1)**

- 📏 `submit_node_exam()` L60: 62 代码量

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 5
- 认知复杂度: 平均: 5.0, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 30.7 行, 最大: 62 行
- 文件长度: 103 代码量 (122 总计)
- 参数数量: 平均: 2.7, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 1.0% (1/103)
- 命名规范: 无命名违规

### 256. backend\exams\student_initial_assessment_views.py

**糟糕指数: 3.20**

> 行数: 81 总计, 67 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `initial_assessment_submit` | L49-80 | 32 | 6 | 1 | 1 | ✓ |
| `initial_assessment_start` | L26-44 | 19 | 4 | 1 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 6
- 认知复杂度: 平均: 7.0, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 25.5 行, 最大: 32 行
- 文件长度: 67 代码量 (81 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/67)
- 命名规范: 无命名违规

### 257. backend\platform_ai\search\providers.py

**糟糕指数: 3.17**

> 行数: 36 总计, 24 代码, 0 注释 | 函数: 1 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `search_learning_resources` | L19-31 | 13 | 1 | 0 | 4 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 13.0 行, 最大: 13 行
- 文件长度: 24 代码量 (36 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/24)
- 命名规范: 无命名违规

### 258. backend\exams\serializers.py

**糟糕指数: 3.14**

> 行数: 115 总计, 87 代码, 0 注释 | 函数: 3 | 类: 7

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `validate` | L83-97 | 15 | 6 | 1 | 2 | ✓ |
| `get_questions` | L37-46 | 10 | 1 | 0 | 1 | ✓ |
| `to_internal_value` | L78-81 | 4 | 1 | 0 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.7, 最大: 6
- 认知复杂度: 平均: 3.3, 最大: 8
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 9.7 行, 最大: 15 行
- 文件长度: 87 代码量 (115 总计)
- 参数数量: 平均: 1.7, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/87)
- 命名规范: 无命名违规

### 259. backend\knowledge\tests.py

**糟糕指数: 3.13**

> 行数: 75 总计, 65 代码, 0 注释 | 函数: 3 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L15-35 | 21 | 1 | 0 | 1 | ✓ |
| `test_knowledge_map_should_fail_when_neo4j_graph_missing` | L39-42 | 4 | 1 | 0 | 1 | ✓ |
| `test_knowledge_map_should_mark_data_source_as_neo4j` | L46-74 | 29 | 1 | 0 | 3 | ✓ |

**全部问题 (1)**

- 🏷️ `setUp()` L15: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 18.0 行, 最大: 29 行
- 文件长度: 65 代码量 (75 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/65)
- 命名规范: 发现 1 个违规

### 260. backend\models\DKT\KnowledgeTracing\data\DKTDataSet.py

**糟糕指数: 3.07**

> 行数: 52 总计, 30 代码, 14 注释 | 函数: 4 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `onehot` | L37-51 | 15 | 4 | 2 | 2 | ✓ |
| `__init__` | L14-19 | 6 | 1 | 0 | 3 | ✓ |
| `__len__` | L21-24 | 4 | 1 | 0 | 1 | ✓ |
| `__getitem__` | L26-34 | 9 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- 🏷️ `__init__()` L14: "__init__" - snake_case
- 🏷️ `__len__()` L21: "__len__" - snake_case
- 🏷️ `__getitem__()` L26: "__getitem__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.8, 最大: 4
- 认知复杂度: 平均: 2.8, 最大: 8
- 嵌套深度: 平均: 0.5, 最大: 2
- 函数长度: 平均: 8.5 行, 最大: 15 行
- 文件长度: 30 代码量 (52 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 46.7% (14/30)
- 命名规范: 发现 3 个违规

### 261. frontend\src\api\errors.ts

**糟糕指数: 3.04**

> 行数: 95 总计, 84 代码, 0 注释 | 函数: 8 | 类: 1

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `collectDetailMessages` | L24-43 | 15 | 6 | 1 | 2 | ✗ |
| `extractPayloadMessage` | L45-60 | 16 | 5 | 2 | 2 | ✗ |
| `extractApiErrorMessage` | L69-80 | 12 | 4 | 1 | 2 | ✗ |
| `normalizeError` | L86-94 | 9 | 3 | 1 | 1 | ✗ |
| `constructor` | L10-17 | 8 | 1 | 0 | 2 | ✗ |
| `isRecord` | L20-22 | 3 | 1 | 0 | 1 | ✗ |
| `createApiError` | L62-67 | 6 | 1 | 0 | 2 | ✗ |
| `isApiErrorHandled` | L82-84 | 3 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 6
- 认知复杂度: 平均: 4.0, 最大: 9
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 9.0 行, 最大: 16 行
- 文件长度: 84 代码量 (95 总计)
- 参数数量: 平均: 1.6, 最大: 2
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/84)
- 命名规范: 无命名违规

### 262. backend\logs\models.py

**糟糕指数: 2.92**

> 行数: 139 总计, 126 代码, 3 注释 | 函数: 1 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__str__` | L136-138 | 3 | 2 | 0 | 1 | ✗ |

**全部问题 (1)**

- 🏷️ `__str__()` L136: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 2.0, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.0 行, 最大: 3 行
- 文件长度: 126 代码量 (139 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 2.4% (3/126)
- 命名规范: 发现 1 个违规

### 263. frontend\src\views\student\useFeedbackReport.js

**糟糕指数: 2.84**

> 行数: 221 总计, 195 代码, 0 注释 | 函数: 12 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `loadAIFeedback` | L129-157 | 29 | 5 | 2 | 0 | ✗ |
| `loadFeedbackReport` | L109-127 | 19 | 4 | 1 | 0 | ✗ |
| `retryAIFeedback` | L159-176 | 18 | 3 | 1 | 0 | ✗ |
| `stopAIProgress` | L66-71 | 6 | 2 | 1 | 0 | ✗ |
| `clearPollTimer` | L93-98 | 6 | 2 | 1 | 0 | ✗ |
| `schedulePoll` | L100-107 | 4 | 2 | 1 | 0 | ✗ |
| `useFeedbackReport` | L15-220 | 59 | 1 | 0 | 0 | ✗ |
| `startAIProgress` | L73-85 | 6 | 1 | 0 | 0 | ✗ |
| `finishAIProgress` | L87-91 | 5 | 1 | 0 | 0 | ✗ |
| `goBack` | L178-180 | 3 | 1 | 0 | 0 | ✗ |
| `retryExam` | L182-184 | 3 | 1 | 0 | 0 | ✗ |
| `goToLearningPath` | L186-188 | 3 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 5
- 认知复杂度: 平均: 3.2, 最大: 9
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 13.4 行, 最大: 59 行
- 文件长度: 195 代码量 (221 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/195)
- 命名规范: 无命名违规

### 264. backend\ai_services\auth.py

**糟糕指数: 2.81**

> 行数: 53 总计, 36 代码, 3 注释 | 函数: 3 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__call__` | L27-43 | 17 | 5 | 2 | 4 | ✗ |
| `_resolve_user_from_token` | L17-21 | 5 | 1 | 0 | 1 | ✓ |
| `query_string_jwt_auth_middleware_stack` | L46-48 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 🏷️ `_resolve_user_from_token()` L17: "_resolve_user_from_token" - snake_case
- 🏷️ `__call__()` L27: "__call__" - snake_case

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 5
- 认知复杂度: 平均: 3.7, 最大: 9
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 8.3 行, 最大: 17 行
- 文件长度: 36 代码量 (53 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 8.3% (3/36)
- 命名规范: 发现 2 个违规

### 265. backend\models\DKT\KnowledgeTracing\model\RNNModel.py

**糟糕指数: 2.81**

> 行数: 45 总计, 29 代码, 10 注释 | 函数: 2 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__init__` | L13-27 | 15 | 1 | 0 | 5 | ✓ |
| `forward` | L29-44 | 16 | 1 | 0 | 2 | ✓ |

**全部问题 (1)**

- 🏷️ `__init__()` L13: "__init__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 15.5 行, 最大: 16 行
- 文件长度: 29 代码量 (45 总计)
- 参数数量: 平均: 3.5, 最大: 5
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 34.5% (10/29)
- 命名规范: 发现 1 个违规

### 266. frontend\src\views\teacher\useTeacherKnowledgeManage.js

**糟糕指数: 2.64**

> 行数: 297 总计, 256 代码, 1 注释 | 函数: 11 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `submitPointForm` | L163-202 | 40 | 4 | 1 | 0 | ✗ |
| `buildRagIndex` | L240-260 | 21 | 4 | 1 | 0 | ✗ |
| `loadAll` | L86-112 | 27 | 3 | 1 | 0 | ✗ |
| `deletePoint` | L204-216 | 13 | 3 | 1 | 1 | ✗ |
| `handleGraphSave` | L218-234 | 17 | 3 | 1 | 1 | ✗ |
| `addPoint` | L144-153 | 10 | 2 | 1 | 0 | ✗ |
| `useTeacherKnowledgeManage` | L21-296 | 67 | 1 | 0 | 0 | ✗ |
| `resetPointForm` | L57-61 | 5 | 1 | 0 | 0 | ✗ |
| `refreshStats` | L63-84 | 15 | 1 | 0 | 0 | ✗ |
| `editPoint` | L155-161 | 7 | 1 | 0 | 1 | ✗ |
| `handleNodeClick` | L236-238 | 3 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 4
- 认知复杂度: 平均: 3.3, 最大: 6
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 20.5 行, 最大: 67 行
- 文件长度: 256 代码量 (297 总计)
- 参数数量: 平均: 0.4, 最大: 1
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.4% (1/256)
- 命名规范: 无命名违规

### 267. backend\common\pagination.py

**糟糕指数: 2.52**

> 行数: 70 总计, 53 代码, 1 注释 | 函数: 3 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `parse_pagination` | L26-46 | 21 | 5 | 0 | 4 | ✓ |
| `paginate_list` | L49-66 | 18 | 3 | 0 | 3 | ✓ |
| `safe_int` | L12-23 | 12 | 2 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 5
- 认知复杂度: 平均: 4.0, 最大: 5
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 17.0 行, 最大: 21 行
- 文件长度: 53 代码量 (70 总计)
- 参数数量: 平均: 3.0, 最大: 4
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 1.9% (1/53)
- 命名规范: 无命名违规

### 268. backend\users\tests.py

**糟糕指数: 2.50**

> 行数: 2 总计, 1 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (2 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/1)
- 命名规范: 无命名违规

### 269. backend\users\apps.py

**糟糕指数: 2.50**

> 行数: 16 总计, 13 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 13 代码量 (16 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/13)
- 命名规范: 无命名违规

### 270. backend\users\admin_views.py

**糟糕指数: 2.50**

> 行数: 6 总计, 1 代码, 3 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (6 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 300.0% (3/1)
- 命名规范: 无命名违规

### 271. backend\users\admin.py

**糟糕指数: 2.50**

> 行数: 34 总计, 27 代码, 0 注释 | 函数: 0 | 类: 3

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 27 代码量 (34 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/27)
- 命名规范: 无命名违规

### 272. backend\wisdom_edu_api\wsgi.py

**糟糕指数: 2.50**

> 行数: 17 总计, 10 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 10 代码量 (17 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/10)
- 命名规范: 无命名违规

### 273. backend\wisdom_edu_api\asgi.py

**糟糕指数: 2.50**

> 行数: 24 总计, 16 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 16 代码量 (24 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/16)
- 命名规范: 无命名违规

### 274. backend\tools\rag_index.py

**糟糕指数: 2.50**

> 行数: 30 总计, 20 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_rag_index` | L10-23 | 14 | 3 | 1 | 1 | ✓ |
| `refresh_rag_corpus` | L26-29 | 4 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 3
- 认知复杂度: 平均: 3.0, 最大: 5
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 9.0 行, 最大: 14 行
- 文件长度: 20 代码量 (30 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/20)
- 命名规范: 无命名违规

### 275. backend\logs\serializers.py

**糟糕指数: 2.50**

> 行数: 37 总计, 30 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 30 代码量 (37 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/30)
- 命名规范: 无命名违规

### 276. backend\logs\apps.py

**糟糕指数: 2.50**

> 行数: 16 总计, 13 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 13 代码量 (16 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/13)
- 命名规范: 无命名违规

### 277. backend\logs\admin.py

**糟糕指数: 2.50**

> 行数: 24 总计, 19 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 19 代码量 (24 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/19)
- 命名规范: 无命名违规

### 278. backend\knowledge\views.py

**糟糕指数: 2.50**

> 行数: 5 总计, 1 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (5 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 200.0% (2/1)
- 命名规范: 无命名违规

### 279. backend\knowledge\teacher_views.py

**糟糕指数: 2.50**

> 行数: 124 总计, 116 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 116 代码量 (124 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/116)
- 命名规范: 无命名违规

### 280. backend\knowledge\apps.py

**糟糕指数: 2.50**

> 行数: 16 总计, 13 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 13 代码量 (16 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/13)
- 命名规范: 无命名违规

### 281. backend\knowledge\admin.py

**糟糕指数: 2.50**

> 行数: 45 总计, 34 代码, 0 注释 | 函数: 0 | 类: 5

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 34 代码量 (45 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/34)
- 命名规范: 无命名违规

### 282. backend\learning\stage_test_submit_views.py

**糟糕指数: 2.50**

> 行数: 39 总计, 31 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `submit_stage_test` | L14-38 | 25 | 4 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 6.0, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 25.0 行, 最大: 25 行
- 文件长度: 31 代码量 (39 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/31)
- 命名规范: 无命名违规

### 283. backend\learning\stage_test_models.py

**糟糕指数: 2.50**

> 行数: 29 总计, 20 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 20 代码量 (29 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/20)
- 命名规范: 无命名违规

### 284. backend\learning\stage_test_get_views.py

**糟糕指数: 2.50**

> 行数: 33 总计, 26 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_stage_test` | L14-32 | 19 | 4 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 6.0, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 19.0 行, 最大: 19 行
- 文件长度: 26 代码量 (33 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/26)
- 命名规范: 无命名违规

### 285. backend\learning\apps.py

**糟糕指数: 2.50**

> 行数: 16 总计, 13 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 13 代码量 (16 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/13)
- 命名规范: 无命名违规

### 286. backend\learning\admin.py

**糟糕指数: 2.50**

> 行数: 29 总计, 22 代码, 0 注释 | 函数: 0 | 类: 3

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 22 代码量 (29 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/22)
- 命名规范: 无命名违规

### 287. backend\common\utils.py

**糟糕指数: 2.50**

> 行数: 55 总计, 49 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 49 代码量 (55 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/49)
- 命名规范: 无命名违规

### 288. backend\common\test_responses.py

**糟糕指数: 2.50**

> 行数: 49 总计, 40 代码, 0 注释 | 函数: 2 | 类: 1

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_error_response_should_include_structured_error_details` | L13-33 | 21 | 1 | 0 | 1 | ✓ |
| `test_exception_handler_should_flatten_field_message` | L35-48 | 14 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 17.5 行, 最大: 21 行
- 文件长度: 40 代码量 (49 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/40)
- 命名规范: 无命名违规

### 289. backend\common\neo4j_service.py

**糟糕指数: 2.50**

> 行数: 21 总计, 14 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 14 代码量 (21 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/14)
- 命名规范: 无命名违规

### 290. backend\common\models.py

**糟糕指数: 2.50**

> 行数: 4 总计, 1 代码, 1 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (4 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 100.0% (1/1)
- 命名规范: 无命名违规

### 291. backend\common\apps.py

**糟糕指数: 2.50**

> 行数: 16 总计, 13 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 13 代码量 (16 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/13)
- 命名规范: 无命名违规

### 292. backend\common\admin.py

**糟糕指数: 2.50**

> 行数: 4 总计, 1 代码, 1 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (4 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 100.0% (1/1)
- 命名规范: 无命名违规

### 293. backend\exams\teacher_views.py

**糟糕指数: 2.50**

> 行数: 72 总计, 67 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 67 代码量 (72 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/67)
- 命名规范: 无命名违规

### 294. backend\exams\student_class_views.py

**糟糕指数: 2.50**

> 行数: 109 总计, 86 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `student_class_ranking` | L38-63 | 26 | 5 | 1 | 2 | ✓ |
| `student_class_assignments` | L90-108 | 19 | 5 | 1 | 2 | ✓ |
| `student_class_members` | L20-33 | 14 | 3 | 1 | 2 | ✓ |
| `student_class_notifications` | L68-85 | 18 | 3 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 5
- 认知复杂度: 平均: 6.0, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 19.3 行, 最大: 26 行
- 文件长度: 86 代码量 (109 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/86)
- 命名规范: 无命名违规

### 295. backend\exams\apps.py

**糟糕指数: 2.50**

> 行数: 16 总计, 13 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 13 代码量 (16 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/13)
- 命名规范: 无命名违规

### 296. backend\exams\admin.py

**糟糕指数: 2.50**

> 行数: 36 总计, 27 代码, 0 注释 | 函数: 0 | 类: 4

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 27 代码量 (36 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/27)
- 命名规范: 无命名违规

### 297. backend\courses\teacher_views.py

**糟糕指数: 2.50**

> 行数: 86 总计, 81 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 81 代码量 (86 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/81)
- 命名规范: 无命名违规

### 298. backend\courses\serializers.py

**糟糕指数: 2.50**

> 行数: 80 总计, 60 代码, 0 注释 | 函数: 0 | 类: 5

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 60 代码量 (80 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/60)
- 命名规范: 无命名违规

### 299. backend\courses\course_cleanup.py

**糟糕指数: 2.50**

> 行数: 27 总计, 20 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `cleanup_course_runtime_artifacts` | L15-27 | 13 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 13.0 行, 最大: 13 行
- 文件长度: 20 代码量 (27 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/20)
- 命名规范: 无命名违规

### 300. backend\courses\admin.py

**糟糕指数: 2.50**

> 行数: 38 总计, 29 代码, 0 注释 | 函数: 0 | 类: 4

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 29 代码量 (38 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/29)
- 命名规范: 无命名违规

### 301. backend\assessments\views.py

**糟糕指数: 2.50**

> 行数: 64 总计, 60 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 60 代码量 (64 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/60)
- 命名规范: 无命名违规

### 302. backend\assessments\models.py

**糟糕指数: 2.50**

> 行数: 6 总计, 1 代码, 3 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (6 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 300.0% (3/1)
- 命名规范: 无命名违规

### 303. backend\assessments\habit_survey_defaults.py

**糟糕指数: 2.50**

> 行数: 104 总计, 100 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 100 代码量 (104 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/100)
- 命名规范: 无命名违规

### 304. backend\assessments\apps.py

**糟糕指数: 2.50**

> 行数: 16 总计, 13 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 13 代码量 (16 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/13)
- 命名规范: 无命名违规

### 305. backend\assessments\admin.py

**糟糕指数: 2.50**

> 行数: 61 总计, 46 代码, 0 注释 | 函数: 0 | 类: 7

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 46 代码量 (61 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/46)
- 命名规范: 无命名违规

### 306. backend\assessments\ability_survey_defaults.py

**糟糕指数: 2.50**

> 行数: 248 总计, 244 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 244 代码量 (248 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/244)
- 命名规范: 无命名违规

### 307. backend\application\__init__.py

**糟糕指数: 2.50**

> 行数: 6 总计, 1 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (6 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 200.0% (2/1)
- 命名规范: 无命名违规

### 308. backend\ai_services\views.py

**糟糕指数: 2.50**

> 行数: 6 总计, 1 代码, 3 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (6 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 300.0% (3/1)
- 命名规范: 无命名违规

### 309. backend\ai_services\tests.py

**糟糕指数: 2.50**

> 行数: 2 总计, 1 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (2 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/1)
- 命名规范: 无命名违规

### 310. backend\ai_services\student_ai_views.py

**糟糕指数: 2.50**

> 行数: 5 总计, 1 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (5 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 200.0% (2/1)
- 命名规范: 无命名违规

### 311. backend\ai_services\serializers.py

**糟糕指数: 2.50**

> 行数: 32 总计, 22 代码, 0 注释 | 函数: 0 | 类: 4

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 22 代码量 (32 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/22)
- 命名规范: 无命名违规

### 312. backend\ai_services\routing.py

**糟糕指数: 2.50**

> 行数: 11 总计, 6 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 6 代码量 (11 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/6)
- 命名规范: 无命名违规

### 313. backend\ai_services\apps.py

**糟糕指数: 2.50**

> 行数: 16 总计, 13 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 13 代码量 (16 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/13)
- 命名规范: 无命名违规

### 314. backend\ai_services\admin.py

**糟糕指数: 2.50**

> 行数: 16 总计, 13 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 13 代码量 (16 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/13)
- 命名规范: 无命名违规

### 315. frontend\src\utils\markdown.ts

**糟糕指数: 2.50**

> 行数: 42 总计, 19 代码, 19 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `renderMarkdown` | L18-26 | 9 | 3 | 1 | 1 | ✗ |
| `renderMarkdownInline` | L34-41 | 8 | 3 | 1 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 3
- 认知复杂度: 平均: 5.0, 最大: 5
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 8.5 行, 最大: 9 行
- 文件长度: 19 代码量 (42 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 100.0% (19/19)
- 命名规范: 无命名违规

### 316. frontend\src\stores\index.ts

**糟糕指数: 2.50**

> 行数: 14 总计, 5 代码, 6 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 5 代码量 (14 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 120.0% (6/5)
- 命名规范: 无命名违规

### 317. frontend\src\api\types.ts

**糟糕指数: 2.50**

> 行数: 32 总计, 26 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 26 代码量 (32 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/26)
- 命名规范: 无命名违规

### 318. frontend\src\api\course.ts

**糟糕指数: 2.50**

> 行数: 40 总计, 12 代码, 24 注释 | 函数: 3 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getCourses` | L15-17 | 3 | 1 | 0 | 1 | ✗ |
| `selectCourse` | L26-28 | 3 | 1 | 0 | 1 | ✗ |
| `searchCourses` | L35-39 | 5 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.7 行, 最大: 5 行
- 文件长度: 12 代码量 (40 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 200.0% (24/12)
- 命名规范: 无命名违规

### 319. frontend\src\api\authTokens.ts

**糟糕指数: 2.50**

> 行数: 31 总计, 27 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getAuthStorage` | L1-9 | 9 | 3 | 1 | 0 | ✗ |
| `getStoredAccessToken` | L11-18 | 8 | 1 | 0 | 0 | ✗ |
| `getStoredRefreshToken` | L20-22 | 3 | 1 | 0 | 0 | ✗ |
| `clearStoredAuthTokens` | L24-30 | 3 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 3
- 认知复杂度: 平均: 2.0, 最大: 5
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 5.8 行, 最大: 9 行
- 文件长度: 27 代码量 (31 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/27)
- 命名规范: 无命名违规

### 320. frontend\src\api\auth.ts

**糟糕指数: 2.50**

> 行数: 115 总计, 29 代码, 76 注释 | 函数: 9 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `login` | L20-22 | 3 | 1 | 0 | 1 | ✗ |
| `register` | L35-37 | 3 | 1 | 0 | 1 | ✗ |
| `getUserInfo` | L44-46 | 3 | 1 | 0 | 0 | ✗ |
| `updateUserInfo` | L58-60 | 3 | 1 | 0 | 2 | ✗ |
| `refreshToken` | L68-70 | 3 | 1 | 0 | 1 | ✗ |
| `changePassword` | L80-82 | 3 | 1 | 0 | 1 | ✗ |
| `sendResetCode` | L91-93 | 3 | 1 | 0 | 1 | ✗ |
| `resetPassword` | L102-104 | 3 | 1 | 0 | 1 | ✗ |
| `logout` | L111-114 | 4 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.1 行, 最大: 4 行
- 文件长度: 29 代码量 (115 总计)
- 参数数量: 平均: 0.9, 最大: 2
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 0/9 个错误被忽略 (0.0%)
- 注释比例: 262.1% (76/29)
- 命名规范: 无命名违规

### 321. backend\models\MEFKT\constants.py

**糟糕指数: 2.50**

> 行数: 44 总计, 36 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 36 代码量 (44 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/36)
- 命名规范: 无命名违规

### 322. backend\platform_ai\search\__init__.py

**糟糕指数: 2.50**

> 行数: 7 总计, 3 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 3 代码量 (7 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/3)
- 命名规范: 无命名违规

### 323. backend\platform_ai\rag\__init__.py

**糟糕指数: 2.50**

> 行数: 7 总计, 3 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 3 代码量 (7 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/3)
- 命名规范: 无命名违规

### 324. backend\platform_ai\rag\student.py

**糟糕指数: 2.50**

> 行数: 107 总计, 94 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 94 代码量 (107 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/94)
- 命名规范: 无命名违规

### 325. backend\platform_ai\rag\runtime_course.py

**糟糕指数: 2.50**

> 行数: 14 总计, 10 代码, 0 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 10 代码量 (14 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/10)
- 命名规范: 无命名违规

### 326. backend\platform_ai\rag\corpus_types.py

**糟糕指数: 2.50**

> 行数: 73 总计, 58 代码, 0 注释 | 函数: 3 | 类: 3

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `as_dict` | L19-28 | 10 | 1 | 0 | 1 | ✓ |
| `as_dict` | L42-51 | 10 | 1 | 0 | 1 | ✓ |
| `as_dict` | L64-72 | 9 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 9.7 行, 最大: 10 行
- 文件长度: 58 代码量 (73 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/58)
- 命名规范: 无命名违规

### 327. backend\platform_ai\rag\corpus_storage.py

**糟糕指数: 2.50**

> 行数: 39 总计, 27 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `load_course_index` | L24-29 | 6 | 2 | 1 | 1 | ✓ |
| `delete_course_index` | L32-38 | 7 | 2 | 1 | 1 | ✓ |
| `get_index_path` | L11-13 | 3 | 1 | 0 | 1 | ✓ |
| `save_course_index` | L16-21 | 6 | 1 | 0 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 2
- 认知复杂度: 平均: 2.5, 最大: 4
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 5.5 行, 最大: 7 行
- 文件长度: 27 代码量 (39 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/27)
- 命名规范: 无命名违规

### 328. backend\platform_ai\rag\corpus.py

**糟糕指数: 2.50**

> 行数: 31 总计, 22 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_course_graph_index` | L11-13 | 3 | 1 | 0 | 1 | ✓ |
| `build_course_corpus` | L16-19 | 4 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.5 行, 最大: 4 行
- 文件长度: 22 代码量 (31 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/22)
- 命名规范: 无命名违规

### 329. backend\platform_ai\mcp\__init__.py

**糟糕指数: 2.50**

> 行数: 10 总计, 7 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 7 代码量 (10 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/7)
- 命名规范: 无命名违规

### 330. backend\platform_ai\kt\__init__.py

**糟糕指数: 2.50**

> 行数: 12 总计, 8 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 8 代码量 (12 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/8)
- 命名规范: 无命名违规

### 331. backend\platform_ai\kt\facade.py

**糟糕指数: 2.50**

> 行数: 39 总计, 26 代码, 0 注释 | 函数: 4 | 类: 1

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `predict_mastery` | L14-16 | 3 | 1 | 0 | 0 | ✓ |
| `batch_predict` | L19-21 | 3 | 1 | 0 | 0 | ✓ |
| `get_learning_recommendations` | L24-26 | 3 | 1 | 0 | 0 | ✓ |
| `get_model_info` | L29-34 | 6 | 1 | 0 | 0 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.8 行, 最大: 6 行
- 文件长度: 26 代码量 (39 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/26)
- 命名规范: 无命名违规

### 332. backend\platform_ai\kt\datasets.py

**糟糕指数: 2.50**

> 行数: 98 总计, 78 代码, 0 注释 | 函数: 3 | 类: 1

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `list_public_datasets` | L81-96 | 16 | 4 | 1 | 0 | ✓ |
| `get_public_dataset_info` | L63-78 | 16 | 3 | 1 | 1 | ✓ |
| `is_available` | L29-31 | 3 | 2 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 4
- 认知复杂度: 平均: 4.3, 最大: 6
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 11.7 行, 最大: 16 行
- 文件长度: 78 代码量 (98 总计)
- 参数数量: 平均: 0.7, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/78)
- 命名规范: 无命名违规

### 333. backend\platform_ai\llm\__init__.py

**糟糕指数: 2.50**

> 行数: 7 总计, 4 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 4 代码量 (7 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/4)
- 命名规范: 无命名违规

### 334. backend\platform_ai\llm\facade.py

**糟糕指数: 2.50**

> 行数: 59 总计, 40 代码, 0 注释 | 函数: 10 | 类: 1

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_llm_service` | L11-13 | 3 | 1 | 0 | 0 | ✓ |
| `service` | L20-22 | 3 | 1 | 0 | 1 | ✓ |
| `is_available` | L25-27 | 3 | 1 | 0 | 1 | ✓ |
| `analyze_profile` | L29-31 | 3 | 1 | 0 | 1 | ✓ |
| `plan_learning_path` | L33-35 | 3 | 1 | 0 | 1 | ✓ |
| `generate_resource_reason` | L37-39 | 3 | 1 | 0 | 1 | ✓ |
| `generate_feedback_report` | L41-43 | 3 | 1 | 0 | 1 | ✓ |
| `recommend_internal_resources` | L45-47 | 3 | 1 | 0 | 1 | ✓ |
| `recommend_external_resources` | L49-51 | 3 | 1 | 0 | 1 | ✓ |
| `call_with_fallback` | L53-55 | 3 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.0 行, 最大: 3 行
- 文件长度: 40 代码量 (59 总计)
- 参数数量: 平均: 0.9, 最大: 1
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/40)
- 命名规范: 无命名违规

### 335. backend\application\teacher\__init__.py

**糟糕指数: 2.50**

> 行数: 6 总计, 1 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 1 代码量 (6 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 200.0% (2/1)
- 命名规范: 无命名违规

### 336. backend\ai_services\services\__init__.py

**糟糕指数: 2.50**

> 行数: 23 总计, 20 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 20 代码量 (23 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/20)
- 命名规范: 无命名违规

### 337. frontend\src\views\teacher\resourceManageModels.js

**糟糕指数: 2.50**

> 行数: 154 总计, 129 代码, 0 注释 | 函数: 18 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `normalizeText` | L31-35 | 5 | 3 | 1 | 1 | ✗ |
| `normalizeNumber` | L39-42 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeListFromPayload` | L44-44 | 1 | 2 | 0 | 1 | ✗ |
| `resolvePointNameText` | L89-94 | 5 | 2 | 1 | 2 | ✗ |
| `getUploadTipText` | L144-148 | 5 | 2 | 0 | 1 | ✗ |
| `formatTime` | L150-153 | 4 | 2 | 1 | 1 | ✗ |
| `normalizeIdentifier` | L37-37 | 1 | 1 | 0 | 1 | ✗ |
| `normalizeResourceType` | L46-49 | 4 | 1 | 0 | 1 | ✗ |
| `buildDefaultKnowledgePointOption` | L51-54 | 4 | 1 | 0 | 0 | ✗ |
| `buildDefaultResourceRecord` | L56-71 | 16 | 1 | 0 | 0 | ✗ |
| `normalizeKnowledgePointOption` | L73-77 | 5 | 1 | 0 | 1 | ✗ |
| `normalizeResourcePointOptions` | L79-82 | 3 | 1 | 0 | 1 | ✗ |
| `resolvePrimaryPointId` | L84-87 | 4 | 1 | 0 | 2 | ✗ |
| `normalizeResourceRecord` | L96-119 | 23 | 1 | 0 | 1 | ✗ |
| `normalizeResourceListPayload` | L121-125 | 4 | 1 | 0 | 1 | ✗ |
| `normalizeKnowledgePointListPayload` | L127-130 | 3 | 1 | 0 | 1 | ✗ |
| `buildDefaultResourceForm` | L132-140 | 9 | 1 | 0 | 0 | ✗ |
| `getAcceptTypes` | L142-142 | 1 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 3
- 认知复杂度: 平均: 1.7, 最大: 5
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 5.6 行, 最大: 23 行
- 文件长度: 129 代码量 (154 总计)
- 参数数量: 平均: 0.9, 最大: 2
- 代码重复: 0.0% 重复 (0/18)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/129)
- 命名规范: 无命名违规

### 338. frontend\src\views\student\learningPathModels.js

**糟糕指数: 2.50**

> 行数: 101 总计, 89 代码, 0 注释 | 函数: 12 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `normalizeLearningStatus` | L19-25 | 7 | 4 | 1 | 1 | ✗ |
| `normalizeText` | L1-5 | 5 | 3 | 1 | 1 | ✗ |
| `normalizeIdentifier` | L7-10 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeNumber` | L12-15 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeListFromPayload` | L17-17 | 1 | 2 | 0 | 1 | ✗ |
| `normalizeDurationMinutes` | L27-30 | 4 | 2 | 0 | 1 | ✗ |
| `buildDefaultLearningPathNode` | L32-43 | 12 | 1 | 0 | 0 | ✗ |
| `normalizeLearningPathNode` | L45-57 | 13 | 1 | 0 | 1 | ✗ |
| `normalizeLearningPathPayload` | L59-65 | 6 | 1 | 0 | 1 | ✗ |
| `normalizeLearningPathRefreshSummary` | L67-80 | 14 | 1 | 0 | 1 | ✗ |
| `getNodeTagType` | L82-90 | 9 | 1 | 0 | 1 | ✗ |
| `getNodeStatusText` | L92-100 | 9 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.8, 最大: 4
- 认知复杂度: 平均: 2.1, 最大: 6
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 7.3 行, 最大: 14 行
- 文件长度: 89 代码量 (101 总计)
- 参数数量: 平均: 0.9, 最大: 1
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/89)
- 命名规范: 无命名违规

### 339. frontend\src\views\student\examTakingModels.js

**糟糕指数: 2.50**

> 行数: 137 总计, 123 代码, 0 注释 | 函数: 14 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `normalizeText` | L1-9 | 9 | 4 | 1 | 1 | ✗ |
| `normalizeIdentifier` | L16-21 | 6 | 3 | 1 | 1 | ✗ |
| `normalizeFeedbackRouteId` | L118-128 | 11 | 3 | 1 | 1 | ✗ |
| `normalizeNumber` | L11-14 | 4 | 2 | 0 | 1 | ✗ |
| `normalizeListFromPayload` | L23-25 | 3 | 2 | 0 | 1 | ✗ |
| `normalizeQuestionType` | L27-42 | 16 | 2 | 0 | 1 | ✗ |
| `normalizeQuestionOption` | L74-84 | 11 | 2 | 0 | 2 | ✗ |
| `createEmptyAnswer` | L114-116 | 3 | 2 | 0 | 1 | ✗ |
| `formatTime` | L130-136 | 7 | 2 | 1 | 1 | ✗ |
| `getQuestionTagType` | L44-53 | 10 | 1 | 0 | 1 | ✗ |
| `getQuestionTypeName` | L55-64 | 10 | 1 | 0 | 1 | ✗ |
| `buildDefaultExamInfo` | L66-72 | 7 | 1 | 0 | 0 | ✗ |
| `normalizeExamQuestion` | L86-100 | 12 | 1 | 0 | 2 | ✗ |
| `normalizeExamDetail` | L102-112 | 8 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.9, 最大: 4
- 认知复杂度: 平均: 2.5, 最大: 6
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 8.4 行, 最大: 16 行
- 文件长度: 123 代码量 (137 总计)
- 参数数量: 平均: 1.1, 最大: 2
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/123)
- 命名规范: 无命名违规

### 340. frontend\src\api\teacher\settings.ts

**糟糕指数: 2.50**

> 行数: 25 总计, 7 代码, 15 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getCourseSettings` | L12-14 | 3 | 1 | 0 | 1 | ✗ |
| `updateCourseSettings` | L22-24 | 3 | 1 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.0 行, 最大: 3 行
- 文件长度: 7 代码量 (25 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 214.3% (15/7)
- 命名规范: 无命名违规

### 341. frontend\src\api\teacher\question.ts

**糟糕指数: 2.50**

> 行数: 129 总计, 43 代码, 75 注释 | 函数: 10 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getQuestions` | L19-21 | 3 | 1 | 0 | 1 | ✗ |
| `getQuestionDetail` | L28-30 | 3 | 1 | 0 | 1 | ✗ |
| `createQuestion` | L46-48 | 3 | 1 | 0 | 1 | ✗ |
| `updateQuestion` | L56-58 | 3 | 1 | 0 | 2 | ✗ |
| `deleteQuestion` | L65-67 | 3 | 1 | 0 | 1 | ✗ |
| `batchDeleteQuestions` | L74-76 | 3 | 1 | 0 | 1 | ✗ |
| `importQuestions` | L85-92 | 8 | 1 | 0 | 2 | ✗ |
| `exportQuestions` | L101-106 | 6 | 1 | 0 | 1 | ✗ |
| `getQuestionTemplate` | L112-116 | 5 | 1 | 0 | 0 | ✗ |
| `linkQuestionToKnowledge` | L124-128 | 5 | 1 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.2 行, 最大: 8 行
- 文件长度: 43 代码量 (129 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 0/10 个错误被忽略 (0.0%)
- 注释比例: 174.4% (75/43)
- 命名规范: 无命名违规

### 342. frontend\src\api\teacher\knowledge.ts

**糟糕指数: 2.50**

> 行数: 260 总计, 92 代码, 142 注释 | 函数: 21 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getKnowledgePoints` | L17-21 | 5 | 1 | 0 | 2 | ✗ |
| `getKnowledgePointDetail` | L28-30 | 3 | 1 | 0 | 1 | ✗ |
| `createKnowledgePoint` | L42-44 | 3 | 1 | 0 | 1 | ✗ |
| `updateKnowledgePoint` | L52-54 | 3 | 1 | 0 | 2 | ✗ |
| `deleteKnowledgePoint` | L61-63 | 3 | 1 | 0 | 1 | ✗ |
| `getKnowledgeRelations` | L72-76 | 5 | 1 | 0 | 1 | ✗ |
| `createKnowledgeRelation` | L86-88 | 3 | 1 | 0 | 1 | ✗ |
| `deleteKnowledgeRelation` | L95-97 | 3 | 1 | 0 | 1 | ✗ |
| `importKnowledgeMap` | L108-115 | 8 | 1 | 0 | 2 | ✗ |
| `saveKnowledgeGraph` | L123-128 | 6 | 1 | 0 | 2 | ✗ |
| `exportKnowledgeMap` | L136-141 | 6 | 1 | 0 | 2 | ✗ |
| `publishKnowledgeMap` | L149-153 | 5 | 1 | 0 | 1 | ✗ |
| `buildKnowledgeRagIndex` | L160-164 | 5 | 1 | 0 | 1 | ✗ |
| `getKnowledgeMapTemplate` | L170-174 | 5 | 1 | 0 | 0 | ✗ |
| `getResources` | L186-188 | 3 | 1 | 0 | 1 | ✗ |
| `getResourceDetail` | L195-197 | 3 | 1 | 0 | 1 | ✗ |
| `createResource` | L211-213 | 3 | 1 | 0 | 1 | ✗ |
| `uploadResource` | L221-228 | 8 | 1 | 0 | 2 | ✗ |
| `updateResource` | L236-238 | 3 | 1 | 0 | 2 | ✗ |
| `deleteResource` | L245-247 | 3 | 1 | 0 | 1 | ✗ |
| `linkResourceToKnowledge` | L255-259 | 5 | 1 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.3 行, 最大: 8 行
- 文件长度: 92 代码量 (260 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/21)
- 结构分析: 0 个结构问题
- 错误处理: 0/21 个错误被忽略 (0.0%)
- 注释比例: 154.3% (142/92)
- 命名规范: 无命名违规

### 343. frontend\src\api\teacher\index.ts

**糟糕指数: 2.50**

> 行数: 19 总计, 5 代码, 12 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 5 代码量 (19 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 240.0% (12/5)
- 命名规范: 无命名违规

### 344. frontend\src\api\teacher\exam.ts

**糟糕指数: 2.50**

> 行数: 158 总计, 49 代码, 95 注释 | 函数: 13 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getExams` | L16-20 | 5 | 1 | 0 | 2 | ✗ |
| `getExamDetail` | L27-29 | 3 | 1 | 0 | 1 | ✗ |
| `createExam` | L45-47 | 3 | 1 | 0 | 1 | ✗ |
| `updateExam` | L55-57 | 3 | 1 | 0 | 2 | ✗ |
| `deleteExam` | L64-66 | 3 | 1 | 0 | 1 | ✗ |
| `publishExam` | L77-79 | 3 | 1 | 0 | 2 | ✗ |
| `unpublishExam` | L86-88 | 3 | 1 | 0 | 1 | ✗ |
| `getExamResults` | L98-100 | 3 | 1 | 0 | 2 | ✗ |
| `getStudentExamDetail` | L109-111 | 3 | 1 | 0 | 2 | ✗ |
| `getExamAnalysis` | L118-120 | 3 | 1 | 0 | 1 | ✗ |
| `exportExamResults` | L128-133 | 6 | 1 | 0 | 2 | ✗ |
| `addQuestionsToExam` | L141-145 | 5 | 1 | 0 | 2 | ✗ |
| `removeQuestionsFromExam` | L153-157 | 5 | 1 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.7 行, 最大: 6 行
- 文件长度: 49 代码量 (158 总计)
- 参数数量: 平均: 1.6, 最大: 2
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 0/13 个错误被忽略 (0.0%)
- 注释比例: 193.9% (95/49)
- 命名规范: 无命名违规

### 345. frontend\src\api\teacher\course.ts

**糟糕指数: 2.50**

> 行数: 94 总计, 34 代码, 52 注释 | 函数: 7 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getMyCourses` | L15-17 | 3 | 1 | 0 | 1 | ✗ |
| `getCourseDetail` | L24-26 | 3 | 1 | 0 | 1 | ✗ |
| `createCourse` | L38-48 | 6 | 1 | 0 | 1 | ✗ |
| `updateCourse` | L58-60 | 3 | 1 | 0 | 2 | ✗ |
| `deleteCourse` | L68-70 | 3 | 1 | 0 | 1 | ✗ |
| `uploadCourseCover` | L78-84 | 7 | 1 | 0 | 2 | ✗ |
| `getCourseStats` | L91-93 | 3 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.0 行, 最大: 7 行
- 文件长度: 34 代码量 (94 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 152.9% (52/34)
- 命名规范: 无命名违规

### 346. frontend\src\api\teacher\class.ts

**糟糕指数: 2.50**

> 行数: 195 总计, 57 代码, 118 注释 | 函数: 18 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getStudentProfileDetail` | L141-145 | 5 | 2 | 1 | 3 | ✗ |
| `getMyClasses` | L15-17 | 3 | 1 | 0 | 1 | ✗ |
| `getClassDetail` | L24-26 | 3 | 1 | 0 | 1 | ✗ |
| `createClass` | L36-38 | 3 | 1 | 0 | 1 | ✗ |
| `updateClass` | L46-48 | 3 | 1 | 0 | 2 | ✗ |
| `deleteClass` | L55-57 | 3 | 1 | 0 | 1 | ✗ |
| `publishCourse` | L67-69 | 3 | 1 | 0 | 2 | ✗ |
| `getClassStudents` | L79-81 | 3 | 1 | 0 | 2 | ✗ |
| `removeStudent` | L89-91 | 3 | 1 | 0 | 2 | ✗ |
| `getInvitations` | L98-100 | 3 | 1 | 0 | 1 | ✗ |
| `generateInvitation` | L110-112 | 3 | 1 | 0 | 1 | ✗ |
| `deleteInvitation` | L119-121 | 3 | 1 | 0 | 1 | ✗ |
| `getStudentProfiles` | L129-131 | 3 | 1 | 0 | 2 | ✗ |
| `getClassProgress` | L152-154 | 3 | 1 | 0 | 1 | ✗ |
| `getAnnouncements` | L163-165 | 3 | 1 | 0 | 1 | ✗ |
| `createAnnouncement` | L173-175 | 3 | 1 | 0 | 2 | ✗ |
| `updateAnnouncement` | L183-185 | 3 | 1 | 0 | 2 | ✗ |
| `deleteAnnouncement` | L192-194 | 3 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.1, 最大: 2
- 认知复杂度: 平均: 1.2, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 3.1 行, 最大: 5 行
- 文件长度: 57 代码量 (195 总计)
- 参数数量: 平均: 1.5, 最大: 3
- 代码重复: 0.0% 重复 (0/18)
- 结构分析: 0 个结构问题
- 错误处理: 0/18 个错误被忽略 (0.0%)
- 注释比例: 207.0% (118/57)
- 命名规范: 无命名违规

### 347. frontend\src\api\student\profile.ts

**糟糕指数: 2.50**

> 行数: 98 总计, 34 代码, 56 注释 | 函数: 7 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getProfile` | L14-18 | 5 | 1 | 0 | 1 | ✗ |
| `updateHabitPreference` | L28-30 | 3 | 1 | 0 | 1 | ✗ |
| `updateProfile` | L39-43 | 5 | 1 | 0 | 1 | ✗ |
| `refreshProfileWithAI` | L52-56 | 5 | 1 | 0 | 1 | ✗ |
| `getProfileHistory` | L67-71 | 5 | 1 | 0 | 2 | ✗ |
| `compareProfiles` | L81-85 | 5 | 1 | 0 | 3 | ✗ |
| `exportProfile` | L93-97 | 5 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.7 行, 最大: 5 行
- 文件长度: 34 代码量 (98 总计)
- 参数数量: 平均: 1.4, 最大: 3
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 164.7% (56/34)
- 命名规范: 无命名违规

### 348. frontend\src\api\student\learning.ts

**糟糕指数: 2.50**

> 行数: 198 总计, 67 代码, 114 注释 | 函数: 16 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getPathNodeDetail` | L38-42 | 5 | 2 | 0 | 2 | ✗ |
| `startLearningNode` | L51-53 | 3 | 2 | 0 | 2 | ✗ |
| `completeResource` | L63-65 | 3 | 2 | 0 | 3 | ✗ |
| `getNodeResources` | L84-88 | 5 | 2 | 0 | 2 | ✗ |
| `getNodeExams` | L120-124 | 5 | 2 | 0 | 2 | ✗ |
| `completePathNode` | L133-135 | 3 | 2 | 0 | 2 | ✗ |
| `skipPathNode` | L145-150 | 6 | 2 | 0 | 3 | ✗ |
| `getLearningPath` | L13-17 | 5 | 1 | 0 | 1 | ✗ |
| `adjustLearningPath` | L27-29 | 3 | 1 | 0 | 1 | ✗ |
| `pauseResource` | L74-76 | 3 | 1 | 0 | 2 | ✗ |
| `getAIResources` | L96-100 | 5 | 1 | 0 | 1 | ✗ |
| `submitNodeExam` | L110-112 | 3 | 1 | 0 | 3 | ✗ |
| `getLearningProgress` | L158-162 | 5 | 1 | 0 | 1 | ✗ |
| `refreshLearningPathWithAI` | L170-176 | 7 | 1 | 0 | 1 | ✗ |
| `getStageTest` | L184-186 | 3 | 1 | 0 | 1 | ✗ |
| `submitStageTest` | L195-197 | 3 | 1 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 2
- 认知复杂度: 平均: 1.4, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.2 行, 最大: 7 行
- 文件长度: 67 代码量 (198 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/16)
- 结构分析: 0 个结构问题
- 错误处理: 0/16 个错误被忽略 (0.0%)
- 注释比例: 170.1% (114/67)
- 命名规范: 无命名违规

### 349. frontend\src\api\student\knowledge.ts

**糟糕指数: 2.50**

> 行数: 127 总计, 46 代码, 71 注释 | 函数: 9 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getKnowledgeMap` | L13-17 | 5 | 1 | 0 | 1 | ✗ |
| `getKnowledgePoints` | L29-33 | 5 | 1 | 0 | 2 | ✗ |
| `getKnowledgePointDetail` | L42-46 | 5 | 1 | 0 | 2 | ✗ |
| `getKnowledgeRelations` | L54-58 | 5 | 1 | 0 | 1 | ✗ |
| `getKnowledgeMastery` | L66-70 | 5 | 1 | 0 | 1 | ✗ |
| `updateKnowledgeMastery` | L80-86 | 7 | 1 | 0 | 3 | ✗ |
| `getPointResources` | L95-99 | 5 | 1 | 0 | 2 | ✗ |
| `getStudentResources` | L112-114 | 3 | 1 | 0 | 1 | ✗ |
| `searchKnowledgePoints` | L122-126 | 5 | 1 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 5.0 行, 最大: 7 行
- 文件长度: 46 代码量 (127 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 0/9 个错误被忽略 (0.0%)
- 注释比例: 154.3% (71/46)
- 命名规范: 无命名违规

### 350. frontend\src\api\student\index.ts

**糟糕指数: 2.50**

> 行数: 26 总计, 7 代码, 11 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 7 代码量 (26 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 157.1% (11/7)
- 命名规范: 无命名违规

### 351. frontend\src\api\student\exam.ts

**糟糕指数: 2.50**

> 行数: 130 总计, 37 代码, 81 注释 | 函数: 11 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getExamList` | L16-19 | 4 | 2 | 0 | 2 | ✗ |
| `getExamDetail` | L27-29 | 3 | 1 | 0 | 1 | ✗ |
| `saveExamDraft` | L38-40 | 3 | 1 | 0 | 2 | ✗ |
| `submitExam` | L51-53 | 3 | 1 | 0 | 2 | ✗ |
| `getExamResult` | L61-63 | 3 | 1 | 0 | 1 | ✗ |
| `generateFeedback` | L74-76 | 3 | 1 | 0 | 2 | ✗ |
| `getFeedback` | L84-86 | 3 | 1 | 0 | 1 | ✗ |
| `getExamStatistics` | L94-96 | 3 | 1 | 0 | 1 | ✗ |
| `downloadExamReport` | L105-109 | 5 | 1 | 0 | 2 | ✗ |
| `retakeExam` | L117-119 | 3 | 1 | 0 | 1 | ✗ |
| `getExamAnswerSheet` | L127-129 | 3 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.1, 最大: 2
- 认知复杂度: 平均: 1.1, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.3 行, 最大: 5 行
- 文件长度: 37 代码量 (130 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 0 个结构问题
- 错误处理: 0/11 个错误被忽略 (0.0%)
- 注释比例: 218.9% (81/37)
- 命名规范: 无命名违规

### 352. frontend\src\api\student\class.ts

**糟糕指数: 2.50**

> 行数: 123 总计, 52 代码, 58 注释 | 函数: 8 | 类: 4

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getClassList` | L39-41 | 3 | 1 | 0 | 0 | ✗ |
| `getClassDetail` | L49-51 | 3 | 1 | 0 | 1 | ✗ |
| `joinClass` | L60-64 | 5 | 1 | 0 | 1 | ✗ |
| `leaveClass` | L72-74 | 3 | 1 | 0 | 1 | ✗ |
| `getClassMembers` | L85-87 | 3 | 1 | 0 | 2 | ✗ |
| `getClassRanking` | L96-100 | 5 | 1 | 0 | 2 | ✗ |
| `getClassNotifications` | L109-111 | 3 | 1 | 0 | 2 | ✗ |
| `getClassAssignments` | L120-122 | 3 | 1 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.5 行, 最大: 5 行
- 文件长度: 52 代码量 (123 总计)
- 参数数量: 平均: 1.4, 最大: 2
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 0/6 个错误被忽略 (0.0%)
- 注释比例: 111.5% (58/52)
- 命名规范: 无命名违规

### 353. frontend\src\api\student\assessment.ts

**糟糕指数: 2.50**

> 行数: 156 总计, 74 代码, 64 注释 | 函数: 10 | 类: 7

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getAssessmentStatus` | L49-53 | 5 | 2 | 0 | 1 | ✗ |
| `getHabitSurvey` | L83-87 | 5 | 2 | 0 | 1 | ✗ |
| `getAbilityAssessment` | L61-65 | 5 | 1 | 0 | 1 | ✗ |
| `submitAbilityAssessment` | L73-75 | 3 | 1 | 0 | 1 | ✗ |
| `submitHabitSurvey` | L95-97 | 3 | 1 | 0 | 1 | ✗ |
| `getKnowledgeAssessment` | L105-109 | 5 | 1 | 0 | 1 | ✗ |
| `submitKnowledgeAssessment` | L118-120 | 3 | 1 | 0 | 1 | ✗ |
| `getKnowledgeResult` | L128-132 | 5 | 1 | 0 | 1 | ✗ |
| `generateProfile` | L140-144 | 5 | 1 | 0 | 1 | ✗ |
| `retakeAbilityAssessment` | L151-155 | 5 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.2, 最大: 2
- 认知复杂度: 平均: 1.2, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.4 行, 最大: 5 行
- 文件长度: 74 代码量 (156 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 0/5 个错误被忽略 (0.0%)
- 注释比例: 86.5% (64/74)
- 命名规范: 无命名违规

### 354. frontend\src\api\admin\user.ts

**糟糕指数: 2.50**

> 行数: 147 总计, 51 代码, 82 注释 | 函数: 13 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getUsers` | L17-19 | 3 | 1 | 0 | 1 | ✗ |
| `getUserList` | L26-28 | 3 | 1 | 0 | 1 | ✗ |
| `getUserDetail` | L35-37 | 3 | 1 | 0 | 1 | ✗ |
| `createUser` | L49-51 | 3 | 1 | 0 | 1 | ✗ |
| `updateUser` | L59-61 | 3 | 1 | 0 | 2 | ✗ |
| `deleteUser` | L68-70 | 3 | 1 | 0 | 1 | ✗ |
| `batchDeleteUsers` | L77-79 | 3 | 1 | 0 | 1 | ✗ |
| `resetUserPassword` | L87-91 | 5 | 1 | 0 | 2 | ✗ |
| `disableUser` | L98-100 | 3 | 1 | 0 | 1 | ✗ |
| `enableUser` | L107-109 | 3 | 1 | 0 | 1 | ✗ |
| `importUsers` | L117-123 | 7 | 1 | 0 | 1 | ✗ |
| `exportUsers` | L131-136 | 6 | 1 | 0 | 1 | ✗ |
| `getUserImportTemplate` | L142-146 | 5 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.8 行, 最大: 7 行
- 文件长度: 51 代码量 (147 总计)
- 参数数量: 平均: 1.1, 最大: 2
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 0/13 个错误被忽略 (0.0%)
- 注释比例: 160.8% (82/51)
- 命名规范: 无命名违规

### 355. frontend\src\api\admin\statistics.ts

**糟糕指数: 2.50**

> 行数: 105 总计, 31 代码, 64 注释 | 函数: 9 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getOverviewStats` | L12-14 | 3 | 1 | 0 | 0 | ✗ |
| `getSystemStats` | L20-22 | 3 | 1 | 0 | 0 | ✗ |
| `getUserStats` | L33-35 | 3 | 1 | 0 | 1 | ✗ |
| `getCourseStats` | L45-47 | 3 | 1 | 0 | 1 | ✗ |
| `getLearningStats` | L58-60 | 3 | 1 | 0 | 1 | ✗ |
| `getExamStats` | L68-70 | 3 | 1 | 0 | 1 | ✗ |
| `getActiveUserRanking` | L78-80 | 3 | 1 | 0 | 1 | ✗ |
| `getSystemReport` | L88-90 | 3 | 1 | 0 | 1 | ✗ |
| `exportStatistics` | L99-104 | 6 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.3 行, 最大: 6 行
- 文件长度: 31 代码量 (105 总计)
- 参数数量: 平均: 0.8, 最大: 1
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 0/9 个错误被忽略 (0.0%)
- 注释比例: 206.5% (64/31)
- 命名规范: 无命名违规

### 356. frontend\src\api\admin\profile.ts

**糟糕指数: 2.50**

> 行数: 27 总计, 9 代码, 15 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getStudentProfiles` | L13-15 | 3 | 1 | 0 | 1 | ✗ |
| `getStudentProfileDetail` | L22-26 | 5 | 1 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.0 行, 最大: 5 行
- 文件长度: 9 代码量 (27 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 166.7% (15/9)
- 命名规范: 无命名违规

### 357. frontend\src\api\admin\log.ts

**糟糕指数: 2.50**

> 行数: 112 总计, 37 代码, 64 注释 | 函数: 10 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getLogs` | L20-22 | 3 | 1 | 0 | 1 | ✗ |
| `getSystemLogs` | L29-31 | 3 | 1 | 0 | 1 | ✗ |
| `getLogDetail` | L38-40 | 3 | 1 | 0 | 1 | ✗ |
| `getLogStatistics` | L50-52 | 3 | 1 | 0 | 1 | ✗ |
| `getLogOptions` | L58-60 | 3 | 1 | 0 | 0 | ✗ |
| `getLogModules` | L67-69 | 3 | 1 | 0 | 0 | ✗ |
| `getLogActions` | L75-77 | 3 | 1 | 0 | 0 | ✗ |
| `exportLogs` | L84-89 | 6 | 1 | 0 | 1 | ✗ |
| `exportData` | L96-101 | 6 | 1 | 0 | 1 | ✗ |
| `cleanExpiredLogs` | L109-111 | 3 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.6 行, 最大: 6 行
- 文件长度: 37 代码量 (112 总计)
- 参数数量: 平均: 0.7, 最大: 1
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 0/10 个错误被忽略 (0.0%)
- 注释比例: 173.0% (64/37)
- 命名规范: 无命名违规

### 358. frontend\src\api\admin\course.ts

**糟糕指数: 2.50**

> 行数: 81 总计, 24 代码, 49 注释 | 函数: 7 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getAllCourses` | L17-19 | 3 | 1 | 0 | 1 | ✗ |
| `getCourseDetail` | L26-28 | 3 | 1 | 0 | 1 | ✗ |
| `createCourse` | L38-40 | 3 | 1 | 0 | 1 | ✗ |
| `updateCourse` | L48-50 | 3 | 1 | 0 | 2 | ✗ |
| `deleteCourse` | L57-59 | 3 | 1 | 0 | 1 | ✗ |
| `assignCourseTeacher` | L67-71 | 5 | 1 | 0 | 2 | ✗ |
| `getCourseStats` | L78-80 | 3 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.3 行, 最大: 5 行
- 文件长度: 24 代码量 (81 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 204.2% (49/24)
- 命名规范: 无命名违规

### 359. frontend\src\api\admin\class.ts

**糟糕指数: 2.50**

> 行数: 113 总计, 35 代码, 67 注释 | 函数: 10 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getClassList` | L17-19 | 3 | 1 | 0 | 1 | ✗ |
| `getClassDetail` | L26-28 | 3 | 1 | 0 | 1 | ✗ |
| `createClass` | L38-40 | 3 | 1 | 0 | 1 | ✗ |
| `updateClass` | L48-50 | 3 | 1 | 0 | 2 | ✗ |
| `deleteClass` | L57-59 | 3 | 1 | 0 | 1 | ✗ |
| `getClassStudents` | L67-69 | 3 | 1 | 0 | 2 | ✗ |
| `addStudentsToClass` | L77-81 | 5 | 1 | 0 | 2 | ✗ |
| `removeStudentFromClass` | L89-91 | 3 | 1 | 0 | 2 | ✗ |
| `assignClassTeacher` | L99-103 | 5 | 1 | 0 | 2 | ✗ |
| `getClassStats` | L110-112 | 3 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.4 行, 最大: 5 行
- 文件长度: 35 代码量 (113 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 0/10 个错误被忽略 (0.0%)
- 注释比例: 191.4% (67/35)
- 命名规范: 无命名违规

### 360. frontend\src\api\admin\activation.ts

**糟糕指数: 2.50**

> 行数: 84 总计, 27 代码, 49 注释 | 函数: 7 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getActivationCodes` | L18-20 | 3 | 1 | 0 | 1 | ✗ |
| `getActivationCodeDetail` | L27-29 | 3 | 1 | 0 | 1 | ✗ |
| `generateActivationCodes` | L40-42 | 3 | 1 | 0 | 1 | ✗ |
| `deleteActivationCode` | L49-51 | 3 | 1 | 0 | 1 | ✗ |
| `batchDeleteActivationCodes` | L58-62 | 5 | 1 | 0 | 1 | ✗ |
| `validateActivationCode` | L69-71 | 3 | 1 | 0 | 1 | ✗ |
| `exportActivationCodes` | L78-83 | 6 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.7 行, 最大: 6 行
- 文件长度: 27 代码量 (84 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 181.5% (49/27)
- 命名规范: 无命名违规

### 361. frontend\src\components\knowledge\knowledgeGraphModels.js

**糟糕指数: 2.50**

> 行数: 87 总计, 75 代码, 0 注释 | 函数: 11 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `normalizeText` | L3-11 | 9 | 4 | 1 | 1 | ✗ |
| `normalizeIdentifier` | L13-18 | 6 | 3 | 1 | 1 | ✗ |
| `normalizeOptionalNumber` | L24-28 | 5 | 3 | 1 | 1 | ✗ |
| `getLinkCoordinate` | L73-80 | 8 | 3 | 1 | 3 | ✗ |
| `getRelationStroke` | L82-86 | 5 | 3 | 1 | 1 | ✗ |
| `normalizeListFromPayload` | L20-22 | 3 | 2 | 0 | 1 | ✗ |
| `normalizeGraphNode` | L30-39 | 10 | 1 | 0 | 2 | ✗ |
| `normalizeGraphEdge` | L41-48 | 8 | 1 | 0 | 2 | ✗ |
| `normalizeResourceItem` | L50-56 | 7 | 1 | 0 | 2 | ✗ |
| `normalizeNodeDetail` | L58-66 | 9 | 1 | 0 | 1 | ✗ |
| `normalizeNodeResources` | L68-71 | 3 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.1, 最大: 4
- 认知复杂度: 平均: 3.0, 最大: 6
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 6.6 行, 最大: 10 行
- 文件长度: 75 代码量 (87 总计)
- 参数数量: 平均: 1.5, 最大: 3
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/75)
- 命名规范: 无命名违规

### 362. backend\users\auth_password_views.py

**糟糕指数: 2.39**

> 行数: 75 总计, 52 代码, 2 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `password_reset` | L47-74 | 28 | 6 | 1 | 1 | ✓ |
| `password_reset_send` | L22-41 | 20 | 3 | 1 | 1 | ✓ |

**全部问题 (1)**

- ❌ L72: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 6
- 认知复杂度: 平均: 6.5, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 24.0 行, 最大: 28 行
- 文件长度: 52 代码量 (75 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/8 个错误被忽略 (12.5%)
- 注释比例: 3.8% (2/52)
- 命名规范: 无命名违规

### 363. frontend\src\api\common.ts

**糟糕指数: 2.31**

> 行数: 9 总计, 4 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getMenu` | L6-8 | 3 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.0 行, 最大: 3 行
- 文件长度: 4 代码量 (9 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 75.0% (3/4)
- 命名规范: 无命名违规

### 364. backend\models\DKT\KnowledgeTracing\evaluation\run.py

**糟糕指数: 2.26**

> 行数: 41 总计, 19 代码, 14 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 19 代码量 (41 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 73.7% (14/19)
- 命名规范: 无命名违规

### 365. backend\tools\browser_audit.py

**糟糕指数: 2.14**

> 行数: 42 总计, 33 代码, 2 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `browser_audit` | L9-41 | 33 | 5 | 1 | 5 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 5
- 认知复杂度: 平均: 7.0, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 33.0 行, 最大: 33 行
- 文件长度: 33 代码量 (42 总计)
- 参数数量: 平均: 5.0, 最大: 5
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 6.1% (2/33)
- 命名规范: 无命名违规

### 366. backend\ai_services\migrations\0001_initial.py

**糟糕指数: 2.05**

> 行数: 54 总计, 28 代码, 19 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 28 代码量 (54 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 67.9% (19/28)
- 命名规范: 无命名违规

### 367. frontend\src\router\guards.ts

**糟糕指数: 2.03**

> 行数: 145 总计, 74 代码, 50 注释 | 函数: 5 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `hasRolePermission` | L24-34 | 11 | 3 | 1 | 2 | ✗ |
| `setPageTitle` | L60-64 | 5 | 2 | 0 | 1 | ✗ |
| `getDefaultRouteForUser` | L41-44 | 4 | 1 | 0 | 1 | ✗ |
| `shouldSkipCourseCheck` | L51-54 | 3 | 1 | 0 | 1 | ✗ |
| `setupRouterGuards` | L70-139 | 7 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 3
- 认知复杂度: 平均: 2.0, 最大: 5
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 6.0 行, 最大: 11 行
- 文件长度: 74 代码量 (145 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 67.6% (50/74)
- 命名规范: 无命名违规

### 368. backend\ai_services\services\llm_provider_config.py

**糟糕指数: 1.96**

> 行数: 145 总计, 130 代码, 2 注释 | 函数: 0 | 类: 2

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 130 代码量 (145 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 1.5% (2/130)
- 命名规范: 无命名违规

### 369. backend\exams\migrations\0001_initial.py

**糟糕指数: 1.92**

> 行数: 137 总计, 79 代码, 51 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 79 代码量 (137 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 64.6% (51/79)
- 命名规范: 无命名违规

### 370. backend\logs\migrations\0001_initial.py

**糟糕指数: 1.89**

> 行数: 66 总计, 36 代码, 23 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 36 代码量 (66 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 63.9% (23/36)
- 命名规范: 无命名违规

### 371. frontend\src\composables\useCourse.ts

**糟糕指数: 1.87**

> 行数: 163 总计, 91 代码, 49 注释 | 函数: 8 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `fetchCourses` | L47-54 | 8 | 2 | 0 | 0 | ✗ |
| `selectCourse` | L60-67 | 8 | 2 | 1 | 1 | ✗ |
| `selectCourseById` | L73-80 | 7 | 2 | 1 | 1 | ✗ |
| `initCourse` | L92-97 | 6 | 2 | 1 | 0 | ✗ |
| `ensureCourse` | L103-109 | 7 | 2 | 1 | 0 | ✗ |
| `useCourse` | L12-141 | 76 | 1 | 0 | 0 | ✗ |
| `clearSelection` | L85-87 | 3 | 1 | 0 | 0 | ✗ |
| `useCourseWatcher` | L148-162 | 10 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 2
- 认知复杂度: 平均: 2.6, 最大: 4
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 15.6 行, 最大: 76 行
- 文件长度: 91 代码量 (163 总计)
- 参数数量: 平均: 0.4, 最大: 1
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 53.8% (49/91)
- 命名规范: 无命名违规

### 372. backend\learning\migrations\0001_initial.py

**糟糕指数: 1.83**

> 行数: 106 总计, 61 代码, 38 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 61 代码量 (106 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 62.3% (38/61)
- 命名规范: 无命名违规

### 373. backend\assessments\migrations\0001_initial.py

**糟糕指数: 1.80**

> 行数: 191 总计, 114 代码, 70 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 114 代码量 (191 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 61.4% (70/114)
- 命名规范: 无命名违规

### 374. backend\common\config.py

**糟糕指数: 1.77**

> 行数: 319 总计, 240 代码, 14 注释 | 函数: 38 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_get_parser` | L26-33 | 8 | 3 | 2 | 0 | ✓ |
| `get_config_bool` | L93-110 | 18 | 3 | 1 | 3 | ✓ |
| `get_config_list` | L113-136 | 24 | 3 | 1 | 4 | ✓ |
| `get_config` | L36-52 | 17 | 2 | 1 | 3 | ✓ |
| `get_config_int` | L55-71 | 17 | 2 | 1 | 3 | ✓ |
| `get_config_float` | L74-90 | 17 | 2 | 1 | 3 | ✓ |
| `llm_provider` | L195-197 | 3 | 2 | 0 | 0 | ✓ |
| `llm_model` | L200-202 | 3 | 2 | 0 | 0 | ✓ |
| `llm_api_format` | L205-207 | 3 | 2 | 0 | 0 | ✓ |
| `graphrag_embedder_provider` | L226-228 | 3 | 2 | 0 | 0 | ✓ |
| `graphrag_sentence_model` | L231-237 | 7 | 2 | 0 | 0 | ✓ |
| `graphrag_qdrant_path` | L245-247 | 3 | 2 | 0 | 0 | ✓ |
| `reload_config` | L139-143 | 5 | 1 | 0 | 0 | ✓ |
| `password_min_length` | L152-154 | 3 | 1 | 0 | 0 | ✓ |
| `password_require_uppercase` | L157-159 | 3 | 1 | 0 | 0 | ✓ |
| `password_require_numbers` | L162-164 | 3 | 1 | 0 | 0 | ✓ |
| `password_require_special` | L167-169 | 3 | 1 | 0 | 0 | ✓ |
| `default_page_size` | L173-175 | 3 | 1 | 0 | 0 | ✓ |
| `max_page_size` | L178-180 | 3 | 1 | 0 | 0 | ✓ |
| `ai_api_timeout` | L184-186 | 3 | 1 | 0 | 0 | ✓ |
| `ai_feedback_enabled` | L189-191 | 3 | 1 | 0 | 0 | ✓ |
| `llm_base_url` | L210-212 | 3 | 1 | 0 | 0 | ✓ |
| `llm_request_timeout` | L215-217 | 3 | 1 | 0 | 0 | ✓ |
| `llm_max_retries` | L220-222 | 3 | 1 | 0 | 0 | ✓ |
| `graphrag_vector_dimension` | L240-242 | 3 | 1 | 0 | 0 | ✓ |
| `mastery_threshold` | L251-253 | 3 | 1 | 0 | 0 | ✓ |
| `activation_code_length` | L257-259 | 3 | 1 | 0 | 0 | ✓ |
| `activation_code_expiration_days` | L262-264 | 3 | 1 | 0 | 0 | ✓ |
| `invitation_code_length` | L268-270 | 3 | 1 | 0 | 0 | ✓ |
| `invitation_code_max_uses` | L273-275 | 3 | 1 | 0 | 0 | ✓ |
| `invitation_code_expiration_days` | L278-280 | 3 | 1 | 0 | 0 | ✓ |
| `exam_default_duration` | L284-286 | 3 | 1 | 0 | 0 | ✓ |
| `exam_pass_ratio` | L289-291 | 3 | 1 | 0 | 0 | ✓ |
| `max_file_size_mb` | L295-297 | 3 | 1 | 0 | 0 | ✓ |
| `allowed_image_formats` | L300-302 | 3 | 1 | 0 | 0 | ✓ |
| `allowed_document_formats` | L305-307 | 3 | 1 | 0 | 0 | ✓ |
| `max_path_nodes` | L311-313 | 3 | 1 | 0 | 0 | ✓ |
| `path_test_interval` | L316-318 | 3 | 1 | 0 | 0 | ✓ |

**全部问题 (1)**

- 📋 `get_config()` L36: 重复模式: get_config, get_config_int, get_config_float

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 3
- 认知复杂度: 平均: 1.8, 最大: 7
- 嵌套深度: 平均: 0.2, 最大: 2
- 函数长度: 平均: 5.3 行, 最大: 24 行
- 文件长度: 240 代码量 (319 总计)
- 参数数量: 平均: 0.4, 最大: 4
- 代码重复: 5.3% 重复 (2/38)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 5.8% (14/240)
- 命名规范: 发现 1 个违规

### 375. backend\knowledge\migrations\0001_initial.py

**糟糕指数: 1.75**

> 行数: 151 总计, 90 代码, 54 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 90 代码量 (151 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 60.0% (54/90)
- 命名规范: 无命名违规

### 376. backend\courses\migrations\0001_initial.py

**糟糕指数: 1.73**

> 行数: 90 总计, 52 代码, 31 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 52 代码量 (90 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 59.6% (31/52)
- 命名规范: 无命名违规

### 377. backend\users\migrations\0001_initial.py

**糟糕指数: 1.73**

> 行数: 125 总计, 74 代码, 44 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 74 代码量 (125 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 59.5% (44/74)
- 命名规范: 无命名违规

### 378. backend\tools\rebuild_demo.py

**糟糕指数: 1.66**

> 行数: 71 总计, 61 代码, 4 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `rebuild_demo_data` | L24-70 | 47 | 2 | 1 | 3 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 47.0 行, 最大: 47 行
- 文件长度: 61 代码量 (71 总计)
- 参数数量: 平均: 3.0, 最大: 3
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 6.6% (4/61)
- 命名规范: 无命名违规

### 379. backend\courses\admin_course_class_stats_views.py

**糟糕指数: 1.65**

> 行数: 54 总计, 41 代码, 1 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `admin_course_statistics` | L15-33 | 19 | 2 | 1 | 2 | ✓ |
| `admin_class_statistics` | L38-53 | 16 | 2 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 17.5 行, 最大: 19 行
- 文件长度: 41 代码量 (54 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 2.4% (1/41)
- 命名规范: 无命名违规

### 380. backend\courses\views.py

**糟糕指数: 1.64**

> 行数: 13 总计, 7 代码, 4 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 7 代码量 (13 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 57.1% (4/7)
- 命名规范: 无命名违规

### 381. backend\knowledge\urls.py

**糟糕指数: 1.61**

> 行数: 208 总计, 198 代码, 5 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 198 代码量 (208 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 2.5% (5/198)
- 命名规范: 无命名违规

### 382. frontend\src\utils\courseCover.ts

**糟糕指数: 1.60**

> 行数: 72 总计, 41 代码, 23 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `getGeometricDecorations` | L49-71 | 23 | 4 | 0 | 1 | ✗ |
| `generateCoverStyle` | L7-44 | 38 | 3 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 4
- 认知复杂度: 平均: 3.5, 最大: 4
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 30.5 行, 最大: 38 行
- 文件长度: 41 代码量 (72 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 56.1% (23/41)
- 命名规范: 无命名违规

### 383. backend\assessments\migrations\0004_alter_surveyquestion_options_and_more.py

**糟糕指数: 1.56**

> 行数: 167 总计, 104 代码, 57 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 104 代码量 (167 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 54.8% (57/104)
- 命名规范: 无命名违规

### 384. backend\users\migrations\0005_remove_habitpreference_reminder_settings.py

**糟糕指数: 1.55**

> 行数: 23 总计, 11 代码, 6 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 11 代码量 (23 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 54.5% (6/11)
- 命名规范: 无命名违规

### 385. frontend\src\main.ts

**糟糕指数: 1.53**

> 行数: 45 总计, 24 代码, 13 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 24 代码量 (45 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 54.2% (13/24)
- 命名规范: 无命名违规

### 386. frontend\src\composables\useAIProgress.ts

**糟糕指数: 1.53**

> 行数: 150 总计, 85 代码, 46 注释 | 函数: 6 | 类: 2

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `tick` | L78-99 | 22 | 3 | 1 | 0 | ✗ |
| `stop` | L124-130 | 7 | 2 | 1 | 0 | ✗ |
| `useAIProgress` | L48-149 | 48 | 1 | 0 | 1 | ✗ |
| `start` | L102-109 | 8 | 1 | 0 | 0 | ✗ |
| `complete` | L112-115 | 4 | 1 | 0 | 0 | ✗ |
| `reset` | L118-121 | 4 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 3
- 认知复杂度: 平均: 2.2, 最大: 5
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 15.5 行, 最大: 48 行
- 文件长度: 85 代码量 (150 总计)
- 参数数量: 平均: 0.2, 最大: 1
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 54.1% (46/85)
- 命名规范: 无命名违规

### 387. backend\courses\migrations\0005_announcement.py

**糟糕指数: 1.51**

> 行数: 49 总计, 28 代码, 15 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 28 代码量 (49 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 53.6% (15/28)
- 命名规范: 无命名违规

### 388. backend\exams\student_views.py

**糟糕指数: 1.48**

> 行数: 79 总计, 69 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 69 代码量 (79 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 2.9% (2/69)
- 命名规范: 无命名违规

### 389. backend\users\views.py

**糟糕指数: 1.38**

> 行数: 14 总计, 8 代码, 4 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 8 代码量 (14 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 50.0% (4/8)
- 命名规范: 无命名违规

### 390. backend\users\migrations\0004_alter_habitpreference_review_frequency.py

**糟糕指数: 1.38**

> 行数: 24 总计, 12 代码, 6 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 12 代码量 (24 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 50.0% (6/12)
- 命名规范: 无命名违规

### 391. backend\logs\migrations\0002_alter_operationlog_module.py

**糟糕指数: 1.38**

> 行数: 24 总计, 12 代码, 6 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 12 代码量 (24 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 50.0% (6/12)
- 命名规范: 无命名违规

### 392. backend\knowledge\migrations\0005_alter_knowledgerelation_relation_type.py

**糟糕指数: 1.38**

> 行数: 24 总计, 12 代码, 6 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 12 代码量 (24 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 50.0% (6/12)
- 命名规范: 无命名违规

### 393. backend\learning\migrations\0005_nodeprogress_extra_data.py

**糟糕指数: 1.38**

> 行数: 23 总计, 12 代码, 6 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 12 代码量 (23 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 50.0% (6/12)
- 命名规范: 无命名违规

### 394. backend\learning\migrations\0003_add_skipped_status.py

**糟糕指数: 1.38**

> 行数: 24 总计, 12 代码, 6 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 12 代码量 (24 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 50.0% (6/12)
- 命名规范: 无命名违规

### 395. backend\courses\migrations\0004_course_config.py

**糟糕指数: 1.38**

> 行数: 24 总计, 12 代码, 6 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 12 代码量 (24 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 50.0% (6/12)
- 命名规范: 无命名违规

### 396. backend\ai_services\migrations\0003_add_chat_kt_call_types.py

**糟糕指数: 1.38**

> 行数: 24 总计, 12 代码, 6 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 12 代码量 (24 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 50.0% (6/12)
- 命名规范: 无命名违规

### 397. frontend\src\utils\logger.ts

**糟糕指数: 1.35**

> 行数: 55 总计, 40 代码, 6 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `installConsoleFormat` | L37-54 | 10 | 2 | 1 | 1 | ✗ |
| `formatTime` | L8-15 | 8 | 1 | 0 | 1 | ✗ |
| `formatPrefix` | L17-19 | 3 | 1 | 0 | 2 | ✗ |
| `output` | L21-25 | 5 | 1 | 0 | 4 | ✗ |
| `createLogger` | L27-35 | 5 | 1 | 0 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.2, 最大: 2
- 认知复杂度: 平均: 1.6, 最大: 4
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 6.2 行, 最大: 10 行
- 文件长度: 40 代码量 (55 总计)
- 参数数量: 平均: 1.8, 最大: 4
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 15.0% (6/40)
- 命名规范: 无命名违规

### 398. backend\users\migrations\0002_habitpreference_accept_challenge_and_more.py

**糟糕指数: 1.34**

> 行数: 179 总计, 116 代码, 57 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 116 代码量 (179 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 49.1% (57/116)
- 命名规范: 无命名违规

### 399. backend\tools\cli.py

**糟糕指数: 1.32**

> 行数: 36 总计, 21 代码, 2 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `main` | L23-32 | 10 | 2 | 1 | 0 | ✓ |
| `_dispatch_command` | L18-20 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- 🏷️ `_dispatch_command()` L18: "_dispatch_command" - snake_case

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 2
- 认知复杂度: 平均: 2.5, 最大: 4
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 6.5 行, 最大: 10 行
- 文件长度: 21 代码量 (36 总计)
- 参数数量: 平均: 0.5, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 9.5% (2/21)
- 命名规范: 发现 1 个违规

### 400. backend\users\migrations\0003_alter_user_email_alter_user_phone.py

**糟糕指数: 1.27**

> 行数: 31 总计, 17 代码, 8 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 17 代码量 (31 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 47.1% (8/17)
- 命名规范: 无命名违规

### 401. backend\learning\migrations\0004_pathnode_estimated_minutes_pathnode_node_type.py

**糟糕指数: 1.27**

> 行数: 31 总计, 17 代码, 8 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 17 代码量 (31 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 47.1% (8/17)
- 命名规范: 无命名违规

### 402. backend\assessments\migrations\0006_assessmentstatus_generating_and_more.py

**糟糕指数: 1.27**

> 行数: 31 总计, 17 代码, 8 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 17 代码量 (31 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 47.1% (8/17)
- 命名规范: 无命名违规

### 403. backend\assessments\migrations\0005_question_chapter_question_suggested_score.py

**糟糕指数: 1.27**

> 行数: 31 总计, 17 代码, 8 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 17 代码量 (31 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 47.1% (8/17)
- 命名规范: 无命名违规

### 404. backend\assessments\migrations\0002_initial.py

**糟糕指数: 1.25**

> 行数: 29 总计, 15 代码, 7 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 15 代码量 (29 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 46.7% (7/15)
- 命名规范: 无命名违规

### 405. backend\knowledge\migrations\0004_resource_chapter_number_resource_duration_and_more.py

**糟糕指数: 1.20**

> 行数: 38 总计, 22 代码, 10 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 22 代码量 (38 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 45.5% (10/22)
- 命名规范: 无命名违规

### 406. backend\common\defense_demo.py

**糟糕指数: 1.20**

> 行数: 59 总计, 54 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 54 代码量 (59 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 3.7% (2/54)
- 命名规范: 无命名违规

### 407. backend\courses\migrations\0003_alter_class_options_class_description_and_more.py

**糟糕指数: 1.16**

> 行数: 94 总计, 61 代码, 27 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 61 代码量 (94 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 44.3% (27/61)
- 命名规范: 无命名违规

### 408. backend\ai_services\migrations\0002_initial.py

**糟糕指数: 1.14**

> 行数: 30 总计, 16 代码, 7 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 16 代码量 (30 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 43.8% (7/16)
- 命名规范: 无命名违规

### 409. backend\common\permissions.py

**糟糕指数: 1.12**

> 行数: 90 总计, 57 代码, 4 注释 | 函数: 6 | 类: 6

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `has_permission` | L56-79 | 24 | 5 | 1 | 3 | ✗ |
| `has_object_permission` | L40-50 | 11 | 4 | 1 | 4 | ✗ |
| `has_permission` | L26-27 | 2 | 3 | 0 | 3 | ✗ |
| `has_permission` | L12-13 | 2 | 2 | 0 | 3 | ✗ |
| `has_permission` | L19-20 | 2 | 2 | 0 | 3 | ✗ |
| `has_permission` | L33-34 | 2 | 2 | 0 | 3 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 5
- 认知复杂度: 平均: 3.7, 最大: 7
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 7.2 行, 最大: 24 行
- 文件长度: 57 代码量 (90 总计)
- 参数数量: 平均: 3.2, 最大: 4
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 7.0% (4/57)
- 命名规范: 无命名违规

### 410. backend\knowledge\migrations\0003_knowledgepoint_category_and_more.py

**糟糕指数: 1.12**

> 行数: 59 总计, 37 代码, 16 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 37 代码量 (59 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 43.2% (16/37)
- 命名规范: 无命名违规

### 411. frontend\src\stores\assessment.ts

**糟糕指数: 1.09**

> 行数: 316 总计, 200 代码, 85 注释 | 函数: 12 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `submit` | L194-235 | 32 | 4 | 1 | 1 | ✓ |
| `fetchStatus` | L86-109 | 24 | 3 | 1 | 1 | ✓ |
| `startAssessment` | L117-141 | 22 | 3 | 0 | 2 | ✓ |
| `prevQuestion` | L164-168 | 5 | 2 | 1 | 0 | ✓ |
| `nextQuestion` | L173-177 | 5 | 2 | 1 | 0 | ✓ |
| `goToQuestion` | L183-187 | 5 | 2 | 1 | 1 | ✓ |
| `generateLearnerProfile` | L242-252 | 11 | 2 | 0 | 1 | ✓ |
| `setAnswer` | L148-150 | 3 | 1 | 0 | 2 | ✓ |
| `getAnswer` | L157-159 | 3 | 1 | 0 | 1 | ✓ |
| `reset` | L258-263 | 6 | 1 | 0 | 0 | ✓ |
| `canSubmit` | L269-271 | 3 | 1 | 0 | 0 | ✓ |
| `getUnansweredIndices` | L277-282 | 3 | 1 | 0 | 0 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.9, 最大: 4
- 认知复杂度: 平均: 2.8, 最大: 6
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 10.2 行, 最大: 32 行
- 文件长度: 200 代码量 (316 总计)
- 参数数量: 平均: 0.8, 最大: 2
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 42.5% (85/200)
- 命名规范: 无命名违规

### 412. frontend\src\router\routes\auth.ts

**糟糕指数: 1.06**

> 行数: 37 总计, 24 代码, 10 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `LoginView` | L7-7 | 1 | 1 | 0 | 0 | ✗ |
| `RegisterView` | L8-8 | 1 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 1.0 行, 最大: 1 行
- 文件长度: 24 代码量 (37 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 41.7% (10/24)
- 命名规范: 无命名违规

### 413. backend\wisdom_edu_api\urls.py

**糟糕指数: 1.02**

> 行数: 58 总计, 37 代码, 15 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 37 代码量 (58 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 40.5% (15/37)
- 命名规范: 无命名违规

### 414. backend\platform_ai\__init__.py

**糟糕指数: 1.00**

> 行数: 11 总计, 5 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 5 代码量 (11 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 40.0% (2/5)
- 命名规范: 无命名违规

### 415. backend\courses\migrations\0002_initial.py

**糟糕指数: 1.00**

> 行数: 63 总计, 40 代码, 16 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 40 代码量 (63 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 40.0% (16/40)
- 命名规范: 无命名违规

### 416. backend\exams\migrations\0003_alter_feedbackreport_unique_together_and_more.py

**糟糕指数: 0.96**

> 行数: 52 总计, 33 代码, 13 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 33 代码量 (52 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 39.4% (13/33)
- 命名规范: 无命名违规

### 417. backend\ai_services\urls.py

**糟糕指数: 0.94**

> 行数: 99 总计, 90 代码, 4 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 90 代码量 (99 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 4.4% (4/90)
- 命名规范: 无命名违规

### 418. backend\learning\views.py

**糟糕指数: 0.87**

> 行数: 48 总计, 43 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 43 代码量 (48 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 4.7% (2/43)
- 命名规范: 无命名违规

### 419. backend\exams\migrations\0002_initial.py

**糟糕指数: 0.87**

> 行数: 105 总计, 71 代码, 27 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 71 代码量 (105 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 38.0% (27/71)
- 命名规范: 无命名违规

### 420. backend\knowledge\migrations\0002_initial.py

**糟糕指数: 0.86**

> 行数: 116 总计, 79 代码, 30 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 79 代码量 (116 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 38.0% (30/79)
- 命名规范: 无命名违规

### 421. backend\assessments\migrations\0003_initial.py

**糟糕指数: 0.86**

> 行数: 138 总计, 95 代码, 36 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 95 代码量 (138 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 37.9% (36/95)
- 命名规范: 无命名违规

### 422. backend\learning\migrations\0002_initial.py

**糟糕指数: 0.83**

> 行数: 84 总计, 56 代码, 21 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 56 代码量 (84 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 37.5% (21/56)
- 命名规范: 无命名违规

### 423. frontend\src\router\index.ts

**糟糕指数: 0.67**

> 行数: 117 总计, 74 代码, 26 注释 | 函数: 7 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `wrapWithLayout` | L55-76 | 22 | 2 | 1 | 2 | ✗ |
| `scrollBehavior` | L105-111 | 7 | 2 | 1 | 3 | ✓ |
| `DefaultLayout` | L13-13 | 1 | 1 | 0 | 0 | ✗ |
| `AuthLayout` | L14-14 | 1 | 1 | 0 | 0 | ✗ |
| `EmptyLayout` | L15-15 | 1 | 1 | 0 | 0 | ✗ |
| `NotFoundView` | L17-17 | 1 | 1 | 0 | 0 | ✗ |
| `ForbiddenView` | L18-18 | 1 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.3, 最大: 2
- 认知复杂度: 平均: 1.9, 最大: 4
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 4.9 行, 最大: 22 行
- 文件长度: 74 代码量 (117 总计)
- 参数数量: 平均: 0.7, 最大: 3
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 35.1% (26/74)
- 命名规范: 无命名违规

### 424. backend\logs\urls.py

**糟糕指数: 0.67**

> 行数: 24 总计, 18 代码, 1 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 18 代码量 (24 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 5.6% (1/18)
- 命名规范: 无命名违规

### 425. backend\courses\signals.py

**糟糕指数: 0.67**

> 行数: 27 总计, 18 代码, 1 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `cleanup_deleted_course_artifacts` | L18-27 | 10 | 4 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 6.0, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 10.0 行, 最大: 10 行
- 文件长度: 18 代码量 (27 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 5.6% (1/18)
- 命名规范: 无命名违规

### 426. backend\ai_services\services\mefkt_loader.py

**糟糕指数: 0.66**

> 行数: 37 总计, 26 代码, 2 注释 | 函数: 2 | 类: 1

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `auto_load_mefkt_model` | L21-36 | 16 | 4 | 2 | 3 | ✓ |
| `load_model` | L17-18 | 2 | 1 | 0 | 3 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 4
- 认知复杂度: 平均: 4.5, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 9.0 行, 最大: 16 行
- 文件长度: 26 代码量 (37 总计)
- 参数数量: 平均: 3.0, 最大: 3
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 7.7% (2/26)
- 命名规范: 无命名违规

### 427. frontend\src\router\routes\teacher.ts

**糟糕指数: 0.66**

> 行数: 210 总计, 196 代码, 11 注释 | 函数: 12 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `DashboardView` | L7-7 | 1 | 1 | 0 | 0 | ✗ |
| `CourseListView` | L8-8 | 1 | 1 | 0 | 0 | ✗ |
| `CourseDetailView` | L9-9 | 1 | 1 | 0 | 0 | ✗ |
| `CourseEditView` | L10-10 | 1 | 1 | 0 | 0 | ✗ |
| `ClassListView` | L11-11 | 1 | 1 | 0 | 0 | ✗ |
| `ClassDetailView` | L12-12 | 1 | 1 | 0 | 0 | ✗ |
| `KnowledgeManageView` | L13-13 | 1 | 1 | 0 | 0 | ✗ |
| `QuestionListView` | L14-14 | 1 | 1 | 0 | 0 | ✗ |
| `ExamManageView` | L15-15 | 1 | 1 | 0 | 0 | ✗ |
| `ResourceManageView` | L16-16 | 1 | 1 | 0 | 0 | ✗ |
| `StudentProfileView` | L17-17 | 1 | 1 | 0 | 0 | ✗ |
| `SettingsView` | L18-18 | 1 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 1.0 行, 最大: 1 行
- 文件长度: 196 代码量 (210 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 5.6% (11/196)
- 命名规范: 无命名违规

### 428. backend\manage.py

**糟糕指数: 0.62**

> 行数: 23 总计, 17 代码, 1 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `main` | L7-18 | 12 | 2 | 1 | 0 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 12.0 行, 最大: 12 行
- 文件长度: 17 代码量 (23 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 5.9% (1/17)
- 命名规范: 无命名违规

### 429. backend\models\MEFKT\__init__.py

**糟糕指数: 0.59**

> 行数: 37 总计, 33 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 33 代码量 (37 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 6.1% (2/33)
- 命名规范: 无命名违规

### 430. frontend\src\router\routes\student.ts

**糟糕指数: 0.58**

> 行数: 228 总计, 212 代码, 13 注释 | 函数: 19 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `DashboardView` | L7-7 | 1 | 1 | 0 | 0 | ✗ |
| `AssessmentView` | L8-8 | 1 | 1 | 0 | 0 | ✗ |
| `AssessmentKnowledgeView` | L9-9 | 1 | 1 | 0 | 0 | ✗ |
| `AssessmentAbilityView` | L10-10 | 1 | 1 | 0 | 0 | ✗ |
| `AssessmentHabitView` | L11-11 | 1 | 1 | 0 | 0 | ✗ |
| `AssessmentReportView` | L12-12 | 1 | 1 | 0 | 0 | ✗ |
| `ProfileView` | L13-13 | 1 | 1 | 0 | 0 | ✗ |
| `KnowledgeMapView` | L14-14 | 1 | 1 | 0 | 0 | ✗ |
| `LearningPathView` | L15-15 | 1 | 1 | 0 | 0 | ✗ |
| `TaskLearningView` | L16-16 | 1 | 1 | 0 | 0 | ✗ |
| `AIAssistantView` | L17-17 | 1 | 1 | 0 | 0 | ✗ |
| `ExamView` | L18-18 | 1 | 1 | 0 | 0 | ✗ |
| `ExamTakingView` | L19-19 | 1 | 1 | 0 | 0 | ✗ |
| `ClassesView` | L20-20 | 1 | 1 | 0 | 0 | ✗ |
| `ClassDetailView` | L21-21 | 1 | 1 | 0 | 0 | ✗ |
| `CourseSelectView` | L22-22 | 1 | 1 | 0 | 0 | ✗ |
| `SettingsView` | L23-23 | 1 | 1 | 0 | 0 | ✗ |
| `FeedbackReportView` | L24-24 | 1 | 1 | 0 | 0 | ✗ |
| `ResourceListView` | L25-25 | 1 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 1.0 行, 最大: 1 行
- 文件长度: 212 代码量 (228 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 0.0% 重复 (0/19)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 6.1% (13/212)
- 命名规范: 无命名违规

### 431. backend\exams\views.py

**糟糕指数: 0.56**

> 行数: 10 总计, 6 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 6 代码量 (10 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 33.3% (2/6)
- 命名规范: 无命名违规

### 432. frontend\src\env.d.ts

**糟糕指数: 0.34**

> 行数: 19 总计, 13 代码, 1 注释 | 函数: 0 | 类: 2

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 13 代码量 (19 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 7.7% (1/13)
- 命名规范: 无命名违规

### 433. backend\knowledge\migrations\0006_knowledgepoint_introduction_fields.py

**糟糕指数: 0.31**

> 行数: 39 总计, 27 代码, 8 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 27 代码量 (39 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 29.6% (8/27)
- 命名规范: 无命名违规

### 434. backend\models\MEFKT\model.py

**糟糕指数: 0.30**

> 行数: 32 总计, 25 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 25 代码量 (32 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 8.0% (2/25)
- 命名规范: 无命名违规

### 435. backend\tools\dkt_paths.py

**糟糕指数: 0.24**

> 行数: 13 总计, 7 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 7 代码量 (13 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 28.6% (2/7)
- 命名规范: 无命名违规

### 436. backend\models\DKT\KnowledgeTracing\Constant\Constants.py

**糟糕指数: 0.17**

> 行数: 42 总计, 29 代码, 8 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 29 代码量 (42 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 27.6% (8/29)
- 命名规范: 无命名违规

### 437. frontend\vite.config.ts

**糟糕指数: 0.00**

> 行数: 115 总计, 92 代码, 16 注释 | 函数: 3 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `manualChunks` | L81-107 | 27 | 5 | 1 | 1 | ✗ |
| `normalizeProxyTarget` | L9-11 | 3 | 1 | 0 | 2 | ✓ |
| `closeBundle` | L34-39 | 6 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 5
- 认知复杂度: 平均: 3.0, 最大: 7
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 12.0 行, 最大: 27 行
- 文件长度: 92 代码量 (115 总计)
- 参数数量: 平均: 1.0, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 17.4% (16/92)
- 命名规范: 无命名违规

### 438. backend\users\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 439. backend\users\urls.py

**糟糕指数: 0.00**

> 行数: 62 总计, 46 代码, 7 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 46 代码量 (62 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 15.2% (7/46)
- 命名规范: 无命名违规

### 440. backend\wisdom_edu_api\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 441. backend\tools\__init__.py

**糟糕指数: 0.00**

> 行数: 164 总计, 143 代码, 17 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 143 代码量 (164 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 11.9% (17/143)
- 命名规范: 无命名违规

### 442. backend\tools\mefkt_paths.py

**糟糕指数: 0.00**

> 行数: 15 总计, 9 代码, 2 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 9 代码量 (15 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 22.2% (2/9)
- 命名规范: 无命名违规

### 443. backend\logs\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 444. backend\knowledge\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 445. backend\learning\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 446. backend\learning\urls.py

**糟糕指数: 0.00**

> 行数: 36 总计, 28 代码, 3 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 28 代码量 (36 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 10.7% (3/28)
- 命名规范: 无命名违规

### 447. backend\common\__init__.py

**糟糕指数: 0.00**

> 行数: 13 总计, 8 代码, 2 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 8 代码量 (13 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 25.0% (2/8)
- 命名规范: 无命名违规

### 448. backend\common\urls.py

**糟糕指数: 0.00**

> 行数: 15 总计, 9 代码, 1 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 9 代码量 (15 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 11.1% (1/9)
- 命名规范: 无命名违规

### 449. backend\exams\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 450. backend\exams\urls.py

**糟糕指数: 0.00**

> 行数: 56 总计, 41 代码, 7 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 41 代码量 (56 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 17.1% (7/41)
- 命名规范: 无命名违规

### 451. backend\courses\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 452. backend\courses\urls.py

**糟糕指数: 0.00**

> 行数: 86 总计, 62 代码, 11 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 62 代码量 (86 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 17.7% (11/62)
- 命名规范: 无命名违规

### 453. backend\courses\apps.py

**糟糕指数: 0.00**

> 行数: 21 总计, 15 代码, 2 注释 | 函数: 1 | 类: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ready` | L17-20 | 4 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.0 行, 最大: 4 行
- 文件长度: 15 代码量 (21 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 13.3% (2/15)
- 命名规范: 无命名违规

### 454. backend\assessments\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 455. backend\assessments\urls.py

**糟糕指数: 0.00**

> 行数: 41 总计, 26 代码, 6 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 26 代码量 (41 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 23.1% (6/26)
- 命名规范: 无命名违规

### 456. backend\ai_services\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 457. backend\users\migrations\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 458. backend\logs\migrations\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 459. backend\knowledge\migrations\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 460. backend\learning\migrations\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 461. backend\common\migrations\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 462. backend\exams\migrations\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 463. backend\courses\migrations\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 464. backend\assessments\migrations\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 465. backend\ai_services\migrations\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 466. frontend\src\router\routes\admin.ts

**糟糕指数: 0.00**

> 行数: 96 总计, 82 代码, 11 注释 | 函数: 7 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `DashboardView` | L7-7 | 1 | 1 | 0 | 0 | ✗ |
| `UserManageView` | L8-8 | 1 | 1 | 0 | 0 | ✗ |
| `ActivationCodeView` | L9-9 | 1 | 1 | 0 | 0 | ✗ |
| `LogView` | L10-10 | 1 | 1 | 0 | 0 | ✗ |
| `CourseManageView` | L11-11 | 1 | 1 | 0 | 0 | ✗ |
| `ClassManageView` | L12-12 | 1 | 1 | 0 | 0 | ✗ |
| `SettingsView` | L13-13 | 1 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 1.0 行, 最大: 1 行
- 文件长度: 82 代码量 (96 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 13.4% (11/82)
- 命名规范: 无命名违规

### 467. frontend\src\api\admin\index.ts

**糟糕指数: 0.00**

> 行数: 29 总计, 25 代码, 3 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 25 代码量 (29 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 12.0% (3/25)
- 命名规范: 无命名违规

### 468. backend\models\DKT\KnowledgeTracing\model\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 469. backend\models\DKT\KnowledgeTracing\data\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 470. backend\models\DKT\KnowledgeTracing\evaluation\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

### 471. backend\models\DKT\KnowledgeTracing\Constant\__init__.py

**糟糕指数: 0.00**

> 行数: 1 总计, 0 代码, 0 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 0 代码量 (1 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 无代码行
- 命名规范: 无命名违规

## 最差函数 Top 10

| 函数 | 文件 | 复杂度 | 嵌套 | 行数 |
|:-----|:-----|------:|------:|------:|
| `resource_update` | backend\knowledge\teacher_resource_views.py | 24 | 2 | 70 |
| `update_userinfo` | backend\users\auth_views.py | 22 | 4 | 66 |
| `admin_user_import` | backend\users\admin_user_management_views.py | 21 | 3 | 54 |
| `build_excel_question_payload` | backend\tools\question_import_support.py | 20 | 1 | 44 |
| `_handle_kt_menu_choice` | backend\tools\cli_menu.py | 19 | 1 | 48 |
| `question_detail` | backend\knowledge\teacher_question_views.py | 19 | 3 | 61 |
| `resource_list` | backend\knowledge\teacher_resource_views.py | 18 | 3 | 53 |
| `resource_create` | backend\knowledge\teacher_resource_views.py | 18 | 2 | 65 |
| `course_create` | backend\courses\teacher_course_views.py | 18 | 4 | 65 |
| `userinfo` | backend\users\auth_views.py | 17 | 3 | 92 |

## 诊断结论 {#conclusion}

🌸 **偶有异味** - 基本没事，但是有伤风化

👍 继续保持，你是编码界的一股清流，代码洁癖者的骄傲

---

*由 [fuck-u-code](https://github.com/Done-0/fuck-u-code) 生成*