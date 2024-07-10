import string
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
        super().__init__(host, httpx.BasicAuth(user, password))

    async def get(self) -> EcoGeoDevice:
        """Retrieve ecoforest information from api."""
        return EcoGeoDevice.build(
            {
                "serial": {"value": await self._serial()}
            }
        )

    async def _serial(self) -> str:
        response = await self._request(data={"idOperacion": API_SERIAL.op, "dir": API_SERIAL.start, "num": API_SERIAL.number})
        return parse_serial_number(response)

    def _parse(self, response: str) -> dict[str, str]:
        lines = response.split('\n')

        a, b = lines[0].split('=')
        if a != "error_geo_get_reg" or b != "0":
            raise Exception("bad response: {}".format(response))

        return lines[1].split('&')[2:]
    def parse_serial_number(self, data):
        serial_dictionary = ["--"] + [*string.digits] + [*string.ascii_uppercase]
        return ''.join([serial_dictionary[self.parse_ecoforest_int(x)] for x in data])

    def parse_ecoforest_int(self, value):
        result = int(value, 16)
        return result if result <= 32768 else result - 65536
