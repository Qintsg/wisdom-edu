# 🌸 屎山代码分析报告 🌸

## 📑 目录

- [糟糕指数](#overall-score)
- [评分指标详情](#metrics-details)
- [最屎代码排行榜](#problem-files)
- [诊断结论](#conclusion)

![Score](https://img.shields.io/badge/Score-93%25-brightgreen)

## 糟糕指数 {#overall-score}

| 指标摘要 | 评分 |
|------|-------|
| **糟糕指数** | **93.01/100** |
| 屎山等级 | 🌸 偶有异味 |

> 如沐春风，仿佛被天使亲吻过

### 📊 统计信息

| 指标 | 数值 |
|--------|-------|
| 总文件数 | 500 |
| 已跳过 | 100908 |
| 耗时 | 8762ms |

### 📋 项目概览

| 指标 | 数值 |
|--------|-------|
| 总代码行数 | 58426 |
| 总注释行数 | 10548 |
| 整体注释比例 | 18.1% |
| 平均文件大小 | 157 行 |
| 最大文件 | `backend\ai_services\services\llm_service.py` (555) |

#### 语言分布

| 语言 | 文件数 |
|:-----|------:|
| Python | 418 |
| TypeScript | 49 |
| JavaScript | 33 |

## 评分指标详情 {#metrics-details}

| 指标摘要 | 评分 | Min | Max | Median | 状态 |
|:-----|------:|------:|------:|------:|:------:|
| 循环复杂度 | 3.48% | 0.0% | 40.5% | 0.0% | ✓✓ |
| 认知复杂度 | 4.81% | 0.0% | 41.9% | 0.0% | ✓✓ |
| 嵌套深度 | 0.24% | 0.0% | 10.0% | 0.0% | ✓✓ |
| 函数长度 | 4.44% | 0.0% | 75.9% | 0.0% | ✓✓ |
| 文件长度 | 0.33% | 0.0% | 14.1% | 0.0% | ✓✓ |
| 参数数量 | 7.22% | 0.0% | 98.5% | 0.0% | ✓✓ |
| 代码重复 | 2.99% | 0.0% | 94.2% | 0.0% | ✓✓ |
| 结构分析 | 0.75% | 0.0% | 20.0% | 0.0% | ✓✓ |
| 错误处理 | 17.06% | 0.0% | 98.8% | 0.0% | ✓✓ |
| 注释比例 | 30.74% | 0.0% | 100.0% | 6.1% | ✓ |
| 命名规范 | 12.87% | 0.0% | 100.0% | 0.0% | ✓✓ |

## 最屎代码排行榜 {#problem-files}

### 1. backend\common\neo4j_crud.py

**糟糕指数: 17.60**

> 行数: 276 总计, 226 代码, 27 注释 | 函数: 8 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 📋 重复问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `sync_single_point` | L20-63 | 44 | 14 | 2 | 2 | ✓ |
| `has_course_graphrag_projection` | L188-207 | 20 | 5 | 2 | 2 | ✓ |
| `delete_point_neo4j` | L68-86 | 19 | 4 | 2 | 2 | ✓ |
| `sync_single_relation` | L91-123 | 33 | 4 | 2 | 2 | ✓ |
| `delete_relation_neo4j` | L128-150 | 23 | 4 | 2 | 3 | ✓ |
| `clear_course_graph` | L155-183 | 29 | 4 | 2 | 2 | ✓ |
| `sync_course_graphrag_projection` | L212-275 | 25 | 3 | 1 | 4 | ✓ |
| `sync_projection_tx` | L229-267 | 39 | 3 | 1 | 1 | ✗ |

**全部问题 (4)**

- 🔄 `sync_single_point()` L20: 复杂度: 14
- 🔄 `sync_single_point()` L20: 认知复杂度: 18
- 📋 `delete_point_neo4j()` L68: 重复模式: delete_point_neo4j, delete_relation_neo4j, has_course_graphrag_projection
- 📋 `sync_single_relation()` L91: 重复模式: sync_single_relation, clear_course_graph

**详情**:
- 循环复杂度: 平均: 5.1, 最大: 14
- 认知复杂度: 平均: 8.6, 最大: 18
- 嵌套深度: 平均: 1.8, 最大: 2
- 函数长度: 平均: 29.0 行, 最大: 44 行
- 文件长度: 226 代码量 (276 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 37.5% 重复 (3/8)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 11.9% (27/226)
- 命名规范: 无命名违规

### 2. backend\tools\api_smoke.py

**糟糕指数: 17.23**

> 行数: 225 总计, 183 代码, 18 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `student_flow_smoke` | L116-215 | 100 | 15 | 3 | 5 | ✓ |
| `api_smoke` | L22-110 | 89 | 14 | 2 | 5 | ✓ |
| `test_business_logic` | L221-224 | 4 | 1 | 0 | 0 | ✓ |

**全部问题 (7)**

- 🔄 `api_smoke()` L22: 复杂度: 14
- 🔄 `student_flow_smoke()` L116: 复杂度: 15
- 🔄 `api_smoke()` L22: 认知复杂度: 18
- 🔄 `student_flow_smoke()` L116: 认知复杂度: 21
- 📏 `api_smoke()` L22: 89 代码量
- 📏 `student_flow_smoke()` L116: 100 代码量
- 🏗️ `student_flow_smoke()` L116: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 10.0, 最大: 15
- 认知复杂度: 平均: 13.3, 最大: 21
- 嵌套深度: 平均: 1.7, 最大: 3
- 函数长度: 平均: 64.3 行, 最大: 100 行
- 文件长度: 183 代码量 (225 总计)
- 参数数量: 平均: 3.3, 最大: 5
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 1 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 9.8% (18/183)
- 命名规范: 无命名违规

### 3. backend\tools\questions.py

**糟糕指数: 16.74**

> 行数: 231 总计, 183 代码, 19 注释 | 函数: 5 | 类: 0

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 3, 📋 重复问题: 1, 🏗️ 结构问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_questions_json` | L94-167 | 74 | 13 | 3 | 4 | ✓ |
| `import_question_bank` | L173-225 | 53 | 7 | 3 | 3 | ✓ |
| `print_json_import_summary` | L64-73 | 10 | 4 | 1 | 2 | ✓ |
| `print_excel_import_summary` | L79-88 | 10 | 4 | 1 | 1 | ✓ |
| `build_result_payload` | L39-58 | 20 | 1 | 0 | 5 | ✓ |

**全部问题 (8)**

- 🔄 `import_questions_json()` L94: 复杂度: 13
- 🔄 `import_questions_json()` L94: 认知复杂度: 19
- 🔄 `import_question_bank()` L173: 认知复杂度: 13
- 📏 `import_questions_json()` L94: 74 代码量
- 📏 `import_question_bank()` L173: 53 代码量
- 📋 `print_json_import_summary()` L64: 重复模式: print_json_import_summary, print_excel_import_summary
- 🏗️ `import_questions_json()` L94: 中等嵌套: 3
- 🏗️ `import_question_bank()` L173: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 5.8, 最大: 13
- 认知复杂度: 平均: 9.0, 最大: 19
- 嵌套深度: 平均: 1.6, 最大: 3
- 函数长度: 平均: 33.4 行, 最大: 74 行
- 文件长度: 183 代码量 (231 总计)
- 参数数量: 平均: 3.0, 最大: 5
- 代码重复: 20.0% 重复 (1/5)
- 结构分析: 2 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 10.4% (19/183)
- 命名规范: 无命名违规

### 4. backend\common\defense_demo_assessment_state.py

**糟糕指数: 16.27**

> 行数: 238 总计, 195 代码, 19 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_demo_student_answer` | L102-151 | 50 | 11 | 3 | 2 | ✓ |
| `_seed_demo_practice_histories` | L157-237 | 81 | 7 | 2 | 4 | ✓ |
| `_ensure_demo_assessment_state` | L37-96 | 60 | 1 | 0 | 4 | ✓ |

**全部问题 (12)**

- 🔄 `_build_demo_student_answer()` L102: 复杂度: 11
- 🔄 `_build_demo_student_answer()` L102: 认知复杂度: 17
- 📏 `_ensure_demo_assessment_state()` L37: 60 代码量
- 📏 `_seed_demo_practice_histories()` L157: 81 代码量
- 🏗️ `_build_demo_student_answer()` L102: 中等嵌套: 3
- ❌ L118: 未处理的易出错调用
- ❌ L120: 未处理的易出错调用
- ❌ L140: 未处理的易出错调用
- ❌ L214: 未处理的易出错调用
- 🏷️ `_ensure_demo_assessment_state()` L37: "_ensure_demo_assessment_state" - snake_case
- 🏷️ `_build_demo_student_answer()` L102: "_build_demo_student_answer" - snake_case
- 🏷️ `_seed_demo_practice_histories()` L157: "_seed_demo_practice_histories" - snake_case

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 11
- 认知复杂度: 平均: 9.7, 最大: 17
- 嵌套深度: 平均: 1.7, 最大: 3
- 函数长度: 平均: 63.7 行, 最大: 81 行
- 文件长度: 195 代码量 (238 总计)
- 参数数量: 平均: 3.3, 最大: 4
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 1 个结构问题
- 错误处理: 4/8 个错误被忽略 (50.0%)
- 注释比例: 9.7% (19/195)
- 命名规范: 发现 3 个违规

### 5. backend\exams\teacher_exam_management_views.py

**糟糕指数: 16.21**

> 行数: 430 总计, 336 代码, 27 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 4, 🏗️ 结构问题: 3, ❌ 错误处理问题: 5, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `exam_update` | L229-293 | 65 | 17 | 3 | 2 | ✓ |
| `exam_publish` | L134-161 | 28 | 8 | 2 | 2 | ✓ |
| `exam_teacher_detail` | L169-221 | 53 | 8 | 1 | 2 | ✓ |
| `teacher_exam_add_questions` | L365-394 | 30 | 8 | 3 | 2 | ✓ |
| `exam_create` | L72-126 | 55 | 7 | 3 | 1 | ✓ |
| `exam_delete` | L301-325 | 25 | 5 | 1 | 2 | ✓ |
| `exam_unpublish` | L333-357 | 25 | 5 | 1 | 2 | ✓ |
| `teacher_exam_remove_questions` | L402-416 | 15 | 4 | 1 | 2 | ✓ |
| `exam_manage_list` | L31-64 | 34 | 3 | 1 | 1 | ✓ |

**全部问题 (15)**

- 🔄 `exam_update()` L229: 复杂度: 17
- 🔄 `exam_create()` L72: 认知复杂度: 13
- 🔄 `exam_update()` L229: 认知复杂度: 23
- 🔄 `teacher_exam_add_questions()` L365: 认知复杂度: 14
- 📏 `exam_create()` L72: 55 代码量
- 📏 `exam_teacher_detail()` L169: 53 代码量
- 📏 `exam_update()` L229: 65 代码量
- 🏗️ `exam_create()` L72: 中等嵌套: 3
- 🏗️ `exam_update()` L229: 中等嵌套: 3
- 🏗️ `teacher_exam_add_questions()` L365: 中等嵌套: 3
- ❌ L81: 未处理的易出错调用
- ❌ L82: 未处理的易出错调用
- ❌ L191: 未处理的易出错调用
- ❌ L323: 未处理的易出错调用
- ❌ L413: 忽略了错误返回值

**详情**:
- 循环复杂度: 平均: 7.2, 最大: 17
- 认知复杂度: 平均: 10.8, 最大: 23
- 嵌套深度: 平均: 1.8, 最大: 3
- 函数长度: 平均: 36.7 行, 最大: 65 行
- 文件长度: 336 代码量 (430 总计)
- 参数数量: 平均: 1.8, 最大: 2
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 3 个结构问题
- 错误处理: 5/27 个错误被忽略 (18.5%)
- 注释比例: 8.0% (27/336)
- 命名规范: 无命名违规

### 6. backend\assessments\status_profile_views.py

**糟糕指数: 15.58**

> 行数: 135 总计, 108 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_assessment_status` | L24-89 | 66 | 13 | 2 | 1 | ✓ |
| `generate_course_profile` | L97-134 | 38 | 6 | 1 | 1 | ✓ |

**全部问题 (7)**

- 🔄 `get_assessment_status()` L24: 复杂度: 13
- 🔄 `get_assessment_status()` L24: 认知复杂度: 17
- 📏 `get_assessment_status()` L24: 66 代码量
- ❌ L123: 未处理的易出错调用
- ❌ L128: 未处理的易出错调用
- ❌ L129: 未处理的易出错调用
- ❌ L130: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 9.5, 最大: 13
- 认知复杂度: 平均: 12.5, 最大: 17
- 嵌套深度: 平均: 1.5, 最大: 2
- 函数长度: 平均: 52.0 行, 最大: 66 行
- 文件长度: 108 代码量 (135 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 4/8 个错误被忽略 (50.0%)
- 注释比例: 5.6% (6/108)
- 命名规范: 无命名违规

### 7. backend\assessments\knowledge_views.py

**糟糕指数: 15.50**

> 行数: 295 总计, 253 代码, 9 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_knowledge_result` | L238-294 | 57 | 11 | 2 | 1 | ✓ |
| `submit_knowledge_assessment` | L133-230 | 98 | 9 | 2 | 1 | ✓ |
| `get_knowledge_assessment` | L54-125 | 72 | 7 | 2 | 1 | ✓ |

**全部问题 (10)**

- 🔄 `get_knowledge_result()` L238: 复杂度: 11
- 🔄 `submit_knowledge_assessment()` L133: 认知复杂度: 13
- 🔄 `get_knowledge_result()` L238: 认知复杂度: 15
- 📏 `get_knowledge_assessment()` L54: 72 代码量
- 📏 `submit_knowledge_assessment()` L133: 98 代码量
- 📏 `get_knowledge_result()` L238: 57 代码量
- ❌ L285: 未处理的易出错调用
- ❌ L286: 未处理的易出错调用
- ❌ L287: 未处理的易出错调用
- ❌ L289: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 9.0, 最大: 11
- 认知复杂度: 平均: 13.0, 最大: 15
- 嵌套深度: 平均: 2.0, 最大: 2
- 函数长度: 平均: 75.7 行, 最大: 98 行
- 文件长度: 253 代码量 (295 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 4/12 个错误被忽略 (33.3%)
- 注释比例: 3.6% (9/253)
- 命名规范: 无命名违规

### 8. frontend\scripts\browser-audit\defense-scenario.mjs

**糟糕指数: 15.28**

> 行数: 231 总计, 206 代码, 0 注释 | 函数: 12 | 类: 0

**问题**: ⚠️ 其他问题: 5, 📋 重复问题: 2, ❌ 错误处理问题: 5, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `prepareDefenseAccount` | L75-101 | 27 | 3 | 1 | 6 | ✗ |
| `openTeacherImportCourseFlow` | L15-37 | 23 | 2 | 1 | 4 | ✗ |
| `captureQuestionWorkspace` | L39-51 | 13 | 2 | 1 | 5 | ✗ |
| `prepareDefenseDemoScenario` | L53-73 | 21 | 2 | 1 | 3 | ✗ |
| `captureStudentDefenseSteps` | L182-198 | 16 | 2 | 1 | 5 | ✗ |
| `captureStageTestIfAvailable` | L207-216 | 9 | 2 | 1 | 6 | ✗ |
| `captureStudentFinalRoutes` | L218-230 | 13 | 2 | 1 | 4 | ✗ |
| `simulateDefenseDemoScenario` | L103-116 | 14 | 1 | 0 | 3 | ✗ |
| `simulateTeacherDefenseFlow` | L118-136 | 19 | 1 | 0 | 4 | ✗ |
| `simulateWarmupDefenseFlow` | L138-158 | 21 | 1 | 0 | 4 | ✗ |
| `simulateStudentDefenseFlow` | L160-180 | 21 | 1 | 0 | 4 | ✗ |
| `captureStudentBasics` | L200-205 | 6 | 1 | 0 | 5 | ✗ |

**全部问题 (12)**

- 📏 `captureQuestionWorkspace()` L39: 5 参数数量
- 📏 `prepareDefenseAccount()` L75: 6 参数数量
- 📏 `captureStudentDefenseSteps()` L182: 5 参数数量
- 📏 `captureStudentBasics()` L200: 5 参数数量
- 📏 `captureStageTestIfAvailable()` L207: 6 参数数量
- 📋 `prepareDefenseAccount()` L75: 重复模式: prepareDefenseAccount, captureStudentDefenseSteps
- 📋 `simulateTeacherDefenseFlow()` L118: 重复模式: simulateTeacherDefenseFlow, simulateWarmupDefenseFlow
- ❌ L35: 未处理的易出错调用
- ❌ L98: 未处理的易出错调用
- ❌ L133: 未处理的易出错调用
- ❌ L155: 未处理的易出错调用
- ❌ L177: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.7, 最大: 3
- 认知复杂度: 平均: 2.8, 最大: 5
- 嵌套深度: 平均: 0.6, 最大: 1
- 函数长度: 平均: 16.9 行, 最大: 27 行
- 文件长度: 206 代码量 (231 总计)
- 参数数量: 平均: 4.4, 最大: 6
- 代码重复: 16.7% 重复 (2/12)
- 结构分析: 0 个结构问题
- 错误处理: 5/5 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/206)
- 命名规范: 无命名违规

### 9. backend\logs\middleware.py

**糟糕指数: 15.25**

> 行数: 525 总计, 392 代码, 59 注释 | 函数: 13 | 类: 1

**问题**: 🔄 复杂度问题: 6, ⚠️ 其他问题: 3, 🏗️ 结构问题: 5, ❌ 错误处理问题: 4, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_log_debug_info` | L395-461 | 67 | 13 | 2 | 3 | ✓ |
| `get_request_params` | L260-302 | 43 | 9 | 4 | 2 | ✓ |
| `_mask_sensitive_data` | L373-390 | 18 | 8 | 3 | 3 | ✓ |
| `get_response_content` | L307-332 | 26 | 7 | 3 | 2 | ✓ |
| `process_response` | L466-524 | 59 | 7 | 2 | 3 | ✓ |
| `process_request` | L149-169 | 21 | 6 | 3 | 2 | ✓ |
| `get_action_type` | L193-213 | 21 | 6 | 1 | 2 | ✓ |
| `should_debug_log` | L126-144 | 19 | 5 | 2 | 2 | ✓ |
| `get_module` | L174-188 | 15 | 5 | 2 | 2 | ✓ |
| `get_request_headers` | L234-255 | 22 | 5 | 3 | 2 | ✓ |
| `get_db_queries` | L337-368 | 32 | 5 | 1 | 2 | ✓ |
| `should_log` | L106-121 | 16 | 4 | 2 | 2 | ✓ |
| `get_client_ip` | L218-229 | 12 | 2 | 1 | 2 | ✓ |

**全部问题 (19)**

- 🔄 `_log_debug_info()` L395: 复杂度: 13
- 🔄 `get_request_params()` L260: 认知复杂度: 17
- 🔄 `get_response_content()` L307: 认知复杂度: 13
- 🔄 `_mask_sensitive_data()` L373: 认知复杂度: 14
- 🔄 `_log_debug_info()` L395: 认知复杂度: 17
- 🔄 `get_request_params()` L260: 嵌套深度: 4
- 📏 `_log_debug_info()` L395: 67 代码量
- 📏 `process_response()` L466: 59 代码量
- 🏗️ `process_request()` L149: 中等嵌套: 3
- 🏗️ `get_request_headers()` L234: 中等嵌套: 3
- 🏗️ `get_request_params()` L260: 中等嵌套: 4
- 🏗️ `get_response_content()` L307: 中等嵌套: 3
- 🏗️ `_mask_sensitive_data()` L373: 中等嵌套: 3
- ❌ L324: 未处理的易出错调用
- ❌ L355: 未处理的易出错调用
- ❌ L356: 未处理的易出错调用
- ❌ L491: 未处理的易出错调用
- 🏷️ `_mask_sensitive_data()` L373: "_mask_sensitive_data" - snake_case
- 🏷️ `_log_debug_info()` L395: "_log_debug_info" - snake_case

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 13
- 认知复杂度: 平均: 10.8, 最大: 17
- 嵌套深度: 平均: 2.2, 最大: 4
- 函数长度: 平均: 28.5 行, 最大: 67 行
- 文件长度: 392 代码量 (525 总计)
- 参数数量: 平均: 2.2, 最大: 3
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 5 个结构问题
- 错误处理: 4/13 个错误被忽略 (30.8%)
- 注释比例: 15.1% (59/392)
- 命名规范: 发现 2 个违规

### 10. backend\assessments\habit_views.py

**糟糕指数: 15.19**

> 行数: 307 总计, 222 代码, 42 注释 | 函数: 14 | 类: 0

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 7, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_resolve_habit_field` | L198-219 | 22 | 17 | 1 | 1 | ✓ |
| `_normalize_habit_answer` | L225-234 | 10 | 7 | 1 | 2 | ✓ |
| `_map_habit_responses` | L153-175 | 23 | 5 | 2 | 1 | ✓ |
| `submit_habit_survey` | L61-85 | 25 | 4 | 2 | 1 | ✓ |
| `_seed_default_habit_questions` | L105-118 | 14 | 3 | 2 | 0 | ✓ |
| `_normalize_response_items` | L181-192 | 12 | 3 | 1 | 1 | ✓ |
| `get_habit_survey` | L35-53 | 19 | 2 | 1 | 1 | ✓ |
| `_get_or_create_habit_questions` | L91-99 | 9 | 2 | 1 | 1 | ✓ |
| `_mark_habit_assessment_done` | L275-284 | 10 | 2 | 1 | 2 | ✓ |
| `_habit_question_queryset` | L124-129 | 6 | 1 | 0 | 1 | ✓ |
| `_serialize_habit_questions` | L135-147 | 13 | 1 | 0 | 1 | ✓ |
| `_save_habit_preference` | L240-261 | 22 | 1 | 0 | 3 | ✓ |
| `_study_duration_bucket` | L267-269 | 3 | 1 | 0 | 1 | ✓ |
| `_create_missing_course_assessment_statuses` | L290-306 | 17 | 1 | 0 | 1 | ✓ |

**全部问题 (19)**

- 🔄 `_resolve_habit_field()` L198: 复杂度: 17
- 🔄 `_resolve_habit_field()` L198: 认知复杂度: 19
- ❌ L250: 未处理的易出错调用
- ❌ L251: 未处理的易出错调用
- ❌ L252: 未处理的易出错调用
- ❌ L254: 未处理的易出错调用
- ❌ L255: 未处理的易出错调用
- ❌ L256: 未处理的易出错调用
- ❌ L258: 未处理的易出错调用
- 🏷️ `_get_or_create_habit_questions()` L91: "_get_or_create_habit_questions" - snake_case
- 🏷️ `_seed_default_habit_questions()` L105: "_seed_default_habit_questions" - snake_case
- 🏷️ `_habit_question_queryset()` L124: "_habit_question_queryset" - snake_case
- 🏷️ `_serialize_habit_questions()` L135: "_serialize_habit_questions" - snake_case
- 🏷️ `_map_habit_responses()` L153: "_map_habit_responses" - snake_case
- 🏷️ `_normalize_response_items()` L181: "_normalize_response_items" - snake_case
- 🏷️ `_resolve_habit_field()` L198: "_resolve_habit_field" - snake_case
- 🏷️ `_normalize_habit_answer()` L225: "_normalize_habit_answer" - snake_case
- 🏷️ `_save_habit_preference()` L240: "_save_habit_preference" - snake_case
- 🏷️ `_study_duration_bucket()` L267: "_study_duration_bucket" - snake_case

**详情**:
- 循环复杂度: 平均: 3.6, 最大: 17
- 认知复杂度: 平均: 5.3, 最大: 19
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 14.6 行, 最大: 25 行
- 文件长度: 222 代码量 (307 总计)
- 参数数量: 平均: 1.2, 最大: 3
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 7/14 个错误被忽略 (50.0%)
- 注释比例: 18.9% (42/222)
- 命名规范: 发现 12 个违规

### 11. backend\tools\knowledge_import_support.py

**糟糕指数: 15.01**

> 行数: 492 总计, 372 代码, 60 注释 | 函数: 20 | 类: 0

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 2, 📋 重复问题: 2, 🏗️ 结构问题: 2, ❌ 错误处理问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `validate_import_json_payload` | L14-35 | 22 | 14 | 2 | 2 | ✓ |
| `append_relation_edges` | L230-254 | 25 | 8 | 3 | 5 | ✓ |
| `upsert_course_knowledge_edges` | L445-470 | 26 | 8 | 2 | 4 | ✓ |
| `build_hierarchical_node` | L137-158 | 22 | 7 | 0 | 6 | ✓ |
| `patch_existing_point_from_node` | L426-439 | 14 | 7 | 2 | 2 | ✓ |
| `upsert_course_knowledge_nodes` | L383-420 | 38 | 6 | 2 | 2 | ✓ |
| `parse_knowledge_excel` | L54-75 | 22 | 5 | 1 | 1 | ✓ |
| `collect_flat_nodes` | L304-323 | 20 | 5 | 2 | 2 | ✓ |
| `collect_flat_prerequisite_edges` | L329-348 | 20 | 5 | 3 | 3 | ✓ |
| `read_knowledge_import_source` | L41-48 | 8 | 4 | 1 | 1 | ✓ |
| `resolve_hierarchical_point` | L121-131 | 11 | 4 | 2 | 3 | ✓ |
| `append_parent_edge` | L164-177 | 14 | 4 | 1 | 5 | ✓ |
| `resolve_hierarchical_header_row` | L81-87 | 7 | 3 | 2 | 1 | ✓ |
| `parse_hierarchical_knowledge_excel` | L183-224 | 42 | 3 | 2 | 2 | ✓ |
| `build_course_point_maps` | L354-364 | 11 | 3 | 1 | 1 | ✓ |
| `sync_knowledge_graph_copy` | L476-491 | 16 | 3 | 2 | 1 | ✓ |
| `resolve_hierarchical_columns` | L93-115 | 23 | 1 | 0 | 1 | ✓ |
| `parse_flat_knowledge_excel` | L260-269 | 10 | 1 | 0 | 1 | ✓ |
| `resolve_flat_columns` | L275-298 | 24 | 1 | 0 | 1 | ✓ |
| `write_tmp_knowledge_json` | L370-377 | 8 | 1 | 0 | 1 | ✓ |

**全部问题 (16)**

- 🔄 `validate_import_json_payload()` L14: 复杂度: 14
- 🔄 `validate_import_json_payload()` L14: 认知复杂度: 18
- 🔄 `append_relation_edges()` L230: 认知复杂度: 14
- 📏 `build_hierarchical_node()` L137: 6 参数数量
- 📋 `resolve_hierarchical_columns()` L93: 重复模式: resolve_hierarchical_columns, parse_flat_knowledge_excel
- 📋 `resolve_flat_columns()` L275: 重复模式: resolve_flat_columns, build_course_point_maps
- 🏗️ `append_relation_edges()` L230: 中等嵌套: 3
- 🏗️ `collect_flat_prerequisite_edges()` L329: 中等嵌套: 3
- ❌ L152: 未处理的易出错调用
- ❌ L154: 未处理的易出错调用
- ❌ L155: 未处理的易出错调用
- ❌ L156: 未处理的易出错调用
- ❌ L157: 未处理的易出错调用
- ❌ L318: 未处理的易出错调用
- ❌ L319: 未处理的易出错调用
- ❌ L418: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 14
- 认知复杂度: 平均: 7.5, 最大: 18
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 19.1 行, 最大: 42 行
- 文件长度: 372 代码量 (492 总计)
- 参数数量: 平均: 2.3, 最大: 6
- 代码重复: 10.0% 重复 (2/20)
- 结构分析: 2 个结构问题
- 错误处理: 8/36 个错误被忽略 (22.2%)
- 注释比例: 16.1% (60/372)
- 命名规范: 无命名违规

### 12. backend\platform_ai\mcp\resources.py

**糟糕指数: 14.94**

> 行数: 493 总计, 359 代码, 60 注释 | 函数: 18 | 类: 3

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 5, 📋 重复问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `search_internal_resources` | L198-268 | 71 | 14 | 3 | 5 | ✓ |
| `_search_with_exa` | L348-426 | 79 | 13 | 2 | 6 | ✓ |
| `_enrich_with_firecrawl` | L444-489 | 46 | 10 | 1 | 2 | ✓ |
| `search_external_resources` | L273-303 | 31 | 7 | 2 | 6 | ✓ |
| `_guess_resource_type` | L98-109 | 12 | 6 | 1 | 2 | ✓ |
| `_mastery_stage` | L62-73 | 12 | 5 | 1 | 1 | ✓ |
| `_resource_id` | L50-56 | 7 | 3 | 1 | 1 | ✓ |
| `_external_search_enabled` | L308-315 | 8 | 3 | 0 | 1 | ✓ |
| `_firecrawl_enabled` | L320-327 | 8 | 3 | 0 | 1 | ✓ |
| `_extract_exa_snippet` | L431-439 | 9 | 3 | 2 | 2 | ✓ |
| `_coerce_text` | L41-44 | 4 | 2 | 0 | 1 | ✓ |
| `_is_valid_http_url` | L79-83 | 5 | 2 | 0 | 1 | ✓ |
| `_truncate_text` | L115-121 | 7 | 2 | 1 | 2 | ✓ |
| `__init__` | L190-193 | 4 | 2 | 0 | 2 | ✓ |
| `_build_search_query` | L332-343 | 12 | 2 | 0 | 4 | ✓ |
| `_domain_from_url` | L89-92 | 4 | 1 | 0 | 1 | ✓ |
| `resource_id` | L139-142 | 4 | 1 | 0 | 1 | ✓ |
| `to_response` | L164-181 | 18 | 1 | 0 | 1 | ✓ |

**全部问题 (21)**

- 🔄 `search_internal_resources()` L198: 复杂度: 14
- 🔄 `_search_with_exa()` L348: 复杂度: 13
- 🔄 `search_internal_resources()` L198: 认知复杂度: 20
- 🔄 `_search_with_exa()` L348: 认知复杂度: 17
- 📏 `search_internal_resources()` L198: 71 代码量
- 📏 `_search_with_exa()` L348: 79 代码量
- 📏 `search_external_resources()` L273: 6 参数数量
- 📏 `_search_with_exa()` L348: 6 参数数量
- 📋 `_truncate_text()` L115: 重复模式: _truncate_text, _extract_exa_snippet
- 🏗️ `search_internal_resources()` L198: 中等嵌套: 3
- ❌ L257: 未处理的易出错调用
- 🏷️ `_coerce_text()` L41: "_coerce_text" - snake_case
- 🏷️ `_resource_id()` L50: "_resource_id" - snake_case
- 🏷️ `_mastery_stage()` L62: "_mastery_stage" - snake_case
- 🏷️ `_is_valid_http_url()` L79: "_is_valid_http_url" - snake_case
- 🏷️ `_domain_from_url()` L89: "_domain_from_url" - snake_case
- 🏷️ `_guess_resource_type()` L98: "_guess_resource_type" - snake_case
- 🏷️ `_truncate_text()` L115: "_truncate_text" - snake_case
- 🏷️ `__init__()` L190: "__init__" - snake_case
- 🏷️ `_external_search_enabled()` L308: "_external_search_enabled" - snake_case
- 🏷️ `_firecrawl_enabled()` L320: "_firecrawl_enabled" - snake_case

**详情**:
- 循环复杂度: 平均: 4.4, 最大: 14
- 认知复杂度: 平均: 6.0, 最大: 20
- 嵌套深度: 平均: 0.8, 最大: 3
- 函数长度: 平均: 18.9 行, 最大: 79 行
- 文件长度: 359 代码量 (493 总计)
- 参数数量: 平均: 2.2, 最大: 6
- 代码重复: 5.6% 重复 (1/18)
- 结构分析: 1 个结构问题
- 错误处理: 1/18 个错误被忽略 (5.6%)
- 注释比例: 16.7% (60/359)
- 命名规范: 发现 14 个违规

### 13. backend\common\defense_demo_assessment_questions.py

**糟糕指数: 14.92**

> 行数: 274 总计, 235 代码, 16 注释 | 函数: 3 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_planned_answer_value` | L162-201 | 40 | 8 | 1 | 2 | ✓ |
| `_build_assessment_report_payload` | L207-273 | 67 | 7 | 2 | 2 | ✓ |
| `_ensure_demo_assessment_questions` | L21-156 | 136 | 3 | 1 | 3 | ✓ |

**全部问题 (8)**

- 📏 `_ensure_demo_assessment_questions()` L21: 136 代码量
- 📏 `_build_assessment_report_payload()` L207: 67 代码量
- ❌ L182: 未处理的易出错调用
- ❌ L184: 未处理的易出错调用
- ❌ L196: 未处理的易出错调用
- 🏷️ `_ensure_demo_assessment_questions()` L21: "_ensure_demo_assessment_questions" - snake_case
- 🏷️ `_build_planned_answer_value()` L162: "_build_planned_answer_value" - snake_case
- 🏷️ `_build_assessment_report_payload()` L207: "_build_assessment_report_payload" - snake_case

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 8
- 认知复杂度: 平均: 8.7, 最大: 11
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 81.0 行, 最大: 136 行
- 文件长度: 235 代码量 (274 总计)
- 参数数量: 平均: 2.3, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 3/4 个错误被忽略 (75.0%)
- 注释比例: 6.8% (16/235)
- 命名规范: 发现 3 个违规

### 14. backend\tools\cli_parser.py

**糟糕指数: 14.72**

> 行数: 375 总计, 301 代码, 26 注释 | 函数: 8 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_dispatch_import_commands` | L230-262 | 33 | 15 | 1 | 1 | ✓ |
| `_dispatch_data_admin_commands` | L268-296 | 29 | 13 | 1 | 1 | ✓ |
| `_dispatch_test_commands` | L302-324 | 23 | 10 | 1 | 1 | ✓ |
| `_dispatch_training_commands` | L330-356 | 27 | 5 | 1 | 1 | ✓ |
| `dispatch_command` | L370-374 | 5 | 3 | 2 | 1 | ✓ |
| `_parse_model_filters` | L220-224 | 5 | 2 | 1 | 1 | ✓ |
| `_add_json_import_args` | L46-51 | 6 | 1 | 0 | 1 | ✓ |
| `build_parser` | L57-214 | 158 | 1 | 0 | 0 | ✓ |

**全部问题 (12)**

- 🔄 `_dispatch_import_commands()` L230: 复杂度: 15
- 🔄 `_dispatch_data_admin_commands()` L268: 复杂度: 13
- 🔄 `_dispatch_import_commands()` L230: 认知复杂度: 17
- 🔄 `_dispatch_data_admin_commands()` L268: 认知复杂度: 15
- 📏 `build_parser()` L57: 158 代码量
- 🏗️ L1: 导入过多: 23
- 🏷️ `_add_json_import_args()` L46: "_add_json_import_args" - snake_case
- 🏷️ `_parse_model_filters()` L220: "_parse_model_filters" - snake_case
- 🏷️ `_dispatch_import_commands()` L230: "_dispatch_import_commands" - snake_case
- 🏷️ `_dispatch_data_admin_commands()` L268: "_dispatch_data_admin_commands" - snake_case
- 🏷️ `_dispatch_test_commands()` L302: "_dispatch_test_commands" - snake_case
- 🏷️ `_dispatch_training_commands()` L330: "_dispatch_training_commands" - snake_case

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 15
- 认知复杂度: 平均: 8.0, 最大: 17
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 35.8 行, 最大: 158 行
- 文件长度: 301 代码量 (375 总计)
- 参数数量: 平均: 0.9, 最大: 1
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 8.6% (26/301)
- 命名规范: 发现 6 个违规

### 15. backend\assessments\knowledge_assessment_logic.py

**糟糕指数: 14.58**

> 行数: 362 总计, 291 代码, 30 注释 | 函数: 9 | 类: 1

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 2, 📋 重复问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_feedback_report_payload` | L306-323 | 18 | 11 | 1 | 1 | ✓ |
| `is_answer_correct` | L77-100 | 24 | 9 | 1 | 3 | ✓ |
| `evaluate_knowledge_answers` | L188-256 | 69 | 7 | 3 | 4 | ✓ |
| `blend_mastery_with_kt` | L262-300 | 39 | 6 | 2 | 5 | ✓ |
| `normalize_bool_answer` | L50-61 | 12 | 5 | 1 | 1 | ✓ |
| `build_answer_history_models` | L143-182 | 40 | 4 | 1 | 7 | ✓ |
| `resolve_correct_answer_payload` | L67-71 | 5 | 2 | 1 | 1 | ✓ |
| `build_question_detail_payload` | L106-137 | 32 | 1 | 0 | 5 | ✓ |
| `build_empty_knowledge_result` | L329-347 | 19 | 1 | 0 | 3 | ✓ |

**全部问题 (9)**

- 🔄 `build_feedback_report_payload()` L306: 复杂度: 11
- 🔄 `evaluate_knowledge_answers()` L188: 认知复杂度: 13
- 🔄 `build_feedback_report_payload()` L306: 认知复杂度: 13
- 📏 `evaluate_knowledge_answers()` L188: 69 代码量
- 📏 `build_answer_history_models()` L143: 7 参数数量
- 📋 `build_question_detail_payload()` L106: 重复模式: build_question_detail_payload, build_empty_knowledge_result
- 🏗️ `evaluate_knowledge_answers()` L188: 中等嵌套: 3
- ❌ L315: 未处理的易出错调用
- ❌ L317: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.1, 最大: 11
- 认知复杂度: 平均: 7.3, 最大: 13
- 嵌套深度: 平均: 1.1, 最大: 3
- 函数长度: 平均: 28.7 行, 最大: 69 行
- 文件长度: 291 代码量 (362 总计)
- 参数数量: 平均: 3.3, 最大: 7
- 代码重复: 11.1% 重复 (1/9)
- 结构分析: 1 个结构问题
- 错误处理: 2/7 个错误被忽略 (28.6%)
- 注释比例: 10.3% (30/291)
- 命名规范: 无命名违规

### 16. backend\ai_services\student_ai_chat_views.py

**糟糕指数: 14.57**

> 行数: 155 总计, 121 代码, 15 注释 | 函数: 5 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 📋 重复问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_chat_response` | L22-70 | 49 | 11 | 2 | 6 | ✓ |
| `ai_chat` | L78-98 | 21 | 7 | 1 | 1 | ✓ |
| `ai_graph_rag_search` | L116-131 | 16 | 6 | 1 | 1 | ✓ |
| `ai_graph_rag_ask` | L139-154 | 16 | 6 | 1 | 1 | ✓ |
| `ai_knowledge_graph_query` | L106-108 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `build_chat_response()` L22: 复杂度: 11
- 🔄 `build_chat_response()` L22: 认知复杂度: 15
- 📏 `build_chat_response()` L22: 6 参数数量
- 📋 `ai_graph_rag_search()` L116: 重复模式: ai_graph_rag_search, ai_graph_rag_ask

**详情**:
- 循环复杂度: 平均: 6.2, 最大: 11
- 认知复杂度: 平均: 8.2, 最大: 15
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 21.0 行, 最大: 49 行
- 文件长度: 121 代码量 (155 总计)
- 参数数量: 平均: 2.0, 最大: 6
- 代码重复: 20.0% 重复 (1/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/12 个错误被忽略 (0.0%)
- 注释比例: 12.4% (15/121)
- 命名规范: 无命名违规

### 17. backend\common\defense_demo_assessment_support.py

**糟糕指数: 14.54**

> 行数: 361 总计, 304 代码, 27 注释 | 函数: 8 | 类: 1

**问题**: ⚠️ 其他问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_load_demo_assessment_defaults` | L42-122 | 81 | 7 | 1 | 1 | ✓ |
| `_build_demo_mastery_map` | L229-247 | 19 | 6 | 3 | 2 | ✓ |
| `_upsert_demo_assessment_feedback` | L319-360 | 42 | 4 | 0 | 7 | ✓ |
| `_ensure_demo_knowledge_assessment` | L164-192 | 29 | 3 | 1 | 2 | ✓ |
| `_refresh_demo_answer_histories` | L198-223 | 26 | 3 | 1 | 5 | ✓ |
| `_persist_demo_mastery_records` | L253-266 | 14 | 2 | 1 | 4 | ✓ |
| `_upsert_demo_assessment_result` | L272-313 | 42 | 2 | 0 | 9 | ✓ |
| `_seed_demo_profile_state` | L128-158 | 31 | 1 | 0 | 3 | ✓ |

**全部问题 (14)**

- 📏 `_load_demo_assessment_defaults()` L42: 81 代码量
- 📏 `_upsert_demo_assessment_result()` L272: 9 参数数量
- 📏 `_upsert_demo_assessment_feedback()` L319: 7 参数数量
- 🏗️ `_build_demo_mastery_map()` L229: 中等嵌套: 3
- ❌ L185: 未处理的易出错调用
- ❌ L303: 未处理的易出错调用
- 🏷️ `_load_demo_assessment_defaults()` L42: "_load_demo_assessment_defaults" - snake_case
- 🏷️ `_seed_demo_profile_state()` L128: "_seed_demo_profile_state" - snake_case
- 🏷️ `_ensure_demo_knowledge_assessment()` L164: "_ensure_demo_knowledge_assessment" - snake_case
- 🏷️ `_refresh_demo_answer_histories()` L198: "_refresh_demo_answer_histories" - snake_case
- 🏷️ `_build_demo_mastery_map()` L229: "_build_demo_mastery_map" - snake_case
- 🏷️ `_persist_demo_mastery_records()` L253: "_persist_demo_mastery_records" - snake_case
- 🏷️ `_upsert_demo_assessment_result()` L272: "_upsert_demo_assessment_result" - snake_case
- 🏷️ `_upsert_demo_assessment_feedback()` L319: "_upsert_demo_assessment_feedback" - snake_case

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 7
- 认知复杂度: 平均: 5.3, 最大: 12
- 嵌套深度: 平均: 0.9, 最大: 3
- 函数长度: 平均: 35.5 行, 最大: 81 行
- 文件长度: 304 代码量 (361 总计)
- 参数数量: 平均: 4.1, 最大: 9
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 2/10 个错误被忽略 (20.0%)
- 注释比例: 8.9% (27/304)
- 命名规范: 发现 8 个违规

### 18. backend\platform_ai\rag\runtime_search_mixin.py

**糟糕指数: 14.48**

> 行数: 247 总计, 206 代码, 21 注释 | 函数: 6 | 类: 1

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `search_points` | L201-246 | 46 | 11 | 4 | 4 | ✓ |
| `_search_qdrant_only` | L104-136 | 33 | 10 | 1 | 4 | ✓ |
| `_format_retriever_record` | L54-71 | 18 | 9 | 0 | 2 | ✓ |
| `_parse_items` | L76-99 | 24 | 9 | 2 | 2 | ✓ |
| `search_documents` | L141-196 | 56 | 9 | 1 | 5 | ✓ |
| `_retrieval_query` | L31-49 | 19 | 1 | 0 | 1 | ✓ |

**全部问题 (13)**

- 🔄 `search_points()` L201: 复杂度: 11
- 🔄 `_parse_items()` L76: 认知复杂度: 13
- 🔄 `search_points()` L201: 认知复杂度: 19
- 🔄 `search_points()` L201: 嵌套深度: 4
- 📏 `search_documents()` L141: 56 代码量
- 🏗️ `search_points()` L201: 中等嵌套: 4
- ❌ L241: 未处理的易出错调用
- ❌ L242: 未处理的易出错调用
- ❌ L243: 未处理的易出错调用
- 🏷️ `_retrieval_query()` L31: "_retrieval_query" - snake_case
- 🏷️ `_format_retriever_record()` L54: "_format_retriever_record" - snake_case
- 🏷️ `_parse_items()` L76: "_parse_items" - snake_case
- 🏷️ `_search_qdrant_only()` L104: "_search_qdrant_only" - snake_case

**详情**:
- 循环复杂度: 平均: 8.2, 最大: 11
- 认知复杂度: 平均: 10.8, 最大: 19
- 嵌套深度: 平均: 1.3, 最大: 4
- 函数长度: 平均: 32.7 行, 最大: 56 行
- 文件长度: 206 代码量 (247 总计)
- 参数数量: 平均: 3.0, 最大: 5
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 1 个结构问题
- 错误处理: 3/24 个错误被忽略 (12.5%)
- 注释比例: 10.2% (21/206)
- 命名规范: 发现 4 个违规

### 19. backend\tools\demo_course_archive.py

**糟糕指数: 14.33**

> 行数: 107 总计, 73 代码, 12 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_demo_course_archive` | L57-106 | 50 | 12 | 4 | 2 | ✓ |
| `_resolve_output_path` | L39-51 | 13 | 3 | 1 | 1 | ✓ |
| `_copy_file_to_dir` | L24-33 | 10 | 2 | 0 | 3 | ✓ |

**全部问题 (7)**

- 🔄 `generate_demo_course_archive()` L57: 复杂度: 12
- 🔄 `generate_demo_course_archive()` L57: 认知复杂度: 20
- 🔄 `generate_demo_course_archive()` L57: 嵌套深度: 4
- 🏗️ `generate_demo_course_archive()` L57: 中等嵌套: 4
- ❌ L101: 未处理的易出错调用
- 🏷️ `_copy_file_to_dir()` L24: "_copy_file_to_dir" - snake_case
- 🏷️ `_resolve_output_path()` L39: "_resolve_output_path" - snake_case

**详情**:
- 循环复杂度: 平均: 5.7, 最大: 12
- 认知复杂度: 平均: 9.0, 最大: 20
- 嵌套深度: 平均: 1.7, 最大: 4
- 函数长度: 平均: 24.3 行, 最大: 50 行
- 文件长度: 73 代码量 (107 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 1 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 16.4% (12/73)
- 命名规范: 发现 2 个违规

### 20. backend\models\MEFKT\attribute.py

**糟糕指数: 14.16**

> 行数: 210 总计, 176 代码, 12 注释 | 函数: 3 | 类: 2

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `forward` | L115-206 | 92 | 9 | 2 | 9 | ✓ |
| `_build_default_relation_stats` | L82-110 | 29 | 3 | 1 | 4 | ✓ |
| `__init__` | L32-77 | 46 | 2 | 0 | 5 | ✓ |

**全部问题 (5)**

- 🔄 `forward()` L115: 认知复杂度: 13
- 📏 `forward()` L115: 92 代码量
- 📏 `forward()` L115: 9 参数数量
- 🏷️ `__init__()` L32: "__init__" - snake_case
- 🏷️ `_build_default_relation_stats()` L82: "_build_default_relation_stats" - snake_case

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 9
- 认知复杂度: 平均: 6.7, 最大: 13
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 55.7 行, 最大: 92 行
- 文件长度: 176 代码量 (210 总计)
- 参数数量: 平均: 6.0, 最大: 9
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 6.8% (12/176)
- 命名规范: 发现 2 个违规

### 21. backend\ai_services\services\web_search_service.py

**糟糕指数: 14.01**

> 行数: 306 总计, 232 代码, 27 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_search_with_provider` | L165-213 | 49 | 12 | 2 | 4 | ✓ |
| `search_learning_resources` | L219-305 | 87 | 10 | 3 | 3 | ✓ |
| `_resolve_result_url` | L128-159 | 32 | 9 | 2 | 2 | ✓ |
| `_guess_resource_type` | L76-85 | 10 | 4 | 1 | 2 | ✓ |
| `_normalize_candidate_url` | L65-70 | 6 | 3 | 1 | 1 | ✓ |
| `_clean_html_text` | L54-59 | 6 | 2 | 1 | 1 | ✓ |
| `_is_accessible_url` | L91-105 | 15 | 2 | 1 | 2 | ✓ |
| `_matches_expected_domain` | L119-122 | 4 | 2 | 0 | 2 | ✓ |
| `_is_search_engine_url` | L111-113 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (17)**

- 🔄 `_search_with_provider()` L165: 复杂度: 12
- 🔄 `_resolve_result_url()` L128: 认知复杂度: 13
- 🔄 `_search_with_provider()` L165: 认知复杂度: 16
- 🔄 `search_learning_resources()` L219: 认知复杂度: 16
- 📏 `search_learning_resources()` L219: 87 代码量
- 🏗️ `search_learning_resources()` L219: 中等嵌套: 3
- ❌ L101: 未处理的易出错调用
- ❌ L149: 未处理的易出错调用
- ❌ L275: 未处理的易出错调用
- 🏷️ `_clean_html_text()` L54: "_clean_html_text" - snake_case
- 🏷️ `_normalize_candidate_url()` L65: "_normalize_candidate_url" - snake_case
- 🏷️ `_guess_resource_type()` L76: "_guess_resource_type" - snake_case
- 🏷️ `_is_accessible_url()` L91: "_is_accessible_url" - snake_case
- 🏷️ `_is_search_engine_url()` L111: "_is_search_engine_url" - snake_case
- 🏷️ `_matches_expected_domain()` L119: "_matches_expected_domain" - snake_case
- 🏷️ `_resolve_result_url()` L128: "_resolve_result_url" - snake_case
- 🏷️ `_search_with_provider()` L165: "_search_with_provider" - snake_case

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 12
- 认知复杂度: 平均: 7.4, 最大: 16
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 23.6 行, 最大: 87 行
- 文件长度: 232 代码量 (306 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 3/6 个错误被忽略 (50.0%)
- 注释比例: 11.6% (27/232)
- 命名规范: 发现 8 个违规

### 22. backend\tools\mefkt_public_data.py

**糟糕指数: 13.69**

> 行数: 378 总计, 282 代码, 48 注释 | 函数: 14 | 类: 1

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 1, 🏗️ 结构问题: 3, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `load_csv_sequences` | L89-129 | 41 | 15 | 2 | 1 | ✓ |
| `build_public_bundle` | L260-302 | 43 | 8 | 2 | 2 | ✓ |
| `chunk_public_sequences` | L145-157 | 13 | 7 | 3 | 2 | ✓ |
| `evaluate_sequence_model` | L339-360 | 22 | 7 | 3 | 4 | ✓ |
| `estimate_public_time_proxy` | L197-210 | 14 | 6 | 3 | 2 | ✓ |
| `load_three_line_sequences` | L71-83 | 13 | 4 | 2 | 1 | ✓ |
| `build_transition_matrices` | L163-177 | 15 | 4 | 2 | 2 | ✓ |
| `estimate_public_difficulty` | L183-191 | 9 | 4 | 2 | 3 | ✓ |
| `normalize_tensor` | L57-65 | 9 | 3 | 1 | 2 | ✓ |
| `relative_to_project` | L45-51 | 7 | 2 | 1 | 1 | ✓ |
| `load_public_sequences` | L135-139 | 5 | 2 | 1 | 1 | ✓ |
| `build_public_features` | L216-254 | 39 | 2 | 1 | 6 | ✓ |
| `collate_batch` | L308-320 | 13 | 2 | 1 | 1 | ✓ |
| `split_sequences` | L326-333 | 8 | 2 | 1 | 3 | ✓ |

**全部问题 (9)**

- 🔄 `load_csv_sequences()` L89: 复杂度: 15
- 🔄 `load_csv_sequences()` L89: 认知复杂度: 19
- 🔄 `chunk_public_sequences()` L145: 认知复杂度: 13
- 🔄 `evaluate_sequence_model()` L339: 认知复杂度: 13
- 📏 `build_public_features()` L216: 6 参数数量
- 🏗️ `chunk_public_sequences()` L145: 中等嵌套: 3
- 🏗️ `estimate_public_time_proxy()` L197: 中等嵌套: 3
- 🏗️ `evaluate_sequence_model()` L339: 中等嵌套: 3
- ❌ L119: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.9, 最大: 15
- 认知复杂度: 平均: 8.4, 最大: 19
- 嵌套深度: 平均: 1.8, 最大: 3
- 函数长度: 平均: 17.9 行, 最大: 43 行
- 文件长度: 282 代码量 (378 总计)
- 参数数量: 平均: 2.2, 最大: 6
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 3 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 17.0% (48/282)
- 命名规范: 无命名违规

### 23. backend\tools\mefkt_training.py

**糟糕指数: 13.62**

> 行数: 202 总计, 155 代码, 23 注释 | 函数: 7 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 7, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `train_mefkt_v2` | L66-108 | 43 | 5 | 1 | 17 | ✓ |
| `build_training_bundle` | L114-137 | 24 | 3 | 1 | 3 | ✓ |
| `resolve_mefkt_output_path` | L143-149 | 7 | 3 | 1 | 2 | ✓ |
| `mefkt_status` | L168-189 | 22 | 2 | 1 | 0 | ✓ |
| `_train_mefkt_bundle` | L27-60 | 34 | 1 | 0 | 13 | ✓ |
| `print_training_result` | L155-162 | 8 | 1 | 0 | 1 | ✓ |
| `print_mefkt_status` | L195-198 | 4 | 1 | 0 | 1 | ✓ |

**全部问题 (10)**

- 📏 `_train_mefkt_bundle()` L27: 13 参数数量
- 📏 `train_mefkt_v2()` L66: 17 参数数量
- ❌ L182: 未处理的易出错调用
- ❌ L183: 未处理的易出错调用
- ❌ L184: 未处理的易出错调用
- ❌ L185: 未处理的易出错调用
- ❌ L186: 未处理的易出错调用
- ❌ L187: 未处理的易出错调用
- ❌ L188: 未处理的易出错调用
- 🏷️ `_train_mefkt_bundle()` L27: "_train_mefkt_bundle" - snake_case

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 5
- 认知复杂度: 平均: 3.4, 最大: 7
- 嵌套深度: 平均: 0.6, 最大: 1
- 函数长度: 平均: 20.3 行, 最大: 43 行
- 文件长度: 155 代码量 (202 总计)
- 参数数量: 平均: 5.3, 最大: 17
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 7/7 个错误被忽略 (100.0%)
- 注释比例: 14.8% (23/155)
- 命名规范: 发现 1 个违规

### 24. backend\platform_ai\rag\runtime_graph_query_support.py

**糟糕指数: 13.58**

> 行数: 230 总计, 188 代码, 18 注释 | 函数: 6 | 类: 0

**问题**: 🔄 复杂度问题: 8, ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_tools_query_context` | L171-229 | 59 | 16 | 2 | 1 | ✓ |
| `build_tool_line` | L67-88 | 22 | 14 | 2 | 1 | ✓ |
| `build_tool_source` | L94-129 | 36 | 14 | 1 | 1 | ✓ |
| `build_graph_record_item` | L23-61 | 39 | 12 | 1 | 1 | ✓ |
| `build_semantic_only_query_context` | L151-165 | 15 | 4 | 0 | 2 | ✓ |
| `build_empty_query_context` | L135-145 | 11 | 1 | 0 | 0 | ✓ |

**全部问题 (9)**

- 🔄 `build_graph_record_item()` L23: 复杂度: 12
- 🔄 `build_tool_line()` L67: 复杂度: 14
- 🔄 `build_tool_source()` L94: 复杂度: 14
- 🔄 `build_tools_query_context()` L171: 复杂度: 16
- 🔄 `build_graph_record_item()` L23: 认知复杂度: 14
- 🔄 `build_tool_line()` L67: 认知复杂度: 18
- 🔄 `build_tool_source()` L94: 认知复杂度: 16
- 🔄 `build_tools_query_context()` L171: 认知复杂度: 20
- 📏 `build_tools_query_context()` L171: 59 代码量

**详情**:
- 循环复杂度: 平均: 10.2, 最大: 16
- 认知复杂度: 平均: 12.2, 最大: 20
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 30.3 行, 最大: 59 行
- 文件长度: 188 代码量 (230 总计)
- 参数数量: 平均: 1.0, 最大: 2
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/30 个错误被忽略 (0.0%)
- 注释比例: 9.6% (18/188)
- 命名规范: 无命名违规

### 25. backend\wisdom_edu_api\settings_ai.py

**糟糕指数: 13.45**

> 行数: 221 总计, 193 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_load_llm_settings` | L142-220 | 79 | 15 | 1 | 5 | ✓ |
| `_load_graph_and_resource_settings` | L69-136 | 68 | 4 | 0 | 3 | ✓ |
| `_int_setting` | L19-31 | 13 | 2 | 1 | 5 | ✓ |
| `load_ai_settings` | L37-63 | 27 | 1 | 0 | 5 | ✓ |

**全部问题 (7)**

- 🔄 `_load_llm_settings()` L142: 复杂度: 15
- 🔄 `_load_llm_settings()` L142: 认知复杂度: 17
- 📏 `_load_graph_and_resource_settings()` L69: 68 代码量
- 📏 `_load_llm_settings()` L142: 79 代码量
- 🏷️ `_int_setting()` L19: "_int_setting" - snake_case
- 🏷️ `_load_graph_and_resource_settings()` L69: "_load_graph_and_resource_settings" - snake_case
- 🏷️ `_load_llm_settings()` L142: "_load_llm_settings" - snake_case

**详情**:
- 循环复杂度: 平均: 5.5, 最大: 15
- 认知复杂度: 平均: 6.5, 最大: 17
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 46.8 行, 最大: 79 行
- 文件长度: 193 代码量 (221 总计)
- 参数数量: 平均: 4.5, 最大: 5
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 6.2% (12/193)
- 命名规范: 发现 3 个违规

### 26. backend\tools\bootstrap_support.py

**糟糕指数: 13.22**

> 行数: 382 总计, 288 代码, 44 注释 | 函数: 14 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_bundle_question_assets` | L179-227 | 49 | 12 | 3 | 4 | ✓ |
| `import_media_resources` | L96-142 | 47 | 7 | 2 | 7 | ✓ |
| `collect_batch_candidates` | L346-381 | 30 | 7 | 2 | 2 | ✓ |
| `finalize_bootstrap_course` | L289-305 | 17 | 6 | 2 | 3 | ✓ |
| `resolve_batch_resource_root` | L321-340 | 20 | 6 | 1 | 0 | ✓ |
| `import_bundle_knowledge_assets` | L148-173 | 26 | 5 | 2 | 4 | ✓ |
| `import_bundle_media_assets` | L255-283 | 29 | 4 | 2 | 4 | ✓ |
| `copy_to_media` | L56-72 | 17 | 3 | 2 | 2 | ✓ |
| `import_bundle_resource_assets` | L233-249 | 17 | 3 | 1 | 4 | ✓ |
| `enqueue` | L362-367 | 6 | 3 | 1 | 2 | ✓ |
| `ensure_teacher` | L29-34 | 6 | 2 | 1 | 1 | ✓ |
| `ensure_course_record` | L40-50 | 11 | 2 | 1 | 2 | ✓ |
| `resolve_resources_root` | L311-315 | 5 | 2 | 1 | 1 | ✓ |
| `bundle_has_importable_assets` | L78-90 | 13 | 1 | 0 | 1 | ✓ |

**全部问题 (5)**

- 🔄 `import_bundle_question_assets()` L179: 复杂度: 12
- 🔄 `import_bundle_question_assets()` L179: 认知复杂度: 18
- 📏 `import_media_resources()` L96: 7 参数数量
- 🏗️ `import_bundle_question_assets()` L179: 中等嵌套: 3
- ❌ L129: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 12
- 认知复杂度: 平均: 7.5, 最大: 18
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 20.9 行, 最大: 49 行
- 文件长度: 288 代码量 (382 总计)
- 参数数量: 平均: 2.6, 最大: 7
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 1 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 15.3% (44/288)
- 命名规范: 无命名违规

### 27. backend\users\profile_generation.py

**糟糕指数: 12.95**

> 行数: 331 总计, 264 代码, 31 注释 | 函数: 9 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_profile_text` | L247-298 | 52 | 9 | 1 | 7 | ✓ |
| `generate_profile_for_course` | L48-170 | 123 | 7 | 3 | 3 | ✓ |
| `refresh_mastery_with_kt` | L203-241 | 39 | 6 | 2 | 2 | ✓ |
| `load_cached_profile_result` | L176-184 | 9 | 2 | 1 | 2 | ✓ |
| `resolve_course_name` | L190-197 | 8 | 2 | 1 | 1 | ✓ |
| `record_profile_llm_log` | L304-324 | 21 | 2 | 1 | 5 | ✓ |
| `get_knowledge_mastery` | L29-30 | 2 | 1 | 0 | 2 | ✓ |
| `get_ability_scores` | L35-36 | 2 | 1 | 0 | 2 | ✓ |
| `get_habit_preferences` | L41-42 | 2 | 1 | 0 | 1 | ✓ |

**全部问题 (7)**

- 🔄 `generate_profile_for_course()` L48: 认知复杂度: 13
- 📏 `generate_profile_for_course()` L48: 123 代码量
- 📏 `build_profile_text()` L247: 52 代码量
- 📏 `build_profile_text()` L247: 7 参数数量
- 🏗️ `generate_profile_for_course()` L48: 中等嵌套: 3
- ❌ L279: 未处理的易出错调用
- ❌ L281: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.4, 最大: 9
- 认知复杂度: 平均: 5.4, 最大: 13
- 嵌套深度: 平均: 1.0, 最大: 3
- 函数长度: 平均: 28.7 行, 最大: 123 行
- 文件长度: 264 代码量 (331 总计)
- 参数数量: 平均: 2.8, 最大: 7
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 2/7 个错误被忽略 (28.6%)
- 注释比例: 11.7% (31/264)
- 命名规范: 无命名违规

### 28. backend\knowledge\services.py

**糟糕指数: 12.89**

> 行数: 110 总计, 81 代码, 9 注释 | 函数: 2 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_or_generate_point_intro` | L47-109 | 63 | 14 | 1 | 1 | ✓ |
| `build_intro_fallback` | L30-41 | 12 | 4 | 0 | 1 | ✓ |

**全部问题 (5)**

- 🔄 `get_or_generate_point_intro()` L47: 复杂度: 14
- 🔄 `get_or_generate_point_intro()` L47: 认知复杂度: 16
- 📏 `get_or_generate_point_intro()` L47: 63 代码量
- ❌ L104: 未处理的易出错调用
- ❌ L106: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 9.0, 最大: 14
- 认知复杂度: 平均: 10.0, 最大: 16
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 37.5 行, 最大: 63 行
- 文件长度: 81 代码量 (110 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 2/5 个错误被忽略 (40.0%)
- 注释比例: 11.1% (9/81)
- 命名规范: 无命名违规

### 29. backend\ai_services\services\llm_response_mixin.py

**糟糕指数: 12.81**

> 行数: 402 总计, 325 代码, 42 注释 | 函数: 13 | 类: 1

**问题**: ⚠️ 其他问题: 6, ❌ 错误处理问题: 2, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_agent_json_call` | L107-141 | 35 | 5 | 1 | 6 | ✓ |
| `_try_agent_structured_call` | L265-295 | 31 | 5 | 1 | 5 | ✓ |
| `_attempt_llm_json_response` | L161-183 | 23 | 4 | 1 | 5 | ✓ |
| `_run_llm_json_call` | L188-236 | 49 | 4 | 2 | 7 | ✓ |
| `_prepare_structured_call` | L243-260 | 18 | 4 | 1 | 3 | ✓ |
| `_call_with_fallback` | L328-377 | 50 | 4 | 1 | 6 | ✓ |
| `_apply_temperature_override` | L81-87 | 7 | 3 | 1 | 2 | ✓ |
| `_restore_temperature` | L72-75 | 4 | 2 | 1 | 2 | ✓ |
| `_repair_json_response` | L45-66 | 22 | 1 | 0 | 4 | ✓ |
| `_finalize_success_response` | L94-102 | 9 | 1 | 0 | 4 | ✓ |
| `_invoke_llm_messages` | L146-156 | 11 | 1 | 0 | 3 | ✓ |
| `_run_model_structured_call` | L300-323 | 24 | 1 | 1 | 8 | ✓ |
| `call_with_fallback` | L382-397 | 16 | 1 | 0 | 6 | ✓ |

**全部问题 (17)**

- 📏 `_run_agent_json_call()` L107: 6 参数数量
- 📏 `_run_llm_json_call()` L188: 7 参数数量
- 📏 `_run_model_structured_call()` L300: 8 参数数量
- 📏 `_call_with_fallback()` L328: 6 参数数量
- 📏 `call_with_fallback()` L382: 6 参数数量
- ❌ L171: 未处理的易出错调用
- ❌ L181: 未处理的易出错调用
- 🏷️ `_repair_json_response()` L45: "_repair_json_response" - snake_case
- 🏷️ `_restore_temperature()` L72: "_restore_temperature" - snake_case
- 🏷️ `_apply_temperature_override()` L81: "_apply_temperature_override" - snake_case
- 🏷️ `_finalize_success_response()` L94: "_finalize_success_response" - snake_case
- 🏷️ `_run_agent_json_call()` L107: "_run_agent_json_call" - snake_case
- 🏷️ `_invoke_llm_messages()` L146: "_invoke_llm_messages" - snake_case
- 🏷️ `_attempt_llm_json_response()` L161: "_attempt_llm_json_response" - snake_case
- 🏷️ `_run_llm_json_call()` L188: "_run_llm_json_call" - snake_case
- 🏷️ `_prepare_structured_call()` L243: "_prepare_structured_call" - snake_case
- 🏷️ `_try_agent_structured_call()` L265: "_try_agent_structured_call" - snake_case

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 5
- 认知复杂度: 平均: 4.3, 最大: 8
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 23.0 行, 最大: 50 行
- 文件长度: 325 代码量 (402 总计)
- 参数数量: 平均: 4.7, 最大: 8
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 2/2 个错误被忽略 (100.0%)
- 注释比例: 12.9% (42/325)
- 命名规范: 发现 12 个违规

### 30. backend\tools\cli_menu.py

**糟糕指数: 12.62**

> 行数: 355 总计, 288 代码, 35 注释 | 函数: 11 | 类: 0

**问题**: 🔄 复杂度问题: 6, 🏗️ 结构问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_handle_data_menu_choice` | L124-168 | 45 | 15 | 2 | 1 | ✓ |
| `_handle_graphrag_and_demo_menu_choice` | L282-311 | 30 | 15 | 2 | 1 | ✓ |
| `_handle_kt_menu_choice` | L246-276 | 31 | 12 | 1 | 1 | ✓ |
| `_handle_neo4j_menu_choice` | L197-217 | 21 | 7 | 1 | 1 | ✓ |
| `_handle_database_menu_choice` | L174-191 | 18 | 6 | 1 | 1 | ✓ |
| `_handle_api_and_service_menu_choice` | L223-240 | 18 | 6 | 1 | 1 | ✓ |
| `_handle_menu_choice` | L327-338 | 12 | 4 | 2 | 1 | ✓ |
| `show_menu` | L344-354 | 11 | 4 | 3 | 0 | ✓ |
| `_render_menu` | L91-98 | 8 | 2 | 1 | 0 | ✓ |
| `_parse_optional_course_id` | L104-107 | 4 | 2 | 0 | 1 | ✓ |
| `_prompt_yes_no` | L113-118 | 6 | 2 | 1 | 2 | ✓ |

**全部问题 (17)**

- 🔄 `_handle_data_menu_choice()` L124: 复杂度: 15
- 🔄 `_handle_kt_menu_choice()` L246: 复杂度: 12
- 🔄 `_handle_graphrag_and_demo_menu_choice()` L282: 复杂度: 15
- 🔄 `_handle_data_menu_choice()` L124: 认知复杂度: 19
- 🔄 `_handle_kt_menu_choice()` L246: 认知复杂度: 14
- 🔄 `_handle_graphrag_and_demo_menu_choice()` L282: 认知复杂度: 19
- 🏗️ `show_menu()` L344: 中等嵌套: 3
- 🏷️ `_render_menu()` L91: "_render_menu" - snake_case
- 🏷️ `_parse_optional_course_id()` L104: "_parse_optional_course_id" - snake_case
- 🏷️ `_prompt_yes_no()` L113: "_prompt_yes_no" - snake_case
- 🏷️ `_handle_data_menu_choice()` L124: "_handle_data_menu_choice" - snake_case
- 🏷️ `_handle_database_menu_choice()` L174: "_handle_database_menu_choice" - snake_case
- 🏷️ `_handle_neo4j_menu_choice()` L197: "_handle_neo4j_menu_choice" - snake_case
- 🏷️ `_handle_api_and_service_menu_choice()` L223: "_handle_api_and_service_menu_choice" - snake_case
- 🏷️ `_handle_kt_menu_choice()` L246: "_handle_kt_menu_choice" - snake_case
- 🏷️ `_handle_graphrag_and_demo_menu_choice()` L282: "_handle_graphrag_and_demo_menu_choice" - snake_case
- 🏷️ `_handle_menu_choice()` L327: "_handle_menu_choice" - snake_case

**详情**:
- 循环复杂度: 平均: 6.8, 最大: 15
- 认知复杂度: 平均: 9.5, 最大: 19
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 18.5 行, 最大: 45 行
- 文件长度: 288 代码量 (355 总计)
- 参数数量: 平均: 0.9, 最大: 2
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 12.2% (35/288)
- 命名规范: 发现 10 个违规

### 31. backend\tools\ai_services_test.py

**糟糕指数: 12.54**

> 行数: 91 总计, 73 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_kt_service` | L11-71 | 61 | 9 | 4 | 0 | ✓ |
| `test_llm_service` | L77-90 | 14 | 1 | 0 | 0 | ✓ |

**全部问题 (8)**

- 🔄 `test_kt_service()` L11: 认知复杂度: 17
- 🔄 `test_kt_service()` L11: 嵌套深度: 4
- 📏 `test_kt_service()` L11: 61 代码量
- 🏗️ `test_kt_service()` L11: 中等嵌套: 4
- ❌ L18: 未处理的易出错调用
- ❌ L19: 未处理的易出错调用
- ❌ L71: 未处理的易出错调用
- ❌ L90: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 9
- 认知复杂度: 平均: 9.0, 最大: 17
- 嵌套深度: 平均: 2.0, 最大: 4
- 函数长度: 平均: 37.5 行, 最大: 61 行
- 文件长度: 73 代码量 (91 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 未发现函数
- 结构分析: 1 个结构问题
- 错误处理: 4/4 个错误被忽略 (100.0%)
- 注释比例: 8.2% (6/73)
- 命名规范: 无命名违规

### 32. frontend\scripts\browser-audit\demo-scenario.mjs

**糟糕指数: 12.53**

> 行数: 170 总计, 153 代码, 0 注释 | 函数: 7 | 类: 0

**问题**: ⚠️ 其他问题: 4, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `prepareStudentDemoState` | L39-74 | 36 | 4 | 1 | 5 | ✗ |
| `buildPreparedStudentRoutes` | L76-86 | 11 | 3 | 1 | 2 | ✗ |
| `captureStableStudentSimulation` | L132-144 | 13 | 3 | 1 | 5 | ✗ |
| `prepareDemoScenario` | L18-37 | 20 | 2 | 1 | 3 | ✗ |
| `simulateDemoScenario` | L88-105 | 17 | 2 | 1 | 3 | ✗ |
| `simulateStudentDemoFlow` | L107-130 | 24 | 2 | 0 | 6 | ✗ |
| `captureTriggerStudentSimulation` | L146-169 | 24 | 2 | 1 | 7 | ✗ |

**全部问题 (6)**

- 📏 `prepareStudentDemoState()` L39: 5 参数数量
- 📏 `simulateStudentDemoFlow()` L107: 6 参数数量
- 📏 `captureStableStudentSimulation()` L132: 5 参数数量
- 📏 `captureTriggerStudentSimulation()` L146: 7 参数数量
- ❌ L71: 未处理的易出错调用
- ❌ L127: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 4
- 认知复杂度: 平均: 4.3, 最大: 6
- 嵌套深度: 平均: 0.9, 最大: 1
- 函数长度: 平均: 20.7 行, 最大: 36 行
- 文件长度: 153 代码量 (170 总计)
- 参数数量: 平均: 4.4, 最大: 7
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 2/2 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/153)
- 命名规范: 无命名违规

### 33. backend\platform_ai\rag\student_context_mixin.py

**糟糕指数: 12.51**

> 行数: 200 总计, 157 代码, 18 注释 | 函数: 5 | 类: 1

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_drift_context` | L113-162 | 50 | 12 | 3 | 4 | ✓ |
| `_build_local_context` | L22-82 | 61 | 10 | 2 | 5 | ✓ |
| `_build_global_context` | L87-108 | 22 | 5 | 2 | 3 | ✓ |
| `_compose_query_context` | L167-191 | 25 | 4 | 1 | 5 | ✓ |
| `_humanize_document_title` | L196-199 | 4 | 1 | 0 | 2 | ✓ |

**全部问题 (11)**

- 🔄 `_build_drift_context()` L113: 复杂度: 12
- 🔄 `_build_local_context()` L22: 认知复杂度: 14
- 🔄 `_build_drift_context()` L113: 认知复杂度: 18
- 📏 `_build_local_context()` L22: 61 代码量
- 🏗️ `_build_drift_context()` L113: 中等嵌套: 3
- ❌ L124: 未处理的易出错调用
- 🏷️ `_build_local_context()` L22: "_build_local_context" - snake_case
- 🏷️ `_build_global_context()` L87: "_build_global_context" - snake_case
- 🏷️ `_build_drift_context()` L113: "_build_drift_context" - snake_case
- 🏷️ `_compose_query_context()` L167: "_compose_query_context" - snake_case
- 🏷️ `_humanize_document_title()` L196: "_humanize_document_title" - snake_case

**详情**:
- 循环复杂度: 平均: 6.4, 最大: 12
- 认知复杂度: 平均: 9.6, 最大: 18
- 嵌套深度: 平均: 1.6, 最大: 3
- 函数长度: 平均: 32.4 行, 最大: 61 行
- 文件长度: 157 代码量 (200 总计)
- 参数数量: 平均: 3.8, 最大: 5
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 1 个结构问题
- 错误处理: 1/12 个错误被忽略 (8.3%)
- 注释比例: 11.5% (18/157)
- 命名规范: 发现 5 个违规

### 34. backend\platform_ai\llm\agent.py

**糟糕指数: 12.51**

> 行数: 295 总计, 234 代码, 33 注释 | 函数: 11 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_get_model` | L75-108 | 34 | 9 | 2 | 1 | ✓ |
| `_get_agent` | L181-205 | 25 | 5 | 1 | 1 | ✓ |
| `invoke_json` | L210-229 | 20 | 5 | 1 | 4 | ✓ |
| `get_agent_service` | L236-267 | 32 | 4 | 1 | 11 | ✓ |
| `get_default_agent_service` | L273-294 | 22 | 4 | 0 | 0 | ✓ |
| `__init__` | L35-62 | 28 | 2 | 0 | 12 | ✓ |
| `_get_tools` | L113-176 | 28 | 2 | 1 | 1 | ✓ |
| `lookup_course_context` | L125-130 | 6 | 2 | 1 | 2 | ✓ |
| `summarize_mastery` | L155-170 | 16 | 2 | 0 | 2 | ✓ |
| `is_available` | L68-70 | 3 | 1 | 0 | 1 | ✓ |
| `query_course_graphrag` | L136-149 | 14 | 1 | 0 | 4 | ✓ |

**全部问题 (7)**

- 🔄 `_get_model()` L75: 认知复杂度: 13
- 📏 `__init__()` L35: 12 参数数量
- 📏 `get_agent_service()` L236: 11 参数数量
- 🏷️ `__init__()` L35: "__init__" - snake_case
- 🏷️ `_get_model()` L75: "_get_model" - snake_case
- 🏷️ `_get_tools()` L113: "_get_tools" - snake_case
- 🏷️ `_get_agent()` L181: "_get_agent" - snake_case

**详情**:
- 循环复杂度: 平均: 3.4, 最大: 9
- 认知复杂度: 平均: 4.6, 最大: 13
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 20.7 行, 最大: 34 行
- 文件长度: 234 代码量 (295 总计)
- 参数数量: 平均: 3.5, 最大: 12
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 14.1% (33/234)
- 命名规范: 发现 4 个违规

### 35. backend\tools\db_seed_support.py

**糟糕指数: 12.38**

> 行数: 428 总计, 342 代码, 42 注释 | 函数: 13 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 3, 🏗️ 结构问题: 2, ❌ 错误处理问题: 38, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_seed_course_content` | L38-109 | 72 | 10 | 2 | 3 | ✓ |
| `_attach_students_to_classes` | L273-312 | 40 | 8 | 2 | 4 | ✓ |
| `sync_seeded_courses` | L412-427 | 16 | 6 | 3 | 1 | ✓ |
| `_seed_courses` | L185-209 | 25 | 5 | 2 | 3 | ✓ |
| `_seed_classes` | L215-242 | 28 | 5 | 3 | 4 | ✓ |
| `_resolve_big_data_context` | L248-267 | 20 | 4 | 1 | 2 | ✓ |
| `_seed_class_invitations` | L329-347 | 19 | 4 | 2 | 3 | ✓ |
| `_seed_survey_questions` | L353-381 | 29 | 4 | 1 | 2 | ✓ |
| `_seed_user_accounts` | L126-163 | 38 | 3 | 1 | 1 | ✓ |
| `_seed_student_demo_state` | L318-323 | 6 | 3 | 1 | 2 | ✓ |
| `_seed_activation_codes` | L169-179 | 11 | 2 | 1 | 2 | ✓ |
| `_create_user` | L115-120 | 6 | 1 | 0 | 3 | ✓ |
| `seed_database_from_testdata` | L387-406 | 20 | 1 | 0 | 1 | ✓ |

**全部问题 (52)**

- 🔄 `_seed_course_content()` L38: 认知复杂度: 14
- 📏 `_seed_course_content()` L38: 72 代码量
- 🏗️ `_seed_classes()` L215: 中等嵌套: 3
- 🏗️ `sync_seeded_courses()` L412: 中等嵌套: 3
- ❌ L50: 未处理的易出错调用
- ❌ L51: 未处理的易出错调用
- ❌ L52: 未处理的易出错调用
- ❌ L58: 未处理的易出错调用
- ❌ L76: 未处理的易出错调用
- ❌ L78: 未处理的易出错调用
- ❌ L79: 未处理的易出错调用
- ❌ L95: 未处理的易出错调用
- ❌ L96: 未处理的易出错调用
- ❌ L97: 未处理的易出错调用
- ❌ L98: 未处理的易出错调用
- ❌ L99: 未处理的易出错调用
- ❌ L100: 未处理的易出错调用
- ❌ L101: 未处理的易出错调用
- ❌ L140: 未处理的易出错调用
- ❌ L152: 未处理的易出错调用
- ❌ L171: 未处理的易出错调用
- ❌ L177: 未处理的易出错调用
- ❌ L192: 未处理的易出错调用
- ❌ L198: 未处理的易出错调用
- ❌ L200: 未处理的易出错调用
- ❌ L201: 未处理的易出错调用
- ❌ L223: 未处理的易出错调用
- ❌ L229: 未处理的易出错调用
- ❌ L231: 未处理的易出错调用
- ❌ L235: 未处理的易出错调用
- ❌ L335: 未处理的易出错调用
- ❌ L345: 未处理的易出错调用
- ❌ L356: 未处理的易出错调用
- ❌ L362: 未处理的易出错调用
- ❌ L363: 未处理的易出错调用
- ❌ L364: 未处理的易出错调用
- ❌ L365: 未处理的易出错调用
- ❌ L369: 未处理的易出错调用
- ❌ L375: 未处理的易出错调用
- ❌ L376: 未处理的易出错调用
- ❌ L377: 未处理的易出错调用
- ❌ L378: 未处理的易出错调用
- 🏷️ `_seed_course_content()` L38: "_seed_course_content" - snake_case
- 🏷️ `_create_user()` L115: "_create_user" - snake_case
- 🏷️ `_seed_user_accounts()` L126: "_seed_user_accounts" - snake_case
- 🏷️ `_seed_activation_codes()` L169: "_seed_activation_codes" - snake_case
- 🏷️ `_seed_courses()` L185: "_seed_courses" - snake_case
- 🏷️ `_seed_classes()` L215: "_seed_classes" - snake_case
- 🏷️ `_resolve_big_data_context()` L248: "_resolve_big_data_context" - snake_case
- 🏷️ `_attach_students_to_classes()` L273: "_attach_students_to_classes" - snake_case
- 🏷️ `_seed_student_demo_state()` L318: "_seed_student_demo_state" - snake_case
- 🏷️ `_seed_class_invitations()` L329: "_seed_class_invitations" - snake_case

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 10
- 认知复杂度: 平均: 7.2, 最大: 14
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 25.4 行, 最大: 72 行
- 文件长度: 342 代码量 (428 总计)
- 参数数量: 平均: 2.4, 最大: 4
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 2 个结构问题
- 错误处理: 38/55 个错误被忽略 (69.1%)
- 注释比例: 12.3% (42/342)
- 命名规范: 发现 11 个违规

### 36. backend\ai_services\services\path_service.py

**糟糕指数: 12.38**

> 行数: 279 总计, 212 代码, 26 注释 | 函数: 4 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_path` | L43-176 | 134 | 9 | 3 | 4 | ✓ |
| `get_path_progress` | L251-278 | 28 | 4 | 0 | 2 | ✓ |
| `unlock_next_node` | L181-203 | 23 | 2 | 1 | 2 | ✓ |
| `insert_remedial_node` | L208-246 | 39 | 2 | 1 | 4 | ✓ |

**全部问题 (5)**

- 🔄 `generate_path()` L43: 认知复杂度: 15
- 📏 `generate_path()` L43: 134 代码量
- 🏗️ `generate_path()` L43: 中等嵌套: 3
- ❌ L117: 未处理的易出错调用
- ❌ L173: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 9
- 认知复杂度: 平均: 6.8, 最大: 15
- 嵌套深度: 平均: 1.3, 最大: 3
- 函数长度: 平均: 56.0 行, 最大: 134 行
- 文件长度: 212 代码量 (279 总计)
- 参数数量: 平均: 3.0, 最大: 4
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 1 个结构问题
- 错误处理: 2/4 个错误被忽略 (50.0%)
- 注释比例: 12.3% (26/212)
- 命名规范: 无命名违规

### 37. backend\tools\testing.py

**糟糕指数: 12.30**

> 行数: 271 总计, 184 代码, 35 注释 | 函数: 8 | 类: 1

**问题**: 🔄 复杂度问题: 4, 🏗️ 结构问题: 1, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_resolve_course_id` | L182-229 | 48 | 13 | 2 | 3 | ✓ |
| `_load_testdata` | L236-270 | 35 | 10 | 4 | 0 | ✓ |
| `_login` | L142-175 | 34 | 8 | 1 | 3 | ✓ |
| `_print_checks` | L56-83 | 28 | 6 | 2 | 2 | ✓ |
| `_status_flag` | L33-37 | 5 | 4 | 1 | 1 | ✓ |
| `_extract_data` | L117-135 | 19 | 3 | 1 | 1 | ✓ |
| `_supports_unicode_output` | L24-27 | 4 | 2 | 0 | 0 | ✓ |
| `_request` | L90-111 | 22 | 2 | 1 | 2 | ✓ |

**全部问题 (13)**

- 🔄 `_resolve_course_id()` L182: 复杂度: 13
- 🔄 `_resolve_course_id()` L182: 认知复杂度: 17
- 🔄 `_load_testdata()` L236: 认知复杂度: 18
- 🔄 `_load_testdata()` L236: 嵌套深度: 4
- 🏗️ `_load_testdata()` L236: 中等嵌套: 4
- 🏷️ `_supports_unicode_output()` L24: "_supports_unicode_output" - snake_case
- 🏷️ `_status_flag()` L33: "_status_flag" - snake_case
- 🏷️ `_print_checks()` L56: "_print_checks" - snake_case
- 🏷️ `_request()` L90: "_request" - snake_case
- 🏷️ `_extract_data()` L117: "_extract_data" - snake_case
- 🏷️ `_login()` L142: "_login" - snake_case
- 🏷️ `_resolve_course_id()` L182: "_resolve_course_id" - snake_case
- 🏷️ `_load_testdata()` L236: "_load_testdata" - snake_case

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 13
- 认知复杂度: 平均: 9.0, 最大: 18
- 嵌套深度: 平均: 1.5, 最大: 4
- 函数长度: 平均: 24.4 行, 最大: 48 行
- 文件长度: 184 代码量 (271 总计)
- 参数数量: 平均: 1.5, 最大: 3
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 0/5 个错误被忽略 (0.0%)
- 注释比例: 19.0% (35/184)
- 命名规范: 发现 8 个违规

### 38. backend\courses\admin_views.py

**糟糕指数: 12.21**

> 行数: 504 总计, 384 代码, 44 注释 | 函数: 12 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 4, 🏗️ 结构问题: 2, ❌ 错误处理问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `admin_class_detail` | L196-255 | 60 | 14 | 3 | 2 | ✓ |
| `admin_course_detail` | L380-433 | 54 | 13 | 2 | 2 | ✓ |
| `admin_class_create` | L148-188 | 41 | 8 | 2 | 1 | ✓ |
| `admin_course_create` | L341-372 | 32 | 8 | 2 | 1 | ✓ |
| `admin_class_list` | L85-140 | 56 | 7 | 2 | 1 | ✓ |
| `admin_course_assign_teacher` | L441-472 | 32 | 7 | 2 | 2 | ✓ |
| `admin_class_add_students` | L291-315 | 25 | 6 | 3 | 2 | ✓ |
| `admin_course_list` | L38-77 | 40 | 5 | 1 | 1 | ✓ |
| `admin_class_assign_teacher` | L480-503 | 24 | 5 | 2 | 2 | ✓ |
| `admin_class_students` | L263-283 | 21 | 3 | 1 | 2 | ✓ |
| `_parse_pagination_params` | L19-30 | 12 | 2 | 1 | 1 | ✓ |
| `admin_class_remove_student` | L323-333 | 11 | 2 | 1 | 3 | ✓ |

**全部问题 (12)**

- 🔄 `admin_class_detail()` L196: 复杂度: 14
- 🔄 `admin_course_detail()` L380: 复杂度: 13
- 🔄 `admin_class_detail()` L196: 认知复杂度: 20
- 🔄 `admin_course_detail()` L380: 认知复杂度: 17
- 📏 `admin_class_list()` L85: 56 代码量
- 📏 `admin_class_detail()` L196: 60 代码量
- 📏 `admin_course_detail()` L380: 54 代码量
- 🏗️ `admin_class_detail()` L196: 中等嵌套: 3
- 🏗️ `admin_class_add_students()` L291: 中等嵌套: 3
- ❌ L220: 未处理的易出错调用
- ❌ L330: 未处理的易出错调用
- ❌ L410: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 6.7, 最大: 14
- 认知复杂度: 平均: 10.3, 最大: 20
- 嵌套深度: 平均: 1.8, 最大: 3
- 函数长度: 平均: 34.0 行, 最大: 60 行
- 文件长度: 384 代码量 (504 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 2 个结构问题
- 错误处理: 3/45 个错误被忽略 (6.7%)
- 注释比例: 11.5% (44/384)
- 命名规范: 发现 1 个违规

### 39. backend\courses\student_views.py

**糟糕指数: 12.10**

> 行数: 380 总计, 272 代码, 41 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `course_list` | L85-136 | 52 | 10 | 4 | 1 | ✓ |
| `course_select` | L144-198 | 55 | 10 | 2 | 1 | ✓ |
| `student_join_class` | L209-271 | 63 | 9 | 1 | 1 | ✓ |
| `_serialize_student_class` | L57-77 | 21 | 6 | 0 | 1 | ✓ |
| `student_class_detail` | L330-376 | 47 | 6 | 1 | 2 | ✓ |
| `_get_class_course_summaries` | L32-51 | 20 | 5 | 2 | 1 | ✓ |
| `student_leave_class` | L279-296 | 18 | 3 | 1 | 2 | ✓ |
| `_serialize_course_summary` | L20-26 | 7 | 2 | 0 | 1 | ✓ |
| `student_class_list` | L304-322 | 19 | 2 | 1 | 1 | ✓ |

**全部问题 (13)**

- 🔄 `course_list()` L85: 认知复杂度: 18
- 🔄 `course_select()` L144: 认知复杂度: 14
- 🔄 `course_list()` L85: 嵌套深度: 4
- 📏 `course_list()` L85: 52 代码量
- 📏 `course_select()` L144: 55 代码量
- 📏 `student_join_class()` L209: 63 代码量
- 🏗️ `course_list()` L85: 中等嵌套: 4
- ❌ L74: 未处理的易出错调用
- ❌ L75: 未处理的易出错调用
- ❌ L295: 未处理的易出错调用
- 🏷️ `_serialize_course_summary()` L20: "_serialize_course_summary" - snake_case
- 🏷️ `_get_class_course_summaries()` L32: "_get_class_course_summaries" - snake_case
- 🏷️ `_serialize_student_class()` L57: "_serialize_student_class" - snake_case

**详情**:
- 循环复杂度: 平均: 5.9, 最大: 10
- 认知复杂度: 平均: 8.6, 最大: 18
- 嵌套深度: 平均: 1.3, 最大: 4
- 函数长度: 平均: 33.6 行, 最大: 63 行
- 文件长度: 272 代码量 (380 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 3/10 个错误被忽略 (30.0%)
- 注释比例: 15.1% (41/272)
- 命名规范: 发现 3 个违规

### 40. backend\ai_services\services\kt_prediction_stats.py

**糟糕指数: 12.09**

> 行数: 222 总计, 171 代码, 24 注释 | 函数: 7 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 5, 🏷️ 命名问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_calculate_point_mastery` | L108-178 | 71 | 10 | 3 | 3 | ✓ |
| `_extract_prediction_map` | L71-89 | 19 | 5 | 2 | 1 | ✓ |
| `_attach_prediction_metadata` | L21-39 | 19 | 4 | 0 | 3 | ✓ |
| `_estimate_stat_confidence` | L44-65 | 22 | 4 | 1 | 4 | ✓ |
| `_coerce_int_identifier` | L95-103 | 9 | 3 | 1 | 2 | ✓ |
| `_get_default_prediction` | L207-221 | 15 | 3 | 2 | 2 | ✓ |
| `_prepare_input_data` | L184-202 | 19 | 1 | 0 | 1 | ✓ |

**全部问题 (15)**

- 🔄 `_calculate_point_mastery()` L108: 认知复杂度: 16
- 📏 `_calculate_point_mastery()` L108: 71 代码量
- 🏗️ `_calculate_point_mastery()` L108: 中等嵌套: 3
- ❌ L34: 未处理的易出错调用
- ❌ L36: 未处理的易出错调用
- ❌ L54: 未处理的易出错调用
- ❌ L56: 未处理的易出错调用
- ❌ L192: 未处理的易出错调用
- 🏷️ `_attach_prediction_metadata()` L21: "_attach_prediction_metadata" - snake_case
- 🏷️ `_estimate_stat_confidence()` L44: "_estimate_stat_confidence" - snake_case
- 🏷️ `_extract_prediction_map()` L71: "_extract_prediction_map" - snake_case
- 🏷️ `_coerce_int_identifier()` L95: "_coerce_int_identifier" - snake_case
- 🏷️ `_calculate_point_mastery()` L108: "_calculate_point_mastery" - snake_case
- 🏷️ `_prepare_input_data()` L184: "_prepare_input_data" - snake_case
- 🏷️ `_get_default_prediction()` L207: "_get_default_prediction" - snake_case

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 10
- 认知复杂度: 平均: 6.9, 最大: 16
- 嵌套深度: 平均: 1.3, 最大: 3
- 函数长度: 平均: 24.9 行, 最大: 71 行
- 文件长度: 171 代码量 (222 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 1 个结构问题
- 错误处理: 5/11 个错误被忽略 (45.5%)
- 注释比例: 14.0% (24/171)
- 命名规范: 发现 7 个违规

### 41. backend\exams\student_submission_support.py

**糟糕指数: 11.93**

> 行数: 369 总计, 304 代码, 30 注释 | 函数: 8 | 类: 2

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `refresh_exam_kt_analysis` | L234-303 | 70 | 7 | 4 | 3 | ✓ |
| `upsert_exam_submission_record` | L102-138 | 37 | 6 | 1 | 4 | ✓ |
| `sync_result_submission_snapshot` | L359-368 | 10 | 5 | 1 | 2 | ✓ |
| `build_answer_history_batch` | L144-197 | 54 | 4 | 2 | 4 | ✓ |
| `build_exam_submission_context` | L58-96 | 39 | 2 | 0 | 2 | ✓ |
| `persist_answer_histories` | L203-208 | 6 | 2 | 1 | 1 | ✓ |
| `capture_mastery_snapshot_from_records` | L214-228 | 15 | 1 | 0 | 3 | ✓ |
| `build_submission_feedback_state` | L309-353 | 45 | 1 | 0 | 6 | ✓ |

**全部问题 (9)**

- 🔄 `refresh_exam_kt_analysis()` L234: 认知复杂度: 15
- 🔄 `refresh_exam_kt_analysis()` L234: 嵌套深度: 4
- 📏 `build_answer_history_batch()` L144: 54 代码量
- 📏 `refresh_exam_kt_analysis()` L234: 70 代码量
- 📏 `build_submission_feedback_state()` L309: 6 参数数量
- 🏗️ `refresh_exam_kt_analysis()` L234: 中等嵌套: 4
- ❌ L225: 未处理的易出错调用
- ❌ L282: 未处理的易出错调用
- ❌ L283: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 7
- 认知复杂度: 平均: 5.8, 最大: 15
- 嵌套深度: 平均: 1.1, 最大: 4
- 函数长度: 平均: 34.5 行, 最大: 70 行
- 文件长度: 304 代码量 (369 总计)
- 参数数量: 平均: 3.1, 最大: 6
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 3/10 个错误被忽略 (30.0%)
- 注释比例: 9.9% (30/304)
- 命名规范: 无命名违规

### 42. backend\ai_services\services\kt_service.py

**糟糕指数: 11.59**

> 行数: 302 总计, 239 代码, 24 注释 | 函数: 8 | 类: 1

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 7, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__init__` | L70-129 | 60 | 8 | 1 | 6 | ✓ |
| `is_available` | L210-238 | 29 | 6 | 2 | 1 | ✓ |
| `_resolve_backend_path` | L43-53 | 11 | 4 | 1 | 1 | ✓ |
| `_resolve_enabled_models` | L134-155 | 22 | 4 | 2 | 2 | ✓ |
| `_normalize_weights` | L182-204 | 23 | 4 | 2 | 1 | ✓ |
| `get_model_info` | L243-277 | 35 | 4 | 1 | 1 | ✓ |
| `_load_fusion_weights` | L160-177 | 18 | 3 | 2 | 1 | ✓ |
| `_load_runtime_info` | L282-291 | 10 | 3 | 2 | 2 | ✓ |

**全部问题 (15)**

- 📏 `__init__()` L70: 60 代码量
- 📏 `__init__()` L70: 6 参数数量
- ❌ L251: 未处理的易出错调用
- ❌ L252: 未处理的易出错调用
- ❌ L253: 未处理的易出错调用
- ❌ L254: 未处理的易出错调用
- ❌ L255: 未处理的易出错调用
- ❌ L256: 未处理的易出错调用
- ❌ L270: 未处理的易出错调用
- 🏷️ `_resolve_backend_path()` L43: "_resolve_backend_path" - snake_case
- 🏷️ `__init__()` L70: "__init__" - snake_case
- 🏷️ `_resolve_enabled_models()` L134: "_resolve_enabled_models" - snake_case
- 🏷️ `_load_fusion_weights()` L160: "_load_fusion_weights" - snake_case
- 🏷️ `_normalize_weights()` L182: "_normalize_weights" - snake_case
- 🏷️ `_load_runtime_info()` L282: "_load_runtime_info" - snake_case

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 8
- 认知复杂度: 平均: 7.8, 最大: 10
- 嵌套深度: 平均: 1.6, 最大: 2
- 函数长度: 平均: 26.0 行, 最大: 60 行
- 文件长度: 239 代码量 (302 总计)
- 参数数量: 平均: 1.9, 最大: 6
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 7/9 个错误被忽略 (77.8%)
- 注释比例: 10.0% (24/239)
- 命名规范: 发现 6 个违规

### 43. backend\ai_services\services\llm_resource_support.py

**糟糕指数: 11.55**

> 行数: 238 总计, 200 代码, 15 注释 | 函数: 5 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 3, 🏗️ 结构问题: 2, ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_internal_resources_prompt` | L111-183 | 73 | 11 | 3 | 5 | ✓ |
| `normalize_external_resource_result` | L85-105 | 21 | 6 | 3 | 4 | ✓ |
| `build_external_resources_prompt` | L11-79 | 69 | 4 | 1 | 5 | ✓ |
| `normalize_internal_resource_result` | L189-194 | 6 | 2 | 0 | 2 | ✓ |
| `build_stage_question_prompt` | L200-237 | 38 | 1 | 0 | 3 | ✓ |

**全部问题 (8)**

- 🔄 `build_internal_resources_prompt()` L111: 复杂度: 11
- 🔄 `build_internal_resources_prompt()` L111: 认知复杂度: 17
- 📏 `build_external_resources_prompt()` L11: 69 代码量
- 📏 `build_internal_resources_prompt()` L111: 73 代码量
- 🏗️ `normalize_external_resource_result()` L85: 中等嵌套: 3
- 🏗️ `build_internal_resources_prompt()` L111: 中等嵌套: 3
- ❌ L123: 未处理的易出错调用
- ❌ L177: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 11
- 认知复杂度: 平均: 7.6, 最大: 17
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 41.4 行, 最大: 73 行
- 文件长度: 200 代码量 (238 总计)
- 参数数量: 平均: 3.8, 最大: 5
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 2 个结构问题
- 错误处理: 2/7 个错误被忽略 (28.6%)
- 注释比例: 7.5% (15/200)
- 命名规范: 无命名违规

### 44. backend\platform_ai\rag\student_resource_mixin.py

**糟糕指数: 11.54**

> 行数: 372 总计, 289 代码, 45 注释 | 函数: 13 | 类: 2

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, ❌ 错误处理问题: 6, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_parse_internal_llm_result` | L295-318 | 24 | 8 | 2 | 3 | ✓ |
| `_parse_external_llm_result` | L345-371 | 27 | 7 | 2 | 3 | ✓ |
| `_select_internal_resources` | L169-201 | 33 | 4 | 1 | 5 | ✓ |
| `_serialize_available_resources` | L275-289 | 15 | 4 | 0 | 2 | ✓ |
| `recommend_node_resources` | L44-54 | 11 | 3 | 0 | 2 | ✓ |
| `_build_internal_resources` | L133-164 | 32 | 3 | 2 | 5 | ✓ |
| `_build_external_resources` | L206-240 | 35 | 3 | 1 | 4 | ✓ |
| `_recommend_node_resources` | L81-112 | 32 | 2 | 1 | 2 | ✓ |
| `recommend_resources_for_node` | L59-76 | 18 | 1 | 0 | 6 | ✓ |
| `_search_internal_candidates` | L117-128 | 12 | 1 | 0 | 3 | ✓ |
| `_resource_map` | L246-254 | 9 | 1 | 0 | 1 | ✓ |
| `_ordered_resources` | L260-269 | 10 | 1 | 0 | 2 | ✓ |
| `_fallback_internal_selection` | L324-339 | 16 | 1 | 0 | 3 | ✓ |

**全部问题 (18)**

- 📏 `recommend_resources_for_node()` L59: 6 参数数量
- 📋 `recommend_node_resources()` L44: 重复模式: recommend_node_resources, recommend_resources_for_node
- ❌ L315: 未处理的易出错调用
- ❌ L316: 未处理的易出错调用
- ❌ L361: 未处理的易出错调用
- ❌ L362: 未处理的易出错调用
- ❌ L363: 未处理的易出错调用
- ❌ L364: 未处理的易出错调用
- 🏷️ `_recommend_node_resources()` L81: "_recommend_node_resources" - snake_case
- 🏷️ `_search_internal_candidates()` L117: "_search_internal_candidates" - snake_case
- 🏷️ `_build_internal_resources()` L133: "_build_internal_resources" - snake_case
- 🏷️ `_select_internal_resources()` L169: "_select_internal_resources" - snake_case
- 🏷️ `_build_external_resources()` L206: "_build_external_resources" - snake_case
- 🏷️ `_resource_map()` L246: "_resource_map" - snake_case
- 🏷️ `_ordered_resources()` L260: "_ordered_resources" - snake_case
- 🏷️ `_serialize_available_resources()` L275: "_serialize_available_resources" - snake_case
- 🏷️ `_parse_internal_llm_result()` L295: "_parse_internal_llm_result" - snake_case
- 🏷️ `_fallback_internal_selection()` L324: "_fallback_internal_selection" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 8
- 认知复杂度: 平均: 4.4, 最大: 12
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 21.1 行, 最大: 35 行
- 文件长度: 289 代码量 (372 总计)
- 参数数量: 平均: 3.2, 最大: 6
- 代码重复: 7.7% 重复 (1/13)
- 结构分析: 0 个结构问题
- 错误处理: 6/14 个错误被忽略 (42.9%)
- 注释比例: 15.6% (45/289)
- 命名规范: 发现 11 个违规

### 45. backend\platform_ai\rag\runtime.py

**糟糕指数: 11.45**

> 行数: 334 总计, 285 代码, 23 注释 | 函数: 7 | 类: 1

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `invoke_with_tools` | L230-308 | 79 | 11 | 3 | 5 | ✓ |
| `heuristic_tool_calls` | L109-174 | 66 | 10 | 1 | 2 | ✓ |
| `normalize_invoke_input` | L63-91 | 29 | 9 | 2 | 1 | ✓ |
| `invoke` | L179-209 | 31 | 5 | 1 | 6 | ✓ |
| `response_format_hint` | L97-103 | 7 | 4 | 1 | 1 | ✓ |
| `__init__` | L53-57 | 5 | 1 | 0 | 1 | ✗ |
| `ainvoke` | L214-225 | 12 | 1 | 0 | 4 | ✓ |

**全部问题 (8)**

- 🔄 `invoke_with_tools()` L230: 复杂度: 11
- 🔄 `normalize_invoke_input()` L63: 认知复杂度: 13
- 🔄 `invoke_with_tools()` L230: 认知复杂度: 17
- 📏 `heuristic_tool_calls()` L109: 66 代码量
- 📏 `invoke_with_tools()` L230: 79 代码量
- 📏 `invoke()` L179: 6 参数数量
- 🏗️ `invoke_with_tools()` L230: 中等嵌套: 3
- 🏷️ `__init__()` L53: "__init__" - snake_case

**详情**:
- 循环复杂度: 平均: 5.9, 最大: 11
- 认知复杂度: 平均: 8.1, 最大: 17
- 嵌套深度: 平均: 1.1, 最大: 3
- 函数长度: 平均: 32.7 行, 最大: 79 行
- 文件长度: 285 代码量 (334 总计)
- 参数数量: 平均: 2.9, 最大: 6
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 1 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 8.1% (23/285)
- 命名规范: 发现 1 个违规

### 46. backend\ai_services\services\mefkt_runtime_rows.py

**糟糕指数: 11.43**

> 行数: 239 总计, 190 代码, 26 注释 | 函数: 8 | 类: 1

**问题**: ⚠️ 其他问题: 4, ❌ 错误处理问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_single_feature_row` | L75-107 | 33 | 2 | 0 | 9 | ✓ |
| `build_feature_value_map` | L113-142 | 30 | 2 | 0 | 8 | ✓ |
| `build_runtime_feature_rows` | L148-177 | 30 | 2 | 1 | 7 | ✓ |
| `build_neighbor_difficulty_tensor` | L27-40 | 14 | 1 | 0 | 2 | ✓ |
| `build_relation_stats_matrix` | L46-69 | 24 | 1 | 0 | 2 | ✓ |
| `__init__` | L186-190 | 5 | 1 | 0 | 2 | ✗ |
| `add_row` | L195-222 | 28 | 1 | 0 | 10 | ✓ |
| `to_tuple` | L227-238 | 12 | 1 | 0 | 2 | ✓ |

**全部问题 (6)**

- 📏 `build_single_feature_row()` L75: 9 参数数量
- 📏 `build_feature_value_map()` L113: 8 参数数量
- 📏 `build_runtime_feature_rows()` L148: 7 参数数量
- 📏 `add_row()` L195: 10 参数数量
- ❌ L137: 未处理的易出错调用
- 🏷️ `__init__()` L186: "__init__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 2
- 认知复杂度: 平均: 1.6, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 22.0 行, 最大: 33 行
- 文件长度: 190 代码量 (239 总计)
- 参数数量: 平均: 5.3, 最大: 10
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 1/2 个错误被忽略 (50.0%)
- 注释比例: 13.7% (26/190)
- 命名规范: 发现 1 个违规

### 47. backend\ai_services\student_ai_profile_views.py

**糟糕指数: 11.42**

> 行数: 356 总计, 283 代码, 33 注释 | 函数: 11 | 类: 0

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 7, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ai_feedback_report` | L138-189 | 52 | 14 | 2 | 1 | ✓ |
| `ai_resource_reason` | L88-130 | 43 | 13 | 3 | 1 | ✓ |
| `ai_profile_analysis` | L58-80 | 23 | 9 | 1 | 1 | ✓ |
| `ai_refresh_profile` | L223-236 | 14 | 5 | 1 | 1 | ✓ |
| `ai_refresh_learning_path` | L244-284 | 41 | 5 | 1 | 1 | ✓ |
| `ai_time_scheduling` | L315-332 | 18 | 5 | 1 | 1 | ✓ |
| `ai_analysis_compare` | L340-355 | 16 | 5 | 1 | 1 | ✓ |
| `ai_learning_advice` | L197-215 | 19 | 4 | 1 | 1 | ✓ |
| `ai_key_points_reminder` | L292-307 | 16 | 4 | 1 | 1 | ✓ |
| `_build_habit_data` | L29-34 | 6 | 2 | 1 | 1 | ✓ |
| `_build_mastery_data` | L40-50 | 11 | 2 | 0 | 2 | ✓ |

**全部问题 (15)**

- 🔄 `ai_resource_reason()` L88: 复杂度: 13
- 🔄 `ai_feedback_report()` L138: 复杂度: 14
- 🔄 `ai_resource_reason()` L88: 认知复杂度: 19
- 🔄 `ai_feedback_report()` L138: 认知复杂度: 18
- 📏 `ai_feedback_report()` L138: 52 代码量
- 🏗️ `ai_resource_reason()` L88: 中等嵌套: 3
- ❌ L78: 未处理的易出错调用
- ❌ L123: 未处理的易出错调用
- ❌ L211: 未处理的易出错调用
- ❌ L212: 未处理的易出错调用
- ❌ L213: 未处理的易出错调用
- ❌ L214: 未处理的易出错调用
- ❌ L234: 未处理的易出错调用
- 🏷️ `_build_habit_data()` L29: "_build_habit_data" - snake_case
- 🏷️ `_build_mastery_data()` L40: "_build_mastery_data" - snake_case

**详情**:
- 循环复杂度: 平均: 6.2, 最大: 14
- 认知复杂度: 平均: 8.5, 最大: 19
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 23.5 行, 最大: 52 行
- 文件长度: 283 代码量 (356 总计)
- 参数数量: 平均: 1.1, 最大: 2
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 1 个结构问题
- 错误处理: 7/33 个错误被忽略 (21.2%)
- 注释比例: 11.7% (33/283)
- 命名规范: 发现 2 个违规

### 48. backend\knowledge\teacher_point_views.py

**糟糕指数: 11.40**

> 行数: 183 总计, 147 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 8, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `knowledge_point_update` | L124-161 | 38 | 12 | 1 | 2 | ✓ |
| `knowledge_point_create` | L69-116 | 48 | 10 | 3 | 1 | ✓ |
| `knowledge_point_list` | L29-61 | 33 | 4 | 1 | 1 | ✓ |
| `knowledge_point_delete` | L169-182 | 14 | 2 | 1 | 2 | ✓ |

**全部问题 (12)**

- 🔄 `knowledge_point_update()` L124: 复杂度: 12
- 🔄 `knowledge_point_create()` L69: 认知复杂度: 16
- 🔄 `knowledge_point_update()` L124: 认知复杂度: 14
- 🏗️ `knowledge_point_create()` L69: 中等嵌套: 3
- ❌ L39: 未处理的易出错调用
- ❌ L40: 未处理的易出错调用
- ❌ L41: 未处理的易出错调用
- ❌ L42: 未处理的易出错调用
- ❌ L43: 未处理的易出错调用
- ❌ L44: 未处理的易出错调用
- ❌ L100: 未处理的易出错调用
- ❌ L180: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.0, 最大: 12
- 认知复杂度: 平均: 10.0, 最大: 16
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 33.3 行, 最大: 48 行
- 文件长度: 147 代码量 (183 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 1 个结构问题
- 错误处理: 8/18 个错误被忽略 (44.4%)
- 注释比例: 8.2% (12/147)
- 命名规范: 无命名违规

### 49. backend\tools\api_regression_student_learning.py

**糟糕指数: 11.33**

> 行数: 285 总计, 259 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_student_path_checks` | L170-284 | 115 | 7 | 3 | 5 | ✓ |
| `_run_student_knowledge_checks` | L47-133 | 87 | 2 | 1 | 4 | ✓ |
| `_run_student_assessment_checks` | L139-164 | 26 | 2 | 1 | 4 | ✓ |
| `_run_student_learning_checks` | L14-41 | 28 | 1 | 0 | 5 | ✓ |

**全部问题 (8)**

- 🔄 `_run_student_path_checks()` L170: 认知复杂度: 13
- 📏 `_run_student_knowledge_checks()` L47: 87 代码量
- 📏 `_run_student_path_checks()` L170: 115 代码量
- 🏗️ `_run_student_path_checks()` L170: 中等嵌套: 3
- 🏷️ `_run_student_learning_checks()` L14: "_run_student_learning_checks" - snake_case
- 🏷️ `_run_student_knowledge_checks()` L47: "_run_student_knowledge_checks" - snake_case
- 🏷️ `_run_student_assessment_checks()` L139: "_run_student_assessment_checks" - snake_case
- 🏷️ `_run_student_path_checks()` L170: "_run_student_path_checks" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 7
- 认知复杂度: 平均: 5.5, 最大: 13
- 嵌套深度: 平均: 1.3, 最大: 3
- 函数长度: 平均: 64.0 行, 最大: 115 行
- 文件长度: 259 代码量 (285 总计)
- 参数数量: 平均: 4.5, 最大: 5
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 1 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 4.6% (12/259)
- 命名规范: 发现 4 个违规

### 50. backend\courses\admin_statistics_views.py

**糟糕指数: 11.30**

> 行数: 214 总计, 160 代码, 24 注释 | 函数: 8 | 类: 0

**问题**: 📋 重复问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `admin_statistics_learning` | L110-121 | 12 | 2 | 0 | 1 | ✓ |
| `admin_statistics_exams` | L129-139 | 11 | 2 | 0 | 1 | ✓ |
| `admin_statistics_overview` | L31-52 | 22 | 1 | 0 | 1 | ✓ |
| `admin_statistics_users` | L60-78 | 19 | 1 | 0 | 1 | ✓ |
| `admin_statistics_courses` | L86-102 | 17 | 1 | 0 | 1 | ✓ |
| `admin_statistics_active_users` | L147-158 | 12 | 1 | 0 | 1 | ✓ |
| `admin_statistics_report` | L166-190 | 25 | 1 | 0 | 1 | ✓ |
| `admin_statistics_export` | L198-213 | 16 | 1 | 0 | 1 | ✓ |

**全部问题 (3)**

- 📋 `admin_statistics_courses()` L86: 重复模式: admin_statistics_courses, admin_statistics_learning, admin_statistics_exams
- 📋 `admin_statistics_active_users()` L147: 重复模式: admin_statistics_active_users, admin_statistics_export
- ❌ L202: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.3, 最大: 2
- 认知复杂度: 平均: 1.3, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 16.8 行, 最大: 25 行
- 文件长度: 160 代码量 (214 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 37.5% 重复 (3/8)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 15.0% (24/160)
- 命名规范: 无命名违规

### 51. backend\tools\db_demo_preset_support.py

**糟糕指数: 11.30**

> 行数: 345 总计, 276 代码, 33 注释 | 函数: 9 | 类: 2

**问题**: ⚠️ 其他问题: 3, ❌ 错误处理问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_student1_answer_value` | L177-200 | 24 | 10 | 1 | 2 | ✓ |
| `rebuild_student1_path` | L282-344 | 63 | 4 | 2 | 7 | ✓ |
| `load_student1_demo_course_data` | L103-121 | 19 | 2 | 0 | 1 | ✓ |
| `sync_student1_initial_assessment` | L149-171 | 23 | 2 | 1 | 2 | ✓ |
| `build_student1_demo_defaults` | L40-97 | 58 | 1 | 0 | 0 | ✓ |
| `reset_course_demo_state` | L127-143 | 17 | 1 | 0 | 2 | ✓ |
| `apply_student1_static_state` | L206-225 | 20 | 1 | 0 | 3 | ✓ |
| `build_mastery_payload` | L231-240 | 10 | 1 | 0 | 3 | ✓ |
| `build_student1_feedback_defaults` | L246-276 | 31 | 1 | 0 | 5 | ✓ |

**全部问题 (9)**

- 📏 `build_student1_demo_defaults()` L40: 58 代码量
- 📏 `rebuild_student1_path()` L282: 63 代码量
- 📏 `rebuild_student1_path()` L282: 7 参数数量
- ❌ L164: 未处理的易出错调用
- ❌ L186: 未处理的易出错调用
- ❌ L188: 未处理的易出错调用
- ❌ L237: 未处理的易出错调用
- ❌ L305: 未处理的易出错调用
- ❌ L335: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 10
- 认知复杂度: 平均: 3.4, 最大: 12
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 29.4 行, 最大: 63 行
- 文件长度: 276 代码量 (345 总计)
- 参数数量: 平均: 2.8, 最大: 7
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 6/17 个错误被忽略 (35.3%)
- 注释比例: 12.0% (33/276)
- 命名规范: 无命名违规

### 52. backend\platform_ai\rag\student_point_path_mixin.py

**糟糕指数: 11.25**

> 行数: 243 总计, 185 代码, 31 注释 | 函数: 7 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `explain_knowledge_point` | L105-190 | 86 | 14 | 1 | 5 | ✓ |
| `build_path_context` | L51-67 | 17 | 5 | 0 | 4 | ✓ |
| `build_point_support_payload` | L72-100 | 29 | 4 | 1 | 3 | ✓ |
| `plan_learning_path` | L195-234 | 40 | 4 | 1 | 6 | ✓ |
| `find_course_point` | L25-34 | 10 | 3 | 1 | 4 | ✓ |
| `estimate_point_difficulty` | L39-46 | 8 | 3 | 1 | 2 | ✓ |
| `mapping_value` | L240-242 | 3 | 1 | 0 | 3 | ✓ |

**全部问题 (4)**

- 🔄 `explain_knowledge_point()` L105: 复杂度: 14
- 🔄 `explain_knowledge_point()` L105: 认知复杂度: 16
- 📏 `explain_knowledge_point()` L105: 86 代码量
- 📏 `plan_learning_path()` L195: 6 参数数量

**详情**:
- 循环复杂度: 平均: 4.9, 最大: 14
- 认知复杂度: 平均: 6.3, 最大: 16
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 27.6 行, 最大: 86 行
- 文件长度: 185 代码量 (243 总计)
- 参数数量: 平均: 3.9, 最大: 6
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 16.8% (31/185)
- 命名规范: 无命名违规

### 53. backend\platform_ai\rag\student_retrieval_mixin.py

**糟糕指数: 11.18**

> 行数: 239 总计, 181 代码, 39 注释 | 函数: 12 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 3, ❌ 错误处理问题: 7, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_rank_documents` | L181-208 | 28 | 9 | 3 | 6 | ✓ |
| `_entity_score` | L99-120 | 22 | 8 | 3 | 4 | ✓ |
| `_collect_neighbor_ids` | L141-154 | 14 | 8 | 2 | 4 | ✓ |
| `_rank_community_reports` | L213-238 | 26 | 7 | 2 | 5 | ✓ |
| `_relationship_lines` | L159-176 | 18 | 6 | 2 | 4 | ✓ |
| `_merge_sources` | L83-94 | 12 | 5 | 3 | 2 | ✓ |
| `_extract_point_ids` | L32-41 | 10 | 4 | 2 | 2 | ✓ |
| `_rank_entities` | L125-136 | 12 | 4 | 2 | 5 | ✓ |
| `_document_excerpt` | L20-27 | 8 | 3 | 1 | 3 | ✓ |
| `_source_from_document` | L46-55 | 10 | 2 | 0 | 4 | ✓ |
| `_source_from_report` | L60-71 | 12 | 2 | 0 | 3 | ✓ |
| `_source_from_graphrag_hit` | L76-78 | 3 | 1 | 0 | 3 | ✓ |

**全部问题 (23)**

- 🔄 `_entity_score()` L99: 认知复杂度: 14
- 🔄 `_rank_documents()` L181: 认知复杂度: 15
- 📏 `_rank_documents()` L181: 6 参数数量
- 🏗️ `_merge_sources()` L83: 中等嵌套: 3
- 🏗️ `_entity_score()` L99: 中等嵌套: 3
- 🏗️ `_rank_documents()` L181: 中等嵌套: 3
- ❌ L49: 未处理的易出错调用
- ❌ L51: 未处理的易出错调用
- ❌ L52: 未处理的易出错调用
- ❌ L66: 未处理的易出错调用
- ❌ L134: 未处理的易出错调用
- ❌ L228: 未处理的易出错调用
- ❌ L236: 未处理的易出错调用
- 🏷️ `_document_excerpt()` L20: "_document_excerpt" - snake_case
- 🏷️ `_extract_point_ids()` L32: "_extract_point_ids" - snake_case
- 🏷️ `_source_from_document()` L46: "_source_from_document" - snake_case
- 🏷️ `_source_from_report()` L60: "_source_from_report" - snake_case
- 🏷️ `_source_from_graphrag_hit()` L76: "_source_from_graphrag_hit" - snake_case
- 🏷️ `_merge_sources()` L83: "_merge_sources" - snake_case
- 🏷️ `_entity_score()` L99: "_entity_score" - snake_case
- 🏷️ `_rank_entities()` L125: "_rank_entities" - snake_case
- 🏷️ `_collect_neighbor_ids()` L141: "_collect_neighbor_ids" - snake_case
- 🏷️ `_relationship_lines()` L159: "_relationship_lines" - snake_case

**详情**:
- 循环复杂度: 平均: 4.9, 最大: 9
- 认知复杂度: 平均: 8.3, 最大: 15
- 嵌套深度: 平均: 1.7, 最大: 3
- 函数长度: 平均: 14.6 行, 最大: 28 行
- 文件长度: 181 代码量 (239 总计)
- 参数数量: 平均: 3.8, 最大: 6
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 3 个结构问题
- 错误处理: 7/39 个错误被忽略 (17.9%)
- 注释比例: 21.5% (39/181)
- 命名规范: 发现 12 个违规

### 54. backend\common\course_utils.py

**糟糕指数: 11.16**

> 行数: 80 总计, 54 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: 🔄 复杂度问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `resolve_course_id` | L35-76 | 42 | 12 | 3 | 1 | ✓ |
| `validate_course_exists` | L17-29 | 13 | 2 | 1 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `resolve_course_id()` L35: 复杂度: 12
- 🔄 `resolve_course_id()` L35: 认知复杂度: 18
- 🏗️ `resolve_course_id()` L35: 中等嵌套: 3
- ❌ L45: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.0, 最大: 12
- 认知复杂度: 平均: 11.0, 最大: 18
- 嵌套深度: 平均: 2.0, 最大: 3
- 函数长度: 平均: 27.5 行, 最大: 42 行
- 文件长度: 54 代码量 (80 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 1 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 11.1% (6/54)
- 命名规范: 无命名违规

### 55. backend\tools\api_regression_student_basics.py

**糟糕指数: 11.14**

> 行数: 142 总计, 131 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_student_basic_checks` | L14-141 | 128 | 2 | 1 | 4 | ✓ |

**全部问题 (2)**

- 📏 `_run_student_basic_checks()` L14: 128 代码量
- 🏷️ `_run_student_basic_checks()` L14: "_run_student_basic_checks" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 128.0 行, 最大: 128 行
- 文件长度: 131 代码量 (142 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 2.3% (3/131)
- 命名规范: 发现 1 个违规

### 56. backend\ai_services\services\path_generation_nodes.py

**糟糕指数: 11.10**

> 行数: 387 总计, 301 代码, 45 注释 | 函数: 14 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `expand_linked_point_ids` | L79-102 | 24 | 7 | 3 | 5 | ✓ |
| `fill_unlinked_point_ids` | L108-123 | 16 | 4 | 2 | 3 | ✓ |
| `attach_resources_to_created_nodes` | L376-386 | 11 | 4 | 2 | 2 | ✓ |
| `build_linked_pending_batch` | L30-55 | 26 | 3 | 1 | 5 | ✓ |
| `build_pending_nodes` | L166-206 | 41 | 3 | 1 | 8 | ✓ |
| `build_study_title` | L241-245 | 5 | 3 | 1 | 3 | ✓ |
| `build_study_suggestion` | L251-255 | 5 | 3 | 1 | 3 | ✓ |
| `build_completed_nodes` | L129-160 | 32 | 2 | 1 | 4 | ✓ |
| `build_test_node` | L261-285 | 25 | 2 | 1 | 3 | ✓ |
| `build_test_title` | L291-295 | 5 | 2 | 1 | 1 | ✓ |
| `assemble_generation_plan` | L345-370 | 26 | 2 | 1 | 7 | ✓ |
| `order_pending_points` | L61-73 | 13 | 1 | 0 | 2 | ✓ |
| `build_study_node` | L212-235 | 24 | 1 | 0 | 5 | ✓ |
| `build_generation_plan` | L301-339 | 39 | 1 | 0 | 8 | ✓ |

**全部问题 (6)**

- 🔄 `expand_linked_point_ids()` L79: 认知复杂度: 13
- 📏 `build_pending_nodes()` L166: 8 参数数量
- 📏 `build_generation_plan()` L301: 8 参数数量
- 📏 `assemble_generation_plan()` L345: 7 参数数量
- 🏗️ `expand_linked_point_ids()` L79: 中等嵌套: 3
- ❌ L69: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.7, 最大: 7
- 认知复杂度: 平均: 4.9, 最大: 13
- 嵌套深度: 平均: 1.1, 最大: 3
- 函数长度: 平均: 20.9 行, 最大: 41 行
- 文件长度: 301 代码量 (387 总计)
- 参数数量: 平均: 4.2, 最大: 8
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 1 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 15.0% (45/301)
- 命名规范: 无命名违规

### 57. backend\tools\api_regression_student_exam_ai.py

**糟糕指数: 11.04**

> 行数: 247 总计, 231 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: ⚠️ 其他问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_student_exam_checks` | L14-134 | 121 | 5 | 1 | 4 | ✓ |
| `_run_student_ai_kt_checks` | L140-246 | 107 | 3 | 1 | 5 | ✓ |

**全部问题 (4)**

- 📏 `_run_student_exam_checks()` L14: 121 代码量
- 📏 `_run_student_ai_kt_checks()` L140: 107 代码量
- 🏷️ `_run_student_exam_checks()` L14: "_run_student_exam_checks" - snake_case
- 🏷️ `_run_student_ai_kt_checks()` L140: "_run_student_ai_kt_checks" - snake_case

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 5
- 认知复杂度: 平均: 6.0, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 114.0 行, 最大: 121 行
- 文件长度: 231 代码量 (247 总计)
- 参数数量: 平均: 4.5, 最大: 5
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 2.6% (6/231)
- 命名规范: 发现 2 个违规

### 58. backend\ai_services\services\mefkt_runtime_features.py

**糟糕指数: 10.94**

> 行数: 287 总计, 226 代码, 35 注释 | 函数: 11 | 类: 1

**问题**: ⚠️ 其他问题: 3, 📋 重复问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `collect_question_feature_entry` | L37-71 | 35 | 3 | 0 | 4 | ✓ |
| `build_question_raw_values` | L134-154 | 21 | 3 | 0 | 7 | ✓ |
| `build_chapter_norm_map` | L20-31 | 12 | 2 | 0 | 2 | ✓ |
| `prepare_question_features` | L192-221 | 30 | 2 | 1 | 4 | ✓ |
| `add_question` | L247-272 | 26 | 2 | 1 | 4 | ✓ |
| `collect_resource_ids` | L77-86 | 10 | 1 | 0 | 2 | ✓ |
| `collect_relation_counts` | L92-100 | 9 | 1 | 0 | 2 | ✓ |
| `build_question_meta` | L106-128 | 23 | 1 | 0 | 7 | ✓ |
| `normalize_question_feature_scales` | L160-186 | 27 | 1 | 0 | 10 | ✓ |
| `__init__` | L230-242 | 13 | 1 | 0 | 3 | ✗ |
| `to_preparation` | L277-286 | 10 | 1 | 0 | 2 | ✓ |

**全部问题 (5)**

- 📏 `build_question_meta()` L106: 7 参数数量
- 📏 `build_question_raw_values()` L134: 7 参数数量
- 📏 `normalize_question_feature_scales()` L160: 10 参数数量
- 📋 `build_chapter_norm_map()` L20: 重复模式: build_chapter_norm_map, collect_relation_counts
- ❌ L85: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 3
- 认知复杂度: 平均: 2.0, 最大: 4
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 19.6 行, 最大: 35 行
- 文件长度: 226 代码量 (287 总计)
- 参数数量: 平均: 4.3, 最大: 10
- 代码重复: 9.1% 重复 (1/11)
- 结构分析: 0 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 15.5% (35/226)
- 命名规范: 发现 1 个违规

### 59. backend\users\services.py

**糟糕指数: 10.69**

> 行数: 428 总计, 317 代码, 41 注释 | 函数: 13 | 类: 1

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_habit_preferences` | L101-127 | 27 | 12 | 1 | 1 | ✓ |
| `update_mastery_from_answers` | L236-303 | 68 | 9 | 3 | 3 | ✓ |
| `get_knowledge_mastery` | L43-71 | 29 | 8 | 1 | 2 | ✓ |
| `get_profile_summary` | L132-162 | 31 | 7 | 1 | 2 | ✓ |
| `_build_cached_profile_result` | L188-208 | 21 | 6 | 1 | 2 | ✓ |
| `_derive_strength_points` | L168-183 | 16 | 5 | 1 | 1 | ✓ |
| `check_assessment_status` | L342-391 | 50 | 5 | 2 | 2 | ✓ |
| `get_ability_scores` | L76-96 | 21 | 4 | 2 | 2 | ✓ |
| `__init__` | L31-38 | 8 | 1 | 0 | 2 | ✓ |
| `get_full_profile` | L213-231 | 19 | 1 | 0 | 2 | ✓ |
| `get_profile_history` | L308-337 | 30 | 1 | 0 | 3 | ✓ |
| `generate_profile_for_course` | L396-411 | 16 | 1 | 0 | 3 | ✓ |
| `get_learner_profile_service` | L417-427 | 11 | 1 | 0 | 1 | ✓ |

**全部问题 (11)**

- 🔄 `get_habit_preferences()` L101: 复杂度: 12
- 🔄 `get_habit_preferences()` L101: 认知复杂度: 14
- 🔄 `update_mastery_from_answers()` L236: 认知复杂度: 15
- 📏 `update_mastery_from_answers()` L236: 68 代码量
- 🏗️ `update_mastery_from_answers()` L236: 中等嵌套: 3
- ❌ L171: 未处理的易出错调用
- ❌ L179: 未处理的易出错调用
- ❌ L290: 未处理的易出错调用
- 🏷️ `__init__()` L31: "__init__" - snake_case
- 🏷️ `_derive_strength_points()` L168: "_derive_strength_points" - snake_case
- 🏷️ `_build_cached_profile_result()` L188: "_build_cached_profile_result" - snake_case

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 12
- 认知复杂度: 平均: 6.5, 最大: 15
- 嵌套深度: 平均: 0.9, 最大: 3
- 函数长度: 平均: 26.7 行, 最大: 68 行
- 文件长度: 317 代码量 (428 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 1 个结构问题
- 错误处理: 3/6 个错误被忽略 (50.0%)
- 注释比例: 12.9% (41/317)
- 命名规范: 发现 3 个违规

### 60. backend\courses\teacher_student_views.py

**糟糕指数: 10.50**

> 行数: 105 总计, 82 代码, 9 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_class_student_profiles` | L61-104 | 44 | 13 | 2 | 2 | ✓ |
| `class_students` | L18-31 | 14 | 5 | 1 | 2 | ✓ |
| `remove_student_from_class` | L39-53 | 15 | 5 | 1 | 3 | ✓ |

**全部问题 (4)**

- 🔄 `get_class_student_profiles()` L61: 复杂度: 13
- 🔄 `get_class_student_profiles()` L61: 认知复杂度: 17
- ❌ L52: 未处理的易出错调用
- ❌ L102: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.7, 最大: 13
- 认知复杂度: 平均: 10.3, 最大: 17
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 24.3 行, 最大: 44 行
- 文件长度: 82 代码量 (105 总计)
- 参数数量: 平均: 2.3, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 2/8 个错误被忽略 (25.0%)
- 注释比例: 11.0% (9/82)
- 命名规范: 无命名违规

### 61. backend\users\admin_profile_views.py

**糟糕指数: 10.50**

> 行数: 121 总计, 99 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `admin_get_all_student_profiles` | L22-71 | 50 | 11 | 2 | 1 | ✓ |
| `admin_student_profile_detail` | L79-120 | 42 | 8 | 1 | 2 | ✓ |

**全部问题 (3)**

- 🔄 `admin_get_all_student_profiles()` L22: 复杂度: 11
- 🔄 `admin_get_all_student_profiles()` L22: 认知复杂度: 15
- ❌ L68: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 9.5, 最大: 11
- 认知复杂度: 平均: 12.5, 最大: 15
- 嵌套深度: 平均: 1.5, 最大: 2
- 函数长度: 平均: 46.0 行, 最大: 50 行
- 文件长度: 99 代码量 (121 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 6.1% (6/99)
- 命名规范: 无命名违规

### 62. backend\platform_ai\rag\runtime_models.py

**糟糕指数: 10.48**

> 行数: 452 总计, 316 代码, 71 注释 | 函数: 20 | 类: 6

**问题**: 🔄 复杂度问题: 3, ⚠️ 其他问题: 3, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `run` | L397-451 | 55 | 9 | 2 | 5 | ✓ |
| `_message_history_text` | L186-207 | 22 | 8 | 2 | 1 | ✓ |
| `_vector_point_ids` | L255-271 | 17 | 6 | 4 | 1 | ✓ |
| `embed_query` | L302-325 | 24 | 6 | 1 | 2 | ✓ |
| `_coerce_int_list` | L159-172 | 14 | 5 | 2 | 1 | ✓ |
| `_dedupe_strings` | L231-241 | 11 | 4 | 2 | 1 | ✓ |
| `_resolve_delegate` | L348-360 | 13 | 4 | 1 | 1 | ✓ |
| `embed_query` | L365-375 | 11 | 3 | 1 | 2 | ✓ |
| `_coerce_string` | L140-142 | 3 | 2 | 0 | 1 | ✓ |
| `_coerce_int` | L148-153 | 6 | 2 | 1 | 2 | ✓ |
| `_qdrant_point_id` | L277-282 | 6 | 2 | 1 | 1 | ✓ |
| `as_dict` | L56-66 | 11 | 1 | 0 | 1 | ✓ |
| `as_source` | L92-103 | 12 | 1 | 0 | 2 | ✓ |
| `as_dict` | L124-134 | 11 | 1 | 0 | 1 | ✓ |
| `_escape_cypher_string` | L178-180 | 3 | 1 | 0 | 1 | ✓ |
| `_query_tool_parameters` | L213-225 | 13 | 1 | 0 | 1 | ✓ |
| `_compact_excerpt` | L246-249 | 4 | 1 | 0 | 2 | ✓ |
| `__init__` | L295-297 | 3 | 1 | 0 | 2 | ✗ |
| `__init__` | L338-343 | 6 | 1 | 0 | 3 | ✗ |
| `__init__` | L390-392 | 3 | 1 | 0 | 2 | ✗ |

**全部问题 (18)**

- 🔄 `_vector_point_ids()` L255: 认知复杂度: 14
- 🔄 `run()` L397: 认知复杂度: 13
- 🔄 `_vector_point_ids()` L255: 嵌套深度: 4
- 📏 `run()` L397: 55 代码量
- 🏗️ `_vector_point_ids()` L255: 中等嵌套: 4
- ❌ L260: 未处理的易出错调用
- ❌ L261: 未处理的易出错调用
- ❌ L425: 未处理的易出错调用
- 🏷️ `_coerce_string()` L140: "_coerce_string" - snake_case
- 🏷️ `_coerce_int()` L148: "_coerce_int" - snake_case
- 🏷️ `_coerce_int_list()` L159: "_coerce_int_list" - snake_case
- 🏷️ `_escape_cypher_string()` L178: "_escape_cypher_string" - snake_case
- 🏷️ `_message_history_text()` L186: "_message_history_text" - snake_case
- 🏷️ `_query_tool_parameters()` L213: "_query_tool_parameters" - snake_case
- 🏷️ `_dedupe_strings()` L231: "_dedupe_strings" - snake_case
- 🏷️ `_compact_excerpt()` L246: "_compact_excerpt" - snake_case
- 🏷️ `_vector_point_ids()` L255: "_vector_point_ids" - snake_case
- 🏷️ `_qdrant_point_id()` L277: "_qdrant_point_id" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 9
- 认知复杂度: 平均: 4.7, 最大: 14
- 嵌套深度: 平均: 0.8, 最大: 4
- 函数长度: 平均: 12.4 行, 最大: 55 行
- 文件长度: 316 代码量 (452 总计)
- 参数数量: 平均: 1.6, 最大: 5
- 代码重复: 0.0% 重复 (0/20)
- 结构分析: 1 个结构问题
- 错误处理: 3/15 个错误被忽略 (20.0%)
- 注释比例: 22.5% (71/316)
- 命名规范: 发现 14 个违规

### 63. backend\learning\serializers.py

**糟糕指数: 10.44**

> 行数: 156 总计, 98 代码, 39 注释 | 函数: 6 | 类: 4

**问题**: 📋 重复问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_progress` | L108-127 | 20 | 6 | 2 | 2 | ✓ |
| `get_mastery_before` | L132-141 | 10 | 6 | 2 | 2 | ✓ |
| `get_mastery_after` | L146-155 | 10 | 6 | 2 | 2 | ✓ |
| `get_resources` | L82-90 | 9 | 3 | 0 | 1 | ✗ |
| `get_tasks_count` | L29-30 | 2 | 2 | 0 | 1 | ✗ |
| `get_exercises` | L96-103 | 8 | 2 | 1 | 1 | ✗ |

**全部问题 (1)**

- 📋 `get_progress()` L108: 重复模式: get_progress, get_mastery_before, get_mastery_after

**详情**:
- 循环复杂度: 平均: 4.2, 最大: 6
- 认知复杂度: 平均: 6.5, 最大: 10
- 嵌套深度: 平均: 1.2, 最大: 2
- 函数长度: 平均: 9.8 行, 最大: 20 行
- 文件长度: 98 代码量 (156 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 33.3% 重复 (2/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 39.8% (39/98)
- 命名规范: 无命名违规

### 64. backend\platform_ai\rag\corpus_builder.py

**糟糕指数: 10.40**

> 行数: 410 总计, 316 代码, 54 注释 | 函数: 17 | 类: 1

**问题**: ⚠️ 其他问题: 2, 📋 重复问题: 1, 🏗️ 结构问题: 3, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `point_summary` | L86-100 | 15 | 7 | 0 | 2 | ✓ |
| `populate_resources` | L262-308 | 47 | 5 | 3 | 1 | ✓ |
| `populate_questions` | L314-361 | 48 | 5 | 3 | 1 | ✓ |
| `link_chapter_members` | L367-381 | 15 | 5 | 3 | 1 | ✓ |
| `populate_knowledge_relations` | L238-256 | 19 | 4 | 2 | 1 | ✓ |
| `remember_chapter_member` | L34-39 | 6 | 3 | 0 | 3 | ✓ |
| `resource_summary` | L106-116 | 11 | 3 | 0 | 3 | ✓ |
| `question_summary` | L122-132 | 11 | 3 | 0 | 2 | ✓ |
| `populate_points` | L168-201 | 34 | 3 | 1 | 2 | ✓ |
| `populate_chapters` | L207-232 | 26 | 2 | 1 | 1 | ✓ |
| `add_entity` | L44-48 | 5 | 1 | 0 | 3 | ✓ |
| `add_relationship` | L53-72 | 20 | 1 | 0 | 6 | ✓ |
| `join_nonempty` | L78-80 | 3 | 1 | 0 | 1 | ✓ |
| `published_points` | L138-142 | 5 | 1 | 0 | 1 | ✓ |
| `visible_resources` | L148-150 | 3 | 1 | 0 | 1 | ✓ |
| `visible_questions` | L156-162 | 7 | 1 | 0 | 1 | ✓ |
| `build_course_graph_payload` | L386-406 | 21 | 1 | 0 | 1 | ✓ |

**全部问题 (6)**

- 📏 `add_relationship()` L53: 6 参数数量
- 📋 `populate_resources()` L262: 重复模式: populate_resources, populate_questions
- 🏗️ `populate_resources()` L262: 中等嵌套: 3
- 🏗️ `populate_questions()` L314: 中等嵌套: 3
- 🏗️ `link_chapter_members()` L367: 中等嵌套: 3
- ❌ L211: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 7
- 认知复杂度: 平均: 4.3, 最大: 11
- 嵌套深度: 平均: 0.8, 最大: 3
- 函数长度: 平均: 17.4 行, 最大: 48 行
- 文件长度: 316 代码量 (410 总计)
- 参数数量: 平均: 1.8, 最大: 6
- 代码重复: 5.9% 重复 (1/17)
- 结构分析: 3 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 17.1% (54/316)
- 命名规范: 无命名违规

### 65. backend\knowledge\resource_views.py

**糟糕指数: 10.40**

> 行数: 129 总计, 105 代码, 9 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_student_resources` | L16-76 | 61 | 15 | 1 | 1 | ✓ |
| `knowledge_point_resources` | L84-102 | 19 | 4 | 1 | 2 | ✓ |
| `knowledge_search` | L110-128 | 19 | 4 | 1 | 1 | ✓ |

**全部问题 (3)**

- 🔄 `get_student_resources()` L16: 复杂度: 15
- 🔄 `get_student_resources()` L16: 认知复杂度: 17
- 📏 `get_student_resources()` L16: 61 代码量

**详情**:
- 循环复杂度: 平均: 7.7, 最大: 15
- 认知复杂度: 平均: 9.7, 最大: 17
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 33.0 行, 最大: 61 行
- 文件长度: 105 代码量 (129 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/9 个错误被忽略 (0.0%)
- 注释比例: 8.6% (9/105)
- 命名规范: 无命名违规

### 66. backend\courses\teacher_invitation_views.py

**糟糕指数: 10.34**

> 行数: 108 总计, 86 代码, 9 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_class_invitation` | L24-71 | 48 | 14 | 2 | 1 | ✓ |
| `list_class_invitations` | L79-89 | 11 | 5 | 1 | 2 | ✓ |
| `delete_class_invitation` | L97-107 | 11 | 4 | 1 | 2 | ✓ |

**全部问题 (3)**

- 🔄 `generate_class_invitation()` L24: 复杂度: 14
- 🔄 `generate_class_invitation()` L24: 认知复杂度: 18
- ❌ L106: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.7, 最大: 14
- 认知复杂度: 平均: 10.3, 最大: 18
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 23.3 行, 最大: 48 行
- 文件长度: 86 代码量 (108 总计)
- 参数数量: 平均: 1.7, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 1/8 个错误被忽略 (12.5%)
- 注释比例: 10.5% (9/86)
- 命名规范: 无命名违规

### 67. backend\learning\dashboard_views.py

**糟糕指数: 10.33**

> 行数: 111 总计, 85 代码, 9 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `student_dashboard` | L20-110 | 91 | 10 | 1 | 1 | ✓ |

**全部问题 (1)**

- 📏 `student_dashboard()` L20: 91 代码量

**详情**:
- 循环复杂度: 平均: 10.0, 最大: 10
- 认知复杂度: 平均: 12.0, 最大: 12
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 91.0 行, 最大: 91 行
- 文件长度: 85 代码量 (111 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 10.6% (9/85)
- 命名规范: 无命名违规

### 68. backend\users\test_models.py

**糟糕指数: 10.30**

> 行数: 214 总计, 143 代码, 48 注释 | 函数: 13 | 类: 3

**问题**: 📋 重复问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_create_student` | L20-31 | 12 | 1 | 0 | 1 | ✓ |
| `test_create_teacher` | L36-46 | 11 | 1 | 0 | 1 | ✓ |
| `test_create_admin` | L51-60 | 10 | 1 | 0 | 1 | ✓ |
| `setUp` | L72-79 | 8 | 1 | 0 | 1 | ✓ |
| `test_generate_code` | L84-88 | 5 | 1 | 0 | 1 | ✓ |
| `test_create_activation_code` | L93-101 | 9 | 1 | 0 | 1 | ✓ |
| `test_use_activation_code` | L106-122 | 17 | 1 | 0 | 1 | ✓ |
| `test_cannot_reuse_activation_code` | L127-135 | 9 | 1 | 0 | 1 | ✓ |
| `setUp` | L147-162 | 16 | 1 | 0 | 1 | ✓ |
| `test_generate_code` | L167-171 | 5 | 1 | 0 | 1 | ✓ |
| `test_create_invitation` | L176-184 | 9 | 1 | 0 | 1 | ✓ |
| `test_use_invitation` | L189-197 | 9 | 1 | 0 | 1 | ✓ |
| `test_invitation_max_uses` | L202-213 | 12 | 1 | 0 | 1 | ✓ |

**全部问题 (4)**

- 📋 `test_create_student()` L20: 重复模式: test_create_student, test_create_teacher, test_create_admin, setUp, test_cannot_reuse_activation_code, test_invitation_max_uses
- 📋 `test_create_activation_code()` L93: 重复模式: test_create_activation_code, test_create_invitation, test_use_invitation
- 🏷️ `setUp()` L72: "setUp" - snake_case
- 🏷️ `setUp()` L147: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 10.2 行, 最大: 17 行
- 文件长度: 143 代码量 (214 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 53.8% 重复 (7/13)
- 结构分析: 0 个结构问题
- 错误处理: 0/8 个错误被忽略 (0.0%)
- 注释比例: 33.6% (48/143)
- 命名规范: 发现 2 个违规

### 69. backend\common\question_options.py

**糟糕指数: 10.30**

> 行数: 368 总计, 245 代码, 60 注释 | 函数: 20 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, 📋 重复问题: 2, ❌ 错误处理问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_answer_display` | L274-304 | 31 | 10 | 2 | 3 | ✓ |
| `format_option_display` | L257-268 | 12 | 7 | 0 | 1 | ✓ |
| `serialize_answer_payload` | L335-355 | 21 | 7 | 2 | 2 | ✓ |
| `normalize_dict_option` | L146-156 | 11 | 6 | 0 | 3 | ✓ |
| `clean_display_text` | L17-34 | 18 | 5 | 2 | 1 | ✓ |
| `true_false_alias_tokens` | L81-90 | 10 | 4 | 1 | 2 | ✓ |
| `normalize_question_options` | L96-114 | 19 | 4 | 2 | 2 | ✓ |
| `joined_answer_values` | L322-329 | 8 | 4 | 2 | 1 | ✓ |
| `answer_tokens` | L40-54 | 15 | 3 | 2 | 2 | ✓ |
| `answer_values` | L60-67 | 8 | 3 | 1 | 1 | ✓ |
| `default_true_false_options` | L120-127 | 8 | 3 | 1 | 2 | ✓ |
| `normalize_single_option` | L133-140 | 8 | 3 | 1 | 2 | ✓ |
| `normalize_text_option` | L162-167 | 6 | 3 | 0 | 3 | ✓ |
| `first_truthy_option_field` | L173-179 | 7 | 3 | 2 | 2 | ✓ |
| `option_tokens` | L198-210 | 13 | 3 | 2 | 1 | ✓ |
| `display_token_variants` | L73-75 | 3 | 1 | 0 | 1 | ✓ |
| `option_payload` | L185-192 | 8 | 1 | 0 | 3 | ✓ |
| `option_token_values` | L216-223 | 8 | 1 | 0 | 1 | ✓ |
| `decorate_question_options` | L229-251 | 23 | 1 | 0 | 4 | ✓ |
| `matched_option_displays` | L310-316 | 7 | 1 | 0 | 2 | ✓ |

**全部问题 (8)**

- 🔄 `build_answer_display()` L274: 认知复杂度: 14
- 📋 `answer_values()` L60: 重复模式: answer_values, normalize_single_option
- 📋 `option_tokens()` L198: 重复模式: option_tokens, joined_answer_values
- ❌ L219: 未处理的易出错调用
- ❌ L220: 未处理的易出错调用
- ❌ L221: 未处理的易出错调用
- ❌ L222: 未处理的易出错调用
- ❌ L266: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.6, 最大: 10
- 认知复杂度: 平均: 5.7, 最大: 14
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 12.2 行, 最大: 31 行
- 文件长度: 245 代码量 (368 总计)
- 参数数量: 平均: 1.9, 最大: 4
- 代码重复: 10.0% 重复 (2/20)
- 结构分析: 0 个结构问题
- 错误处理: 5/8 个错误被忽略 (62.5%)
- 注释比例: 24.5% (60/245)
- 命名规范: 无命名违规

### 70. backend\ai_services\services\scoring_service.py

**糟糕指数: 10.19**

> 行数: 302 总计, 216 代码, 39 注释 | 函数: 7 | 类: 1

**问题**: 🔄 复杂度问题: 4, ⚠️ 其他问题: 3, 🏗️ 结构问题: 2, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `score_objective_question` | L30-86 | 57 | 12 | 2 | 4 | ✓ |
| `score_exam` | L129-201 | 73 | 8 | 3 | 2 | ✓ |
| `calculate_ability_score` | L252-301 | 50 | 8 | 3 | 2 | ✓ |
| `_normalize_list` | L102-110 | 9 | 4 | 1 | 1 | ✓ |
| `update_mastery` | L207-246 | 40 | 4 | 2 | 3 | ✓ |
| `_to_bool` | L116-123 | 8 | 3 | 1 | 1 | ✓ |
| `_normalize_answer` | L92-96 | 5 | 2 | 1 | 1 | ✓ |

**全部问题 (11)**

- 🔄 `score_objective_question()` L30: 复杂度: 12
- 🔄 `score_objective_question()` L30: 认知复杂度: 16
- 🔄 `score_exam()` L129: 认知复杂度: 14
- 🔄 `calculate_ability_score()` L252: 认知复杂度: 14
- 📏 `score_objective_question()` L30: 57 代码量
- 📏 `score_exam()` L129: 73 代码量
- 🏗️ `score_exam()` L129: 中等嵌套: 3
- 🏗️ `calculate_ability_score()` L252: 中等嵌套: 3
- 🏷️ `_normalize_answer()` L92: "_normalize_answer" - snake_case
- 🏷️ `_normalize_list()` L102: "_normalize_list" - snake_case
- 🏷️ `_to_bool()` L116: "_to_bool" - snake_case

**详情**:
- 循环复杂度: 平均: 5.9, 最大: 12
- 认知复杂度: 平均: 9.6, 最大: 16
- 嵌套深度: 平均: 1.9, 最大: 3
- 函数长度: 平均: 34.6 行, 最大: 73 行
- 文件长度: 216 代码量 (302 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 2 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 18.1% (39/216)
- 命名规范: 发现 3 个违规

### 71. backend\tools\common.py

**糟糕指数: 10.13**

> 行数: 240 总计, 168 代码, 34 注释 | 函数: 9 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_course_asset_bundle` | L133-224 | 92 | 14 | 3 | 2 | ✓ |
| `clean_nan` | L102-111 | 10 | 5 | 1 | 1 | ✓ |
| `safe_float` | L117-127 | 11 | 5 | 2 | 2 | ✓ |
| `list_courses` | L230-239 | 10 | 5 | 1 | 1 | ✓ |
| `split_multi_values` | L49-52 | 4 | 3 | 0 | 1 | ✓ |
| `find_first_file` | L58-64 | 7 | 3 | 2 | 2 | ✓ |
| `load_json` | L79-85 | 7 | 3 | 1 | 1 | ✓ |
| `resolve_path` | L70-73 | 4 | 2 | 0 | 1 | ✓ |
| `get_course` | L91-96 | 6 | 2 | 1 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `build_course_asset_bundle()` L133: 复杂度: 14
- 🔄 `build_course_asset_bundle()` L133: 认知复杂度: 20
- 📏 `build_course_asset_bundle()` L133: 92 代码量
- 🏗️ `build_course_asset_bundle()` L133: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 14
- 认知复杂度: 平均: 7.1, 最大: 20
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 16.8 行, 最大: 92 行
- 文件长度: 168 代码量 (240 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 20.2% (34/168)
- 命名规范: 无命名违规

### 72. backend\assessments\knowledge_generation.py

**糟糕指数: 10.13**

> 行数: 105 总计, 86 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `async_generate_after_assessment` | L28-104 | 77 | 8 | 2 | 4 | ✓ |

**全部问题 (1)**

- 📏 `async_generate_after_assessment()` L28: 77 代码量

**详情**:
- 循环复杂度: 平均: 8.0, 最大: 8
- 认知复杂度: 平均: 12.0, 最大: 12
- 嵌套深度: 平均: 2.0, 最大: 2
- 函数长度: 平均: 77.0 行, 最大: 77 行
- 文件长度: 86 代码量 (105 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 3.5% (3/86)
- 命名规范: 无命名违规

### 73. backend\common\defense_demo_stage.py

**糟糕指数: 10.04**

> 行数: 411 总计, 336 代码, 42 注释 | 函数: 14 | 类: 0

**问题**: ⚠️ 其他问题: 3, ❌ 错误处理问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_stage_score_map` | L102-116 | 15 | 4 | 0 | 2 | ✓ |
| `resolve_pass_score` | L143-153 | 11 | 3 | 1 | 2 | ✓ |
| `build_mastery_changes` | L196-226 | 31 | 3 | 2 | 4 | ✓ |
| `resolve_mastery_before` | L232-255 | 24 | 3 | 1 | 4 | ✓ |
| `upsert_stage_submission` | L159-190 | 32 | 2 | 1 | 6 | ✓ |
| `ensure_warmup_stage_submission_and_feedback` | L366-410 | 45 | 2 | 1 | 4 | ✓ |
| `build_stage_feedback_payload` | L25-52 | 28 | 1 | 0 | 1 | ✓ |
| `load_stage_exam_questions` | L58-69 | 12 | 1 | 0 | 1 | ✓ |
| `collect_exam_questions` | L75-81 | 7 | 1 | 0 | 1 | ✓ |
| `build_submission_answers` | L87-96 | 10 | 1 | 0 | 1 | ✓ |
| `grade_stage_exam` | L122-137 | 16 | 1 | 0 | 4 | ✓ |
| `build_mastery_change_item` | L261-279 | 19 | 1 | 0 | 3 | ✓ |
| `upsert_stage_feedback_report` | L285-327 | 43 | 1 | 0 | 8 | ✓ |
| `build_feedback_overview` | L333-360 | 28 | 1 | 0 | 5 | ✓ |

**全部问题 (8)**

- 📏 `upsert_stage_submission()` L159: 6 参数数量
- 📏 `upsert_stage_feedback_report()` L285: 8 参数数量
- ❌ L322: 未处理的易出错调用
- ❌ L323: 未处理的易出错调用
- ❌ L324: 未处理的易出错调用
- ❌ L325: 未处理的易出错调用
- ❌ L357: 未处理的易出错调用
- ❌ L358: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.8, 最大: 4
- 认知复杂度: 平均: 2.6, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 22.9 行, 最大: 45 行
- 文件长度: 336 代码量 (411 总计)
- 参数数量: 平均: 3.3, 最大: 8
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 6/9 个错误被忽略 (66.7%)
- 注释比例: 12.5% (42/336)
- 命名规范: 无命名违规

### 74. frontend\src\views\student\useLearningPath.js

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

### 75. backend\ai_services\services\kt_prediction_modes.py

**糟糕指数: 9.79**

> 行数: 329 总计, 265 代码, 27 注释 | 函数: 8 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `predict_mastery` | L28-75 | 48 | 9 | 2 | 5 | ✓ |
| `_ensemble_predict` | L116-168 | 53 | 6 | 2 | 5 | ✓ |
| `_fuse_predictions` | L224-249 | 26 | 6 | 3 | 2 | ✓ |
| `_fusion_predict` | L173-219 | 47 | 4 | 1 | 5 | ✓ |
| `batch_predict` | L275-294 | 20 | 4 | 1 | 2 | ✓ |
| `_single_model_predict` | L80-111 | 32 | 3 | 1 | 5 | ✓ |
| `get_learning_recommendations` | L299-328 | 30 | 3 | 1 | 5 | ✓ |
| `_builtin_prediction` | L254-270 | 17 | 1 | 0 | 5 | ✓ |

**全部问题 (11)**

- 🔄 `predict_mastery()` L28: 认知复杂度: 13
- 📏 `_ensemble_predict()` L116: 53 代码量
- 🏗️ `_fuse_predictions()` L224: 中等嵌套: 3
- ❌ L48: 未处理的易出错调用
- ❌ L139: 未处理的易出错调用
- ❌ L196: 未处理的易出错调用
- 🏷️ `_single_model_predict()` L80: "_single_model_predict" - snake_case
- 🏷️ `_ensemble_predict()` L116: "_ensemble_predict" - snake_case
- 🏷️ `_fusion_predict()` L173: "_fusion_predict" - snake_case
- 🏷️ `_fuse_predictions()` L224: "_fuse_predictions" - snake_case
- 🏷️ `_builtin_prediction()` L254: "_builtin_prediction" - snake_case

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 9
- 认知复杂度: 平均: 7.3, 最大: 13
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 34.1 行, 最大: 53 行
- 文件长度: 265 代码量 (329 总计)
- 参数数量: 平均: 4.3, 最大: 5
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 3/8 个错误被忽略 (37.5%)
- 注释比例: 10.2% (27/265)
- 命名规范: 发现 5 个违规

### 76. backend\learning\path_views.py

**糟糕指数: 9.75**

> 行数: 143 总计, 110 代码, 10 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_learning_path` | L25-89 | 65 | 14 | 2 | 1 | ✓ |
| `adjust_learning_path` | L97-130 | 34 | 5 | 1 | 1 | ✓ |
| `generate_initial_path` | L136-142 | 7 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- 🔄 `get_learning_path()` L25: 复杂度: 14
- 🔄 `get_learning_path()` L25: 认知复杂度: 18
- 📏 `get_learning_path()` L25: 65 代码量

**详情**:
- 循环复杂度: 平均: 6.7, 最大: 14
- 认知复杂度: 平均: 8.7, 最大: 18
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 35.3 行, 最大: 65 行
- 文件长度: 110 代码量 (143 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 9.1% (10/110)
- 命名规范: 无命名违规

### 77. backend\tools\api_regression_teacher.py

**糟糕指数: 9.74**

> 行数: 388 总计, 299 代码, 45 注释 | 函数: 14 | 类: 1

**问题**: ⚠️ 其他问题: 2, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_response_id` | L373-387 | 15 | 7 | 2 | 3 | ✓ |
| `_create_question` | L150-185 | 36 | 3 | 1 | 2 | ✓ |
| `_create_exam` | L236-273 | 38 | 3 | 1 | 1 | ✓ |
| `_run_teacher_list_checks` | L306-316 | 11 | 3 | 1 | 1 | ✓ |
| `_run_teacher_regression` | L40-72 | 33 | 2 | 1 | 6 | ✓ |
| `_run_teacher_mutation_checks` | L87-94 | 8 | 2 | 1 | 1 | ✓ |
| `_create_course` | L100-124 | 25 | 2 | 1 | 1 | ✓ |
| `_create_class` | L191-214 | 24 | 2 | 1 | 1 | ✓ |
| `_publish_and_unpublish_exam` | L279-300 | 22 | 2 | 1 | 2 | ✓ |
| `_run_teacher_read_checks` | L78-81 | 4 | 1 | 0 | 1 | ✓ |
| `_create_knowledge_point` | L130-144 | 15 | 1 | 0 | 1 | ✓ |
| `_create_invitation` | L220-230 | 11 | 1 | 0 | 1 | ✓ |
| `record_check_get` | L322-337 | 16 | 1 | 0 | 4 | ✓ |
| `record_check_request` | L343-367 | 25 | 1 | 0 | 8 | ✓ |

**全部问题 (12)**

- 📏 `_run_teacher_regression()` L40: 6 参数数量
- 📏 `record_check_request()` L343: 8 参数数量
- 🏷️ `_run_teacher_regression()` L40: "_run_teacher_regression" - snake_case
- 🏷️ `_run_teacher_read_checks()` L78: "_run_teacher_read_checks" - snake_case
- 🏷️ `_run_teacher_mutation_checks()` L87: "_run_teacher_mutation_checks" - snake_case
- 🏷️ `_create_course()` L100: "_create_course" - snake_case
- 🏷️ `_create_knowledge_point()` L130: "_create_knowledge_point" - snake_case
- 🏷️ `_create_question()` L150: "_create_question" - snake_case
- 🏷️ `_create_class()` L191: "_create_class" - snake_case
- 🏷️ `_create_invitation()` L220: "_create_invitation" - snake_case
- 🏷️ `_create_exam()` L236: "_create_exam" - snake_case
- 🏷️ `_publish_and_unpublish_exam()` L279: "_publish_and_unpublish_exam" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 7
- 认知复杂度: 平均: 3.6, 最大: 11
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 20.2 行, 最大: 38 行
- 文件长度: 299 代码量 (388 总计)
- 参数数量: 平均: 2.4, 最大: 8
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 15.1% (45/299)
- 命名规范: 发现 12 个违规

### 78. backend\tools\activation.py

**糟糕指数: 9.70**

> 行数: 43 总计, 31 代码, 4 注释 | 函数: 1 | 类: 0

**问题**: 🔄 复杂度问题: 2, 🏗️ 结构问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_activation_codes` | L14-42 | 29 | 8 | 4 | 3 | ✓ |

**全部问题 (3)**

- 🔄 `generate_activation_codes()` L14: 认知复杂度: 16
- 🔄 `generate_activation_codes()` L14: 嵌套深度: 4
- 🏗️ `generate_activation_codes()` L14: 中等嵌套: 4

**详情**:
- 循环复杂度: 平均: 8.0, 最大: 8
- 认知复杂度: 平均: 16.0, 最大: 16
- 嵌套深度: 平均: 4.0, 最大: 4
- 函数长度: 平均: 29.0 行, 最大: 29 行
- 文件长度: 31 代码量 (43 总计)
- 参数数量: 平均: 3.0, 最大: 3
- 代码重复: 未发现函数
- 结构分析: 1 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 12.9% (4/31)
- 命名规范: 无命名违规

### 79. backend\exams\report_service_support.py

**糟糕指数: 9.69**

> 行数: 208 总计, 167 代码, 21 注释 | 函数: 5 | 类: 2

**问题**: ⚠️ 其他问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_report_generation_context` | L48-99 | 52 | 7 | 0 | 10 | ✓ |
| `normalize_llm_feedback` | L105-129 | 25 | 5 | 1 | 3 | ✓ |
| `apply_completed_report` | L172-199 | 28 | 5 | 0 | 5 | ✓ |
| `build_report_overview` | L135-166 | 32 | 2 | 0 | 12 | ✓ |
| `mapping_value` | L205-207 | 3 | 1 | 0 | 3 | ✓ |

**全部问题 (3)**

- 📏 `build_report_generation_context()` L48: 52 代码量
- 📏 `build_report_generation_context()` L48: 10 参数数量
- 📏 `build_report_overview()` L135: 12 参数数量

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 7
- 认知复杂度: 平均: 4.4, 最大: 7
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 28.0 行, 最大: 52 行
- 文件长度: 167 代码量 (208 总计)
- 参数数量: 平均: 6.6, 最大: 12
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 12.6% (21/167)
- 命名规范: 无命名违规

### 80. backend\ai_services\test_student_rag_base.py

**糟糕指数: 9.55**

> 行数: 180 总计, 168 代码, 6 注释 | 函数: 1 | 类: 1

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L43-179 | 137 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 📏 `setUp()` L43: 137 代码量
- 🏷️ `setUp()` L43: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 137.0 行, 最大: 137 行
- 文件长度: 168 代码量 (180 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 3.6% (6/168)
- 命名规范: 发现 1 个违规

### 81. backend\ai_services\test_student_rag_context.py

**糟糕指数: 9.46**

> 行数: 256 总计, 213 代码, 21 注释 | 函数: 6 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 2, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_build_path_context_should_expose_multi_mode_sources` | L44-59 | 16 | 1 | 0 | 2 | ✓ |
| `test_answer_graph_question_should_fallback_to_graph_context_when_llm_unavailable` | L66-82 | 17 | 1 | 0 | 3 | ✓ |
| `test_local_context_should_merge_vector_hits_into_sources` | L89-117 | 29 | 1 | 0 | 3 | ✓ |
| `test_answer_graph_question_should_merge_graph_query_sources` | L125-164 | 40 | 1 | 0 | 4 | ✓ |
| `test_build_point_support_payload_should_include_graph_query_summary` | L171-207 | 37 | 1 | 0 | 3 | ✓ |
| `test_answer_course_question_should_merge_course_level_graph_sources` | L215-255 | 41 | 1 | 0 | 4 | ✓ |

**全部问题 (2)**

- 📋 `test_build_path_context_should_expose_multi_mode_sources()` L44: 重复模式: test_build_path_context_should_expose_multi_mode_sources, test_answer_graph_question_should_fallback_to_graph_context_when_llm_unavailable
- 📋 `test_answer_graph_question_should_merge_graph_query_sources()` L125: 重复模式: test_answer_graph_question_should_merge_graph_query_sources, test_answer_course_question_should_merge_course_level_graph_sources

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 30.0 行, 最大: 41 行
- 文件长度: 213 代码量 (256 总计)
- 参数数量: 平均: 3.2, 最大: 4
- 代码重复: 33.3% 重复 (2/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 9.9% (21/213)
- 命名规范: 无命名违规

### 82. backend\ai_services\services\llm_service.py

**糟糕指数: 9.33**

> 行数: 555 总计, 418 代码, 78 注释 | 函数: 24 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_detect_provider` | L233-279 | 47 | 11 | 1 | 1 | ✓ |
| `_resolve_extra_body` | L284-302 | 19 | 8 | 2 | 1 | ✓ |
| `_create_llm_client` | L383-420 | 38 | 8 | 1 | 4 | ✓ |
| `resolve_llm_proxy_for_base_url` | L61-69 | 9 | 7 | 1 | 1 | ✓ |
| `_get_llm_for_policy` | L467-507 | 41 | 7 | 1 | 3 | ✓ |
| `__init__` | L92-126 | 35 | 6 | 1 | 3 | ✓ |
| `_get_llm` | L425-462 | 38 | 6 | 3 | 1 | ✓ |
| `_truncate_prompt` | L316-333 | 18 | 5 | 1 | 3 | ✓ |
| `_should_use_agent_service` | L540-550 | 11 | 5 | 1 | 2 | ✓ |
| `_resolve_execution_policy` | L338-370 | 33 | 4 | 1 | 2 | ✓ |
| `_read_runtime_setting` | L50-55 | 6 | 3 | 1 | 1 | ✓ |
| `_provider_from_model_name` | L209-216 | 8 | 3 | 2 | 2 | ✓ |
| `_first_non_empty_setting` | L222-228 | 7 | 3 | 2 | 2 | ✓ |
| `_get_agent_service` | L512-534 | 23 | 3 | 1 | 1 | ✓ |
| `provider_name` | L132-134 | 3 | 2 | 0 | 1 | ✓ |
| `resolved_api_key` | L140-142 | 3 | 2 | 0 | 1 | ✓ |
| `resolved_base_url` | L148-150 | 3 | 2 | 0 | 1 | ✓ |
| `api_format` | L156-158 | 3 | 2 | 0 | 1 | ✓ |
| `resolved_proxy_url` | L172-174 | 3 | 2 | 0 | 1 | ✓ |
| `_read_setting` | L164-166 | 3 | 1 | 0 | 1 | ✓ |
| `resolved_extra_body` | L180-182 | 3 | 1 | 0 | 1 | ✓ |
| `_normalize_provider_name` | L188-203 | 16 | 1 | 0 | 2 | ✓ |
| `_clamp_positive_int` | L308-310 | 3 | 1 | 0 | 2 | ✓ |
| `is_available` | L376-378 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (14)**

- 🔄 `_detect_provider()` L233: 复杂度: 11
- 🔄 `_detect_provider()` L233: 认知复杂度: 13
- 🏗️ `_get_llm()` L425: 中等嵌套: 3
- ❌ L263: 未处理的易出错调用
- 🏷️ `_read_runtime_setting()` L50: "_read_runtime_setting" - snake_case
- 🏷️ `__init__()` L92: "__init__" - snake_case
- 🏷️ `_read_setting()` L164: "_read_setting" - snake_case
- 🏷️ `_normalize_provider_name()` L188: "_normalize_provider_name" - snake_case
- 🏷️ `_provider_from_model_name()` L209: "_provider_from_model_name" - snake_case
- 🏷️ `_first_non_empty_setting()` L222: "_first_non_empty_setting" - snake_case
- 🏷️ `_detect_provider()` L233: "_detect_provider" - snake_case
- 🏷️ `_resolve_extra_body()` L284: "_resolve_extra_body" - snake_case
- 🏷️ `_clamp_positive_int()` L308: "_clamp_positive_int" - snake_case
- 🏷️ `_truncate_prompt()` L316: "_truncate_prompt" - snake_case

**详情**:
- 循环复杂度: 平均: 3.9, 最大: 11
- 认知复杂度: 平均: 5.5, 最大: 13
- 嵌套深度: 平均: 0.8, 最大: 3
- 函数长度: 平均: 15.7 行, 最大: 47 行
- 文件长度: 418 代码量 (555 总计)
- 参数数量: 平均: 1.6, 最大: 4
- 代码重复: 4.2% 重复 (1/24)
- 结构分析: 1 个结构问题
- 错误处理: 1/6 个错误被忽略 (16.7%)
- 注释比例: 18.7% (78/418)
- 命名规范: 发现 16 个违规

### 83. backend\knowledge\teacher_map_support.py

**糟糕指数: 9.31**

> 行数: 138 总计, 109 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 3, 🏗️ 结构问题: 2, ❌ 错误处理问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `persist_imported_knowledge_map` | L106-137 | 32 | 9 | 3 | 3 | ✓ |
| `parse_imported_knowledge_map` | L67-100 | 34 | 8 | 4 | 1 | ✓ |
| `update_existing_graph_nodes` | L15-38 | 24 | 5 | 2 | 2 | ✓ |
| `rebuild_graph_relations` | L44-61 | 18 | 5 | 2 | 2 | ✓ |

**全部问题 (8)**

- 🔄 `parse_imported_knowledge_map()` L67: 认知复杂度: 16
- 🔄 `persist_imported_knowledge_map()` L106: 认知复杂度: 15
- 🔄 `parse_imported_knowledge_map()` L67: 嵌套深度: 4
- 🏗️ `parse_imported_knowledge_map()` L67: 中等嵌套: 4
- 🏗️ `persist_imported_knowledge_map()` L106: 中等嵌套: 3
- ❌ L83: 未处理的易出错调用
- ❌ L84: 未处理的易出错调用
- ❌ L85: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 6.8, 最大: 9
- 认知复杂度: 平均: 12.3, 最大: 16
- 嵌套深度: 平均: 2.8, 最大: 4
- 函数长度: 平均: 27.0 行, 最大: 34 行
- 文件长度: 109 代码量 (138 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 2 个结构问题
- 错误处理: 3/22 个错误被忽略 (13.6%)
- 注释比例: 11.0% (12/109)
- 命名规范: 无命名违规

### 84. backend\platform_ai\rag\runtime_materialization_mixin.py

**糟糕指数: 9.31**

> 行数: 296 总计, 229 代码, 39 注释 | 函数: 13 | 类: 1

**问题**: 🔄 复杂度问题: 1, ❌ 错误处理问题: 17, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_projection_from_graph` | L146-187 | 42 | 10 | 2 | 2 | ✓ |
| `_embedder` | L88-102 | 15 | 6 | 1 | 1 | ✓ |
| `_vector_points` | L192-225 | 34 | 5 | 2 | 3 | ✓ |
| `materialize_course_payload` | L230-267 | 38 | 5 | 1 | 3 | ✓ |
| `ensure_materialized` | L272-280 | 9 | 5 | 1 | 3 | ✓ |
| `_build_chunks` | L118-141 | 24 | 4 | 1 | 2 | ✓ |
| `clear_course_payload` | L285-295 | 11 | 3 | 1 | 2 | ✓ |
| `_vector_dimension` | L50-55 | 6 | 2 | 1 | 1 | ✓ |
| `qdrant_directory` | L60-65 | 6 | 2 | 1 | 1 | ✓ |
| `_qdrant` | L77-83 | 7 | 2 | 1 | 1 | ✓ |
| `_collection_exists` | L107-113 | 7 | 2 | 1 | 2 | ✓ |
| `__init__` | L41-45 | 5 | 1 | 0 | 1 | ✗ |
| `collection_name` | L70-72 | 3 | 1 | 0 | 2 | ✓ |

**全部问题 (26)**

- 🔄 `_projection_from_graph()` L146: 认知复杂度: 14
- ❌ L132: 未处理的易出错调用
- ❌ L133: 未处理的易出错调用
- ❌ L134: 未处理的易出错调用
- ❌ L135: 未处理的易出错调用
- ❌ L157: 未处理的易出错调用
- ❌ L158: 未处理的易出错调用
- ❌ L159: 未处理的易出错调用
- ❌ L160: 未处理的易出错调用
- ❌ L161: 未处理的易出错调用
- ❌ L162: 未处理的易出错调用
- ❌ L163: 未处理的易出错调用
- ❌ L165: 未处理的易出错调用
- ❌ L167: 未处理的易出错调用
- ❌ L211: 未处理的易出错调用
- ❌ L212: 未处理的易出错调用
- ❌ L213: 未处理的易出错调用
- ❌ L214: 未处理的易出错调用
- 🏷️ `__init__()` L41: "__init__" - snake_case
- 🏷️ `_vector_dimension()` L50: "_vector_dimension" - snake_case
- 🏷️ `_qdrant()` L77: "_qdrant" - snake_case
- 🏷️ `_embedder()` L88: "_embedder" - snake_case
- 🏷️ `_collection_exists()` L107: "_collection_exists" - snake_case
- 🏷️ `_build_chunks()` L118: "_build_chunks" - snake_case
- 🏷️ `_projection_from_graph()` L146: "_projection_from_graph" - snake_case
- 🏷️ `_vector_points()` L192: "_vector_points" - snake_case

**详情**:
- 循环复杂度: 平均: 3.7, 最大: 10
- 认知复杂度: 平均: 5.7, 最大: 14
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 15.9 行, 最大: 42 行
- 文件长度: 229 代码量 (296 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 17/30 个错误被忽略 (56.7%)
- 注释比例: 17.0% (39/229)
- 命名规范: 发现 8 个违规

### 85. backend\common\defense_demo_path.py

**糟糕指数: 9.31**

> 行数: 424 总计, 351 代码, 39 注释 | 函数: 13 | 类: 0

**问题**: ⚠️ 其他问题: 5, ❌ 错误处理问题: 2, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_complete_study_progress` | L356-385 | 30 | 7 | 1 | 5 | ✓ |
| `_complete_stage_progress` | L391-423 | 33 | 7 | 1 | 5 | ✓ |
| `_apply_demo_progress_payload` | L240-259 | 20 | 5 | 1 | 4 | ✓ |
| `_collect_mastery_change` | L338-350 | 13 | 5 | 1 | 3 | ✓ |
| `_apply_completed_statuses` | L298-313 | 16 | 4 | 2 | 1 | ✓ |
| `_mastery_maps_from_result` | L319-332 | 14 | 4 | 2 | 1 | ✓ |
| `_ensure_demo_learning_path` | L19-55 | 37 | 2 | 1 | 6 | ✓ |
| `_sync_demo_nodes` | L152-178 | 27 | 2 | 1 | 6 | ✓ |
| `_upsert_demo_node` | L184-220 | 37 | 2 | 0 | 6 | ✓ |
| `_apply_completed_stage_result` | L265-292 | 28 | 2 | 1 | 5 | ✓ |
| `_upsert_demo_path` | L61-71 | 11 | 1 | 0 | 2 | ✓ |
| `_demo_node_specs` | L77-146 | 70 | 1 | 0 | 1 | ✓ |
| `_progress_defaults` | L226-234 | 9 | 1 | 0 | 0 | ✓ |

**全部问题 (16)**

- 📏 `_demo_node_specs()` L77: 70 代码量
- 📏 `_ensure_demo_learning_path()` L19: 6 参数数量
- 📏 `_sync_demo_nodes()` L152: 6 参数数量
- 📏 `_upsert_demo_node()` L184: 6 参数数量
- ❌ L253: 未处理的易出错调用
- ❌ L371: 未处理的易出错调用
- 🏷️ `_ensure_demo_learning_path()` L19: "_ensure_demo_learning_path" - snake_case
- 🏷️ `_upsert_demo_path()` L61: "_upsert_demo_path" - snake_case
- 🏷️ `_demo_node_specs()` L77: "_demo_node_specs" - snake_case
- 🏷️ `_sync_demo_nodes()` L152: "_sync_demo_nodes" - snake_case
- 🏷️ `_upsert_demo_node()` L184: "_upsert_demo_node" - snake_case
- 🏷️ `_progress_defaults()` L226: "_progress_defaults" - snake_case
- 🏷️ `_apply_demo_progress_payload()` L240: "_apply_demo_progress_payload" - snake_case
- 🏷️ `_apply_completed_stage_result()` L265: "_apply_completed_stage_result" - snake_case
- 🏷️ `_apply_completed_statuses()` L298: "_apply_completed_statuses" - snake_case
- 🏷️ `_mastery_maps_from_result()` L319: "_mastery_maps_from_result" - snake_case

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 7
- 认知复杂度: 平均: 5.0, 最大: 9
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 26.5 行, 最大: 70 行
- 文件长度: 351 代码量 (424 总计)
- 参数数量: 平均: 3.5, 最大: 6
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 2/12 个错误被忽略 (16.7%)
- 注释比例: 11.1% (39/351)
- 命名规范: 发现 13 个违规

### 86. backend\tools\db_management.py

**糟糕指数: 9.21**

> 行数: 216 总计, 161 代码, 15 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `pg_bootstrap` | L173-215 | 43 | 8 | 2 | 4 | ✓ |
| `clear_database` | L65-141 | 77 | 5 | 2 | 1 | ✓ |
| `create_test_data` | L147-167 | 21 | 4 | 1 | 0 | ✓ |
| `django_check` | L45-59 | 15 | 2 | 1 | 1 | ✓ |
| `db_check` | L20-39 | 20 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 📏 `clear_database()` L65: 77 代码量
- ❌ L138: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 8
- 认知复杂度: 平均: 6.4, 最大: 12
- 嵌套深度: 平均: 1.2, 最大: 2
- 函数长度: 平均: 35.2 行, 最大: 77 行
- 文件长度: 161 代码量 (216 总计)
- 参数数量: 平均: 1.4, 最大: 4
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 9.3% (15/161)
- 命名规范: 无命名违规

### 87. backend\common\neo4j_queries.py

**糟糕指数: 9.17**

> 行数: 293 总计, 246 代码, 27 注释 | 函数: 8 | 类: 1

**问题**: 📋 重复问题: 2, 🏗️ 结构问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `find_learning_path` | L68-100 | 33 | 6 | 2 | 3 | ✓ |
| `get_knowledge_map` | L130-178 | 49 | 5 | 2 | 3 | ✓ |
| `get_knowledge_point_neo4j` | L183-232 | 50 | 5 | 3 | 2 | ✓ |
| `get_knowledge_points_neo4j` | L237-263 | 27 | 4 | 2 | 2 | ✓ |
| `get_knowledge_relations_neo4j` | L268-292 | 25 | 4 | 2 | 2 | ✓ |
| `get_graph_stats` | L105-125 | 21 | 3 | 2 | 2 | ✓ |
| `get_prerequisites` | L20-39 | 20 | 2 | 1 | 3 | ✓ |
| `get_dependents` | L44-63 | 20 | 2 | 1 | 3 | ✓ |

**全部问题 (3)**

- 📋 `get_prerequisites()` L20: 重复模式: get_prerequisites, get_dependents
- 📋 `get_knowledge_points_neo4j()` L237: 重复模式: get_knowledge_points_neo4j, get_knowledge_relations_neo4j
- 🏗️ `get_knowledge_point_neo4j()` L183: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 3.9, 最大: 6
- 认知复杂度: 平均: 7.6, 最大: 11
- 嵌套深度: 平均: 1.9, 最大: 3
- 函数长度: 平均: 30.6 行, 最大: 50 行
- 文件长度: 246 代码量 (293 总计)
- 参数数量: 平均: 2.5, 最大: 3
- 代码重复: 25.0% 重复 (2/8)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 11.0% (27/246)
- 命名规范: 无命名违规

### 88. backend\platform_ai\rag\runtime_graph_query_mixin.py

**糟糕指数: 9.01**

> 行数: 401 总计, 329 代码, 42 注释 | 函数: 13 | 类: 1

**问题**: ⚠️ 其他问题: 4, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_available_tools` | L276-320 | 45 | 6 | 2 | 7 | ✓ |
| `_text2cypher_tool_result` | L189-245 | 57 | 5 | 1 | 5 | ✓ |
| `query_graph` | L365-400 | 36 | 5 | 1 | 6 | ✓ |
| `_graph_query_examples` | L59-100 | 42 | 3 | 0 | 4 | ✓ |
| `_semantic_tool_result` | L146-184 | 39 | 2 | 0 | 5 | ✓ |
| `_graph_query_schema` | L40-54 | 15 | 1 | 0 | 1 | ✓ |
| `_text2cypher_prompt` | L105-134 | 30 | 1 | 0 | 1 | ✓ |
| `_graph_record_formatter` | L139-141 | 3 | 1 | 0 | 2 | ✓ |
| `_graph_tools_system_instruction` | L250-257 | 8 | 1 | 0 | 1 | ✓ |
| `_tool_line` | L262-264 | 3 | 1 | 0 | 2 | ✓ |
| `_tool_source` | L269-271 | 3 | 1 | 0 | 2 | ✓ |
| `_query_graph_semantic_only` | L325-340 | 16 | 1 | 0 | 5 | ✓ |
| `_query_graph_with_tools` | L345-360 | 16 | 1 | 0 | 4 | ✓ |

**全部问题 (13)**

- 📏 `_text2cypher_tool_result()` L189: 57 代码量
- 📏 `_build_available_tools()` L276: 7 参数数量
- 📏 `query_graph()` L365: 6 参数数量
- 🏷️ `_graph_query_schema()` L40: "_graph_query_schema" - snake_case
- 🏷️ `_graph_query_examples()` L59: "_graph_query_examples" - snake_case
- 🏷️ `_text2cypher_prompt()` L105: "_text2cypher_prompt" - snake_case
- 🏷️ `_graph_record_formatter()` L139: "_graph_record_formatter" - snake_case
- 🏷️ `_semantic_tool_result()` L146: "_semantic_tool_result" - snake_case
- 🏷️ `_text2cypher_tool_result()` L189: "_text2cypher_tool_result" - snake_case
- 🏷️ `_graph_tools_system_instruction()` L250: "_graph_tools_system_instruction" - snake_case
- 🏷️ `_tool_line()` L262: "_tool_line" - snake_case
- 🏷️ `_tool_source()` L269: "_tool_source" - snake_case
- 🏷️ `_build_available_tools()` L276: "_build_available_tools" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 6
- 认知复杂度: 平均: 2.8, 最大: 10
- 嵌套深度: 平均: 0.3, 最大: 2
- 函数长度: 平均: 24.1 行, 最大: 57 行
- 文件长度: 329 代码量 (401 总计)
- 参数数量: 平均: 3.5, 最大: 7
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 12.8% (42/329)
- 命名规范: 发现 12 个违规

### 89. backend\platform_ai\rag\corpus_communities.py

**糟糕指数: 8.99**

> 行数: 240 总计, 176 代码, 33 注释 | 函数: 10 | 类: 1

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `community_summary` | L92-103 | 12 | 4 | 0 | 3 | ✓ |
| `detect_communities` | L30-36 | 7 | 3 | 1 | 1 | ✓ |
| `community_centrality` | L42-46 | 5 | 2 | 1 | 1 | ✓ |
| `build_community_records` | L191-236 | 46 | 2 | 1 | 1 | ✓ |
| `select_top_node_ids` | L52-61 | 10 | 1 | 0 | 2 | ✓ |
| `relation_breakdown` | L67-72 | 6 | 1 | 0 | 1 | ✓ |
| `community_themes` | L78-86 | 9 | 1 | 0 | 2 | ✓ |
| `build_community_payload` | L109-123 | 15 | 1 | 0 | 4 | ✓ |
| `build_community_report` | L129-155 | 27 | 1 | 0 | 7 | ✓ |
| `append_community_document` | L161-185 | 25 | 1 | 0 | 6 | ✓ |

**全部问题 (3)**

- 📏 `build_community_report()` L129: 7 参数数量
- 📏 `append_community_document()` L161: 6 参数数量
- ❌ L70: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.7, 最大: 4
- 认知复杂度: 平均: 2.3, 最大: 5
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 16.2 行, 最大: 46 行
- 文件长度: 176 代码量 (240 总计)
- 参数数量: 平均: 2.8, 最大: 7
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 18.8% (33/176)
- 命名规范: 无命名违规

### 90. frontend\src\views\teacher\useTeacherResourceManage.js

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

### 91. backend\ai_services\services\mefkt_legacy_runtime.py

**糟糕指数: 8.77**

> 行数: 399 总计, 310 代码, 45 注释 | 函数: 14 | 类: 1

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_legacy_state` | L180-227 | 48 | 7 | 1 | 5 | ✓ |
| `build_question_online_state` | L142-174 | 33 | 6 | 0 | 5 | ✓ |
| `load_mefkt_state` | L63-99 | 37 | 5 | 1 | 3 | ✓ |
| `resolve_backend_path` | L47-57 | 11 | 4 | 1 | 2 | ✓ |
| `load_metadata_payload` | L115-124 | 10 | 4 | 1 | 2 | ✓ |
| `build_history_tensors_legacy` | L294-320 | 27 | 4 | 2 | 2 | ✓ |
| `resolve_metadata_path` | L105-109 | 5 | 3 | 0 | 3 | ✓ |
| `is_question_online_checkpoint` | L130-136 | 7 | 3 | 0 | 2 | ✓ |
| `predict_legacy_mastery` | L241-288 | 48 | 3 | 1 | 5 | ✓ |
| `resolve_legacy_target_ids` | L326-340 | 15 | 3 | 1 | 3 | ✓ |
| `cast_tensor_state` | L233-235 | 3 | 2 | 0 | 1 | ✓ |
| `predict_legacy_candidates` | L359-388 | 30 | 2 | 1 | 8 | ✓ |
| `empty_legacy_prediction` | L346-353 | 8 | 1 | 0 | 0 | ✓ |
| `legacy_confidence` | L394-398 | 5 | 1 | 0 | 3 | ✓ |

**全部问题 (4)**

- 📏 `predict_legacy_candidates()` L359: 8 参数数量
- ❌ L162: 未处理的易出错调用
- ❌ L170: 未处理的易出错调用
- ❌ L338: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.4, 最大: 7
- 认知复杂度: 平均: 4.7, 最大: 9
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 20.5 行, 最大: 48 行
- 文件长度: 310 代码量 (399 总计)
- 参数数量: 平均: 3.1, 最大: 8
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 3/15 个错误被忽略 (20.0%)
- 注释比例: 14.5% (45/310)
- 命名规范: 无命名违规

### 92. backend\ai_services\services\llm_profile_path_support.py

**糟糕指数: 8.73**

> 行数: 379 总计, 288 代码, 42 注释 | 函数: 14 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 23

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_path_constraints_text` | L180-218 | 39 | 7 | 1 | 1 | ✓ |
| `summarize_path_strengths_and_weaknesses` | L154-174 | 21 | 6 | 0 | 1 | ✓ |
| `build_profile_course_context` | L10-23 | 14 | 5 | 1 | 2 | ✓ |
| `summarize_mastery_distribution` | L42-55 | 14 | 5 | 1 | 1 | ✓ |
| `build_path_prompt` | L224-271 | 48 | 5 | 0 | 5 | ✓ |
| `build_path_fallback` | L277-305 | 29 | 5 | 0 | 1 | ✓ |
| `resolve_learning_stage` | L311-321 | 11 | 5 | 1 | 1 | ✓ |
| `build_profile_prompt` | L85-135 | 51 | 4 | 0 | 6 | ✓ |
| `build_resource_reason_prompt` | L327-355 | 29 | 4 | 0 | 4 | ✓ |
| `build_resource_reason_fallback` | L361-378 | 18 | 3 | 0 | 3 | ✓ |
| `format_mastery_lines` | L29-36 | 8 | 2 | 0 | 1 | ✓ |
| `identify_weaknesses` | L61-67 | 7 | 2 | 0 | 1 | ✓ |
| `identify_strengths` | L73-79 | 7 | 2 | 0 | 1 | ✓ |
| `build_profile_fallback` | L141-148 | 8 | 1 | 0 | 1 | ✓ |

**全部问题 (25)**

- 📏 `build_profile_prompt()` L85: 51 代码量
- 📏 `build_profile_prompt()` L85: 6 参数数量
- ❌ L33: 未处理的易出错调用
- ❌ L49: 未处理的易出错调用
- ❌ L64: 未处理的易出错调用
- ❌ L66: 未处理的易出错调用
- ❌ L76: 未处理的易出错调用
- ❌ L160: 未处理的易出错调用
- ❌ L165: 未处理的易出错调用
- ❌ L167: 未处理的易出错调用
- ❌ L170: 未处理的易出错调用
- ❌ L184: 未处理的易出错调用
- ❌ L199: 未处理的易出错调用
- ❌ L201: 未处理的易出错调用
- ❌ L203: 未处理的易出错调用
- ❌ L208: 未处理的易出错调用
- ❌ L216: 未处理的易出错调用
- ❌ L282: 未处理的易出错调用
- ❌ L288: 未处理的易出错调用
- ❌ L289: 未处理的易出错调用
- ❌ L290: 未处理的易出错调用
- ❌ L341: 未处理的易出错调用
- ❌ L342: 未处理的易出错调用
- ❌ L343: 未处理的易出错调用
- ❌ L375: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 7
- 认知复杂度: 平均: 4.6, 最大: 9
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 21.7 行, 最大: 51 行
- 文件长度: 288 代码量 (379 总计)
- 参数数量: 平均: 2.1, 最大: 6
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 23/31 个错误被忽略 (74.2%)
- 注释比例: 14.6% (42/288)
- 命名规范: 无命名违规

### 93. backend\assessments\assessment_helpers.py

**糟糕指数: 8.70**

> 行数: 220 总计, 151 代码, 36 注释 | 函数: 12 | 类: 0

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `format_option_display` | L90-94 | 5 | 7 | 0 | 1 | ✓ |
| `get_question_title` | L120-129 | 10 | 5 | 1 | 1 | ✓ |
| `extract_answer_payload` | L62-68 | 7 | 3 | 2 | 1 | ✓ |
| `calculate_initial_mastery_baseline` | L45-56 | 12 | 2 | 1 | 2 | ✓ |
| `persist_mastery_snapshot` | L143-172 | 30 | 2 | 1 | 4 | ✓ |
| `upsert_knowledge_assessment_result` | L178-219 | 42 | 2 | 0 | 10 | ✓ |
| `get_authenticated_user` | L33-39 | 7 | 1 | 0 | 1 | ✓ |
| `answer_tokens_for` | L74-76 | 3 | 1 | 0 | 2 | ✓ |
| `option_tokens_for` | L82-84 | 3 | 1 | 0 | 1 | ✓ |
| `build_answer_display_value` | L100-106 | 7 | 1 | 0 | 3 | ✓ |
| `clean_text` | L112-114 | 3 | 1 | 0 | 1 | ✓ |
| `normalize_options` | L135-137 | 3 | 1 | 0 | 2 | ✓ |

**全部问题 (1)**

- 📏 `upsert_knowledge_assessment_result()` L178: 10 参数数量

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 7
- 认知复杂度: 平均: 3.1, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 11.0 行, 最大: 42 行
- 文件长度: 151 代码量 (220 总计)
- 参数数量: 平均: 2.4, 最大: 10
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 0/5 个错误被忽略 (0.0%)
- 注释比例: 23.8% (36/151)
- 命名规范: 无命名违规

### 94. backend\common\grading.py

**糟糕指数: 8.68**

> 行数: 284 总计, 213 代码, 27 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_normalized_score_map` | L133-174 | 42 | 10 | 1 | 3 | ✓ |
| `score_questions` | L180-258 | 79 | 9 | 3 | 3 | ✓ |
| `check_answer` | L95-127 | 33 | 8 | 2 | 3 | ✓ |
| `_normalize_option_values` | L58-76 | 19 | 7 | 2 | 1 | ✓ |
| `extract_answer_value` | L28-40 | 13 | 5 | 2 | 1 | ✓ |
| `_normalize_text_answer` | L46-52 | 7 | 4 | 1 | 1 | ✓ |
| `_normalize_boolean_answer` | L82-89 | 8 | 3 | 1 | 1 | ✓ |
| `calculate_mastery` | L12-22 | 11 | 2 | 1 | 2 | ✓ |
| `grade_exam` | L264-273 | 10 | 1 | 0 | 3 | ✓ |

**全部问题 (7)**

- 🔄 `score_questions()` L180: 认知复杂度: 15
- 📏 `score_questions()` L180: 79 代码量
- 🏗️ `score_questions()` L180: 中等嵌套: 3
- ❌ L36: 未处理的易出错调用
- 🏷️ `_normalize_text_answer()` L46: "_normalize_text_answer" - snake_case
- 🏷️ `_normalize_option_values()` L58: "_normalize_option_values" - snake_case
- 🏷️ `_normalize_boolean_answer()` L82: "_normalize_boolean_answer" - snake_case

**详情**:
- 循环复杂度: 平均: 5.4, 最大: 10
- 认知复杂度: 平均: 8.3, 最大: 15
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 24.7 行, 最大: 79 行
- 文件长度: 213 代码量 (284 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 12.7% (27/213)
- 命名规范: 发现 3 个违规

### 95. backend\knowledge\map_views.py

**糟糕指数: 8.59**

> 行数: 257 总计, 204 代码, 18 注释 | 函数: 6 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `update_knowledge_mastery` | L219-256 | 38 | 10 | 3 | 1 | ✓ |
| `get_knowledge_point_detail` | L77-129 | 53 | 7 | 2 | 2 | ✓ |
| `get_knowledge_points_list` | L166-195 | 30 | 6 | 1 | 1 | ✓ |
| `get_knowledge_map` | L36-69 | 34 | 5 | 1 | 1 | ✓ |
| `get_knowledge_relations` | L137-158 | 22 | 3 | 1 | 1 | ✓ |
| `get_knowledge_mastery` | L203-211 | 9 | 2 | 1 | 1 | ✓ |

**全部问题 (6)**

- 🔄 `update_knowledge_mastery()` L219: 认知复杂度: 16
- 📏 `get_knowledge_point_detail()` L77: 53 代码量
- 🏗️ `update_knowledge_mastery()` L219: 中等嵌套: 3
- ❌ L54: 未处理的易出错调用
- ❌ L103: 未处理的易出错调用
- ❌ L106: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.5, 最大: 10
- 认知复杂度: 平均: 8.5, 最大: 16
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 31.0 行, 最大: 53 行
- 文件长度: 204 代码量 (257 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 1 个结构问题
- 错误处理: 3/10 个错误被忽略 (30.0%)
- 注释比例: 8.8% (18/204)
- 命名规范: 无命名违规

### 96. backend\tools\kt_synthetic.py

**糟糕指数: 8.52**

> 行数: 257 总计, 209 代码, 20 注释 | 函数: 6 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_simulate_student_sequence` | L148-250 | 103 | 5 | 2 | 6 | ✓ |
| `_sample_student_profile` | L81-125 | 45 | 3 | 1 | 1 | ✓ |
| `_build_kp_profiles` | L53-75 | 23 | 2 | 1 | 3 | ✓ |
| `_clamp` | L37-39 | 3 | 1 | 0 | 3 | ✓ |
| `_mean` | L45-47 | 3 | 1 | 0 | 2 | ✓ |
| `_choose_focus_kp` | L131-142 | 12 | 1 | 0 | 4 | ✓ |

**全部问题 (8)**

- 📏 `_simulate_student_sequence()` L148: 103 代码量
- 📏 `_simulate_student_sequence()` L148: 6 参数数量
- 🏷️ `_clamp()` L37: "_clamp" - snake_case
- 🏷️ `_mean()` L45: "_mean" - snake_case
- 🏷️ `_build_kp_profiles()` L53: "_build_kp_profiles" - snake_case
- 🏷️ `_sample_student_profile()` L81: "_sample_student_profile" - snake_case
- 🏷️ `_choose_focus_kp()` L131: "_choose_focus_kp" - snake_case
- 🏷️ `_simulate_student_sequence()` L148: "_simulate_student_sequence" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 5
- 认知复杂度: 平均: 3.5, 最大: 9
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 31.5 行, 最大: 103 行
- 文件长度: 209 代码量 (257 总计)
- 参数数量: 平均: 3.2, 最大: 6
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 9.6% (20/209)
- 命名规范: 发现 6 个违规

### 97. frontend\src\components\knowledge\useKnowledgeGraphD3.js

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

### 98. backend\common\neo4j_sync.py

**糟糕指数: 8.42**

> 行数: 239 总计, 202 代码, 18 注释 | 函数: 5 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `sync_knowledge_graph` | L20-119 | 53 | 13 | 1 | 2 | ✓ |
| `_sync_tx` | L61-107 | 47 | 4 | 2 | 1 | ✗ |
| `clear_all` | L124-147 | 24 | 4 | 1 | 1 | ✓ |
| `import_test_data` | L152-219 | 68 | 4 | 2 | 2 | ✓ |
| `get_all_courses` | L224-238 | 15 | 2 | 1 | 1 | ✓ |

**全部问题 (5)**

- 🔄 `sync_knowledge_graph()` L20: 复杂度: 13
- 🔄 `sync_knowledge_graph()` L20: 认知复杂度: 15
- 📏 `sync_knowledge_graph()` L20: 53 代码量
- 📏 `import_test_data()` L152: 68 代码量
- 🏷️ `_sync_tx()` L61: "_sync_tx" - snake_case

**详情**:
- 循环复杂度: 平均: 5.4, 最大: 13
- 认知复杂度: 平均: 8.2, 最大: 15
- 嵌套深度: 平均: 1.4, 最大: 2
- 函数长度: 平均: 41.4 行, 最大: 68 行
- 文件长度: 202 代码量 (239 总计)
- 参数数量: 平均: 1.4, 最大: 2
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/13 个错误被忽略 (0.0%)
- 注释比例: 8.9% (18/202)
- 命名规范: 发现 1 个违规

### 99. backend\tools\api_regression_cleanup.py

**糟糕指数: 8.28**

> 行数: 171 总计, 117 代码, 27 注释 | 函数: 7 | 类: 2

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `cleanup_regression_entities` | L47-53 | 7 | 3 | 1 | 1 | ✓ |
| `build_actions_from_templates` | L109-129 | 21 | 3 | 2 | 4 | ✓ |
| `build_cleanup_actions` | L59-64 | 6 | 1 | 0 | 1 | ✓ |
| `teacher_cleanup_actions` | L70-84 | 15 | 1 | 0 | 1 | ✓ |
| `admin_cleanup_actions` | L90-103 | 14 | 1 | 0 | 1 | ✓ |
| `record_cleanup_action` | L135-144 | 10 | 1 | 0 | 2 | ✓ |
| `_cleanup_regression_entities` | L150-170 | 21 | 1 | 0 | 7 | ✓ |

**全部问题 (3)**

- 📏 `_cleanup_regression_entities()` L150: 7 参数数量
- 📋 `teacher_cleanup_actions()` L70: 重复模式: teacher_cleanup_actions, admin_cleanup_actions
- 🏷️ `_cleanup_regression_entities()` L150: "_cleanup_regression_entities" - snake_case

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 3
- 认知复杂度: 平均: 2.4, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 13.4 行, 最大: 21 行
- 文件长度: 117 代码量 (171 总计)
- 参数数量: 平均: 2.4, 最大: 7
- 代码重复: 14.3% 重复 (1/7)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 23.1% (27/117)
- 命名规范: 发现 1 个违规

### 100. backend\users\test_class_api.py

**糟糕指数: 8.23**

> 行数: 238 总计, 167 代码, 36 注释 | 函数: 10 | 类: 2

**问题**: 📋 重复问题: 2, ❌ 错误处理问题: 7, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L21-41 | 21 | 1 | 0 | 1 | ✓ |
| `test_generate_invitation` | L46-54 | 9 | 1 | 0 | 1 | ✓ |
| `test_student_join_class` | L59-80 | 22 | 1 | 0 | 1 | ✓ |
| `test_cannot_join_class_twice` | L85-103 | 19 | 1 | 0 | 1 | ✓ |
| `test_join_class_returns_published_course_without_default_course` | L108-133 | 26 | 1 | 0 | 1 | ✓ |
| `test_my_classes` | L138-150 | 13 | 1 | 0 | 1 | ✓ |
| `test_leave_class` | L155-170 | 16 | 1 | 0 | 1 | ✓ |
| `setUp` | L182-209 | 28 | 1 | 0 | 1 | ✓ |
| `test_get_class_students` | L214-220 | 7 | 1 | 0 | 1 | ✓ |
| `test_remove_student_from_class` | L225-237 | 13 | 1 | 0 | 1 | ✓ |

**全部问题 (11)**

- 📋 `test_student_join_class()` L59: 重复模式: test_student_join_class, test_cannot_join_class_twice
- 📋 `test_my_classes()` L138: 重复模式: test_my_classes, test_remove_student_from_class
- ❌ L61: 未处理的易出错调用
- ❌ L87: 未处理的易出错调用
- ❌ L93: 未处理的易出错调用
- ❌ L114: 未处理的易出错调用
- ❌ L119: 未处理的易出错调用
- ❌ L140: 未处理的易出错调用
- ❌ L157: 未处理的易出错调用
- 🏷️ `setUp()` L21: "setUp" - snake_case
- 🏷️ `setUp()` L182: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 17.4 行, 最大: 28 行
- 文件长度: 167 代码量 (238 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 20.0% 重复 (2/10)
- 结构分析: 0 个结构问题
- 错误处理: 7/22 个错误被忽略 (31.8%)
- 注释比例: 21.6% (36/167)
- 命名规范: 发现 2 个违规

### 101. frontend\src\views\student\useTaskLearning.js

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

### 102. backend\learning\path_rules.py

**糟糕指数: 8.19**

> 行数: 139 总计, 96 代码, 18 注释 | 函数: 6 | 类: 0

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `topological_mastery_order` | L82-116 | 35 | 12 | 3 | 4 | ✓ |
| `apply_prerequisite_caps` | L45-63 | 19 | 5 | 2 | 3 | ✓ |
| `partition_points_for_path` | L122-138 | 17 | 4 | 2 | 3 | ✓ |
| `is_auto_completable` | L69-76 | 8 | 3 | 1 | 3 | ✓ |
| `build_prerequisite_maps` | L33-39 | 7 | 2 | 1 | 1 | ✓ |
| `load_course_points` | L24-27 | 4 | 1 | 0 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `topological_mastery_order()` L82: 复杂度: 12
- 🔄 `topological_mastery_order()` L82: 认知复杂度: 18
- 🏗️ `topological_mastery_order()` L82: 中等嵌套: 3
- ❌ L108: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 12
- 认知复杂度: 平均: 7.5, 最大: 18
- 嵌套深度: 平均: 1.5, 最大: 3
- 函数长度: 平均: 15.0 行, 最大: 35 行
- 文件长度: 96 代码量 (139 总计)
- 参数数量: 平均: 2.5, 最大: 4
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 1 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 18.8% (18/96)
- 命名规范: 无命名违规

### 103. backend\courses\teacher_workspace_views.py

**糟糕指数: 8.18**

> 行数: 111 总计, 87 代码, 9 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 2, 🏗️ 结构问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `class_create` | L39-76 | 38 | 9 | 4 | 1 | ✓ |
| `course_workspace` | L21-31 | 11 | 5 | 1 | 2 | ✓ |
| `my_classes` | L84-110 | 27 | 5 | 1 | 1 | ✓ |

**全部问题 (3)**

- 🔄 `class_create()` L39: 认知复杂度: 17
- 🔄 `class_create()` L39: 嵌套深度: 4
- 🏗️ `class_create()` L39: 中等嵌套: 4

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 9
- 认知复杂度: 平均: 10.3, 最大: 17
- 嵌套深度: 平均: 2.0, 最大: 4
- 函数长度: 平均: 25.3 行, 最大: 38 行
- 文件长度: 87 代码量 (111 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 1 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 10.3% (9/87)
- 命名规范: 无命名违规

### 104. backend\assessments\knowledge_generation_support.py

**糟糕指数: 8.17**

> 行数: 154 总计, 112 代码, 21 注释 | 函数: 7 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `upsert_assessment_feedback_report` | L106-153 | 48 | 10 | 1 | 4 | ✓ |
| `load_assessment_result_snapshot` | L65-78 | 14 | 4 | 1 | 2 | ✓ |
| `resolve_async_generation_context` | L13-24 | 12 | 2 | 1 | 2 | ✓ |
| `build_assessment_mistake_payload` | L47-59 | 13 | 2 | 0 | 1 | ✓ |
| `update_generation_status` | L30-41 | 12 | 1 | 0 | 4 | ✓ |
| `refresh_learning_path_for_assessment` | L84-90 | 7 | 1 | 0 | 2 | ✓ |
| `refresh_learner_profile_for_assessment` | L96-100 | 5 | 1 | 0 | 2 | ✓ |

**全部问题 (7)**

- ❌ L77: 未处理的易出错调用
- ❌ L144: 未处理的易出错调用
- ❌ L145: 未处理的易出错调用
- ❌ L147: 未处理的易出错调用
- ❌ L148: 未处理的易出错调用
- ❌ L149: 未处理的易出错调用
- ❌ L150: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 10
- 认知复杂度: 平均: 3.9, 最大: 12
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 15.9 行, 最大: 48 行
- 文件长度: 112 代码量 (154 总计)
- 参数数量: 平均: 2.4, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 7/11 个错误被忽略 (63.6%)
- 注释比例: 18.8% (21/112)
- 命名规范: 无命名违规

### 105. backend\learning\stage_test_standard_submission.py

**糟糕指数: 8.08**

> 行数: 217 总计, 171 代码, 21 注释 | 函数: 7 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, 🏗️ 结构问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `update_standard_node_status` | L66-79 | 14 | 5 | 1 | 2 | ✓ |
| `fallback_mastery_update` | L179-206 | 28 | 5 | 3 | 3 | ✓ |
| `submit_standard_stage_test` | L25-60 | 36 | 3 | 1 | 6 | ✓ |
| `apply_stage_kt_predictions` | L149-173 | 25 | 3 | 2 | 3 | ✓ |
| `update_mastery_from_kt_or_fallback` | L85-103 | 19 | 2 | 1 | 3 | ✓ |
| `predict_stage_mastery` | L109-143 | 35 | 2 | 0 | 3 | ✓ |
| `refresh_learning_path` | L212-216 | 5 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- 📏 `submit_standard_stage_test()` L25: 6 参数数量
- 📋 `apply_stage_kt_predictions()` L149: 重复模式: apply_stage_kt_predictions, fallback_mastery_update
- 🏗️ `fallback_mastery_update()` L179: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 5
- 认知复杂度: 平均: 5.3, 最大: 11
- 嵌套深度: 平均: 1.1, 最大: 3
- 函数长度: 平均: 23.1 行, 最大: 36 行
- 文件长度: 171 代码量 (217 总计)
- 参数数量: 平均: 3.1, 最大: 6
- 代码重复: 14.3% 重复 (1/7)
- 结构分析: 1 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 12.3% (21/171)
- 命名规范: 无命名违规

### 106. backend\tools\api_regression_admin_support.py

**糟糕指数: 7.97**

> 行数: 350 总计, 317 代码, 15 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 5, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `run_admin_activation_flow` | L185-210 | 26 | 7 | 1 | 3 | ✓ |
| `run_admin_class_flow` | L267-349 | 83 | 6 | 1 | 6 | ✓ |
| `run_admin_user_flow` | L97-179 | 83 | 5 | 1 | 4 | ✓ |
| `run_admin_course_flow` | L216-261 | 46 | 5 | 1 | 4 | ✓ |
| `run_admin_read_checks` | L14-91 | 78 | 1 | 0 | 3 | ✓ |

**全部问题 (4)**

- 📏 `run_admin_read_checks()` L14: 78 代码量
- 📏 `run_admin_user_flow()` L97: 83 代码量
- 📏 `run_admin_class_flow()` L267: 83 代码量
- 📏 `run_admin_class_flow()` L267: 6 参数数量

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 7
- 认知复杂度: 平均: 6.4, 最大: 9
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 63.2 行, 最大: 83 行
- 文件长度: 317 代码量 (350 总计)
- 参数数量: 平均: 4.0, 最大: 6
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/5 个错误被忽略 (0.0%)
- 注释比例: 4.7% (15/317)
- 命名规范: 无命名违规

### 107. backend\learning\stage_test_results.py

**糟糕指数: 7.96**

> 行数: 124 总计, 105 代码, 9 注释 | 函数: 3 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `persist_stage_progress` | L20-57 | 38 | 3 | 1 | 9 | ✓ |
| `stage_response_payload` | L63-89 | 27 | 1 | 0 | 5 | ✓ |
| `_stored_stage_result` | L95-123 | 29 | 1 | 0 | 6 | ✓ |

**全部问题 (3)**

- 📏 `persist_stage_progress()` L20: 9 参数数量
- 📏 `_stored_stage_result()` L95: 6 参数数量
- 🏷️ `_stored_stage_result()` L95: "_stored_stage_result" - snake_case

**详情**:
- 循环复杂度: 平均: 1.7, 最大: 3
- 认知复杂度: 平均: 2.3, 最大: 5
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 31.3 行, 最大: 38 行
- 文件长度: 105 代码量 (124 总计)
- 参数数量: 平均: 6.7, 最大: 9
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 8.6% (9/105)
- 命名规范: 发现 1 个违规

### 108. backend\logs\views.py

**糟糕指数: 7.94**

> 行数: 362 总计, 242 代码, 54 注释 | 函数: 10 | 类: 1

**问题**: 🔄 复杂度问题: 2, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_apply_log_filters` | L48-85 | 38 | 11 | 2 | 2 | ✓ |
| `list_operation_logs` | L101-158 | 58 | 8 | 2 | 1 | ✓ |
| `export_logs` | L291-332 | 42 | 7 | 1 | 1 | ✓ |
| `get_operation_log_detail` | L166-181 | 16 | 3 | 1 | 2 | ✓ |
| `clean_expired_logs` | L340-361 | 22 | 3 | 1 | 1 | ✓ |
| `is_admin` | L91-93 | 3 | 2 | 0 | 1 | ✓ |
| `get_log_statistics` | L189-229 | 41 | 2 | 1 | 1 | ✓ |
| `get_log_filter_options` | L237-249 | 13 | 2 | 1 | 1 | ✓ |
| `get_log_modules` | L257-266 | 10 | 2 | 1 | 1 | ✓ |
| `get_log_actions` | L274-283 | 10 | 2 | 1 | 1 | ✓ |

**全部问题 (9)**

- 🔄 `_apply_log_filters()` L48: 复杂度: 11
- 🔄 `_apply_log_filters()` L48: 认知复杂度: 15
- 📏 `list_operation_logs()` L101: 58 代码量
- ❌ L311: 未处理的易出错调用
- ❌ L323: 未处理的易出错调用
- ❌ L324: 未处理的易出错调用
- ❌ L356: 忽略了错误返回值
- 🏷️ `_apply_log_filters()` L48: "_apply_log_filters" - snake_case
- 🏷️ L38: "_AdminCapableUser" - PascalCase

**详情**:
- 循环复杂度: 平均: 4.2, 最大: 11
- 认知复杂度: 平均: 6.4, 最大: 15
- 嵌套深度: 平均: 1.1, 最大: 2
- 函数长度: 平均: 25.3 行, 最大: 58 行
- 文件长度: 242 代码量 (362 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 4/17 个错误被忽略 (23.5%)
- 注释比例: 22.3% (54/242)
- 命名规范: 发现 2 个违规

### 109. backend\users\student_profile_support.py

**糟糕指数: 7.88**

> 行数: 333 总计, 235 代码, 54 注释 | 函数: 17 | 类: 1

**问题**: 🔄 复杂度问题: 2, ❌ 错误处理问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_profile_summary_payload` | L199-211 | 13 | 11 | 1 | 2 | ✓ |
| `build_student_profile_payload` | L32-52 | 21 | 5 | 1 | 2 | ✓ |
| `build_ability_scores` | L77-87 | 11 | 5 | 1 | 2 | ✓ |
| `ability_tags` | L130-157 | 28 | 5 | 1 | 1 | ✓ |
| `build_knowledge_mastery_payload` | L58-71 | 14 | 4 | 1 | 2 | ✓ |
| `habit_resource_tags` | L163-171 | 9 | 4 | 1 | 1 | ✓ |
| `habit_time_and_pace_tags` | L177-193 | 17 | 4 | 1 | 1 | ✓ |
| `build_habit_preferences` | L93-108 | 16 | 3 | 1 | 1 | ✓ |
| `parse_profile_history_limit` | L238-243 | 6 | 3 | 1 | 1 | ✓ |
| `snapshot_profile_summary` | L270-279 | 10 | 3 | 1 | 1 | ✓ |
| `build_learner_tags` | L114-124 | 11 | 2 | 1 | 2 | ✓ |
| `build_profile_refresh_payload` | L217-232 | 16 | 2 | 1 | 2 | ✓ |
| `build_export_mastery_list` | L305-314 | 10 | 2 | 0 | 1 | ✓ |
| `build_export_ability_scores` | L320-323 | 4 | 2 | 0 | 1 | ✓ |
| `build_export_habit_preferences` | L329-332 | 4 | 2 | 0 | 1 | ✓ |
| `build_profile_history_payload` | L249-264 | 16 | 1 | 0 | 3 | ✓ |
| `build_profile_export_response` | L285-299 | 15 | 1 | 0 | 1 | ✓ |

**全部问题 (9)**

- 🔄 `build_profile_summary_payload()` L199: 复杂度: 11
- 🔄 `build_profile_summary_payload()` L199: 认知复杂度: 13
- ❌ L191: 未处理的易出错调用
- ❌ L223: 未处理的易出错调用
- ❌ L226: 未处理的易出错调用
- ❌ L227: 未处理的易出错调用
- ❌ L228: 未处理的易出错调用
- ❌ L229: 未处理的易出错调用
- ❌ L230: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 11
- 认知复杂度: 平均: 4.9, 最大: 13
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 13.0 行, 最大: 28 行
- 文件长度: 235 代码量 (333 总计)
- 参数数量: 平均: 1.5, 最大: 3
- 代码重复: 0.0% 重复 (0/17)
- 结构分析: 0 个结构问题
- 错误处理: 7/9 个错误被忽略 (77.8%)
- 注释比例: 23.0% (54/235)
- 命名规范: 无命名违规

### 110. backend\common\defense_demo_content.py

**糟糕指数: 7.83**

> 行数: 347 总计, 313 代码, 15 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_ensure_demo_resources` | L75-168 | 94 | 6 | 2 | 3 | ✓ |
| `_ensure_demo_stage_test` | L174-268 | 95 | 5 | 1 | 3 | ✓ |
| `_ensure_demo_points` | L17-69 | 53 | 3 | 1 | 1 | ✓ |
| `_build_point_intro_payloads` | L274-309 | 36 | 2 | 1 | 1 | ✓ |
| `_build_ai_demo_query_payloads` | L315-346 | 32 | 1 | 0 | 1 | ✓ |

**全部问题 (8)**

- 📏 `_ensure_demo_points()` L17: 53 代码量
- 📏 `_ensure_demo_resources()` L75: 94 代码量
- 📏 `_ensure_demo_stage_test()` L174: 95 代码量
- 🏷️ `_ensure_demo_points()` L17: "_ensure_demo_points" - snake_case
- 🏷️ `_ensure_demo_resources()` L75: "_ensure_demo_resources" - snake_case
- 🏷️ `_ensure_demo_stage_test()` L174: "_ensure_demo_stage_test" - snake_case
- 🏷️ `_build_point_intro_payloads()` L274: "_build_point_intro_payloads" - snake_case
- 🏷️ `_build_ai_demo_query_payloads()` L315: "_build_ai_demo_query_payloads" - snake_case

**详情**:
- 循环复杂度: 平均: 3.4, 最大: 6
- 认知复杂度: 平均: 5.4, 最大: 10
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 62.0 行, 最大: 95 行
- 文件长度: 313 代码量 (347 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 4.8% (15/313)
- 命名规范: 发现 5 个违规

### 111. backend\common\neo4j_base.py

**糟糕指数: 7.83**

> 行数: 199 总计, 123 代码, 42 注释 | 函数: 11 | 类: 4

**问题**: 🏗️ 结构问题: 1, ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_check_connection` | L100-128 | 29 | 6 | 3 | 1 | ✓ |
| `reset_connection_state` | L63-72 | 10 | 3 | 2 | 1 | ✓ |
| `_get_driver` | L153-167 | 15 | 3 | 1 | 1 | ✓ |
| `_warn_fallback` | L77-85 | 9 | 2 | 1 | 2 | ✓ |
| `is_available` | L91-95 | 5 | 2 | 1 | 1 | ✓ |
| `_ensure_available` | L133-138 | 6 | 2 | 1 | 1 | ✓ |
| `close` | L193-198 | 6 | 2 | 1 | 1 | ✓ |
| `__init__` | L55-58 | 4 | 1 | 0 | 1 | ✓ |
| `_build_query` | L144-148 | 5 | 1 | 0 | 1 | ✓ |
| `get_driver` | L172-174 | 3 | 1 | 0 | 1 | ✓ |
| `_resolve_point_course_id` | L180-188 | 9 | 1 | 0 | 1 | ✓ |

**全部问题 (12)**

- 🏗️ `_check_connection()` L100: 中等嵌套: 3
- ❌ L68: 未处理的易出错调用
- ❌ L124: 未处理的易出错调用
- ❌ L193: 未处理的易出错调用
- ❌ L197: 未处理的易出错调用
- 🏷️ `__init__()` L55: "__init__" - snake_case
- 🏷️ `_warn_fallback()` L77: "_warn_fallback" - snake_case
- 🏷️ `_check_connection()` L100: "_check_connection" - snake_case
- 🏷️ `_ensure_available()` L133: "_ensure_available" - snake_case
- 🏷️ `_build_query()` L144: "_build_query" - snake_case
- 🏷️ `_get_driver()` L153: "_get_driver" - snake_case
- 🏷️ `_resolve_point_course_id()` L180: "_resolve_point_course_id" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 6
- 认知复杂度: 平均: 4.0, 最大: 12
- 嵌套深度: 平均: 0.9, 最大: 3
- 函数长度: 平均: 9.2 行, 最大: 29 行
- 文件长度: 123 代码量 (199 总计)
- 参数数量: 平均: 1.1, 最大: 2
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 1 个结构问题
- 错误处理: 4/4 个错误被忽略 (100.0%)
- 注释比例: 34.1% (42/123)
- 命名规范: 发现 7 个违规

### 112. frontend\scripts\browser-audit\session.mjs

**糟糕指数: 7.80**

> 行数: 72 总计, 64 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `slugifyRoute` | L3-5 | 3 | 1 | 0 | 1 | ✗ |
| `createBrowserSession` | L7-51 | 16 | 1 | 0 | 2 | ✗ |
| `captureRoute` | L53-62 | 10 | 1 | 0 | 4 | ✗ |
| `captureCurrentPage` | L64-71 | 8 | 1 | 0 | 3 | ✗ |

**全部问题 (1)**

- ❌ L20: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 9.3 行, 最大: 16 行
- 文件长度: 64 代码量 (72 总计)
- 参数数量: 平均: 2.5, 最大: 4
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/64)
- 命名规范: 无命名违规

### 113. backend\platform_ai\rag\student_answer_support.py

**糟糕指数: 7.80**

> 行数: 539 总计, 386 代码, 81 注释 | 函数: 22 | 类: 5

**问题**: ⚠️ 其他问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_point_name_map` | L112-122 | 11 | 5 | 2 | 1 | ✓ |
| `_entity_knowledge_point_id` | L128-137 | 10 | 4 | 1 | 1 | ✓ |
| `build_graph_fallback_answer` | L315-331 | 17 | 4 | 0 | 2 | ✓ |
| `build_course_graph_focus` | L143-156 | 14 | 3 | 0 | 2 | ✓ |
| `build_course_fallback_answer` | L337-356 | 20 | 3 | 0 | 2 | ✓ |
| `build_graph_answer_prompt` | L362-394 | 33 | 3 | 0 | 3 | ✓ |
| `resolve_course_answer_candidates` | L240-258 | 19 | 2 | 1 | 4 | ✓ |
| `query_graph_bundle` | L289-309 | 21 | 2 | 1 | 6 | ✓ |
| `build_course_answer_prompt` | L400-435 | 36 | 2 | 0 | 3 | ✓ |
| `call_llm_answer` | L441-457 | 17 | 2 | 1 | 4 | ✓ |
| `graph_answer_without_llm` | L463-470 | 8 | 2 | 0 | 1 | ✓ |
| `graph_answer_with_llm` | L494-506 | 13 | 2 | 0 | 2 | ✓ |
| `call_with_fallback` | L39-46 | 8 | 1 | 0 | 4 | ✓ |
| `query_graph` | L58-67 | 10 | 1 | 0 | 6 | ✓ |
| `combine_answer_context` | L162-174 | 13 | 1 | 0 | 2 | ✓ |
| `build_graph_answer_evidence` | L180-198 | 19 | 1 | 0 | 4 | ✓ |
| `build_course_answer_evidence` | L204-234 | 31 | 1 | 0 | 6 | ✓ |
| `_append_missing_point_names` | L264-275 | 12 | 1 | 0 | 3 | ✓ |
| `extract_source_titles` | L281-283 | 3 | 1 | 0 | 2 | ✓ |
| `course_answer_without_llm` | L476-488 | 13 | 1 | 0 | 2 | ✓ |
| `course_answer_with_llm` | L512-526 | 15 | 1 | 0 | 3 | ✓ |
| `normalize_answer_sources` | L532-538 | 7 | 1 | 0 | 3 | ✓ |

**全部问题 (9)**

- 📏 `query_graph()` L58: 6 参数数量
- 📏 `build_course_answer_evidence()` L204: 6 参数数量
- 📏 `query_graph_bundle()` L289: 6 参数数量
- ❌ L170: 未处理的易出错调用
- ❌ L171: 未处理的易出错调用
- ❌ L501: 未处理的易出错调用
- ❌ L505: 未处理的易出错调用
- ❌ L520: 未处理的易出错调用
- ❌ L524: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 5
- 认知复杂度: 平均: 2.5, 最大: 9
- 嵌套深度: 平均: 0.3, 最大: 2
- 函数长度: 平均: 15.9 行, 最大: 36 行
- 文件长度: 386 代码量 (539 总计)
- 参数数量: 平均: 3.0, 最大: 6
- 代码重复: 0.0% 重复 (0/22)
- 结构分析: 0 个结构问题
- 错误处理: 6/14 个错误被忽略 (42.9%)
- 注释比例: 21.0% (81/386)
- 命名规范: 发现 2 个违规

### 114. backend\wisdom_edu_api\settings.py

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

### 115. backend\tools\mefkt_training_support.py

**糟糕指数: 7.74**

> 行数: 414 总计, 341 代码, 39 注释 | 函数: 10 | 类: 3

**问题**: ⚠️ 其他问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `train_sequence_predictor` | L251-289 | 39 | 4 | 2 | 4 | ✓ |
| `pretrain_mefkt_embedding` | L165-198 | 34 | 3 | 1 | 3 | ✓ |
| `run_sequence_epoch` | L295-329 | 35 | 3 | 2 | 5 | ✓ |
| `write_mefkt_metadata` | L83-86 | 4 | 1 | 0 | 2 | ✓ |
| `train_mefkt_bundle` | L92-127 | 36 | 1 | 0 | 4 | ✓ |
| `build_mefkt_components` | L133-159 | 27 | 1 | 0 | 2 | ✓ |
| `run_pretrain_epoch` | L204-245 | 42 | 1 | 0 | 9 | ✓ |
| `cpu_state_dict` | L335-337 | 3 | 1 | 0 | 1 | ✓ |
| `build_mefkt_metadata` | L343-388 | 46 | 1 | 0 | 6 | ✓ |
| `save_mefkt_checkpoint` | L394-413 | 20 | 1 | 0 | 5 | ✓ |

**全部问题 (2)**

- 📏 `run_pretrain_epoch()` L204: 9 参数数量
- 📏 `build_mefkt_metadata()` L343: 6 参数数量

**详情**:
- 循环复杂度: 平均: 1.7, 最大: 4
- 认知复杂度: 平均: 2.7, 最大: 8
- 嵌套深度: 平均: 0.5, 最大: 2
- 函数长度: 平均: 28.6 行, 最大: 46 行
- 文件长度: 341 代码量 (414 总计)
- 参数数量: 平均: 4.1, 最大: 9
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 11.4% (39/341)
- 命名规范: 无命名违规

### 116. backend\tools\db_demo_preset_assessment.py

**糟糕指数: 7.64**

> 行数: 273 总计, 215 代码, 27 注释 | 函数: 8 | 类: 1

**问题**: ⚠️ 其他问题: 3, ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `persist_student1_question_answer` | L108-160 | 53 | 5 | 0 | 4 | ✓ |
| `build_student1_assessment_attempt` | L50-102 | 53 | 4 | 1 | 6 | ✓ |
| `update_student1_point_stats` | L166-176 | 11 | 3 | 2 | 3 | ✓ |
| `calculate_initial_mastery_baseline` | L32-44 | 13 | 2 | 1 | 4 | ✓ |
| `build_student1_mastery_map` | L182-201 | 20 | 2 | 1 | 5 | ✓ |
| `persist_student1_mastery` | L239-260 | 22 | 2 | 1 | 5 | ✓ |
| `persist_student1_assessment_result` | L207-233 | 27 | 1 | 0 | 4 | ✓ |
| `weakest_point_names` | L266-272 | 7 | 1 | 0 | 1 | ✓ |

**全部问题 (5)**

- 📏 `build_student1_assessment_attempt()` L50: 53 代码量
- 📏 `persist_student1_question_answer()` L108: 53 代码量
- 📏 `build_student1_assessment_attempt()` L50: 6 参数数量
- ❌ L152: 未处理的易出错调用
- ❌ L257: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 5
- 认知复杂度: 平均: 4.0, 最大: 7
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 25.8 行, 最大: 53 行
- 文件长度: 215 代码量 (273 总计)
- 参数数量: 平均: 4.0, 最大: 6
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 2/2 个错误被忽略 (100.0%)
- 注释比例: 12.6% (27/215)
- 命名规范: 无命名违规

### 117. backend\ai_services\services\mefkt_runtime.py

**糟糕指数: 7.64**

> 行数: 217 总计, 152 代码, 35 注释 | 函数: 10 | 类: 1

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 2, 🏷️ 命名问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_sorted_history_records` | L86-94 | 9 | 5 | 1 | 1 | ✓ |
| `_append_history_outcome` | L100-114 | 15 | 5 | 1 | 5 | ✓ |
| `_parse_timestamp` | L70-80 | 11 | 4 | 1 | 1 | ✓ |
| `_normalize_values` | L138-146 | 9 | 3 | 1 | 2 | ✓ |
| `_coerce_float` | L48-53 | 6 | 2 | 1 | 2 | ✓ |
| `_coerce_int` | L59-64 | 6 | 2 | 1 | 2 | ✓ |
| `_difficulty_to_score` | L160-166 | 7 | 2 | 0 | 1 | ✓ |
| `build_course_runtime_bundle` | L172-216 | 45 | 2 | 1 | 1 | ✓ |
| `_move_bundle_tensors_to_device` | L120-132 | 13 | 1 | 0 | 2 | ✓ |
| `_clamp` | L152-154 | 3 | 1 | 0 | 3 | ✓ |

**全部问题 (11)**

- ❌ L90: 未处理的易出错调用
- ❌ L166: 未处理的易出错调用
- 🏷️ `_coerce_float()` L48: "_coerce_float" - snake_case
- 🏷️ `_coerce_int()` L59: "_coerce_int" - snake_case
- 🏷️ `_parse_timestamp()` L70: "_parse_timestamp" - snake_case
- 🏷️ `_build_sorted_history_records()` L86: "_build_sorted_history_records" - snake_case
- 🏷️ `_append_history_outcome()` L100: "_append_history_outcome" - snake_case
- 🏷️ `_move_bundle_tensors_to_device()` L120: "_move_bundle_tensors_to_device" - snake_case
- 🏷️ `_normalize_values()` L138: "_normalize_values" - snake_case
- 🏷️ `_clamp()` L152: "_clamp" - snake_case
- 🏷️ `_difficulty_to_score()` L160: "_difficulty_to_score" - snake_case

**详情**:
- 循环复杂度: 平均: 2.7, 最大: 5
- 认知复杂度: 平均: 4.1, 最大: 7
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 12.4 行, 最大: 45 行
- 文件长度: 152 代码量 (217 总计)
- 参数数量: 平均: 2.0, 最大: 5
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 2/3 个错误被忽略 (66.7%)
- 注释比例: 23.0% (35/152)
- 命名规范: 发现 9 个违规

### 118. backend\tools\kt_synthetic_profile.py

**糟糕指数: 7.55**

> 行数: 190 总计, 154 代码, 17 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_children_map` | L17-27 | 11 | 5 | 3 | 2 | ✓ |
| `calculate_kp_depth` | L33-63 | 31 | 5 | 1 | 5 | ✓ |
| `compute_kp_difficulty` | L69-114 | 46 | 4 | 1 | 7 | ✓ |
| `build_kp_profile` | L120-160 | 41 | 3 | 0 | 6 | ✓ |
| `initialize_mastery_levels` | L166-180 | 15 | 2 | 1 | 3 | ✓ |

**全部问题 (6)**

- 📏 `compute_kp_difficulty()` L69: 7 参数数量
- 📏 `build_kp_profile()` L120: 6 参数数量
- 🏗️ `build_children_map()` L17: 中等嵌套: 3
- ❌ L149: 未处理的易出错调用
- ❌ L154: 未处理的易出错调用
- ❌ L156: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.8, 最大: 5
- 认知复杂度: 平均: 6.2, 最大: 11
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 28.8 行, 最大: 46 行
- 文件长度: 154 代码量 (190 总计)
- 参数数量: 平均: 4.6, 最大: 7
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 1 个结构问题
- 错误处理: 3/17 个错误被忽略 (17.6%)
- 注释比例: 11.0% (17/154)
- 命名规范: 无命名违规

### 119. backend\courses\teacher_class_views.py

**糟糕指数: 7.48**

> 行数: 205 总计, 158 代码, 24 注释 | 函数: 8 | 类: 0

**问题**: 🔄 复杂度问题: 4, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `class_update` | L64-94 | 31 | 11 | 2 | 2 | ✓ |
| `class_publish_course` | L116-137 | 22 | 9 | 1 | 2 | ✓ |
| `class_create` | L20-39 | 20 | 6 | 4 | 1 | ✓ |
| `teacher_class_progress` | L186-204 | 19 | 6 | 1 | 2 | ✓ |
| `class_unpublish_course` | L145-159 | 15 | 5 | 1 | 3 | ✓ |
| `class_delete` | L47-56 | 10 | 4 | 1 | 2 | ✓ |
| `class_courses` | L167-178 | 12 | 3 | 1 | 2 | ✓ |
| `my_classes` | L102-108 | 7 | 2 | 1 | 1 | ✓ |

**全部问题 (6)**

- 🔄 `class_update()` L64: 复杂度: 11
- 🔄 `class_create()` L20: 认知复杂度: 14
- 🔄 `class_update()` L64: 认知复杂度: 15
- 🔄 `class_create()` L20: 嵌套深度: 4
- 🏗️ `class_create()` L20: 中等嵌套: 4
- ❌ L55: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.8, 最大: 11
- 认知复杂度: 平均: 8.8, 最大: 15
- 嵌套深度: 平均: 1.5, 最大: 4
- 函数长度: 平均: 17.0 行, 最大: 31 行
- 文件长度: 158 代码量 (205 总计)
- 参数数量: 平均: 1.9, 最大: 3
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 1 个结构问题
- 错误处理: 1/15 个错误被忽略 (6.7%)
- 注释比例: 15.2% (24/158)
- 命名规范: 无命名违规

### 120. backend\knowledge\serializers.py

**糟糕指数: 7.34**

> 行数: 243 总计, 150 代码, 58 注释 | 函数: 6 | 类: 8

**问题**: 📋 重复问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_resources` | L99-127 | 29 | 6 | 3 | 1 | ✓ |
| `get_mastery_rate` | L54-63 | 10 | 4 | 1 | 2 | ✓ |
| `get_format` | L186-192 | 7 | 4 | 1 | 1 | ✓ |
| `get_duration_display` | L198-207 | 10 | 3 | 2 | 1 | ✓ |
| `get_prerequisites` | L69-78 | 10 | 1 | 0 | 1 | ✓ |
| `get_postrequisites` | L84-93 | 10 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 📋 `get_prerequisites()` L69: 重复模式: get_prerequisites, get_postrequisites
- 🏗️ `get_resources()` L99: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 3.2, 最大: 6
- 认知复杂度: 平均: 5.5, 最大: 12
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 12.7 行, 最大: 29 行
- 文件长度: 150 代码量 (243 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 16.7% 重复 (1/6)
- 结构分析: 1 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 38.7% (58/150)
- 命名规范: 无命名违规

### 121. backend\knowledge\map_support.py

**糟糕指数: 7.31**

> 行数: 474 总计, 378 代码, 54 注释 | 函数: 18 | 类: 0

**问题**: ⚠️ 其他问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_postgresql_knowledge_map_payload` | L32-72 | 41 | 8 | 0 | 2 | ✓ |
| `build_mastery_payload` | L361-399 | 39 | 6 | 0 | 2 | ✓ |
| `resolve_resource_url` | L439-454 | 16 | 6 | 2 | 2 | ✓ |
| `build_point_detail_payload` | L202-233 | 32 | 5 | 0 | 7 | ✓ |
| `build_mastery_lookup` | L15-26 | 12 | 4 | 2 | 2 | ✓ |
| `build_resource_payload` | L174-196 | 23 | 4 | 2 | 2 | ✓ |
| `build_neo4j_knowledge_map_payload` | L78-117 | 40 | 3 | 1 | 3 | ✓ |
| `build_knowledge_map_response_payload` | L123-150 | 28 | 3 | 0 | 4 | ✓ |
| `build_postgresql_points_payload` | L327-355 | 29 | 3 | 1 | 3 | ✓ |
| `mapping_records` | L429-433 | 5 | 3 | 1 | 1 | ✓ |
| `build_neo4j_points_payload` | L295-321 | 27 | 2 | 1 | 2 | ✓ |
| `read_mastery_rate` | L421-423 | 3 | 2 | 0 | 2 | ✓ |
| `build_postgresql_point_relations` | L156-168 | 13 | 1 | 0 | 1 | ✓ |
| `build_neo4j_relations_payload` | L239-261 | 23 | 1 | 0 | 2 | ✓ |
| `build_postgresql_relations_payload` | L267-289 | 23 | 1 | 0 | 1 | ✓ |
| `normalize_relation_records` | L405-407 | 3 | 1 | 0 | 1 | ✓ |
| `read_mapping_field` | L413-415 | 3 | 1 | 0 | 3 | ✓ |
| `build_collection_payload` | L460-473 | 14 | 1 | 0 | 4 | ✓ |

**全部问题 (1)**

- 📏 `build_point_detail_payload()` L202: 7 参数数量

**详情**:
- 循环复杂度: 平均: 3.1, 最大: 8
- 认知复杂度: 平均: 4.2, 最大: 10
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 20.8 行, 最大: 41 行
- 文件长度: 378 代码量 (474 总计)
- 参数数量: 平均: 2.4, 最大: 7
- 代码重复: 0.0% 重复 (0/18)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 14.3% (54/378)
- 命名规范: 无命名违规

### 122. backend\ai_services\test_student_ai_multicourse.py

**糟糕指数: 7.30**

> 行数: 406 总计, 316 代码, 48 注释 | 函数: 14 | 类: 4

**问题**: ⚠️ 其他问题: 3, 📋 重复问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `post` | L270-295 | 26 | 2 | 1 | 5 | ✓ |
| `setUp` | L43-80 | 38 | 1 | 0 | 1 | ✓ |
| `test_graph_rag_search_should_only_return_points_from_selected_course` | L85-96 | 12 | 1 | 0 | 1 | ✓ |
| `test_graph_rag_search_should_surface_runtime_supporting_sources` | L102-122 | 21 | 1 | 0 | 2 | ✓ |
| `test_graph_rag_search_should_match_point_names_inside_full_sentence` | L127-137 | 11 | 1 | 0 | 1 | ✓ |
| `test_graph_rag_ask_should_route_structure_question_without_point` | L143-173 | 31 | 1 | 0 | 2 | ✓ |
| `test_graph_rag_ask_endpoint_should_surface_runtime_modes` | L179-213 | 35 | 1 | 0 | 2 | ✓ |
| `test_ai_resource_reason_should_reject_cross_course_resource_requests` | L218-231 | 14 | 1 | 0 | 1 | ✓ |
| `__init__` | L240-241 | 2 | 1 | 0 | 2 | ✗ |
| `raise_for_status` | L246-247 | 2 | 1 | 0 | 1 | ✓ |
| `json` | L252-255 | 4 | 1 | 0 | 1 | ✓ |
| `__init__` | L264-265 | 2 | 1 | 0 | 1 | ✗ |
| `test_external_resource_mcp_should_search_exa_and_enrich_with_firecrawl` | L321-343 | 23 | 1 | 0 | 1 | ✓ |
| `test_node_resource_recommendation_should_prefer_mcp_external_results` | L351-405 | 55 | 1 | 0 | 4 | ✓ |

**全部问题 (9)**

- 📏 `test_node_resource_recommendation_should_prefer_mcp_external_results()` L351: 55 代码量
- 📋 `test_graph_rag_search_should_only_return_points_from_selected_course()` L85: 重复模式: test_graph_rag_search_should_only_return_points_from_selected_course, test_graph_rag_search_should_surface_runtime_supporting_sources
- 📋 `test_graph_rag_search_should_match_point_names_inside_full_sentence()` L127: 重复模式: test_graph_rag_search_should_match_point_names_inside_full_sentence, test_graph_rag_ask_should_route_structure_question_without_point
- ❌ L270: 未处理的易出错调用
- 🏷️ `setUp()` L43: "setUp" - snake_case
- 🏷️ `__init__()` L240: "__init__" - snake_case
- 🏷️ `__init__()` L264: "__init__" - snake_case
- 🏷️ L237: "_MCPStubResponse" - PascalCase
- 🏷️ L261: "_MCPStubSession" - PascalCase

**详情**:
- 循环复杂度: 平均: 1.1, 最大: 2
- 认知复杂度: 平均: 1.2, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 19.7 行, 最大: 55 行
- 文件长度: 316 代码量 (406 总计)
- 参数数量: 平均: 1.8, 最大: 5
- 代码重复: 14.3% 重复 (2/14)
- 结构分析: 0 个结构问题
- 错误处理: 1/8 个错误被忽略 (12.5%)
- 注释比例: 15.2% (48/316)
- 命名规范: 发现 5 个违规

### 123. backend\platform_ai\rag\student_index_mixin.py

**糟糕指数: 7.29**

> 行数: 154 总计, 103 代码, 33 注释 | 函数: 10 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_index` | L22-46 | 25 | 6 | 2 | 4 | ✓ |
| `_entity_to_communities` | L139-153 | 15 | 6 | 3 | 2 | ✓ |
| `_ensure_index` | L51-60 | 10 | 4 | 2 | 3 | ✓ |
| `_entity_map` | L115-122 | 8 | 3 | 2 | 2 | ✓ |
| `_community_lookup` | L127-134 | 8 | 3 | 2 | 2 | ✓ |
| `_entity_list` | L65-70 | 6 | 2 | 1 | 2 | ✓ |
| `_relationship_list` | L75-80 | 6 | 2 | 1 | 2 | ✓ |
| `_document_list` | L85-90 | 6 | 2 | 1 | 2 | ✓ |
| `_community_list` | L95-100 | 6 | 2 | 1 | 2 | ✓ |
| `_community_report_list` | L105-110 | 6 | 2 | 1 | 2 | ✓ |

**全部问题 (11)**

- 📋 `_entity_map()` L115: 重复模式: _entity_map, _community_lookup
- 🏗️ `_entity_to_communities()` L139: 中等嵌套: 3
- 🏷️ `_ensure_index()` L51: "_ensure_index" - snake_case
- 🏷️ `_entity_list()` L65: "_entity_list" - snake_case
- 🏷️ `_relationship_list()` L75: "_relationship_list" - snake_case
- 🏷️ `_document_list()` L85: "_document_list" - snake_case
- 🏷️ `_community_list()` L95: "_community_list" - snake_case
- 🏷️ `_community_report_list()` L105: "_community_report_list" - snake_case
- 🏷️ `_entity_map()` L115: "_entity_map" - snake_case
- 🏷️ `_community_lookup()` L127: "_community_lookup" - snake_case
- 🏷️ `_entity_to_communities()` L139: "_entity_to_communities" - snake_case

**详情**:
- 循环复杂度: 平均: 3.2, 最大: 6
- 认知复杂度: 平均: 6.4, 最大: 12
- 嵌套深度: 平均: 1.6, 最大: 3
- 函数长度: 平均: 9.6 行, 最大: 25 行
- 文件长度: 103 代码量 (154 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 10.0% 重复 (1/10)
- 结构分析: 1 个结构问题
- 错误处理: 0/11 个错误被忽略 (0.0%)
- 注释比例: 32.0% (33/103)
- 命名规范: 发现 9 个违规

### 124. backend\learning\stage_test_selection.py

**糟糕指数: 7.03**

> 行数: 310 总计, 222 代码, 48 注释 | 函数: 16 | 类: 0

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 4, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_stage_knowledge_point_ids` | L46-69 | 24 | 4 | 1 | 1 | ✓ |
| `_pick_stage_questions_with_llm` | L172-194 | 23 | 4 | 2 | 3 | ✓ |
| `_serialize_stage_options` | L300-309 | 10 | 4 | 0 | 1 | ✓ |
| `_questions_from_bank` | L122-138 | 17 | 3 | 1 | 3 | ✓ |
| `_stage_test_result` | L230-235 | 6 | 3 | 1 | 1 | ✓ |
| `build_stage_test_payload` | L22-40 | 19 | 2 | 1 | 2 | ✓ |
| `_select_stage_questions` | L75-84 | 10 | 2 | 1 | 3 | ✓ |
| `_resolve_stage_exam` | L90-103 | 14 | 2 | 1 | 2 | ✓ |
| `_knowledge_point_names` | L216-224 | 9 | 2 | 0 | 1 | ✓ |
| `_serialize_stage_question` | L275-294 | 20 | 2 | 1 | 3 | ✓ |
| `_questions_from_exam` | L109-116 | 8 | 1 | 0 | 1 | ✓ |
| `_candidate_questions` | L144-154 | 11 | 1 | 0 | 2 | ✓ |
| `_course_questions` | L160-166 | 7 | 1 | 0 | 1 | ✓ |
| `_candidate_info` | L200-210 | 11 | 1 | 0 | 1 | ✓ |
| `_empty_stage_test_payload` | L241-250 | 10 | 1 | 0 | 2 | ✓ |
| `_serialize_stage_questions` | L256-269 | 14 | 1 | 0 | 2 | ✓ |

**全部问题 (15)**

- 📋 `build_stage_test_payload()` L22: 重复模式: build_stage_test_payload, _questions_from_bank
- ❌ L286: 未处理的易出错调用
- ❌ L304: 未处理的易出错调用
- ❌ L305: 未处理的易出错调用
- ❌ L306: 未处理的易出错调用
- 🏷️ `_stage_knowledge_point_ids()` L46: "_stage_knowledge_point_ids" - snake_case
- 🏷️ `_select_stage_questions()` L75: "_select_stage_questions" - snake_case
- 🏷️ `_resolve_stage_exam()` L90: "_resolve_stage_exam" - snake_case
- 🏷️ `_questions_from_exam()` L109: "_questions_from_exam" - snake_case
- 🏷️ `_questions_from_bank()` L122: "_questions_from_bank" - snake_case
- 🏷️ `_candidate_questions()` L144: "_candidate_questions" - snake_case
- 🏷️ `_course_questions()` L160: "_course_questions" - snake_case
- 🏷️ `_pick_stage_questions_with_llm()` L172: "_pick_stage_questions_with_llm" - snake_case
- 🏷️ `_candidate_info()` L200: "_candidate_info" - snake_case
- 🏷️ `_knowledge_point_names()` L216: "_knowledge_point_names" - snake_case

**详情**:
- 循环复杂度: 平均: 2.1, 最大: 4
- 认知复杂度: 平均: 3.3, 最大: 8
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 13.3 行, 最大: 24 行
- 文件长度: 222 代码量 (310 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 6.3% 重复 (1/16)
- 结构分析: 0 个结构问题
- 错误处理: 4/5 个错误被忽略 (80.0%)
- 注释比例: 21.6% (48/222)
- 命名规范: 发现 15 个违规

### 125. backend\ai_services\consumers.py

**糟糕指数: 7.01**

> 行数: 87 总计, 59 代码, 13 注释 | 函数: 3 | 类: 1

**问题**: 🔄 复杂度问题: 1, ❌ 错误处理问题: 5, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `receive_json` | L47-86 | 40 | 9 | 2 | 2 | ✓ |
| `connect` | L35-42 | 8 | 3 | 1 | 1 | ✓ |
| `_split_reply_chunks` | L16-23 | 8 | 2 | 1 | 2 | ✓ |

**全部问题 (7)**

- 🔄 `receive_json()` L47: 认知复杂度: 13
- ❌ L35: 未处理的易出错调用
- ❌ L41: 未处理的易出错调用
- ❌ L78: 未处理的易出错调用
- ❌ L79: 未处理的易出错调用
- ❌ L80: 未处理的易出错调用
- 🏷️ `_split_reply_chunks()` L16: "_split_reply_chunks" - snake_case

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 9
- 认知复杂度: 平均: 7.3, 最大: 13
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 18.7 行, 最大: 40 行
- 文件长度: 59 代码量 (87 总计)
- 参数数量: 平均: 1.7, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 5/13 个错误被忽略 (38.5%)
- 注释比例: 22.0% (13/59)
- 命名规范: 发现 1 个违规

### 126. backend\platform_ai\llm\agent_graphrag.py

**糟糕指数: 6.97**

> 行数: 315 总计, 223 代码, 48 注释 | 函数: 16 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `trim_graph_sources` | L16-27 | 12 | 5 | 2 | 2 | ✓ |
| `build_point_graphrag_payload` | L56-66 | 11 | 4 | 1 | 2 | ✓ |
| `build_lookup_course_context_payload` | L252-266 | 15 | 4 | 1 | 2 | ✓ |
| `build_point_context_payload` | L284-302 | 19 | 4 | 1 | 3 | ✓ |
| `normalize_graph_source` | L33-42 | 10 | 3 | 0 | 1 | ✓ |
| `fetch_point_support_payload` | L72-89 | 18 | 3 | 1 | 2 | ✓ |
| `resolve_point_name` | L128-133 | 6 | 3 | 1 | 2 | ✓ |
| `query_course_graph` | L163-190 | 28 | 3 | 1 | 5 | ✓ |
| `clean_positive_ids` | L242-246 | 5 | 3 | 1 | 1 | ✓ |
| `build_course_graphrag_payload` | L95-122 | 28 | 2 | 1 | 4 | ✓ |
| `clean_string_list` | L232-236 | 5 | 2 | 1 | 1 | ✓ |
| `clean_source_field` | L48-50 | 3 | 1 | 0 | 2 | ✓ |
| `empty_course_graphrag_payload` | L139-157 | 19 | 1 | 0 | 3 | ✓ |
| `normalize_course_graphrag_payload` | L196-218 | 23 | 1 | 0 | 6 | ✓ |
| `clean_payload_text` | L224-226 | 3 | 1 | 0 | 2 | ✓ |
| `build_missing_point_payload` | L272-278 | 7 | 1 | 0 | 1 | ✓ |

**全部问题 (6)**

- 📏 `normalize_course_graphrag_payload()` L196: 6 参数数量
- ❌ L60: 未处理的易出错调用
- ❌ L64: 未处理的易出错调用
- ❌ L212: 未处理的易出错调用
- ❌ L213: 未处理的易出错调用
- ❌ L217: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 5
- 认知复杂度: 平均: 3.9, 最大: 9
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 13.3 行, 最大: 28 行
- 文件长度: 223 代码量 (315 总计)
- 参数数量: 平均: 2.4, 最大: 6
- 代码重复: 0.0% 重复 (0/16)
- 结构分析: 0 个结构问题
- 错误处理: 5/10 个错误被忽略 (50.0%)
- 注释比例: 21.5% (48/223)
- 命名规范: 无命名违规

### 127. backend\logs\descriptions.py

**糟糕指数: 6.94**

> 行数: 116 总计, 83 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 2, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_operation_description` | L66-101 | 36 | 12 | 1 | 3 | ✓ |
| `_match_fixed_description` | L107-112 | 6 | 3 | 2 | 2 | ✓ |
| `_contains_with_method` | L26-28 | 3 | 2 | 0 | 2 | ✓ |
| `_contains` | L18-20 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (5)**

- 🔄 `generate_operation_description()` L66: 复杂度: 12
- 🔄 `generate_operation_description()` L66: 认知复杂度: 14
- 🏷️ `_contains()` L18: "_contains" - snake_case
- 🏷️ `_contains_with_method()` L26: "_contains_with_method" - snake_case
- 🏷️ `_match_fixed_description()` L107: "_match_fixed_description" - snake_case

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 12
- 认知复杂度: 平均: 6.0, 最大: 14
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 12.0 行, 最大: 36 行
- 文件长度: 83 代码量 (116 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 14.5% (12/83)
- 命名规范: 发现 3 个违规

### 128. backend\ai_services\test_kt_models.py

**糟糕指数: 6.87**

> 行数: 474 总计, 388 代码, 41 注释 | 函数: 10 | 类: 3

**问题**: ⚠️ 其他问题: 3, 📋 重复问题: 1, 🏗️ 结构问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_mefkt_predictor_should_load_checkpoint_and_return_predictions` | L64-123 | 60 | 3 | 2 | 1 | ✓ |
| `test_mefkt_predictor_should_support_question_online_runtime` | L128-256 | 129 | 3 | 2 | 1 | ✓ |
| `test_predict_mastery_should_degrade_gracefully_on_model_name_error` | L293-322 | 30 | 2 | 1 | 1 | ✓ |
| `test_predict_mastery_should_return_course_defaults_without_history` | L327-351 | 25 | 2 | 1 | 1 | ✓ |
| `test_kt_service_model_info_should_expose_mefkt_config` | L43-59 | 17 | 1 | 0 | 1 | ✓ |
| `test_mefkt_perceived_distance_should_increase_with_longer_gap` | L261-281 | 21 | 1 | 0 | 1 | ✓ |
| `setUp` | L363-412 | 50 | 1 | 0 | 1 | ✓ |
| `_profile` | L417-431 | 15 | 1 | 0 | 3 | ✓ |
| `test_kp_profile_should_reflect_prerequisite_depth_and_item_difficulty` | L436-442 | 7 | 1 | 0 | 1 | ✓ |
| `test_simulated_sequences_should_show_ability_gap_and_revisits` | L447-473 | 27 | 1 | 0 | 1 | ✓ |

**全部问题 (6)**

- 📏 `test_mefkt_predictor_should_load_checkpoint_and_return_predictions()` L64: 60 代码量
- 📏 `test_mefkt_predictor_should_support_question_online_runtime()` L128: 129 代码量
- 📋 `test_mefkt_predictor_should_load_checkpoint_and_return_predictions()` L64: 重复模式: test_mefkt_predictor_should_load_checkpoint_and_return_predictions, test_simulated_sequences_should_show_ability_gap_and_revisits
- 🏗️ L1: 导入过多: 32
- 🏷️ `setUp()` L363: "setUp" - snake_case
- 🏷️ `_profile()` L417: "_profile" - snake_case

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 3
- 认知复杂度: 平均: 2.8, 最大: 7
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 38.1 行, 最大: 129 行
- 文件长度: 388 代码量 (474 总计)
- 参数数量: 平均: 1.2, 最大: 3
- 代码重复: 10.0% 重复 (1/10)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 10.6% (41/388)
- 命名规范: 发现 2 个违规

### 129. backend\courses\teacher_course_support.py

**糟糕指数: 6.83**

> 行数: 479 总计, 311 代码, 93 注释 | 函数: 30 | 类: 1

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `create_teacher_course` | L88-128 | 41 | 9 | 3 | 3 | ✓ |
| `resolve_publish_class` | L134-147 | 14 | 5 | 1 | 2 | ✓ |
| `update_course_config` | L437-451 | 15 | 5 | 1 | 2 | ✓ |
| `build_course_detail_payload` | L222-234 | 13 | 4 | 0 | 1 | ✓ |
| `update_teacher_course` | L240-247 | 8 | 4 | 2 | 2 | ✓ |
| `delete_teacher_course` | L306-317 | 12 | 4 | 1 | 2 | ✓ |
| `update_course_settings_for_user` | L468-478 | 11 | 4 | 1 | 3 | ✓ |
| `build_course_search_item` | L73-82 | 10 | 3 | 0 | 1 | ✓ |
| `bootstrap_course_archive` | L153-176 | 24 | 3 | 1 | 3 | ✓ |
| `publish_course_to_class` | L182-195 | 14 | 3 | 1 | 3 | ✓ |
| `cleanup_course_archive` | L201-208 | 8 | 3 | 1 | 1 | ✓ |
| `apply_legacy_course_fields` | L253-261 | 9 | 3 | 2 | 2 | ✓ |
| `can_delete_course` | L290-292 | 3 | 3 | 0 | 2 | ✓ |
| `get_owned_course` | L323-330 | 8 | 3 | 1 | 3 | ✓ |
| `upload_teacher_course_cover` | L336-345 | 10 | 3 | 1 | 3 | ✓ |
| `save_course_cover` | L351-360 | 10 | 3 | 1 | 3 | ✓ |
| `write_course_cover_file` | L366-375 | 10 | 3 | 2 | 2 | ✓ |
| `build_course_statistics_for_user` | L405-410 | 6 | 3 | 1 | 2 | ✓ |
| `build_course_settings_for_user` | L457-462 | 6 | 3 | 1 | 2 | ✓ |
| `build_course_search_payload` | L39-54 | 16 | 2 | 1 | 1 | ✓ |
| `parse_course_pagination` | L60-67 | 8 | 2 | 1 | 1 | ✓ |
| `can_access_owned_course` | L298-300 | 3 | 2 | 0 | 2 | ✓ |
| `merged_course_config` | L425-431 | 7 | 2 | 1 | 1 | ✓ |
| `chunks` | L32-33 | 2 | 1 | 0 | 1 | ✓ |
| `get_teacher_course` | L214-216 | 3 | 1 | 0 | 1 | ✓ |
| `build_my_created_courses_payload` | L267-270 | 4 | 1 | 0 | 1 | ✓ |
| `build_my_course_item` | L276-284 | 9 | 1 | 0 | 1 | ✓ |
| `build_course_statistics_payload` | L381-390 | 10 | 1 | 0 | 1 | ✓ |
| `course_student_ids` | L396-399 | 4 | 1 | 0 | 1 | ✓ |
| `build_course_settings_payload` | L416-419 | 4 | 1 | 0 | 1 | ✓ |

**全部问题 (5)**

- 🔄 `create_teacher_course()` L88: 认知复杂度: 15
- 🏗️ `create_teacher_course()` L88: 中等嵌套: 3
- ❌ L314: 未处理的易出错调用
- ❌ L372: 未处理的易出错调用
- ❌ L374: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.9, 最大: 9
- 认知复杂度: 平均: 4.5, 最大: 15
- 嵌套深度: 平均: 0.8, 最大: 3
- 函数长度: 平均: 10.1 行, 最大: 41 行
- 文件长度: 311 代码量 (479 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/30)
- 结构分析: 1 个结构问题
- 错误处理: 3/11 个错误被忽略 (27.3%)
- 注释比例: 29.9% (93/311)
- 命名规范: 无命名违规

### 130. frontend\src\views\student\useExamTaking.js

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

### 131. backend\users\teacher_profile_support.py

**糟糕指数: 6.74**

> 行数: 200 总计, 137 代码, 33 注释 | 函数: 11 | 类: 0

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 4, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `resolve_profile_course_id` | L27-45 | 19 | 4 | 1 | 2 | ✓ |
| `ensure_teacher_can_view_student` | L51-63 | 13 | 3 | 1 | 3 | ✓ |
| `_build_ability_scores` | L108-113 | 6 | 3 | 1 | 2 | ✓ |
| `_average_history_mastery` | L157-161 | 5 | 3 | 1 | 1 | ✓ |
| `resolve_student_for_teacher_profile` | L16-21 | 6 | 2 | 1 | 1 | ✓ |
| `_build_habit_preferences` | L119-131 | 13 | 2 | 1 | 1 | ✓ |
| `_build_answer_stats` | L167-178 | 12 | 2 | 0 | 2 | ✓ |
| `build_profile_refresh_payload` | L184-199 | 16 | 2 | 1 | 2 | ✓ |
| `build_student_profile_payload` | L69-82 | 14 | 1 | 0 | 2 | ✓ |
| `_build_mastery_list` | L88-102 | 15 | 1 | 0 | 2 | ✓ |
| `_build_profile_history` | L137-151 | 15 | 1 | 0 | 2 | ✓ |

**全部问题 (11)**

- 📋 `_build_mastery_list()` L88: 重复模式: _build_mastery_list, _build_profile_history
- ❌ L190: 未处理的易出错调用
- ❌ L192: 未处理的易出错调用
- ❌ L193: 未处理的易出错调用
- ❌ L194: 未处理的易出错调用
- 🏷️ `_build_mastery_list()` L88: "_build_mastery_list" - snake_case
- 🏷️ `_build_ability_scores()` L108: "_build_ability_scores" - snake_case
- 🏷️ `_build_habit_preferences()` L119: "_build_habit_preferences" - snake_case
- 🏷️ `_build_profile_history()` L137: "_build_profile_history" - snake_case
- 🏷️ `_average_history_mastery()` L157: "_average_history_mastery" - snake_case
- 🏷️ `_build_answer_stats()` L167: "_build_answer_stats" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 4
- 认知复杂度: 平均: 3.5, 最大: 6
- 嵌套深度: 平均: 0.6, 最大: 1
- 函数长度: 平均: 12.2 行, 最大: 19 行
- 文件长度: 137 代码量 (200 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 9.1% 重复 (1/11)
- 结构分析: 0 个结构问题
- 错误处理: 4/6 个错误被忽略 (66.7%)
- 注释比例: 24.1% (33/137)
- 命名规范: 发现 6 个违规

### 132. frontend\src\api\index.ts

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

### 133. backend\learning\stage_test_evaluation.py

**糟糕指数: 6.71**

> 行数: 241 总计, 194 代码, 24 注释 | 函数: 8 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 11

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `mistake_detail` | L223-240 | 18 | 7 | 0 | 2 | ✓ |
| `build_single_question_detail` | L144-202 | 59 | 4 | 0 | 5 | ✓ |
| `question_ids_from_answers` | L74-82 | 9 | 3 | 2 | 1 | ✓ |
| `evaluate_stage_test` | L29-68 | 40 | 2 | 0 | 3 | ✓ |
| `build_question_details` | L118-138 | 21 | 2 | 1 | 5 | ✓ |
| `question_map_for_node` | L88-96 | 9 | 1 | 0 | 2 | ✓ |
| `grade_stage_questions` | L102-112 | 11 | 1 | 0 | 2 | ✓ |
| `build_detailed_mistakes` | L208-217 | 10 | 1 | 0 | 2 | ✓ |

**全部问题 (12)**

- 📏 `build_single_question_detail()` L144: 59 代码量
- ❌ L167: 未处理的易出错调用
- ❌ L194: 未处理的易出错调用
- ❌ L200: 未处理的易出错调用
- ❌ L201: 未处理的易出错调用
- ❌ L214: 未处理的易出错调用
- ❌ L234: 未处理的易出错调用
- ❌ L235: 未处理的易出错调用
- ❌ L236: 未处理的易出错调用
- ❌ L237: 未处理的易出错调用
- ❌ L238: 未处理的易出错调用
- ❌ L239: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 7
- 认知复杂度: 平均: 3.4, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 22.1 行, 最大: 59 行
- 文件长度: 194 代码量 (241 总计)
- 参数数量: 平均: 2.8, 最大: 5
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 11/16 个错误被忽略 (68.8%)
- 注释比例: 12.4% (24/194)
- 命名规范: 无命名违规

### 134. backend\tools\rebuild_demo_support.py

**糟糕指数: 6.63**

> 行数: 212 总计, 162 代码, 27 注释 | 函数: 9 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, ❌ 错误处理问题: 2, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `print_assistant_demo_queries` | L112-136 | 25 | 10 | 2 | 1 | ✓ |
| `sync_demo_course_runtime` | L46-60 | 15 | 3 | 1 | 2 | ✓ |
| `assert_demo_graph_ready` | L66-74 | 9 | 3 | 1 | 3 | ✓ |
| `print_demo_user_statuses` | L175-200 | 26 | 3 | 2 | 2 | ✓ |
| `iter_demo_usernames` | L27-32 | 6 | 2 | 1 | 0 | ✓ |
| `print_demo_course_summary` | L80-106 | 27 | 2 | 1 | 5 | ✓ |
| `_user_course_status` | L142-169 | 28 | 2 | 0 | 3 | ✓ |
| `load_demo_course` | L38-40 | 3 | 1 | 0 | 1 | ✓ |
| `print_demo_followup_hint` | L206-211 | 6 | 1 | 0 | 0 | ✓ |

**全部问题 (4)**

- 🔄 `print_assistant_demo_queries()` L112: 认知复杂度: 14
- ❌ L115: 未处理的易出错调用
- ❌ L120: 未处理的易出错调用
- 🏷️ `_user_course_status()` L142: "_user_course_status" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 10
- 认知复杂度: 平均: 4.8, 最大: 14
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 16.1 行, 最大: 28 行
- 文件长度: 162 代码量 (212 总计)
- 参数数量: 平均: 1.9, 最大: 5
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 2/11 个错误被忽略 (18.2%)
- 注释比例: 16.7% (27/162)
- 命名规范: 发现 1 个违规

### 135. backend\ai_services\kt_views.py

**糟糕指数: 6.50**

> 行数: 109 总计, 82 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 📋 重复问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `kt_predict` | L23-46 | 24 | 4 | 1 | 1 | ✓ |
| `kt_recommendations` | L86-108 | 23 | 4 | 1 | 1 | ✓ |
| `kt_batch_predict` | L64-78 | 15 | 3 | 1 | 1 | ✓ |
| `kt_model_info` | L54-56 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- 📋 `kt_predict()` L23: 重复模式: kt_predict, kt_recommendations

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 4
- 认知复杂度: 平均: 4.5, 最大: 6
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 16.3 行, 最大: 24 行
- 文件长度: 82 代码量 (109 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 25.0% 重复 (1/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/7 个错误被忽略 (0.0%)
- 注释比例: 14.6% (12/82)
- 命名规范: 无命名违规

### 136. backend\exams\student_helpers.py

**糟糕指数: 6.49**

> 行数: 343 总计, 244 代码, 54 注释 | 函数: 16 | 类: 2

**问题**: ❌ 错误处理问题: 9, 🏷️ 命名问题: 6

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_feedback_overview` | L292-306 | 15 | 10 | 0 | 1 | ✓ |
| `normalize_feedback_payload` | L169-198 | 30 | 8 | 0 | 2 | ✓ |
| `_extract_list_analysis` | L246-257 | 12 | 6 | 1 | 1 | ✓ |
| `resolve_pass_threshold` | L88-109 | 22 | 5 | 2 | 1 | ✓ |
| `_extract_analysis_text_and_gaps` | L230-240 | 11 | 5 | 1 | 1 | ✓ |
| `build_exam_score_map` | L115-120 | 6 | 4 | 0 | 2 | ✓ |
| `_normalize_feedback_text` | L212-224 | 13 | 4 | 1 | 2 | ✓ |
| `build_submission_feedback_snapshot` | L320-342 | 23 | 4 | 0 | 1 | ✓ |
| `build_question_detail` | L126-150 | 25 | 3 | 0 | 3 | ✓ |
| `build_exam_question_details` | L156-163 | 8 | 3 | 1 | 3 | ✓ |
| `_apply_question_detail_stats` | L272-286 | 15 | 3 | 1 | 2 | ✓ |
| `snapshot_mastery_for_points` | L59-66 | 8 | 2 | 1 | 3 | ✓ |
| `_normalized_overview` | L204-206 | 3 | 2 | 0 | 1 | ✓ |
| `build_mastery_change_payload` | L72-82 | 11 | 1 | 0 | 2 | ✓ |
| `_clean_text_list` | L263-266 | 4 | 1 | 0 | 1 | ✓ |
| `build_feedback_report_ref` | L312-314 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (15)**

- ❌ L78: 未处理的易出错调用
- ❌ L79: 未处理的易出错调用
- ❌ L80: 未处理的易出错调用
- ❌ L81: 未处理的易出错调用
- ❌ L146: 未处理的易出错调用
- ❌ L148: 未处理的易出错调用
- ❌ L149: 未处理的易出错调用
- ❌ L162: 未处理的易出错调用
- ❌ L252: 未处理的易出错调用
- 🏷️ `_normalized_overview()` L204: "_normalized_overview" - snake_case
- 🏷️ `_normalize_feedback_text()` L212: "_normalize_feedback_text" - snake_case
- 🏷️ `_extract_analysis_text_and_gaps()` L230: "_extract_analysis_text_and_gaps" - snake_case
- 🏷️ `_extract_list_analysis()` L246: "_extract_list_analysis" - snake_case
- 🏷️ `_clean_text_list()` L263: "_clean_text_list" - snake_case
- 🏷️ `_apply_question_detail_stats()` L272: "_apply_question_detail_stats" - snake_case

**详情**:
- 循环复杂度: 平均: 3.9, 最大: 10
- 认知复杂度: 平均: 4.9, 最大: 10
- 嵌套深度: 平均: 0.5, 最大: 2
- 函数长度: 平均: 13.1 行, 最大: 30 行
- 文件长度: 244 代码量 (343 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/16)
- 结构分析: 0 个结构问题
- 错误处理: 9/20 个错误被忽略 (45.0%)
- 注释比例: 22.1% (54/244)
- 命名规范: 发现 6 个违规

### 137. frontend\scripts\browser-audit\audit-scenario.mjs

**糟糕指数: 6.45**

> 行数: 83 总计, 72 代码, 0 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `auditRole` | L9-37 | 29 | 3 | 1 | 2 | ✗ |
| `runAuditScenario` | L39-82 | 44 | 2 | 1 | 2 | ✗ |

**全部问题 (1)**

- ❌ L36: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 3
- 认知复杂度: 平均: 4.5, 最大: 5
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 36.5 行, 最大: 44 行
- 文件长度: 72 代码量 (83 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 0.0% (0/72)
- 命名规范: 无命名违规

### 138. frontend\src\views\teacher\knowledgeManageModels.js

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

### 139. frontend\src\views\student\useStudentKnowledgeMap.js

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

### 140. frontend\src\views\student\knowledgeMapModels.js

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

### 141. backend\tools\diagnostics.py

**糟糕指数: 6.44**

> 行数: 237 总计, 147 代码, 45 注释 | 函数: 14 | 类: 0

**问题**: ❌ 错误处理问题: 4, 📝 注释问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_print_llm_section` | L161-172 | 12 | 5 | 0 | 0 | ✓ |
| `_print_migration_section` | L113-128 | 16 | 4 | 1 | 0 | ✓ |
| `_print_directory_section` | L62-70 | 9 | 3 | 0 | 0 | ✓ |
| `_print_database_section` | L87-96 | 10 | 3 | 1 | 0 | ✓ |
| `_first_configured_env` | L178-184 | 7 | 3 | 2 | 1 | ✓ |
| `_check_postgres` | L102-107 | 6 | 2 | 1 | 0 | ✓ |
| `_print_dependency_section` | L150-155 | 6 | 2 | 1 | 1 | ✓ |
| `_print_data_summary_section` | L190-206 | 17 | 2 | 1 | 0 | ✓ |
| `_mark` | L234-236 | 3 | 2 | 0 | 2 | ✓ |
| `diagnose_env` | L36-46 | 11 | 1 | 0 | 0 | ✓ |
| `_print_header` | L52-56 | 5 | 1 | 0 | 1 | ✓ |
| `_print_config_section` | L76-81 | 6 | 1 | 0 | 0 | ✓ |
| `_get_unapplied_migrations` | L134-144 | 11 | 1 | 0 | 0 | ✓ |
| `_collect_data_summary` | L212-228 | 17 | 1 | 0 | 0 | ✓ |

**全部问题 (14)**

- ❌ L107: 未处理的易出错调用
- ❌ L167: 未处理的易出错调用
- ❌ L168: 未处理的易出错调用
- ❌ L171: 未处理的易出错调用
- 🏷️ `_print_header()` L52: "_print_header" - snake_case
- 🏷️ `_print_directory_section()` L62: "_print_directory_section" - snake_case
- 🏷️ `_print_config_section()` L76: "_print_config_section" - snake_case
- 🏷️ `_print_database_section()` L87: "_print_database_section" - snake_case
- 🏷️ `_check_postgres()` L102: "_check_postgres" - snake_case
- 🏷️ `_print_migration_section()` L113: "_print_migration_section" - snake_case
- 🏷️ `_get_unapplied_migrations()` L134: "_get_unapplied_migrations" - snake_case
- 🏷️ `_print_dependency_section()` L150: "_print_dependency_section" - snake_case
- 🏷️ `_print_llm_section()` L161: "_print_llm_section" - snake_case
- 🏷️ `_first_configured_env()` L178: "_first_configured_env" - snake_case

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 5
- 认知复杂度: 平均: 3.2, 最大: 7
- 嵌套深度: 平均: 0.5, 最大: 2
- 函数长度: 平均: 9.7 行, 最大: 17 行
- 文件长度: 147 代码量 (237 总计)
- 参数数量: 平均: 0.4, 最大: 2
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 4/6 个错误被忽略 (66.7%)
- 注释比例: 30.6% (45/147)
- 命名规范: 发现 13 个违规

### 142. backend\models\MEFKT\sequence.py

**糟糕指数: 6.42**

> 行数: 213 总计, 179 代码, 12 注释 | 函数: 4 | 类: 1

**问题**: ⚠️ 其他问题: 3, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `forward` | L159-209 | 51 | 4 | 2 | 4 | ✓ |
| `predict_candidate` | L89-154 | 66 | 3 | 1 | 5 | ✓ |
| `__init__` | L18-52 | 35 | 2 | 1 | 6 | ✓ |
| `_perceived_distance` | L57-84 | 28 | 1 | 0 | 3 | ✓ |

**全部问题 (5)**

- 📏 `predict_candidate()` L89: 66 代码量
- 📏 `forward()` L159: 51 代码量
- 📏 `__init__()` L18: 6 参数数量
- 🏷️ `__init__()` L18: "__init__" - snake_case
- 🏷️ `_perceived_distance()` L57: "_perceived_distance" - snake_case

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 4
- 认知复杂度: 平均: 4.5, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 45.0 行, 最大: 66 行
- 文件长度: 179 代码量 (213 总计)
- 参数数量: 平均: 4.5, 最大: 6
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 6.7% (12/179)
- 命名规范: 发现 2 个违规

### 143. backend\common\errors.py

**糟糕指数: 6.41**

> 行数: 144 总计, 109 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 1, 🏗️ 结构问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_flatten_error_messages` | L42-66 | 25 | 9 | 3 | 1 | ✓ |
| `custom_exception_handler` | L72-113 | 42 | 5 | 1 | 2 | ✓ |
| `_normalize_error_detail` | L20-36 | 17 | 4 | 1 | 1 | ✓ |
| `get_error_message` | L119-140 | 22 | 3 | 2 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `_flatten_error_messages()` L42: 认知复杂度: 15
- 🏗️ `_flatten_error_messages()` L42: 中等嵌套: 3
- 🏷️ `_normalize_error_detail()` L20: "_normalize_error_detail" - snake_case
- 🏷️ `_flatten_error_messages()` L42: "_flatten_error_messages" - snake_case

**详情**:
- 循环复杂度: 平均: 5.3, 最大: 9
- 认知复杂度: 平均: 8.8, 最大: 15
- 嵌套深度: 平均: 1.8, 最大: 3
- 函数长度: 平均: 26.5 行, 最大: 42 行
- 文件长度: 109 代码量 (144 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 1 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 11.0% (12/109)
- 命名规范: 发现 2 个违规

### 144. frontend\src\api\backend.ts

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

### 145. backend\knowledge\teacher_relation_views.py

**糟糕指数: 6.30**

> 行数: 123 总计, 94 代码, 9 注释 | 函数: 3 | 类: 0

**问题**: ❌ 错误处理问题: 7, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `knowledge_relation_create` | L70-103 | 34 | 9 | 1 | 1 | ✓ |
| `knowledge_relation_list` | L28-62 | 35 | 4 | 1 | 1 | ✓ |
| `knowledge_relation_delete` | L111-122 | 12 | 2 | 1 | 2 | ✓ |

**全部问题 (7)**

- ❌ L38: 未处理的易出错调用
- ❌ L39: 未处理的易出错调用
- ❌ L40: 未处理的易出错调用
- ❌ L41: 未处理的易出错调用
- ❌ L42: 未处理的易出错调用
- ❌ L43: 未处理的易出错调用
- ❌ L120: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 9
- 认知复杂度: 平均: 7.0, 最大: 11
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 27.0 行, 最大: 35 行
- 文件长度: 94 代码量 (123 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 7/13 个错误被忽略 (53.8%)
- 注释比例: 9.6% (9/94)
- 命名规范: 无命名违规

### 146. backend\exams\student_submission_views.py

**糟糕指数: 6.29**

> 行数: 192 总计, 162 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `exam_submit` | L36-118 | 83 | 9 | 2 | 2 | ✓ |
| `exam_statistics` | L176-191 | 16 | 5 | 1 | 2 | ✓ |
| `exam_result` | L126-153 | 28 | 3 | 1 | 2 | ✓ |
| `exam_save_draft` | L161-168 | 8 | 2 | 1 | 2 | ✓ |

**全部问题 (3)**

- 🔄 `exam_submit()` L36: 认知复杂度: 13
- 📏 `exam_submit()` L36: 83 代码量
- ❌ L167: 忽略了错误返回值

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 9
- 认知复杂度: 平均: 7.3, 最大: 13
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 33.8 行, 最大: 83 行
- 文件长度: 162 代码量 (192 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 7.4% (12/162)
- 命名规范: 无命名违规

### 147. backend\ai_services\services\mefkt_question_online.py

**糟糕指数: 6.18**

> 行数: 422 总计, 325 代码, 48 注释 | 函数: 14 | 类: 2

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 3, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_resolve_target_point_ids` | L220-227 | 8 | 4 | 1 | 1 | ✓ |
| `_points_from_answer_history` | L233-245 | 13 | 4 | 2 | 1 | ✓ |
| `_aggregate_point_predictions` | L343-360 | 18 | 3 | 2 | 3 | ✓ |
| `_point_probabilities` | L366-385 | 20 | 3 | 1 | 3 | ✓ |
| `predict_question_online` | L58-92 | 35 | 2 | 1 | 1 | ✓ |
| `_build_online_model_bundle` | L98-126 | 29 | 2 | 1 | 1 | ✓ |
| `_build_fused_question_embedding` | L132-172 | 41 | 2 | 0 | 1 | ✓ |
| `_encode_fused_embedding` | L178-206 | 29 | 2 | 1 | 5 | ✓ |
| `_predict_candidate_questions` | L281-318 | 38 | 2 | 1 | 4 | ✓ |
| `_metadata_int` | L212-214 | 3 | 1 | 0 | 3 | ✓ |
| `_resolve_candidate_question_indices` | L251-262 | 12 | 1 | 0 | 2 | ✓ |
| `_empty_question_online_response` | L268-275 | 8 | 1 | 0 | 0 | ✓ |
| `_build_per_question_predictions` | L324-337 | 14 | 1 | 0 | 3 | ✓ |
| `_question_online_response` | L391-421 | 31 | 1 | 0 | 4 | ✓ |

**全部问题 (13)**

- ❌ L243: 未处理的易出错调用
- ❌ L260: 未处理的易出错调用
- ❌ L375: 未处理的易出错调用
- 🏷️ `_build_online_model_bundle()` L98: "_build_online_model_bundle" - snake_case
- 🏷️ `_build_fused_question_embedding()` L132: "_build_fused_question_embedding" - snake_case
- 🏷️ `_encode_fused_embedding()` L178: "_encode_fused_embedding" - snake_case
- 🏷️ `_metadata_int()` L212: "_metadata_int" - snake_case
- 🏷️ `_resolve_target_point_ids()` L220: "_resolve_target_point_ids" - snake_case
- 🏷️ `_points_from_answer_history()` L233: "_points_from_answer_history" - snake_case
- 🏷️ `_resolve_candidate_question_indices()` L251: "_resolve_candidate_question_indices" - snake_case
- 🏷️ `_empty_question_online_response()` L268: "_empty_question_online_response" - snake_case
- 🏷️ `_predict_candidate_questions()` L281: "_predict_candidate_questions" - snake_case
- 🏷️ `_build_per_question_predictions()` L324: "_build_per_question_predictions" - snake_case

**详情**:
- 循环复杂度: 平均: 2.1, 最大: 4
- 认知复杂度: 平均: 3.5, 最大: 8
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 21.4 行, 最大: 41 行
- 文件长度: 325 代码量 (422 总计)
- 参数数量: 平均: 2.3, 最大: 5
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 3/11 个错误被忽略 (27.3%)
- 注释比例: 14.8% (48/325)
- 命名规范: 发现 13 个违规

### 148. frontend\src\views\teacher\useTeacherExamManage.js

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

### 149. frontend\scripts\browser-audit\files.mjs

**糟糕指数: 6.14**

> 行数: 31 总计, 25 代码, 0 注释 | 函数: 5 | 类: 0

**问题**: ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `readJson` | L13-20 | 8 | 2 | 0 | 1 | ✗ |
| `ensureDir` | L4-6 | 3 | 1 | 0 | 1 | ✗ |
| `writeJson` | L8-11 | 4 | 1 | 0 | 2 | ✗ |
| `resolveDefenseDemoArchivePath` | L22-24 | 3 | 1 | 0 | 1 | ✗ |
| `ensureDefenseArchiveExists` | L26-30 | 5 | 1 | 0 | 1 | ✗ |

**全部问题 (3)**

- ❌ L5: 未处理的易出错调用
- ❌ L10: 未处理的易出错调用
- ❌ L28: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.2, 最大: 2
- 认知复杂度: 平均: 1.2, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.6 行, 最大: 8 行
- 文件长度: 25 代码量 (31 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 3/5 个错误被忽略 (60.0%)
- 注释比例: 0.0% (0/25)
- 命名规范: 无命名违规

### 150. backend\ai_services\services\mefkt_inference.py

**糟糕指数: 6.12**

> 行数: 263 总计, 199 代码, 38 注释 | 函数: 12 | 类: 1

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 7, 🏷️ 命名问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_resolve_runtime_history_index` | L108-123 | 16 | 4 | 2 | 3 | ✓ |
| `predict` | L211-229 | 19 | 4 | 2 | 4 | ✓ |
| `_build_history_tensors_runtime` | L128-154 | 27 | 3 | 2 | 3 | ✓ |
| `is_loaded` | L55-57 | 3 | 2 | 0 | 1 | ✓ |
| `load_model` | L62-72 | 11 | 2 | 1 | 3 | ✓ |
| `_build_course_runtime_bundle` | L97-103 | 7 | 2 | 1 | 2 | ✓ |
| `_predict_question_online` | L177-206 | 30 | 2 | 0 | 4 | ✓ |
| `__init__` | L35-49 | 15 | 1 | 0 | 1 | ✗ |
| `_apply_loaded_state` | L77-92 | 16 | 1 | 0 | 2 | ✓ |
| `_predict_legacy` | L159-172 | 14 | 1 | 0 | 3 | ✓ |
| `get_info` | L234-249 | 16 | 1 | 0 | 1 | ✓ |
| `auto_load_model` | L258-262 | 5 | 1 | 0 | 0 | ✓ |

**全部问题 (14)**

- ❌ L242: 未处理的易出错调用
- ❌ L243: 未处理的易出错调用
- ❌ L244: 未处理的易出错调用
- ❌ L245: 未处理的易出错调用
- ❌ L246: 未处理的易出错调用
- ❌ L247: 未处理的易出错调用
- ❌ L248: 未处理的易出错调用
- 🏷️ `__init__()` L35: "__init__" - snake_case
- 🏷️ `_apply_loaded_state()` L77: "_apply_loaded_state" - snake_case
- 🏷️ `_build_course_runtime_bundle()` L97: "_build_course_runtime_bundle" - snake_case
- 🏷️ `_resolve_runtime_history_index()` L108: "_resolve_runtime_history_index" - snake_case
- 🏷️ `_build_history_tensors_runtime()` L128: "_build_history_tensors_runtime" - snake_case
- 🏷️ `_predict_legacy()` L159: "_predict_legacy" - snake_case
- 🏷️ `_predict_question_online()` L177: "_predict_question_online" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 4
- 认知复杂度: 平均: 3.3, 最大: 8
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 14.9 行, 最大: 30 行
- 文件长度: 199 代码量 (263 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 7/10 个错误被忽略 (70.0%)
- 注释比例: 19.1% (38/199)
- 命名规范: 发现 7 个违规

### 151. frontend\src\views\student\taskLearningModels.js

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

### 152. backend\ai_services\student_rag_views.py

**糟糕指数: 5.94**

> 行数: 99 总计, 79 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ai_node_intro` | L60-98 | 39 | 10 | 1 | 1 | ✓ |
| `ai_path_planning` | L29-52 | 24 | 4 | 1 | 1 | ✓ |

**全部问题 (1)**

- ❌ L47: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.0, 最大: 10
- 认知复杂度: 平均: 9.0, 最大: 12
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 31.5 行, 最大: 39 行
- 文件长度: 79 代码量 (99 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 7.6% (6/79)
- 命名规范: 无命名违规

### 153. backend\learning\path_adjustment.py

**糟糕指数: 5.87**

> 行数: 452 总计, 336 代码, 57 注释 | 函数: 19 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 1, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_create_path_nodes_with_resources` | L350-364 | 15 | 5 | 2 | 2 | ✓ |
| `_update_mastery_from_answer_history` | L68-101 | 34 | 4 | 2 | 2 | ✓ |
| `insert_remediation_nodes` | L47-62 | 16 | 3 | 2 | 1 | ✓ |
| `_build_kt_history` | L107-125 | 19 | 3 | 1 | 2 | ✓ |
| `_apply_kt_predictions` | L131-155 | 25 | 3 | 2 | 3 | ✓ |
| `_make_path_node_batch` | L263-290 | 28 | 3 | 2 | 5 | ✓ |
| `_make_study_node` | L296-314 | 19 | 3 | 0 | 4 | ✓ |
| `_ensure_active_path_node` | L370-377 | 8 | 3 | 1 | 1 | ✓ |
| `_serialize_refreshed_nodes` | L383-401 | 19 | 3 | 0 | 1 | ✓ |
| `_insert_remediation_node_if_missing` | L407-432 | 26 | 3 | 1 | 2 | ✓ |
| `refresh_learning_path_from_mastery` | L25-41 | 17 | 2 | 1 | 3 | ✓ |
| `_make_test_node` | L320-344 | 25 | 2 | 1 | 3 | ✓ |
| `_serialize_legacy_adjusted_nodes` | L438-451 | 14 | 2 | 0 | 1 | ✓ |
| `_rebuild_locked_path_nodes` | L161-185 | 25 | 1 | 0 | 3 | ✓ |
| `_preserved_path_nodes` | L191-194 | 4 | 1 | 0 | 1 | ✓ |
| `_build_replacement_nodes` | L200-223 | 24 | 1 | 0 | 5 | ✓ |
| `_course_mastery_map` | L229-234 | 6 | 1 | 0 | 2 | ✓ |
| `_remaining_course_points` | L240-249 | 10 | 1 | 0 | 2 | ✓ |
| `_next_order_index` | L255-257 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (11)**

- ❌ L420: 未处理的易出错调用
- 🏷️ `_update_mastery_from_answer_history()` L68: "_update_mastery_from_answer_history" - snake_case
- 🏷️ `_build_kt_history()` L107: "_build_kt_history" - snake_case
- 🏷️ `_apply_kt_predictions()` L131: "_apply_kt_predictions" - snake_case
- 🏷️ `_rebuild_locked_path_nodes()` L161: "_rebuild_locked_path_nodes" - snake_case
- 🏷️ `_preserved_path_nodes()` L191: "_preserved_path_nodes" - snake_case
- 🏷️ `_build_replacement_nodes()` L200: "_build_replacement_nodes" - snake_case
- 🏷️ `_course_mastery_map()` L229: "_course_mastery_map" - snake_case
- 🏷️ `_remaining_course_points()` L240: "_remaining_course_points" - snake_case
- 🏷️ `_next_order_index()` L255: "_next_order_index" - snake_case
- 🏷️ `_make_path_node_batch()` L263: "_make_path_node_batch" - snake_case

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 5
- 认知复杂度: 平均: 3.9, 最大: 9
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 17.7 行, 最大: 34 行
- 文件长度: 336 代码量 (452 总计)
- 参数数量: 平均: 2.3, 最大: 5
- 代码重复: 0.0% 重复 (0/19)
- 结构分析: 0 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 17.0% (57/336)
- 命名规范: 发现 17 个违规

### 154. backend\exams\report_service.py

**糟糕指数: 5.84**

> 行数: 222 总计, 180 代码, 16 注释 | 函数: 4 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_feedback_report_sync` | L104-221 | 118 | 9 | 1 | 2 | ✓ |
| `enqueue_feedback_report` | L52-65 | 14 | 3 | 2 | 2 | ✓ |
| `run_feedback_generation` | L84-98 | 15 | 2 | 2 | 2 | ✓ |
| `enqueue_feedback_report_on_commit` | L71-78 | 8 | 1 | 0 | 2 | ✓ |

**全部问题 (1)**

- 📏 `generate_feedback_report_sync()` L104: 118 代码量

**详情**:
- 循环复杂度: 平均: 3.8, 最大: 9
- 认知复杂度: 平均: 6.3, 最大: 11
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 38.8 行, 最大: 118 行
- 文件长度: 180 代码量 (222 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 8.9% (16/180)
- 命名规范: 无命名违规

### 155. backend\common\views.py

**糟糕指数: 5.77**

> 行数: 99 总计, 86 代码, 4 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_menu` | L13-98 | 86 | 6 | 1 | 1 | ✓ |

**全部问题 (1)**

- 📏 `get_menu()` L13: 86 代码量

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 6
- 认知复杂度: 平均: 8.0, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 86.0 行, 最大: 86 行
- 文件长度: 86 代码量 (99 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 4.7% (4/86)
- 命名规范: 无命名违规

### 156. backend\tools\api_regression_admin.py

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

### 157. backend\ai_services\services\llm_feedback_kt_support.py

**糟糕指数: 5.73**

> 行数: 355 总计, 260 代码, 48 注释 | 函数: 11 | 类: 5

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_kt_analysis_prompt` | L272-309 | 38 | 6 | 0 | 1 | ✓ |
| `classify_feedback_performance` | L104-144 | 41 | 5 | 1 | 1 | ✓ |
| `build_kt_analysis_fallback` | L315-339 | 25 | 5 | 0 | 1 | ✓ |
| `build_feedback_report_prompt` | L150-183 | 34 | 3 | 0 | 1 | ✓ |
| `summarize_kt_predictions` | L214-242 | 29 | 3 | 0 | 2 | ✓ |
| `readable_point_name` | L248-251 | 4 | 3 | 0 | 2 | ✓ |
| `summarize_answer_trend` | L257-266 | 10 | 3 | 1 | 1 | ✓ |
| `accuracy` | L40-42 | 3 | 2 | 0 | 1 | ✓ |
| `build_mistake_points` | L86-98 | 13 | 2 | 1 | 1 | ✓ |
| `build_feedback_report_fallback` | L189-208 | 20 | 2 | 0 | 1 | ✓ |
| `build_weak_point_analysis` | L345-354 | 10 | 2 | 1 | 2 | ✓ |

**全部问题 (10)**

- 📋 `build_mistake_points()` L86: 重复模式: build_mistake_points, build_weak_point_analysis
- ❌ L91: 未处理的易出错调用
- ❌ L92: 未处理的易出错调用
- ❌ L93: 未处理的易出错调用
- ❌ L94: 未处理的易出错调用
- ❌ L95: 未处理的易出错调用
- ❌ L158: 未处理的易出错调用
- ❌ L159: 未处理的易出错调用
- ❌ L193: 未处理的易出错调用
- ❌ L200: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 6
- 认知复杂度: 平均: 4.0, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 20.6 行, 最大: 41 行
- 文件长度: 260 代码量 (355 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 9.1% 重复 (1/11)
- 结构分析: 0 个结构问题
- 错误处理: 9/18 个错误被忽略 (50.0%)
- 注释比例: 18.5% (48/260)
- 命名规范: 无命名违规

### 158. backend\tools\kt_synthetic_sampling.py

**糟糕指数: 5.72**

> 行数: 470 总计, 335 代码, 74 注释 | 函数: 19 | 类: 5

**问题**: ⚠️ 其他问题: 2, 📋 重复问题: 2, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `apply_focus_weight` | L165-180 | 16 | 6 | 1 | 3 | ✓ |
| `build_focus_candidate_weight` | L233-250 | 18 | 6 | 1 | 4 | ✓ |
| `apply_session_gap_decay` | L82-99 | 18 | 5 | 2 | 5 | ✓ |
| `apply_recent_state_weight` | L186-198 | 13 | 5 | 1 | 4 | ✓ |
| `choose_focus_kp` | L256-272 | 17 | 4 | 2 | 3 | ✓ |
| `adjusted_item_difficulty` | L308-321 | 14 | 4 | 1 | 4 | ✓ |
| `is_kp_unlocked` | L122-133 | 12 | 3 | 0 | 4 | ✓ |
| `apply_attempt_weight` | L155-159 | 5 | 3 | 1 | 4 | ✓ |
| `compute_correct_probability` | L327-357 | 31 | 3 | 0 | 5 | ✓ |
| `update_child_mastery` | L419-431 | 13 | 3 | 1 | 4 | ✓ |
| `sample_sequence_length` | L437-454 | 18 | 3 | 1 | 4 | ✓ |
| `compute_interaction_outcome` | L278-302 | 25 | 2 | 0 | 4 | ✓ |
| `update_mastery_after_interaction` | L363-374 | 12 | 2 | 1 | 4 | ✓ |
| `apply_wrong_interaction` | L398-413 | 16 | 2 | 1 | 4 | ✓ |
| `prerequisite_mastery` | L105-116 | 12 | 1 | 0 | 4 | ✓ |
| `base_sampling_weight` | L139-149 | 11 | 1 | 0 | 3 | ✓ |
| `build_single_sampling_weight` | L204-219 | 16 | 1 | 0 | 2 | ✓ |
| `build_sampling_weights` | L225-227 | 3 | 1 | 0 | 2 | ✓ |
| `apply_correct_interaction` | L380-392 | 13 | 1 | 0 | 3 | ✓ |

**全部问题 (3)**

- 📋 `apply_recent_state_weight()` L186: 重复模式: apply_recent_state_weight, sample_sequence_length
- 📋 `compute_interaction_outcome()` L278: 重复模式: compute_interaction_outcome, compute_correct_probability
- ❌ L114: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.9, 最大: 6
- 认知复杂度: 平均: 4.3, 最大: 9
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 14.9 行, 最大: 31 行
- 文件长度: 335 代码量 (470 总计)
- 参数数量: 平均: 3.7, 最大: 5
- 代码重复: 10.5% 重复 (2/19)
- 结构分析: 0 个结构问题
- 错误处理: 1/6 个错误被忽略 (16.7%)
- 注释比例: 22.1% (74/335)
- 命名规范: 无命名违规

### 159. backend\assessments\ability_views.py

**糟糕指数: 5.70**

> 行数: 427 总计, 311 代码, 60 注释 | 函数: 20 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 2, 🏷️ 命名问题: 10

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_normalize_answer_map` | L193-208 | 16 | 5 | 1 | 1 | ✓ |
| `_is_question_answer_correct` | L255-269 | 15 | 4 | 1 | 2 | ✓ |
| `_score_global_survey` | L275-298 | 24 | 4 | 2 | 1 | ✓ |
| `_save_ability_result` | L372-401 | 30 | 4 | 1 | 5 | ✓ |
| `_resolve_default_course_id` | L407-414 | 8 | 4 | 1 | 1 | ✓ |
| `submit_ability_assessment` | L79-111 | 33 | 3 | 1 | 1 | ✓ |
| `_score_course_assessment` | L238-249 | 12 | 3 | 2 | 2 | ✓ |
| `_answer_question_ids` | L304-312 | 9 | 3 | 2 | 1 | ✓ |
| `_survey_option_score` | L318-329 | 12 | 3 | 2 | 2 | ✓ |
| `get_ability_assessment` | L60-71 | 12 | 2 | 1 | 1 | ✓ |
| `_get_course_ability_assessment` | L117-125 | 9 | 2 | 1 | 1 | ✓ |
| `_get_or_create_global_ability_questions` | L131-143 | 13 | 2 | 1 | 0 | ✓ |
| `_score_ability_answers` | L214-232 | 19 | 2 | 1 | 2 | ✓ |
| `_add_dimension_score` | L335-345 | 11 | 2 | 1 | 4 | ✓ |
| `_build_ability_analysis` | L351-358 | 8 | 2 | 0 | 1 | ✓ |
| `_percentage` | L364-366 | 3 | 2 | 0 | 2 | ✓ |
| `_mark_ability_assessment_done` | L420-426 | 7 | 2 | 1 | 2 | ✓ |
| `retake_ability_assessment` | L47-52 | 6 | 1 | 0 | 1 | ✓ |
| `_serialize_survey_payload` | L149-166 | 18 | 1 | 0 | 1 | ✓ |
| `_serialize_assessment_payload` | L172-187 | 16 | 1 | 0 | 1 | ✓ |

**全部问题 (12)**

- ❌ L247: 未处理的易出错调用
- ❌ L258: 未处理的易出错调用
- 🏷️ `_get_course_ability_assessment()` L117: "_get_course_ability_assessment" - snake_case
- 🏷️ `_get_or_create_global_ability_questions()` L131: "_get_or_create_global_ability_questions" - snake_case
- 🏷️ `_serialize_survey_payload()` L149: "_serialize_survey_payload" - snake_case
- 🏷️ `_serialize_assessment_payload()` L172: "_serialize_assessment_payload" - snake_case
- 🏷️ `_normalize_answer_map()` L193: "_normalize_answer_map" - snake_case
- 🏷️ `_score_ability_answers()` L214: "_score_ability_answers" - snake_case
- 🏷️ `_score_course_assessment()` L238: "_score_course_assessment" - snake_case
- 🏷️ `_is_question_answer_correct()` L255: "_is_question_answer_correct" - snake_case
- 🏷️ `_score_global_survey()` L275: "_score_global_survey" - snake_case
- 🏷️ `_answer_question_ids()` L304: "_answer_question_ids" - snake_case

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 5
- 认知复杂度: 平均: 4.5, 最大: 8
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 14.1 行, 最大: 33 行
- 文件长度: 311 代码量 (427 总计)
- 参数数量: 平均: 1.6, 最大: 5
- 代码重复: 5.0% 重复 (1/20)
- 结构分析: 0 个结构问题
- 错误处理: 2/8 个错误被忽略 (25.0%)
- 注释比例: 19.3% (60/311)
- 命名规范: 发现 17 个违规

### 160. backend\tools\bootstrap.py

**糟糕指数: 5.63**

> 行数: 146 总计, 118 代码, 10 注释 | 函数: 2 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_course_resources` | L107-145 | 39 | 5 | 2 | 1 | ✓ |
| `bootstrap_course_assets` | L35-98 | 64 | 2 | 1 | 6 | ✓ |

**全部问题 (2)**

- 📏 `bootstrap_course_assets()` L35: 64 代码量
- 📏 `bootstrap_course_assets()` L35: 6 参数数量

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 5
- 认知复杂度: 平均: 6.5, 最大: 9
- 嵌套深度: 平均: 1.5, 最大: 2
- 函数长度: 平均: 51.5 行, 最大: 64 行
- 文件长度: 118 代码量 (146 总计)
- 参数数量: 平均: 3.5, 最大: 6
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 8.5% (10/118)
- 命名规范: 无命名违规

### 161. backend\ai_services\test_llm_service.py

**糟糕指数: 5.58**

> 行数: 466 总计, 333 代码, 66 注释 | 函数: 17 | 类: 5

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 2, 🏗️ 结构问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_agent_graphrag_tool_should_call_public_payload_builder` | L391-417 | 27 | 2 | 1 | 1 | ✓ |
| `test_facade_graphrag_llm_should_instantiate_without_legacy_warning` | L429-438 | 10 | 2 | 1 | 1 | ✓ |
| `test_facade_graphrag_llm_should_accept_v2_message_lists` | L443-465 | 23 | 2 | 1 | 1 | ✓ |
| `test_llm_service_should_resolve_explicit_doubao_provider` | L53-62 | 10 | 1 | 0 | 1 | ✓ |
| `test_llm_service_should_resolve_custom_gateway_fields` | L76-85 | 10 | 1 | 0 | 1 | ✓ |
| `test_llm_service_should_attach_https_proxy_to_chat_client` | L101-115 | 15 | 1 | 0 | 2 | ✓ |
| `test_llm_service_should_default_deepseek_v4_to_non_thinking_mode` | L132-151 | 20 | 1 | 0 | 2 | ✓ |
| `test_external_resource_recommendation_should_enable_provider_web_search` | L168-197 | 30 | 1 | 0 | 2 | ✓ |
| `test_llm_json_parser_should_ignore_think_blocks` | L202-210 | 9 | 1 | 0 | 1 | ✓ |
| `_build_service` | L223-228 | 6 | 1 | 0 | 0 | ✗ |
| `test_call_with_fallback_should_skip_agent_for_profile_analysis` | L233-251 | 19 | 1 | 0 | 1 | ✓ |
| `test_call_with_fallback_should_only_use_agent_for_explicit_agent_calls` | L256-272 | 17 | 1 | 0 | 1 | ✓ |
| `_build_service` | L285-290 | 6 | 1 | 0 | 0 | ✗ |
| `test_call_with_fallback_should_fast_fail_graph_rag_calls_without_repair` | L295-319 | 25 | 1 | 0 | 1 | ✓ |
| `test_call_with_fallback_should_keep_repair_for_profile_analysis` | L324-339 | 16 | 1 | 0 | 1 | ✓ |
| `test_chat_policy_should_fast_fail_like_other_interactive_routes` | L344-353 | 10 | 1 | 0 | 1 | ✓ |
| `test_agent_service_should_forward_proxy_to_chat_openai` | L376-386 | 11 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- 📋 `test_llm_service_should_attach_https_proxy_to_chat_client()` L101: 重复模式: test_llm_service_should_attach_https_proxy_to_chat_client, test_llm_service_should_default_deepseek_v4_to_non_thinking_mode
- 📋 `test_call_with_fallback_should_only_use_agent_for_explicit_agent_calls()` L256: 重复模式: test_call_with_fallback_should_only_use_agent_for_explicit_agent_calls, test_call_with_fallback_should_keep_repair_for_profile_analysis, test_facade_graphrag_llm_should_accept_v2_message_lists
- 🏗️ L1: 导入过多: 33

**详情**:
- 循环复杂度: 平均: 1.2, 最大: 2
- 认知复杂度: 平均: 1.5, 最大: 4
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 15.5 行, 最大: 30 行
- 文件长度: 333 代码量 (466 总计)
- 参数数量: 平均: 1.1, 最大: 2
- 代码重复: 17.6% 重复 (3/17)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 19.8% (66/333)
- 命名规范: 发现 2 个违规

### 162. backend\ai_services\services\llm_profile_path_mixin.py

**糟糕指数: 5.50**

> 行数: 151 总计, 115 代码, 18 注释 | 函数: 5 | 类: 1

**问题**: ⚠️ 其他问题: 2, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `plan_learning_path` | L63-97 | 35 | 2 | 1 | 6 | ✓ |
| `analyze_profile` | L26-58 | 33 | 1 | 0 | 7 | ✓ |
| `generate_resource_reason` | L102-134 | 33 | 1 | 0 | 5 | ✓ |
| `_identify_weakness` | L140-142 | 3 | 1 | 0 | 1 | ✓ |
| `_identify_strength` | L148-150 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (4)**

- 📏 `analyze_profile()` L26: 7 参数数量
- 📏 `plan_learning_path()` L63: 6 参数数量
- 🏷️ `_identify_weakness()` L140: "_identify_weakness" - snake_case
- 🏷️ `_identify_strength()` L148: "_identify_strength" - snake_case

**详情**:
- 循环复杂度: 平均: 1.2, 最大: 2
- 认知复杂度: 平均: 1.6, 最大: 4
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 21.4 行, 最大: 35 行
- 文件长度: 115 代码量 (151 总计)
- 参数数量: 平均: 4.0, 最大: 7
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 15.7% (18/115)
- 命名规范: 发现 2 个违规

### 163. backend\common\defense_demo_environment.py

**糟糕指数: 5.50**

> 行数: 128 总计, 113 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ensure_defense_demo_environment` | L37-127 | 91 | 4 | 1 | 1 | ✓ |

**全部问题 (1)**

- 📏 `ensure_defense_demo_environment()` L37: 91 代码量

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 6.0, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 91.0 行, 最大: 91 行
- 文件长度: 113 代码量 (128 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 2.7% (3/113)
- 命名规范: 无命名违规

### 164. backend\users\admin_activation_views.py

**糟糕指数: 5.42**

> 行数: 235 总计, 180 代码, 21 注释 | 函数: 7 | 类: 0

**问题**: 🔄 复杂度问题: 1, ❌ 错误处理问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_activation_code` | L22-60 | 39 | 9 | 2 | 1 | ✓ |
| `activation_code_export` | L208-234 | 27 | 8 | 1 | 1 | ✓ |
| `delete_activation_code` | L111-134 | 24 | 7 | 1 | 2 | ✓ |
| `list_activation_codes` | L68-103 | 36 | 6 | 1 | 1 | ✓ |
| `activation_code_detail` | L142-160 | 19 | 6 | 1 | 2 | ✓ |
| `activation_code_validate` | L183-200 | 18 | 4 | 1 | 1 | ✓ |
| `activation_code_batch_delete` | L168-175 | 8 | 2 | 1 | 1 | ✓ |

**全部问题 (4)**

- 🔄 `generate_activation_code()` L22: 认知复杂度: 13
- ❌ L133: 未处理的易出错调用
- ❌ L174: 忽略了错误返回值
- ❌ L217: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 9
- 认知复杂度: 平均: 8.3, 最大: 13
- 嵌套深度: 平均: 1.1, 最大: 2
- 函数长度: 平均: 24.4 行, 最大: 39 行
- 文件长度: 180 代码量 (235 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 3/16 个错误被忽略 (18.8%)
- 注释比例: 11.7% (21/180)
- 命名规范: 无命名违规

### 165. backend\common\defense_demo_accounts.py

**糟糕指数: 5.41**

> 行数: 209 总计, 174 代码, 20 注释 | 函数: 6 | 类: 0

**问题**: ⚠️ 其他问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_ensure_class` | L127-156 | 30 | 3 | 2 | 3 | ✓ |
| `_ensure_user` | L21-52 | 32 | 2 | 0 | 6 | ✓ |
| `ensure_defense_demo_accounts` | L80-121 | 42 | 2 | 1 | 0 | ✓ |
| `_ensure_course_only_demo_students` | L187-208 | 22 | 2 | 1 | 2 | ✓ |
| `_ensure_course` | L58-74 | 17 | 1 | 0 | 2 | ✓ |
| `_reset_course_only_student_state` | L162-181 | 20 | 1 | 0 | 2 | ✓ |

**全部问题 (6)**

- 📏 `_ensure_user()` L21: 6 参数数量
- 🏷️ `_ensure_user()` L21: "_ensure_user" - snake_case
- 🏷️ `_ensure_course()` L58: "_ensure_course" - snake_case
- 🏷️ `_ensure_class()` L127: "_ensure_class" - snake_case
- 🏷️ `_reset_course_only_student_state()` L162: "_reset_course_only_student_state" - snake_case
- 🏷️ `_ensure_course_only_demo_students()` L187: "_ensure_course_only_demo_students" - snake_case

**详情**:
- 循环复杂度: 平均: 1.8, 最大: 3
- 认知复杂度: 平均: 3.2, 最大: 7
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 27.2 行, 最大: 42 行
- 文件长度: 174 代码量 (209 总计)
- 参数数量: 平均: 2.5, 最大: 6
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/12 个错误被忽略 (0.0%)
- 注释比例: 11.5% (20/174)
- 命名规范: 发现 5 个违规

### 166. backend\ai_services\services\mefkt_runtime_graph.py

**糟糕指数: 5.31**

> 行数: 147 总计, 114 代码, 17 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `pairwise_graph_weight` | L13-35 | 23 | 7 | 0 | 7 | ✓ |
| `compute_related_bridge_score` | L41-52 | 12 | 3 | 1 | 4 | ✓ |
| `accumulate_left_question_edges` | L98-132 | 35 | 3 | 2 | 7 | ✓ |
| `build_graph_statistics` | L58-92 | 35 | 2 | 1 | 3 | ✓ |
| `build_two_hop_density` | L138-146 | 9 | 2 | 1 | 3 | ✓ |

**全部问题 (2)**

- 📏 `pairwise_graph_weight()` L13: 7 参数数量
- 📏 `accumulate_left_question_edges()` L98: 7 参数数量

**详情**:
- 循环复杂度: 平均: 3.4, 最大: 7
- 认知复杂度: 平均: 5.4, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 22.8 行, 最大: 35 行
- 文件长度: 114 代码量 (147 总计)
- 参数数量: 平均: 4.8, 最大: 7
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 14.9% (17/114)
- 命名规范: 无命名违规

### 167. frontend\src\views\student\feedbackReportModels.js

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

### 168. backend\ai_services\services\llm_resource_mixin.py

**糟糕指数: 5.23**

> 行数: 140 总计, 112 代码, 12 注释 | 函数: 3 | 类: 1

**问题**: ⚠️ 其他问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `select_stage_test_questions` | L109-139 | 31 | 4 | 1 | 4 | ✓ |
| `recommend_internal_resources` | L71-104 | 34 | 2 | 1 | 6 | ✓ |
| `recommend_external_resources` | L22-66 | 45 | 1 | 0 | 7 | ✓ |

**全部问题 (2)**

- 📏 `recommend_external_resources()` L22: 7 参数数量
- 📏 `recommend_internal_resources()` L71: 6 参数数量

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 4
- 认知复杂度: 平均: 3.7, 最大: 6
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 36.7 行, 最大: 45 行
- 文件长度: 112 代码量 (140 总计)
- 参数数量: 平均: 5.7, 最大: 7
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 10.7% (12/112)
- 命名规范: 无命名违规

### 169. backend\common\responses.py

**糟糕指数: 5.21**

> 行数: 122 总计, 78 代码, 21 注释 | 函数: 7 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `api_response` | L13-49 | 37 | 8 | 1 | 6 | ✓ |
| `success_response` | L55-57 | 3 | 1 | 0 | 2 | ✓ |
| `created_response` | L63-65 | 3 | 1 | 0 | 2 | ✓ |
| `error_response` | L71-86 | 16 | 1 | 0 | 5 | ✓ |
| `not_found_response` | L92-94 | 3 | 1 | 0 | 1 | ✓ |
| `unauthorized_response` | L100-102 | 3 | 1 | 0 | 1 | ✓ |
| `forbidden_response` | L108-110 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- 📏 `api_response()` L13: 6 参数数量

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 8
- 认知复杂度: 平均: 2.3, 最大: 10
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 9.7 行, 最大: 37 行
- 文件长度: 78 代码量 (122 总计)
- 参数数量: 平均: 2.6, 最大: 6
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 26.9% (21/78)
- 命名规范: 无命名违规

### 170. backend\ai_services\services\student_graph_rag_support.py

**糟糕指数: 5.18**

> 行数: 544 总计, 378 代码, 87 注释 | 函数: 28 | 类: 1

**问题**: ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 7

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `match_points_by_query_text` | L89-104 | 16 | 6 | 2 | 3 | ✓ |
| `extract_matched_point_ids` | L158-171 | 14 | 6 | 2 | 1 | ✓ |
| `build_graph_answer_payload` | L216-236 | 21 | 6 | 0 | 3 | ✓ |
| `answer_explicit_or_structure_question` | L450-477 | 28 | 6 | 1 | 3 | ✓ |
| `coerce_positive_int` | L177-184 | 8 | 5 | 1 | 1 | ✓ |
| `build_search_item` | L242-260 | 19 | 5 | 0 | 2 | ✓ |
| `answer_graph_question` | L409-434 | 26 | 5 | 2 | 4 | ✓ |
| `unique_ranked_points` | L110-121 | 12 | 4 | 2 | 2 | ✓ |
| `resolve_point_from_ids` | L127-141 | 15 | 4 | 2 | 2 | ✓ |
| `extract_first_search_point_id` | L201-210 | 10 | 4 | 1 | 1 | ✓ |
| `search_graph_points` | L296-309 | 14 | 4 | 1 | 4 | ✓ |
| `search_with_runtime` | L315-328 | 14 | 4 | 1 | 4 | ✓ |
| `build_runtime_matched_points` | L334-353 | 20 | 4 | 2 | 3 | ✓ |
| `has_course_rag_result` | L190-195 | 6 | 3 | 1 | 1 | ✓ |
| `neo4j_relation_names` | L266-276 | 11 | 3 | 1 | 1 | ✓ |
| `relation_point_names` | L282-290 | 9 | 3 | 1 | 1 | ✓ |
| `build_runtime_match_item` | L359-368 | 10 | 3 | 1 | 3 | ✓ |
| `answer_course_or_llm_fallback` | L504-517 | 14 | 3 | 1 | 4 | ✓ |
| `extract_text_list` | L147-152 | 6 | 2 | 1 | 2 | ✓ |
| `search_with_database_keyword` | L386-403 | 18 | 2 | 0 | 4 | ✓ |
| `point_from_explicit_id` | L440-444 | 5 | 2 | 1 | 2 | ✓ |
| `point_from_search` | L483-489 | 7 | 2 | 1 | 3 | ✓ |
| `build_llm_fallback` | L523-543 | 21 | 2 | 1 | 2 | ✓ |
| `to_dict` | L55-65 | 11 | 1 | 0 | 1 | ✓ |
| `normalize_match_text` | L71-74 | 4 | 1 | 0 | 1 | ✓ |
| `is_graph_structure_question` | L80-83 | 4 | 1 | 0 | 1 | ✓ |
| `build_name_match_response` | L374-380 | 7 | 1 | 0 | 3 | ✓ |
| `answer_focused_point_question` | L495-498 | 4 | 1 | 0 | 4 | ✓ |

**全部问题 (7)**

- ❌ L229: 未处理的易出错调用
- ❌ L230: 未处理的易出错调用
- ❌ L231: 未处理的易出错调用
- ❌ L274: 未处理的易出错调用
- ❌ L275: 未处理的易出错调用
- ❌ L287: 未处理的易出错调用
- ❌ L289: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 6
- 认知复杂度: 平均: 5.2, 最大: 10
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 12.6 行, 最大: 28 行
- 文件长度: 378 代码量 (544 总计)
- 参数数量: 平均: 2.4, 最大: 4
- 代码重复: 3.6% 重复 (1/28)
- 结构分析: 0 个结构问题
- 错误处理: 7/21 个错误被忽略 (33.3%)
- 注释比例: 23.0% (87/378)
- 命名规范: 无命名违规

### 171. frontend\src\stores\user.ts

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

### 172. frontend\scripts\browser-audit\args.mjs

**糟糕指数: 5.16**

> 行数: 20 总计, 18 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `parseArgs` | L1-19 | 19 | 7 | 2 | 1 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 7.0, 最大: 7
- 认知复杂度: 平均: 11.0, 最大: 11
- 嵌套深度: 平均: 2.0, 最大: 2
- 函数长度: 平均: 19.0 行, 最大: 19 行
- 文件长度: 18 代码量 (20 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/18)
- 命名规范: 无命名违规

### 173. backend\common\defense_demo_stage_result.py

**糟糕指数: 5.11**

> 行数: 171 总计, 148 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 3, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_question_detail` | L46-96 | 51 | 2 | 0 | 3 | ✓ |
| `build_demo_stage_test_result` | L123-170 | 48 | 2 | 0 | 4 | ✓ |
| `build_question_result_map` | L31-40 | 10 | 1 | 0 | 1 | ✓ |
| `build_question_details` | L102-117 | 16 | 1 | 0 | 3 | ✓ |

**全部问题 (4)**

- 📏 `build_question_detail()` L46: 51 代码量
- ❌ L94: 未处理的易出错调用
- ❌ L95: 未处理的易出错调用
- ❌ L166: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 2
- 认知复杂度: 平均: 1.5, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 31.3 行, 最大: 51 行
- 文件长度: 148 代码量 (171 总计)
- 参数数量: 平均: 2.8, 最大: 4
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 3/6 个错误被忽略 (50.0%)
- 注释比例: 8.1% (12/148)
- 命名规范: 无命名违规

### 174. backend\users\auth_support.py

**糟糕指数: 5.09**

> 行数: 443 总计, 292 代码, 78 注释 | 函数: 25 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `validate_userinfo_field` | L346-354 | 9 | 7 | 1 | 3 | ✓ |
| `registration_duplicate_error` | L82-92 | 11 | 6 | 1 | 2 | ✓ |
| `authenticate_user_login` | L136-153 | 18 | 6 | 1 | 2 | ✓ |
| `build_enrollment_class_payload` | L228-246 | 19 | 6 | 0 | 1 | ✓ |
| `update_userinfo_payload` | L305-330 | 26 | 6 | 2 | 3 | ✓ |
| `validate_activation_code` | L117-130 | 14 | 5 | 1 | 2 | ✓ |
| `validate_username_value` | L384-395 | 12 | 5 | 1 | 2 | ✓ |
| `change_user_password` | L415-428 | 14 | 5 | 1 | 2 | ✓ |
| `register_user` | L61-76 | 16 | 4 | 1 | 1 | ✓ |
| `register_privileged_user` | L98-111 | 14 | 4 | 1 | 3 | ✓ |
| `build_user_learning_context` | L194-210 | 17 | 4 | 2 | 1 | ✓ |
| `get_avatar_url` | L47-55 | 9 | 3 | 1 | 1 | ✓ |
| `resolve_class_course` | L252-258 | 7 | 3 | 1 | 1 | ✓ |
| `build_teaching_class_payload` | L272-284 | 13 | 3 | 0 | 1 | ✓ |
| `append_unique_course` | L290-299 | 10 | 3 | 1 | 4 | ✓ |
| `normalize_userinfo_value` | L336-340 | 5 | 3 | 1 | 2 | ✓ |
| `validate_phone_value` | L360-366 | 7 | 3 | 1 | 2 | ✓ |
| `validate_email_value` | L372-378 | 7 | 3 | 1 | 2 | ✓ |
| `refresh_access_token` | L401-409 | 9 | 3 | 1 | 1 | ✓ |
| `blacklist_refresh_token` | L434-442 | 9 | 3 | 1 | 1 | ✓ |
| `get_authenticated_user` | L39-41 | 3 | 1 | 0 | 1 | ✓ |
| `build_auth_payload` | L159-168 | 10 | 1 | 0 | 1 | ✓ |
| `build_userinfo_payload` | L174-188 | 15 | 1 | 0 | 1 | ✓ |
| `user_enrollments` | L216-222 | 7 | 1 | 0 | 1 | ✓ |
| `teaching_classes` | L264-266 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 📋 `register_privileged_user()` L98: 重复模式: register_privileged_user, resolve_class_course
- 📋 `validate_phone_value()` L360: 重复模式: validate_phone_value, validate_email_value, refresh_access_token

**详情**:
- 循环复杂度: 平均: 3.6, 最大: 7
- 认知复杂度: 平均: 5.2, 最大: 10
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 11.4 行, 最大: 26 行
- 文件长度: 292 代码量 (443 总计)
- 参数数量: 平均: 1.7, 最大: 4
- 代码重复: 12.0% 重复 (3/25)
- 结构分析: 0 个结构问题
- 错误处理: 0/10 个错误被忽略 (0.0%)
- 注释比例: 26.7% (78/292)
- 命名规范: 无命名违规

### 175. backend\exams\teacher_helpers.py

**糟糕指数: 5.08**

> 行数: 168 总计, 111 代码, 24 注释 | 函数: 8 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 🏷️ 命名问题: 8

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_validate_exam_scores` | L24-41 | 18 | 6 | 1 | 2 | ✓ |
| `_normalize_choice_answer_set` | L67-84 | 18 | 5 | 1 | 1 | ✓ |
| `_ensure_teacher_exam_access` | L123-138 | 16 | 5 | 1 | 4 | ✓ |
| `_parse_pagination` | L47-61 | 15 | 2 | 1 | 4 | ✓ |
| `_get_exam_or_404` | L90-96 | 7 | 2 | 1 | 1 | ✓ |
| `_get_owned_exam_or_404` | L102-108 | 7 | 2 | 1 | 2 | ✓ |
| `_get_teacher_course_ids` | L114-117 | 4 | 1 | 0 | 1 | ✓ |
| `_build_exam_question_rows` | L144-155 | 12 | 1 | 0 | 3 | ✓ |

**全部问题 (9)**

- ❌ L71: 未处理的易出错调用
- 🏷️ `_validate_exam_scores()` L24: "_validate_exam_scores" - snake_case
- 🏷️ `_parse_pagination()` L47: "_parse_pagination" - snake_case
- 🏷️ `_normalize_choice_answer_set()` L67: "_normalize_choice_answer_set" - snake_case
- 🏷️ `_get_exam_or_404()` L90: "_get_exam_or_404" - snake_case
- 🏷️ `_get_owned_exam_or_404()` L102: "_get_owned_exam_or_404" - snake_case
- 🏷️ `_get_teacher_course_ids()` L114: "_get_teacher_course_ids" - snake_case
- 🏷️ `_ensure_teacher_exam_access()` L123: "_ensure_teacher_exam_access" - snake_case
- 🏷️ `_build_exam_question_rows()` L144: "_build_exam_question_rows" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 6
- 认知复杂度: 平均: 4.5, 最大: 8
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 12.1 行, 最大: 18 行
- 文件长度: 111 代码量 (168 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 21.6% (24/111)
- 命名规范: 发现 8 个违规

### 176. backend\users\backends.py

**糟糕指数: 5.06**

> 行数: 70 总计, 49 代码, 9 注释 | 函数: 1 | 类: 1

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `authenticate` | L32-69 | 38 | 8 | 1 | 4 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 8.0, 最大: 8
- 认知复杂度: 平均: 10.0, 最大: 10
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 38.0 行, 最大: 38 行
- 文件长度: 49 代码量 (70 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 18.4% (9/49)
- 命名规范: 无命名违规

### 177. backend\learning\node_detail_support.py

**糟糕指数: 5.04**

> 行数: 353 总计, 261 代码, 50 注释 | 函数: 13 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_node_detail_payload` | L78-102 | 25 | 6 | 1 | 3 | ✓ |
| `update_node_exam_progress` | L172-190 | 19 | 6 | 2 | 4 | ✓ |
| `persist_node_exam_histories` | L196-228 | 33 | 5 | 2 | 5 | ✓ |
| `refresh_node_exam_mastery` | L311-352 | 42 | 5 | 2 | 1 | ✓ |
| `ensure_progress_baseline` | L56-72 | 17 | 4 | 3 | 2 | ✓ |
| `apply_node_mastery_fallback` | L292-305 | 14 | 4 | 1 | 1 | ✓ |
| `mark_node_resource_completed` | L108-125 | 18 | 3 | 1 | 2 | ✓ |
| `build_node_exam_context` | L131-153 | 23 | 3 | 0 | 2 | ✓ |
| `resolve_node_knowledge_point_ids` | L256-260 | 5 | 3 | 1 | 1 | ✓ |
| `persist_node_kt_predictions` | L266-286 | 21 | 3 | 2 | 2 | ✓ |
| `load_node_for_user` | L44-50 | 7 | 2 | 1 | 3 | ✓ |
| `load_node_kt_history` | L234-250 | 17 | 2 | 0 | 1 | ✓ |
| `upsert_node_exam_submission` | L159-166 | 8 | 1 | 0 | 5 | ✓ |

**全部问题 (3)**

- 📋 `load_node_for_user()` L44: 重复模式: load_node_for_user, mark_node_resource_completed
- 🏗️ `ensure_progress_baseline()` L56: 中等嵌套: 3
- ❌ L209: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.6, 最大: 6
- 认知复杂度: 平均: 6.1, 最大: 10
- 嵌套深度: 平均: 1.2, 最大: 3
- 函数长度: 平均: 19.2 行, 最大: 42 行
- 文件长度: 261 代码量 (353 总计)
- 参数数量: 平均: 2.5, 最大: 5
- 代码重复: 7.7% 重复 (1/13)
- 结构分析: 1 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 19.2% (50/261)
- 命名规范: 无命名违规

### 178. backend\tools\excel_templates.py

**糟糕指数: 5.03**

> 行数: 87 总计, 74 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_template` | L16-86 | 71 | 6 | 1 | 2 | ✓ |

**全部问题 (1)**

- 📏 `generate_template()` L16: 71 代码量

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 6
- 认知复杂度: 平均: 8.0, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 71.0 行, 最大: 71 行
- 文件长度: 74 代码量 (87 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 4.1% (3/74)
- 命名规范: 无命名违规

### 179. backend\platform_ai\kt\__init__.py

**糟糕指数: 5.00**

> 行数: 20 总计, 13 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__getattr__` | L6-12 | 7 | 2 | 1 | 1 | ✓ |

**全部问题 (1)**

- 🏷️ `__getattr__()` L6: "__getattr__" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 7.0 行, 最大: 7 行
- 文件长度: 13 代码量 (20 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/13)
- 命名规范: 发现 1 个违规

### 180. frontend\src\stores\course.ts

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

### 181. backend\learning\view_helpers.py

**糟糕指数: 4.90**

> 行数: 198 总计, 146 代码, 27 注释 | 函数: 9 | 类: 0

**问题**: ❌ 错误处理问题: 1, 🏷️ 命名问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_exam_score_map` | L72-85 | 14 | 4 | 0 | 2 | ✓ |
| `_serialize_path_nodes` | L91-120 | 30 | 4 | 1 | 2 | ✓ |
| `_coerce_string_list` | L25-33 | 9 | 2 | 1 | 1 | ✓ |
| `_path_node_sort_key` | L39-46 | 8 | 2 | 0 | 1 | ✓ |
| `_clean_text_for_llm` | L52-66 | 15 | 2 | 1 | 2 | ✓ |
| `_snapshot_mastery_for_points` | L126-146 | 21 | 2 | 1 | 3 | ✓ |
| `_average_mastery` | L152-162 | 11 | 2 | 1 | 1 | ✓ |
| `_build_mastery_change_payload` | L168-197 | 30 | 2 | 1 | 2 | ✓ |
| `_get_authenticated_user` | L13-19 | 7 | 1 | 0 | 1 | ✓ |

**全部问题 (10)**

- ❌ L189: 未处理的易出错调用
- 🏷️ `_get_authenticated_user()` L13: "_get_authenticated_user" - snake_case
- 🏷️ `_coerce_string_list()` L25: "_coerce_string_list" - snake_case
- 🏷️ `_path_node_sort_key()` L39: "_path_node_sort_key" - snake_case
- 🏷️ `_clean_text_for_llm()` L52: "_clean_text_for_llm" - snake_case
- 🏷️ `_build_exam_score_map()` L72: "_build_exam_score_map" - snake_case
- 🏷️ `_serialize_path_nodes()` L91: "_serialize_path_nodes" - snake_case
- 🏷️ `_snapshot_mastery_for_points()` L126: "_snapshot_mastery_for_points" - snake_case
- 🏷️ `_average_mastery()` L152: "_average_mastery" - snake_case
- 🏷️ `_build_mastery_change_payload()` L168: "_build_mastery_change_payload" - snake_case

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 4
- 认知复杂度: 平均: 3.7, 最大: 6
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 16.1 行, 最大: 30 行
- 文件长度: 146 代码量 (198 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 18.5% (27/146)
- 命名规范: 发现 9 个违规

### 182. backend\tools\api_regression_helpers.py

**糟糕指数: 4.84**

> 行数: 195 总计, 135 代码, 30 注释 | 函数: 10 | 类: 0

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `pick_first_id` | L147-164 | 18 | 7 | 2 | 3 | ✓ |
| `build_question_answer` | L95-105 | 11 | 6 | 1 | 1 | ✓ |
| `record_check` | L24-44 | 21 | 5 | 1 | 6 | ✓ |
| `record_blob_check` | L50-68 | 19 | 5 | 1 | 5 | ✓ |
| `build_choice_answer` | L84-89 | 6 | 5 | 1 | 2 | ✓ |
| `first_option_value` | L74-78 | 5 | 4 | 1 | 1 | ✓ |
| `build_exam_answers` | L111-117 | 7 | 3 | 1 | 1 | ✓ |
| `load_documented_paths` | L123-133 | 11 | 3 | 1 | 0 | ✓ |
| `run_document_checks` | L170-194 | 25 | 3 | 1 | 2 | ✓ |
| `build_auth_headers` | L139-141 | 3 | 2 | 0 | 1 | ✓ |

**全部问题 (1)**

- 📏 `record_check()` L24: 6 参数数量

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 7
- 认知复杂度: 平均: 6.3, 最大: 11
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 12.6 行, 最大: 25 行
- 文件长度: 135 代码量 (195 总计)
- 参数数量: 平均: 2.2, 最大: 6
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 0/6 个错误被忽略 (0.0%)
- 注释比例: 22.2% (30/135)
- 命名规范: 无命名违规

### 183. backend\tools\question_import_knowledge.py

**糟糕指数: 4.79**

> 行数: 114 总计, 80 代码, 17 注释 | 函数: 5 | 类: 0

**问题**: 🔄 复杂度问题: 1, ⚠️ 其他问题: 1, 🏗️ 结构问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `match_knowledge_point_by_topic` | L40-60 | 21 | 9 | 3 | 2 | ✓ |
| `normalize_knowledge_point_names` | L26-34 | 9 | 4 | 1 | 1 | ✓ |
| `link_question_knowledge_points` | L79-99 | 21 | 4 | 2 | 4 | ✓ |
| `resolve_filename_knowledge_point` | L105-113 | 9 | 2 | 1 | 2 | ✓ |
| `build_question_import_context` | L66-73 | 8 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 🔄 `match_knowledge_point_by_topic()` L40: 认知复杂度: 15
- 🏗️ `match_knowledge_point_by_topic()` L40: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 9
- 认知复杂度: 平均: 6.8, 最大: 15
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 13.6 行, 最大: 21 行
- 文件长度: 80 代码量 (114 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 1 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 21.3% (17/80)
- 命名规范: 无命名违规

### 184. backend\tools\neo4j_tools.py

**糟糕指数: 4.78**

> 行数: 165 总计, 108 代码, 22 注释 | 函数: 7 | 类: 0

**问题**: 📋 重复问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `neo4j_clear` | L72-92 | 21 | 6 | 2 | 2 | ✓ |
| `import_neo4j_test_data` | L118-140 | 23 | 5 | 1 | 0 | ✓ |
| `neo4j_status` | L36-46 | 11 | 4 | 1 | 0 | ✓ |
| `clear_neo4j_data` | L146-164 | 19 | 4 | 2 | 1 | ✓ |
| `sync_neo4j` | L17-30 | 14 | 3 | 1 | 1 | ✓ |
| `neo4j_sync_all` | L52-66 | 15 | 3 | 1 | 0 | ✓ |
| `test_neo4j_connection` | L100-112 | 13 | 3 | 1 | 0 | ✓ |

**全部问题 (1)**

- 📋 `neo4j_status()` L36: 重复模式: neo4j_status, test_neo4j_connection

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 6
- 认知复杂度: 平均: 6.6, 最大: 10
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 16.6 行, 最大: 23 行
- 文件长度: 108 代码量 (165 总计)
- 参数数量: 平均: 0.6, 最大: 2
- 代码重复: 14.3% 重复 (1/7)
- 结构分析: 0 个结构问题
- 错误处理: 0/17 个错误被忽略 (0.0%)
- 注释比例: 20.4% (22/108)
- 命名规范: 无命名违规

### 185. backend\courses\teacher_announcement_views.py

**糟糕指数: 4.76**

> 行数: 74 总计, 56 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `class_announcements` | L18-45 | 28 | 9 | 1 | 2 | ✓ |
| `announcement_detail` | L53-73 | 21 | 6 | 1 | 2 | ✓ |

**全部问题 (1)**

- ❌ L63: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 7.5, 最大: 9
- 认知复杂度: 平均: 9.5, 最大: 11
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 24.5 行, 最大: 28 行
- 文件长度: 56 代码量 (74 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/8 个错误被忽略 (12.5%)
- 注释比例: 10.7% (6/56)
- 命名规范: 无命名违规

### 186. backend\courses\teacher_course_helpers.py

**糟糕指数: 4.75**

> 行数: 49 总计, 35 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `extract_course_archive` | L25-36 | 12 | 5 | 2 | 1 | ✓ |
| `resolve_archive_root` | L42-48 | 7 | 4 | 1 | 1 | ✓ |

**全部问题 (2)**

- ❌ L31: 未处理的易出错调用
- ❌ L33: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 5
- 认知复杂度: 平均: 7.5, 最大: 9
- 嵌套深度: 平均: 1.5, 最大: 2
- 函数长度: 平均: 9.5 行, 最大: 12 行
- 文件长度: 35 代码量 (49 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 2/2 个错误被忽略 (100.0%)
- 注释比例: 17.1% (6/35)
- 命名规范: 无命名违规

### 187. backend\tools\course_cleanup.py

**糟糕指数: 4.73**

> 行数: 46 总计, 34 代码, 5 注释 | 函数: 1 | 类: 0

**问题**: ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `delete_course_with_cleanup` | L14-45 | 32 | 4 | 2 | 2 | ✓ |

**全部问题 (1)**

- ❌ L29: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 8.0, 最大: 8
- 嵌套深度: 平均: 2.0, 最大: 2
- 函数长度: 平均: 32.0 行, 最大: 32 行
- 文件长度: 34 代码量 (46 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 14.7% (5/34)
- 命名规范: 无命名违规

### 188. frontend\src\views\teacher\useTeacherQuestionList.js

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

### 189. backend\tools\db_demo_preset.py

**糟糕指数: 4.69**

> 行数: 198 总计, 159 代码, 15 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `preset_student1_demo_data` | L42-107 | 66 | 5 | 1 | 2 | ✓ |
| `preset_student1_demo_course_state` | L181-197 | 17 | 4 | 1 | 1 | ✓ |
| `persist_student1_profile_and_feedback` | L113-147 | 35 | 2 | 0 | 6 | ✓ |
| `print_student1_preset_result` | L153-164 | 12 | 1 | 0 | 4 | ✓ |
| `_preset_student1_demo_data` | L170-175 | 6 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- 📏 `preset_student1_demo_data()` L42: 66 代码量
- 📏 `persist_student1_profile_and_feedback()` L113: 6 参数数量
- 🏷️ `_preset_student1_demo_data()` L170: "_preset_student1_demo_data" - snake_case

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 5
- 认知复杂度: 平均: 3.4, 最大: 7
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 27.2 行, 最大: 66 行
- 文件长度: 159 代码量 (198 总计)
- 参数数量: 平均: 3.0, 最大: 6
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 9.4% (15/159)
- 命名规范: 发现 1 个违规

### 190. backend\platform_ai\llm\agent_message.py

**糟糕指数: 4.68**

> 行数: 43 总计, 25 代码, 9 注释 | 函数: 3 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `extract_agent_message_text` | L8-12 | 5 | 4 | 1 | 1 | ✓ |
| `extract_content_part_text` | L29-35 | 7 | 4 | 1 | 1 | ✓ |
| `extract_message_content` | L18-23 | 6 | 2 | 1 | 1 | ✓ |

**全部问题 (1)**

- ❌ L33: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 4
- 认知复杂度: 平均: 5.3, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 6.0 行, 最大: 7 行
- 文件长度: 25 代码量 (43 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 36.0% (9/25)
- 命名规范: 无命名违规

### 191. backend\tools\knowledge.py

**糟糕指数: 4.67**

> 行数: 165 总计, 118 代码, 21 注释 | 函数: 7 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 2, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_knowledge_map` | L80-110 | 31 | 7 | 1 | 3 | ✓ |
| `import_knowledge` | L40-74 | 35 | 5 | 2 | 4 | ✓ |
| `export_knowledge_map` | L140-164 | 25 | 3 | 0 | 2 | ✓ |
| `validate_json` | L31-34 | 4 | 1 | 0 | 2 | ✓ |
| `_parse_knowledge_excel` | L116-118 | 3 | 1 | 0 | 1 | ✓ |
| `_parse_hierarchical_excel` | L124-126 | 3 | 1 | 0 | 2 | ✓ |
| `_parse_flat_excel` | L132-134 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (5)**

- ❌ L108: 未处理的易出错调用
- ❌ L109: 未处理的易出错调用
- 🏷️ `_parse_knowledge_excel()` L116: "_parse_knowledge_excel" - snake_case
- 🏷️ `_parse_hierarchical_excel()` L124: "_parse_hierarchical_excel" - snake_case
- 🏷️ `_parse_flat_excel()` L132: "_parse_flat_excel" - snake_case

**详情**:
- 循环复杂度: 平均: 2.7, 最大: 7
- 认知复杂度: 平均: 3.6, 最大: 9
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 14.9 行, 最大: 35 行
- 文件长度: 118 代码量 (165 总计)
- 参数数量: 平均: 2.1, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 2/9 个错误被忽略 (22.2%)
- 注释比例: 17.8% (21/118)
- 命名规范: 发现 3 个违规

### 192. backend\ai_services\services\kt_model_runtime.py

**糟糕指数: 4.67**

> 行数: 147 总计, 117 代码, 12 注释 | 函数: 3 | 类: 1

**问题**: ⚠️ 其他问题: 2, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_predict_with_mefkt` | L91-146 | 56 | 4 | 2 | 4 | ✓ |
| `_load_course_knowledge_point_ids` | L26-48 | 23 | 3 | 1 | 2 | ✓ |
| `_run_model_prediction` | L53-86 | 34 | 3 | 1 | 5 | ✓ |

**全部问题 (4)**

- 📏 `_predict_with_mefkt()` L91: 56 代码量
- 🏷️ `_load_course_knowledge_point_ids()` L26: "_load_course_knowledge_point_ids" - snake_case
- 🏷️ `_run_model_prediction()` L53: "_run_model_prediction" - snake_case
- 🏷️ `_predict_with_mefkt()` L91: "_predict_with_mefkt" - snake_case

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 4
- 认知复杂度: 平均: 6.0, 最大: 8
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 37.7 行, 最大: 56 行
- 文件长度: 117 代码量 (147 总计)
- 参数数量: 平均: 3.7, 最大: 5
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 10.3% (12/117)
- 命名规范: 发现 3 个违规

### 193. backend\ai_services\student_rag_support.py

**糟糕指数: 4.65**

> 行数: 224 总计, 155 代码, 36 注释 | 函数: 12 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_path_constraints` | L57-63 | 7 | 4 | 1 | 3 | ✓ |
| `demo_intro_payload` | L146-151 | 6 | 3 | 1 | 2 | ✓ |
| `merge_intro_payload` | L208-215 | 8 | 3 | 1 | 2 | ✓ |
| `resolve_course` | L26-31 | 6 | 2 | 1 | 1 | ✓ |
| `plan_student_path` | L69-108 | 40 | 2 | 1 | 5 | ✓ |
| `log_path_planning_call` | L114-129 | 16 | 2 | 0 | 5 | ✓ |
| `resolve_intro_point` | L135-140 | 6 | 2 | 1 | 3 | ✓ |
| `node_intro_cache_key` | L157-159 | 3 | 2 | 0 | 4 | ✓ |
| `cached_node_intro` | L165-168 | 4 | 2 | 0 | 1 | ✓ |
| `build_node_intro_payload` | L174-202 | 29 | 2 | 1 | 5 | ✓ |
| `build_mastery_data` | L37-51 | 15 | 1 | 0 | 2 | ✓ |
| `cache_node_intro` | L221-223 | 3 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- ❌ L106: 未处理的易出错调用
- ❌ L107: 未处理的易出错调用
- ❌ L123: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 4
- 认知复杂度: 平均: 3.3, 最大: 6
- 嵌套深度: 平均: 0.6, 最大: 1
- 函数长度: 平均: 11.9 行, 最大: 40 行
- 文件长度: 155 代码量 (224 总计)
- 参数数量: 平均: 2.9, 最大: 5
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 3/7 个错误被忽略 (42.9%)
- 注释比例: 23.2% (36/155)
- 命名规范: 无命名违规

### 194. backend\learning\stage_test_demo_submission.py

**糟糕指数: 4.63**

> 行数: 123 总计, 93 代码, 15 注释 | 函数: 5 | 类: 0

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `apply_demo_mastery` | L74-89 | 16 | 3 | 1 | 3 | ✓ |
| `submit_demo_stage_test` | L18-51 | 34 | 2 | 1 | 7 | ✓ |
| `update_demo_node_status` | L57-68 | 12 | 2 | 1 | 4 | ✓ |
| `apply_single_demo_mastery` | L95-113 | 19 | 2 | 1 | 4 | ✓ |
| `demo_feedback_report` | L119-122 | 4 | 2 | 0 | 1 | ✓ |

**全部问题 (1)**

- 📏 `submit_demo_stage_test()` L18: 7 参数数量

**详情**:
- 循环复杂度: 平均: 2.2, 最大: 3
- 认知复杂度: 平均: 3.8, 最大: 5
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 17.0 行, 最大: 34 行
- 文件长度: 93 代码量 (123 总计)
- 参数数量: 平均: 3.8, 最大: 7
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 16.1% (15/93)
- 命名规范: 无命名违规

### 195. backend\learning\student_rag_support.py

**糟糕指数: 4.63**

> 行数: 165 总计, 112 代码, 27 注释 | 函数: 9 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_fallback_resource_payload` | L150-164 | 15 | 4 | 0 | 3 | ✓ |
| `build_ai_resource_payload` | L31-51 | 21 | 3 | 1 | 2 | ✓ |
| `defense_demo_resource_payload` | L65-78 | 14 | 3 | 1 | 3 | ✓ |
| `completed_resource_id_set` | L84-88 | 5 | 3 | 1 | 1 | ✓ |
| `mastery_before_value` | L94-98 | 5 | 3 | 1 | 1 | ✓ |
| `recommend_node_resources` | L104-130 | 27 | 3 | 1 | 4 | ✓ |
| `get_student_path_node` | L19-25 | 7 | 1 | 0 | 2 | ✓ |
| `empty_resource_payload` | L57-59 | 3 | 1 | 0 | 0 | ✓ |
| `fallback_node_resources` | L136-144 | 9 | 1 | 0 | 2 | ✓ |

**全部问题 (4)**

- ❌ L49: 未处理的易出错调用
- ❌ L50: 未处理的易出错调用
- ❌ L75: 未处理的易出错调用
- ❌ L76: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 4
- 认知复杂度: 平均: 3.6, 最大: 5
- 嵌套深度: 平均: 0.6, 最大: 1
- 函数长度: 平均: 11.8 行, 最大: 27 行
- 文件长度: 112 代码量 (165 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 4/4 个错误被忽略 (100.0%)
- 注释比例: 24.1% (27/112)
- 命名规范: 无命名违规

### 196. backend\knowledge\teacher_map_views.py

**糟糕指数: 4.62**

> 行数: 206 总计, 155 代码, 18 注释 | 函数: 6 | 类: 0

**问题**: 🔄 复杂度问题: 2, 🏗️ 结构问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `knowledge_map_import` | L67-107 | 41 | 11 | 1 | 1 | ✓ |
| `knowledge_graph_save` | L37-59 | 23 | 5 | 1 | 1 | ✓ |
| `knowledge_map_publish` | L115-133 | 19 | 4 | 1 | 1 | ✓ |
| `knowledge_map_export` | L157-182 | 26 | 3 | 1 | 1 | ✓ |
| `knowledge_map_build_rag_index` | L141-149 | 9 | 2 | 1 | 1 | ✓ |
| `knowledge_map_template` | L190-205 | 16 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 🔄 `knowledge_map_import()` L67: 复杂度: 11
- 🔄 `knowledge_map_import()` L67: 认知复杂度: 13

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 11
- 认知复杂度: 平均: 6.0, 最大: 13
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 22.3 行, 最大: 41 行
- 文件长度: 155 代码量 (206 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 11.6% (18/155)
- 命名规范: 无命名违规

### 197. backend\common\defense_demo_progress.py

**糟糕指数: 4.61**

> 行数: 221 总计, 159 代码, 33 注释 | 函数: 11 | 类: 0

**问题**: 🏷️ 命名问题: 9

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_coerce_mastery_after_map` | L93-109 | 17 | 8 | 2 | 1 | ✓ |
| `_question_options` | L62-75 | 14 | 4 | 2 | 1 | ✓ |
| `_activate_next_locked_node` | L16-29 | 14 | 3 | 1 | 1 | ✓ |
| `_as_object_dict` | L81-87 | 7 | 2 | 0 | 1 | ✓ |
| `_average_snapshot` | L115-123 | 9 | 2 | 1 | 1 | ✓ |
| `_build_mastery_change_payload` | L154-179 | 26 | 2 | 1 | 3 | ✓ |
| `advance_defense_demo_path` | L185-196 | 12 | 2 | 0 | 3 | ✓ |
| `_set_related_knowledge_points` | L35-43 | 9 | 1 | 0 | 2 | ✓ |
| `_question_knowledge_points` | L49-56 | 8 | 1 | 0 | 1 | ✓ |
| `_capture_mastery_snapshot` | L129-148 | 20 | 1 | 0 | 3 | ✓ |
| `complete_defense_demo_stage_test` | L202-220 | 19 | 1 | 0 | 3 | ✓ |

**全部问题 (9)**

- 🏷️ `_activate_next_locked_node()` L16: "_activate_next_locked_node" - snake_case
- 🏷️ `_set_related_knowledge_points()` L35: "_set_related_knowledge_points" - snake_case
- 🏷️ `_question_knowledge_points()` L49: "_question_knowledge_points" - snake_case
- 🏷️ `_question_options()` L62: "_question_options" - snake_case
- 🏷️ `_as_object_dict()` L81: "_as_object_dict" - snake_case
- 🏷️ `_coerce_mastery_after_map()` L93: "_coerce_mastery_after_map" - snake_case
- 🏷️ `_average_snapshot()` L115: "_average_snapshot" - snake_case
- 🏷️ `_capture_mastery_snapshot()` L129: "_capture_mastery_snapshot" - snake_case
- 🏷️ `_build_mastery_change_payload()` L154: "_build_mastery_change_payload" - snake_case

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 8
- 认知复杂度: 平均: 3.7, 最大: 12
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 14.1 行, 最大: 26 行
- 文件长度: 159 代码量 (221 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 20.8% (33/159)
- 命名规范: 发现 9 个违规

### 198. backend\tools\api_regression_student.py

**糟糕指数: 4.60**

> 行数: 53 总计, 44 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_run_student_regression` | L19-52 | 34 | 1 | 0 | 5 | ✓ |

**全部问题 (1)**

- 🏷️ `_run_student_regression()` L19: "_run_student_regression" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 34.0 行, 最大: 34 行
- 文件长度: 44 代码量 (53 总计)
- 参数数量: 平均: 5.0, 最大: 5
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 6.8% (3/44)
- 命名规范: 发现 1 个违规

### 199. backend\exams\student_feedback_views.py

**糟糕指数: 4.58**

> 行数: 93 总计, 73 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_feedback_report` | L23-74 | 52 | 9 | 1 | 1 | ✓ |
| `get_feedback_report` | L82-92 | 11 | 4 | 1 | 2 | ✓ |

**全部问题 (1)**

- 📏 `generate_feedback_report()` L23: 52 代码量

**详情**:
- 循环复杂度: 平均: 6.5, 最大: 9
- 认知复杂度: 平均: 8.5, 最大: 11
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 31.5 行, 最大: 52 行
- 文件长度: 73 代码量 (93 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/6 个错误被忽略 (0.0%)
- 注释比例: 8.2% (6/73)
- 命名规范: 无命名违规

### 200. backend\exams\teacher_result_views.py

**糟糕指数: 4.54**

> 行数: 225 总计, 172 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `exam_student_detail` | L76-116 | 41 | 6 | 1 | 3 | ✓ |
| `teacher_exam_export` | L182-215 | 34 | 6 | 1 | 2 | ✓ |
| `exam_analysis` | L124-174 | 51 | 4 | 1 | 2 | ✓ |
| `exam_results` | L35-68 | 34 | 3 | 1 | 2 | ✓ |

**全部问题 (2)**

- 📏 `exam_analysis()` L124: 51 代码量
- ❌ L201: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 6
- 认知复杂度: 平均: 6.8, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 40.0 行, 最大: 51 行
- 文件长度: 172 代码量 (225 总计)
- 参数数量: 平均: 2.3, 最大: 3
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 7.0% (12/172)
- 命名规范: 无命名违规

### 201. backend\tools\question_import_answers.py

**糟糕指数: 4.51**

> 行数: 74 总计, 50 代码, 11 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_excel_answer` | L37-50 | 14 | 9 | 2 | 2 | ✓ |
| `normalize_true_false_options` | L56-73 | 18 | 6 | 2 | 2 | ✓ |
| `normalize_question_answer` | L24-31 | 8 | 4 | 1 | 1 | ✓ |

**全部问题 (1)**

- 🔄 `build_excel_answer()` L37: 认知复杂度: 13

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 9
- 认知复杂度: 平均: 9.7, 最大: 13
- 嵌套深度: 平均: 1.7, 最大: 2
- 函数长度: 平均: 13.3 行, 最大: 18 行
- 文件长度: 50 代码量 (74 总计)
- 参数数量: 平均: 1.7, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 22.0% (11/50)
- 命名规范: 无命名违规

### 202. backend\exams\report_generation_support.py

**糟糕指数: 4.51**

> 行数: 289 总计, 219 代码, 32 注释 | 函数: 10 | 类: 0

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_detailed_mistakes` | L162-190 | 29 | 7 | 2 | 2 | ✓ |
| `persist_failed_report` | L264-275 | 12 | 6 | 0 | 2 | ✓ |
| `refresh_kt_analysis` | L108-156 | 49 | 5 | 2 | 4 | ✓ |
| `build_answer_history_records` | L43-67 | 25 | 4 | 2 | 2 | ✓ |
| `persist_kt_predictions` | L73-102 | 30 | 3 | 2 | 4 | ✓ |
| `extract_habit_preferences` | L196-208 | 13 | 2 | 1 | 1 | ✓ |
| `normalize_llm_list` | L214-217 | 4 | 2 | 0 | 2 | ✓ |
| `save_llm_call_log` | L231-258 | 28 | 2 | 1 | 5 | ✓ |
| `load_report_with_dependencies` | L29-37 | 9 | 1 | 0 | 1 | ✓ |
| `mapping_value` | L223-225 | 3 | 1 | 0 | 3 | ✓ |

**全部问题 (1)**

- ❌ L243: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 7
- 认知复杂度: 平均: 5.3, 最大: 11
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 20.2 行, 最大: 49 行
- 文件长度: 219 代码量 (289 总计)
- 参数数量: 平均: 2.6, 最大: 5
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 1/8 个错误被忽略 (12.5%)
- 注释比例: 14.6% (32/219)
- 命名规范: 无命名违规

### 203. backend\users\admin_user_management_support.py

**糟糕指数: 4.42**

> 行数: 410 总计, 271 代码, 75 注释 | 函数: 24 | 类: 1

**问题**: 🏗️ 结构问题: 1, ❌ 错误处理问题: 5, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_admin_user_detail_payload` | L116-130 | 15 | 7 | 0 | 1 | ✓ |
| `build_user_export_row` | L374-386 | 13 | 7 | 0 | 1 | ✓ |
| `update_admin_user` | L162-176 | 15 | 6 | 2 | 2 | ✓ |
| `read_user_excel_rows` | L277-296 | 20 | 6 | 2 | 1 | ✓ |
| `filtered_admin_users` | L65-85 | 21 | 5 | 1 | 1 | ✓ |
| `create_admin_user` | L136-156 | 21 | 5 | 1 | 1 | ✓ |
| `import_admin_users` | L302-313 | 12 | 5 | 3 | 1 | ✓ |
| `create_user_from_import_row` | L319-338 | 20 | 5 | 1 | 2 | ✓ |
| `build_admin_user_list_item` | L91-102 | 12 | 4 | 0 | 1 | ✓ |
| `read_user_import_rows` | L252-262 | 11 | 4 | 2 | 1 | ✓ |
| `reset_admin_user_password` | L192-202 | 11 | 3 | 1 | 2 | ✓ |
| `normalize_delete_user_ids` | L238-246 | 9 | 3 | 1 | 2 | ✓ |
| `first_row_value` | L344-350 | 7 | 3 | 2 | 2 | ✓ |
| `build_user_export_response` | L356-368 | 13 | 3 | 1 | 1 | ✓ |
| `set_admin_user_active` | L217-222 | 6 | 2 | 0 | 2 | ✓ |
| `read` | L42-43 | 2 | 1 | 0 | 1 | ✓ |
| `build_admin_user_list_payload` | L49-59 | 11 | 1 | 0 | 3 | ✓ |
| `get_admin_user` | L108-110 | 3 | 1 | 0 | 1 | ✓ |
| `delete_admin_user` | L182-186 | 5 | 1 | 0 | 1 | ✓ |
| `generate_random_password` | L208-211 | 4 | 1 | 0 | 1 | ✓ |
| `delete_admin_users` | L228-232 | 5 | 1 | 0 | 2 | ✓ |
| `read_user_csv_rows` | L268-271 | 4 | 1 | 0 | 1 | ✓ |
| `build_user_import_template_response` | L392-398 | 7 | 1 | 0 | 0 | ✓ |
| `build_csv_response` | L404-409 | 6 | 1 | 0 | 1 | ✓ |

**全部问题 (6)**

- 🏗️ `import_admin_users()` L302: 中等嵌套: 3
- ❌ L42: 未处理的易出错调用
- ❌ L185: 未处理的易出错调用
- ❌ L231: 忽略了错误返回值
- ❌ L296: 未处理的易出错调用
- ❌ L408: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.2, 最大: 7
- 认知复杂度: 平均: 4.6, 最大: 11
- 嵌套深度: 平均: 0.7, 最大: 3
- 函数长度: 平均: 10.5 行, 最大: 21 行
- 文件长度: 271 代码量 (410 总计)
- 参数数量: 平均: 1.3, 最大: 3
- 代码重复: 4.2% 重复 (1/24)
- 结构分析: 1 个结构问题
- 错误处理: 5/17 个错误被忽略 (29.4%)
- 注释比例: 27.7% (75/271)
- 命名规范: 无命名违规

### 204. backend\common\defense_demo_config.py

**糟糕指数: 4.27**

> 行数: 151 总计, 144 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_get_demo_assessment_preset` | L141-150 | 10 | 2 | 1 | 1 | ✓ |

**全部问题 (1)**

- 🏷️ `_get_demo_assessment_preset()` L141: "_get_demo_assessment_preset" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 10.0 行, 最大: 10 行
- 文件长度: 144 代码量 (151 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 2.1% (3/144)
- 命名规范: 发现 1 个违规

### 205. backend\courses\teacher_course_views.py

**糟糕指数: 4.26**

> 行数: 156 总计, 101 代码, 30 注释 | 函数: 10 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `course_update` | L65-76 | 12 | 4 | 1 | 2 | ✓ |
| `teacher_course_error_response` | L40-44 | 5 | 2 | 1 | 2 | ✓ |
| `course_create` | L52-57 | 6 | 2 | 1 | 1 | ✓ |
| `course_delete` | L94-99 | 6 | 2 | 1 | 2 | ✓ |
| `teacher_course_cover_upload` | L107-112 | 6 | 2 | 1 | 2 | ✓ |
| `teacher_course_statistics` | L120-125 | 6 | 2 | 1 | 2 | ✓ |
| `get_course_settings` | L133-138 | 6 | 2 | 1 | 2 | ✓ |
| `update_course_settings` | L146-155 | 10 | 2 | 1 | 2 | ✓ |
| `course_search` | L32-34 | 3 | 1 | 0 | 1 | ✓ |
| `my_created_courses` | L84-86 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- ❌ L151: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 4
- 认知复杂度: 平均: 3.6, 最大: 6
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 6.3 行, 最大: 12 行
- 文件长度: 101 代码量 (156 总计)
- 参数数量: 平均: 1.7, 最大: 2
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 1/1 个错误被忽略 (100.0%)
- 注释比例: 29.7% (30/101)
- 命名规范: 无命名违规

### 206. backend\exams\tests.py

**糟糕指数: 4.23**

> 行数: 330 总计, 252 代码, 43 注释 | 函数: 11 | 类: 3

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 4, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_model_id` | L28-33 | 6 | 3 | 1 | 1 | ✓ |
| `test_exam_submit_should_use_question_accuracy_and_normalized_score` | L141-186 | 46 | 3 | 1 | 1 | ✓ |
| `_api_client` | L20-22 | 3 | 1 | 0 | 1 | ✓ |
| `setUp` | L43-72 | 30 | 1 | 0 | 1 | ✓ |
| `_create_exam` | L77-93 | 17 | 1 | 0 | 3 | ✓ |
| `test_exam_submit_low_score_should_not_pass` | L98-114 | 17 | 1 | 0 | 1 | ✓ |
| `test_exam_result_should_use_fallback_threshold_when_pass_score_invalid` | L119-136 | 18 | 1 | 0 | 1 | ✓ |
| `test_true_false_answer_display_should_be_human_readable` | L196-205 | 10 | 1 | 0 | 1 | ✗ |
| `setUp` | L215-264 | 50 | 1 | 0 | 1 | ✓ |
| `test_submit_should_create_pending_report_and_enqueue_worker` | L271-292 | 22 | 1 | 0 | 3 | ✗ |
| `test_get_feedback_should_return_pending_state` | L297-329 | 33 | 1 | 0 | 1 | ✓ |

**全部问题 (10)**

- 📋 `test_exam_submit_low_score_should_not_pass()` L98: 重复模式: test_exam_submit_low_score_should_not_pass, test_submit_should_create_pending_report_and_enqueue_worker
- ❌ L87: 未处理的易出错调用
- ❌ L122: 未处理的易出错调用
- ❌ L258: 未处理的易出错调用
- ❌ L305: 未处理的易出错调用
- 🏷️ `_api_client()` L20: "_api_client" - snake_case
- 🏷️ `_model_id()` L28: "_model_id" - snake_case
- 🏷️ `setUp()` L43: "setUp" - snake_case
- 🏷️ `_create_exam()` L77: "_create_exam" - snake_case
- 🏷️ `setUp()` L215: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 3
- 认知复杂度: 平均: 1.7, 最大: 5
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 22.9 行, 最大: 50 行
- 文件长度: 252 代码量 (330 总计)
- 参数数量: 平均: 1.4, 最大: 3
- 代码重复: 9.1% 重复 (1/11)
- 结构分析: 0 个结构问题
- 错误处理: 4/23 个错误被忽略 (17.4%)
- 注释比例: 17.1% (43/252)
- 命名规范: 发现 5 个违规

### 207. backend\exams\teacher_question_views.py

**糟糕指数: 4.23**

> 行数: 176 总计, 129 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `question_list` | L19-64 | 46 | 8 | 1 | 1 | ✓ |
| `question_update` | L118-147 | 30 | 8 | 2 | 2 | ✓ |
| `question_delete` | L155-167 | 13 | 5 | 1 | 2 | ✓ |
| `question_create` | L72-110 | 39 | 4 | 1 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 6.3, 最大: 8
- 认知复杂度: 平均: 8.8, 最大: 12
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 32.0 行, 最大: 46 行
- 文件长度: 129 代码量 (176 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 1/21 个错误被忽略 (4.8%)
- 注释比例: 9.3% (12/129)
- 命名规范: 无命名违规

### 208. backend\platform_ai\rag\student_dependencies.py

**糟糕指数: 4.19**

> 行数: 34 总计, 16 代码, 12 注释 | 函数: 3 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_runtime` | L14-17 | 4 | 1 | 0 | 1 | ✓ |
| `_llm_facade` | L22-25 | 4 | 1 | 0 | 1 | ✓ |
| `_resource_mcp_service` | L30-33 | 4 | 1 | 0 | 1 | ✓ |

**全部问题 (3)**

- 🏷️ `_runtime()` L14: "_runtime" - snake_case
- 🏷️ `_llm_facade()` L22: "_llm_facade" - snake_case
- 🏷️ `_resource_mcp_service()` L30: "_resource_mcp_service" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.0 行, 最大: 4 行
- 文件长度: 16 代码量 (34 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 75.0% (12/16)
- 命名规范: 发现 3 个违规

### 209. frontend\src\views\teacher\questionListModels.js

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

### 210. backend\tools\survey.py

**糟糕指数: 4.10**

> 行数: 280 总计, 179 代码, 54 注释 | 函数: 14 | 类: 4

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_survey_questions` | L75-99 | 25 | 4 | 1 | 3 | ✓ |
| `persist_survey_questions` | L171-190 | 20 | 4 | 3 | 4 | ✓ |
| `resolve_option_score` | L250-262 | 13 | 4 | 1 | 3 | ✓ |
| `find_first_matching_column` | L134-141 | 8 | 3 | 2 | 2 | ✓ |
| `find_named_column` | L159-165 | 7 | 3 | 2 | 2 | ✓ |
| `create_question_from_row` | L196-223 | 28 | 3 | 1 | 5 | ✓ |
| `build_survey_options` | L229-244 | 16 | 3 | 2 | 2 | ✓ |
| `resolve_dimension` | L268-271 | 4 | 3 | 0 | 2 | ✓ |
| `import_pandas` | L105-112 | 8 | 2 | 1 | 0 | ✓ |
| `resolve_survey_columns` | L118-128 | 11 | 2 | 0 | 1 | ✓ |
| `resolve_option_columns` | L147-153 | 7 | 2 | 1 | 2 | ✓ |
| `iterrows` | L32-33 | 2 | 1 | 0 | 1 | ✓ |
| `read_excel` | L45-46 | 2 | 1 | 0 | 2 | ✓ |
| `import_ability_scale` | L277-279 | 3 | 1 | 0 | 2 | ✓ |

**全部问题 (2)**

- 🏗️ `persist_survey_questions()` L171: 中等嵌套: 3
- ❌ L213: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.6, 最大: 4
- 认知复杂度: 平均: 4.6, 最大: 10
- 嵌套深度: 平均: 1.0, 最大: 3
- 函数长度: 平均: 11.0 行, 最大: 28 行
- 文件长度: 179 代码量 (280 总计)
- 参数数量: 平均: 2.2, 最大: 5
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 1 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 30.2% (54/179)
- 命名规范: 无命名违规

### 211. backend\exams\student_exam_support.py

**糟糕指数: 4.08**

> 行数: 284 总计, 193 代码, 51 注释 | 函数: 16 | 类: 1

**问题**: ❌ 错误处理问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `serialize_exam_summary` | L171-190 | 20 | 9 | 0 | 2 | ✓ |
| `resolve_exam_detail_access_error` | L217-226 | 10 | 6 | 1 | 2 | ✓ |
| `normalize_query_value` | L63-67 | 5 | 3 | 1 | 1 | ✓ |
| `build_visible_exam_queryset` | L92-100 | 9 | 3 | 1 | 2 | ✓ |
| `apply_exam_filters` | L106-112 | 7 | 3 | 1 | 2 | ✓ |
| `resolve_submission_score` | L196-200 | 5 | 3 | 1 | 1 | ✓ |
| `apply_student_exam_visibility` | L118-129 | 12 | 2 | 1 | 3 | ✓ |
| `build_submission_map` | L157-165 | 9 | 2 | 1 | 2 | ✓ |
| `get_published_exam` | L206-211 | 6 | 2 | 1 | 1 | ✓ |
| `offset` | L34-36 | 3 | 1 | 0 | 1 | ✓ |
| `limit` | L42-44 | 3 | 1 | 0 | 1 | ✓ |
| `parse_exam_list_params` | L50-57 | 8 | 1 | 0 | 1 | ✓ |
| `build_exam_list_payload` | L73-86 | 14 | 1 | 0 | 2 | ✓ |
| `load_student_exam_scope` | L135-151 | 17 | 1 | 0 | 1 | ✓ |
| `build_exam_detail_payload` | L232-251 | 20 | 1 | 0 | 1 | ✓ |
| `serialize_exam_question` | L257-269 | 13 | 1 | 0 | 2 | ✓ |

**全部问题 (2)**

- ❌ L83: 未处理的易出错调用
- ❌ L268: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 9
- 认知复杂度: 平均: 3.5, 最大: 9
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 10.1 行, 最大: 20 行
- 文件长度: 193 代码量 (284 总计)
- 参数数量: 平均: 1.6, 最大: 3
- 代码重复: 0.0% 重复 (0/16)
- 结构分析: 0 个结构问题
- 错误处理: 2/7 个错误被忽略 (28.6%)
- 注释比例: 26.4% (51/193)
- 命名规范: 无命名违规

### 212. backend\assessments\serializers.py

**糟糕指数: 3.98**

> 行数: 210 总计, 110 代码, 66 注释 | 函数: 8 | 类: 8

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_clean_options` | L26-37 | 12 | 7 | 2 | 1 | ✓ |
| `_clean_html` | L15-20 | 6 | 3 | 1 | 1 | ✓ |
| `get_points` | L62-64 | 3 | 1 | 0 | 1 | ✓ |
| `to_representation` | L69-75 | 7 | 1 | 0 | 2 | ✓ |
| `get_points` | L98-100 | 3 | 1 | 0 | 1 | ✓ |
| `get_points` | L124-127 | 4 | 1 | 0 | 1 | ✓ |
| `get_points` | L165-167 | 3 | 1 | 0 | 1 | ✓ |
| `to_representation` | L172-177 | 6 | 1 | 0 | 2 | ✓ |

**全部问题 (2)**

- 🏷️ `_clean_html()` L15: "_clean_html" - snake_case
- 🏷️ `_clean_options()` L26: "_clean_options" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 7
- 认知复杂度: 平均: 2.8, 最大: 11
- 嵌套深度: 平均: 0.4, 最大: 2
- 函数长度: 平均: 5.5 行, 最大: 12 行
- 文件长度: 110 代码量 (210 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 0/5 个错误被忽略 (0.0%)
- 注释比例: 60.0% (66/110)
- 命名规范: 发现 2 个违规

### 213. backend\models\MEFKT\graph.py

**糟糕指数: 3.95**

> 行数: 170 总计, 122 代码, 21 注释 | 函数: 7 | 类: 2

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `load_compatible_state` | L36-62 | 27 | 4 | 2 | 2 | ✓ |
| `normalize_dense_adjacency` | L13-30 | 18 | 1 | 0 | 1 | ✓ |
| `__init__` | L71-79 | 9 | 1 | 0 | 3 | ✓ |
| `forward` | L84-93 | 10 | 1 | 0 | 3 | ✓ |
| `__init__` | L102-113 | 12 | 1 | 0 | 4 | ✓ |
| `encode` | L118-129 | 12 | 1 | 0 | 3 | ✓ |
| `contrastive_loss` | L134-161 | 28 | 1 | 0 | 3 | ✓ |

**全部问题 (3)**

- ❌ L118: 未处理的易出错调用
- 🏷️ `__init__()` L71: "__init__" - snake_case
- 🏷️ `__init__()` L102: "__init__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 4
- 认知复杂度: 平均: 2.0, 最大: 8
- 嵌套深度: 平均: 0.3, 最大: 2
- 函数长度: 平均: 16.6 行, 最大: 28 行
- 文件长度: 122 代码量 (170 总计)
- 参数数量: 平均: 2.7, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 17.2% (21/122)
- 命名规范: 发现 2 个违规

### 214. backend\learning\node_progress_views.py

**糟糕指数: 3.93**

> 行数: 322 总计, 238 代码, 32 注释 | 函数: 8 | 类: 0

**问题**: ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_ai_resources` | L210-254 | 45 | 8 | 1 | 2 | ✓ |
| `get_learning_progress` | L18-67 | 50 | 6 | 1 | 1 | ✓ |
| `start_learning_node` | L75-101 | 27 | 4 | 1 | 2 | ✓ |
| `complete_path_node` | L109-144 | 36 | 4 | 2 | 2 | ✓ |
| `get_node_exams` | L262-287 | 26 | 4 | 1 | 2 | ✓ |
| `skip_path_node` | L152-181 | 30 | 3 | 1 | 2 | ✓ |
| `pause_node_resource` | L295-321 | 27 | 3 | 1 | 3 | ✓ |
| `get_node_resources` | L189-202 | 14 | 2 | 1 | 2 | ✓ |

**全部问题 (2)**

- ❌ L250: 未处理的易出错调用
- ❌ L251: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 8
- 认知复杂度: 平均: 6.5, 最大: 10
- 嵌套深度: 平均: 1.1, 最大: 2
- 函数长度: 平均: 31.9 行, 最大: 50 行
- 文件长度: 238 代码量 (322 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 2/10 个错误被忽略 (20.0%)
- 注释比例: 13.4% (32/238)
- 命名规范: 无命名违规

### 215. backend\tools\api_regression.py

**糟糕指数: 3.92**

> 行数: 88 总计, 69 代码, 5 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `api_regression` | L24-87 | 64 | 6 | 1 | 3 | ✓ |

**全部问题 (1)**

- 📏 `api_regression()` L24: 64 代码量

**详情**:
- 循环复杂度: 平均: 6.0, 最大: 6
- 认知复杂度: 平均: 8.0, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 64.0 行, 最大: 64 行
- 文件长度: 69 代码量 (88 总计)
- 参数数量: 平均: 3.0, 最大: 3
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 7.2% (5/69)
- 命名规范: 无命名违规

### 216. backend\exams\student_initial_assessment_support.py

**糟糕指数: 3.86**

> 行数: 348 总计, 255 代码, 48 注释 | 函数: 13 | 类: 3

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `score_initial_assessment` | L126-169 | 44 | 4 | 1 | 4 | ✓ |
| `apply_kt_initial_mastery` | L236-271 | 36 | 4 | 2 | 4 | ✓ |
| `create_initial_answer_history` | L175-192 | 18 | 3 | 1 | 1 | ✓ |
| `update_question_stats` | L198-207 | 10 | 3 | 2 | 3 | ✓ |
| `update_rule_based_mastery` | L213-230 | 18 | 3 | 1 | 3 | ✓ |
| `persist_kt_predictions` | L297-324 | 28 | 3 | 2 | 4 | ✓ |
| `select_initial_questions` | L70-82 | 13 | 2 | 1 | 1 | ✓ |
| `parse_answer_question_ids` | L105-110 | 6 | 2 | 1 | 1 | ✓ |
| `build_initial_kt_history` | L277-291 | 15 | 2 | 0 | 2 | ✓ |
| `serialize_initial_questions` | L88-99 | 12 | 1 | 0 | 1 | ✓ |
| `load_answered_questions` | L116-120 | 5 | 1 | 0 | 1 | ✓ |
| `mark_initial_assessment_done` | L330-334 | 5 | 1 | 0 | 2 | ✓ |
| `build_initial_assessment_result` | L340-347 | 8 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- ❌ L179: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 4
- 认知复杂度: 平均: 4.0, 最大: 8
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 16.8 行, 最大: 44 行
- 文件长度: 255 代码量 (348 总计)
- 参数数量: 平均: 2.2, 最大: 4
- 代码重复: 0.0% 重复 (0/13)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 18.8% (48/255)
- 命名规范: 无命名违规

### 217. backend\users\auth_views.py

**糟糕指数: 3.85**

> 行数: 135 总计, 85 代码, 27 注释 | 函数: 8 | 类: 1

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `register` | L41-46 | 6 | 2 | 1 | 1 | ✓ |
| `login` | L55-60 | 6 | 2 | 1 | 1 | ✓ |
| `update_userinfo` | L79-85 | 7 | 2 | 1 | 1 | ✓ |
| `token_refresh` | L94-99 | 6 | 2 | 1 | 1 | ✓ |
| `change_password` | L107-112 | 6 | 2 | 1 | 1 | ✓ |
| `userinfo` | L68-71 | 4 | 1 | 0 | 1 | ✓ |
| `logout` | L120-123 | 4 | 1 | 0 | 1 | ✓ |
| `health` | L132-134 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- ❌ L122: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 2
- 认知复杂度: 平均: 2.9, 最大: 4
- 嵌套深度: 平均: 0.6, 最大: 1
- 函数长度: 平均: 5.3 行, 最大: 7 行
- 文件长度: 85 代码量 (135 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 1/2 个错误被忽略 (50.0%)
- 注释比例: 31.8% (27/85)
- 命名规范: 无命名违规

### 218. frontend\scripts\browser-audit\student-prep.mjs

**糟糕指数: 3.85**

> 行数: 108 总计, 96 代码, 0 注释 | 函数: 8 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ensureInitialAssessments` | L9-36 | 28 | 4 | 1 | 2 | ✗ |
| `ensureNeo4jKnowledgeMap` | L57-64 | 8 | 2 | 1 | 2 | ✗ |
| `prepareStableStudent` | L66-85 | 19 | 2 | 1 | 2 | ✗ |
| `submitFirstAvailableExam` | L87-95 | 8 | 2 | 1 | 4 | ✗ |
| `ensureProfileAndPath` | L38-44 | 5 | 1 | 0 | 2 | ✗ |
| `fetchExamList` | L46-49 | 4 | 1 | 0 | 2 | ✗ |
| `refreshLearningPath` | L51-55 | 4 | 1 | 0 | 2 | ✗ |
| `prepareTriggerStudent` | L97-107 | 10 | 1 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.8, 最大: 4
- 认知复杂度: 平均: 2.8, 最大: 6
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 10.8 行, 最大: 28 行
- 文件长度: 96 代码量 (108 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/96)
- 命名规范: 无命名违规

### 219. frontend\src\api\student\ai.ts

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

### 220. backend\ai_services\services\llm_feedback_kt_mixin.py

**糟糕指数: 3.82**

> 行数: 112 总计, 86 代码, 9 注释 | 函数: 2 | 类: 1

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `generate_feedback_report` | L29-75 | 47 | 2 | 1 | 6 | ✓ |
| `analyze_knowledge_tracing_result` | L80-111 | 32 | 1 | 0 | 5 | ✓ |

**全部问题 (1)**

- 📏 `generate_feedback_report()` L29: 6 参数数量

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 2
- 认知复杂度: 平均: 2.5, 最大: 4
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 39.5 行, 最大: 47 行
- 文件长度: 86 代码量 (112 总计)
- 参数数量: 平均: 5.5, 最大: 6
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 10.5% (9/86)
- 命名规范: 无命名违规

### 221. backend\learning\tests.py

**糟糕指数: 3.80**

> 行数: 351 总计, 297 代码, 30 注释 | 函数: 7 | 类: 3

**问题**: ⚠️ 其他问题: 2, ❌ 错误处理问题: 5, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L83-139 | 57 | 2 | 1 | 1 | ✓ |
| `test_stage_test_should_return_100_point_scale_and_question_details` | L146-185 | 40 | 2 | 0 | 3 | ✓ |
| `test_refresh_learning_path_should_reinsert_low_mastery_completed_point` | L314-350 | 37 | 2 | 0 | 2 | ✓ |
| `setUp` | L23-56 | 34 | 1 | 0 | 1 | ✓ |
| `test_complete_external_resource_should_accept_string_identifier` | L61-71 | 11 | 1 | 0 | 1 | ✓ |
| `setUp` | L197-276 | 80 | 1 | 0 | 1 | ✓ |
| `test_refresh_learning_path_should_preserve_current_context` | L283-308 | 26 | 1 | 0 | 3 | ✓ |

**全部问题 (10)**

- 📏 `setUp()` L83: 57 代码量
- 📏 `setUp()` L197: 80 代码量
- ❌ L251: 未处理的易出错调用
- ❌ L257: 未处理的易出错调用
- ❌ L263: 未处理的易出错调用
- ❌ L269: 未处理的易出错调用
- ❌ L347: 未处理的易出错调用
- 🏷️ `setUp()` L23: "setUp" - snake_case
- 🏷️ `setUp()` L83: "setUp" - snake_case
- 🏷️ `setUp()` L197: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 2
- 认知复杂度: 平均: 1.7, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 40.7 行, 最大: 80 行
- 文件长度: 297 代码量 (351 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 5/28 个错误被忽略 (17.9%)
- 注释比例: 10.1% (30/297)
- 命名规范: 发现 3 个违规

### 222. backend\platform_ai\rag\student_utils.py

**糟糕指数: 3.68**

> 行数: 241 总计, 154 代码, 48 注释 | 函数: 15 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `to_int` | L21-37 | 17 | 7 | 2 | 2 | ✓ |
| `to_float` | L43-57 | 15 | 6 | 2 | 2 | ✓ |
| `humanize_document_title` | L188-202 | 15 | 6 | 1 | 1 | ✓ |
| `bundle_query_modes` | L134-147 | 14 | 5 | 2 | 2 | ✓ |
| `ordered_unique` | L71-84 | 14 | 4 | 2 | 2 | ✓ |
| `bundle_sources` | L109-118 | 10 | 4 | 2 | 1 | ✓ |
| `bundle_mode` | L124-128 | 5 | 3 | 1 | 2 | ✓ |
| `normalize_nonempty_string` | L90-93 | 4 | 2 | 0 | 1 | ✓ |
| `normalize_positive_int` | L99-103 | 5 | 2 | 1 | 1 | ✓ |
| `bundle_positive_ints` | L153-158 | 6 | 2 | 1 | 2 | ✓ |
| `append_internal_resource` | L208-228 | 21 | 2 | 0 | 5 | ✓ |
| `model_pk` | L63-65 | 3 | 1 | 0 | 1 | ✓ |
| `dedupe_strings` | L164-166 | 3 | 1 | 0 | 1 | ✓ |
| `dedupe_ints` | L172-174 | 3 | 1 | 0 | 1 | ✓ |
| `sanitize_answer_text` | L180-182 | 3 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.1, 最大: 7
- 认知复杂度: 平均: 5.0, 最大: 11
- 嵌套深度: 平均: 0.9, 最大: 2
- 函数长度: 平均: 9.2 行, 最大: 21 行
- 文件长度: 154 代码量 (241 总计)
- 参数数量: 平均: 1.7, 最大: 5
- 代码重复: 0.0% 重复 (0/15)
- 结构分析: 0 个结构问题
- 错误处理: 0/6 个错误被忽略 (0.0%)
- 注释比例: 31.2% (48/154)
- 命名规范: 无命名违规

### 223. frontend\src\views\student\useProfileView.js

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

### 224. backend\tools\resources.py

**糟糕指数: 3.45**

> 行数: 205 总计, 139 代码, 30 注释 | 函数: 9 | 类: 1

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_resource_row` | L84-99 | 16 | 6 | 1 | 2 | ✓ |
| `import_resources_json` | L35-61 | 27 | 5 | 2 | 4 | ✓ |
| `parse_resource_rows` | L67-78 | 12 | 5 | 3 | 1 | ✓ |
| `delete_link_resources` | L163-193 | 31 | 4 | 1 | 2 | ✓ |
| `create_resource_rows` | L105-115 | 11 | 3 | 2 | 3 | ✓ |
| `bind_resource_points` | L148-157 | 10 | 3 | 2 | 3 | ✓ |
| `preview_link_resources` | L199-204 | 6 | 3 | 1 | 2 | ✓ |
| `should_skip_existing_resource` | L121-125 | 5 | 2 | 1 | 3 | ✓ |
| `create_resource` | L131-142 | 12 | 1 | 0 | 2 | ✓ |

**全部问题 (3)**

- 🏗️ `parse_resource_rows()` L67: 中等嵌套: 3
- ❌ L57: 忽略了错误返回值
- ❌ L192: 忽略了错误返回值

**详情**:
- 循环复杂度: 平均: 3.6, 最大: 6
- 认知复杂度: 平均: 6.4, 最大: 11
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 14.4 行, 最大: 31 行
- 文件长度: 139 代码量 (205 总计)
- 参数数量: 平均: 2.4, 最大: 4
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 1 个结构问题
- 错误处理: 2/12 个错误被忽略 (16.7%)
- 注释比例: 21.6% (30/139)
- 命名规范: 无命名违规

### 225. backend\tools\question_import_text.py

**糟糕指数: 3.41**

> 行数: 79 总计, 55 代码, 11 注释 | 函数: 3 | 类: 0

**问题**: 🔄 复杂度问题: 1, 🏗️ 结构问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `strip_import_answer_payload` | L36-54 | 19 | 7 | 3 | 1 | ✓ |
| `clean_question_options` | L60-78 | 19 | 6 | 2 | 1 | ✓ |
| `strip_import_text` | L23-30 | 8 | 2 | 1 | 1 | ✓ |

**全部问题 (2)**

- 🔄 `strip_import_answer_payload()` L36: 认知复杂度: 13
- 🏗️ `strip_import_answer_payload()` L36: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 7
- 认知复杂度: 平均: 9.0, 最大: 13
- 嵌套深度: 平均: 2.0, 最大: 3
- 函数长度: 平均: 15.3 行, 最大: 19 行
- 文件长度: 55 代码量 (79 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 1 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 20.0% (11/55)
- 命名规范: 无命名违规

### 226. backend\users\teacher_views.py

**糟糕指数: 3.40**

> 行数: 84 总计, 60 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_student_profile_detail` | L26-54 | 29 | 5 | 1 | 2 | ✓ |
| `teacher_refresh_student_profile` | L62-83 | 22 | 5 | 1 | 2 | ✓ |

**全部问题 (1)**

- ❌ L45: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 5
- 认知复杂度: 平均: 7.0, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 25.5 行, 最大: 29 行
- 文件长度: 60 代码量 (84 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/2 个错误被忽略 (50.0%)
- 注释比例: 10.0% (6/60)
- 命名规范: 无命名违规

### 227. backend\ai_services\services\llm_response_support.py

**糟糕指数: 3.37**

> 行数: 182 总计, 116 代码, 36 注释 | 函数: 12 | 类: 0

**问题**: 📋 重复问题: 1, 🏗️ 结构问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `format_input_data` | L13-27 | 15 | 5 | 3 | 2 | ✓ |
| `merge_missing_fields` | L135-141 | 7 | 5 | 2 | 2 | ✓ |
| `clean_response_list` | L171-181 | 11 | 5 | 3 | 1 | ✓ |
| `parse_json_response` | L48-62 | 15 | 4 | 1 | 1 | ✓ |
| `coerce_message_text` | L105-116 | 12 | 4 | 1 | 1 | ✓ |
| `parse_json_object` | L68-74 | 7 | 3 | 1 | 1 | ✓ |
| `parse_fenced_json` | L80-87 | 8 | 3 | 2 | 1 | ✓ |
| `parse_embedded_json` | L93-99 | 7 | 3 | 1 | 1 | ✓ |
| `clean_response_value` | L159-165 | 7 | 3 | 1 | 1 | ✓ |
| `strip_reasoning_blocks` | L33-42 | 10 | 2 | 1 | 1 | ✓ |
| `build_retry_prompt` | L122-129 | 8 | 2 | 1 | 2 | ✓ |
| `post_process_response` | L147-153 | 7 | 2 | 0 | 2 | ✓ |

**全部问题 (3)**

- 📋 `merge_missing_fields()` L135: 重复模式: merge_missing_fields, clean_response_list
- 🏗️ `format_input_data()` L13: 中等嵌套: 3
- 🏗️ `clean_response_list()` L171: 中等嵌套: 3

**详情**:
- 循环复杂度: 平均: 3.4, 最大: 5
- 认知复杂度: 平均: 6.3, 最大: 11
- 嵌套深度: 平均: 1.4, 最大: 3
- 函数长度: 平均: 9.5 行, 最大: 15 行
- 文件长度: 116 代码量 (182 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 8.3% 重复 (1/12)
- 结构分析: 2 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 31.0% (36/116)
- 命名规范: 无命名违规

### 228. backend\knowledge\teacher_helpers.py

**糟糕指数: 3.34**

> 行数: 166 总计, 98 代码, 36 注释 | 函数: 10 | 类: 2

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `parse_pagination` | L65-85 | 21 | 4 | 3 | 4 | ✓ |
| `require_point_ids` | L102-114 | 13 | 4 | 1 | 1 | ✓ |
| `extract_question_answer_text` | L131-140 | 10 | 4 | 1 | 1 | ✓ |
| `refresh_course_rag_index` | L157-165 | 9 | 2 | 1 | 1 | ✓ |
| `set` | L37-38 | 2 | 1 | 0 | 2 | ✓ |
| `add` | L50-51 | 2 | 1 | 0 | 2 | ✓ |
| `bad_request` | L57-59 | 3 | 1 | 0 | 1 | ✓ |
| `replace_knowledge_points` | L91-96 | 6 | 1 | 0 | 2 | ✓ |
| `link_knowledge_points` | L120-125 | 6 | 1 | 0 | 2 | ✓ |
| `build_csv_download_response` | L146-151 | 6 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 🏗️ `parse_pagination()` L65: 中等嵌套: 3
- ❌ L150: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 4
- 认知复杂度: 平均: 3.2, 最大: 10
- 嵌套深度: 平均: 0.6, 最大: 3
- 函数长度: 平均: 7.8 行, 最大: 21 行
- 文件长度: 98 代码量 (166 总计)
- 参数数量: 平均: 1.7, 最大: 4
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 1 个结构问题
- 错误处理: 1/7 个错误被忽略 (14.3%)
- 注释比例: 36.7% (36/98)
- 命名规范: 无命名违规

### 229. frontend\src\views\student\profileModels.js

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

### 230. backend\knowledge\teacher_question_views.py

**糟糕指数: 3.28**

> 行数: 321 总计, 248 代码, 30 注释 | 函数: 10 | 类: 0

**问题**: 🏗️ 结构问题: 1, ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `question_export` | L239-263 | 25 | 9 | 1 | 1 | ✓ |
| `question_create` | L103-135 | 33 | 7 | 1 | 1 | ✓ |
| `question_list` | L42-70 | 29 | 6 | 1 | 1 | ✓ |
| `question_import` | L206-231 | 26 | 6 | 2 | 1 | ✓ |
| `question_batch_delete` | L186-198 | 13 | 4 | 2 | 1 | ✓ |
| `question_detail` | L78-95 | 18 | 3 | 1 | 2 | ✓ |
| `question_update` | L143-161 | 19 | 3 | 1 | 2 | ✓ |
| `question_link_knowledge` | L308-320 | 13 | 3 | 1 | 2 | ✓ |
| `question_delete` | L169-178 | 10 | 2 | 1 | 2 | ✓ |
| `question_template` | L271-300 | 30 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- ❌ L174: 未处理的易出错调用
- ❌ L194: 忽略了错误返回值

**详情**:
- 循环复杂度: 平均: 4.4, 最大: 9
- 认知复杂度: 平均: 6.6, 最大: 11
- 嵌套深度: 平均: 1.1, 最大: 2
- 函数长度: 平均: 21.6 行, 最大: 33 行
- 文件长度: 248 代码量 (321 总计)
- 参数数量: 平均: 1.4, 最大: 2
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 2/20 个错误被忽略 (10.0%)
- 注释比例: 12.1% (30/248)
- 命名规范: 无命名违规

### 231. backend\knowledge\teacher_resource_support.py

**糟糕指数: 3.23**

> 行数: 243 总计, 173 代码, 39 注释 | 函数: 12 | 类: 1

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `update_resource_from_payload` | L202-221 | 20 | 9 | 1 | 2 | ✓ |
| `resource_list_payload` | L53-74 | 22 | 7 | 0 | 1 | ✓ |
| `parse_resource_points` | L145-156 | 12 | 6 | 2 | 1 | ✓ |
| `filtered_teacher_resources` | L35-47 | 13 | 5 | 1 | 2 | ✓ |
| `resource_file_display` | L80-89 | 10 | 5 | 2 | 1 | ✓ |
| `resource_detail_payload` | L105-120 | 16 | 5 | 0 | 1 | ✓ |
| `parse_resource_write_payload` | L126-139 | 14 | 4 | 0 | 2 | ✓ |
| `parse_optional_int` | L162-169 | 8 | 4 | 1 | 1 | ✓ |
| `resource_create_result` | L236-242 | 7 | 4 | 0 | 1 | ✓ |
| `create_resource_from_payload` | L175-196 | 22 | 3 | 0 | 4 | ✓ |
| `resource_duration_display` | L95-99 | 5 | 2 | 1 | 1 | ✓ |
| `replace_resource_points` | L227-230 | 4 | 2 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.7, 最大: 9
- 认知复杂度: 平均: 6.2, 最大: 11
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 12.8 行, 最大: 22 行
- 文件长度: 173 代码量 (243 总计)
- 参数数量: 平均: 1.6, 最大: 4
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 0/10 个错误被忽略 (0.0%)
- 注释比例: 22.5% (39/173)
- 命名规范: 无命名违规

### 232. backend\tools\question_import_excel.py

**糟糕指数: 3.23**

> 行数: 247 总计, 172 代码, 38 注释 | 函数: 12 | 类: 0

**问题**: 🔄 复杂度问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `extract_question_content` | L58-67 | 10 | 9 | 2 | 2 | ✓ |
| `build_excel_options` | L73-85 | 13 | 6 | 2 | 2 | ✓ |
| `build_excel_question_payload` | L146-171 | 26 | 6 | 1 | 3 | ✓ |
| `open_question_bank_workbook` | L177-204 | 28 | 6 | 2 | 2 | ✓ |
| `iter_workbook_rows` | L210-226 | 17 | 6 | 2 | 2 | ✓ |
| `resolve_excel_question_type` | L91-99 | 9 | 4 | 0 | 1 | ✓ |
| `resolve_excel_answer_text` | L114-117 | 4 | 4 | 0 | 1 | ✓ |
| `resolve_excel_analysis` | L123-126 | 4 | 4 | 0 | 1 | ✓ |
| `resolve_excel_score` | L132-140 | 9 | 4 | 0 | 1 | ✓ |
| `resolve_excel_difficulty` | L105-108 | 4 | 3 | 0 | 1 | ✓ |
| `iter_excel_question_payloads` | L232-246 | 15 | 3 | 2 | 3 | ✓ |
| `row_get` | L47-52 | 6 | 2 | 1 | 2 | ✓ |

**全部问题 (1)**

- 🔄 `extract_question_content()` L58: 认知复杂度: 13

**详情**:
- 循环复杂度: 平均: 4.8, 最大: 9
- 认知复杂度: 平均: 6.8, 最大: 13
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 12.1 行, 最大: 28 行
- 文件长度: 172 代码量 (247 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/12)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 22.1% (38/172)
- 命名规范: 无命名违规

### 233. backend\platform_ai\rag\runtime_proxies.py

**糟糕指数: 3.21**

> 行数: 27 总计, 11 代码, 6 注释 | 函数: 2 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__getattr__` | L10-13 | 4 | 1 | 0 | 2 | ✗ |
| `FacadeGraphRAGLLM` | L22-26 | 5 | 1 | 0 | 0 | ✓ |

**全部问题 (2)**

- 🏷️ `__getattr__()` L10: "__getattr__" - snake_case
- 🏷️ `FacadeGraphRAGLLM()` L22: "FacadeGraphRAGLLM" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.5 行, 最大: 5 行
- 文件长度: 11 代码量 (27 总计)
- 参数数量: 平均: 1.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 54.5% (6/11)
- 命名规范: 发现 2 个违规

### 234. backend\users\admin_helpers.py

**糟糕指数: 3.17**

> 行数: 27 总计, 18 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_parse_pagination` | L13-26 | 14 | 2 | 1 | 4 | ✓ |

**全部问题 (1)**

- 🏷️ `_parse_pagination()` L13: "_parse_pagination" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 14.0 行, 最大: 14 行
- 文件长度: 18 代码量 (27 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 16.7% (3/18)
- 命名规范: 发现 1 个违规

### 235. backend\ai_services\auth.py

**糟糕指数: 3.12**

> 行数: 62 总计, 36 代码, 12 注释 | 函数: 3 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__call__` | L33-49 | 17 | 5 | 2 | 4 | ✗ |
| `_resolve_user_from_token` | L20-24 | 5 | 1 | 0 | 1 | ✓ |
| `query_string_jwt_auth_middleware_stack` | L55-57 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 🏷️ `_resolve_user_from_token()` L20: "_resolve_user_from_token" - snake_case
- 🏷️ `__call__()` L33: "__call__" - snake_case

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 5
- 认知复杂度: 平均: 3.7, 最大: 9
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 8.3 行, 最大: 17 行
- 文件长度: 36 代码量 (62 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 33.3% (12/36)
- 命名规范: 发现 2 个违规

### 236. backend\ai_services\services\student_graph_rag_service.py

**糟糕指数: 3.10**

> 行数: 33 总计, 15 代码, 9 注释 | 函数: 2 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `search_points` | L20-22 | 3 | 1 | 0 | 5 | ✓ |
| `ask` | L27-29 | 3 | 1 | 0 | 5 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.0 行, 最大: 3 行
- 文件长度: 15 代码量 (33 总计)
- 参数数量: 平均: 5.0, 最大: 5
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 60.0% (9/15)
- 命名规范: 无命名违规

### 237. frontend\src\api\errors.ts

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

### 238. backend\exams\student_artifact_views.py

**糟糕指数: 3.04**

> 行数: 92 总计, 66 代码, 9 注释 | 函数: 3 | 类: 0

**问题**: ❌ 错误处理问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `exam_download` | L67-91 | 25 | 6 | 1 | 2 | ✓ |
| `exam_answer_sheet` | L23-40 | 18 | 4 | 1 | 2 | ✓ |
| `exam_retake` | L48-59 | 12 | 3 | 1 | 2 | ✓ |

**全部问题 (2)**

- ❌ L58: 未处理的易出错调用
- ❌ L80: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.3, 最大: 6
- 认知复杂度: 平均: 6.3, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 18.3 行, 最大: 25 行
- 文件长度: 66 代码量 (92 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 2/6 个错误被忽略 (33.3%)
- 注释比例: 13.6% (9/66)
- 命名规范: 无命名违规

### 239. backend\tools\question_import_json.py

**糟糕指数: 2.99**

> 行数: 72 总计, 51 代码, 11 注释 | 函数: 3 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_json_question_payload` | L54-71 | 18 | 9 | 1 | 1 | ✓ |
| `load_question_json_source` | L34-48 | 15 | 5 | 2 | 1 | ✓ |
| `validate_question_json_payload` | L24-28 | 5 | 2 | 1 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 5.3, 最大: 9
- 认知复杂度: 平均: 8.0, 最大: 11
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 12.7 行, 最大: 18 行
- 文件长度: 51 代码量 (72 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/12 个错误被忽略 (0.0%)
- 注释比例: 21.6% (11/51)
- 命名规范: 无命名违规

### 240. backend\users\test_profile.py

**糟糕指数: 2.98**

> 行数: 137 总计, 97 代码, 21 注释 | 函数: 5 | 类: 2

**问题**: ❌ 错误处理问题: 2, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L26-32 | 7 | 1 | 0 | 1 | ✓ |
| `test_update_habit_preference` | L37-49 | 13 | 1 | 0 | 1 | ✓ |
| `test_get_profile` | L54-62 | 9 | 1 | 0 | 1 | ✓ |
| `setUp` | L74-109 | 36 | 1 | 0 | 1 | ✓ |
| `test_generate_profile_for_course_should_reuse_cached_summary` | L116-136 | 21 | 1 | 0 | 3 | ✓ |

**全部问题 (4)**

- ❌ L96: 未处理的易出错调用
- ❌ L102: 未处理的易出错调用
- 🏷️ `setUp()` L26: "setUp" - snake_case
- 🏷️ `setUp()` L74: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 17.2 行, 最大: 36 行
- 文件长度: 97 代码量 (137 总计)
- 参数数量: 平均: 1.4, 最大: 3
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 2/7 个错误被忽略 (28.6%)
- 注释比例: 21.6% (21/97)
- 命名规范: 发现 2 个违规

### 241. backend\tools\exam_sets.py

**糟糕指数: 2.93**

> 行数: 201 总计, 146 代码, 26 注释 | 函数: 8 | 类: 0

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `import_exam_sets` | L161-200 | 40 | 7 | 2 | 4 | ✓ |
| `import_single_exam_file` | L97-128 | 32 | 6 | 1 | 3 | ✓ |
| `build_exam_title` | L82-91 | 10 | 4 | 0 | 1 | ✓ |
| `collect_import_files` | L62-76 | 15 | 3 | 1 | 1 | ✓ |
| `resolve_homework_path` | L36-44 | 9 | 2 | 1 | 1 | ✓ |
| `print_dry_run` | L134-142 | 9 | 2 | 1 | 1 | ✓ |
| `collect_excel_files` | L50-56 | 7 | 1 | 0 | 1 | ✓ |
| `clear_existing_question_sets` | L148-155 | 8 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 7
- 认知复杂度: 平均: 4.8, 最大: 11
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 16.3 行, 最大: 40 行
- 文件长度: 146 代码量 (201 总计)
- 参数数量: 平均: 1.6, 最大: 4
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 17.8% (26/146)
- 命名规范: 无命名违规

### 242. backend\ai_services\services\mefkt_runtime_sources.py

**糟糕指数: 2.92**

> 行数: 136 总计, 97 代码, 20 注释 | 函数: 6 | 类: 0

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `collect_point_resource_map` | L45-51 | 7 | 3 | 2 | 1 | ✓ |
| `collect_question_answer_stats` | L107-121 | 15 | 3 | 1 | 1 | ✓ |
| `collect_knowledge_relation_maps` | L57-80 | 24 | 2 | 1 | 1 | ✓ |
| `register_relation_row` | L86-101 | 16 | 2 | 1 | 6 | ✓ |
| `load_runtime_source_data` | L13-39 | 27 | 1 | 0 | 1 | ✓ |
| `build_feature_sources` | L127-135 | 9 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- 📏 `register_relation_row()` L86: 6 参数数量

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 3
- 认知复杂度: 平均: 3.7, 最大: 7
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 16.3 行, 最大: 27 行
- 文件长度: 97 代码量 (136 总计)
- 参数数量: 平均: 1.8, 最大: 6
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 20.6% (20/97)
- 命名规范: 无命名违规

### 243. frontend\src\views\student\useFeedbackReport.js

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

### 244. backend\common\permissions.py

**糟糕指数: 2.81**

> 行数: 126 总计, 57 代码, 40 注释 | 函数: 6 | 类: 6

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `has_permission` | L92-115 | 24 | 5 | 1 | 3 | ✓ |
| `has_object_permission` | L70-80 | 11 | 4 | 1 | 4 | ✓ |
| `has_permission` | L44-45 | 2 | 3 | 0 | 3 | ✓ |
| `has_permission` | L18-19 | 2 | 2 | 0 | 3 | ✓ |
| `has_permission` | L31-32 | 2 | 2 | 0 | 3 | ✓ |
| `has_permission` | L57-58 | 2 | 2 | 0 | 3 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 5
- 认知复杂度: 平均: 3.7, 最大: 7
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 7.2 行, 最大: 24 行
- 文件长度: 57 代码量 (126 总计)
- 参数数量: 平均: 3.2, 最大: 4
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 70.2% (40/57)
- 命名规范: 无命名违规

### 245. backend\tools\exam_sets_support.py

**糟糕指数: 2.80**

> 行数: 424 总计, 311 代码, 59 注释 | 函数: 17 | 类: 2

**问题**: ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `bind_question_knowledge_points` | L146-170 | 25 | 5 | 2 | 4 | ✓ |
| `iter_excel_rows` | L193-212 | 20 | 5 | 2 | 3 | ✓ |
| `extract_row_content` | L104-115 | 12 | 4 | 2 | 2 | ✓ |
| `match_row_question` | L286-308 | 23 | 4 | 1 | 3 | ✓ |
| `resolve_content_columns` | L82-98 | 17 | 3 | 1 | 1 | ✓ |
| `match_question` | L266-280 | 15 | 3 | 1 | 2 | ✓ |
| `load_matched_questions` | L314-331 | 18 | 3 | 2 | 3 | ✓ |
| `collect_question_knowledge_point_names` | L337-347 | 11 | 3 | 2 | 1 | ✓ |
| `create_exam_set` | L387-423 | 37 | 3 | 1 | 4 | ✓ |
| `load_pandas_module` | L54-64 | 11 | 2 | 1 | 0 | ✓ |
| `resolve_knowledge_point` | L121-140 | 20 | 2 | 1 | 3 | ✓ |
| `read_excel_sheet` | L176-187 | 12 | 2 | 1 | 3 | ✓ |
| `build_question_lookup` | L218-237 | 20 | 2 | 1 | 1 | ✓ |
| `open_excel_file` | L353-364 | 12 | 2 | 1 | 2 | ✓ |
| `normalize_question_content` | L70-76 | 7 | 1 | 0 | 1 | ✓ |
| `build_import_context` | L243-260 | 18 | 1 | 0 | 2 | ✓ |
| `question_set_exists` | L370-381 | 12 | 1 | 0 | 2 | ✓ |

**全部问题 (1)**

- ❌ L304: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.7, 最大: 5
- 认知复杂度: 平均: 4.9, 最大: 9
- 嵌套深度: 平均: 1.1, 最大: 2
- 函数长度: 平均: 17.1 行, 最大: 37 行
- 文件长度: 311 代码量 (424 总计)
- 参数数量: 平均: 2.2, 最大: 4
- 代码重复: 0.0% 重复 (0/17)
- 结构分析: 0 个结构问题
- 错误处理: 1/6 个错误被忽略 (16.7%)
- 注释比例: 19.0% (59/311)
- 命名规范: 无命名违规

### 246. backend\common\config.py

**糟糕指数: 2.70**

> 行数: 436 总计, 240 代码, 131 注释 | 函数: 38 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📋 重复问题: 1, 🏗️ 结构问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_get_parser` | L29-36 | 8 | 3 | 2 | 0 | ✓ |
| `get_config_bool` | L108-125 | 18 | 3 | 1 | 3 | ✓ |
| `get_config_list` | L131-154 | 24 | 3 | 1 | 4 | ✓ |
| `get_config` | L42-58 | 17 | 2 | 1 | 3 | ✓ |
| `get_config_int` | L64-80 | 17 | 2 | 1 | 3 | ✓ |
| `get_config_float` | L86-102 | 17 | 2 | 1 | 3 | ✓ |
| `llm_provider` | L246-248 | 3 | 2 | 0 | 0 | ✓ |
| `llm_model` | L254-256 | 3 | 2 | 0 | 0 | ✓ |
| `llm_api_format` | L262-264 | 3 | 2 | 0 | 0 | ✓ |
| `graphrag_embedder_provider` | L295-297 | 3 | 2 | 0 | 0 | ✓ |
| `graphrag_sentence_model` | L303-309 | 7 | 2 | 0 | 0 | ✓ |
| `graphrag_qdrant_path` | L323-325 | 3 | 2 | 0 | 0 | ✓ |
| `reload_config` | L160-164 | 5 | 1 | 0 | 0 | ✓ |
| `password_min_length` | L179-181 | 3 | 1 | 0 | 0 | ✓ |
| `password_require_uppercase` | L187-189 | 3 | 1 | 0 | 0 | ✓ |
| `password_require_numbers` | L195-197 | 3 | 1 | 0 | 0 | ✓ |
| `password_require_special` | L203-205 | 3 | 1 | 0 | 0 | ✓ |
| `default_page_size` | L212-214 | 3 | 1 | 0 | 0 | ✓ |
| `max_page_size` | L220-222 | 3 | 1 | 0 | 0 | ✓ |
| `ai_api_timeout` | L229-231 | 3 | 1 | 0 | 0 | ✓ |
| `ai_feedback_enabled` | L237-239 | 3 | 1 | 0 | 0 | ✓ |
| `llm_base_url` | L270-272 | 3 | 1 | 0 | 0 | ✓ |
| `llm_request_timeout` | L278-280 | 3 | 1 | 0 | 0 | ✓ |
| `llm_max_retries` | L286-288 | 3 | 1 | 0 | 0 | ✓ |
| `graphrag_vector_dimension` | L315-317 | 3 | 1 | 0 | 0 | ✓ |
| `mastery_threshold` | L332-334 | 3 | 1 | 0 | 0 | ✓ |
| `activation_code_length` | L341-343 | 3 | 1 | 0 | 0 | ✓ |
| `activation_code_expiration_days` | L349-351 | 3 | 1 | 0 | 0 | ✓ |
| `invitation_code_length` | L358-360 | 3 | 1 | 0 | 0 | ✓ |
| `invitation_code_max_uses` | L366-368 | 3 | 1 | 0 | 0 | ✓ |
| `invitation_code_expiration_days` | L374-376 | 3 | 1 | 0 | 0 | ✓ |
| `exam_default_duration` | L383-385 | 3 | 1 | 0 | 0 | ✓ |
| `exam_pass_ratio` | L391-393 | 3 | 1 | 0 | 0 | ✓ |
| `max_file_size_mb` | L400-402 | 3 | 1 | 0 | 0 | ✓ |
| `allowed_image_formats` | L408-410 | 3 | 1 | 0 | 0 | ✓ |
| `allowed_document_formats` | L416-418 | 3 | 1 | 0 | 0 | ✓ |
| `max_path_nodes` | L425-427 | 3 | 1 | 0 | 0 | ✓ |
| `path_test_interval` | L433-435 | 3 | 1 | 0 | 0 | ✓ |

**全部问题 (1)**

- 📋 `get_config()` L42: 重复模式: get_config, get_config_int, get_config_float

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 3
- 认知复杂度: 平均: 1.8, 最大: 7
- 嵌套深度: 平均: 0.2, 最大: 2
- 函数长度: 平均: 5.3 行, 最大: 24 行
- 文件长度: 240 代码量 (436 总计)
- 参数数量: 平均: 0.4, 最大: 4
- 代码重复: 5.3% 重复 (2/38)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 54.6% (131/240)
- 命名规范: 发现 1 个违规

### 247. backend\exams\teacher_result_support.py

**糟糕指数: 2.67**

> 行数: 187 总计, 129 代码, 33 注释 | 函数: 11 | 类: 0

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_score_bucket` | L109-119 | 11 | 5 | 1 | 1 | ✓ |
| `is_teacher_answer_correct` | L66-78 | 13 | 3 | 1 | 3 | ✓ |
| `build_single_question_analysis` | L140-164 | 25 | 3 | 0 | 3 | ✓ |
| `is_teacher_analysis_answer_correct` | L170-178 | 9 | 3 | 1 | 3 | ✓ |
| `build_submission_result` | L12-22 | 11 | 2 | 0 | 1 | ✓ |
| `build_teacher_question_detail` | L28-50 | 23 | 2 | 0 | 2 | ✓ |
| `extract_question_answer` | L56-60 | 5 | 2 | 1 | 1 | ✓ |
| `build_score_distribution` | L92-103 | 12 | 2 | 1 | 1 | ✓ |
| `truncate_question_content` | L184-186 | 3 | 2 | 0 | 1 | ✓ |
| `normalized_answer_text` | L84-86 | 3 | 1 | 0 | 1 | ✓ |
| `build_question_analysis` | L125-134 | 10 | 1 | 0 | 2 | ✓ |

**全部问题 (1)**

- ❌ L153: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.4, 最大: 5
- 认知复杂度: 平均: 3.3, 最大: 7
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 11.4 行, 最大: 25 行
- 文件长度: 129 代码量 (187 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/11)
- 结构分析: 0 个结构问题
- 错误处理: 1/3 个错误被忽略 (33.3%)
- 注释比例: 25.6% (33/129)
- 命名规范: 发现 1 个违规

### 248. frontend\src\views\teacher\useTeacherKnowledgeManage.js

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

### 249. backend\learning\stage_test_feedback.py

**糟糕指数: 2.56**

> 行数: 101 总计, 73 代码, 13 注释 | 函数: 4 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `normalize_feedback_report` | L51-71 | 21 | 9 | 1 | 1 | ✓ |
| `build_feedback_report` | L19-45 | 27 | 2 | 1 | 3 | ✓ |
| `llm_field` | L77-79 | 3 | 1 | 0 | 3 | ✓ |
| `fallback_feedback_report` | L85-100 | 16 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 9
- 认知复杂度: 平均: 4.3, 最大: 11
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 16.8 行, 最大: 27 行
- 文件长度: 73 代码量 (101 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 17.8% (13/73)
- 命名规范: 无命名违规

### 250. backend\knowledge\teacher_question_support.py

**糟糕指数: 2.56**

> 行数: 137 总计, 97 代码, 19 注释 | 函数: 6 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `apply_question_update_fields` | L78-93 | 16 | 8 | 2 | 3 | ✓ |
| `replace_question_points_from_payload` | L99-118 | 20 | 4 | 2 | 3 | ✓ |
| `build_question_detail` | L51-72 | 22 | 3 | 0 | 1 | ✓ |
| `question_identifier` | L27-29 | 3 | 2 | 0 | 1 | ✓ |
| `build_question_list_item` | L35-45 | 11 | 2 | 0 | 1 | ✓ |
| `has_question_point_payload` | L124-126 | 3 | 2 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 8
- 认知复杂度: 平均: 4.8, 最大: 12
- 嵌套深度: 平均: 0.7, 最大: 2
- 函数长度: 平均: 12.5 行, 最大: 22 行
- 文件长度: 97 代码量 (137 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 19.6% (19/97)
- 命名规范: 无命名违规

### 251. backend\tools.py

**糟糕指数: 2.50**

> 行数: 37 总计, 23 代码, 4 注释 | 函数: 1 | 类: 0

**问题**: 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_load_cli_main` | L30-33 | 4 | 1 | 0 | 0 | ✓ |

**全部问题 (1)**

- 🏷️ `_load_cli_main()` L30: "_load_cli_main" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 4.0 行, 最大: 4 行
- 文件长度: 23 代码量 (37 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 17.4% (4/23)
- 命名规范: 发现 1 个违规

### 252. frontend\scripts\browser-audit.mjs

**糟糕指数: 2.50**

> 行数: 41 总计, 35 代码, 0 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `main` | L24-35 | 12 | 1 | 0 | 0 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 12.0 行, 最大: 12 行
- 文件长度: 35 代码量 (41 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/35)
- 命名规范: 无命名违规

### 253. backend\wisdom_edu_api\wsgi.py

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

### 254. backend\wisdom_edu_api\asgi.py

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

### 255. backend\users\tests.py

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

### 256. backend\users\admin_views.py

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

### 257. backend\exams\teacher_views.py

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

### 258. backend\courses\teacher_views.py

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

### 259. backend\common\utils.py

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

### 260. backend\common\models.py

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

### 261. backend\common\admin.py

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

### 262. backend\assessments\views.py

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

### 263. backend\assessments\models.py

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

### 264. backend\assessments\habit_survey_defaults.py

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

### 265. backend\assessments\ability_survey_defaults.py

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

### 266. backend\knowledge\views.py

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

### 267. backend\knowledge\teacher_views.py

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

### 268. backend\application\__init__.py

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

### 269. backend\ai_services\views.py

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

### 270. backend\ai_services\tests.py

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

### 271. backend\ai_services\student_ai_views.py

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

### 272. backend\ai_services\routing.py

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

### 273. frontend\src\utils\markdown.ts

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

### 274. frontend\src\stores\index.ts

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

### 275. frontend\src\api\types.ts

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

### 276. frontend\src\api\course.ts

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

### 277. frontend\src\api\authTokens.ts

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

### 278. frontend\src\api\auth.ts

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

### 279. frontend\scripts\browser-audit\context.mjs

**糟糕指数: 2.50**

> 行数: 121 总计, 109 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `buildStudentRoutes` | L102-120 | 19 | 4 | 1 | 1 | ✗ |
| `resolveStudentContext` | L3-46 | 38 | 3 | 1 | 2 | ✗ |
| `resolveDefenseCourseContext` | L48-74 | 26 | 3 | 1 | 2 | ✗ |
| `buildRoutes` | L76-100 | 25 | 3 | 1 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 4
- 认知复杂度: 平均: 5.3, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 27.0 行, 最大: 38 行
- 文件长度: 109 代码量 (121 总计)
- 参数数量: 平均: 1.8, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/109)
- 命名规范: 无命名违规

### 280. frontend\scripts\browser-audit\constants.mjs

**糟糕指数: 2.50**

> 行数: 10 总计, 9 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 9 代码量 (10 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/9)
- 命名规范: 无命名违规

### 281. frontend\scripts\browser-audit\api.mjs

**糟糕指数: 2.50**

> 行数: 51 总计, 46 代码, 0 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `loginApi` | L3-18 | 15 | 2 | 1 | 3 | ✗ |
| `ensureBackendReady` | L20-30 | 11 | 2 | 1 | 1 | ✗ |
| `apiJson` | L39-50 | 11 | 2 | 1 | 3 | ✗ |
| `createAuthedClient` | L32-37 | 6 | 1 | 0 | 2 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.8, 最大: 2
- 认知复杂度: 平均: 3.3, 最大: 4
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 10.8 行, 最大: 15 行
- 文件长度: 46 代码量 (51 总计)
- 参数数量: 平均: 2.3, 最大: 3
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 0.0% (0/46)
- 命名规范: 无命名违规

### 282. frontend\scripts\browser-audit\answers.mjs

**糟糕指数: 2.50**

> 行数: 85 总计, 76 代码, 0 注释 | 函数: 7 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `buildKnowledgeAnswer` | L41-60 | 19 | 4 | 1 | 3 | ✗ |
| `waitForFeedbackReady` | L75-84 | 8 | 3 | 2 | 2 | ✗ |
| `pickOptionValue` | L23-28 | 6 | 2 | 1 | 0 | ✗ |
| `buildDefenseStageTestAnswers` | L9-21 | 6 | 1 | 0 | 2 | ✗ |
| `buildSurveyAnswers` | L30-35 | 2 | 1 | 0 | 0 | ✗ |
| `buildKnowledgeAnswers` | L37-39 | 2 | 1 | 0 | 0 | ✗ |
| `submitExamWithGeneratedAnswers` | L62-73 | 8 | 1 | 0 | 3 | ✗ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.9, 最大: 4
- 认知复杂度: 平均: 3.0, 最大: 7
- 嵌套深度: 平均: 0.6, 最大: 2
- 函数长度: 平均: 7.3 行, 最大: 19 行
- 文件长度: 76 代码量 (85 总计)
- 参数数量: 平均: 1.4, 最大: 3
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 0.0% (0/76)
- 命名规范: 无命名违规

### 283. backend\models\MEFKT\constants.py

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

### 284. backend\platform_ai\search\__init__.py

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

### 285. backend\platform_ai\rag\__init__.py

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

### 286. backend\platform_ai\mcp\__init__.py

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

### 287. backend\platform_ai\llm\__init__.py

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

### 288. backend\platform_ai\llm\facade.py

**糟糕指数: 2.50**

> 行数: 92 总计, 40 代码, 33 注释 | 函数: 10 | 类: 1

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_llm_service` | L14-16 | 3 | 1 | 0 | 0 | ✓ |
| `service` | L29-31 | 3 | 1 | 0 | 1 | ✓ |
| `is_available` | L37-39 | 3 | 1 | 0 | 1 | ✓ |
| `analyze_profile` | L44-46 | 3 | 1 | 0 | 1 | ✓ |
| `plan_learning_path` | L51-53 | 3 | 1 | 0 | 1 | ✓ |
| `generate_resource_reason` | L58-60 | 3 | 1 | 0 | 1 | ✓ |
| `generate_feedback_report` | L65-67 | 3 | 1 | 0 | 1 | ✓ |
| `recommend_internal_resources` | L72-74 | 3 | 1 | 0 | 1 | ✓ |
| `recommend_external_resources` | L79-81 | 3 | 1 | 0 | 1 | ✓ |
| `call_with_fallback` | L86-88 | 3 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.0 行, 最大: 3 行
- 文件长度: 40 代码量 (92 总计)
- 参数数量: 平均: 0.9, 最大: 1
- 代码重复: 0.0% 重复 (0/10)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 82.5% (33/40)
- 命名规范: 无命名违规

### 289. backend\platform_ai\llm\agent_support.py

**糟糕指数: 2.50**

> 行数: 22 总计, 18 代码, 0 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 18 代码量 (22 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 0.0% (0/18)
- 命名规范: 无命名违规

### 290. backend\application\teacher\__init__.py

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

### 291. backend\ai_services\services\__init__.py

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

### 292. frontend\src\views\teacher\resourceManageModels.js

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

### 293. frontend\src\views\student\learningPathModels.js

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

### 294. frontend\src\views\student\examTakingModels.js

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

### 295. frontend\src\components\knowledge\knowledgeGraphModels.js

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

### 296. frontend\src\api\teacher\settings.ts

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

### 297. frontend\src\api\teacher\question.ts

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

### 298. frontend\src\api\teacher\knowledge.ts

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

### 299. frontend\src\api\teacher\index.ts

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

### 300. frontend\src\api\teacher\exam.ts

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

### 301. frontend\src\api\teacher\course.ts

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

### 302. frontend\src\api\teacher\class.ts

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

### 303. frontend\src\api\student\profile.ts

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

### 304. frontend\src\api\student\learning.ts

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

### 305. frontend\src\api\student\knowledge.ts

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

### 306. frontend\src\api\student\index.ts

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

### 307. frontend\src\api\student\exam.ts

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

### 308. frontend\src\api\student\class.ts

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

### 309. frontend\src\api\student\assessment.ts

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

### 310. frontend\src\api\admin\user.ts

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

### 311. frontend\src\api\admin\statistics.ts

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

### 312. frontend\src\api\admin\profile.ts

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

### 313. frontend\src\api\admin\log.ts

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

### 314. frontend\src\api\admin\course.ts

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

### 315. frontend\src\api\admin\class.ts

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

### 316. frontend\src\api\admin\activation.ts

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

### 317. backend\users\serializers.py

**糟糕指数: 2.49**

> 行数: 167 总计, 98 代码, 45 注释 | 函数: 3 | 类: 7

**问题**: ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `create` | L50-60 | 11 | 1 | 0 | 1 | ✓ |
| `get_token` | L73-78 | 6 | 1 | 0 | 2 | ✓ |
| `get_is_valid` | L164-166 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- ❌ L50: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 6.7 行, 最大: 11 行
- 文件长度: 98 代码量 (167 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 1/5 个错误被忽略 (20.0%)
- 注释比例: 45.9% (45/98)
- 命名规范: 无命名违规

### 318. backend\ai_services\test_student_rag_runtime.py

**糟糕指数: 2.48**

> 行数: 204 总计, 159 代码, 24 注释 | 函数: 7 | 类: 1

**问题**: ⚠️ 其他问题: 2, 🏗️ 结构问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_runtime_materialization_should_write_qdrant_points` | L46-130 | 69 | 1 | 1 | 4 | ✓ |
| `__init__` | L60-62 | 3 | 1 | 0 | 1 | ✗ |
| `collection_exists` | L67-70 | 4 | 1 | 0 | 2 | ✓ |
| `create_collection` | L75-78 | 4 | 1 | 0 | 4 | ✓ |
| `upsert` | L83-87 | 5 | 1 | 0 | 4 | ✓ |
| `test_recommend_resources_for_node_should_return_internal_course_resources` | L136-159 | 24 | 1 | 0 | 2 | ✓ |
| `test_recommend_resources_for_node_should_fallback_to_course_local_resources` | L165-203 | 39 | 1 | 0 | 2 | ✓ |

**全部问题 (2)**

- 📏 `test_runtime_materialization_should_write_qdrant_points()` L46: 69 代码量
- 🏷️ `__init__()` L60: "__init__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.3, 最大: 3
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 21.1 行, 最大: 69 行
- 文件长度: 159 代码量 (204 总计)
- 参数数量: 平均: 2.7, 最大: 4
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 15.1% (24/159)
- 命名规范: 发现 1 个违规

### 319. backend\platform_ai\rag\corpus_utils.py

**糟糕指数: 2.35**

> 行数: 69 总计, 44 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_safe_resource_url` | L39-48 | 10 | 4 | 2 | 1 | ✓ |
| `_top_themes` | L54-59 | 6 | 3 | 1 | 2 | ✓ |
| `tokenize` | L29-33 | 5 | 2 | 1 | 1 | ✓ |
| `_chapter_entity_id` | L65-68 | 4 | 2 | 0 | 1 | ✓ |

**全部问题 (3)**

- 🏷️ `_safe_resource_url()` L39: "_safe_resource_url" - snake_case
- 🏷️ `_top_themes()` L54: "_top_themes" - snake_case
- 🏷️ `_chapter_entity_id()` L65: "_chapter_entity_id" - snake_case

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 4
- 认知复杂度: 平均: 4.8, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 6.3 行, 最大: 10 行
- 文件长度: 44 代码量 (69 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 27.3% (12/44)
- 命名规范: 发现 3 个违规

### 320. backend\assessments\tests.py

**糟糕指数: 2.33**

> 行数: 183 总计, 149 代码, 18 注释 | 函数: 4 | 类: 2

**问题**: ⚠️ 其他问题: 1, ❌ 错误处理问题: 2, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L22-62 | 41 | 1 | 0 | 1 | ✓ |
| `test_submit_ability_assessment_should_not_fabricate_dimension_scores` | L67-82 | 16 | 1 | 0 | 1 | ✓ |
| `setUp` | L94-148 | 55 | 1 | 0 | 1 | ✓ |
| `test_knowledge_assessment_should_keep_mastery_conservative_and_respect_prerequisite` | L154-182 | 29 | 1 | 0 | 2 | ✓ |

**全部问题 (5)**

- 📏 `setUp()` L94: 55 代码量
- ❌ L57: 未处理的易出错调用
- ❌ L118: 未处理的易出错调用
- 🏷️ `setUp()` L22: "setUp" - snake_case
- 🏷️ `setUp()` L94: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 35.3 行, 最大: 55 行
- 文件长度: 149 代码量 (183 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 2/18 个错误被忽略 (11.1%)
- 注释比例: 12.1% (18/149)
- 命名规范: 发现 2 个违规

### 321. frontend\src\api\common.ts

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

### 322. backend\common\logging_utils.py

**糟糕指数: 2.24**

> 行数: 149 总计, 122 代码, 13 注释 | 函数: 4 | 类: 0

**问题**: ⚠️ 其他问题: 1, 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_log_message` | L131-140 | 10 | 4 | 2 | 2 | ✓ |
| `_normalize_log_value` | L105-114 | 10 | 3 | 1 | 2 | ✓ |
| `_humanize_event` | L120-125 | 6 | 3 | 1 | 1 | ✓ |
| `log_event` | L146-148 | 3 | 1 | 0 | 4 | ✓ |

**全部问题 (2)**

- 🏷️ `_normalize_log_value()` L105: "_normalize_log_value" - snake_case
- 🏷️ `_humanize_event()` L120: "_humanize_event" - snake_case

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 4
- 认知复杂度: 平均: 4.8, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 7.3 行, 最大: 10 行
- 文件长度: 122 代码量 (149 总计)
- 参数数量: 平均: 2.3, 最大: 4
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 10.7% (13/122)
- 命名规范: 发现 2 个违规

### 323. backend\users\test_auth_api.py

**糟糕指数: 2.20**

> 行数: 214 总计, 147 代码, 39 注释 | 函数: 11 | 类: 2

**问题**: 📋 重复问题: 1, ❌ 错误处理问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_list_activation_codes` | L200-213 | 14 | 2 | 1 | 1 | ✓ |
| `test_register_student` | L20-30 | 11 | 1 | 0 | 1 | ✓ |
| `test_register_teacher_without_activation_code` | L35-43 | 9 | 1 | 0 | 1 | ✓ |
| `test_register_teacher_with_activation_code` | L48-71 | 24 | 1 | 0 | 1 | ✓ |
| `test_login` | L76-88 | 13 | 1 | 0 | 1 | ✓ |
| `test_login_wrong_password` | L93-104 | 12 | 1 | 0 | 1 | ✓ |
| `test_userinfo` | L109-121 | 13 | 1 | 0 | 1 | ✓ |
| `test_update_userinfo` | L126-145 | 20 | 1 | 0 | 1 | ✓ |
| `setUp` | L157-168 | 12 | 1 | 0 | 1 | ✓ |
| `test_generate_activation_code_as_admin` | L173-182 | 10 | 1 | 0 | 1 | ✓ |
| `test_generate_activation_code_as_student` | L187-195 | 9 | 1 | 0 | 1 | ✓ |

**全部问题 (2)**

- 📋 `test_login()` L76: 重复模式: test_login, test_login_wrong_password
- ❌ L205: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 1.1, 最大: 2
- 认知复杂度: 平均: 1.3, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 13.4 行, 最大: 24 行
- 文件长度: 147 代码量 (214 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 9.1% 重复 (1/11)
- 结构分析: 0 个结构问题
- 错误处理: 1/12 个错误被忽略 (8.3%)
- 注释比例: 26.5% (39/147)
- 命名规范: 发现 1 个违规

### 324. backend\tools\cli.py

**糟糕指数: 2.12**

> 行数: 42 总计, 21 代码, 8 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `main` | L29-38 | 10 | 2 | 1 | 0 | ✓ |
| `_dispatch_command` | L21-23 | 3 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- 🏷️ `_dispatch_command()` L21: "_dispatch_command" - snake_case

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 2
- 认知复杂度: 平均: 2.5, 最大: 4
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 6.5 行, 最大: 10 行
- 文件长度: 21 代码量 (42 总计)
- 参数数量: 平均: 0.5, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 38.1% (8/21)
- 命名规范: 发现 1 个违规

### 325. backend\ai_services\migrations\0001_initial.py

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

### 326. frontend\src\router\guards.ts

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

### 327. backend\assessments\assessment_models.py

**糟糕指数: 2.01**

> 行数: 144 总计, 82 代码, 33 注释 | 函数: 5 | 类: 5

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 4

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `is_all_done` | L116-118 | 3 | 3 | 0 | 1 | ✓ |
| `__str__` | L37-38 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L82-83 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L109-110 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L142-143 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (4)**

- 🏷️ `__str__()` L37: "__str__" - snake_case
- 🏷️ `__str__()` L82: "__str__" - snake_case
- 🏷️ `__str__()` L109: "__str__" - snake_case
- 🏷️ `__str__()` L142: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.4, 最大: 3
- 认知复杂度: 平均: 1.4, 最大: 3
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 2.2 行, 最大: 3 行
- 文件长度: 82 代码量 (144 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 40.2% (33/82)
- 命名规范: 发现 4 个违规

### 328. backend\exams\serializers.py

**糟糕指数: 1.95**

> 行数: 157 总计, 87 代码, 42 注释 | 函数: 3 | 类: 7

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `validate` | L116-130 | 15 | 6 | 1 | 2 | ✓ |
| `get_questions` | L52-61 | 10 | 1 | 0 | 1 | ✓ |
| `to_internal_value` | L108-111 | 4 | 1 | 0 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.7, 最大: 6
- 认知复杂度: 平均: 3.3, 最大: 8
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 9.7 行, 最大: 15 行
- 文件长度: 87 代码量 (157 总计)
- 参数数量: 平均: 1.7, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 48.3% (42/87)
- 命名规范: 无命名违规

### 329. backend\platform_ai\rag\resource_utils.py

**糟糕指数: 1.92**

> 行数: 199 总计, 141 代码, 24 注释 | 函数: 8 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `ascii_resource_terms` | L86-106 | 21 | 7 | 2 | 1 | ✓ |
| `point_resource_match_terms` | L112-133 | 22 | 7 | 2 | 1 | ✓ |
| `score_resource_point_match` | L139-164 | 26 | 5 | 2 | 2 | ✓ |
| `resource_rank_key` | L170-186 | 17 | 5 | 0 | 2 | ✓ |
| `safe_resource_url` | L30-46 | 17 | 4 | 1 | 1 | ✓ |
| `dedupe_resource_terms` | L65-80 | 16 | 4 | 2 | 1 | ✓ |
| `coerce_resource_text` | L17-24 | 8 | 2 | 0 | 1 | ✓ |
| `normalize_resource_match_text` | L52-59 | 8 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.4, 最大: 7
- 认知复杂度: 平均: 6.6, 最大: 11
- 嵌套深度: 平均: 1.1, 最大: 2
- 函数长度: 平均: 16.9 行, 最大: 26 行
- 文件长度: 141 代码量 (199 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 17.0% (24/141)
- 命名规范: 无命名违规

### 330. backend\exams\migrations\0001_initial.py

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

### 331. backend\users\models.py

**糟糕指数: 1.90**

> 行数: 494 总计, 390 代码, 59 注释 | 函数: 14 | 类: 5

**问题**: ⚠️ 其他问题: 1, 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `is_valid` | L294-304 | 11 | 6 | 1 | 1 | ✓ |
| `is_valid` | L199-205 | 7 | 4 | 1 | 1 | ✓ |
| `is_admin` | L105-107 | 3 | 2 | 0 | 1 | ✓ |
| `__str__` | L184-186 | 3 | 2 | 0 | 1 | ✗ |
| `use` | L210-218 | 9 | 2 | 1 | 2 | ✓ |
| `__str__` | L491-493 | 3 | 2 | 0 | 1 | ✗ |
| `__str__` | L82-83 | 2 | 1 | 0 | 1 | ✗ |
| `is_teacher` | L89-91 | 3 | 1 | 0 | 1 | ✓ |
| `is_student` | L97-99 | 3 | 1 | 0 | 1 | ✓ |
| `generate_code` | L192-194 | 3 | 1 | 0 | 0 | ✓ |
| `__str__` | L280-281 | 2 | 1 | 0 | 1 | ✗ |
| `generate_code` | L287-289 | 3 | 1 | 0 | 0 | ✓ |
| `use` | L309-312 | 4 | 1 | 0 | 1 | ✓ |
| `__str__` | L445-446 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (5)**

- 🏷️ `__str__()` L82: "__str__" - snake_case
- 🏷️ `__str__()` L184: "__str__" - snake_case
- 🏷️ `__str__()` L280: "__str__" - snake_case
- 🏷️ `__str__()` L445: "__str__" - snake_case
- 🏷️ `__str__()` L491: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.9, 最大: 6
- 认知复杂度: 平均: 2.3, 最大: 8
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 4.1 行, 最大: 11 行
- 文件长度: 390 代码量 (494 总计)
- 参数数量: 平均: 0.9, 最大: 2
- 代码重复: 0.0% 重复 (0/14)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 15.1% (59/390)
- 命名规范: 发现 5 个违规

### 332. backend\logs\migrations\0001_initial.py

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

### 333. backend\ai_services\services\path_generation_support.py

**糟糕指数: 1.89**

> 行数: 169 总计, 134 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: ⚠️ 其他问题: 2, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `sync_course_mastery` | L42-93 | 52 | 4 | 2 | 3 | ✓ |
| `predict_course_mastery` | L99-136 | 38 | 4 | 1 | 4 | ✓ |
| `persist_course_mastery` | L142-157 | 16 | 2 | 1 | 3 | ✓ |
| `load_course_point_ids` | L28-36 | 9 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- 📏 `sync_course_mastery()` L42: 52 代码量

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 4
- 认知复杂度: 平均: 4.8, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 28.8 行, 最大: 52 行
- 文件长度: 134 代码量 (169 总计)
- 参数数量: 平均: 2.8, 最大: 4
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 9.0% (12/134)
- 命名规范: 无命名违规

### 334. frontend\src\composables\useCourse.ts

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

### 335. backend\learning\migrations\0001_initial.py

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

### 336. backend\assessments\migrations\0001_initial.py

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

### 337. backend\common\defense_demo_public.py

**糟糕指数: 1.77**

> 行数: 132 总计, 91 代码, 21 注释 | 函数: 7 | 类: 0

**问题**: ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_defense_demo_visible_order` | L107-131 | 25 | 7 | 1 | 2 | ✓ |
| `get_course_defense_demo_config` | L12-21 | 10 | 4 | 1 | 1 | ✓ |
| `get_defense_demo_intro_payload` | L56-71 | 16 | 4 | 1 | 2 | ✓ |
| `get_defense_demo_resource_payload` | L77-86 | 10 | 4 | 1 | 1 | ✓ |
| `get_defense_demo_stage_test_payload` | L92-101 | 10 | 4 | 1 | 1 | ✓ |
| `is_defense_demo_student` | L39-50 | 12 | 3 | 0 | 2 | ✓ |
| `is_defense_demo_primary_course` | L27-33 | 7 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- ❌ L129: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.9, 最大: 7
- 认知复杂度: 平均: 5.3, 最大: 9
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 12.9 行, 最大: 25 行
- 文件长度: 91 代码量 (132 总计)
- 参数数量: 平均: 1.4, 最大: 2
- 代码重复: 0.0% 重复 (0/7)
- 结构分析: 0 个结构问题
- 错误处理: 1/9 个错误被忽略 (11.1%)
- 注释比例: 23.1% (21/91)
- 命名规范: 无命名违规

### 338. backend\knowledge\migrations\0001_initial.py

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

### 339. backend\tools\question_import_support.py

**糟糕指数: 1.74**

> 行数: 99 总计, 92 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 92 代码量 (99 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 2.2% (2/92)
- 命名规范: 无命名违规

### 340. backend\courses\migrations\0001_initial.py

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

### 341. backend\users\migrations\0001_initial.py

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

### 342. backend\logs\models.py

**糟糕指数: 1.68**

> 行数: 145 总计, 126 代码, 9 注释 | 函数: 1 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__str__` | L142-144 | 3 | 2 | 0 | 1 | ✗ |

**全部问题 (1)**

- 🏷️ `__str__()` L142: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 2.0, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.0 行, 最大: 3 行
- 文件长度: 126 代码量 (145 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 7.1% (9/126)
- 命名规范: 发现 1 个违规

### 343. backend\ai_services\models.py

**糟糕指数: 1.68**

> 行数: 98 总计, 84 代码, 6 注释 | 函数: 1 | 类: 1

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__str__` | L95-97 | 3 | 2 | 0 | 1 | ✗ |

**全部问题 (1)**

- 🏷️ `__str__()` L95: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 2.0, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.0 行, 最大: 3 行
- 文件长度: 84 代码量 (98 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 7.1% (6/84)
- 命名规范: 发现 1 个违规

### 344. backend\platform_ai\kt\facade.py

**糟糕指数: 1.66**

> 行数: 54 总计, 26 代码, 15 注释 | 函数: 4 | 类: 1

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `predict_mastery` | L20-22 | 3 | 1 | 0 | 0 | ✓ |
| `batch_predict` | L28-30 | 3 | 1 | 0 | 0 | ✓ |
| `get_learning_recommendations` | L36-38 | 3 | 1 | 0 | 0 | ✓ |
| `get_model_info` | L44-49 | 6 | 1 | 0 | 0 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.8 行, 最大: 6 行
- 文件长度: 26 代码量 (54 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 57.7% (15/26)
- 命名规范: 无命名违规

### 345. backend\courses\views.py

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

### 346. backend\application\teacher\workspace.py

**糟糕指数: 1.63**

> 行数: 61 总计, 51 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_course_workspace` | L16-60 | 45 | 4 | 0 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 45.0 行, 最大: 45 行
- 文件长度: 51 代码量 (61 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 5.9% (3/51)
- 命名规范: 无命名违规

### 347. backend\knowledge\urls.py

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

### 348. backend\platform_ai\rag\student_answer_mixin.py

**糟糕指数: 1.61**

> 行数: 119 总计, 98 代码, 9 注释 | 函数: 2 | 类: 1

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `answer_graph_question` | L35-70 | 36 | 2 | 1 | 4 | ✓ |
| `answer_course_question` | L75-118 | 44 | 2 | 1 | 4 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 40.0 行, 最大: 44 行
- 文件长度: 98 代码量 (119 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 9.2% (9/98)
- 命名规范: 无命名违规

### 349. frontend\src\utils\courseCover.ts

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

### 350. backend\assessments\history_models.py

**糟糕指数: 1.58**

> 行数: 97 总计, 60 代码, 18 注释 | 函数: 3 | 类: 3

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__str__` | L36-38 | 3 | 2 | 0 | 1 | ✗ |
| `__str__` | L66-67 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L95-96 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (3)**

- 🏷️ `__str__()` L36: "__str__" - snake_case
- 🏷️ `__str__()` L66: "__str__" - snake_case
- 🏷️ `__str__()` L95: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.3, 最大: 2
- 认知复杂度: 平均: 1.3, 最大: 2
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 2.3 行, 最大: 3 行
- 文件长度: 60 代码量 (97 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 30.0% (18/60)
- 命名规范: 发现 3 个违规

### 351. backend\assessments\migrations\0004_alter_surveyquestion_options_and_more.py

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

### 352. backend\tools\browser_audit.py

**糟糕指数: 1.55**

> 行数: 45 总计, 33 代码, 5 注释 | 函数: 1 | 类: 0

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `browser_audit` | L12-44 | 33 | 5 | 1 | 5 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 5
- 认知复杂度: 平均: 7.0, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 33.0 行, 最大: 33 行
- 文件长度: 33 代码量 (45 总计)
- 参数数量: 平均: 5.0, 最大: 5
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 15.2% (5/33)
- 命名规范: 无命名违规

### 353. backend\ai_services\serializers.py

**糟糕指数: 1.55**

> 行数: 44 总计, 22 代码, 12 注释 | 函数: 0 | 类: 4

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 22 代码量 (44 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 54.5% (12/22)
- 命名规范: 无命名违规

### 354. backend\users\migrations\0005_remove_habitpreference_reminder_settings.py

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

### 355. backend\courses\models.py

**糟糕指数: 1.53**

> 行数: 313 总计, 229 代码, 44 注释 | 函数: 9 | 类: 5

**问题**: 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `can_edit` | L82-97 | 16 | 6 | 1 | 2 | ✓ |
| `get_manageable_courses` | L103-111 | 9 | 3 | 1 | 2 | ✓ |
| `__str__` | L76-77 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L163-164 | 2 | 1 | 0 | 1 | ✗ |
| `get_student_count` | L169-171 | 3 | 1 | 0 | 1 | ✓ |
| `courses_list` | L177-179 | 3 | 1 | 0 | 1 | ✓ |
| `__str__` | L223-224 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L270-271 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L311-312 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (5)**

- 🏷️ `__str__()` L76: "__str__" - snake_case
- 🏷️ `__str__()` L163: "__str__" - snake_case
- 🏷️ `__str__()` L223: "__str__" - snake_case
- 🏷️ `__str__()` L270: "__str__" - snake_case
- 🏷️ `__str__()` L311: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.8, 最大: 6
- 认知复杂度: 平均: 2.2, 最大: 8
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 4.6 行, 最大: 16 行
- 文件长度: 229 代码量 (313 总计)
- 参数数量: 平均: 1.2, 最大: 2
- 代码重复: 0.0% 重复 (0/9)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 19.2% (44/229)
- 命名规范: 发现 5 个违规

### 356. frontend\src\main.ts

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

### 357. frontend\src\composables\useAIProgress.ts

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

### 358. backend\courses\migrations\0005_announcement.py

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

### 359. backend\models\MEFKT\fusion.py

**糟糕指数: 1.51**

> 行数: 42 总计, 25 代码, 6 注释 | 函数: 2 | 类: 1

**问题**: ⚠️ 其他问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__init__` | L15-25 | 11 | 1 | 0 | 4 | ✓ |
| `forward` | L30-38 | 9 | 1 | 0 | 3 | ✓ |

**全部问题 (1)**

- 🏷️ `__init__()` L15: "__init__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 10.0 行, 最大: 11 行
- 文件长度: 25 代码量 (42 总计)
- 参数数量: 平均: 3.5, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 24.0% (6/25)
- 命名规范: 发现 1 个违规

### 360. backend\exams\student_views.py

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

### 361. backend\common\tests.py

**糟糕指数: 1.46**

> 行数: 174 总计, 141 代码, 18 注释 | 函数: 5 | 类: 1

**问题**: ❌ 错误处理问题: 2, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_course_only_students_should_stay_enrolled_without_primary_course_traces` | L149-173 | 25 | 2 | 1 | 1 | ✓ |
| `setUp` | L30-41 | 12 | 1 | 0 | 1 | ✓ |
| `test_warmup_student_should_receive_full_preset_journey` | L46-77 | 32 | 1 | 0 | 1 | ✓ |
| `test_reseeding_should_not_duplicate_demo_histories_or_paths` | L82-126 | 45 | 1 | 0 | 1 | ✓ |
| `test_primary_course_should_include_ai_demo_queries` | L131-144 | 14 | 1 | 0 | 1 | ✓ |

**全部问题 (3)**

- ❌ L137: 未处理的易出错调用
- ❌ L140: 未处理的易出错调用
- 🏷️ `setUp()` L30: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.2, 最大: 2
- 认知复杂度: 平均: 1.6, 最大: 4
- 嵌套深度: 平均: 0.2, 最大: 1
- 函数长度: 平均: 25.6 行, 最大: 45 行
- 文件长度: 141 代码量 (174 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 2/17 个错误被忽略 (11.8%)
- 注释比例: 12.8% (18/141)
- 命名规范: 发现 1 个违规

### 362. backend\ai_services\services\mefkt_loader.py

**糟糕指数: 1.41**

> 行数: 46 总计, 26 代码, 11 注释 | 函数: 2 | 类: 1

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `auto_load_mefkt_model` | L30-45 | 16 | 4 | 2 | 3 | ✓ |
| `load_model` | L23-24 | 2 | 1 | 0 | 3 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.5, 最大: 4
- 认知复杂度: 平均: 4.5, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 2
- 函数长度: 平均: 9.0 行, 最大: 16 行
- 文件长度: 26 代码量 (46 总计)
- 参数数量: 平均: 3.0, 最大: 3
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 42.3% (11/26)
- 命名规范: 无命名违规

### 363. backend\users\admin_user_management_views.py

**糟糕指数: 1.40**

> 行数: 211 总计, 138 代码, 36 注释 | 函数: 12 | 类: 0

**问题**: 📋 重复问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `admin_user_update` | L78-92 | 15 | 5 | 1 | 2 | ✓ |
| `admin_user_delete` | L100-109 | 10 | 3 | 1 | 2 | ✓ |
| `admin_user_disable` | L132-140 | 9 | 3 | 1 | 2 | ✓ |
| `admin_user_import` | L176-189 | 14 | 3 | 1 | 1 | ✓ |
| `admin_user_detail` | L52-57 | 6 | 2 | 1 | 2 | ✓ |
| `admin_user_create` | L65-70 | 6 | 2 | 1 | 1 | ✓ |
| `admin_user_reset_password` | L117-124 | 8 | 2 | 1 | 2 | ✓ |
| `admin_user_enable` | L148-153 | 6 | 2 | 1 | 2 | ✓ |
| `admin_user_batch_delete` | L161-168 | 8 | 2 | 1 | 1 | ✓ |
| `admin_user_list` | L41-44 | 4 | 1 | 0 | 1 | ✓ |
| `admin_user_export` | L197-199 | 3 | 1 | 0 | 1 | ✓ |
| `admin_user_template` | L207-210 | 4 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- 📋 `admin_user_reset_password()` L117: 重复模式: admin_user_reset_password, admin_user_batch_delete

**详情**:
- 循环复杂度: 平均: 2.3, 最大: 5
- 认知复杂度: 平均: 3.8, 最大: 7
- 嵌套深度: 平均: 0.8, 最大: 1
- 函数长度: 平均: 7.8 行, 最大: 15 行
- 文件长度: 138 代码量 (211 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 8.3% 重复 (1/12)
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 26.1% (36/138)
- 命名规范: 无命名违规

### 364. backend\platform_ai\rag\student.py

**糟糕指数: 1.38**

> 行数: 110 总计, 94 代码, 3 注释 | 函数: 0 | 类: 1

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 94 代码量 (110 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 3.2% (3/94)
- 命名规范: 无命名违规

### 365. backend\users\views.py

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

### 366. backend\users\migrations\0004_alter_habitpreference_review_frequency.py

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

### 367. backend\logs\migrations\0002_alter_operationlog_module.py

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

### 368. backend\learning\migrations\0005_nodeprogress_extra_data.py

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

### 369. backend\learning\migrations\0003_add_skipped_status.py

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

### 370. backend\courses\migrations\0004_course_config.py

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

### 371. backend\knowledge\migrations\0005_alter_knowledgerelation_relation_type.py

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

### 372. backend\ai_services\migrations\0003_add_chat_kt_call_types.py

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

### 373. frontend\src\utils\logger.ts

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

### 374. backend\users\migrations\0002_habitpreference_accept_challenge_and_more.py

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

### 375. backend\application\teacher\contracts.py

**糟糕指数: 1.28**

> 行数: 91 总计, 63 代码, 15 注释 | 函数: 5 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `first_present` | L11-22 | 12 | 6 | 2 | 3 | ✓ |
| `normalize_question_point_ids` | L83-90 | 8 | 3 | 1 | 1 | ✓ |
| `normalize_course_payload` | L28-43 | 16 | 2 | 1 | 1 | ✓ |
| `normalize_exam_payload` | L62-77 | 16 | 2 | 0 | 1 | ✓ |
| `normalize_class_payload` | L49-56 | 8 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.8, 最大: 6
- 认知复杂度: 平均: 4.4, 最大: 10
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 12.0 行, 最大: 16 行
- 文件长度: 63 代码量 (91 总计)
- 参数数量: 平均: 1.4, 最大: 3
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 23.8% (15/63)
- 命名规范: 无命名违规

### 376. backend\users\migrations\0003_alter_user_email_alter_user_phone.py

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

### 377. backend\learning\migrations\0004_pathnode_estimated_minutes_pathnode_node_type.py

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

### 378. backend\assessments\migrations\0006_assessmentstatus_generating_and_more.py

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

### 379. backend\assessments\migrations\0005_question_chapter_question_suggested_score.py

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

### 380. backend\logs\logging_setup.py

**糟糕指数: 1.25**

> 行数: 143 总计, 106 代码, 12 注释 | 函数: 3 | 类: 1

**问题**: 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `_build_debug_logger` | L100-129 | 30 | 5 | 1 | 0 | ✓ |
| `_build_operation_logger` | L80-94 | 15 | 3 | 1 | 0 | ✓ |
| `format` | L69-74 | 6 | 1 | 0 | 2 | ✓ |

**全部问题 (2)**

- 🏷️ `_build_operation_logger()` L80: "_build_operation_logger" - snake_case
- 🏷️ `_build_debug_logger()` L100: "_build_debug_logger" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 5
- 认知复杂度: 平均: 4.3, 最大: 7
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 17.0 行, 最大: 30 行
- 文件长度: 106 代码量 (143 总计)
- 参数数量: 平均: 0.7, 最大: 2
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 11.3% (12/106)
- 命名规范: 发现 2 个违规

### 381. backend\assessments\question_models.py

**糟糕指数: 1.25**

> 行数: 82 总计, 56 代码, 12 注释 | 函数: 2 | 类: 2

**问题**: 🏷️ 命名问题: 2

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `__str__` | L48-49 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L80-81 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (2)**

- 🏷️ `__str__()` L48: "__str__" - snake_case
- 🏷️ `__str__()` L80: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 2.0 行, 最大: 2 行
- 文件长度: 56 代码量 (82 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 21.4% (12/56)
- 命名规范: 发现 2 个违规

### 382. backend\assessments\migrations\0002_initial.py

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

### 383. backend\users\auth_password_views.py

**糟糕指数: 1.24**

> 行数: 81 总计, 52 代码, 8 注释 | 函数: 2 | 类: 0

**问题**: ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `password_reset` | L53-80 | 28 | 6 | 1 | 1 | ✓ |
| `password_reset_send` | L25-44 | 20 | 3 | 1 | 1 | ✓ |

**全部问题 (1)**

- ❌ L78: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 4.5, 最大: 6
- 认知复杂度: 平均: 6.5, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 24.0 行, 最大: 28 行
- 文件长度: 52 代码量 (81 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 1/8 个错误被忽略 (12.5%)
- 注释比例: 15.4% (8/52)
- 命名规范: 无命名违规

### 384. backend\exams\score_policy.py

**糟糕指数: 1.24**

> 行数: 84 总计, 48 代码, 15 注释 | 函数: 5 | 类: 0

**问题**: 📝 注释问题: 1, 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `sum_exam_question_scores` | L26-35 | 10 | 4 | 2 | 1 | ✓ |
| `sync_exam_totals` | L51-64 | 14 | 4 | 1 | 3 | ✓ |
| `sync_course_exam_totals` | L70-83 | 14 | 3 | 1 | 2 | ✓ |
| `_to_decimal` | L19-20 | 2 | 2 | 0 | 1 | ✓ |
| `compute_exam_pass_score` | L41-45 | 5 | 2 | 0 | 2 | ✓ |

**全部问题 (1)**

- 🏷️ `_to_decimal()` L19: "_to_decimal" - snake_case

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 4
- 认知复杂度: 平均: 4.6, 最大: 8
- 嵌套深度: 平均: 0.8, 最大: 2
- 函数长度: 平均: 9.0 行, 最大: 14 行
- 文件长度: 48 代码量 (84 总计)
- 参数数量: 平均: 1.8, 最大: 3
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 31.3% (15/48)
- 命名规范: 发现 1 个违规

### 385. backend\assessments\admin.py

**糟糕指数: 1.21**

> 行数: 82 总计, 46 代码, 21 注释 | 函数: 0 | 类: 7

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 46 代码量 (82 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 45.7% (21/46)
- 命名规范: 无命名违规

### 386. backend\knowledge\migrations\0004_resource_chapter_number_resource_duration_and_more.py

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

### 387. backend\ai_services\test_web_search.py

**糟糕指数: 1.20**

> 行数: 132 总计, 103 代码, 13 注释 | 函数: 3 | 类: 1

**问题**: ⚠️ 其他问题: 1, 🏗️ 结构问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `side_effect` | L103-118 | 16 | 3 | 1 | 4 | ✓ |
| `test_search_with_baidu_should_resolve_redirect_and_filter_domain` | L44-82 | 39 | 1 | 0 | 2 | ✓ |
| `test_search_learning_resources_should_use_configured_engines_in_order` | L91-131 | 25 | 1 | 0 | 3 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.7, 最大: 3
- 认知复杂度: 平均: 2.3, 最大: 5
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 26.7 行, 最大: 39 行
- 文件长度: 103 代码量 (132 总计)
- 参数数量: 平均: 3.0, 最大: 4
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 12.6% (13/103)
- 命名规范: 无命名违规

### 388. backend\common\defense_demo.py

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

### 389. backend\learning\node_detail_views.py

**糟糕指数: 1.19**

> 行数: 134 总计, 105 代码, 10 注释 | 函数: 3 | 类: 0

**问题**: ⚠️ 其他问题: 1, 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `submit_node_exam` | L71-133 | 63 | 5 | 1 | 3 | ✓ |
| `get_path_node_detail` | L27-41 | 15 | 2 | 1 | 2 | ✓ |
| `complete_node_resource` | L49-63 | 15 | 2 | 1 | 3 | ✓ |

**全部问题 (1)**

- 📏 `submit_node_exam()` L71: 63 代码量

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 5
- 认知复杂度: 平均: 5.0, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 31.0 行, 最大: 63 行
- 文件长度: 105 代码量 (134 总计)
- 参数数量: 平均: 2.7, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 9.5% (10/105)
- 命名规范: 无命名违规

### 390. backend\courses\serializers.py

**糟糕指数: 1.19**

> 行数: 107 总计, 60 代码, 27 注释 | 函数: 0 | 类: 5

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 60 代码量 (107 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 45.0% (27/60)
- 命名规范: 无命名违规

### 391. backend\exams\admin.py

**糟糕指数: 1.17**

> 行数: 48 总计, 27 代码, 12 注释 | 函数: 0 | 类: 4

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 27 代码量 (48 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 44.4% (12/27)
- 命名规范: 无命名违规

### 392. backend\platform_ai\rag\corpus_storage.py

**糟糕指数: 1.17**

> 行数: 51 总计, 27 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `load_course_index` | L33-38 | 6 | 2 | 1 | 1 | ✓ |
| `delete_course_index` | L44-50 | 7 | 2 | 1 | 1 | ✓ |
| `get_index_path` | L14-16 | 3 | 1 | 0 | 1 | ✓ |
| `save_course_index` | L22-27 | 6 | 1 | 0 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.5, 最大: 2
- 认知复杂度: 平均: 2.5, 最大: 4
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 5.5 行, 最大: 7 行
- 文件长度: 27 代码量 (51 总计)
- 参数数量: 平均: 1.3, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 44.4% (12/27)
- 命名规范: 无命名违规

### 393. backend\courses\migrations\0003_alter_class_options_class_description_and_more.py

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

### 394. backend\knowledge\admin.py

**糟糕指数: 1.16**

> 行数: 60 总计, 34 代码, 15 注释 | 函数: 0 | 类: 5

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 34 代码量 (60 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 44.1% (15/34)
- 命名规范: 无命名违规

### 395. backend\tools\rebuild_demo.py

**糟糕指数: 1.14**

> 行数: 74 总计, 61 代码, 7 注释 | 函数: 1 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `rebuild_demo_data` | L27-73 | 47 | 2 | 1 | 3 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 47.0 行, 最大: 47 行
- 文件长度: 61 代码量 (74 总计)
- 参数数量: 平均: 3.0, 最大: 3
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 11.5% (7/61)
- 命名规范: 无命名违规

### 396. backend\ai_services\migrations\0002_initial.py

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

### 397. backend\knowledge\migrations\0003_knowledgepoint_category_and_more.py

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

### 398. frontend\src\stores\assessment.ts

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

### 399. frontend\src\router\routes\auth.ts

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

### 400. backend\courses\admin.py

**糟糕指数: 1.05**

> 行数: 50 总计, 29 代码, 12 注释 | 函数: 0 | 类: 4

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 29 代码量 (50 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 41.4% (12/29)
- 命名规范: 无命名违规

### 401. backend\learning\admin.py

**糟糕指数: 1.03**

> 行数: 38 总计, 22 代码, 9 注释 | 函数: 0 | 类: 3

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
- 注释比例: 40.9% (9/22)
- 命名规范: 无命名违规

### 402. backend\wisdom_edu_api\urls.py

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

### 403. backend\platform_ai\__init__.py

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

### 404. backend\courses\migrations\0002_initial.py

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

### 405. backend\knowledge\models.py

**糟糕指数: 0.96**

> 行数: 372 总计, 291 代码, 40 注释 | 函数: 8 | 类: 5

**问题**: 🏷️ 命名问题: 5

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_tags_list` | L143-147 | 5 | 2 | 1 | 1 | ✓ |
| `__str__` | L123-124 | 2 | 1 | 0 | 1 | ✗ |
| `get_prerequisites` | L129-131 | 3 | 1 | 0 | 1 | ✓ |
| `get_dependents` | L136-138 | 3 | 1 | 0 | 1 | ✓ |
| `__str__` | L204-205 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L274-275 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L327-328 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L370-371 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (5)**

- 🏷️ `__str__()` L123: "__str__" - snake_case
- 🏷️ `__str__()` L204: "__str__" - snake_case
- 🏷️ `__str__()` L274: "__str__" - snake_case
- 🏷️ `__str__()` L327: "__str__" - snake_case
- 🏷️ `__str__()` L370: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.1, 最大: 2
- 认知复杂度: 平均: 1.4, 最大: 4
- 嵌套深度: 平均: 0.1, 最大: 1
- 函数长度: 平均: 2.6 行, 最大: 5 行
- 文件长度: 291 代码量 (372 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 13.7% (40/291)
- 命名规范: 发现 5 个违规

### 406. backend\exams\migrations\0003_alter_feedbackreport_unique_together_and_more.py

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

### 407. backend\users\student_views.py

**糟糕指数: 0.96**

> 行数: 167 总计, 125 代码, 18 注释 | 函数: 6 | 类: 0

**问题**: ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `update_student_profile` | L73-93 | 21 | 3 | 1 | 1 | ✓ |
| `profile_compare` | L129-153 | 25 | 3 | 1 | 1 | ✓ |
| `update_habit_preference` | L52-65 | 14 | 2 | 1 | 1 | ✓ |
| `get_profile_history` | L101-121 | 21 | 2 | 1 | 1 | ✓ |
| `get_profile` | L34-44 | 11 | 1 | 0 | 1 | ✓ |
| `profile_export` | L161-166 | 6 | 1 | 0 | 1 | ✓ |

**全部问题 (1)**

- ❌ L119: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 3
- 认知复杂度: 平均: 3.3, 最大: 5
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 16.3 行, 最大: 25 行
- 文件长度: 125 代码量 (167 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 1/6 个错误被忽略 (16.7%)
- 注释比例: 14.4% (18/125)
- 命名规范: 无命名违规

### 408. backend\ai_services\urls.py

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

### 409. backend\learning\models.py

**糟糕指数: 0.94**

> 行数: 267 总计, 221 代码, 25 注释 | 函数: 5 | 类: 3

**问题**: 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `mastery_improvement` | L262-266 | 5 | 3 | 1 | 1 | ✓ |
| `progress_percent` | L68-74 | 7 | 2 | 1 | 1 | ✓ |
| `__str__` | L61-62 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L189-190 | 2 | 1 | 0 | 1 | ✗ |
| `__str__` | L255-256 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (3)**

- 🏷️ `__str__()` L61: "__str__" - snake_case
- 🏷️ `__str__()` L189: "__str__" - snake_case
- 🏷️ `__str__()` L255: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 3
- 认知复杂度: 平均: 2.4, 最大: 5
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 3.6 行, 最大: 7 行
- 文件长度: 221 代码量 (267 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 11.3% (25/221)
- 命名规范: 发现 3 个违规

### 410. backend\learning\stage_test_submission.py

**糟糕指数: 0.93**

> 行数: 56 总计, 46 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `submit_stage_test_answers` | L20-55 | 36 | 3 | 1 | 3 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 3
- 认知复杂度: 平均: 5.0, 最大: 5
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 36.0 行, 最大: 36 行
- 文件长度: 46 代码量 (56 总计)
- 参数数量: 平均: 3.0, 最大: 3
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 6.5% (3/46)
- 命名规范: 无命名违规

### 411. backend\tools\kt_synthetic_support.py

**糟糕指数: 0.91**

> 行数: 51 总计, 44 代码, 2 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 44 代码量 (51 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 4.5% (2/44)
- 命名规范: 无命名违规

### 412. backend\ai_services\services\mefkt_runtime_types.py

**糟糕指数: 0.91**

> 行数: 132 总计, 75 代码, 29 注释 | 函数: 1 | 类: 8

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `values_list` | L24-25 | 2 | 1 | 0 | 3 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 2.0 行, 最大: 2 行
- 文件长度: 75 代码量 (132 总计)
- 参数数量: 平均: 3.0, 最大: 3
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 38.7% (29/75)
- 命名规范: 无命名违规

### 413. backend\learning\views.py

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

### 414. backend\exams\migrations\0002_initial.py

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

### 415. backend\knowledge\migrations\0002_initial.py

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

### 416. backend\exams\student_initial_assessment_views.py

**糟糕指数: 0.86**

> 行数: 87 总计, 67 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `initial_assessment_submit` | L55-86 | 32 | 6 | 1 | 1 | ✓ |
| `initial_assessment_start` | L29-47 | 19 | 4 | 1 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 5.0, 最大: 6
- 认知复杂度: 平均: 7.0, 最大: 8
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 25.5 行, 最大: 32 行
- 文件长度: 67 代码量 (87 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/3 个错误被忽略 (0.0%)
- 注释比例: 9.0% (6/67)
- 命名规范: 无命名违规

### 417. backend\assessments\migrations\0003_initial.py

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

### 418. backend\exams\models.py

**糟糕指数: 0.83**

> 行数: 264 总计, 202 代码, 30 注释 | 函数: 5 | 类: 4

**问题**: 🏷️ 命名问题: 3

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `score_percent` | L181-185 | 5 | 3 | 1 | 1 | ✓ |
| `__str__` | L260-263 | 4 | 2 | 1 | 1 | ✗ |
| `__str__` | L102-103 | 2 | 1 | 0 | 1 | ✗ |
| `question_count` | L109-111 | 3 | 1 | 0 | 1 | ✓ |
| `__str__` | L174-175 | 2 | 1 | 0 | 1 | ✗ |

**全部问题 (3)**

- 🏷️ `__str__()` L102: "__str__" - snake_case
- 🏷️ `__str__()` L174: "__str__" - snake_case
- 🏷️ `__str__()` L260: "__str__" - snake_case

**详情**:
- 循环复杂度: 平均: 1.6, 最大: 3
- 认知复杂度: 平均: 2.4, 最大: 5
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 3.2 行, 最大: 5 行
- 文件长度: 202 代码量 (264 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/5)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 14.9% (30/202)
- 命名规范: 发现 3 个违规

### 419. backend\platform_ai\kt\torch_device.py

**糟糕指数: 0.83**

> 行数: 73 总计, 50 代码, 9 注释 | 函数: 2 | 类: 1

**问题**: 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `resolve_torch_device` | L44-72 | 29 | 5 | 1 | 1 | ✓ |
| `_parse_bool_env` | L33-38 | 6 | 2 | 1 | 2 | ✓ |

**全部问题 (1)**

- 🏷️ `_parse_bool_env()` L33: "_parse_bool_env" - snake_case

**详情**:
- 循环复杂度: 平均: 3.5, 最大: 5
- 认知复杂度: 平均: 5.5, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 17.5 行, 最大: 29 行
- 文件长度: 50 代码量 (73 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 18.0% (9/50)
- 命名规范: 发现 1 个违规

### 420. backend\learning\migrations\0002_initial.py

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

### 421. backend\tools\question_import_types.py

**糟糕指数: 0.80**

> 行数: 80 总计, 46 代码, 17 注释 | 函数: 1 | 类: 4

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `record_import` | L43-47 | 5 | 2 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 5.0 行, 最大: 5 行
- 文件长度: 46 代码量 (80 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 37.0% (17/46)
- 命名规范: 无命名违规

### 422. backend\common\pagination.py

**糟糕指数: 0.67**

> 行数: 79 总计, 53 代码, 10 注释 | 函数: 3 | 类: 0

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `parse_pagination` | L32-52 | 21 | 5 | 0 | 4 | ✓ |
| `paginate_list` | L58-75 | 18 | 3 | 0 | 3 | ✓ |
| `safe_int` | L15-26 | 12 | 2 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.3, 最大: 5
- 认知复杂度: 平均: 4.0, 最大: 5
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 17.0 行, 最大: 21 行
- 文件长度: 53 代码量 (79 总计)
- 参数数量: 平均: 3.0, 最大: 4
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 18.9% (10/53)
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

### 424. backend\platform_ai\search\providers.py

**糟糕指数: 0.67**

> 行数: 42 总计, 24 代码, 6 注释 | 函数: 1 | 类: 1

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `search_learning_resources` | L25-37 | 13 | 1 | 0 | 4 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 13.0 行, 最大: 13 行
- 文件长度: 24 代码量 (42 总计)
- 参数数量: 平均: 4.0, 最大: 4
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 25.0% (6/24)
- 命名规范: 无命名违规

### 425. backend\platform_ai\rag\runtime_cypher.py

**糟糕指数: 0.67**

> 行数: 184 总计, 133 代码, 25 注释 | 函数: 8 | 类: 0

**问题**: ⚠️ 其他问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `fallback_cypher_from_prompt` | L157-178 | 22 | 4 | 1 | 1 | ✓ |
| `build_target_match` | L40-59 | 20 | 3 | 1 | 4 | ✓ |
| `extract_line_value` | L20-23 | 4 | 2 | 0 | 2 | ✓ |
| `extract_user_question` | L29-34 | 6 | 2 | 1 | 1 | ✓ |
| `build_prerequisite_query` | L65-81 | 17 | 1 | 0 | 2 | ✓ |
| `build_postrequisite_query` | L87-103 | 17 | 1 | 0 | 2 | ✓ |
| `build_path_query` | L109-130 | 22 | 1 | 0 | 2 | ✓ |
| `build_resource_query` | L136-151 | 16 | 1 | 0 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.9, 最大: 4
- 认知复杂度: 平均: 2.6, 最大: 6
- 嵌套深度: 平均: 0.4, 最大: 1
- 函数长度: 平均: 15.5 行, 最大: 22 行
- 文件长度: 133 代码量 (184 总计)
- 参数数量: 平均: 2.0, 最大: 4
- 代码重复: 0.0% 重复 (0/8)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 18.8% (25/133)
- 命名规范: 无命名违规

### 426. backend\logs\urls.py

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

### 428. backend\platform_ai\llm\agent_json.py

**糟糕指数: 0.65**

> 行数: 66 总计, 40 代码, 12 注释 | 函数: 4 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `parse_json_payload` | L15-21 | 7 | 4 | 2 | 1 | ✓ |
| `extract_inline_json_candidate` | L39-45 | 7 | 3 | 1 | 1 | ✓ |
| `parse_json_candidate` | L51-57 | 7 | 3 | 1 | 1 | ✓ |
| `iter_json_candidates` | L27-33 | 7 | 2 | 1 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 4
- 认知复杂度: 平均: 5.5, 最大: 8
- 嵌套深度: 平均: 1.3, 最大: 2
- 函数长度: 平均: 7.0 行, 最大: 7 行
- 文件长度: 40 代码量 (66 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 30.0% (12/40)
- 命名规范: 无命名违规

### 429. backend\knowledge\tests.py

**糟糕指数: 0.63**

> 行数: 87 总计, 65 代码, 12 注释 | 函数: 3 | 类: 1

**问题**: 🏷️ 命名问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `setUp` | L21-41 | 21 | 1 | 0 | 1 | ✓ |
| `test_knowledge_map_should_fail_when_neo4j_graph_missing` | L48-51 | 4 | 1 | 0 | 1 | ✓ |
| `test_knowledge_map_should_mark_data_source_as_neo4j` | L58-86 | 29 | 1 | 0 | 3 | ✓ |

**全部问题 (1)**

- 🏷️ `setUp()` L21: "setUp" - snake_case

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 18.0 行, 最大: 29 行
- 文件长度: 65 代码量 (87 总计)
- 参数数量: 平均: 1.7, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 18.5% (12/65)
- 命名规范: 发现 1 个违规

### 430. backend\models\MEFKT\__init__.py

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

### 431. frontend\src\router\routes\student.ts

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

### 432. backend\ai_services\services\llm_provider_config.py

**糟糕指数: 0.58**

> 行数: 151 总计, 130 代码, 8 注释 | 函数: 0 | 类: 2

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 130 代码量 (151 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 6.2% (8/130)
- 命名规范: 无命名违规

### 433. backend\users\admin.py

**糟糕指数: 0.56**

> 行数: 43 总计, 27 代码, 9 注释 | 函数: 0 | 类: 3

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 27 代码量 (43 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 33.3% (9/27)
- 命名规范: 无命名违规

### 434. backend\exams\views.py

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

### 435. backend\platform_ai\rag\corpus_types.py

**糟糕指数: 0.40**

> 行数: 91 总计, 58 代码, 18 注释 | 函数: 3 | 类: 3

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `as_dict` | L25-34 | 10 | 1 | 0 | 1 | ✓ |
| `as_dict` | L54-63 | 10 | 1 | 0 | 1 | ✓ |
| `as_dict` | L82-90 | 9 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 9.7 行, 最大: 10 行
- 文件长度: 58 代码量 (91 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 31.0% (18/58)
- 命名规范: 无命名违规

### 436. backend\knowledge\teacher_resource_views.py

**糟糕指数: 0.40**

> 行数: 172 总计, 131 代码, 18 注释 | 函数: 6 | 类: 0

**问题**: ❌ 错误处理问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `resource_create` | L59-79 | 21 | 4 | 1 | 1 | ✓ |
| `resource_update` | L87-105 | 19 | 4 | 1 | 2 | ✓ |
| `resource_upload` | L130-151 | 22 | 4 | 1 | 1 | ✓ |
| `resource_link_knowledge` | L159-171 | 13 | 3 | 1 | 2 | ✓ |
| `resource_list` | L36-51 | 16 | 2 | 1 | 1 | ✓ |
| `resource_delete` | L113-122 | 10 | 2 | 1 | 2 | ✓ |

**全部问题 (1)**

- ❌ L118: 未处理的易出错调用

**详情**:
- 循环复杂度: 平均: 3.2, 最大: 4
- 认知复杂度: 平均: 5.2, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 16.8 行, 最大: 22 行
- 文件长度: 131 代码量 (172 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 0.0% 重复 (0/6)
- 结构分析: 0 个结构问题
- 错误处理: 1/10 个错误被忽略 (10.0%)
- 注释比例: 13.7% (18/131)
- 命名规范: 无命名违规

### 437. frontend\src\env.d.ts

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

### 438. backend\tools\rag_index.py

**糟糕指数: 0.33**

> 行数: 36 总计, 20 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_rag_index` | L13-26 | 14 | 3 | 1 | 1 | ✓ |
| `refresh_rag_corpus` | L32-35 | 4 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 3
- 认知复杂度: 平均: 3.0, 最大: 5
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 9.0 行, 最大: 14 行
- 文件长度: 20 代码量 (36 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 30.0% (6/20)
- 命名规范: 无命名违规

### 439. backend\platform_ai\rag\runtime_course.py

**糟糕指数: 0.33**

> 行数: 17 总计, 10 代码, 3 注释 | 函数: 0 | 类: 1

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
- 注释比例: 30.0% (3/10)
- 命名规范: 无命名违规

### 440. backend\knowledge\migrations\0006_knowledgepoint_introduction_fields.py

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

### 441. backend\models\MEFKT\model.py

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

### 442. backend\platform_ai\rag\corpus.py

**糟糕指数: 0.15**

> 行数: 37 总计, 22 代码, 6 注释 | 函数: 2 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `build_course_graph_index` | L14-16 | 3 | 1 | 0 | 1 | ✓ |
| `build_course_corpus` | L22-25 | 4 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 3.5 行, 最大: 4 行
- 文件长度: 22 代码量 (37 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 27.3% (6/22)
- 命名规范: 无命名违规

### 443. backend\ai_services\services\mefkt_runtime_support.py

**糟糕指数: 0.09**

> 行数: 40 总计, 32 代码, 3 注释 | 函数: 0 | 类: 0

**问题**: 📝 注释问题: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 32 代码量 (40 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 9.4% (3/32)
- 命名规范: 无命名违规

### 444. backend\learning\stage_test_submit_views.py

**糟糕指数: 0.05**

> 行数: 42 总计, 31 代码, 3 注释 | 函数: 1 | 类: 0

**问题**: 📝 注释问题: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `submit_stage_test` | L17-41 | 25 | 4 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 6.0, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 25.0 行, 最大: 25 行
- 文件长度: 31 代码量 (42 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 9.7% (3/31)
- 命名规范: 无命名违规

### 445. frontend\vite.config.ts

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

### 446. backend\manage.py

**糟糕指数: 0.00**

> 行数: 26 总计, 17 代码, 4 注释 | 函数: 1 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `main` | L10-21 | 12 | 2 | 1 | 0 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 12.0 行, 最大: 12 行
- 文件长度: 17 代码量 (26 总计)
- 参数数量: 平均: 0.0, 最大: 0
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 23.5% (4/17)
- 命名规范: 无命名违规

### 447. backend\wisdom_edu_api\__init__.py

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

### 448. backend\users\__init__.py

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

### 449. backend\users\urls.py

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

### 450. backend\users\apps.py

**糟糕指数: 0.00**

> 行数: 19 总计, 13 代码, 3 注释 | 函数: 0 | 类: 1

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
- 注释比例: 23.1% (3/13)
- 命名规范: 无命名违规

### 451. backend\tools\__init__.py

**糟糕指数: 0.00**

> 行数: 152 总计, 132 代码, 16 注释 | 函数: 0 | 类: 0

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 132 代码量 (152 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 12.1% (16/132)
- 命名规范: 无命名违规

### 452. backend\tools\question_import_records.py

**糟糕指数: 0.00**

> 行数: 33 总计, 23 代码, 5 注释 | 函数: 1 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `create_question_from_payload` | L18-32 | 15 | 1 | 0 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 15.0 行, 最大: 15 行
- 文件长度: 23 代码量 (33 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 21.7% (5/23)
- 命名规范: 无命名违规

### 453. backend\tools\mefkt_paths.py

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

### 454. backend\tools\kt_synthetic_math.py

**糟糕指数: 0.00**

> 行数: 31 总计, 18 代码, 2 注释 | 函数: 3 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `mean_or_default` | L22-27 | 6 | 2 | 1 | 2 | ✓ |
| `clamp_value` | L11-13 | 3 | 1 | 0 | 3 | ✓ |
| `sigmoid` | L16-19 | 4 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.3, 最大: 2
- 认知复杂度: 平均: 2.0, 最大: 4
- 嵌套深度: 平均: 0.3, 最大: 1
- 函数长度: 平均: 4.3 行, 最大: 6 行
- 文件长度: 18 代码量 (31 总计)
- 参数数量: 平均: 2.0, 最大: 3
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 11.1% (2/18)
- 命名规范: 无命名违规

### 455. backend\logs\__init__.py

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

### 456. backend\logs\serializers.py

**糟糕指数: 0.00**

> 行数: 43 总计, 30 代码, 6 注释 | 函数: 0 | 类: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 30 代码量 (43 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 20.0% (6/30)
- 命名规范: 无命名违规

### 457. backend\logs\apps.py

**糟糕指数: 0.00**

> 行数: 19 总计, 13 代码, 3 注释 | 函数: 0 | 类: 1

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
- 注释比例: 23.1% (3/13)
- 命名规范: 无命名违规

### 458. backend\logs\admin.py

**糟糕指数: 0.00**

> 行数: 27 总计, 19 代码, 3 注释 | 函数: 0 | 类: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 19 代码量 (27 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 15.8% (3/19)
- 命名规范: 无命名违规

### 459. backend\learning\__init__.py

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

### 460. backend\learning\urls.py

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

### 461. backend\learning\student_rag_views.py

**糟糕指数: 0.00**

> 行数: 25 总计, 16 代码, 3 注释 | 函数: 1 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_ai_resources` | L19-24 | 6 | 2 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 6.0 行, 最大: 6 行
- 文件长度: 16 代码量 (25 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 18.8% (3/16)
- 命名规范: 无命名违规

### 462. backend\learning\stage_test_models.py

**糟糕指数: 0.00**

> 行数: 32 总计, 20 代码, 3 注释 | 函数: 0 | 类: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 20 代码量 (32 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 15.0% (3/20)
- 命名规范: 无命名违规

### 463. backend\learning\stage_test_get_views.py

**糟糕指数: 0.00**

> 行数: 36 总计, 26 代码, 3 注释 | 函数: 1 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `get_stage_test` | L17-35 | 19 | 4 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 6.0, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 19.0 行, 最大: 19 行
- 文件长度: 26 代码量 (36 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/1 个错误被忽略 (0.0%)
- 注释比例: 11.5% (3/26)
- 命名规范: 无命名违规

### 464. backend\learning\apps.py

**糟糕指数: 0.00**

> 行数: 19 总计, 13 代码, 3 注释 | 函数: 0 | 类: 1

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
- 注释比例: 23.1% (3/13)
- 命名规范: 无命名违规

### 465. backend\exams\__init__.py

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

### 466. backend\exams\urls.py

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

### 467. backend\exams\student_exam_views.py

**糟糕指数: 0.00**

> 行数: 45 总计, 29 代码, 6 注释 | 函数: 2 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `exam_detail` | L34-44 | 11 | 3 | 1 | 2 | ✓ |
| `exam_list` | L24-26 | 3 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 3
- 认知复杂度: 平均: 3.0, 最大: 5
- 嵌套深度: 平均: 0.5, 最大: 1
- 函数长度: 平均: 7.0 行, 最大: 11 行
- 文件长度: 29 代码量 (45 总计)
- 参数数量: 平均: 1.5, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 20.7% (6/29)
- 命名规范: 无命名违规

### 468. backend\exams\student_class_views.py

**糟糕指数: 0.00**

> 行数: 121 总计, 86 代码, 12 注释 | 函数: 4 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `student_class_ranking` | L44-69 | 26 | 5 | 1 | 2 | ✓ |
| `student_class_assignments` | L102-120 | 19 | 5 | 1 | 2 | ✓ |
| `student_class_members` | L23-36 | 14 | 3 | 1 | 2 | ✓ |
| `student_class_notifications` | L77-94 | 18 | 3 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 5
- 认知复杂度: 平均: 6.0, 最大: 7
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 19.3 行, 最大: 26 行
- 文件长度: 86 代码量 (121 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 0.0% 重复 (0/4)
- 结构分析: 0 个结构问题
- 错误处理: 0/4 个错误被忽略 (0.0%)
- 注释比例: 14.0% (12/86)
- 命名规范: 无命名违规

### 469. backend\exams\apps.py

**糟糕指数: 0.00**

> 行数: 19 总计, 13 代码, 3 注释 | 函数: 0 | 类: 1

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
- 注释比例: 23.1% (3/13)
- 命名规范: 无命名违规

### 470. backend\courses\__init__.py

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

### 471. backend\courses\urls.py

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

### 472. backend\courses\signals.py

**糟糕指数: 0.00**

> 行数: 31 总计, 18 代码, 4 注释 | 函数: 1 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `cleanup_deleted_course_artifacts` | L21-30 | 10 | 4 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 4.0, 最大: 4
- 认知复杂度: 平均: 6.0, 最大: 6
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 10.0 行, 最大: 10 行
- 文件长度: 18 代码量 (31 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 22.2% (4/18)
- 命名规范: 无命名违规

### 473. backend\courses\course_cleanup.py

**糟糕指数: 0.00**

> 行数: 31 总计, 20 代码, 3 注释 | 函数: 1 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `cleanup_course_runtime_artifacts` | L18-30 | 13 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 13.0 行, 最大: 13 行
- 文件长度: 20 代码量 (31 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 15.0% (3/20)
- 命名规范: 无命名违规

### 474. backend\courses\apps.py

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

### 475. backend\courses\admin_course_class_stats_views.py

**糟糕指数: 0.00**

> 行数: 60 总计, 41 代码, 7 注释 | 函数: 2 | 类: 0

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `admin_course_statistics` | L18-36 | 19 | 2 | 1 | 2 | ✓ |
| `admin_class_statistics` | L44-59 | 16 | 2 | 1 | 2 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 2.0, 最大: 2
- 认知复杂度: 平均: 4.0, 最大: 4
- 嵌套深度: 平均: 1.0, 最大: 1
- 函数长度: 平均: 17.5 行, 最大: 19 行
- 文件长度: 41 代码量 (60 总计)
- 参数数量: 平均: 2.0, 最大: 2
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 0/2 个错误被忽略 (0.0%)
- 注释比例: 17.1% (7/41)
- 命名规范: 无命名违规

### 476. backend\common\__init__.py

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

### 477. backend\common\urls.py

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

### 478. backend\common\test_responses.py

**糟糕指数: 0.00**

> 行数: 58 总计, 40 代码, 9 注释 | 函数: 2 | 类: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `test_error_response_should_include_structured_error_details` | L19-39 | 21 | 1 | 0 | 1 | ✓ |
| `test_exception_handler_should_flatten_field_message` | L44-57 | 14 | 1 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 1.0, 最大: 1
- 认知复杂度: 平均: 1.0, 最大: 1
- 嵌套深度: 平均: 0.0, 最大: 0
- 函数长度: 平均: 17.5 行, 最大: 21 行
- 文件长度: 40 代码量 (58 总计)
- 参数数量: 平均: 1.0, 最大: 1
- 代码重复: 未发现函数
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 22.5% (9/40)
- 命名规范: 无命名违规

### 479. backend\common\neo4j_service.py

**糟糕指数: 0.00**

> 行数: 24 总计, 14 代码, 3 注释 | 函数: 0 | 类: 1

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 未发现函数
- 认知复杂度: 未发现函数
- 嵌套深度: 未发现函数
- 函数长度: 未发现函数
- 文件长度: 14 代码量 (24 总计)
- 参数数量: 未发现函数
- 代码重复: 未发现函数
- 结构分析: 未发现函数
- 错误处理: 未发现函数
- 注释比例: 21.4% (3/14)
- 命名规范: 无命名违规

### 480. backend\common\apps.py

**糟糕指数: 0.00**

> 行数: 19 总计, 13 代码, 3 注释 | 函数: 0 | 类: 1

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
- 注释比例: 23.1% (3/13)
- 命名规范: 无命名违规

### 481. backend\assessments\__init__.py

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

### 482. backend\assessments\urls.py

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

### 483. backend\assessments\apps.py

**糟糕指数: 0.00**

> 行数: 19 总计, 13 代码, 3 注释 | 函数: 0 | 类: 1

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
- 注释比例: 23.1% (3/13)
- 命名规范: 无命名违规

### 484. backend\knowledge\__init__.py

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

### 485. backend\knowledge\apps.py

**糟糕指数: 0.00**

> 行数: 19 总计, 13 代码, 3 注释 | 函数: 0 | 类: 1

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
- 注释比例: 23.1% (3/13)
- 命名规范: 无命名违规

### 486. backend\ai_services\__init__.py

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

### 487. backend\ai_services\apps.py

**糟糕指数: 0.00**

> 行数: 19 总计, 13 代码, 3 注释 | 函数: 0 | 类: 1

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
- 注释比例: 23.1% (3/13)
- 命名规范: 无命名违规

### 488. backend\ai_services\admin.py

**糟糕指数: 0.00**

> 行数: 19 总计, 13 代码, 3 注释 | 函数: 0 | 类: 1

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
- 注释比例: 23.1% (3/13)
- 命名规范: 无命名违规

### 489. backend\users\migrations\__init__.py

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

### 490. backend\platform_ai\kt\datasets.py

**糟糕指数: 0.00**

> 行数: 110 总计, 78 代码, 12 注释 | 函数: 3 | 类: 1

#### 函数详情

| 函数 | 行范围 | 行数 | 复杂度 | 嵌套 | 参数 | 注释 |
|:-----|------:|------:|------:|------:|------:|:------:|
| `list_public_datasets` | L93-108 | 16 | 4 | 1 | 0 | ✓ |
| `get_public_dataset_info` | L72-87 | 16 | 3 | 1 | 1 | ✓ |
| `is_available` | L35-37 | 3 | 2 | 0 | 1 | ✓ |

✓ 代码质量良好，没有明显问题

**详情**:
- 循环复杂度: 平均: 3.0, 最大: 4
- 认知复杂度: 平均: 4.3, 最大: 6
- 嵌套深度: 平均: 0.7, 最大: 1
- 函数长度: 平均: 11.7 行, 最大: 16 行
- 文件长度: 78 代码量 (110 总计)
- 参数数量: 平均: 0.7, 最大: 1
- 代码重复: 0.0% 重复 (0/3)
- 结构分析: 0 个结构问题
- 错误处理: 未检测到易出错调用
- 注释比例: 15.4% (12/78)
- 命名规范: 无命名违规

### 491. backend\logs\migrations\__init__.py

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

### 492. backend\learning\migrations\__init__.py

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

### 493. backend\exams\migrations\__init__.py

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

### 494. backend\courses\migrations\__init__.py

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

### 495. backend\common\migrations\__init__.py

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

### 496. backend\assessments\migrations\__init__.py

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

### 497. backend\knowledge\migrations\__init__.py

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

### 498. backend\ai_services\migrations\__init__.py

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

### 499. frontend\src\router\routes\admin.ts

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

### 500. frontend\src\api\admin\index.ts

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

## 最差函数 Top 10

| 函数 | 文件 | 复杂度 | 嵌套 | 行数 |
|:-----|:-----|------:|------:|------:|
| `exam_update` | backend\exams\teacher_exam_management_views.py | 17 | 3 | 65 |
| `_resolve_habit_field` | backend\assessments\habit_views.py | 17 | 1 | 22 |
| `build_tools_query_context` | backend\platform_ai\rag\runtime_graph_query_support.py | 16 | 2 | 59 |
| `_load_llm_settings` | backend\wisdom_edu_api\settings_ai.py | 15 | 1 | 79 |
| `load_csv_sequences` | backend\tools\mefkt_public_data.py | 15 | 2 | 41 |
| `_dispatch_import_commands` | backend\tools\cli_parser.py | 15 | 1 | 33 |
| `_handle_data_menu_choice` | backend\tools\cli_menu.py | 15 | 2 | 45 |
| `_handle_graphrag_and_demo_menu_choice` | backend\tools\cli_menu.py | 15 | 2 | 30 |
| `student_flow_smoke` | backend\tools\api_smoke.py | 15 | 3 | 100 |
| `get_student_resources` | backend\knowledge\resource_views.py | 15 | 1 | 61 |

## 诊断结论 {#conclusion}

🌸 **偶有异味** - 基本没事，但是有伤风化

👍 继续保持，你是编码界的一股清流，代码洁癖者的骄傲

---

*由 [fuck-u-code](https://github.com/Done-0/fuck-u-code) 生成*