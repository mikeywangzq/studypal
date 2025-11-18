# Bug 报告和修复记录

## 🐛 已发现的Bug

### Bug #1: collaboration.py 中 JSON 解析缺少异常处理

**文件**: `backend/app/api/collaboration.py`
**位置**: 第 284 行和第 295-305 行
**严重性**: 🟡 中等

**问题描述**:
在获取评论列表时，解析 `mentions` 字段的 JSON 没有异常处理。如果数据库中的 JSON 数据损坏，会导致 API 崩溃。

```python
# 第284行 - 无异常处理
mentions=json.loads(comment.mentions) if comment.mentions else [],

# 第295-305行 - 构建回复时也有相同问题
comment_data.replies.append(CommentWithUser(
    ...
    mentions=json.loads(reply.mentions) if reply.mentions else [],
    ...
))
```

**影响**:
- 如果数据库中的 mentions 字段数据损坏，整个 API 请求会失败
- 用户无法查看评论列表
- 500 Internal Server Error

**修复方案**:
添加 try-except 异常处理，失败时使用空数组作为默认值。

---

### Bug #2: WebSocket 断开时可能抛出异常

**文件**: `backend/app/services/websocket_manager.py`
**位置**: broadcast_to_note 方法
**严重性**: 🟢 低

**问题描述**:
在广播消息时，如果连接已断开但还没有被清理，`send_json` 可能抛出异常。

**当前实现**:
```python
try:
    await connection.send_json(message)
except Exception as e:
    logger.warning(f"发送消息失败，连接可能已断开: user_id={user_id}, error={e}")
    disconnected_users.append(user_id)
```

**状态**: ✅ 已修复（已有异常处理）

---

### Bug #3: notification_service 中重复通知问题

**文件**: `backend/app/services/notification_service.py`
**位置**: notify_* 辅助方法
**严重性**: 🟡 中等

**问题描述**:
没有检查是否已经存在相同的未读通知，可能导致重复通知。

**场景**:
1. 用户A评论笔记B的笔记
2. 通知发送给用户B
3. 用户A短时间内又评论
4. 再次发送通知给用户B
5. 结果：用户B收到多条相同笔记的评论通知

**建议**:
添加通知去重逻辑，或者合并相似通知。

---

### Bug #4: 版本历史可能无限增长

**文件**: `backend/app/services/version_service.py`
**位置**: create_version 方法
**严重性**: 🟡 中等

**问题描述**:
没有限制版本数量，长期使用可能导致：
- 数据库空间占用过大
- 查询性能下降

**当前状态**:
- 提供了 `delete_old_versions` 方法
- 但没有自动调用

**建议**:
- 在创建新版本时自动清理旧版本
- 或设置定时任务清理

---

### Bug #5: mentions 字段验证缺失

**文件**: `backend/app/services/comment_service.py`
**位置**: create_comment 方法
**严重性**: 🟢 低

**问题描述**:
没有验证 mentions 中的用户ID是否真实存在。

**场景**:
- 前端发送不存在的用户ID
- 创建通知时可能失败
- 但不会报错，只是通知无法送达

**建议**:
添加用户ID验证，过滤掉不存在的用户。

---

### Bug #6: 并发创建版本可能导致版本号重复

**文件**: `backend/app/services/version_service.py`
**位置**: create_version 方法第71-77行
**严重性**: 🟡 中等

**问题描述**:
在高并发情况下，两个请求可能同时查询到相同的 `latest_version`，导致版本号重复。

```python
# 获取最新版本号
latest_version = db.query(NoteVersion).filter(
    NoteVersion.note_id == note_id
).order_by(NoteVersion.version_number.desc()).first()

# 版本号从1开始递增
version_number = (latest_version.version_number + 1) if latest_version else 1
```

**场景**:
1. 请求A查询最新版本号: 5
2. 请求B查询最新版本号: 5（同时进行）
3. 请求A创建版本6
4. 请求B也创建版本6（冲突）

**修复方案**:
使用数据库锁或唯一约束。

---

### Bug #7: WebSocket token 可能被记录到日志

**文件**: `backend/app/api/collaboration.py`
**位置**: websocket_endpoint 第493-495行
**严重性**: 🔴 高（安全）

**问题描述**:
如果token验证失败，异常信息可能包含token本身被记录到日志中。

```python
except Exception as e:
    logger.error(f"WebSocket认证失败: {e}")  # 可能泄露token
```

**修复方案**:
不要记录详细的异常信息，或者确保不包含敏感数据。

---

## ✅ 已修复的Bug

### ~~Bug #8: WebSocket 缺少认证~~
**状态**: ✅ 已修复（提交 2af2420）
**修复**: 添加了JWT token验证和权限检查

### ~~Bug #9: JSON 解析异常（version_service）~~
**状态**: ✅ 已修复（提交 2af2420）
**修复**: 添加了try-except异常处理

### ~~Bug #10: 数据库事务回滚缺失~~
**状态**: ✅ 已修复（提交 2af2420, b1d2974）
**修复**: 所有数据库操作添加了异常处理和回滚

### ~~Bug #11: JSON 序列化异常（comment_service）~~
**状态**: ✅ 已修复（提交 b1d2974）
**修复**: 添加了异常处理和降级逻辑

---

## 📋 修复优先级

### 🔴 高优先级（立即修复）
1. ✅ WebSocket 认证缺失
2. Bug #7: Token 可能泄露到日志
3. Bug #1: JSON 解析缺少异常处理

### 🟡 中优先级（尽快修复）
4. Bug #3: 重复通知问题
5. Bug #4: 版本历史无限增长
6. Bug #6: 并发版本号重复

### 🟢 低优先级（可以延后）
7. Bug #5: mentions 字段验证
8. 性能优化建议

---

## 🔧 修复计划

### 立即修复
- [x] Bug #8: WebSocket 认证
- [x] Bug #9: JSON 解析异常（version_service）
- [x] Bug #10: 数据库事务回滚
- [x] Bug #11: JSON 序列化异常（comment_service）
- [ ] Bug #7: Token 日志泄露
- [ ] Bug #1: JSON 解析异常（collaboration.py）

### 下个版本修复
- [ ] Bug #3: 通知去重
- [ ] Bug #4: 版本自动清理
- [ ] Bug #6: 版本号并发冲突

### 待评估
- [ ] Bug #5: mentions 验证
- [ ] 性能优化

---

## 🧪 测试建议

### 单元测试
```python
# 测试JSON解析异常
def test_comment_with_corrupted_mentions():
    comment.mentions = "invalid json"
    response = client.get(f"/api/notes/{note_id}/comments")
    assert response.status_code == 200  # 不应崩溃
```

### 并发测试
```python
# 测试并发创建版本
import concurrent.futures

def create_version():
    return client.post(f"/api/notes/{note_id}/versions")

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lambda _: create_version(), range(10)))

# 验证版本号唯一性
versions = [r.json()['version_number'] for r in results]
assert len(versions) == len(set(versions))
```

### 安全测试
```python
# 测试token泄露
# 检查日志文件不包含JWT token
import re
log_content = open('app.log').read()
jwt_pattern = r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
assert not re.search(jwt_pattern, log_content)
```

---

## 📝 代码审查清单

- [ ] 所有数据库操作有异常处理
- [ ] 所有JSON解析有异常处理
- [ ] 敏感信息不记录到日志
- [ ] API端点有权限检查
- [ ] 输入数据有验证
- [ ] 并发场景有考虑
- [ ] 资源清理逻辑完整
- [ ] 错误消息用户友好
