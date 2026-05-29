# API 端点测试报告

> 生成时间：2026-05-28 18:02:24 UTC
> 测试地址：`http://127.0.0.1:8000`
> 数据说明：本轮已按用户授权执行 `pg-bootstrap` 重建本地样例库，并创建少量 OpenAPI endpoint audit 临时夹具。

## 汇总

- OpenAPI operation 总数：225
- 非 5xx / 可达结果：225
- 5xx 或请求异常：0
- 文档化状态命中：225
- 可达但未文档化状态：0
- 后端错误：0

### 状态码分布

- `200`：158
- `201`：10
- `400`：30
- `401`：1
- `403`：1
- `404`：25

### 账号与上下文

- 学生 token：可用，账号 `student1`。
- 教师 token：可用，账号 `teacher1`。
- 管理员 token：可用，账号 `admin`。
- 课程：`OpenAPI 巡检名称`，course_id=`146`。
- 班级：`OpenAPI 巡检名称`，class_id=`99`。

## 逐端点结果

### 1. `GET /health/`

健康检查。本次以 `anonymous` 角色请求 `http://127.0.0.1:8000/health/`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `22` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 2. `POST /api/auth/register`

注册学生、教师或管理员账号。本次以 `anonymous` 角色请求 `http://127.0.0.1:8000/api/auth/register`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `201`，OpenAPI 声明状态码为 `200, 201, 400`，耗时 `766` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=201, msg='注册成功'。

### 3. `POST /api/auth/login`

登录。本次以 `anonymous` 角色请求 `http://127.0.0.1:8000/api/auth/login`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `925` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='登录成功'。

### 4. `POST /api/auth/logout`

登出并尝试加入 refresh token 黑名单。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/auth/logout`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 401`，耗时 `568` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='退出成功'。

### 5. `GET /api/auth/userinfo`

获取当前用户信息。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/auth/userinfo`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 401`，耗时 `540` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 6. `PUT /api/auth/userinfo/update`

更新当前用户信息和头像。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/auth/userinfo/update`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `multipart/form-data`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `487` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='没有可更新的字段'。

### 7. `POST /api/auth/token/refresh`

刷新 JWT。本次以 `anonymous` 角色请求 `http://127.0.0.1:8000/api/auth/token/refresh`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `401`，OpenAPI 声明状态码为 `200, 400, 401`，耗时 `517` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=401, msg='刷新令牌无效或已过期'。

### 8. `POST /api/auth/password/change`

修改当前用户密码。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/auth/password/change`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `1334` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='密码修改成功'。

### 9. `POST /api/auth/password/reset/send`

发送密码重置验证码。本次以 `anonymous` 角色请求 `http://127.0.0.1:8000/api/auth/password/reset/send`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `320` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='如果该邮箱已注册，验证码已发送'。

### 10. `POST /api/auth/password/reset`

使用验证码重置密码。本次以 `anonymous` 角色请求 `http://127.0.0.1:8000/api/auth/password/reset`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `529` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='验证码无效或已过期'。

### 11. `GET /api/student/profile`

获取当前学生画像。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/profile`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `331` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 12. `PUT /api/student/profile/habit`

更新学习习惯偏好。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/profile/habit`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `486` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg="{'preferred_resource': [ErrorDetail(string='“OpenAPI audit” 不是合法选项。', code='invalid_choice')], 'preferred_study_time': [ErrorDetail(string='“2026-05-28T18:00:01.777273+00:00” 不是合法选项。', code='invalid_choice')], 'study_pace': [ErrorDetail(string='“OpenAPI audit” 不是合法选项。', code='invalid_choice')], 'study_duration': [ErrorDetail(string='“OpenAPI audit” 不是合法选项。', code='invalid_choice')], 'review_frequency': [ErrorDetail(string='“OpenAPI audit” 不是合法选项。', code='invalid_choice')]}"。

### 13. `POST /api/student/profile/update`

重新生成当前学生课程画像。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/profile/update`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `441` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='课程不存在'。

### 14. `GET /api/student/profile/history`

获取学生画像历史。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/profile/history`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `491` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 15. `GET /api/student/profile/compare`

按日期对比学生画像快照。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/profile/compare`，路径参数 `{}`，查询参数 `{"date1": "2026-05-28", "date2": "2026-05-28"}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `326` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 16. `POST /api/student/profile/export`

导出学生画像 JSON 文件。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/profile/export`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `547` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['user', 'real_name', 'knowledge_mastery', 'ability_scores', 'habit_preferences'], code=None, msg=None。

### 17. `GET /api/admin/activation-codes`

管理员分页查询激活码。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/activation-codes`，路径参数 `{}`，查询参数 `{"page": 1, "page_size": 20}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `383` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 18. `POST /api/admin/activation-codes/generate`

批量生成激活码。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/activation-codes/generate`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `201`，OpenAPI 声明状态码为 `201, 400`，耗时 `340` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=201, msg='成功生成 1 个激活码'。

### 19. `POST /api/admin/activation-codes/batch-delete`

批量删除未使用激活码。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/activation-codes/batch-delete`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `352` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已删除 0 个激活码'。

### 20. `POST /api/admin/activation-codes/validate`

校验激活码可用性。本次以 `anonymous` 角色请求 `http://127.0.0.1:8000/api/admin/activation-codes/validate`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `506` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 21. `GET /api/admin/activation-codes/export`

导出激活码 CSV。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/activation-codes/export`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `427` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：﻿﻿ID,激活码,类型,已使用,使用者,使用时间,过期时间,备注,创建时间 ﻿93,9F91C0F4,teacher,否,,,永不过期,,2026-05-28 18:00:04 ﻿92,AUD91192,teacher,否,,,永不过期,OpenAPI endpoint audit,2026-05-28 17:59。

### 22. `GET /api/admin/activation-codes/{code_id}`

获取单个激活码详情。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/activation-codes/92`，路径参数 `{"code_id": 92}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `485` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 23. `DELETE /api/admin/activation-codes/{code_id}`

删除未使用激活码。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/activation-codes/99999999`，路径参数 `{"code_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `516` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='激活码不存在'。

### 24. `GET /api/admin/users`

管理员分页查询用户。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users`，路径参数 `{}`，查询参数 `{"page": 1, "size": 20, "query": "Hadoop"}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `448` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 25. `POST /api/admin/users/create`

管理员创建用户。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/create`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `201`，OpenAPI 声明状态码为 `201, 400`，耗时 `755` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=201, msg='用户创建成功'。

### 26. `POST /api/admin/users/batch-delete`

批量删除用户。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/batch-delete`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `506` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已删除 0 个用户'。

### 27. `POST /api/admin/users/import`

导入用户 CSV 或 Excel。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/import`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `multipart/form-data`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `438` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='仅支持 .csv / .xlsx 文件'。

### 28. `GET /api/admin/users/export`

导出用户 CSV。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/export`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `501` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：﻿﻿ID,用户名,姓名,学号/工号,角色,邮箱,手机,状态,注册时间 ﻿334,api_audit_student_1779981386,,,student,api-audit-1779981386@edu.qintsg.xyz,,正常,2026-05-28 15:16:29 ﻿330,student4,学生4,2。

### 29. `GET /api/admin/users/template`

下载用户导入模板 CSV。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/template`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `193` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：﻿﻿username,password,role,email,real_name,student_id ﻿zhangsan,Edu@12345,student,zhangsan@example.com,张三,2024001 ﻿teacher1,Edu@12345,teacher,teacher1@example.c。

### 30. `GET /api/admin/users/{user_id}`

获取用户详情。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/327`，路径参数 `{"user_id": 327}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `506` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 31. `PUT /api/admin/users/{user_id}/update`

管理员更新用户资料。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/327/update`，路径参数 `{"user_id": 327}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `423` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='用户信息已更新'。

### 32. `DELETE /api/admin/users/{user_id}/delete`

删除用户。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/99999999/delete`，路径参数 `{"user_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `336` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='用户不存在'。

### 33. `POST /api/admin/users/{user_id}/reset-password`

重置用户密码。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/327/reset-password`，路径参数 `{"user_id": 327}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `947` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='密码已重置'。

### 34. `POST /api/admin/users/{user_id}/disable`

禁用用户。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/327/disable`，路径参数 `{"user_id": 327}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `443` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='用户 student1 已禁用'。

### 35. `POST /api/admin/users/{user_id}/enable`

启用用户。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/users/327/enable`，路径参数 `{"user_id": 327}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `501` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='用户 student1 已启用'。

### 36. `GET /api/admin/student-profiles`

管理员分页查看学生画像摘要。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/student-profiles`，路径参数 `{}`，查询参数 `{"course_id": 146, "page": 1, "page_size": 20}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `475` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 37. `GET /api/admin/student-profiles/{student_id}`

管理员查看学生画像详情。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/student-profiles/327`，路径参数 `{"student_id": 327}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `505` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 38. `GET /api/teacher/students/{user_id}/profile`

教师查看学生画像详情。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/students/327/profile`，路径参数 `{"user_id": 327}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `534` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 39. `POST /api/teacher/students/{user_id}/refresh-profile`

教师刷新指定学生课程画像。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/students/327/refresh-profile`，路径参数 `{"user_id": 327}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400, 403`，耗时 `327` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='课程不存在'。

### 40. `GET /api/courses`

获取当前用户可访问课程。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/courses`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `638` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 41. `POST /api/courses/select`

选择当前课程上下文。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/courses/select`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400, 403`，耗时 `544` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='课程切换成功'。

### 42. `GET /api/courses/search`

搜索课程。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/courses/search`，路径参数 `{}`，查询参数 `{"keyword": "Hadoop", "q": "Hadoop", "page": 1, "page_size": 20}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `529` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 43. `GET /api/student/classes`

获取学生加入的班级。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/classes`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `507` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 44. `GET /api/student/classes/{class_id}`

获取学生班级详情。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/classes/99`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403, 404`，耗时 `526` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 45. `POST /api/student/classes/join`

使用邀请码加入班级。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/classes/join`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `294` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='请提供邀请码'。

### 46. `DELETE /api/student/classes/{class_id}/leave`

退出班级。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/classes/99999999/leave`，路径参数 `{"class_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `528` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='您未加入此班级'。

### 47. `POST /api/teacher/courses/create`

教师创建课程。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/courses/create`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `201`，OpenAPI 声明状态码为 `201, 400`，耗时 `470` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=201, msg='课程创建成功'。

### 48. `GET /api/teacher/courses/my`

获取教师创建的课程。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/courses/my`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `532` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 49. `GET /api/teacher/courses/{course_id}`

获取教师课程详情。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/courses/146`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `476` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 50. `PUT /api/teacher/courses/{course_id}`

更新教师课程。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/courses/146`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `562` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='课程更新成功'。

### 51. `GET /api/teacher/courses/{course_id}/workspace`

获取教师课程工作台聚合数据。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/courses/146/workspace`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `508` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 52. `DELETE /api/teacher/courses/{course_id}/delete`

删除教师课程。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/courses/99999999/delete`，路径参数 `{"course_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `572` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='课程不存在'。

### 53. `POST /api/teacher/courses/{course_id}/cover/upload`

上传课程封面。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/courses/146/cover/upload`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `multipart/form-data`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `450` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='封面上传成功'。

### 54. `GET /api/teacher/courses/{course_id}/statistics`

获取教师课程统计。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/courses/146/statistics`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `566` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 55. `GET /api/teacher/courses/{course_id}/settings`

获取课程设置。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/courses/146/settings`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `326` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 56. `PUT /api/teacher/courses/{course_id}/settings/update`

更新课程设置。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/courses/146/settings/update`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `531` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='课程配置已更新'。

### 57. `POST /api/teacher/classes/create`

教师创建班级。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/create`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `201`，OpenAPI 声明状态码为 `201, 400`，耗时 `450` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=201, msg='班级创建成功'。

### 58. `GET /api/teacher/classes/my`

获取教师班级列表。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/my`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `415` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 59. `GET /api/teacher/classes/{class_id}`

获取教师班级详情。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `528` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 60. `PUT /api/teacher/classes/{class_id}`

更新教师班级。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `491` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='班级更新成功'。

### 61. `DELETE /api/teacher/classes/{class_id}/delete`

删除教师班级。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99999999/delete`，路径参数 `{"class_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `551` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='班级不存在'。

### 62. `GET /api/teacher/classes/{class_id}/progress`

获取班级学习进度。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99/progress`，路径参数 `{"class_id": 99}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400, 403`，耗时 `428` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 63. `GET /api/teacher/classes/{class_id}/courses`

获取班级已发布课程。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99/courses`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `522` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 64. `POST /api/teacher/classes/{class_id}/publish-course`

向班级发布课程。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99/publish-course`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `527` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='课程发布成功'。

### 65. `DELETE /api/teacher/classes/{class_id}/courses/{course_id}`

从班级取消发布课程。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99999999/courses/99999999`，路径参数 `{"class_id": 99999999, "course_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `439` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='班级不存在'。

### 66. `GET /api/teacher/classes/{class_id}/invitations`

获取班级邀请码列表。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99/invitations`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `666` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 67. `POST /api/teacher/invitations/generate`

生成班级邀请码。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/invitations/generate`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `201`，OpenAPI 声明状态码为 `201, 403`，耗时 `545` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=201, msg='邀请码生成成功'。

### 68. `DELETE /api/teacher/invitations/{invitation_id}`

删除班级邀请码。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/invitations/99999999`，路径参数 `{"invitation_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `513` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='邀请码不存在'。

### 69. `GET /api/teacher/classes/{class_id}/students`

获取班级学生列表。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99/students`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `526` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 70. `DELETE /api/teacher/classes/{class_id}/students/{user_id}`

从班级移除学生。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99999999/students/99999999`，路径参数 `{"class_id": 99999999, "user_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `454` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='班级不存在'。

### 71. `GET /api/teacher/classes/{class_id}/student-profiles`

获取班级学生画像摘要。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99/student-profiles`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `516` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 72. `GET /api/teacher/classes/{class_id}/announcements`

获取班级公告。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99/announcements`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `518` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 73. `POST /api/teacher/classes/{class_id}/announcements`

发布班级公告。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/classes/99/announcements`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `201`，OpenAPI 声明状态码为 `201, 403`，耗时 `526` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=201, msg='公告发布成功'。

### 74. `PUT /api/teacher/announcements/{announcement_id}`

更新班级公告。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/announcements/16`，路径参数 `{"announcement_id": 16}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `322` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='公告已更新'。

### 75. `DELETE /api/teacher/announcements/{announcement_id}`

删除班级公告。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/announcements/99999999`，路径参数 `{"announcement_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `498` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='公告不存在'。

### 76. `GET /api/admin/courses`

管理员查询课程列表。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/courses`，路径参数 `{}`，查询参数 `{"page": 1, "page_size": 20, "query": "Hadoop"}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `630` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 77. `POST /api/admin/courses/create`

管理员创建课程。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/courses/create`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `201`，OpenAPI 声明状态码为 `201`，耗时 `524` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=201, msg='课程创建成功'。

### 78. `GET /api/admin/courses/{course_id}`

管理员获取课程详情。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/courses/146`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `532` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 79. `PUT /api/admin/courses/{course_id}`

管理员更新课程。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/courses/146`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `466` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='课程更新成功'。

### 80. `DELETE /api/admin/courses/{course_id}`

管理员删除课程。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/courses/99999999`，路径参数 `{"course_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `552` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='课程不存在'。

### 81. `POST /api/admin/courses/{course_id}/assign-teacher`

为课程分配教师。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/courses/146/assign-teacher`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `446` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='教师分配成功'。

### 82. `GET /api/admin/courses/{course_id}/statistics`

管理员获取课程统计。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/courses/146/statistics`，路径参数 `{"course_id": 146}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `463` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 83. `GET /api/admin/classes`

管理员查询班级列表。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/classes`，路径参数 `{}`，查询参数 `{"page": 1, "page_size": 20, "query": "Hadoop"}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `511` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 84. `POST /api/admin/classes/create`

管理员创建班级。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/classes/create`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `201`，OpenAPI 声明状态码为 `201`，耗时 `560` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=201, msg='班级创建成功'。

### 85. `GET /api/admin/classes/{class_id}`

管理员获取班级详情。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/classes/99`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `462` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 86. `PUT /api/admin/classes/{class_id}`

管理员更新班级。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/classes/99`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `552` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='班级更新成功'。

### 87. `DELETE /api/admin/classes/{class_id}`

管理员删除班级。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/classes/99999999`，路径参数 `{"class_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `493` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='班级不存在'。

### 88. `GET /api/admin/classes/{class_id}/students`

管理员查看班级学生。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/classes/99/students`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `580` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 89. `POST /api/admin/classes/{class_id}/students/add`

管理员向班级添加学生。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/classes/99/students/add`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `556` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='成功添加 0 名学生'。

### 90. `DELETE /api/admin/classes/{class_id}/students/{student_id}`

管理员从班级移除学生。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/classes/99999999/students/99999999`，路径参数 `{"class_id": 99999999, "student_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `540` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='该学生不在班级中'。

### 91. `POST /api/admin/classes/{class_id}/assign-teacher`

为班级分配教师。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/classes/99/assign-teacher`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `217` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已将 teacher1 分配为班级 OpenAPI 巡检名称 的教师'。

### 92. `GET /api/admin/classes/{class_id}/statistics`

管理员获取班级统计。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/classes/99/statistics`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `430` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 93. `GET /api/admin/statistics/overview`

管理员仪表盘总览统计。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/statistics/overview`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `532` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 94. `GET /api/admin/statistics/users`

用户统计。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/statistics/users`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `515` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 95. `GET /api/admin/statistics/courses`

课程统计。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/statistics/courses`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `539` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 96. `GET /api/admin/statistics/learning`

学习统计。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/statistics/learning`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `532` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 97. `GET /api/admin/statistics/exams`

作业考试统计。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/statistics/exams`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `214` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 98. `GET /api/admin/statistics/active-users`

活跃用户统计。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/statistics/active-users`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `489` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 99. `GET /api/admin/statistics/report`

管理端统计报告。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/statistics/report`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `317` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 100. `GET /api/admin/statistics/export`

导出管理端统计。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/statistics/export`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `539` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：﻿﻿指标,数值 ﻿总用户数,26 ﻿学生数,23 ﻿教师数,2 ﻿课程数,21 ﻿班级数,20 ﻿选课人次,9 。

### 101. `GET /api/student/knowledge-map`

获取学生课程知识图谱。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/knowledge-map`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `2396` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 102. `GET /api/student/knowledge-points/{point_id}`

获取学生知识点详情。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/knowledge-points/3026`，路径参数 `{"point_id": 3026}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `534` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 103. `GET /api/student/knowledge-points/{point_id}/resources`

获取知识点关联学习资源。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/knowledge-points/3026/resources`，路径参数 `{"point_id": 3026}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `489` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 104. `GET /api/student/knowledge/points`

获取学生课程知识点列表。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/knowledge/points`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `536` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 105. `GET /api/student/knowledge/relations`

获取学生课程知识点关系。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/knowledge/relations`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `533` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 106. `GET /api/student/knowledge/mastery`

获取学生知识点掌握度。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/knowledge/mastery`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `522` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 107. `PUT /api/student/knowledge/mastery/update`

更新学生知识点掌握度。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/knowledge/mastery/update`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `338` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 108. `GET /api/student/knowledge/search`

搜索学生可见知识点。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/knowledge/search`，路径参数 `{}`，查询参数 `{"keyword": "Hadoop", "course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `529` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 109. `GET /api/student/resources`

获取学生课程资源。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/resources`，路径参数 `{}`，查询参数 `{"course_id": 146, "keyword": "Hadoop", "page": 1, "page_size": 20}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `494` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 110. `GET /api/teacher/resources`

教师查询课程资源。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/resources`，路径参数 `{}`，查询参数 `{"course_id": 146, "keyword": "Hadoop", "page": 1, "page_size": 20}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `568` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 111. `POST /api/teacher/resources/create`

教师创建课程资源。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/resources/create`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `multipart/form-data`；实际返回 `201`，OpenAPI 声明状态码为 `201, 400`，耗时 `324` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=201, msg='资源创建成功'。

### 112. `POST /api/teacher/resources/upload`

上传课程资源文件。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/resources/upload`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `multipart/form-data`；实际返回 `200`，OpenAPI 声明状态码为 `200, 201`，耗时 `353` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='资源上传成功'。

### 113. `GET /api/teacher/resources/{resource_id}`

获取教师资源详情。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/resources/2115`，路径参数 `{"resource_id": 2115}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `174` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 114. `PUT /api/teacher/resources/{resource_id}`

更新教师资源。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/resources/2115`，路径参数 `{"resource_id": 2115}`，查询参数 `{}`，请求体类型为 `multipart/form-data`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `351` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='资源更新成功'。

### 115. `DELETE /api/teacher/resources/{resource_id}/delete`

删除教师资源。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/resources/99999999/delete`，路径参数 `{"resource_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `348` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='资源不存在'。

### 116. `POST /api/teacher/resources/{resource_id}/link-knowledge`

关联资源到知识点。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/resources/2115/link-knowledge`，路径参数 `{"resource_id": 2115}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `257` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已关联 1 个知识点'。

### 117. `GET /api/teacher/questions`

教师查询题库。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions`，路径参数 `{}`，查询参数 `{"course_id": 146, "keyword": "Hadoop", "page": 1, "page_size": 20}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `402` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 118. `POST /api/teacher/questions/create`

教师创建题目。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions/create`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 201`，耗时 `286` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='题目创建成功'。

### 119. `POST /api/teacher/questions/batch-delete`

批量删除题目。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions/batch-delete`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `412` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已删除 0 道题目'。

### 120. `POST /api/teacher/questions/import`

导入题库文件。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions/import`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `multipart/form-data`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `388` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='仅支持 .json / .xlsx 文件'。

### 121. `GET /api/teacher/questions/export`

导出题库 CSV。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions/export`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `252` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：﻿﻿ID,题型,题目内容,选项A,选项B,选项C,选项D,正确答案,解析,难度 ﻿7223,single_choice,OpenAPI巡检题目,"{'label': 'A', 'content': 'A'}","{'label': 'B', 'content': 'B'}",,,A,audit,easy ﻿7373。

### 122. `GET /api/teacher/questions/template`

下载题库导入模板。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions/template`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `309` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：﻿﻿question_type,content,option_a,option_b,option_c,option_d,correct_answer,analysis,difficulty,knowledge_point_name ﻿single_choice,以下哪个不是Python基本数据类型？,整数,字符串,数。

### 123. `GET /api/teacher/questions/{question_id}`

获取题目详情。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions/7223`，路径参数 `{"question_id": 7223}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `394` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 124. `PUT /api/teacher/questions/{question_id}`

更新题目。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions/7223`，路径参数 `{"question_id": 7223}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `194` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='题目更新成功'。

### 125. `PUT /api/teacher/questions/{question_id}/update`

更新题目兼容路径。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions/7223/update`，路径参数 `{"question_id": 7223}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `566` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='题目更新成功'。

### 126. `DELETE /api/teacher/questions/{question_id}/delete`

删除题目。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions/99999999/delete`，路径参数 `{"question_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `552` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='题目不存在'。

### 127. `POST /api/teacher/questions/{question_id}/link-knowledge`

关联题目到知识点。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/questions/7223/link-knowledge`，路径参数 `{"question_id": 7223}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `235` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已关联 1 个知识点'。

### 128. `GET /api/teacher/knowledge-relations`

教师查询知识关系。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-relations`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `561` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 129. `POST /api/teacher/knowledge-relations/create`

创建知识点关系。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-relations/create`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `201, 400`，耗时 `534` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='缺少 from_point_id 或 to_point_id'。

### 130. `DELETE /api/teacher/knowledge-relations/{relation_id}`

删除知识点关系。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-relations/99999999`，路径参数 `{"relation_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `523` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='关系不存在'。

### 131. `GET /api/teacher/knowledge-points`

教师查询知识点。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-points`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `530` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 132. `POST /api/teacher/knowledge-points/create`

创建知识点。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-points/create`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `201, 400`，耗时 `324` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='缺少必要参数'。

### 133. `GET /api/teacher/knowledge-points/{point_id}`

获取教师知识点详情。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-points/3026`，路径参数 `{"point_id": 3026}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `548` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 134. `PUT /api/teacher/knowledge-points/{point_id}`

更新知识点。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-points/3026`，路径参数 `{"point_id": 3026}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `435` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='知识点更新成功'。

### 135. `DELETE /api/teacher/knowledge-points/{point_id}/delete`

删除知识点。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-points/99999999/delete`，路径参数 `{"point_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `349` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='知识点不存在'。

### 136. `POST /api/teacher/knowledge-map/import`

导入知识图谱。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-map/import`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `multipart/form-data`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `488` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='仅支持JSON或Excel格式文件'。

### 137. `POST /api/teacher/knowledge-map/save`

保存课程知识图谱草稿。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-map/save`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `530` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='节点数据为空'。

### 138. `POST /api/teacher/knowledge-map/publish`

发布课程知识图谱。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-map/publish`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `287` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 139. `POST /api/teacher/knowledge-map/build-rag-index`

构建课程 GraphRAG 索引。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-map/build-rag-index`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `532` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='课程 GraphRAG 索引构建完成'。

### 140. `GET /api/teacher/knowledge-map/export`

导出课程知识图谱 JSON。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-map/export`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `520` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['course_id', 'knowledge_points', 'relations'], code=None, msg=None。

### 141. `GET /api/teacher/knowledge-map/template`

下载知识图谱导入模板。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/knowledge-map/template`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `516` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['knowledge_points', 'relations'], code=None, msg=None。

### 142. `GET /api/student/assessments/status`

查询当前用户初始测评完成状态。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/status`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `410` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 143. `GET /api/student/assessments/initial/knowledge`

获取课程知识测评题目。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/initial/knowledge`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `524` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 144. `POST /api/student/assessments/initial/knowledge/submit`

提交课程知识测评。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/initial/knowledge/submit`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `546` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='缺少必要参数'。

### 145. `GET /api/student/assessments/initial/knowledge/result`

获取课程知识测评结果和异步生成状态。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/initial/knowledge/result`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `535` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='尚未完成知识测评'。

### 146. `GET /api/student/assessments/initial/ability`

获取学习能力评测题目。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/initial/ability`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `533` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 147. `GET /api/student/assessments/initial/ability/retake`

重新获取学习能力评测题目。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/initial/ability/retake`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `372` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 148. `POST /api/student/assessments/initial/ability/submit`

提交学习能力评测。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/initial/ability/submit`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `271` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='缺少答案数据'。

### 149. `GET /api/student/assessments/initial/habit`

获取学习习惯问卷。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/initial/habit`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `434` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 150. `POST /api/student/assessments/initial/habit/submit`

提交学习习惯问卷。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/initial/habit/submit`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `502` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='缺少问卷回答'。

### 151. `POST /api/student/assessments/profile/generate`

根据测评结果生成课程画像。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/profile/generate`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `404`，OpenAPI 声明状态码为 `200, 400, 404, 500`，耗时 `515` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='课程不存在'。

### 152. `GET /api/student/learning-path`

获取个性化学习路径。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/learning-path`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `554` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='请先完成初始评测'。

### 153. `POST /api/student/learning-path/adjust`

刷新或调整学习路径。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/learning-path/adjust`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `557` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='路径已更新'。

### 154. `GET /api/student/learning-progress`

获取学习路径进度。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/learning-progress`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `568` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 155. `GET /api/student/path-nodes/{node_id}`

获取学习路径节点详情。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163`，路径参数 `{"node_id": 1163}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `339` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 156. `POST /api/student/path-nodes/{node_id}/start`

开始学习节点。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/start`，路径参数 `{"node_id": 1163}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404, 409`，耗时 `542` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='开始学习'。

### 157. `POST /api/student/path-nodes/{node_id}/complete`

标记学习节点完成。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/complete`，路径参数 `{"node_id": 1163}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404, 409`，耗时 `574` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='节点已完成'。

### 158. `POST /api/student/path-nodes/{node_id}/skip`

跳过学习节点。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/skip`，路径参数 `{"node_id": 1163}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `545` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='节点已跳过'。

### 159. `GET /api/student/path-nodes/{node_id}/resources`

获取节点资源列表兼容接口。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/resources`，路径参数 `{"node_id": 1163}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `627` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 160. `GET /api/student/path-nodes/{node_id}/ai-resources`

获取节点 AI 推荐资源。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/ai-resources`，路径参数 `{"node_id": 1163}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `452` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 161. `POST /api/student/path-nodes/{node_id}/resources/{resource_id}/complete`

标记节点资源学习完成。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/resources/2115/complete`，路径参数 `{"node_id": 1163, "resource_id": 2115}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `530` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='资源已标记为已学习'。

### 162. `POST /api/student/path-nodes/{node_id}/resources/{resource_id}/pause`

暂停资源学习并保存位置。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/resources/2115/pause`，路径参数 `{"node_id": 1163, "resource_id": 2115}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `535` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已暂停'。

### 163. `GET /api/student/path-nodes/{node_id}/exams`

获取节点测验列表。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/exams`，路径参数 `{"node_id": 1163}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `497` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 164. `POST /api/student/path-nodes/{node_id}/exams/{exam_id}/submit`

提交节点练习或小测验。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/exams/599/submit`，路径参数 `{"node_id": 1163, "exam_id": 599}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `477` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='测验不属于该节点'。

### 165. `GET /api/student/path-nodes/{node_id}/stage-test`

获取阶段测试题目。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/stage-test`，路径参数 `{"node_id": 1163}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `540` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='该节点不是测试节点'。

### 166. `POST /api/student/path-nodes/{node_id}/stage-test/submit`

提交阶段测试答案。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/path-nodes/1163/stage-test/submit`，路径参数 `{"node_id": 1163}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `548` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='该节点不是测试节点'。

### 167. `GET /api/student/dashboard`

获取学生仪表盘聚合数据。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/dashboard`，路径参数 `{}`，查询参数 `{"course_id": 146}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `541` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 168. `GET /api/student/exams`

获取学生可见作业列表。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/exams`，路径参数 `{}`，查询参数 `{"course_id": 146, "page": 1, "size": 20}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `529` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 169. `GET /api/student/exams/{exam_id}`

获取作业详情和题目。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/exams/599`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 403, 404`，耗时 `292` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='作业不存在'。

### 170. `POST /api/student/exams/{exam_id}/submit`

提交作业答案。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/exams/599/submit`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `554` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='答案不能为空'。

### 171. `GET /api/student/exams/{exam_id}/result`

获取作业结果。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/exams/599/result`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `524` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='您尚未完成该作业'。

### 172. `POST /api/student/exams/{exam_id}/draft`

保存作业草稿。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/exams/599/draft`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `339` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='草稿已保存'。

### 173. `GET /api/student/exams/{exam_id}/statistics`

获取学生视角作业统计。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/exams/599/statistics`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `352` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 174. `GET /api/student/exams/{exam_id}/answer-sheet`

查看作业标准答案。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/exams/599/answer-sheet`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `538` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='请先完成作业再查看答案'。

### 175. `POST /api/student/exams/{exam_id}/retake`

重置作业提交以重新作答。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/exams/599/retake`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `541` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已重置，可以重新作答'。

### 176. `GET /api/student/exams/{exam_id}/download`

下载作业答案报告 CSV。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/exams/599/download`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `544` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='您尚未完成此作业'。

### 177. `GET /api/student/classes/{class_id}/members`

获取班级成员列表。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/classes/99/members`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `535` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 178. `GET /api/student/classes/{class_id}/ranking`

获取班级学习排行榜。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/classes/99/ranking`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `550` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 179. `GET /api/student/classes/{class_id}/notifications`

获取班级通知公告简表。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/classes/99/notifications`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `554` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 180. `GET /api/student/classes/{class_id}/assignments`

获取班级作业列表。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/classes/99/assignments`，路径参数 `{"class_id": 99}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `560` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 181. `POST /api/student/feedback/generate`

生成或重新排队 AI 反馈报告。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/feedback/generate`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `509` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='您尚未完成该作业'。

### 182. `GET /api/student/feedback/{exam_id}`

获取作业反馈报告。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/feedback/599`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `543` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='报告不存在'。

### 183. `POST /api/student/assessments/initial/start`

开始旧版课程初始评测随机抽题。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/initial/start`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `592` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='课程不存在'。

### 184. `POST /api/student/assessments/initial/submit`

提交旧版课程初始评测。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/assessments/initial/submit`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `529` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='缺少必填参数'。

### 185. `GET /api/teacher/exams`

教师获取课程作业列表。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams`，路径参数 `{}`，查询参数 `{"course_id": 146, "page": 1, "page_size": 20}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `305` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 186. `POST /api/teacher/exams/create`

教师创建作业。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/create`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `543` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='作业创建成功'。

### 187. `GET /api/teacher/exams/{exam_id}`

教师获取作业详情。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/599`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `643` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 188. `PUT /api/teacher/exams/{exam_id}/update`

教师更新作业。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/599/update`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `555` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='及格分不能大于总分'。

### 189. `DELETE /api/teacher/exams/{exam_id}/delete`

教师删除作业。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/99999999/delete`，路径参数 `{"exam_id": 99999999}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `511` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='作业不存在'。

### 190. `POST /api/teacher/exams/{exam_id}/publish`

发布作业。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/599/publish`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `544` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='作业已发布'。

### 191. `POST /api/teacher/exams/{exam_id}/unpublish`

取消发布作业。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/599/unpublish`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `495` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='作业已取消发布'。

### 192. `GET /api/teacher/exams/{exam_id}/results`

获取作业成绩列表。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/599/results`，路径参数 `{"exam_id": 599}`，查询参数 `{"page": 1, "size": 20}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `521` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 193. `GET /api/teacher/exams/{exam_id}/export`

导出作业成绩 CSV。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/599/export`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `408` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：﻿﻿学生ID,用户名,姓名,成绩,提交时间 。

### 194. `POST /api/teacher/exams/{exam_id}/questions/add`

向作业追加题目。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/599/questions/add`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `565` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已添加 0 道题目'。

### 195. `POST /api/teacher/exams/{exam_id}/questions/remove`

从作业移除题目。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/599/questions/remove`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `475` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已移除 0 道题目'。

### 196. `GET /api/teacher/exams/{exam_id}/students/{student_id}`

获取某学生作业详情。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/599/students/327`，路径参数 `{"exam_id": 599, "student_id": 327}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `404`，OpenAPI 声明状态码为 `200, 404`，耗时 `534` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=404, msg='学生未提交作业'。

### 197. `GET /api/teacher/exams/{exam_id}/analysis`

获取作业统计分析。本次以 `teacher` 角色请求 `http://127.0.0.1:8000/api/teacher/exams/599/analysis`，路径参数 `{"exam_id": 599}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `465` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 198. `POST /api/student/ai/profile-analysis`

生成或刷新课程学习者画像分析。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/profile-analysis`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400, 500`，耗时 `541` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='请先完成测评后再获取AI分析'。

### 199. `POST /api/student/ai/path-planning`

基于掌握度与 RAG 证据生成路径规划建议。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/path-planning`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `14459` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='路径规划完成'。

### 200. `POST /api/student/ai/resource-reason`

生成推荐资源理由。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/resource-reason`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `521` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='缺少 resource_id 参数'。

### 201. `POST /api/student/ai/feedback-report`

获取或生成作业 AI 反馈摘要。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/feedback-report`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `547` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='缺少 exam_id 参数'。

### 202. `POST /api/student/ai/learning-advice`

生成当前课程学习建议。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/learning-advice`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `9901` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 203. `POST /api/student/ai/refresh-profile`

强制刷新课程画像。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/refresh-profile`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `8726` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 204. `POST /api/student/ai/refresh-learning-path`

重建当前学生课程学习路径。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/refresh-learning-path`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `424` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 205. `POST /api/student/ai/key-points-reminder`

获取薄弱知识点复习提醒。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/key-points-reminder`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `415` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 206. `POST /api/student/ai/time-scheduling`

根据薄弱点分配可用学习时间。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/time-scheduling`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `514` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 207. `GET /api/student/ai/analysis-compare`

对比两个日期前的画像快照。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/analysis-compare`，路径参数 `{}`，查询参数 `{"date1": "2026-05-28", "date2": "2026-05-28"}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `554` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 208. `POST /api/student/ai/chat`

学生 AI 问答。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/chat`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 400`，耗时 `7580` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 209. `POST /api/student/ai/node-intro`

生成知识点介绍。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/node-intro`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400, 404`，耗时 `314` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='缺少知识点名称或 point_id'。

### 210. `POST /api/student/ai/knowledge-query`

图谱问答兼容路径。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/knowledge-query`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `322` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='请输入问题'。

### 211. `POST /api/student/ai/graph-rag/search`

在课程图谱中检索知识点。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/graph-rag/search`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `519` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='请输入检索内容'。

### 212. `POST /api/student/ai/graph-rag/ask`

基于课程图谱回答问题。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/student/ai/graph-rag/ask`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `438` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='请输入问题'。

### 213. `POST /api/ai/kt/predict`

单学生知识追踪预测。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/ai/kt/predict`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 500`，耗时 `538` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 214. `GET /api/ai/kt/model-info`

获取当前 KT 模型信息。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/ai/kt/model-info`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `439` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 215. `POST /api/ai/kt/batch-predict`

教师批量知识追踪预测。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/ai/kt/batch-predict`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `403`，OpenAPI 声明状态码为 `200, 403`，耗时 `536` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=403, msg='您没有执行该操作的权限。'。

### 216. `POST /api/ai/kt/recommendations`

根据 KT 预测生成学习建议。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/ai/kt/recommendations`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `400`，OpenAPI 声明状态码为 `200, 400`，耗时 `550` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data', 'error'], code=400, msg='缺少 course_id 或 predictions'。

### 217. `GET /api/admin/logs`

管理员查询操作日志。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/logs`，路径参数 `{}`，查询参数 `{"page": 1, "page_size": 20, "keyword": "Hadoop"}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `351` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 218. `GET /api/admin/logs/{log_id}`

获取操作日志详情。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/logs/1780`，路径参数 `{"log_id": 1780}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 404`，耗时 `426` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 219. `GET /api/admin/logs/statistics`

获取日志统计。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/logs/statistics`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `306` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 220. `GET /api/admin/logs/options`

获取日志筛选选项。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/logs/options`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `310` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 221. `GET /api/admin/logs/modules`

获取日志模块列表。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/logs/modules`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `491` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 222. `GET /api/admin/logs/actions`

获取日志操作类型列表。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/logs/actions`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `522` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。

### 223. `GET /api/admin/logs/export`

导出操作日志 CSV。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/logs/export`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200`，耗时 `610` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：﻿﻿ID,用户,操作,模块,路径,描述,成功,错误信息,时间 ﻿1900,student1,创建 Create,AI服务模块 AI Services,/api/ai/kt/recommendations,AI服务 - 创建操作,否,,2026-05-28 18:02:20 ﻿1899,student1,创建 Cre。

### 224. `DELETE /api/admin/logs/clean`

清理过期日志。本次以 `admin` 角色请求 `http://127.0.0.1:8000/api/admin/logs/clean`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `JSON`；实际返回 `200`，OpenAPI 声明状态码为 `200, 403`，耗时 `325` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='已清理 0 条过期日志'。

### 225. `GET /api/common/menu`

获取当前用户菜单树。本次以 `student` 角色请求 `http://127.0.0.1:8000/api/common/menu`，路径参数 `{}`，查询参数 `{}`，请求体类型为 `无请求体`；实际返回 `200`，OpenAPI 声明状态码为 `200, 401`，耗时 `485` ms。结论：**已文档化**，说明：实际状态码已在 OpenAPI responses 中声明。响应摘要：JSON object keys=['code', 'msg', 'data'], code=200, msg='OK'。
