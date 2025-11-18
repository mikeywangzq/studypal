# Phase 9 - 实时协作与版本控制系统

## 📋 概述

Phase 9 为 StudyPal 添加了完整的实时协作和版本控制功能，使用户可以协同编辑笔记、管理版本历史、进行评论讨论，并接收实时通知。

## 🎯 核心功能

### 1. 版本控制系统

#### 设计理念
- **快照机制**: 每个版本存储完整的笔记内容（而非差分）
- **优点**: 实现简单、恢复迅速、版本独立
- **缺点**: 存储空间较大（可通过定期清理缓解）

#### 功能特性
- ✅ 自动/手动创建版本快照
- ✅ 查看版本历史（最多50个版本）
- ✅ 版本对比（标题、内容、分类、标签）
- ✅ 一键回滚到任意版本
- ✅ 版本创建者和变更说明

#### API 端点
```
GET    /api/notes/{note_id}/versions          # 获取版本列表
POST   /api/notes/{note_id}/versions          # 手动创建版本
POST   /api/notes/{note_id}/restore/{version_id}  # 恢复版本
GET    /api/versions/compare                   # 对比两个版本
```

### 2. 评论系统

#### 设计理念
- **两层结构**: 顶层评论 + 回复（避免过深嵌套）
- **@提及功能**: 支持在评论中提及多个用户
- **级联删除**: 删除父评论自动删除所有子回复

#### 功能特性
- ✅ 创建评论和回复
- ✅ @提及用户（支持多个）
- ✅ 编辑评论（标记已编辑状态）
- ✅ 删除评论（级联删除回复）
- ✅ 嵌套回复展示

#### API 端点
```
POST   /api/notes/{note_id}/comments           # 创建评论
GET    /api/notes/{note_id}/comments           # 获取评论树
PUT    /api/comments/{comment_id}              # 更新评论
DELETE /api/comments/{comment_id}              # 删除评论
```

### 3. 通知系统

#### 通知类型
1. **share** - 笔记分享通知
2. **comment** - 评论通知
3. **mention** - @提及通知
4. **permission** - 权限变更通知

#### 功能特性
- ✅ 自动通知触发
- ✅ 已读/未读状态管理
- ✅ 批量标记已读
- ✅ 通知统计（按类型）
- ✅ 删除通知

#### API 端点
```
GET    /api/notifications                      # 获取通知列表
POST   /api/notifications/{id}/read            # 标记已读
POST   /api/notifications/read-all             # 全部已读
GET    /api/notifications/stats                # 获取统计
DELETE /api/notifications/{id}                 # 删除通知
```

### 4. WebSocket 实时协作

#### 设计理念
- **房间模式**: 每个笔记是一个独立的协作房间
- **内存存储**: 光标位置和连接信息存储在内存中
- **自动清理**: 断开连接自动清理资源

#### 功能特性
- ✅ 实时光标同步
- ✅ 编辑操作广播
- ✅ 在线用户列表
- ✅ 用户加入/离开通知
- ✅ JWT 身份验证
- ✅ 权限检查

#### WebSocket 端点
```
WS     /api/ws/notes/{note_id}?token={jwt}     # WebSocket连接
GET    /api/notes/{note_id}/online-users       # 在线用户
```

#### 消息类型
```javascript
// 光标位置更新
{
  type: 'cursor_update',
  position: { line: 10, column: 5 }
}

// 编辑操作
{
  type: 'edit',
  operation: {
    type: 'insert',  // 或 'delete', 'replace'
    position: { line: 10, column: 5 },
    content: '新文本'
  }
}

// 用户加入（系统消息）
{
  type: 'user_joined',
  user_id: '...',
  username: '...',
  users_count: 3
}

// 用户离开（系统消息）
{
  type: 'user_left',
  user_id: '...',
  username: '...',
  users_count: 2
}
```

## 🗄️ 数据库设计

### note_versions 表
```sql
CREATE TABLE note_versions (
    id UUID PRIMARY KEY,
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR,
    tags VARCHAR,  -- JSON数组
    changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    change_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_note_versions_note_id ON note_versions(note_id);
```

### note_comments 表
```sql
CREATE TABLE note_comments (
    id UUID PRIMARY KEY,
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    parent_id UUID REFERENCES note_comments(id) ON DELETE CASCADE,
    mentions VARCHAR,  -- JSON数组
    is_edited BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_note_comments_note_id ON note_comments(note_id);
CREATE INDEX idx_note_comments_user_id ON note_comments(user_id);
CREATE INDEX idx_note_comments_parent_id ON note_comments(parent_id);
```

### notifications 表
```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
```

## 🏗️ 技术实现

### 服务层架构

```
backend/app/services/
├── version_service.py       # 版本控制服务
├── comment_service.py       # 评论管理服务
├── notification_service.py  # 通知系统服务
└── websocket_manager.py     # WebSocket连接管理
```

### 关键设计模式

#### 1. 服务层模式
所有业务逻辑封装在服务类中，API层只负责请求处理。

```python
class VersionService:
    @staticmethod
    def create_version(...) -> Optional[NoteVersion]:
        # 业务逻辑
        pass
```

#### 2. ConnectionManager 模式
```python
class ConnectionManager:
    def __init__(self):
        # note_id -> {user_id: websocket}
        self.active_connections: Dict[UUID, Dict[UUID, WebSocket]] = {}
        # note_id -> {user_id: {line, column}}
        self.cursor_positions: Dict[UUID, Dict[UUID, dict]] = {}
```

#### 3. 辅助方法模式
```python
class NotificationService:
    # 通用方法
    @staticmethod
    def create_notification(...):
        pass

    # 特定类型辅助方法
    @staticmethod
    def notify_share(...):
        return NotificationService.create_notification(...)
```

## 🔒 安全性设计

### WebSocket 认证流程
```
1. 客户端提供 JWT token（查询参数）
2. 服务器验证 token 有效性
3. 检查用户对笔记的访问权限
4. 验证通过后建立连接
5. 验证失败则关闭连接（WS_1008_POLICY_VIOLATION）
```

### 权限控制
- **版本操作**: 需要笔记的编辑权限
- **评论操作**: 需要笔记的查看权限
- **更新/删除评论**: 只有作者可以操作
- **通知操作**: 只能操作自己的通知

## 🐛 Bug 修复记录

### 1. WebSocket 安全漏洞（严重）
**问题**: 缺少身份验证，任何人都可以连接
**修复**: 添加 JWT token 验证和权限检查

### 2. JSON 解析异常
**问题**: 标签数据损坏时会导致崩溃
**修复**: 添加 try-catch 异常处理，失败时使用空数组

### 3. 事务回滚缺失
**问题**: 数据库操作失败可能导致脏数据
**修复**: 所有数据库操作添加异常处理和回滚

### 4. JSON 序列化异常
**问题**: mentions 序列化可能失败
**修复**: 添加异常处理，失败时降级处理

## 📊 性能优化

### 数据库优化
- ✅ 添加索引（note_id, user_id, is_read, type）
- ✅ 限制查询数量（默认50条）
- ✅ 级联删除（数据库级别）

### WebSocket 优化
- ✅ 内存存储（避免频繁数据库访问）
- ✅ 自动清理断开连接
- ✅ 排除发送者（避免消息回环）

### 建议的未来优化
- 🔄 大量通知使用批量 update
- 🔄 版本历史自动清理（保留最近 N 个）
- 🔄 WebSocket 消息压缩
- 🔄 光标位置节流（避免过度广播）

## 🧪 测试建议

### 1. WebSocket 安全测试
```javascript
// 无token连接
const ws1 = new WebSocket('ws://localhost:8000/api/ws/notes/{note_id}');
// 应被拒绝

// 无效token
const ws2 = new WebSocket('ws://localhost:8000/api/ws/notes/{note_id}?token=invalid');
// 应被拒绝

// 有效token但无权限
const ws3 = new WebSocket('ws://localhost:8000/api/ws/notes/{note_id}?token={valid}');
// 应被拒绝

// 有效token且有权限
const ws4 = new WebSocket('ws://localhost:8000/api/ws/notes/{note_id}?token={authorized}');
// 应成功连接
```

### 2. 版本恢复测试
- 恢复包含中文标签的版本
- 恢复标签为 null 的版本
- 恢复标签数据损坏的版本

### 3. 评论功能测试
- 创建顶层评论
- 创建回复评论
- @提及多个用户
- 删除父评论（验证子回复也被删除）

### 4. 并发测试
- 多用户同时连接同一笔记
- 并发创建版本
- 并发评论

## 📈 代码统计

| 文件 | 行数 | 功能 |
|------|------|------|
| note_version.py | 118 | 数据库模型 |
| collaboration.py (schemas) | 180 | Pydantic模型 |
| version_service.py | 330 | 版本控制逻辑 |
| comment_service.py | 353 | 评论管理逻辑 |
| notification_service.py | 533 | 通知系统逻辑 |
| websocket_manager.py | 270 | WebSocket管理 |
| collaboration.py (api) | 551 | API端点 |
| **总计** | **2,335行** | **17个API端点** |

## 🚀 部署注意事项

### 数据库迁移
```bash
# 创建迁移文件
alembic revision --autogenerate -m "Add Phase 9 collaboration tables"

# 执行迁移
alembic upgrade head
```

### 环境变量
无需新增环境变量，使用现有的 JWT 配置。

### WebSocket 配置
确保反向代理（如 Nginx）支持 WebSocket：
```nginx
location /api/ws/ {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## 📚 前端集成示例

### WebSocket 连接
```javascript
const token = localStorage.getItem('jwt_token');
const noteId = '...';
const ws = new WebSocket(
  `ws://localhost:8000/api/ws/notes/${noteId}?token=${token}`
);

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'cursor_update':
      updateCursor(data.user_id, data.position);
      break;
    case 'edit':
      applyEdit(data.operation);
      break;
    case 'user_joined':
      addOnlineUser(data.user_id, data.username);
      break;
    case 'user_left':
      removeOnlineUser(data.user_id);
      break;
  }
};

// 发送光标位置
ws.send(JSON.stringify({
  type: 'cursor_update',
  position: { line: 10, column: 5 }
}));
```

## 🔮 未来扩展

### Phase 10 建议
- 📱 移动端适配
- 🎨 前端界面实现
- 📊 数据分析和统计
- 🔔 邮件/推送通知
- 🌐 国际化支持
- ⚡ 性能优化（Redis缓存）
- 🔍 全文搜索（Elasticsearch）
