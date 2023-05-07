"""Vakio BASE Smart integration."""
from __future__ import annotations
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed

from .api import Coordinator
from .const import DOMAIN
from .const import CONF_USERNAME, CONF_PASSWORD, CONF_SERVER_URL, CONF_SCAN_INTERVAL
from .const import PLATFORMS
from .const import languages, CONF_LANGUAGE, DEFAULT_LANGUAGE, DEFAULT_SCAN_INTERVAL
from .const import ERROR_AUTH, ERROR_CONFIG_NO_TREADY


_LOGGER: logging.Logger = logging.getLogger(__package__)


## noinspection PyUnusedLocal
async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Настройка интеграции с использованием YAML не поддерживается."""
    _LOGGER.info("Вызов функции __init__->async_setup()")

    return True


async def async_setup_entry(hass: HomeAssistant, conf: ConfigEntry) -> bool:
    """Настройка интеграции."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
    username = conf.data.get(CONF_USERNAME)
    password = conf.data.get(CONF_PASSWORD)
    server = conf.data.get(CONF_SERVER_URL)
    language = languages.get(
        conf.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE), DEFAULT_LANGUAGE
    )
    if conf.options.get(CONF_SCAN_INTERVAL):
        update_interval = timedelta(seconds=conf.options[CONF_SCAN_INTERVAL])
    else:
        update_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    coordinator = Coordinator(hass, username, password, server, language, update_interval=update_interval)
    # Аутентификация, для проверки корректности авторизационных данных.
    if not await coordinator.async_login():
        raise ConfigEntryAuthFailed(ERROR_AUTH)
    # Выполнение обновления данных.
    await coordinator.async_config_entry_first_refresh()
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady(ERROR_CONFIG_NO_TREADY)
    # Регистрация интеграции в Home Assistant.
    hass.data[DOMAIN][conf.entry_id] = coordinator
    conf.add_update_listener(async_reload_entry)
    conf.async_on_unload(conf.add_update_listener(config_entry_update_listener))
    await hass.config_entries.async_forward_entry_setups(conf, PLATFORMS)

    return True


async def config_entry_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Функция вызывается при обновлении конфигурации."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Удаление интеграции."""
    unload_ok: bool = False
    if DOMAIN not in hass.data:
        return True
    if entry.entry_id in hass.data[DOMAIN]:
        coordinator = hass.data[DOMAIN][entry.entry_id]
        unload_ok = all(
            await asyncio.gather(
                *[
                    hass.config_entries.async_forward_entry_unload(entry, platform)
                    for platform in PLATFORMS
                ]
            )
        )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info(
            f"Координатор Coordinator() домена {DOMAIN} удалён, entry_id: {entry.entry_id}."
        )

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Перезагрузка интеграции."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
