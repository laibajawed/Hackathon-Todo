"""Token counting utilities using tiktoken.

This module provides functions for estimating token counts for messages
to manage conversation context windows.
"""

import tiktoken
from typing import List, Dict


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count the number of tokens in a text string.

    Args:
        text: Text to count tokens for
        model: Model name for tokenizer (default: gpt-3.5-turbo)

    Returns:
        Number of tokens in the text
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base encoding if model not found
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def count_message_tokens(
    messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo"
) -> int:
    """Count tokens for a list of messages.

    This accounts for the message formatting overhead in addition to content.

    Args:
        messages: List of message dictionaries with 'role' and 'content'
        model: Model name for tokenizer

    Returns:
        Total token count including formatting overhead
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens_per_message = 3  # Every message follows <|start|>{role/name}\n{content}<|end|>\n
    tokens_per_name = 1  # If there's a name, the role is omitted

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name

    num_tokens += 3  # Every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def estimate_tokens(text: str) -> int:
    """Quick estimation of token count without loading tokenizer.

    Uses approximation: 1 token ≈ 0.75 words ≈ 4 characters

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters
    return len(text) // 4
