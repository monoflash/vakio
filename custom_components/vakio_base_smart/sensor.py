from __future__ import annotations
import decimal
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .api import Coordinator
from .const import DOMAIN, DEFAULT_TIME_BETWEEN_UPDATE


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, conf: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> bool:
    """Инициализация сенсора."""
    # _LOGGER.info("Вызов функции sensor->async_setup_entry()")
    name = "Main power"
    unique_id = "main_power"
    async_add_entities([VakioSensorEntity(hass, unique_id, name, conf.entry_id)])
    coordinator: Coordinator = hass.data[DOMAIN][conf.entry_id]
    async_track_time_interval(
        hass, coordinator._async_update, DEFAULT_TIME_BETWEEN_UPDATE
    )

    return True


class VakioSensorEntity(SensorEntity):
    def __init__(
        self, hass: HomeAssistant, unique_id: str, name: str, entry_id: str
    ) -> None:
        super().__init__()
        coordinator: Coordinator = hass.data[DOMAIN][entry_id]
        self.hass = hass
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._entity_id = entry_id
        self._attr_device_class = SensorDeviceClass.BATTERY
        self.coordinator = coordinator

    @property
    def state(self) -> None | decimal.Decimal:
        """
        Состояние доступности сенсора. Запрашивается у координатора.
        Возможные состояния:
        * None - Нет подключения к серверу вентиляционной системы или данные ещё не пришли.
        * 0    - Сервер вентиляционной системы не может проверить доступность вентиляции (не проходят пинги)
        * 100  - Сервер успешно пингует вентиляционную систему.
        """
        ret: decimal.Decimal | None = None
        ave = self.coordinator.Available()
        if ave != None:
            if ave:
                ret = decimal.Decimal(100)
            else:
                ret = decimal.Decimal(0)

        return ret
