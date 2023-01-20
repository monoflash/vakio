from __future__ import annotations
import decimal
from typing import Any, Optional
import logging
import voluptuous as vol
from datetime import datetime, timedelta, timezone

from homeassistant.components.fan import (
    FanEntity,
    FanEntityFeature,
    DIRECTION_FORWARD,
    DIRECTION_REVERSE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util.percentage import (
    ordered_list_item_to_percentage,
    percentage_to_ordered_list_item,
)

from .api import Coordinator
from .const import DOMAIN, DEFAULT_TIME_BETWEEN_UPDATE, SERVER_WORK_TO_FAN_MODE
from .const import (
    FAN_MODE_OFF,
    FAN_MODE_INFLOW,
    FAN_MODE_RECUPERATOR,
    FAN_MODE_INFLOW_MAX,
    FAN_MODE_WINTER,
    FAN_MODE_OUTFLOW,
    FAN_MODE_OUTFLOW_MAX,
    FAN_MODE_NIGHT,
    FAN_SPEED_00,
    FAN_SPEED_01,
    NAMED_FAN_SPEEDS,
)


_LOGGER: logging.Logger = logging.getLogger(__package__)
percentage = ordered_list_item_to_percentage(NAMED_FAN_SPEEDS, FAN_SPEED_01)
named_speed = percentage_to_ordered_list_item(NAMED_FAN_SPEEDS, 14)


FULL_SUPPORT = (
    FanEntityFeature.SET_SPEED
    | FanEntityFeature.OSCILLATE
    | FanEntityFeature.DIRECTION
    | FanEntityFeature.PRESET_MODE
)
LIMITED_SUPPORT = FanEntityFeature.SET_SPEED


async def async_setup_entry(
    hass: HomeAssistant, conf: ConfigEntry, entities: AddEntitiesCallback
) -> bool:
    """Регистрация настроек вентиляционной системы."""
    # _LOGGER.info("Вызов функции fan->async_setup_entry()")
    return await async_setup_platform(hass, conf, entities)


async def async_setup_platform(
    hass: HomeAssistant,
    conf: ConfigType,
    entities: AddEntitiesCallback,
    info: DiscoveryInfoType | None = None,
) -> bool:
    """Настройка платформы интеграции вентиляционной системы."""
    # _LOGGER.info("Вызов функции fan->async_setup_platform()")
    vf = VakioFan(
        hass,
        "fan1",
        "Vent machine",
        conf.entry_id,
        FULL_SUPPORT,
        [
            FAN_MODE_OFF,
            FAN_MODE_INFLOW,
            FAN_MODE_INFLOW_MAX,
            FAN_MODE_OUTFLOW,
            FAN_MODE_OUTFLOW_MAX,
            FAN_MODE_RECUPERATOR,
            FAN_MODE_WINTER,
            FAN_MODE_NIGHT,
        ],
        translation_key="select_preset_modes",
    )
    entities([vf])
    # Регистрация автоматического обновления статуса вентиляционной системы запросами к серверу.
    coordinator: Coordinator = hass.data[DOMAIN][conf.entry_id]
    async_track_time_interval(
        hass, coordinator._async_update, DEFAULT_TIME_BETWEEN_UPDATE
    )
    async_track_time_interval(hass, vf._async_update, DEFAULT_TIME_BETWEEN_UPDATE)

    return True


class VakioBaseFan(FanEntity):
    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        unique_id: str,
        name: str,
        entry_id: str,
        supported_features: FanEntityFeature,
        preset_modes: list[str] | None,
        translation_key: str | None = None,
    ) -> None:
        """Конструктор."""
        self.hass = hass
        self._unique_id = unique_id
        self._attr_supported_features = supported_features
        self._percentage: int | None = None
        self._preset_modes = preset_modes
        self._preset_mode: str | None = None
        self._oscillating: bool | None = None
        self._direction: str | None = None
        self._attr_name = name
        self._entity_id = entry_id
        if supported_features & FanEntityFeature.OSCILLATE:
            self._oscillating = False
        if supported_features & FanEntityFeature.DIRECTION:
            self._direction = None
        self._attr_translation_key = translation_key
        self.coordinator: Coordinator = hass.data[DOMAIN][entry_id]

    @property
    def unique_id(self) -> str:
        """Возвращение уникального идентификатора."""
        return self._unique_id

    @property
    def current_direction(self) -> str | None:
        """Текущий статус направления вентиляции."""
        return self._direction

    @property
    def oscillating(self) -> bool | None:
        """Текущий статус рекупирации."""
        return self._oscillating


class VakioFan(VakioBaseFan, FanEntity):
    """Состояние вентиляционной системы отображаемая в hass."""

    @property
    def percentage(self) -> int | None:
        """Возвращает текущую скорость в процентах."""
        return self._percentage

    @property
    def speed_count(self) -> int:
        """Возвращает количество поддерживаемых скоростей."""
        return len(NAMED_FAN_SPEEDS)

    @property
    def preset_mode(self) -> str | None:
        """Возвращает текущий пресет режима работы."""
        return self._preset_mode

    @property
    def preset_modes(self) -> list[str] | None:
        """Возвращает все пресеты режимов работы."""
        return self._preset_modes

    async def async_set_percentage(self, percentage: int) -> None:
        """Установка скорости работы вентиляции в процентах."""
        self._percentage = percentage
        if percentage == 0:
            self.coordinator.SetTurnOff()
            self.updateAllOptions()
            return
        self.coordinator.SetTurnOn()
        # Получение именованой скорости.
        speed: decimal.Decimal = percentage_to_ordered_list_item(
            NAMED_FAN_SPEEDS, percentage
        )
        # Выполнение метода API установки скорости.
        self.coordinator.SetSpeed(speed)
        if self.updateSpeed():
            self.updateAllOptions()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Переключение режима работы на основе пресета."""
        if self.preset_modes and preset_mode in self.preset_modes:
            self._preset_mode = preset_mode
        else:
            raise ValueError(f"Неизвестный режим: {preset_mode}")
        if self._preset_mode == FAN_MODE_OFF:
            self.coordinator.SetTurnOff()
            self.updateAllOptions()
            return
        # Поиск именованого предустановленного серверного режима.
        for key, mode in SERVER_WORK_TO_FAN_MODE.items():
            if mode == preset_mode:
                # Выполнение метода API установки режима.
                self.coordinator.SetWorkMode(key)
        if self._percentage is None or self._percentage == 0:
            self.coordinator.SetSpeed(FAN_SPEED_01)
        self.updateAllOptions()

    async def async_turn_on(
        self,
        speed: Optional[str] = None,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Включение вентиляционной системы."""
        self.coordinator.SetTurnOn()
        # Получение именованой скорости.
        new_speed: decimal.Decimal = 0
        if percentage != None:
            new_speed = percentage_to_ordered_list_item(NAMED_FAN_SPEEDS, percentage)
        else:
            new_speed = FAN_SPEED_01
        # Выполнение метода API установки скорости.
        self.coordinator.SetSpeed(new_speed)
        self.updateAllOptions()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Выключение вентиляционной системы."""
        self.coordinator.SetTurnOff()
        await self._async_update(datetime.now(timezone.utc))

    async def async_set_direction(self, direction: str) -> None:
        """Переключение направления вентиляции."""
        self._direction = direction
        if direction == DIRECTION_FORWARD and (
            self._preset_mode != FAN_MODE_INFLOW
            or self._preset_mode != FAN_MODE_INFLOW_MAX
        ):
            self._preset_mode = FAN_MODE_INFLOW
            for key, mode in SERVER_WORK_TO_FAN_MODE.items():
                if mode == self._preset_mode:
                    self.coordinator.SetWorkMode(key)
        if direction == DIRECTION_REVERSE and (
            self._preset_mode != FAN_MODE_OUTFLOW
            or self._preset_mode != FAN_MODE_OUTFLOW_MAX
        ):
            self._preset_mode = FAN_MODE_OUTFLOW
            for key, mode in SERVER_WORK_TO_FAN_MODE.items():
                if mode == self._preset_mode:
                    self.coordinator.SetWorkMode(key)
        self.updateAllOptions()

    async def async_oscillate(self, oscillating: bool) -> None:
        """Переключение режима рекуперации."""
        self._oscillating = oscillating
        self.updateAllOptions()

    async def _async_update(self, now: datetime) -> None:
        """
        Функция вызывается по таймеру.
        Выполняется сравнение параметров состояния вентиляционной системы с параметрами записанными в классе.
        Если выявляется разница, тогда параметры класса обновляются.
        """
        isUpdate: bool = False
        if self.updateSpeed():
            isUpdate = True
        if self.updatePresetMode():
            isUpdate = True
        if self.updateOnOff():
            isUpdate = True
        if isUpdate:
            self.updateAllOptions()

    def updateSpeed(self) -> bool:
        """
        Обновление текущей скорости работы вентиляционной системы.
        Возвращается "истина" если было выполнено обновление.
        """
        speed: decimal.Decimal | None = self.coordinator.Speed()
        if (
            speed == None or speed > len(NAMED_FAN_SPEEDS) or speed == 0
        ) and self._percentage != None:
            self._percentage = None
            return True
        if speed == None:
            return False
        speed = speed - 1
        named_speed = NAMED_FAN_SPEEDS[speed]
        new_speed_percentage = ordered_list_item_to_percentage(
            NAMED_FAN_SPEEDS, named_speed
        )
        if self._percentage != new_speed_percentage:
            self._percentage = new_speed_percentage
            return True

        return False

    def updatePresetMode(self) -> bool:
        """
        Обновление текущего предопределённого режима работы вентиляционной системы.
        Возвращается "истина" если было выполнено обновление.
        """
        mode: str | None = self.coordinator.FanMode()
        if self._preset_mode == mode:
            return False
        self._preset_mode = mode
        self._oscillating = (
            mode == FAN_MODE_RECUPERATOR
            or mode == FAN_MODE_WINTER
            or mode == FAN_MODE_NIGHT
        )
        # Переключение значка прямая вентиляция для приточных режимов.
        if mode == FAN_MODE_INFLOW or mode == FAN_MODE_INFLOW_MAX:
            self._direction = DIRECTION_FORWARD
        # Переключение значка обратная вентиляция для режимов вытяжки.
        if mode == FAN_MODE_OUTFLOW or mode == FAN_MODE_OUTFLOW_MAX:
            self._direction = DIRECTION_REVERSE
        # Отключение значка направления для режимов с рекуперацией.
        if (
            mode == FAN_MODE_RECUPERATOR
            or mode == FAN_MODE_WINTER
            or mode == FAN_MODE_NIGHT
            or mode == FAN_MODE_OFF
        ):
            self._direction = None

        return True

    def updateOnOff(self) -> bool:
        """
        Обновление текущего состояния включённости вентиляционной системы.
        Возвращается "истина" если было выполнено обновление.
        """
        isOn: bool | None = self.coordinator.IsOn()
        if isOn == None:
            return False
        if not bool(isOn):
            # Вентиляция выключена.
            if not self._percentage is None and self._percentage > 0:
                self._direction = None
                self._percentage = int(0)
                return True
        else:
            # Вентиляция включена.
            if self._percentage is None or self._percentage == 0:
                if self._percentage is None:
                    self._percentage = ordered_list_item_to_percentage(
                        NAMED_FAN_SPEEDS, FAN_SPEED_01
                    )
                if self._preset_mode == FAN_MODE_OFF:
                    self._preset_mode = None
                return True

        return False

    def updateAllOptions(self) -> None:
        """
        Обновление состояния всех индикаторов интеграции в соответствии
        с переключённым режимом работы вентиляционной системы.
        """
        # Выбор режима рекуперация при включении "колебания".
        if (
            self._oscillating
            and self._preset_mode != FAN_MODE_RECUPERATOR
            and self._preset_mode != FAN_MODE_WINTER
            and self._preset_mode != FAN_MODE_NIGHT
        ):
            self._preset_mode = FAN_MODE_RECUPERATOR
            for key, mode in SERVER_WORK_TO_FAN_MODE.items():
                if mode == self._preset_mode:
                    self.coordinator.SetWorkMode(key)
        if self._oscillating and self._direction != None:
            self._direction = None
        if not self._oscillating and self._direction == None:
            self._direction = DIRECTION_FORWARD
        if self._direction == DIRECTION_REVERSE and (
            self._preset_mode == FAN_MODE_INFLOW
            or self._preset_mode == FAN_MODE_INFLOW_MAX
        ):
            self._direction = DIRECTION_FORWARD
        if self._direction == DIRECTION_FORWARD and (
            self._preset_mode == FAN_MODE_OUTFLOW
            or self._preset_mode == FAN_MODE_OUTFLOW_MAX
        ):
            self._direction = DIRECTION_REVERSE
        if not self._oscillating and (
            self._preset_mode == FAN_MODE_RECUPERATOR
            or self._preset_mode == FAN_MODE_WINTER
            or self._preset_mode == FAN_MODE_NIGHT
        ):
            self._preset_mode = FAN_MODE_INFLOW
            for key, mode in SERVER_WORK_TO_FAN_MODE.items():
                if mode == self._preset_mode:
                    self.coordinator.SetWorkMode(key)
        if (
            not self._percentage is None
            and self._percentage > 0
            and (self._preset_mode is None or self._preset_mode == FAN_MODE_OFF)
        ):
            self._direction = DIRECTION_FORWARD
            self._preset_mode = FAN_MODE_INFLOW
            for key, mode in SERVER_WORK_TO_FAN_MODE.items():
                if mode == self._preset_mode:
                    self.coordinator.SetWorkMode(key)
        self.schedule_update_ha_state()
