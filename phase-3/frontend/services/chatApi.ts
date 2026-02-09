/**
 * Chat API client for Phase 3 frontend.
 *
 * This module provides functions for interacting with the chat API.
 */

// Remove trailing slash from API_URL to prevent double slashes
const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, "");

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at?: string;
  sequence_number?: number;
}

export interface ChatResponse {
  response: string;
  conversation_id: number;
  tokens_used: number;
  error: boolean;
}

export interface HistoryResponse {
  messages: ChatMessage[];
  conversation_id: number | null;
  total_messages: number;
}

/**
 * Send a message to the chatbot
 */
export async function sendMessage(
  userId: string,
  message: string,
  token: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/chat/${userId}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to send message');
  }

  return response.json();
}

/**
 * Get conversation history
 */
export async function getHistory(
  userId: string,
  token: string,
  limit: number = 50,
  offset: number = 0
): Promise<HistoryResponse> {
  const response = await fetch(
    `${API_URL}/api/chat/${userId}/chat/history?limit=${limit}&offset=${offset}`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to get history');
  }

  return response.json();
}

/**
 * Start a new conversation
 */
export async function startNewConversation(
  userId: string,
  token: string
): Promise<{ conversation_id: number; message: string }> {
  const response = await fetch(`${API_URL}/api/chat/${userId}/chat/new`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to start new conversation');
  }

  return response.json();
}

/**
 * Logout and clear conversation data
 */
export async function logout(userId: string, token: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/chat/${userId}/logout`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to logout');
  }
}
