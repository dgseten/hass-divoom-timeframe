from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import DivoomClient
from .const import DOMAIN, MANUFACTURER, MODEL


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    client: DivoomClient = hass.data[DOMAIN][entry.entry_id]
    name = entry.data.get(CONF_NAME, "Divoom Time Frame")
    async_add_entities([DivoomScreenSwitch(hass, entry, client, name)], update_before_add=False)


@dataclass
class _OptimisticState:
    is_on: bool = True  # default “on”


class DivoomScreenSwitch(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: DivoomClient, device_name: str) -> None:
        self.hass = hass
        self._entry = entry
        self._client = client
        self._device_name = device_name
        self._state = _OptimisticState(is_on=True)

        self._attr_unique_id = f"{entry.unique_id}_screen"
        self._attr_name = "Screen"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.unique_id)},
            name=self._device_name,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def is_on(self) -> bool:
        return self._state.is_on

    async def async_turn_on(self, **kwargs) -> None:
        session = async_get_clientsession(self.hass)
        await self._client.set_screen(session, True)
        self._state.is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        session = async_get_clientsession(self.hass)
        await self._client.set_screen(session, False)
        self._state.is_on = False
        self.async_write_ha_state()
