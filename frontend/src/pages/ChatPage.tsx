import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MessageSquare, Plus, Trash2 } from 'lucide-react'
import chatService from '../services/chatService'
import { Conversation, Message, SourceReference } from '../types'
import MessageList from '../components/Chat/MessageList'
import MessageInput from '../components/Chat/MessageInput'
import SourcePanel from '../components/Chat/SourcePanel'

function ChatPage() {
  const queryClient = useQueryClient()
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [selectedSources, setSelectedSources] = useState<SourceReference[]>([])

  // Fetch conversations
  const { data: conversationsData } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => chatService.getConversations(),
  })

  // Fetch current conversation messages
  const { data: currentConversation, isLoading: isLoadingMessages } = useQuery({
    queryKey: ['conversation', currentConversationId],
    queryFn: () => chatService.getConversation(currentConversationId!),
    enabled: !!currentConversationId,
  })

  // Ask question mutation
  const askMutation = useMutation({
    mutationFn: (question: string) =>
      chatService.askQuestion({
        question,
        conversation_id: currentConversationId || undefined,
      }),
    onSuccess: (response) => {
      setCurrentConversationId(response.conversation_id)
      setSelectedSources(response.sources)
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      queryClient.invalidateQueries({ queryKey: ['conversation', response.conversation_id] })
    },
  })

  // Delete conversation mutation
  const deleteMutation = useMutation({
    mutationFn: (conversationId: string) => chatService.deleteConversation(conversationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      if (currentConversationId === conversationsData?.conversations.find(c => c.id === currentConversationId)?.id) {
        setCurrentConversationId(null)
      }
    },
  })

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return
    askMutation.mutate(message)
  }

  const handleNewConversation = () => {
    setCurrentConversationId(null)
    setSelectedSources([])
  }

  const handleDeleteConversation = (conversationId: string) => {
    if (window.confirm('确定要删除这个对话吗？')) {
      deleteMutation.mutate(conversationId)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <MessageSquare className="w-6 h-6 text-blue-600" />
              AI 学习助手
            </h1>
            <button
              onClick={handleNewConversation}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              新对话
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-12 gap-6 h-[calc(100vh-12rem)]">
          {/* Conversations Sidebar */}
          <div className="col-span-3 bg-white rounded-lg shadow-sm overflow-hidden flex flex-col">
            <div className="p-4 border-b">
              <h2 className="font-semibold text-gray-900">对话历史</h2>
            </div>
            <div className="flex-1 overflow-y-auto">
              {conversationsData?.conversations.length === 0 ? (
                <div className="p-4 text-center text-gray-500 text-sm">
                  还没有对话历史
                </div>
              ) : (
                <div className="divide-y">
                  {conversationsData?.conversations.map((conversation) => (
                    <div
                      key={conversation.id}
                      className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                        currentConversationId === conversation.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                      }`}
                      onClick={() => setCurrentConversationId(conversation.id)}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <h3 className="text-sm font-medium text-gray-900 truncate">
                            {conversation.title}
                          </h3>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(conversation.created_at).toLocaleDateString('zh-CN')}
                          </p>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteConversation(conversation.id)
                          }}
                          className="text-gray-400 hover:text-red-600 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Chat Area */}
          <div className="col-span-6 bg-white rounded-lg shadow-sm flex flex-col">
            <MessageList
              messages={currentConversation?.messages || []}
              isLoading={isLoadingMessages || askMutation.isPending}
            />
            <MessageInput
              onSendMessage={handleSendMessage}
              disabled={askMutation.isPending}
              placeholder="输入您的问题..."
            />
          </div>

          {/* Sources Panel */}
          <div className="col-span-3">
            <SourcePanel sources={selectedSources} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatPage
