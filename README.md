# StudyPal - AI Personal Learning Assistant

> An intelligent, all-in-one learning companion designed specifically for Computer Science students to **manage course notes**, **get AI-powered answers**, and **track assignment deadlines**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)

---

## 📚 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Complete API Documentation](#-complete-api-documentation)
- [Usage Guide](#-usage-guide)
- [Architecture](#-architecture)
- [Database Schema](#-database-schema)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Roadmap](#-roadmap)

---

## ✨ Features

### 🎯 Three Core Modules (All Completed!)

#### 📚 **1. Smart Note Management**
- **Upload & Organize**: Support for `.md`, `.txt`, `.py`, `.cpp`, `.java`, `.js`, `.ts`, and more
- **Automatic Indexing**: Files are automatically chunked and vectorized for semantic search
- **Vector Search**: Find relevant notes using natural language queries
- **Metadata Management**: Categories and tags for easy organization
- **Full CRUD**: Create, read, update, and delete notes

#### 🤖 **2. AI Q&A Assistant (RAG)**
- **Intelligent Answers**: Ask questions and get answers based on YOUR notes
- **Source Attribution**: Every answer shows which notes it came from
- **Multi-turn Conversations**: Context-aware dialogue with conversation history
- **Markdown Rendering**: Beautiful formatting with code syntax highlighting
- **Relevance Scoring**: See how confident the AI is about each source

#### 📅 **3. Deadline Tracker**
- **DDL Management**: Track assignments, exams, and project deadlines
- **Priority Levels**: Mark tasks as low/medium/high priority
- **Smart Views**: Filter by upcoming (7 days), overdue, or completed
- **Visual Dashboard**: 5 statistics cards showing key metrics
- **Time Indicators**: Smart time display (e.g., "还剩 2天", "逾期 3天")
- **One-click Complete**: Mark tasks done with a single click

### 🔥 Technical Highlights

- ⚡ **RAG (Retrieval-Augmented Generation)**: Combines vector search + GPT for accurate answers
- 🗄️ **Vector Database**: ChromaDB for efficient semantic similarity search
- 🧠 **LLM Integration**: OpenAI GPT-3.5-turbo for intelligent responses
- 🐳 **Docker Support**: One-command deployment with `docker-compose up`
- 🎨 **Modern UI**: Beautiful, responsive interface built with Tailwind CSS
- 📊 **Real-time Updates**: React Query for automatic cache invalidation
- 🔍 **Full-text Search**: Combine vector and keyword search for best results

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 14+
- **Vector Store**: ChromaDB
- **AI/ML**: LangChain + OpenAI (GPT-3.5-turbo, text-embedding-3-small)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic 2.5+

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3.4
- **State Management**: React Query (TanStack Query)
- **Routing**: React Router v6
- **UI Components**: Lucide Icons
- **Markdown**: react-markdown + react-syntax-highlighter

### DevOps
- **Containerization**: Docker + Docker Compose
- **Database**: PostgreSQL with persistent volumes
- **File Storage**: Local filesystem (expandable to S3)

---

## 🚀 Quick Start

### Prerequisites
- **Docker** & **Docker Compose** installed
- **OpenAI API Key** (get one at https://platform.openai.com/)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/studypal.git
cd studypal
```

### 2. Configure Environment Variables
```bash
# Edit backend/.env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Start All Services
```bash
docker-compose up --build
```

Wait for all services to start (about 2-3 minutes on first run):
- ✅ **PostgreSQL**: localhost:5432
- ✅ **Backend API**: http://localhost:8000
- ✅ **Frontend**: http://localhost:3000

### 4. Access the Application
- **Frontend UI**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

### 5. Upload Sample Notes
```bash
cd test_notes
curl -X POST http://localhost:8000/api/notes/upload \
  -F "files=@xv6_page_table.md" \
  -F "files=@tcp_handshake.md" \
  -F "files=@database_index.md"
```

### 6. Start Asking Questions!
Visit http://localhost:3000/chat and ask:
- "xv6的页表是怎么工作的？"
- "TCP三次握手的过程是什么？"
- "B+Tree索引有什么特点？"

---

## 📖 Complete API Documentation

### 📚 Notes API (6 endpoints)

#### Upload Notes
```http
POST /api/notes/upload
Content-Type: multipart/form-data

files: file1.md, file2.py, file3.cpp...
```

#### List Notes
```http
GET /api/notes?category=操作系统&tags=xv6,RISC-V&page=1&limit=20
```

#### Get Specific Note
```http
GET /api/notes/{note_id}
```

#### Update Note
```http
PUT /api/notes/{note_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "category": "数据库",
  "tags": ["SQL", "索引", "B+Tree"]
}
```

#### Delete Note
```http
DELETE /api/notes/{note_id}
```

#### Semantic Search
```http
GET /api/notes/search?query=页表是如何工作的&k=5
```

### 💬 Chat API (5 endpoints)

#### Ask Question
```http
POST /api/chat/ask
Content-Type: application/json

{
  "question": "xv6的页表是怎么工作的？",
  "conversation_id": "optional-uuid"
}

Response:
{
  "answer": "xv6 使用 RISC-V 的三级页表...",
  "sources": [
    {
      "note_id": "uuid",
      "title": "xv6_page_table.md",
      "content_snippet": "...",
      "relevance_score": 0.15
    }
  ],
  "conversation_id": "uuid"
}
```

#### List Conversations
```http
GET /api/chat/conversations?page=1&limit=20
```

#### Get Conversation with Messages
```http
GET /api/chat/conversations/{conversation_id}
```

#### Update Conversation Title
```http
PUT /api/chat/conversations/{conversation_id}/title?title=New Title
```

#### Delete Conversation
```http
DELETE /api/chat/conversations/{conversation_id}
```

### 📅 Deadlines API (9 endpoints)

#### Create Deadline
```http
POST /api/deadlines
Content-Type: application/json

{
  "title": "数据库大作业",
  "course": "数据库系统",
  "due_date": "2024-12-25T23:59:00",
  "priority": "high",
  "description": "完成ER图设计和SQL实现"
}
```

#### List Deadlines
```http
GET /api/deadlines?status=pending&priority=high&from_date=2024-12-01
```

#### Get Upcoming Deadlines
```http
GET /api/deadlines/upcoming?days=7
```

#### Get Overdue Deadlines
```http
GET /api/deadlines/overdue
```

#### Get Statistics
```http
GET /api/deadlines/statistics

Response:
{
  "total": 15,
  "pending": 8,
  "completed": 5,
  "overdue": 2,
  "upcoming_7days": 4
}
```

#### Get Specific Deadline
```http
GET /api/deadlines/{deadline_id}
```

#### Update Deadline
```http
PUT /api/deadlines/{deadline_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "priority": "medium"
}
```

#### Mark as Complete
```http
PATCH /api/deadlines/{deadline_id}/complete
```

#### Delete Deadline
```http
DELETE /api/deadlines/{deadline_id}
```

**📘 Full Interactive API Docs**: http://localhost:8000/docs (Swagger UI)

---

## 📖 Usage Guide

### Module 1️⃣: Note Management

#### Upload Your First Note

1. **Visit** http://localhost:3000 and click "Manage Notes"
2. **Drag & drop** or click to select files:
   - Supported: `.md`, `.txt`, `.py`, `.cpp`, `.c`, `.java`, `.js`, `.ts`
   - Max size: 10MB per file, 100MB total
3. **Wait** for processing (chunking + embedding generation)
4. **Success!** Your notes are now searchable

#### Search Your Notes

**Semantic Search** (understanding meaning):
```
Query: "如何实现页表转换"
→ Finds notes about page tables, address translation, walk()
```

**Keyword Search** (exact matches):
```
Query: "PTE_V"
→ Finds exact occurrences of this flag
```

---

### Module 2️⃣: AI Q&A Assistant

#### Start a Conversation

1. **Navigate** to http://localhost:3000/chat
2. **Ask** your question in Chinese or English:
   ```
   "xv6的页表是怎么工作的？"
   "Explain TCP three-way handshake"
   "B+Tree和B-Tree的区别是什么？"
   ```
3. **View** the AI's answer with source references
4. **Click** on sources to see which notes were used

#### Example Questions

**Operating Systems:**
- "xv6的walk()函数如何遍历页表？"
- "RISC-V使用几级页表？每级多少条目？"
- "TLB是什么？为什么需要它？"

**Computer Networks:**
- "为什么需要三次握手而不是两次？"
- "TIME_WAIT状态的作用是什么？"
- "SYN洪水攻击如何防御？"

**Databases:**
- "聚簇索引和非聚簇索引的区别"
- "什么情况下索引会失效？"
- "如何选择合适的索引前缀长度？"

**Cross-domain:**
- "我有哪些关于操作系统的笔记？"
- "总结一下我学习的所有内容"

#### Tips for Better Answers

✅ **Good**: Specific questions with context
- "xv6中walk()函数的参数alloc的作用是什么？"

❌ **Poor**: Vague questions
- "页表怎么用？"

---

### Module 3️⃣: Deadline Tracker

#### Add Your First DDL

1. **Navigate** to http://localhost:3000/deadlines
2. **Click** "添加 DDL" button
3. **Fill** the form:
   - **Title**: "数据库大作业" (required)
   - **Course**: "数据库系统" (optional)
   - **Due Date**: Select date & time (required)
   - **Priority**: High/Medium/Low
   - **Description**: Task details (optional)
4. **Submit** and see it in the list!

#### Manage Your DDLs

**View Modes:**
- **全部待办**: All pending tasks
- **即将到期**: Due within 7 days
- **已逾期**: Overdue tasks (red background!)
- **已完成**: Completed tasks

**Quick Actions:**
- ✅ **Complete**: Click checkbox
- 🗑️ **Delete**: Click trash icon (with confirmation)
- 📊 **Statistics**: View dashboard at top

**Visual Indicators:**
- 🔴 **High Priority**: Red badge
- 🟡 **Medium Priority**: Yellow badge
- 🟢 **Low Priority**: Green badge
- ⏰ **Time Display**:
  - "还剩 2小时" → Orange (urgent!)
  - "还剩 3天" → Yellow (soon)
  - "逾期 2天" → Red (overdue!)

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      StudyPal System                         │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐                  ┌──────────────┐
│   Frontend   │ ←── HTTP/JSON ──→│   Backend    │
│  React + TS  │                  │   FastAPI    │
└──────────────┘                  └──────┬───────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
            ┌───────▼────────┐  ┌────────▼───────┐  ┌────────▼────────┐
            │  PostgreSQL    │  │    ChromaDB    │  │  OpenAI API     │
            │  (Metadata)    │  │   (Vectors)    │  │  (LLM + Embed)  │
            └────────────────┘  └────────────────┘  └─────────────────┘
```

### RAG Pipeline

```
📝 User Question
    ↓
🔍 Generate Query Embedding (OpenAI)
    ↓
🗄️ Vector Similarity Search (ChromaDB)
    ↓ TOP_K=20
📊 Filter by Similarity Threshold (0.7)
    ↓ TOP_N=5
📚 Retrieve Note Chunks
    ↓
🤖 Build Prompt (System + Context + History + Question)
    ↓
💬 Generate Answer (GPT-3.5-turbo)
    ↓
📤 Return Answer + Sources
```

### Data Flow

```
Notes Upload:
User → Frontend → API → Service → Database
                               ↓
                         Text Splitter
                               ↓
                      Embedding Service
                               ↓
                          ChromaDB

RAG Q&A:
User → Frontend → API → RAG Service
                           ↓
                    1. Retrieve Context (ChromaDB)
                    2. Format Prompt
                    3. Call LLM (OpenAI)
                    4. Save Conversation
                           ↓
                       Database
```

---

## 🗄️ Database Schema

### Complete Entity-Relationship Diagram

```
┌─────────────┐
│    users    │
├─────────────┤
│ id (PK)     │
│ username    │
│ email       │
│ password    │
└──────┬──────┘
       │
       │ (1:N)
       │
┌──────▼──────────┐     ┌─────────────────┐
│     notes       │────→│  note_chunks    │
├─────────────────┤ 1:N ├─────────────────┤
│ id (PK)         │     │ id (PK)         │
│ user_id (FK)    │     │ note_id (FK)    │
│ title           │     │ chunk_index     │
│ file_type       │     │ content         │
│ file_path       │     │ vector_id       │
│ content         │     │ created_at      │
│ category        │     └─────────────────┘
│ tags (JSONB)    │
│ created_at      │
│ updated_at      │
└─────────────────┘

┌──────▼──────────────┐     ┌─────────────────┐
│  conversations      │────→│    messages     │
├─────────────────────┤ 1:N ├─────────────────┤
│ id (PK)             │     │ id (PK)         │
│ user_id (FK)        │     │ conversation_id │
│ title               │     │ role            │
│ created_at          │     │ content         │
│ updated_at          │     │ sources (JSONB) │
└─────────────────────┘     │ created_at      │
                            └─────────────────┘

┌──────▼──────────┐
│   deadlines     │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ title           │
│ course          │
│ description     │
│ due_date        │
│ priority        │
│ status          │
│ reminder_sent   │
│ created_at      │
│ updated_at      │
└─────────────────┘
```

### Table Details

#### `notes`
- **Purpose**: Store uploaded note files and metadata
- **Indexes**: `user_id`, `category`, `created_at`
- **Relationships**: 1:N with `note_chunks`

#### `note_chunks`
- **Purpose**: Store text chunks for vector search
- **Indexes**: `note_id`, `chunk_index`
- **Vector Storage**: `vector_id` references ChromaDB entry

#### `conversations`
- **Purpose**: Group chat messages into conversations
- **Indexes**: `user_id`, `updated_at`
- **Relationships**: 1:N with `messages`

#### `messages`
- **Purpose**: Store individual chat messages
- **JSONB Fields**: `sources` (note references)
- **Indexes**: `conversation_id`, `created_at`

#### `deadlines`
- **Purpose**: Track assignment and exam deadlines
- **Indexes**: `user_id`, `due_date`, `status`
- **Enums**: priority (low/medium/high), status (pending/completed)

---

## ⚙️ Configuration

### Backend Environment Variables

```env
# Application
APP_NAME=StudyPal - AI Learning Assistant
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Database
DATABASE_URL=postgresql://studypal_user:password@postgres:5432/studypal_db

# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo              # or gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
LLM_TEMPERATURE=0.5                     # 0.0-1.0 (higher = more creative)
LLM_MAX_TOKENS=2000

# Vector Search Configuration
VECTOR_DB=chroma
CHROMA_PERSIST_DIR=/app/chroma_db
SIMILARITY_THRESHOLD=0.7                # 0.0-1.0 (lower = stricter)
TOP_K=20                                # Initial retrieval count
TOP_N=5                                 # Final context chunks

# File Upload Configuration
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE_MB=10
MAX_UPLOAD_SIZE_MB=100
SUPPORTED_EXTENSIONS=.md,.txt,.cpp,.c,.py,.java,.js,.ts,.jsx,.tsx

# Text Processing
CHUNK_SIZE=1000                         # Characters per chunk
CHUNK_OVERLAP=200                       # Overlap between chunks

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Performance
CACHE_TTL_SECONDS=600
ENABLE_QUERY_CACHE=true
RATE_LIMIT_PER_MINUTE=60

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Tuning Tips

#### For Better Answer Quality
```env
LLM_TEMPERATURE=0.3          # More factual, less creative
TOP_N=7                       # More context
SIMILARITY_THRESHOLD=0.6      # Include more sources
```

#### For Faster Performance
```env
TOP_K=10                      # Fewer initial results
TOP_N=3                       # Less context
CHUNK_SIZE=500                # Smaller chunks
```

#### For Longer Notes
```env
CHUNK_SIZE=1500               # Bigger chunks
CHUNK_OVERLAP=300             # More overlap
```

---

## 🧪 Testing

### Quick Test with Sample Notes

We provide 3 high-quality sample notes in `test_notes/`:

1. **xv6_page_table.md** - OS: xv6 page table mechanism
2. **tcp_handshake.md** - Networks: TCP handshake
3. **database_index.md** - Database: Index principles

```bash
# Upload samples
cd test_notes
curl -X POST http://localhost:8000/api/notes/upload \
  -F "files=@xv6_page_table.md" \
  -F "files=@tcp_handshake.md" \
  -F "files=@database_index.md"

# Test semantic search
curl "http://localhost:8000/api/notes/search?query=页表机制&k=3"

# Test RAG Q&A
curl -X POST http://localhost:8000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "xv6的页表是怎么工作的？"}'
```

### Comprehensive Testing Guide

See **[TESTING.md](./TESTING.md)** for:
- Complete test scenarios
- API testing examples
- Performance benchmarks
- Automated test scripts
- Quality evaluation metrics

---

## 🚢 Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` in backend/.env
- [ ] Use strong PostgreSQL password
- [ ] Set `DEBUG=false` in production
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Set up HTTPS/SSL certificates
- [ ] Use production-grade OpenAI API key
- [ ] Set up database backups
- [ ] Configure log rotation
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Implement rate limiting
- [ ] Add user authentication

### Docker Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f backend
```

### Manual Deployment

#### Backend
```bash
cd backend
pip install -r requirements.txt
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend
```bash
cd frontend
npm install
npm run build
# Serve dist/ with nginx or any static file server
```

---

## 🗺️ Roadmap

### ✅ Phase 1: Foundation (Completed)
- [x] Project structure setup
- [x] Database models (5 tables)
- [x] Docker configuration
- [x] FastAPI framework
- [x] React + TypeScript setup

### ✅ Phase 2: Note Management (Completed)
- [x] File upload with validation
- [x] Text chunking (RecursiveCharacterTextSplitter)
- [x] Vector embeddings (OpenAI)
- [x] ChromaDB integration
- [x] Semantic search API
- [x] CRUD operations

### ✅ Phase 3: RAG Q&A System (Completed)
- [x] RAG service implementation
- [x] Vector retrieval pipeline
- [x] LLM integration (GPT-3.5)
- [x] Conversation management
- [x] Chat interface with Markdown
- [x] Source attribution
- [x] Multi-turn dialogue

### ✅ Phase 4: DDL Management (Completed)
- [x] Deadline CRUD API
- [x] Priority and status management
- [x] Statistics dashboard
- [x] List views (upcoming, overdue, completed)
- [x] Visual time indicators
- [x] Responsive UI

### 🔜 Phase 5: Enhancement (Next)
- [ ] Auto-categorization with LLM
- [ ] Automatic tag extraction
- [ ] Query caching for performance
- [ ] Advanced analytics
- [ ] Unit and integration tests

### 🚀 Future Enhancements
- [ ] User authentication (JWT)
- [ ] Calendar view for deadlines
- [ ] Email/push notifications
- [ ] Knowledge graph visualization
- [ ] Learning progress analytics
- [ ] Note sharing and collaboration
- [ ] Mobile app (React Native)
- [ ] Offline mode support
- [ ] Multi-language support
- [ ] Voice input/output

---

## 📊 Project Statistics

- **Total Files**: 64+
- **Lines of Code**: 6,000+
- **API Endpoints**: 20
- **Database Tables**: 5
- **React Components**: 15+
- **Development Time**: 4 phases
- **Test Coverage**: Coming soon

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8
- **TypeScript**: Use ESLint configuration
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[LangChain](https://langchain.com/)** - RAG framework
- **[OpenAI](https://openai.com/)** - GPT and embeddings
- **[FastAPI](https://fastapi.tiangolo.com/)** - Python web framework
- **[React](https://reactjs.org/)** - Frontend framework
- **[ChromaDB](https://www.trychroma.com/)** - Vector database
- **[Tailwind CSS](https://tailwindcss.com/)** - Styling framework

---

## 📞 Support

For issues, questions, or suggestions:
- 📧 Open an issue on GitHub
- 📚 Check [TESTING.md](./TESTING.md) for testing guide
- 💬 Review existing issues for solutions

---

## 📸 Screenshots

### Homepage
Beautiful landing page with 3 core features highlighted.

### Chat Interface
AI-powered Q&A with source attribution and Markdown rendering.

### Deadlines Dashboard
Visual DDL tracking with statistics and smart time indicators.

---

**Made with ❤️ for Computer Science Students**

**Happy Learning with StudyPal! 📚🤖✨**
