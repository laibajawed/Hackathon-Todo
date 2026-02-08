'use client'

import { useEffect, useState } from 'react'
import ChatWindow from '@/components/ChatWindow'

export default function ChatPage() {
  const [userId, setUserId] = useState<string | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Get authentication from localStorage (Phase 2 auth system)
    const storedToken = localStorage.getItem('auth_token')
    const storedUserId = localStorage.getItem('user_id')

    if (storedToken && storedUserId) {
      setUserId(storedUserId)
      setToken(storedToken)
    }
    setIsLoading(false)
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!userId || !token) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Authentication Required
          </h1>
          <p className="text-gray-600 mb-4">
            Please log in to use the chat interface.
          </p>
          <a
            href="/auth/signin"
            className="inline-block bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
          >
            Go to Login
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen w-screen overflow-hidden">
      <ChatWindow userId={userId} token={token} />
    </div>
  )
}
