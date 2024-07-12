"""Support for Ecoforest sensors."""

from __future__ import annotations

import logging
from functools import cached_property

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import StateType

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import EcoforestCoordinator
from .entity import EcoforestEntity, EcoforestSensorEntityDescription
from .overrides.device import EcoGeoDevice
from .overrides.api import MAPPING

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Ecoforest sensor platform."""
    coordinator: EcoforestCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        EcoforestSensor(coordinator, key, definition) for key, definition in MAPPING.items() if definition["entity_type"] != "switch"
    ]

    async_add_entities(entities)


class EcoforestSensor(SensorEntity, EcoforestEntity):
    """Representation of an Ecoforest sensor."""
    entity_description: EcoforestSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(self.data)

        return self.data.state[self.entity_description.key]
