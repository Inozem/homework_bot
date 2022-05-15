class NoneCriticalError(Exception):
    """Класс ошибки, о которой не нужно сообщать в Телеграм."""

    pass


class GetApiAnswerError(Exception):
    """Класс ошибки ответа API."""

    pass
