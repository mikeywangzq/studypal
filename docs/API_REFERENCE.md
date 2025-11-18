# API 快速参考

## 版本控制 API

### 获取版本历史
```http
GET /api/notes/{note_id}/versions?limit=50
Authorization: Bearer {token}
```

### 创建版本快照
```http
POST /api/notes/{note_id}/versions
Authorization: Bearer {token}
Content-Type: application/json

{
  "change_description": "修复了拼写错误"
}
```

### 恢复到指定版本
```http
POST /api/notes/{note_id}/restore/{version_id}
Authorization: Bearer {token}
```

### 对比两个版本
```http
GET /api/versions/compare?version_id1={id1}&version_id2={id2}
Authorization: Bearer {token}
```

## 评论 API

### 创建评论
```http
POST /api/notes/{note_id}/comments
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "这是一条评论",
  "parent_id": null,  // 回复时填写父评论ID
  "mentions": ["user-uuid-1", "user-uuid-2"]  // @提及的用户
}
```

### 获取评论列表
```http
GET /api/notes/{note_id}/comments
Authorization: Bearer {token}  // 可选
```

### 更新评论
```http
PUT /api/comments/{comment_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "content": "更新后的内容"
}
```

### 删除评论
```http
DELETE /api/comments/{comment_id}
Authorization: Bearer {token}
```

## 通知 API

### 获取通知列表
```http
GET /api/notifications?unread_only=true&limit=50
Authorization: Bearer {token}
```

### 标记为已读
```http
POST /api/notifications/{notification_id}/read
Authorization: Bearer {token}
```

### 标记全部已读
```http
POST /api/notifications/read-all
Authorization: Bearer {token}
```

### 获取通知统计
```http
GET /api/notifications/stats
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "total": 25,
  "unread": 5,
  "by_type": {
    "share": 10,
    "comment": 8,
    "mention": 5,
    "permission": 2
  }
}
```

### 删除通知
```http
DELETE /api/notifications/{notification_id}
Authorization: Bearer {token}
```

## WebSocket 实时协作

### 建立连接
```javascript
const token = localStorage.getItem('jwt_token');
const ws = new WebSocket(
  `ws://localhost:8000/api/ws/notes/{note_id}?token=${token}`
);
```

### 发送光标位置
```javascript
ws.send(JSON.stringify({
  type: 'cursor_update',
  position: { line: 10, column: 5 }
}));
```

### 发送编辑操作
```javascript
ws.send(JSON.stringify({
  type: 'edit',
  operation: {
    type: 'insert',
    position: { line: 10, column: 5 },
    content: '新插入的文本'
  }
}));
```

### 接收消息
```javascript
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case 'cursor_update':
      console.log('光标更新:', data.user_id, data.position);
      break;
    case 'edit':
      console.log('编辑操作:', data.operation);
      break;
    case 'user_joined':
      console.log('用户加入:', data.username);
      break;
    case 'user_left':
      console.log('用户离开:', data.username);
      break;
    case 'online_users':
      console.log('在线用户:', data.users);
      break;
  }
};
```

### 获取在线用户
```http
GET /api/notes/{note_id}/online-users
Authorization: Bearer {token}
```

**响应示例**:
```json
{
  "note_id": "...",
  "online_users": ["user-id-1", "user-id-2"],
  "users_count": 2
}
```

## 错误响应

所有API遵循统一的错误响应格式：

```json
{
  "detail": "错误描述信息"
}
```

### 常见状态码
- `200` - 成功
- `201` - 创建成功
- `204` - 删除成功（无内容）
- `400` - 请求参数错误
- `401` - 未认证
- `403` - 无权限
- `404` - 资源不存在
- `500` - 服务器错误
