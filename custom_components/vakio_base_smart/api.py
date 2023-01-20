"""
Класс взаимодействия интеграции с сервисом посредством REST FULL API.
"""
import decimal
import requests
from ppretty import ppretty
import logging
from datetime import datetime, timedelta, timezone
from requests.exceptions import HTTPError, ConnectionError
import json

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_SERVER_URL, DEFAULT_LANGUAGE, SERVER_WORK_TO_FAN_MODE
from .types import ConditionResponse


_LOGGER: logging.Logger = logging.getLogger(__package__)
HEADER_ACCEPT: str = "Accept"
HEADER_CONTENT_TYPE: str = "Content-type"
HEADER_JSON: str = "application/json; charset=UTF-8"
REQUEST_HEADER_JSON: dict[str, str] = {HEADER_CONTENT_TYPE: HEADER_JSON}
REQUEST_HEADER_ACCEPT: dict[str, str] = {HEADER_ACCEPT: "application/json"}


class Coordinator(DataUpdateCoordinator):
    """Класс взаимодействия с сервисом."""

    lastUpdate: datetime | None = None
    condition: ConditionResponse | None = None

    def __init__(
        self,
        hass: HomeAssistant,
        username: str,
        password: str,
        server: str = DEFAULT_SERVER_URL,
        language: str = DEFAULT_LANGUAGE,
        update_interval: timedelta | None = None,
    ) -> None:
        """Конструктор."""
        super().__init__(hass, _LOGGER, name=DOMAIN)
        self._username = username
        self._password = password
        self._server = server
        self._language = language
        self.api = Api(server, username, password, language)
        self.update_interval = update_interval

    async def async_login(self) -> bool:
        try:
            await self.hass.async_add_executor_job(self.api.login)
        except Exception as ex:
            _LOGGER.error(
                f'Не удалось авторизоваться на сервере "{self._server}", ошибка: {ex}'
            )
            return False
        return True

    async def _async_update_data(self) -> None:
        """Запрос данных с общей информацией."""
        await self._async_update(datetime.now(timezone.utc))

    async def _async_update(self, now: datetime) -> None:
        """
        Функция регистритуется в hass, во всех датчиках и устройствах и контролирует
        обновление данных через API не чаще чем раз в 2 секунды.
        """
        update: bool = False
        if self.lastUpdate == None:
            self.lastUpdate = now
            update = True
        diff = now - self.lastUpdate
        if diff > timedelta(seconds=2):
            self.lastUpdate = now
            update = True
        if not update:
            return
        # _LOGGER.warning(f'{now.astimezone(tz=tz.tzlocal())} - выполнение запроса к API: /condition')
        self.condition = await self.hass.async_add_executor_job(self.api.Condition)

    def Available(self) -> bool | None:
        """Состояние доступности сервера и вентиляционной системы на сервере."""
        if self.condition == None:
            return None

        return self.condition.Available

    def Speed(self) -> decimal.Decimal | None:
        """Текущая скорость работы вентиляционной системы."""
        if self.condition == None:
            return None
        if not self.condition.State and self.condition.Speed > 0:
            self.condition.Speed = 0

        return self.condition.Speed

    def FanMode(self) -> str | None:
        """
        Текущей предопределённый режим работы вентиляционной системы.
        Возвращается константа.
        """
        if self.condition == None:
            return None
        if self.condition.Speed == 0:
            return None
        work: str = self.condition.Work

        return SERVER_WORK_TO_FAN_MODE.get(work, None)

    def IsOn(self) -> bool | None:
        """
        Текущее состояние включённости вентиляционной системы.
        Если вентиляционная система включена, возвращается "истина", если выключена, "ложь".
        Если состояние не известно, возвращается None.
        """
        if self.condition == None:
            return None

        return self.condition.State

    def SetTurnOn(self) -> None:
        """Выполнение команды включения вентиляционной системы."""
        self.condition.State = "on"
        self.hass.async_add_executor_job(self.api.State, True)

    def SetTurnOff(self) -> None:
        """Выполнение команды отключения вентиляционной системы."""
        self.condition.State = "off"
        self.hass.async_add_executor_job(self.api.State, False)

    def SetSpeed(self, speed: decimal.Decimal) -> None:
        """Выполнение команды установки скорости вентиляции."""
        self.condition.Speed = speed
        self.hass.async_add_executor_job(self.api.Speed, speed)

    def SetWorkMode(self, workmode: str) -> None:
        """Выполнение команды установки режима работы вентиляции."""
        self.condition.Work = workmode
        self.hass.async_add_executor_job(self.api.Workmode, workmode)


class Api:
    """Класс реализации запросов к методам API сервиса."""

    def __init__(
        self, server: str, username: str, password: str, language: str
    ) -> None:
        self._server = server
        self._username = username
        self._password = password
        self._language = language

    def __enter__(self) -> None:
        _LOGGER.warning("Вызов функции Api->__enter__()")
        self.login()
        return self

    def login(self) -> None:
        _LOGGER.warning(
            f"Вызов метода login. server={self._server}, username={self._username}, password={self._password}, language={self._language}"
        )
        # raise Error("Ошибка аутентификации.") from None
        # raise

    def Condition(self) -> ConditionResponse | None:
        """Получение с сервера состояния устройства."""
        ENDPOINT: str = "/condition"
        condition: ConditionResponse | None = None
        try:
            response = requests.get(
                self._server + ENDPOINT, headers=REQUEST_HEADER_ACCEPT
            )
        except ConnectionError as err:
            _LOGGER.error(f"Ошибка подключения к серверу: {err}")
            return condition
        except HTTPError as err:
            _LOGGER.error(f"Ошибка HTTP запроса: {err}")
            return condition
        else:
            try:
                condition = ConditionResponse(**json.loads(response.text))
            except json.JSONDecodeError as err:
                _LOGGER.error(f"Ошибка декодирования JSON: {err}")
                return condition
        return condition

    def State(self, state: bool) -> None:
        """Установка нового состояния устройства."""
        ENDPOINT: str = "/state"
        try:
            requests.put(
                self._server + ENDPOINT,
                json={"state": state},
                headers=REQUEST_HEADER_JSON,
            )
        except ConnectionError as err:
            _LOGGER.error(f"Ошибка подключения к серверу: {err}")
            return
        except HTTPError as err:
            _LOGGER.error(f"Ошибка HTTP запроса: {err}")
            return

    def Speed(self, speed: decimal.Decimal) -> None:
        """Установка скорости работы вентиляции."""
        ENDPOINT: str = "/speed"
        try:
            requests.put(
                self._server + ENDPOINT,
                json={"speed": speed},
                headers=REQUEST_HEADER_JSON,
            )
        except ConnectionError as err:
            _LOGGER.error(f"Ошибка подключения к серверу: {err}")
            return
        except HTTPError as err:
            _LOGGER.error(f"Ошибка HTTP запроса: {err}")
            return

    def Workmode(self, workmode: str) -> None:
        """Установка предопределённого рабочего режима."""
        ENDPOINT: str = "/workmode"
        try:
            requests.put(
                self._server + ENDPOINT,
                json={"workmode": workmode},
                headers=REQUEST_HEADER_JSON,
            )
        except ConnectionError as err:
            _LOGGER.error(f"Ошибка подключения к серверу: {err}")
            return
        except HTTPError as err:
            _LOGGER.error(f"Ошибка HTTP запроса: {err}")
            return
