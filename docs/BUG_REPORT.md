# Bug 报告和修复记录

## 🎉 所有已知 Bug 已修复！

本文档记录了 Phase 9 开发过程中发现和修复的所有 bug。

---

## ✅ 已修复的Bug

### ~~Bug #1: collaboration.py 中 JSON 解析缺少异常处理~~

**文件**: `backend/app/api/collaboration.py`
**严重性**: 🟡 中等
**状态**: ✅ 已修复（提交 c4a5bae）

**问题描述**: 在获取评论列表时，解析 `mentions` 字段的 JSON 没有异常处理。

**修复方案**: 添加了 try-except 异常处理，失败时使用空数组作为默认值。

```python
# 修复后：第 276-281 行
try:
    mentions_list = json.loads(comment.mentions) if comment.mentions else []
except json.JSONDecodeError as e:
    logger.error(f"解析评论mentions失败: comment_id={comment.id}, error={e}")
    mentions_list = []
```

---

### ~~Bug #2: WebSocket 断开时可能抛出异常~~

**文件**: `backend/app/services/websocket_manager.py`
**严重性**: 🟢 低
**状态**: ✅ 已修复（已有异常处理）

**问题描述**: 在广播消息时，如果连接已断开但还没有被清理，`send_json` 可能抛出异常。

**修复方案**: 代码已包含完善的异常处理机制。

---

### ~~Bug #3: notification_service 中重复通知问题~~

**文件**: `backend/app/services/notification_service.py`
**严重性**: 🟡 中等
**状态**: ✅ 已修复（提交 当前）

**问题描述**: 没有检查是否已经存在相同的未读通知，可能导致重复通知。

**修复方案**: 在 `create_notification` 方法中添加去重检查。

```python
# 修复后：第 72-84 行
# 去重检查：检查是否已存在相同的未读通知
existing = db.query(Notification).filter(
    Notification.user_id == notification_create.user_id,
    Notification.type == notification_create.type,
    Notification.resource_id == notification_create.resource_id,
    Notification.actor_id == notification_create.actor_id,
    Notification.is_read == False
).first()

if existing:
    logger.info(f"通知已存在，跳过创建")
    return existing
```

---

### ~~Bug #4: 版本历史可能无限增长~~

**文件**: `backend/app/services/version_service.py`
**严重性**: 🟡 中等
**状态**: ✅ 已修复（提交 当前）

**问题描述**: 没有限制版本数量，长期使用可能导致数据库空间占用过大。

**修复方案**: 在创建新版本后自动清理旧版本，保留最新50个版本。

```python
# 修复后：第 98-105 行
# 自动清理旧版本（保留最新50个版本）
try:
    deleted_count = VersionService.delete_old_versions(db, note_id, keep_count=50)
    if deleted_count > 0:
        logger.info(f"自动清理旧版本: deleted={deleted_count}")
except Exception as e:
    logger.warning(f"自动清理旧版本失败: {e}")
```

---

### ~~Bug #5: mentions 字段验证缺失~~

**文件**: `backend/app/services/comment_service.py`
**严重性**: 🟢 低
**状态**: ✅ 已修复（提交 当前）

**问题描述**: 没有验证 mentions 中的用户ID是否真实存在。

**修复方案**: 添加用户ID验证，过滤掉不存在的用户。

```python
# 修复后：第 86-99 行
# 验证mentions中的用户ID是否存在
valid_mentions = []
for uid in comment_create.mentions:
    user_exists = db.query(User).filter(User.id == uid).first() is not None
    if user_exists:
        valid_mentions.append(str(uid))
    else:
        logger.warning(f"提及的用户不存在，已过滤: user_id={uid}")

if valid_mentions:
    mentions_json = json.dumps(valid_mentions, ensure_ascii=False)
```

---

### ~~Bug #6: 并发创建版本可能导致版本号重复~~

**文件**: `backend/app/services/version_service.py`
**严重性**: 🟡 中等
**状态**: ✅ 已修复（提交 当前）

**问题描述**: 在高并发情况下，两个请求可能同时查询到相同的版本号。

**修复方案**: 使用数据库行锁（SELECT FOR UPDATE）防止并发冲突。

```python
# 修复后：第 72-75 行
# 使用 with_for_update() 加行锁
latest_version = db.query(NoteVersion).filter(
    NoteVersion.note_id == note_id
).order_by(NoteVersion.version_number.desc()).with_for_update().first()
```

---

### ~~Bug #7: WebSocket token 可能被记录到日志~~

**文件**: `backend/app/api/collaboration.py`
**严重性**: 🔴 高（安全）
**状态**: ✅ 已修复（提交 c4a5bae）

**问题描述**: 如果token验证失败，异常信息可能包含token本身被记录到日志中。

**修复方案**: 改为记录通用错误信息，不包含敏感数据。

```python
# 修复后：第 523 行
logger.warning(f"WebSocket认证失败: note_id={note_id}, reason=invalid_token")
```

---

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

### 🎉 所有优先级的 Bug 已全部修复！

#### ✅ 高优先级（已完成）
1. ✅ Bug #8: WebSocket 认证缺失
2. ✅ Bug #7: Token 可能泄露到日志
3. ✅ Bug #1: JSON 解析缺少异常处理

#### ✅ 中优先级（已完成）
4. ✅ Bug #3: 重复通知问题
5. ✅ Bug #4: 版本历史无限增长
6. ✅ Bug #6: 并发版本号重复

#### ✅ 低优先级（已完成）
7. ✅ Bug #5: mentions 字段验证
8. ✅ Bug #2: WebSocket 断开异常（已有处理）

---

## 🔧 修复计划（全部完成）

### ✅ 立即修复（已完成）
- [x] Bug #8: WebSocket 认证
- [x] Bug #9: JSON 解析异常（version_service）
- [x] Bug #10: 数据库事务回滚
- [x] Bug #11: JSON 序列化异常（comment_service）
- [x] Bug #7: Token 日志泄露
- [x] Bug #1: JSON 解析异常（collaboration.py）

### ✅ 第二批修复（已完成）
- [x] Bug #3: 通知去重
- [x] Bug #4: 版本自动清理
- [x] Bug #6: 版本号并发冲突

### ✅ 第三批修复（已完成）
- [x] Bug #5: mentions 验证
- [x] Bug #2: WebSocket 断开异常验证

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
