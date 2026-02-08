'use client'

import { useEffect, useRef, useState } from 'react'
import { sendMessage, getHistory, startNewConversation } from '@/lib/chatApi'

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at?: string
}

interface ChatWindowProps {
  userId: string
  token: string
  onClose?: () => void
  onTasksChanged?: () => void
}

export default function ChatWindow({ userId, token, onClose, onTasksChanged }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [conversationId, setConversationId] = useState<number | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load conversation history on mount
  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const history = await getHistory(userId, token)
      setMessages(history.messages)
      setConversationId(history.conversation_id)
    } catch (err) {
      console.error('Failed to load history:', err)
      // Don't show error for empty history
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = inputValue.trim()
    setInputValue('')
    setError(null)

    // Add user message to UI immediately
    const newUserMessage: Message = {
      role: 'user',
      content: userMessage,
    }
    setMessages((prev) => [...prev, newUserMessage])
    setIsLoading(true)

    try {
      // Send message to API
      const response = await sendMessage(userId, userMessage, token)

      // Add assistant response to UI
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
      }
      setMessages((prev) => [...prev, assistantMessage])
      setConversationId(response.conversation_id)

      // Refresh tasks after successful chat response
      if (onTasksChanged) {
        try {
          await onTasksChanged();
        } catch (err) {
          console.error('Failed to refresh tasks:', err);
          // Don't show error to user - chat still succeeded
        }
      }

      if (response.error) {
        setError('The assistant encountered an error. Please try again.')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
      // Remove the optimistic user message on error
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleNewConversation = async () => {
    try {
      await startNewConversation(userId, token)
      setMessages([])
      setConversationId(null)
      setError(null)
    } catch (err) {
      setError('Failed to start new conversation')
    }
  }

  return (
    <div className="flex flex-col h-full w-full bg-white shadow-lg rounded-lg overflow-hidden">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 flex justify-between items-center flex-shrink-0">
        <div>
          <h1 className="text-xl font-bold">Todo AI Assistant</h1>
          <p className="text-sm text-blue-100">
            {conversationId ? `Conversation #${conversationId}` : 'New conversation'}
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleNewConversation}
            className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            New Chat
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="bg-blue-700 hover:bg-blue-800 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
              aria-label="Close chat"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-messages min-h-0">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg font-medium mb-2">Welcome to Todo AI Assistant!</p>
            <p className="text-sm">
              Try saying things like:
            </p>
            <ul className="text-sm mt-2 space-y-1">
              <li>&quot;Add buy groceries to my list&quot;</li>
              <li>&quot;Show me my tasks&quot;</li>
              <li>&quot;Mark the first task as done&quot;</li>
            </ul>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap break-words">{message.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce-dot"></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce-dot"
                  style={{ animationDelay: '0.2s' }}
                ></div>
                <div
                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce-dot"
                  style={{ animationDelay: '0.4s' }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <p className="text-sm">{error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4 flex-shrink-0 bg-white">
        <div className="flex space-x-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-medium transition-colors self-end"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
