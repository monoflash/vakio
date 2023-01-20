"""Константы."""
from datetime import timedelta
import decimal

from homeassistant.const import Platform


## Базовые константы.
DOMAIN: str = "vakio_base_smart"
DOMAIN_DATA: str = f"{DOMAIN}_data"
NAME: str = "Vakio BASE Smart"

# Платформы.
SENSOR: Platform = Platform.SENSOR
FAN: Platform = Platform.FAN
PLATFORMS: tuple[Platform] = (
    SENSOR,
    FAN,
)

# Опции конфигурации.
CONF_NAME: str = "name"
CONF_SERVER_URL: str = "server_url"
CONF_USERNAME: str = "username"
CONF_PASSWORD: str = "password"
CONF_LANGUAGE: str = "language"
CONF_SCAN_INTERVAL: str = "scan_interval"
CONF_ZONE: str = "zone"
CONF_TRACK_HOSTS: str = "track_network_hosts"

# Умолчания.
DEFAULT_NAME: str = DOMAIN
DEFAULT_SERVER_URL: str = "http://localhost:8199"
DEFAULT_LANGUAGE: str = "rus"
DEFAULT_SCAN_INTERVAL: str = 2
DEFAULT_ZONE: str = "Сервер"
DEFAULT_TRACK_HOSTS: bool = False
DEFAULT_TIME_BETWEEN_UPDATE = timedelta(seconds=2)

## Поддерживаемые языки.
languages: dict[str, str] = {
    "Русский": "rus",
}

## Предустановленные режимы вентиляционной системы.
## inflow       - Приток
## recuperator  - Рекуператор
## inflow_max   - Приток максимальный режим
## winter       - Рекуператор зимний режим
## outflow      - Вытяжка
## outflow_max  - Вытяжка максимальный режим
## night        - Ночной режим
##
## Локализация в HA ещё не способна переводить элементы выпадающего
## списка в preset_mode... Значит называем их на русском языке.
FAN_MODE_OFF: str = "Выключить"
FAN_MODE_INFLOW: str = "Приток"
FAN_MODE_RECUPERATOR: str = "Рекуператор"
FAN_MODE_INFLOW_MAX: str = "Приток максимальный режим"
FAN_MODE_WINTER: str = "Рекуператор зимний режим"
FAN_MODE_OUTFLOW: str = "Вытяжка"
FAN_MODE_OUTFLOW_MAX: str = "Вытяжка максимальный режим"
FAN_MODE_NIGHT: str = "Ночной режим"

SERVER_WORK_TO_FAN_MODE: dict[str, str] = {
    "off": FAN_MODE_OFF,
    "inflow": FAN_MODE_INFLOW,
    "recuperator": FAN_MODE_RECUPERATOR,
    "inflow_max": FAN_MODE_INFLOW_MAX,
    "winter": FAN_MODE_WINTER,
    "outflow": FAN_MODE_OUTFLOW,
    "outflow_max": FAN_MODE_OUTFLOW_MAX,
    "night": FAN_MODE_NIGHT,
}

## Именованные скорости работы вентиляции.
FAN_SPEED_00: decimal.Decimal = 0
FAN_SPEED_01: decimal.Decimal = 1
FAN_SPEED_02: decimal.Decimal = 2
FAN_SPEED_03: decimal.Decimal = 3
FAN_SPEED_04: decimal.Decimal = 4
FAN_SPEED_05: decimal.Decimal = 5
FAN_SPEED_06: decimal.Decimal = 6
FAN_SPEED_07: decimal.Decimal = 7

## Список именованых скоростей работы вентиляции.
NAMED_FAN_SPEEDS: list[decimal.Decimal] = [
    FAN_SPEED_01,
    FAN_SPEED_02,
    FAN_SPEED_03,
    FAN_SPEED_04,
    FAN_SPEED_05,
    FAN_SPEED_06,
    FAN_SPEED_07,
]

## Ошибки.
ERROR_AUTH: str = "ошибка аутентификации"
ERROR_CONFIG_NO_TREADY: str = "конфигурация интеграции не готова"
