"""
RAG (Retrieval-Augmented Generation) service for intelligent Q&A
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
import uuid

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage

from ..models.conversation import Conversation, Message
from ..schemas.chat import ChatRequest, ChatResponse, SourceReference
from .embedding_service import embedding_service
from .note_service import note_service
from ..config import settings


class RAGService:
    """Service for RAG-based question answering"""

    def __init__(self):
        """Initialize RAG service"""
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize LLM"""
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS,
                openai_api_key=settings.OPENAI_API_KEY
            )

    def _get_conversation_history(
        self,
        db: Session,
        conversation_id: UUID,
        limit: int = 5
    ) -> List[Tuple[str, str]]:
        """
        Get recent conversation history

        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Number of recent messages to retrieve

        Returns:
            List of (role, content) tuples
        """
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(
            Message.created_at.desc()
        ).limit(limit * 2).all()

        # Reverse to get chronological order
        messages.reverse()

        return [(msg.role, msg.content) for msg in messages]

    def _format_chat_history(self, history: List[Tuple[str, str]]) -> List:
        """
        Format chat history for LangChain

        Args:
            history: List of (role, content) tuples

        Returns:
            List of LangChain message objects
        """
        formatted = []
        for role, content in history:
            if role == "user":
                formatted.append(HumanMessage(content=content))
            elif role == "assistant":
                formatted.append(AIMessage(content=content))
        return formatted

    def _retrieve_relevant_chunks(
        self,
        query: str,
        user_id: Optional[str] = None,
        k: int = None
    ) -> List[dict]:
        """
        Retrieve relevant note chunks using vector search

        Args:
            query: Search query
            user_id: User ID for filtering
            k: Number of results

        Returns:
            List of relevant chunks with metadata
        """
        k = k or settings.TOP_N

        filter_dict = {}
        if user_id:
            filter_dict["user_id"] = user_id

        try:
            results = embedding_service.similarity_search(
                query=query,
                k=k,
                filter=filter_dict if filter_dict else None
            )

            relevant_chunks = []
            for doc, score in results:
                # Only include chunks above similarity threshold
                if score <= settings.SIMILARITY_THRESHOLD:
                    relevant_chunks.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": float(score)
                    })

            return relevant_chunks

        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            return []

    def _build_rag_prompt(
        self,
        question: str,
        context_chunks: List[dict],
        chat_history: List[Tuple[str, str]]
    ) -> str:
        """
        Build RAG prompt with context and history

        Args:
            question: User question
            context_chunks: Retrieved context chunks
            chat_history: Conversation history

        Returns:
            Formatted prompt string
        """
        # Format context
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            title = chunk["metadata"].get("title", "Unknown")
            category = chunk["metadata"].get("category", "")
            content = chunk["content"]

            context_parts.append(
                f"【笔记 {i}】{title}" +
                (f" ({category})" if category else "") +
                f"\n{content}\n"
            )

        context = "\n".join(context_parts) if context_parts else "没有找到相关笔记内容。"

        # Format chat history
        history_str = ""
        if chat_history:
            history_parts = []
            for role, content in chat_history[-4:]:  # Last 4 messages
                prefix = "用户" if role == "user" else "助手"
                history_parts.append(f"{prefix}: {content}")
            history_str = "\n".join(history_parts)

        # Build full prompt
        prompt = f"""你是一个个人学习助手，专门帮助计算机专业学生学习和复习。你的任务是基于用户的笔记库回答问题。

**重要原则：**
1. 优先使用笔记中的内容回答问题
2. 如果笔记中没有相关信息，请明确告知用户，不要编造答案
3. 回答要详细、准确、有条理
4. 涉及代码时，给出具体示例
5. 使用中英文混合（技术术语用英文）

---

**相关笔记内容：**
{context}

---
"""

        if history_str:
            prompt += f"""**对话历史：**
{history_str}

---

"""

        prompt += f"""**用户问题：**
{question}

**请回答：**
"""

        return prompt

    async def answer_question(
        self,
        db: Session,
        chat_request: ChatRequest,
        user_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Answer a question using RAG

        Args:
            db: Database session
            chat_request: Chat request with question
            user_id: User ID

        Returns:
            Chat response with answer and sources
        """
        if not self.llm:
            raise ValueError("LLM not initialized. Please set OPENAI_API_KEY.")

        question = chat_request.question
        conversation_id = chat_request.conversation_id

        # Get or create conversation
        if conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            if not conversation:
                raise ValueError("Conversation not found")
        else:
            # Create new conversation
            conversation = Conversation(
                id=uuid.uuid4(),
                user_id=UUID(user_id) if user_id else None,
                title=question[:50] + ("..." if len(question) > 50 else "")
            )
            db.add(conversation)
            db.flush()

        # Retrieve relevant chunks
        relevant_chunks = self._retrieve_relevant_chunks(
            query=question,
            user_id=user_id,
            k=settings.TOP_N
        )

        # Get conversation history
        chat_history = []
        if conversation_id:
            chat_history = self._get_conversation_history(
                db=db,
                conversation_id=conversation.id,
                limit=5
            )

        # Build prompt
        prompt = self._build_rag_prompt(
            question=question,
            context_chunks=relevant_chunks,
            chat_history=chat_history
        )

        # Generate answer
        try:
            response = await self.llm.ainvoke(prompt)
            answer = response.content
        except Exception as e:
            print(f"Error generating answer: {e}")
            answer = "抱歉，我在生成回答时遇到了问题。请稍后再试。"

        # Save user message
        user_message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            role="user",
            content=question,
            sources=[]
        )
        db.add(user_message)

        # Prepare source references
        sources = []
        for chunk in relevant_chunks:
            note_id = chunk["metadata"].get("note_id")
            if note_id:
                try:
                    note = note_service.get_note(db, UUID(note_id))
                    if note:
                        sources.append(
                            SourceReference(
                                note_id=UUID(note_id),
                                title=note.title,
                                content_snippet=chunk["content"][:200],
                                relevance_score=chunk["score"]
                            )
                        )
                except Exception:
                    pass

        # Save assistant message with sources
        assistant_message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
            sources=[
                {
                    "note_id": str(src.note_id),
                    "title": src.title,
                    "content_snippet": src.content_snippet,
                    "relevance_score": src.relevance_score
                }
                for src in sources
            ]
        )
        db.add(assistant_message)

        db.commit()

        return ChatResponse(
            answer=answer,
            sources=sources,
            conversation_id=conversation.id
        )

    def get_conversation(
        self,
        db: Session,
        conversation_id: UUID,
        user_id: Optional[str] = None
    ) -> Optional[Conversation]:
        """Get a conversation by ID"""
        query = db.query(Conversation).filter(Conversation.id == conversation_id)

        if user_id:
            query = query.filter(Conversation.user_id == UUID(user_id))

        return query.first()

    def get_conversations(
        self,
        db: Session,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Conversation], int]:
        """
        Get conversations list

        Returns:
            Tuple of (conversations, total_count)
        """
        query = db.query(Conversation)

        if user_id:
            query = query.filter(Conversation.user_id == UUID(user_id))

        total = query.count()
        conversations = query.order_by(
            Conversation.updated_at.desc()
        ).offset(skip).limit(limit).all()

        return conversations, total

    def delete_conversation(
        self,
        db: Session,
        conversation_id: UUID,
        user_id: Optional[str] = None
    ) -> bool:
        """Delete a conversation"""
        query = db.query(Conversation).filter(Conversation.id == conversation_id)

        if user_id:
            query = query.filter(Conversation.user_id == UUID(user_id))

        conversation = query.first()
        if not conversation:
            return False

        db.delete(conversation)
        db.commit()
        return True


# Global instance
rag_service = RAGService()
