import datetime
import decimal
import dateutil


class Error(Exception):
    """Ошибка."""

    pass


class ResponseError(Error):
    """Неожиданная ошибка."""

    def __init__(self, status_code, message):
        super(ResponseError, self).__init__(
            "Неожиданная ошибка API, код: {1} ({0})".format(status_code, message)
        )
        self.status_code = status_code
        self.message = message


class LoginError(Error):
    """Не верный логин или пароль."""

    pass


class AuthError(Error):
    """Ошибка аутентификации."""

    pass


class ConditionResponse:
    """
    Структура данных возвращаемая запросом API с выполненными обработками полученных данных.
    """

    def __init__(
        self,
        last_activity_at: str,
        available: bool,
        speed: decimal.Decimal,
        state: str,
        work: str,
        mode: str,
        command: str,
    ):
        self.State: bool = False
        self.LastActivityAt: datetime = dateutil.parser.isoparse(last_activity_at)
        self.Available: bool = available
        self.Speed: decimal.Decimal = speed
        self.Work: str = work
        self.Mode: str = mode
        self.Command: str = command
        if state == "on":
            self.State = True
