class ResponseStatusError(Exception):
    """Ошибка ответа сервера."""


class HomeworkStatusError(Exception):
    """Ошибка статуса домашней работы."""


class TelegramMessageSendError(Exception):
    """Ошибка отправки сообщения в Telegram."""
