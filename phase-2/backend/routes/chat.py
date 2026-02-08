"""Chat API routes for Phase 3: Todo AI Chatbot

This module provides the chat endpoint for conversational task management.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user, validate_user_access
from database import get_session
from models import Conversation, Message, MessageRole
from utils.tokens import count_tokens

router = APIRouter(tags=["chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=2000, description="User message")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="Assistant's response")
    conversation_id: int = Field(..., description="Conversation ID")
    tokens_used: int = Field(default=0, description="Tokens used in this exchange")
    error: bool = Field(default=False, description="Whether an error occurred")


class HistoryResponse(BaseModel):
    """Response model for conversation history."""

    messages: List[dict] = Field(..., description="List of messages")
    conversation_id: Optional[int] = Field(None, description="Active conversation ID")
    total_messages: int = Field(..., description="Total message count")


class NewConversationResponse(BaseModel):
    """Response model for new conversation creation."""

    conversation_id: int = Field(..., description="New conversation ID")
    message: str = Field(..., description="Success message")


# Helper Functions
async def get_active_conversation(
    session: AsyncSession, user_id: int
) -> Optional[Conversation]:
    """Get the active conversation for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Active Conversation or None
    """
    statement = select(Conversation).where(
        Conversation.user_id == user_id, Conversation.is_active == True
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def create_conversation(session: AsyncSession, user_id: int) -> Conversation:
    """Create a new conversation for a user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        New Conversation instance
    """
    conversation = Conversation(
        user_id=user_id,
        title="New Conversation",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=True,
        total_tokens=0,
        message_count=0,
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


async def add_message(
    session: AsyncSession,
    conversation_id: int,
    role: MessageRole,
    content: str,
    token_count: int = 0,
) -> Message:
    """Add a message to a conversation.

    Args:
        session: Database session
        conversation_id: Conversation ID
        role: Message role (user/assistant/system)
        content: Message content
        token_count: Estimated token count

    Returns:
        New Message instance
    """
    # Get next sequence number
    count_statement = select(func.count(Message.id)).where(
        Message.conversation_id == conversation_id
    )
    result = await session.execute(count_statement)
    sequence_number = result.scalar_one()

    # Create message
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        token_count=token_count,
        created_at=datetime.utcnow(),
        sequence_number=sequence_number,
    )
    session.add(message)

    # Update conversation metadata
    conversation_statement = select(Conversation).where(
        Conversation.id == conversation_id
    )
    conv_result = await session.execute(conversation_statement)
    conversation = conv_result.scalar_one()

    conversation.message_count += 1
    conversation.total_tokens += token_count
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)

    await session.commit()
    await session.refresh(message)
    return message


# Endpoints
@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Send a message to the AI chatbot.

    This endpoint processes user messages, invokes the AI agent with function tools,
    and returns the assistant's response.

    Args:
        user_id: User ID from URL path
        request: Chat request with user message
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        ChatResponse with assistant's reply and metadata
    """
    # Validate user access
    await validate_user_access(user_id, current_user)

    # Get or create active conversation
    conversation = await get_active_conversation(session, current_user["user_id"])
    if not conversation:
        conversation = await create_conversation(session, current_user["user_id"])

    # Get conversation history for context
    history_statement = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.sequence_number)
        .limit(50)  # Last 50 messages for context
    )
    history_result = await session.execute(history_statement)
    history_messages = history_result.scalars().all()

    # Format history for agent
    conversation_history = [
        {"role": msg.role.value, "content": msg.content}
        for msg in history_messages
    ]

    # Save user message with token count
    user_token_count = count_tokens(request.message)
    user_message = await add_message(
        session, conversation.id, MessageRole.USER, request.message, token_count=user_token_count
    )

    # Run agent with function tools
    try:
        from agent.runner import create_agent, run_agent
        from tools.user_context_tools import (
            set_user_context,
            create_task,
            delete_task,
            list_tasks,
            toggle_task_status,
            update_task,
        )

        # Set user context for this request
        set_user_context(str(current_user["user_id"]))

        # Create agent with context-aware function tools
        agent = create_agent(
            tools=[
                create_task,
                delete_task,
                list_tasks,
                toggle_task_status,
                update_task,
            ]
        )

        # Run agent with user message and conversation history
        agent_result = await run_agent(
            agent=agent,
            user_message=request.message,
            conversation_history=conversation_history,
        )

        assistant_response = agent_result["response"]
        tokens_used = agent_result.get("tokens_used", 0)
        error_occurred = agent_result.get("error", False)

        # If no token count from agent, estimate it
        if tokens_used == 0:
            tokens_used = count_tokens(assistant_response)

    except Exception as e:
        # Handle agent execution errors
        import logging
        logging.error(f"Agent execution failed: {e}", exc_info=True)

        assistant_response = "I'm having trouble processing your request right now. Please try again in a moment."
        tokens_used = count_tokens(assistant_response)
        error_occurred = True

    # Save assistant message with token count
    await add_message(
        session,
        conversation.id,
        MessageRole.ASSISTANT,
        assistant_response,
        token_count=tokens_used,
    )

    return ChatResponse(
        response=assistant_response,
        conversation_id=conversation.id,
        tokens_used=tokens_used,
        error=error_occurred,
    )


@router.get("/{user_id}/chat/history", response_model=HistoryResponse)
async def get_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get conversation history for the current user.

    Args:
        user_id: User ID from URL path
        limit: Maximum number of messages to return
        offset: Number of messages to skip
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        HistoryResponse with message list
    """
    # Validate user access
    await validate_user_access(user_id, current_user)

    # Get active conversation
    conversation = await get_active_conversation(session, current_user["user_id"])

    if not conversation:
        return HistoryResponse(
            messages=[], conversation_id=None, total_messages=0
        )

    # Get messages
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.sequence_number)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(statement)
    messages = result.scalars().all()

    # Format messages
    formatted_messages = [
        {
            "role": msg.role.value,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
            "sequence_number": msg.sequence_number,
        }
        for msg in messages
    ]

    return HistoryResponse(
        messages=formatted_messages,
        conversation_id=conversation.id,
        total_messages=conversation.message_count,
    )


@router.post("/{user_id}/chat/new", response_model=NewConversationResponse)
async def new_conversation(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Start a new conversation (deactivates current conversation).

    Args:
        user_id: User ID from URL path
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        NewConversationResponse with new conversation ID
    """
    # Validate user access
    await validate_user_access(user_id, current_user)

    # Deactivate current conversation
    current_conv = await get_active_conversation(session, current_user["user_id"])
    if current_conv:
        current_conv.is_active = False
        session.add(current_conv)

    # Create new conversation
    new_conv = await create_conversation(session, current_user["user_id"])

    return NewConversationResponse(
        conversation_id=new_conv.id,
        message="New conversation started successfully",
    )


@router.post("/{user_id}/logout")
async def logout(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Logout and delete all user conversations and messages.

    Args:
        user_id: User ID from URL path
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        Success message
    """
    # Validate user access
    await validate_user_access(user_id, current_user)

    # Delete all conversations (cascade deletes messages)
    statement = select(Conversation).where(
        Conversation.user_id == current_user["user_id"]
    )
    result = await session.execute(statement)
    conversations = result.scalars().all()

    for conversation in conversations:
        await session.delete(conversation)

    await session.commit()

    return {"message": "Logout successful, all conversations deleted"}
