"""Button platform for Ecoforest."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.const import CONF_ALIAS
from pyecoforest.api import EcoforestApi
from pyecoforest.models.device import Device

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import EcoforestCoordinator
from .entity import EcoforestEntity
from .overrides.api import MAPPING


@dataclass(frozen=True, kw_only=True)
class EcoforestButtonEntityDescription(ButtonEntityDescription):
    """Describes an Ecoforest button entity."""

    value_fn: Callable[[Device], bool]
    press_fn: Callable[[EcoforestApi, bool], Awaitable[Device]]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ecoforest button platform."""
    coordinator: EcoforestCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    device_alias = config_entry.data[CONF_ALIAS] if CONF_ALIAS in config_entry.data else None
    entities = [
        EcoforestButtonEntity(coordinator, key, definition, device_alias) for key, definition in MAPPING.items() if definition["entity_type"] == "button"
    ]

    async_add_entities(entities)


class EcoforestButtonEntity(EcoforestEntity, ButtonEntity):
    """Representation of an Ecoforest button entity."""

    entity_description: EcoforestButtonEntityDescription

    @property
    def is_on(self) -> bool:
        """Return the state of the ecoforest device."""
        return self.data.state[self.entity_description.key]

    async def async_press(self) -> None:
        """Button press."""
        await self.coordinator.api.turn_switch(self.entity_description.key, True)
        await self.coordinator.async_request_refresh()
