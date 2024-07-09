from dataclasses import dataclass

import httpx
from pyecoforest.api import EcoforestApi

from custom_components.ecoforest_ecogeo.overrides.device import EcoGeoDevice


@dataclass
class ApiRequest:
    op: str
    start: int
    number: int


API_SERIAL = ApiRequest("2002", 5323, 6)


class EcoGeoApi(EcoforestApi):
    def __init__(
        self,
        host: str,
        user: str,
        password: str
    ) -> None:
        super(EcoforestApi, self).__init__(host, httpx.BasicAuth(user, password))

    async def get(self) -> EcoGeoDevice:
        """Retrieve ecoforest information from api."""
        return EcoGeoDevice.build(
            {
                "serial": await self._serial()
            }
        )

    async def _serial(self) -> dict[str, str]:
        return {"asd": "qwe"}
        #return await self._request(data={"idOperacion": API_SERIAL.op, "dir": API_SERIAL.start, "num": API_SERIAL.number})