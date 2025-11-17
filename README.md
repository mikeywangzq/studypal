# StudyPal - AI 智能学习助手

> 🎓 专为计算机系学生打造的智能学习伙伴，让学习更高效、更智能！
>
> **笔记管理** · **AI 问答** · **DDL 追踪** · 三位一体的学习解决方案

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)

</div>

---

## 📖 目录

- [✨ 核心功能](#-核心功能)
- [🛠️ 技术栈](#️-技术栈)
- [🚀 快速开始](#-快速开始)
- [📚 API 文档](#-api-文档)
- [💡 使用指南](#-使用指南)
- [🏗️ 系统架构](#️-系统架构)
- [🗄️ 数据库设计](#️-数据库设计)
- [⚙️ 配置说明](#️-配置说明)
- [🧪 测试指南](#-测试指南)
- [🚢 部署方案](#-部署方案)
- [🗺️ 发展路线](#️-发展路线)

---

## ✨ 核心功能

### 🎯 三大核心模块（已全部实现！）

<table>
<tr>
<td width="33%" valign="top">

#### 📚 智能笔记管理
- ✅ **多格式支持**
  `.md` `.txt` `.py` `.cpp` `.java` `.js` `.ts` 等

- ✅ **自动索引**
  上传即自动分块和向量化

- ✅ **🆕 AI 自动分类**
  使用 LLM 智能推荐笔记分类

- ✅ **🆕 自动标签提取**
  AI 自动提取技术关键词作为标签

- ✅ **语义搜索**
  使用自然语言查找相关笔记

- ✅ **完整 CRUD**
  增删改查一应俱全

</td>
<td width="33%" valign="top">

#### 🤖 AI 智能问答
- ✅ **基于笔记回答**
  AI 只用你的笔记回答问题

- ✅ **来源追溯**
  每个回答都显示引用来源

- ✅ **多轮对话**
  支持上下文理解的连续对话

- ✅ **Markdown 渲染**
  代码高亮、公式显示

- ✅ **相关度评分**
  显示每个来源的可信度

</td>
<td width="33%" valign="top">

#### 📅 DDL 截止日期管理
- ✅ **作业追踪**
  作业、考试、项目一网打尽

- ✅ **优先级管理**
  高/中/低三档优先级

- ✅ **智能视图**
  即将到期、已逾期、已完成

- ✅ **统计面板**
  5 个统计卡片一目了然

- ✅ **时间提示**
  "还剩 2天" "逾期 3天"

</td>
</tr>
</table>

### 🔥 技术亮点

<div align="center">

| 🚀 特性 | 📝 说明 |
|--------|---------|
| **RAG 检索增强** | 向量搜索 + GPT 大模型，答案准确度高 |
| **向量数据库** | ChromaDB 实现高效语义相似度搜索 |
| **大模型集成** | OpenAI GPT-3.5-turbo 提供智能回答 |
| **🆕 智能分类** | LLM 自动分类笔记并提取技术标签 |
| **🆕 查询缓存** | LRU/TTL 缓存策略提升响应速度 |
| **🆕 JWT 认证** | 安全的用户认证和授权系统 |
| **🆕 OAuth 登录** | 支持 Google/GitHub 第三方登录 |
| **🆕 个人资料管理** | 完整的用户资料和密码管理功能 |
| **🆕 笔记分享协作** | 支持公开/私密分享、权限控制、链接访问 |
| **🆕 数据导出** | 支持 JSON/Markdown/CSV 多格式导出 |
| **🆕 测试覆盖** | 完整的单元测试确保代码质量 |
| **一键部署** | Docker Compose 一条命令启动全部服务 |
| **现代化 UI** | Tailwind CSS 打造精美响应式界面 |

</div>

---

## 🛠️ 技术栈

<table>
<tr>
<td width="50%" valign="top">

### 后端技术
```yaml
框架:        FastAPI (Python 3.11+)
数据库:      PostgreSQL 14+
向量库:      ChromaDB
AI/ML:       LangChain + OpenAI
  模型:      GPT-3.5-turbo
  嵌入:      text-embedding-3-small
ORM:         SQLAlchemy 2.0
验证:        Pydantic 2.5+
```

</td>
<td width="50%" valign="top">

### 前端技术
```yaml
框架:        React 18 + TypeScript
构建工具:    Vite 5
样式:        Tailwind CSS 3.4
状态管理:    React Query (TanStack)
路由:        React Router v6
UI 组件:     Lucide Icons
Markdown:    react-markdown + syntax-highlighter
```

</td>
</tr>
</table>

### DevOps 工具
```yaml
容器化:      Docker + Docker Compose
数据库:      PostgreSQL (持久化卷)
文件存储:    本地文件系统 (可扩展至 S3)
```

---

## 🚀 快速开始

### 📋 前置要求
- ✅ **Docker** & **Docker Compose** 已安装
- ✅ **OpenAI API Key** ([获取链接](https://platform.openai.com/))

### 1️⃣ 克隆仓库
```bash
git clone https://github.com/your-username/studypal.git
cd studypal
```

### 2️⃣ 配置环境变量
```bash
# 编辑 backend/.env 文件
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3️⃣ 启动所有服务
```bash
docker-compose up --build
```

⏳ 等待所有服务启动（首次运行约 2-3 分钟）：
- ✅ **PostgreSQL** → localhost:5432
- ✅ **后端 API** → http://localhost:8000
- ✅ **前端界面** → http://localhost:3000

### 4️⃣ 访问应用
- 🎨 **前端界面**: http://localhost:3000
- 📖 **API 文档**: http://localhost:8000/docs (Swagger UI)
- ❤️ **健康检查**: http://localhost:8000/health

### 5️⃣ 上传测试笔记
```bash
cd test_notes
curl -X POST http://localhost:8000/api/notes/upload \
  -F "files=@xv6_page_table.md" \
  -F "files=@tcp_handshake.md" \
  -F "files=@database_index.md"
```

### 6️⃣ 开始提问！
访问 http://localhost:3000/chat 试试这些问题：
- 💬 "xv6 的页表是怎么工作的？"
- 💬 "TCP 三次握手的过程是什么？"
- 💬 "B+Tree 索引有什么特点？"

---

## 📚 API 文档

### 📝 笔记管理 API（7 个端点）

<details>
<summary><b>📤 上传笔记（🆕 支持自动分类）</b></summary>

```http
POST /api/notes/upload?auto_classify=true
Content-Type: multipart/form-data

files: file1.md, file2.py, file3.cpp...
```

**查询参数**:
- `auto_classify` (可选): 是否启用 AI 自动分类和标签提取，默认 false

**支持格式**: `.md` `.txt` `.py` `.cpp` `.c` `.java` `.js` `.ts` `.jsx` `.tsx`
**大小限制**: 单文件 10MB，总计 100MB

**🆕 自动分类功能**:
- 启用后，AI 会自动分析笔记内容
- 推荐最合适的分类（14个预定义分类）
- 自动提取 3-7 个技术关键词作为标签
- 返回置信度和分类理由

</details>

<details>
<summary><b>📋 获取笔记列表</b></summary>

```http
GET /api/notes?category=操作系统&tags=xv6,RISC-V&page=1&limit=20
```

**查询参数**:
- `category` (可选): 分类筛选
- `tags` (可选): 标签筛选（逗号分隔）
- `page` (可选): 页码，默认 1
- `limit` (可选): 每页数量，默认 20

</details>

<details>
<summary><b>🔍 语义搜索</b></summary>

```http
GET /api/notes/search?query=页表是如何工作的&k=5
```

**查询参数**:
- `query` (必填): 搜索关键词或问题
- `k` (可选): 返回结果数量，默认 5

**返回**: 按相关度排序的笔记块

</details>

<details>
<summary><b>📖 获取单个笔记</b></summary>

```http
GET /api/notes/{note_id}
```

</details>

<details>
<summary><b>✏️ 更新笔记</b></summary>

```http
PUT /api/notes/{note_id}
Content-Type: application/json

{
  "title": "更新后的标题",
  "category": "数据库",
  "tags": ["SQL", "索引", "B+Tree"]
}
```

</details>

<details>
<summary><b>🗑️ 删除笔记</b></summary>

```http
DELETE /api/notes/{note_id}
```

**注意**: 会同时删除所有相关的笔记块和向量

</details>

<details>
<summary><b>🆕 📂 获取可用分类列表</b></summary>

```http
GET /api/notes/categories/available
```

**返回示例**:
```json
[
  "操作系统",
  "计算机网络",
  "数据库",
  "算法与数据结构",
  "编程语言",
  "软件工程",
  "计算机体系结构",
  "人工智能",
  "机器学习",
  "Web开发",
  "移动开发",
  "云计算",
  "网络安全",
  "其他"
]
```

**用途**: 前端展示分类选项、筛选笔记

</details>

---

### 💬 AI 问答 API（5 个端点）

<details>
<summary><b>🤖 提问</b></summary>

```http
POST /api/chat/ask
Content-Type: application/json

{
  "question": "xv6 的页表是怎么工作的？",
  "conversation_id": "可选的会话 ID"
}
```

**响应示例**:
```json
{
  "answer": "xv6 使用 RISC-V 的三级页表机制...",
  "sources": [
    {
      "note_id": "uuid",
      "title": "xv6_page_table.md",
      "content_snippet": "...",
      "relevance_score": 0.15
    }
  ],
  "conversation_id": "会话 ID"
}
```

</details>

<details>
<summary><b>📜 获取会话列表</b></summary>

```http
GET /api/chat/conversations?page=1&limit=20
```

**返回**: 所有会话列表（按更新时间排序）

</details>

<details>
<summary><b>💭 获取会话详情</b></summary>

```http
GET /api/chat/conversations/{conversation_id}
```

**返回**: 会话信息 + 所有消息记录

</details>

<details>
<summary><b>✏️ 更新会话标题</b></summary>

```http
PUT /api/chat/conversations/{conversation_id}/title?title=新标题
```

</details>

<details>
<summary><b>🗑️ 删除会话</b></summary>

```http
DELETE /api/chat/conversations/{conversation_id}
```

**注意**: 会同时删除所有相关消息

</details>

---

### 📅 DDL 管理 API（9 个端点）

<details>
<summary><b>➕ 创建 DDL</b></summary>

```http
POST /api/deadlines
Content-Type: application/json

{
  "title": "数据库大作业",
  "course": "数据库系统",
  "due_date": "2024-12-25T23:59:00",
  "priority": "high",
  "description": "完成 ER 图设计和 SQL 实现"
}
```

**优先级**: `low` | `medium` | `high`
**状态**: `pending` | `completed`

</details>

<details>
<summary><b>📋 获取 DDL 列表</b></summary>

```http
GET /api/deadlines?status=pending&priority=high&course=数据库系统
```

**查询参数**:
- `status`: 状态筛选
- `priority`: 优先级筛选
- `course`: 课程筛选
- `from_date`, `to_date`: 时间范围筛选

</details>

<details>
<summary><b>⏰ 即将到期的 DDL</b></summary>

```http
GET /api/deadlines/upcoming?days=7
```

**参数**: `days` - 未来天数，默认 7

**返回**: 未来 N 天内到期的待完成任务

</details>

<details>
<summary><b>🚨 已逾期的 DDL</b></summary>

```http
GET /api/deadlines/overdue
```

**返回**: 所有已逾期但未完成的任务

</details>

<details>
<summary><b>📊 统计数据</b></summary>

```http
GET /api/deadlines/statistics
```

**响应示例**:
```json
{
  "total": 15,
  "pending": 8,
  "completed": 5,
  "overdue": 2,
  "upcoming_7days": 4
}
```

</details>

<details>
<summary><b>📖 获取单个 DDL</b></summary>

```http
GET /api/deadlines/{deadline_id}
```

</details>

<details>
<summary><b>✏️ 更新 DDL</b></summary>

```http
PUT /api/deadlines/{deadline_id}
Content-Type: application/json

{
  "title": "更新后的标题",
  "priority": "medium",
  "due_date": "2024-12-26T23:59:00"
}
```

</details>

<details>
<summary><b>✅ 标记为完成</b></summary>

```http
PATCH /api/deadlines/{deadline_id}/complete
```

**效果**: 将状态改为 `completed`，记录完成时间

</details>

<details>
<summary><b>🗑️ 删除 DDL</b></summary>

```http
DELETE /api/deadlines/{deadline_id}
```

</details>

---

### 🔐 用户认证 API（11 个端点）

<details>
<summary><b>🆕 ✍️ 用户注册</b></summary>

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "your_username",
  "email": "your_email@example.com",
  "password": "your_password",
  "full_name": "Your Name" // 可选
}
```

**返回**:
```json
{
  "user": {
    "id": "uuid",
    "username": "your_username",
    "email": "your_email@example.com",
    "full_name": "Your Name",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

</details>

<details>
<summary><b>🆕 🔑 用户登录</b></summary>

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "your_email@example.com",
  "password": "your_password"
}
```

**返回**: 用户信息和访问令牌

</details>

<details>
<summary><b>🆕 👤 获取当前用户信息</b></summary>

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**需要认证**。返回当前登录用户的信息。

</details>

<details>
<summary><b>🆕 🔄 刷新令牌</b></summary>

```http
POST /api/auth/refresh
Authorization: Bearer <access_token>
```

**需要认证**。使用当前令牌获取新的访问令牌。

</details>

<details>
<summary><b>🆕 📝 更新个人资料</b></summary>

```http
PUT /api/auth/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "username": "new_username", // 可选
  "full_name": "New Name", // 可选
  "bio": "My bio", // 可选
  "avatar_url": "https://example.com/avatar.jpg" // 可选
}
```

**需要认证**。更新个人资料，所有字段均可选。

</details>

<details>
<summary><b>🆕 🔒 修改密码</b></summary>

```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "old_password",
  "new_password": "new_password"
}
```

**需要认证**。修改密码需要验证当前密码。

</details>

<details>
<summary><b>🆕 📧 请求密码重置</b></summary>

```http
POST /api/auth/password-reset/request
Content-Type: application/json

{
  "email": "your_email@example.com"
}
```

**返回重置令牌**（生产环境应通过邮件发送）。

</details>

<details>
<summary><b>🆕 ✅ 确认密码重置</b></summary>

```http
POST /api/auth/password-reset/confirm
Content-Type: application/json

{
  "reset_token": "token_from_email",
  "new_password": "new_password"
}
```

使用重置令牌设置新密码。

</details>

<details>
<summary><b>🆕 🌐 获取 OAuth 授权 URL</b></summary>

```http
GET /api/auth/oauth/{provider}/authorize?redirect_uri=http://localhost:3000/auth/callback
```

**支持提供商**: `google`, `github`

**返回授权 URL**，前端应重定向到该 URL 进行 OAuth 登录。

</details>

<details>
<summary><b>🆕 🔐 OAuth 登录</b></summary>

```http
POST /api/auth/oauth/login
Content-Type: application/json

{
  "provider": "google",
  "code": "authorization_code",
  "redirect_uri": "http://localhost:3000/auth/callback"
}
```

**返回**: 用户信息和 JWT 令牌

**流程**:
1. 前端获取授权 URL 并重定向用户
2. 用户在 OAuth 提供商完成授权
3. 回调带有授权码
4. 前端调用此端点完成登录

</details>

<details>
<summary><b>配置 OAuth</b></summary>

在 `backend/.env` 中配置 OAuth 客户端凭证：

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

**获取凭证**:
- Google: https://console.cloud.google.com/
- GitHub: https://github.com/settings/developers

</details>

---

### 📦 数据导出 API（6 个端点）

<details>
<summary><b>🆕 📄 导出笔记为 JSON</b></summary>

```http
GET /api/export/notes/json
Authorization: Bearer <access_token>
```

**需要认证**。导出当前用户的所有笔记为 JSON 文件。

</details>

<details>
<summary><b>🆕 📝 导出笔记为 Markdown</b></summary>

```http
GET /api/export/notes/markdown
Authorization: Bearer <access_token>
```

**需要认证**。导出所有笔记为一个 Markdown 文件，按分类组织。

</details>

<details>
<summary><b>🆕 💬 导出对话为 JSON</b></summary>

```http
GET /api/export/conversations/json
Authorization: Bearer <access_token>
```

**需要认证**。导出所有对话记录和消息。

</details>

<details>
<summary><b>🆕 📅 导出 DDL 为 JSON</b></summary>

```http
GET /api/export/deadlines/json
Authorization: Bearer <access_token>
```

**需要认证**。导出所有截止日期数据。

</details>

<details>
<summary><b>🆕 📊 导出 DDL 为 CSV</b></summary>

```http
GET /api/export/deadlines/csv
Authorization: Bearer <access_token>
```

**需要认证**。导出DDL为CSV格式，可在Excel中打开。

</details>

<details>
<summary><b>🆕 🗂️ 导出所有数据</b></summary>

```http
GET /api/export/all/json
Authorization: Bearer <access_token>
```

**需要认证**。导出所有数据（笔记、对话、DDL）为一个JSON文件。

**用途**: 数据备份、数据迁移、数据分析

</details>

---

### 🤝 笔记分享与协作 API（10 个端点）

<details>
<summary><b>🆕 🔗 创建笔记分享</b></summary>

```http
POST /api/notes/{note_id}/share
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "shared_with": "user_uuid", // 可选，null表示公开分享
  "permission": "view", // "view" 或 "edit"
  "expires_at": "2024-12-31T23:59:59" // 可选，null表示永不过期
}
```

**返回**包含 `share_token`，可用于访问分享的笔记。

**分享类型**:
- **私密分享**: 指定 `shared_with` 用户ID
- **公开分享**: `shared_with` 设为 null

</details>

<details>
<summary><b>🆕 📋 获取笔记的所有分享</b></summary>

```http
GET /api/notes/{note_id}/shares
Authorization: Bearer <access_token>
```

**需要认证**。仅笔记所有者可查看。

</details>

<details>
<summary><b>🆕 🌐 通过令牌访问分享笔记</b></summary>

```http
GET /api/shares/token/{share_token}
```

**公开端点** - 无需认证！任何持有token的人都可访问。

**返回**: 分享信息 + 笔记内容

</details>

<details>
<summary><b>🆕 ✏️ 更新分享设置</b></summary>

```http
PUT /api/shares/{share_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "permission": "edit", // 可选
  "expires_at": "2025-01-31T23:59:59", // 可选
  "is_active": false // 可选，停用分享
}
```

**需要认证**。仅分享创建者可更新。

</details>

<details>
<summary><b>🆕 🗑️ 取消分享</b></summary>

```http
DELETE /api/shares/{share_id}
Authorization: Bearer <access_token>
```

**需要认证**。仅分享创建者可取消。

</details>

<details>
<summary><b>🆕 📥 获取分享给我的笔记</b></summary>

```http
GET /api/notes/shared-with-me
Authorization: Bearer <access_token>
```

**需要认证**。返回其他用户分享给我的所有笔记列表。

</details>

<details>
<summary><b>🆕 👥 添加用户权限</b></summary>

```http
POST /api/notes/{note_id}/permissions
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "user_id": "user_uuid",
  "permission_level": "editor" // "owner", "editor", "viewer"
}
```

**需要认证**。仅笔记所有者可添加权限。

**权限级别**:
- **owner**: 完全控制（可管理权限）
- **editor**: 可编辑笔记
- **viewer**: 只读访问

</details>

<details>
<summary><b>🆕 📜 获取笔记权限列表</b></summary>

```http
GET /api/notes/{note_id}/permissions
Authorization: Bearer <access_token>
```

**需要认证**。仅笔记所有者可查看。

</details>

<details>
<summary><b>🆕 ❌ 移除用户权限</b></summary>

```http
DELETE /api/permissions/{permission_id}
Authorization: Bearer <access_token>
```

**需要认证**。仅笔记所有者可移除。

</details>

<details>
<summary><b>🆕 ✅ 检查访问权限</b></summary>

```http
GET /api/notes/{note_id}/check-access?permission=view
Authorization: Bearer <access_token>
```

**需要认证**。检查当前用户是否有权限访问笔记。

**参数**: `permission` - "view" 或 "edit"

</details>

---

**📖 完整交互式 API 文档**: http://localhost:8000/docs

---

## 💡 使用指南

### 📚 模块一：笔记管理

#### 📤 上传你的第一个笔记

1. **访问** http://localhost:3000 点击 "管理笔记"
2. **拖放** 或点击选择文件：
   - ✅ 支持格式: `.md` `.txt` `.py` `.cpp` `.c` `.java` `.js` `.ts`
   - 📏 大小限制: 单文件 10MB，总计 100MB
3. **等待** 处理（分块 + 向量化）
4. **完成！** 笔记已可搜索

#### 🔍 搜索你的笔记

**语义搜索**（理解含义）:
```
查询: "如何实现页表转换"
→ 找到关于页表、地址转换、walk() 的笔记
```

**关键词搜索**（精确匹配）:
```
查询: "PTE_V"
→ 找到该标志的精确出现位置
```

---

### 🤖 模块二：AI 问答助手

#### 💬 开始对话

1. **访问** http://localhost:3000/chat
2. **提问**（支持中英文）:
   ```
   "xv6 的页表是怎么工作的？"
   "Explain TCP three-way handshake"
   "B+Tree 和 B-Tree 的区别是什么？"
   ```
3. **查看** AI 的回答和引用来源
4. **点击** 来源查看具体笔记内容

#### 📝 问题示例

<table>
<tr>
<td width="33%" valign="top">

**操作系统**
- xv6 的 walk() 函数如何遍历页表？
- RISC-V 使用几级页表？
- TLB 是什么？为什么需要它？
- 进程切换时页表如何更新？

</td>
<td width="33%" valign="top">

**计算机网络**
- 为什么需要三次握手而不是两次？
- TIME_WAIT 状态的作用是什么？
- SYN 洪水攻击如何防御？
- TCP 如何保证可靠传输？

</td>
<td width="33%" valign="top">

**数据库**
- 聚簇索引和非聚簇索引的区别
- 什么情况下索引会失效？
- 如何选择合适的索引前缀长度？
- B+Tree 为什么适合做索引？

</td>
</tr>
</table>

**跨领域问题**:
- "我有哪些关于操作系统的笔记？"
- "总结一下我学习的所有内容"
- "数据库和操作系统有什么共同点？"

#### 💡 获得更好答案的技巧

| ✅ 好的提问 | ❌ 不好的提问 |
|-----------|------------|
| "xv6 中 walk() 函数的参数 alloc 的作用是什么？" | "页表怎么用？" |
| "TCP 为什么需要 TIME_WAIT 状态？" | "TCP 是什么？" |
| "B+Tree 的叶子节点有什么特点？" | "索引怎么建？" |

**提示**: 越具体的问题，AI 的回答越准确！

---

### 📅 模块三：DDL 管理

#### ➕ 添加你的第一个 DDL

1. **访问** http://localhost:3000/deadlines
2. **点击** "添加 DDL" 按钮
3. **填写** 表单：
   - **标题** *（必填）: "数据库大作业"
   - **课程** （可选）: "数据库系统"
   - **截止时间** *（必填）: 选择日期和时间
   - **优先级**: 高 / 中 / 低
   - **描述** （可选）: 任务详情
4. **提交** 即可在列表中看到！

#### 📊 管理你的 DDL

**视图模式**:
- 🔵 **全部待办** - 所有未完成的任务
- 🟠 **即将到期** - 7 天内到期的任务
- 🔴 **已逾期** - 已过期但未完成（红色背景提醒）
- 🟢 **已完成** - 已完成的任务

**快捷操作**:
- ✅ **完成** - 点击复选框
- 🗑️ **删除** - 点击垃圾桶图标（需确认）
- 📊 **统计** - 查看顶部统计面板

**可视化指示**:
- 🔴 **高优先级** - 红色徽章
- 🟡 **中优先级** - 黄色徽章
- 🟢 **低优先级** - 绿色徽章

**时间显示**:
- 🟠 "还剩 2小时" → 橙色（紧急！）
- 🟡 "还剩 3天" → 黄色（即将到期）
- 🔴 "逾期 2天" → 红色（已逾期！）
- 🟢 "已完成" → 绿色

---

## 🏗️ 系统架构

### 整体架构图

```
┌───────────────────────────────────────────────────────────────────┐
│                     StudyPal AI 学习助手系统                        │
└───────────────────────────────────────────────────────────────────┘

┌─────────────────┐                        ┌─────────────────┐
│   前端 Frontend │ ◀──── HTTP/JSON ────▶  │  后端 Backend   │
│                 │                        │                 │
│  React 18       │                        │  FastAPI        │
│  TypeScript     │                        │  Python 3.11+   │
│  Tailwind CSS   │                        │                 │
└─────────────────┘                        └────────┬────────┘
                                                    │
                           ┌────────────────────────┼────────────────────────┐
                           │                        │                        │
                   ┌───────▼────────┐      ┌────────▼────────┐     ┌────────▼─────────┐
                   │  PostgreSQL    │      │   ChromaDB      │     │   OpenAI API     │
                   │                │      │                 │     │                  │
                   │  关系型数据     │      │   向量数据库     │     │  GPT-3.5-turbo   │
                   │  笔记元数据     │      │   语义搜索       │     │  text-embed-3    │
                   │  会话/DDL      │      │                 │     │                  │
                   └────────────────┘      └─────────────────┘     └──────────────────┘
```

### RAG 检索增强生成流程

```
📝 用户提问
    ↓
🔤 生成问题向量 (OpenAI Embedding)
    ↓
🔍 向量相似度搜索 (ChromaDB)
    ↓ 检索 TOP_K=20 个结果
📊 按相似度阈值过滤 (threshold=0.7)
    ↓ 取前 TOP_N=5 个块
📚 获取笔记块内容
    ↓
🧠 构建提示词
    ├─ 系统指令 (角色定义)
    ├─ 上下文 (检索到的笔记)
    ├─ 历史对话 (最近 5 条)
    └─ 用户问题
    ↓
🤖 调用 GPT-3.5-turbo 生成回答
    ↓
💾 保存到数据库 (conversations + messages)
    ↓
📤 返回答案 + 来源引用
```

### 数据流向图

```
【笔记上传流程】
用户 → 前端 → API → Service → Database
                        ↓
                  Text Splitter
                   (分块处理)
                        ↓
                Embedding Service
                 (生成向量)
                        ↓
                    ChromaDB
                 (存储向量索引)

【AI 问答流程】
用户 → 前端 → API → RAG Service
                        ↓
                1. 检索上下文 (ChromaDB)
                2. 格式化提示词
                3. 调用 LLM (OpenAI)
                4. 保存会话
                        ↓
                   PostgreSQL
                 (conversations + messages)
```

---

## 🗄️ 数据库设计

### ER 实体关系图

```
┌──────────────┐
│    users     │  用户表
├──────────────┤
│ id (PK)      │  UUID 主键
│ username     │  用户名
│ email        │  邮箱
│ password     │  密码哈希
│ created_at   │  创建时间
└──────┬───────┘
       │
       │ (1:N) 一个用户有多个笔记/会话/DDL
       │
┌──────▼───────────┐         ┌──────────────────┐
│     notes        │────────▶│  note_chunks     │  笔记块表
├──────────────────┤   1:N   ├──────────────────┤
│ id (PK)          │         │ id (PK)          │  UUID 主键
│ user_id (FK)     │         │ note_id (FK)     │  外键 → notes.id
│ title            │         │ chunk_index      │  块序号
│ file_type        │         │ content          │  块内容
│ file_path        │         │ vector_id        │  ChromaDB ID
│ content          │         │ created_at       │  创建时间
│ category         │         └──────────────────┘
│ tags (JSONB)     │
│ created_at       │
│ updated_at       │
└──────────────────┘

┌──────▼───────────────┐         ┌──────────────────┐
│  conversations       │────────▶│    messages      │  消息表
├──────────────────────┤   1:N   ├──────────────────┤
│ id (PK)              │         │ id (PK)          │  UUID 主键
│ user_id (FK)         │         │ conversation_id  │  外键 → conversations.id
│ title                │         │ role             │  user / assistant
│ created_at           │         │ content          │  消息内容
│ updated_at           │         │ sources (JSONB)  │  来源引用
└──────────────────────┘         │ created_at       │  创建时间
                                 └──────────────────┘

┌──────▼───────────┐
│   deadlines      │  DDL 表
├──────────────────┤
│ id (PK)          │  UUID 主键
│ user_id (FK)     │  外键 → users.id
│ title            │  标题
│ course           │  课程名称
│ description      │  描述
│ due_date         │  截止时间
│ priority         │  优先级: low/medium/high
│ status           │  状态: pending/completed
│ reminder_sent    │  是否已发送提醒
│ created_at       │  创建时间
│ updated_at       │  更新时间
│ completed_at     │  完成时间
└──────────────────┘
```

### 表详细说明

<table>
<tr>
<th>表名</th>
<th>用途</th>
<th>索引</th>
<th>关键字段</th>
</tr>

<tr>
<td><code>users</code></td>
<td>用户信息（预留，当前未启用）</td>
<td><code>email</code> (UNIQUE)<br><code>username</code></td>
<td><code>password</code> (bcrypt 哈希)</td>
</tr>

<tr>
<td><code>notes</code></td>
<td>笔记文件元数据</td>
<td><code>user_id</code><br><code>category</code><br><code>created_at</code></td>
<td><code>tags</code> (JSONB 数组)<br><code>file_path</code> (本地路径)</td>
</tr>

<tr>
<td><code>note_chunks</code></td>
<td>笔记分块（用于向量搜索）</td>
<td><code>note_id</code><br><code>chunk_index</code></td>
<td><code>vector_id</code> (ChromaDB 引用)<br><code>content</code> (分块文本)</td>
</tr>

<tr>
<td><code>conversations</code></td>
<td>对话会话分组</td>
<td><code>user_id</code><br><code>updated_at</code></td>
<td><code>title</code> (自动生成或用户指定)</td>
</tr>

<tr>
<td><code>messages</code></td>
<td>对话消息记录</td>
<td><code>conversation_id</code><br><code>created_at</code></td>
<td><code>role</code> (user/assistant)<br><code>sources</code> (JSONB 来源列表)</td>
</tr>

<tr>
<td><code>deadlines</code></td>
<td>作业/考试截止日期</td>
<td><code>user_id</code><br><code>due_date</code><br><code>status</code></td>
<td><code>priority</code> (枚举)<br><code>status</code> (枚举)<br><code>reminder_sent</code> (布尔)</td>
</tr>
</table>

---

## ⚙️ 配置说明

### 后端环境变量 (`backend/.env`)

```bash
# ========== 应用配置 ==========
APP_NAME=StudyPal - AI Learning Assistant
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# ========== 数据库配置 ==========
DATABASE_URL=postgresql://studypal_user:studypal_password@postgres:5432/studypal_db

# ========== OpenAI 配置 ==========
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo                  # 或 gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
LLM_TEMPERATURE=0.5                         # 0.0-1.0 (越高越有创造性)
LLM_MAX_TOKENS=2000                         # 最大回复长度

# ========== 向量搜索配置 ==========
VECTOR_DB=chroma
CHROMA_PERSIST_DIR=/app/chroma_db
SIMILARITY_THRESHOLD=0.7                    # 相似度阈值 (越低越严格)
TOP_K=20                                    # 初始检索数量
TOP_N=5                                     # 最终上下文块数

# ========== 文件上传配置 ==========
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE_MB=10                         # 单文件大小限制
MAX_UPLOAD_SIZE_MB=100                      # 总上传大小限制
SUPPORTED_EXTENSIONS=.md,.txt,.cpp,.c,.py,.java,.js,.ts,.jsx,.tsx

# ========== 文本处理配置 ==========
CHUNK_SIZE=1000                             # 每块字符数
CHUNK_OVERLAP=200                           # 块之间重叠字符数

# ========== 安全配置 ==========
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ========== 性能配置 ==========
CACHE_TTL_SECONDS=600
ENABLE_QUERY_CACHE=true
RATE_LIMIT_PER_MINUTE=60

# ========== CORS 配置 ==========
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 前端环境变量 (`frontend/.env`)

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 🎯 调优建议

<table>
<tr>
<th>目标</th>
<th>推荐配置</th>
<th>说明</th>
</tr>

<tr>
<td>🎯 <b>提高答案质量</b></td>
<td>

```env
LLM_TEMPERATURE=0.3
TOP_N=7
SIMILARITY_THRESHOLD=0.6
```

</td>
<td>
• 降低温度让回答更准确<br>
• 增加上下文块数<br>
• 降低阈值纳入更多来源
</td>
</tr>

<tr>
<td>⚡ <b>提高响应速度</b></td>
<td>

```env
TOP_K=10
TOP_N=3
CHUNK_SIZE=500
```

</td>
<td>
• 减少初始检索数量<br>
• 减少上下文块数<br>
• 使用更小的块
</td>
</tr>

<tr>
<td>📚 <b>处理长文档</b></td>
<td>

```env
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
MAX_FILE_SIZE_MB=20
```

</td>
<td>
• 增大块尺寸<br>
• 增加重叠保留上下文<br>
• 放宽文件大小限制
</td>
</tr>

<tr>
<td>💡 <b>更有创意的回答</b></td>
<td>

```env
LLM_TEMPERATURE=0.8
OPENAI_MODEL=gpt-4
```

</td>
<td>
• 提高温度增加创造性<br>
• 使用 GPT-4 (成本更高)
</td>
</tr>
</table>

---

## 🧪 测试指南

### 快速测试（使用示例笔记）

我们在 `test_notes/` 目录提供了 3 个高质量示例笔记：

1. **xv6_page_table.md** - 操作系统：xv6 页表机制
2. **tcp_handshake.md** - 计算机网络：TCP 三次握手
3. **database_index.md** - 数据库：索引原理

#### 📤 上传测试笔记

```bash
cd test_notes

# 上传所有示例笔记
curl -X POST http://localhost:8000/api/notes/upload \
  -F "files=@xv6_page_table.md" \
  -F "files=@tcp_handshake.md" \
  -F "files=@database_index.md"
```

#### 🔍 测试语义搜索

```bash
# 测试 1: 搜索页表相关内容
curl "http://localhost:8000/api/notes/search?query=页表机制&k=3"

# 测试 2: 搜索网络相关内容
curl "http://localhost:8000/api/notes/search?query=三次握手&k=3"

# 测试 3: 搜索数据库相关内容
curl "http://localhost:8000/api/notes/search?query=B+Tree索引&k=3"
```

#### 🤖 测试 AI 问答

```bash
# 问题 1: 操作系统
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "xv6的页表是怎么工作的？"}'

# 问题 2: 计算机网络
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "为什么TCP需要三次握手？"}'

# 问题 3: 数据库
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "B+Tree有什么特点？"}'
```

#### 📅 测试 DDL 管理

```bash
# 创建 DDL
curl -X POST http://localhost:8000/api/deadlines \
  -H "Content-Type: application/json" \
  -d '{
    "title": "数据库大作业",
    "course": "数据库系统",
    "due_date": "2024-12-25T23:59:00",
    "priority": "high",
    "description": "完成ER图设计"
  }'

# 获取统计信息
curl http://localhost:8000/api/deadlines/statistics

# 获取即将到期的 DDL
curl "http://localhost:8000/api/deadlines/upcoming?days=7"
```

#### 🆕 测试智能分类功能

```bash
# 测试 1: 上传笔记并启用自动分类
curl -X POST "http://localhost:8000/api/notes/upload?auto_classify=true" \
  -F "files=@test_notes/xv6_page_table.md"

# 测试 2: 获取可用分类列表
curl http://localhost:8000/api/notes/categories/available
```

#### 🆕 运行单元测试

```bash
# 进入后端目录
cd backend

# 安装测试依赖
pip install -r requirements.txt

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_classification_service.py -v

# 查看测试覆盖率
pytest --cov=app --cov-report=html
```

**测试文件**:
- `tests/test_notes_api.py` - 笔记 API 测试
- `tests/test_classification_service.py` - 分类服务测试
- `tests/test_cache_service.py` - 缓存服务测试

### 📋 完整测试文档

详细测试指南请查看 **[TESTING.md](./TESTING.md)**，包含：
- ✅ 完整测试场景
- 📊 API 测试示例
- ⚡ 性能基准测试
- 🤖 自动化测试脚本
- 📈 质量评估指标

---

## 🚢 部署方案

### ☑️ 生产环境检查清单

部署前请确保完成以下配置：

- [ ] 修改 `backend/.env` 中的 `SECRET_KEY`
- [ ] 使用强密码配置 PostgreSQL
- [ ] 设置 `DEBUG=false`
- [ ] 配置正确的 `CORS_ORIGINS`
- [ ] 配置 HTTPS/SSL 证书
- [ ] 使用生产级 OpenAI API Key（设置使用限额）
- [ ] 设置数据库定期备份
- [ ] 配置日志轮转
- [ ] 部署监控系统 (Prometheus/Grafana)
- [ ] 实现 API 速率限制
- [ ] 启用用户认证系统

### 🐳 Docker 生产部署

```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 启动所有服务（后台运行）
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 停止服务
docker-compose -f docker-compose.prod.yml down
```

### 🔧 手动部署

#### 后端部署

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 使用 Gunicorn + Uvicorn Workers 运行
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

#### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 部署 dist/ 目录
# 方案 1: 使用 Nginx
# 方案 2: 使用 Apache
# 方案 3: 使用 Vercel/Netlify
```

#### Nginx 配置示例

```nginx
# 前端
server {
    listen 80;
    server_name studypal.example.com;

    root /var/www/studypal/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

# 后端 API
server {
    listen 80;
    server_name api.studypal.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🗺️ 发展路线

### ✅ 第一阶段：基础框架（已完成）
- [x] 项目结构搭建
- [x] 数据库模型设计（5 张表）
- [x] Docker 配置
- [x] FastAPI 框架搭建
- [x] React + TypeScript 前端搭建

### ✅ 第二阶段：笔记管理（已完成）
- [x] 文件上传与验证
- [x] 文本分块 (RecursiveCharacterTextSplitter)
- [x] 向量嵌入生成 (OpenAI)
- [x] ChromaDB 向量数据库集成
- [x] 语义搜索 API
- [x] 笔记 CRUD 操作

### ✅ 第三阶段：RAG 问答系统（已完成）
- [x] RAG 服务实现
- [x] 向量检索流程
- [x] LLM 集成 (GPT-3.5)
- [x] 会话管理
- [x] 聊天界面 + Markdown 渲染
- [x] 来源追溯
- [x] 多轮对话

### ✅ 第四阶段：DDL 管理（已完成）
- [x] DDL CRUD API
- [x] 优先级和状态管理
- [x] 统计面板
- [x] 列表视图（即将到期、已逾期、已完成）
- [x] 时间可视化指示
- [x] 响应式 UI

### ✅ 第五阶段：智能增强（已完成）
- [x] 使用 LLM 自动分类笔记
- [x] 自动提取标签
- [x] 查询结果缓存优化（LRU + TTL）
- [x] 单元测试和集成测试
- [ ] 高级数据分析

### ✅ 第六阶段：高级功能（已完成）
- [x] JWT 用户认证系统
- [x] 用户注册和登录
- [x] 数据导出功能（JSON/Markdown/CSV）
- [x] 访问令牌管理
- [ ] 笔记协作分享
- [ ] 移动端适配

### ✅ 第七阶段：用户系统增强（已完成）
- [x] 个人资料管理（更新用户名、姓名、简介、头像）
- [x] 密码修改功能
- [x] 密码重置功能（令牌机制）
- [x] OAuth 第三方登录（Google & GitHub）
- [x] 用户模型扩展（支持更多字段）
- [x] OAuth 服务集成

### ✅ 第八阶段：笔记分享与协作（已完成）
- [x] 笔记分享功能（公开/私密分享）
- [x] 分享令牌生成和验证
- [x] 分享权限控制（仅查看/可编辑）
- [x] 分享过期时间设置
- [x] 用户级别权限管理（所有者/编辑者/查看者）
- [x] 访问权限检查系统
- [x] 分享给我的笔记列表
- [x] 分享访问统计

### 🚀 未来展望

<table>
<tr>
<td width="50%" valign="top">

#### 🤝 协作功能增强
- [ ] 实时协作编辑（WebSocket）
- [ ] 笔记变更历史和版本控制
- [ ] 评论和讨论功能
- [ ] 团队工作空间

#### 📱 移动端
- [ ] React Native 移动应用
- [ ] 离线模式支持
- [ ] 推送通知
- [ ] 语音输入

</td>
<td width="50%" valign="top">

#### 🎨 功能扩展
- [ ] 日历视图展示 DDL
- [ ] 邮件提醒
- [ ] 知识图谱可视化
- [ ] 学习进度分析
- [ ] 笔记分享与协作

#### 🌍 国际化
- [ ] 多语言支持
- [ ] 本地化界面

</td>
</tr>
</table>

---

## 📊 项目数据

<div align="center">

| 📈 指标 | 💯 数值 |
|--------|---------|
| **代码文件数** | 83+ |
| **代码行数** | 11,500+ |
| **API 端点** | 48 |
| **数据库表** | 7 |
| **React 组件** | 15+ |
| **开发阶段** | 8 个阶段 ✅ |
| **测试文件** | 3 个测试套件 |
| **测试用例** | 40+ 个测试 |

</div>

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. **Fork** 本仓库
2. **创建** 特性分支 (`git checkout -b feature/amazing-feature`)
3. **提交** 你的修改 (`git commit -m 'feat: Add amazing feature'`)
4. **推送** 到分支 (`git push origin feature/amazing-feature`)
5. **开启** Pull Request

### 📝 代码规范

- **Python**: 遵循 PEP 8 规范
- **TypeScript**: 使用项目配置的 ESLint
- **提交信息**: 使用约定式提交
  - `feat:` 新功能
  - `fix:` 修复 Bug
  - `docs:` 文档更新
  - `style:` 代码格式
  - `refactor:` 重构
  - `test:` 测试相关
  - `chore:` 构建/工具相关

---

## 📄 开源协议

本项目采用 **MIT License** 开源协议 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

感谢以下开源项目：

<table>
<tr>
<td align="center" width="25%">
<a href="https://langchain.com/">
<img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain"/>
</a><br>
<b>RAG 框架</b>
</td>
<td align="center" width="25%">
<a href="https://openai.com/">
<img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI"/>
</a><br>
<b>GPT & Embeddings</b>
</td>
<td align="center" width="25%">
<a href="https://fastapi.tiangolo.com/">
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
</a><br>
<b>Python Web 框架</b>
</td>
<td align="center" width="25%">
<a href="https://reactjs.org/">
<img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React"/>
</a><br>
<b>前端框架</b>
</td>
</tr>
<tr>
<td align="center" width="25%">
<a href="https://www.trychroma.com/">
<img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=for-the-badge" alt="ChromaDB"/>
</a><br>
<b>向量数据库</b>
</td>
<td align="center" width="25%">
<a href="https://tailwindcss.com/">
<img src="https://img.shields.io/badge/Tailwind-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind"/>
</a><br>
<b>CSS 框架</b>
</td>
<td align="center" width="25%">
<a href="https://www.postgresql.org/">
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
</a><br>
<b>关系型数据库</b>
</td>
<td align="center" width="25%">
<a href="https://www.docker.com/">
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
</a><br>
<b>容器化平台</b>
</td>
</tr>
</table>

---

## 💬 支持与反馈

遇到问题或有建议？

- 📧 **提交 Issue**: [GitHub Issues](https://github.com/your-username/studypal/issues)
- 📚 **查看文档**: [测试指南 TESTING.md](./TESTING.md)
- 💭 **查找答案**: 浏览已有的 Issues

---

## 📸 界面预览

### 🏠 首页
精美的着陆页，突出展示三大核心功能模块

### 💬 聊天界面
AI 智能问答，来源追溯，Markdown 渲染，代码高亮

### 📅 DDL 面板
可视化截止日期追踪，统计面板，智能时间提示

---

<div align="center">

### 🎓 专为计算机系学生打造

**用 StudyPal，让学习更高效！ 📚🤖✨**

---

**如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！**

[![Star History](https://img.shields.io/github/stars/your-username/studypal?style=social)](https://github.com/your-username/studypal/stargazers)

</div>
