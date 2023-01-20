"""Добавление конфигурации для Vakio BASE Smart."""
# from ppretty import ppretty
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import selector
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_NAME,
    CONF_SERVER_URL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_LANGUAGE,
    CONF_SCAN_INTERVAL,
    CONF_ZONE,
    CONF_TRACK_HOSTS,
)
from .const import (
    DEFAULT_SERVER_URL,
    DEFAULT_LANGUAGE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_ZONE,
    DEFAULT_TRACK_HOSTS,
)
from .const import DOMAIN, NAME
from .const import languages
from .api import Coordinator


_LOGGER = logging.getLogger(__name__)


class VakioFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Добавление конфигурации для Vakio BASE Smart."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Конструктор."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Обработчик настройки, вызранной пользователем."""
        self._errors = {}
        if user_input is not None:
            # Проверка введённых данных.
            valid = await self._test_credentials(
                "",  # user_input[CONF_USERNAME],
                "",  # user_input[CONF_PASSWORD],
                user_input[CONF_SERVER_URL],
                user_input[CONF_LANGUAGE],
            )
            _LOGGER.warning(f"Результат: {valid}")
            if valid:
                return self.async_create_entry(title="", data=user_input)
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        return await self._show_config_form(
            user_input={
                CONF_NAME: NAME,
                CONF_SERVER_URL: DEFAULT_SERVER_URL,
                # CONF_USERNAME: "",
                # CONF_PASSWORD: "",
                CONF_LANGUAGE: DEFAULT_LANGUAGE,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return VakioOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Отображение формы конфигурации."""
        data_schema = {
            vol.Required(CONF_SERVER_URL, default=DEFAULT_SERVER_URL): str,
            # vol.Required(CONF_USERNAME): str,
            # vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): selector(
                {"select": {"options": list(languages.keys()), "mode": "dropdown"}}
            ),
        }
        if self.show_advanced_options:
            data_schema = {
                vol.Required(CONF_SERVER_URL, default=DEFAULT_SERVER_URL): str,
                # vol.Required(CONF_USERNAME): str,
                # vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): selector(
                    {"select": {"options": list(languages.keys()), "mode": "dropdown"}}
                ),
            }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=self._errors,
        )

    async def _test_credentials(self, username, password, server, language) -> bool:
        """Возвращается 'истина', если реквизиты доступа верные."""
        try:
            _LOGGER.warning(
                f"Вызов метода VakioFlowHandler->_test_credentials(username={username}, password={password}, server={server}, language={language})"
            )
            coordinator = Coordinator(self.hass, username, password, server, language)
            await self.hass.async_add_executor_job(coordinator.api.login)
            return True
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.exception(ex)
        return False


class VakioOptionsFlowHandler(config_entries.OptionsFlow):
    """Опции конфигурации для Vakio BASE Smart."""

    def __init__(self, config_entry):
        """Инициализация HACS настроек."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Управление опциями."""
        return await self.async_step_basic_options(user_input)

    async def async_step_basic_options(self, user_input=None):
        """Обработчик данных заполняемых пользователейм."""
        if user_input is not None:
            self.options.update(user_input)
            return await self.async_step_sensor_select()

        return self.async_show_form(
            step_id="basic_options",
            last_step=False,
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): cv.positive_int,
                    vol.Optional(
                        CONF_ZONE,
                        default=self.config_entry.options.get(CONF_ZONE, DEFAULT_ZONE),
                    ): str,
                }
            ),
        )

    async def async_step_sensor_select(self, user_input=None):
        """Обновление настроек конфигурации."""
        if user_input is not None:
            self.options.update(user_input)
            return self.async_create_entry(title="", data=self.options)

        return self.async_show_form(
            step_id="sensor_select",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_TRACK_HOSTS,
                        default=self.config_entry.options.get(
                            CONF_TRACK_HOSTS, DEFAULT_TRACK_HOSTS
                        ),
                    ): bool,
                },
            ),
        )
