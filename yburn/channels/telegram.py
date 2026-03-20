"""Telegram notification channel."""

import logging

logger = logging.getLogger(__name__)


def send_message(token: str, chat_id: str, text: str) -> bool:
    """Send a message via Telegram Bot API.

    Args:
        token: Telegram bot token.
        chat_id: Telegram chat ID to send to.
        text: Message text.

    Returns:
        True if the message was sent successfully (not yet implemented).
    """
    raise NotImplementedError("Telegram channel not yet implemented")
