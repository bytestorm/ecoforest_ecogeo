"""Support for Ecoforest sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

#from pyecoforest.models.device import Alarm, Device, State

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN
from .coordinator import EcoforestCoordinator
from .entity import EcoforestEntity
from .overrides.device import EcoGeoDevice

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class EcoforestSensorEntityDescription(SensorEntityDescription):
    """Describes Ecoforest sensor entity."""

    value_fn: Callable[[EcoGeoDevice], StateType]


SENSOR_TYPES: tuple[EcoforestSensorEntityDescription, ...] = (
    EcoforestSensorEntityDescription(
        key="t_outdoor",
        translation_key="t_outdoor",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda data: data.t_outdoor,
    ),
    EcoforestSensorEntityDescription(
        key="t_dhw",
        translation_key="t_dhw",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda data: data.t_dhw,
    ),
    EcoforestSensorEntityDescription(
        key="t_cooling",
        translation_key="t_cooling",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda data: data.t_cooling,
    ),
    EcoforestSensorEntityDescription(
        key="t_heating",
        translation_key="t_heating",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda data: data.t_heating,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Ecoforest sensor platform."""
    coordinator: EcoforestCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        EcoforestSensor(coordinator, description) for description in SENSOR_TYPES
    ]

    async_add_entities(entities)


class EcoforestSensor(SensorEntity, EcoforestEntity):
    """Representation of an Ecoforest sensor."""

    entity_description: EcoforestSensorEntityDescription

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.data)
