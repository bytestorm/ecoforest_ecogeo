"""Switch platform for Ecoforest."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.const import CONF_ALIAS
from pyecoforest.api import EcoforestApi
from pyecoforest.models.device import Device

from homeassistant.components.number.const import NumberMode
from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import EcoforestCoordinator
from .entity import EcoforestEntity
from .overrides.api import MAPPING


@dataclass(frozen=True, kw_only=True)
class EcoforestNumberEntityDescription(NumberEntityDescription):
    """Describes an Ecoforest number entity."""

    min: None
    max: None
    step: None

    value_fn: Callable[[Device], bool]
    switch_fn: Callable[[EcoforestApi, bool], Awaitable[Device]]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ecoforest number platform."""
    coordinator: EcoforestCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    device_alias = config_entry.data[CONF_ALIAS] if CONF_ALIAS in config_entry.data else None
    entities = [
        EcoforestNumberEntity(coordinator, key, definition, device_alias) for key, definition in MAPPING.items() if "is_number" in definition.keys() and definition["is_number"] == True
    ]

    async_add_entities(entities)


class EcoforestNumberEntity(EcoforestEntity, NumberEntity):
    """Representation of an Ecoforest switch entity."""

    entity_description: EcoforestNumberEntityDescription

    # todo: use specs
    @property
    def native_min_value(self) -> float:
        return 0

    # todo: use specs
    @property
    def native_max_value(self) -> float:
        return 1000

    # todo: use specs
    @property
    def native_step(self) -> float:
        return 0.1

    @property
    def mode(self):
        return NumberMode.BOX

    @property
    def native_value(self) -> float:
         """Return the state of the ecoforest device."""
         return self.data.state[self.entity_description.key]

    async def async_set_native_value(self, value: float):
         """Set the value."""
         await self.coordinator.api.set_numeric_value(self.entity_description.key, value)
         await self.coordinator.async_request_refresh()
