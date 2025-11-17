# StudyPal 测试指南

## 快速测试 RAG 问答系统

### 1. 启动应用

```bash
# 确保已配置 OPENAI_API_KEY
cd studypal
docker-compose up --build
```

等待所有服务启动完成：
- PostgreSQL: localhost:5432
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000

### 2. 上传测试笔记

我们已经在 `test_notes/` 目录准备了三个示例笔记：
- `xv6_page_table.md` - 操作系统（xv6页表机制）
- `tcp_handshake.md` - 计算机网络（TCP三次握手）
- `database_index.md` - 数据库系统（索引原理）

#### 方法一：使用 API 上传

```bash
cd test_notes

# 上传所有测试笔记
curl -X POST http://localhost:8000/api/notes/upload \
  -F "files=@xv6_page_table.md" \
  -F "files=@tcp_handshake.md" \
  -F "files=@database_index.md"
```

#### 方法二：使用 Python 脚本上传

```python
import requests

API_BASE = "http://localhost:8000"

files = [
    ('files', open('test_notes/xv6_page_table.md', 'rb')),
    ('files', open('test_notes/tcp_handshake.md', 'rb')),
    ('files', open('test_notes/database_index.md', 'rb')),
]

response = requests.post(f"{API_BASE}/api/notes/upload", files=files)
print(response.json())
```

### 3. 测试问答功能

访问 http://localhost:3000/chat

#### 测试问题示例

**操作系统相关**:
```
Q: xv6的页表是怎么工作的？
Q: walk()函数的作用是什么？
Q: RISC-V使用几级页表？
Q: 什么是TLB？
Q: 页表项PTE包含哪些标志位？
```

**计算机网络相关**:
```
Q: TCP三次握手的过程是什么？
Q: 为什么需要三次握手而不是两次？
Q: TIME_WAIT状态的作用是什么？
Q: SYN洪水攻击是什么？
Q: 四次挥手的详细过程
```

**数据库相关**:
```
Q: B+Tree索引和B-Tree索引的区别
Q: 什么情况下索引会失效？
Q: 什么是覆盖索引？
Q: 聚簇索引和非聚簇索引的区别
Q: 如何优化数据库查询？
```

**跨领域问题**:
```
Q: 我有哪些关于操作系统的笔记？
Q: 总结一下我学习的所有内容
Q: 页表和索引有什么相似之处？
```

### 4. 验证功能

#### ✅ 检查点 1: 笔记上传成功
```bash
# 查看所有笔记
curl http://localhost:8000/api/notes
```

预期结果：返回3条笔记记录

#### ✅ 检查点 2: 向量检索工作
```bash
# 测试语义搜索
curl "http://localhost:8000/api/notes/search?query=页表机制&k=3"
```

预期结果：返回与"页表机制"相关的笔记片段，并包含相关性评分

#### ✅ 检查点 3: RAG 问答工作
```bash
# 测试问答
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "xv6的页表是怎么工作的？"
  }'
```

预期结果：
- 返回基于笔记内容的回答
- 包含来源引用（sources）
- 创建新的conversation_id

#### ✅ 检查点 4: 对话历史保存
```bash
# 继续同一个对话
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "walk函数的作用是什么？",
    "conversation_id": "<上一步返回的conversation_id>"
  }'
```

预期结果：
- 回答会考虑对话历史
- conversation_id 保持不变

#### ✅ 检查点 5: 前端聊天界面
1. 访问 http://localhost:3000/chat
2. 提问："xv6的页表是怎么工作的？"
3. 检查：
   - ✅ 消息显示正确
   - ✅ 回答使用 Markdown 格式渲染
   - ✅ 代码块有语法高亮
   - ✅ 右侧显示来源引用
   - ✅ 对话保存到左侧历史

## API 测试详解

### 测试笔记上传

```bash
# 测试单个文件上传
curl -X POST http://localhost:8000/api/notes/upload \
  -F "files=@test_notes/xv6_page_table.md"

# 预期响应
{
  "note_ids": ["uuid-here"],
  "success_count": 1,
  "failed_count": 0,
  "errors": null
}
```

### 测试笔记列表

```bash
# 获取所有笔记
curl http://localhost:8000/api/notes

# 分页查询
curl "http://localhost:8000/api/notes?page=1&limit=10"

# 按类别筛选
curl "http://localhost:8000/api/notes?category=操作系统"
```

### 测试语义搜索

```bash
# 搜索页表相关内容
curl "http://localhost:8000/api/notes/search?query=页表的工作原理&k=5"

# 预期响应
[
  {
    "note": {
      "id": "uuid",
      "title": "xv6_page_table.md",
      "content": "...",
      ...
    },
    "content_snippet": "xv6 使用 RISC-V 架构的页表机制...",
    "score": 0.15
  },
  ...
]
```

### 测试对话管理

```bash
# 开始新对话
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是TCP三次握手？"}'

# 继续对话
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "TIME_WAIT状态有什么用？",
    "conversation_id": "conversation-uuid"
  }'

# 查看所有对话
curl http://localhost:8000/api/chat/conversations

# 查看特定对话的消息
curl http://localhost:8000/api/chat/conversations/{conversation_id}

# 删除对话
curl -X DELETE http://localhost:8000/api/chat/conversations/{conversation_id}
```

## 性能测试

### 1. 向量检索性能

```bash
# 测试检索延迟
time curl "http://localhost:8000/api/notes/search?query=页表机制&k=5"
```

预期：< 500ms

### 2. RAG 问答性能

```bash
# 测试完整问答延迟（不含LLM生成时间）
time curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "xv6的页表是怎么工作的？"}'
```

预期：< 3秒（不含LLM）

### 3. 批量上传测试

```bash
# 上传多个文件
for file in test_notes/*.md; do
  curl -X POST http://localhost:8000/api/notes/upload -F "files=@$file"
done
```

## 问题排查

### 问题 1: 上传失败

**症状**: `Failed to generate answer`

**检查**:
```bash
# 检查 OPENAI_API_KEY 是否设置
docker-compose exec backend env | grep OPENAI_API_KEY

# 查看后端日志
docker-compose logs backend
```

### 问题 2: 向量搜索无结果

**症状**: 搜索返回空数组

**检查**:
```bash
# 检查笔记是否上传成功
curl http://localhost:8000/api/notes

# 检查 ChromaDB 是否正常
ls -la chroma_db/
```

### 问题 3: RAG 回答不准确

**原因**:
- 检索到的上下文不相关
- 提示词需要优化
- 相似度阈值设置不当

**调整**:
编辑 `backend/.env`:
```env
# 调整检索数量
TOP_K=20
TOP_N=5

# 调整相似度阈值
SIMILARITY_THRESHOLD=0.7

# 调整文本分块大小
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 问题 4: 前端无法连接后端

**检查**:
```bash
# 测试后端健康状态
curl http://localhost:8000/health

# 检查CORS配置
# 编辑 backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 数据库检查

### 查看数据库内容

```bash
# 连接到 PostgreSQL
docker-compose exec postgres psql -U studypal_user -d studypal_db

# 查看笔记表
SELECT id, title, category, created_at FROM notes;

# 查看分块表
SELECT note_id, chunk_index, length(content) FROM note_chunks;

# 查看对话表
SELECT id, title, created_at FROM conversations;

# 查看消息表
SELECT conversation_id, role, left(content, 50) FROM messages;
```

## 自动化测试脚本

### Python 完整测试脚本

```python
#!/usr/bin/env python3
"""
StudyPal 自动化测试脚本
"""
import requests
import time

API_BASE = "http://localhost:8000"

def test_upload():
    """测试笔记上传"""
    print("🧪 测试笔记上传...")
    files = [
        ('files', open('test_notes/xv6_page_table.md', 'rb')),
        ('files', open('test_notes/tcp_handshake.md', 'rb')),
        ('files', open('test_notes/database_index.md', 'rb')),
    ]
    response = requests.post(f"{API_BASE}/api/notes/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data['success_count'] == 3
    print(f"✅ 上传成功: {data['success_count']} 个文件")
    return data['note_ids']

def test_search():
    """测试语义搜索"""
    print("\n🧪 测试语义搜索...")
    response = requests.get(f"{API_BASE}/api/notes/search?query=页表机制&k=3")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    print(f"✅ 搜索成功: 找到 {len(results)} 个结果")
    for i, result in enumerate(results[:3], 1):
        print(f"  {i}. {result['note']['title']} (score: {result['score']:.3f})")

def test_chat():
    """测试RAG问答"""
    print("\n🧪 测试RAG问答...")
    questions = [
        "xv6的页表是怎么工作的？",
        "TCP三次握手的过程是什么？",
        "B+Tree索引有什么特点？"
    ]

    conversation_id = None
    for i, question in enumerate(questions, 1):
        print(f"\n  问题 {i}: {question}")
        payload = {"question": question}
        if conversation_id:
            payload["conversation_id"] = conversation_id

        start = time.time()
        response = requests.post(f"{API_BASE}/api/chat/ask", json=payload)
        elapsed = time.time() - start

        assert response.status_code == 200
        data = response.json()
        conversation_id = data['conversation_id']

        print(f"  ⏱️  耗时: {elapsed:.2f}秒")
        print(f"  📝 回答: {data['answer'][:100]}...")
        print(f"  📚 来源: {len(data['sources'])} 个笔记")

def test_conversations():
    """测试对话历史"""
    print("\n🧪 测试对话历史...")
    response = requests.get(f"{API_BASE}/api/chat/conversations")
    assert response.status_code == 200
    data = response.json()
    print(f"✅ 获取对话列表成功: {data['total']} 个对话")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 StudyPal 自动化测试")
    print("=" * 60)

    try:
        test_upload()
        time.sleep(2)  # 等待索引
        test_search()
        test_chat()
        test_conversations()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
```

运行测试：
```bash
python test_studypal.py
```

## 评估 RAG 系统质量

### 1. 检索质量评估

- ✅ 检索到的内容与问题相关
- ✅ 相关性评分合理（通常 < 0.5 表示相关）
- ✅ Top-K 结果覆盖问题的不同方面

### 2. 回答质量评估

- ✅ 回答准确，基于笔记内容
- ✅ 没有幻觉（编造不存在的信息）
- ✅ 引用来源正确
- ✅ 格式清晰，易于阅读

### 3. 用户体验评估

- ✅ 响应时间 < 3秒
- ✅ 界面流畅，无卡顿
- ✅ 对话历史正确保存
- ✅ 来源引用可点击查看

## 下一步

1. **添加更多笔记**: 上传你自己的课程笔记
2. **测试各种问题**: 尝试不同类型的问题
3. **调整参数**: 优化检索和生成参数
4. **部署生产**: 使用真实的数据库和环境
