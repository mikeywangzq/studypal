# StudyPal - AI Personal Learning Assistant

An intelligent learning assistant designed for Computer Science students to manage course notes, get AI-powered answers from their knowledge base, and track assignment deadlines.

## Features

### Core Features (MVP)
- **📚 Smart Note Management**: Upload and organize course notes, code snippets, and study materials with automatic categorization
- **🤖 AI Q&A Assistant**: Ask questions and get intelligent answers based on your personal knowledge base using RAG (Retrieval-Augmented Generation)
- **📅 Deadline Tracker**: Manage assignment and exam deadlines with calendar view and reminders
- **🔍 Semantic Search**: Search your notes using natural language queries

### Technical Highlights
- **Vector Database**: ChromaDB for efficient semantic search
- **LLM Integration**: OpenAI GPT for intelligent Q&A
- **Modern Stack**: FastAPI backend + React frontend
- **Docker Support**: One-command deployment with Docker Compose

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 14+
- **Vector Store**: ChromaDB
- **AI/ML**: LangChain + OpenAI (GPT-3.5-turbo, text-embedding-3-small)
- **ORM**: SQLAlchemy

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand + React Query

## Project Structure

```
studypal/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # SQLAlchemy models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   ├── utils/       # Helper functions
│   │   ├── config.py    # Configuration
│   │   ├── database.py  # Database setup
│   │   └── main.py      # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── services/    # API services
│   │   ├── types/       # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── vite.config.ts
├── docker-compose.yml   # Docker orchestration
├── uploads/             # Uploaded files storage
├── chroma_db/          # Vector database storage
└── README.md
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API Key (for AI features)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd studypal
```

### 2. Configure Environment Variables
Edit `backend/.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Start with Docker Compose
```bash
docker-compose up --build
```

This will start:
- **PostgreSQL**: localhost:5432
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

## Development Setup

### Backend Development

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. Run development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## API Documentation

### Notes Endpoints

#### Upload Notes
```http
POST /api/notes/upload
Content-Type: multipart/form-data

files: [file1.md, file2.py, ...]
```

#### Get All Notes
```http
GET /api/notes?category=操作系统&page=1&limit=20
```

#### Get Note by ID
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
  "tags": ["SQL", "索引"]
}
```

#### Delete Note
```http
DELETE /api/notes/{note_id}
```

#### Search Notes
```http
GET /api/notes/search?query=页表是如何工作的&k=5
```

For complete API documentation, visit http://localhost:8000/docs after starting the backend.

## Usage Guide

### 1. Upload Notes

1. Navigate to the Notes page
2. Click "Upload Notes" or drag & drop files
3. Supported formats: `.md`, `.txt`, `.py`, `.cpp`, `.c`, `.java`, `.js`, `.ts`
4. Files are automatically processed and indexed for search

### 2. Ask Questions

1. Navigate to the Chat page
2. Type your question in natural language
3. The AI will search your notes and provide answers with source references
4. Click on source references to view the original notes

### 3. Manage Deadlines

1. Navigate to the Deadlines page
2. Add assignments, exams, or project deadlines
3. View them in calendar or list view
4. Get reminders before due dates

## Configuration

### Environment Variables

#### Backend (`backend/.env`)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/studypal_db

# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Vector Store
CHROMA_PERSIST_DIR=/app/chroma_db
TOP_K=20
TOP_N=5

# File Upload
MAX_FILE_SIZE_MB=10
MAX_UPLOAD_SIZE_MB=100
SUPPORTED_EXTENSIONS=.md,.txt,.cpp,.c,.py,.java,.js,.ts

# Text Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

#### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Database Schema

### Notes Table
- `id`: UUID (Primary Key)
- `user_id`: UUID (Optional in MVP)
- `title`: String
- `file_type`: String (markdown, python, cpp, etc.)
- `file_path`: String
- `content`: Text
- `category`: String (操作系统, 网络, 数据库, etc.)
- `tags`: JSONB array
- `created_at`: Timestamp
- `updated_at`: Timestamp

### Note Chunks Table
- `id`: UUID (Primary Key)
- `note_id`: UUID (Foreign Key)
- `chunk_index`: Integer
- `content`: Text
- `vector_id`: String (ID in vector database)
- `created_at`: Timestamp

## Architecture

### RAG (Retrieval-Augmented Generation) Flow

1. **Indexing Phase** (when uploading notes):
   - User uploads a note file
   - Text is split into chunks (1000 chars with 200 overlap)
   - Each chunk is converted to embeddings using OpenAI
   - Embeddings are stored in ChromaDB with metadata

2. **Query Phase** (when asking questions):
   - User asks a question
   - Question is converted to embedding
   - Vector similarity search finds top-k relevant chunks
   - Retrieved chunks are sent to GPT as context
   - GPT generates answer based on the context
   - Sources are returned to the user

### Text Chunking Strategy
- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Splitter**: Recursive Character Text Splitter
- **Separators**: Double newline → Newline → Space

## Troubleshooting

### Backend won't start
- Check if PostgreSQL is running: `docker-compose ps`
- Check environment variables in `backend/.env`
- Check logs: `docker-compose logs backend`

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Check `VITE_API_BASE_URL` in frontend `.env`

### Vector search not working
- Ensure `OPENAI_API_KEY` is set correctly
- Check ChromaDB directory has write permissions
- Check logs for embedding errors

### File upload fails
- Check file size limits in config
- Ensure `uploads/` directory exists and is writable
- Verify file extension is supported

## Performance Tips

1. **Limit Note Size**: Keep notes under 10MB for faster processing
2. **Optimize Chunk Size**: Adjust `CHUNK_SIZE` based on your content
3. **Use Caching**: Enable query caching for repeated questions
4. **Index Management**: Periodically rebuild vector index for better performance

## Security Considerations

- **API Keys**: Never commit `.env` files with real API keys
- **File Upload**: Validate file types and sizes
- **CORS**: Configure allowed origins in production
- **Database**: Use strong passwords and restrict access
- **Authentication**: Implement user authentication for production use

## Roadmap

### Phase 1 ✅ (Completed)
- Project structure setup
- Database models
- Docker configuration
- Basic FastAPI framework
- React frontend setup

### Phase 2 ✅ (Completed)
- Note upload and storage
- Text chunking and embeddings
- Vector database integration
- Notes API endpoints

### Phase 3 (In Progress)
- RAG Q&A system
- Conversation history
- Chat interface

### Phase 4 (Planned)
- DDL management API
- Calendar view
- Reminder system

### Phase 5 (Planned)
- Auto-categorization with LLM
- Tag extraction
- Performance optimization
- Testing and documentation

### Future Enhancements
- User authentication (JWT)
- Knowledge graph visualization
- Learning analytics
- Mobile app
- Collaboration features

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- **LangChain**: For RAG framework
- **OpenAI**: For embeddings and LLM
- **FastAPI**: For the amazing Python web framework
- **React**: For the frontend framework

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the FAQ section
- Review existing issues for solutions

---

**Happy Learning with StudyPal! 📚🤖**
