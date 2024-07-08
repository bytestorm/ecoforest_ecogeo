"""The ecoforest coordinator."""

import logging

#from pyecoforest.api import EcoforestApi
from pyecoforest.exceptions import EcoforestError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .overrides.api import EcoGeoApi
from .overrides.device import EcoGeoDevice
from .const import POLLING_INTERVAL

_LOGGER = logging.getLogger(__name__)


class EcoforestCoordinator(DataUpdateCoordinator[EcoGeoDevice]):
    """DataUpdateCoordinator to gather data from ecoforest device."""

    def __init__(self, hass: HomeAssistant, api: EcoGeoApi) -> None:
        """Initialize DataUpdateCoordinator."""

        super().__init__(
            hass,
            _LOGGER,
            name="ecoforest_ecogeo",
            update_interval=POLLING_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> EcoGeoDevice:
        """Fetch all device and sensor data from api."""
        try:
            data = await self.api.get()
        except EcoforestError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        _LOGGER.debug("Ecoforest data: %s", data)
        return data
