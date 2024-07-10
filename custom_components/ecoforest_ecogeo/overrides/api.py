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
API_TANK_TEMPERATURES = ApiRequest("2002", 200, 2)
API_BASIC_TEMPERATURES = ApiRequest("2002", 8, 3)


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
        serial = await self._serial()
        temperatures_tanks = await self._t_tanks()
        temperatures_basic = await self._t_basic()

        return EcoGeoDevice.build(
            {
                "serial": {"value": serial},
                "temperatures": {
                    "t_outdoor": self.parse_ecoforest_float(temperatures_basic[0]),
                    "t_heating": self.parse_ecoforest_float(temperatures_tanks[0]),
                    "t_cooling": self.parse_ecoforest_float(temperatures_tanks[1]),
                    "t_dhw": self.parse_ecoforest_float(temperatures_basic[2])
                }

            }
        )

    async def _serial(self) -> str:
        response = await self._request(data={"idOperacion": API_SERIAL.op, "dir": API_SERIAL.start, "num": API_SERIAL.number})
        return self.parse_serial_number(response)

    async def _t_tanks(self) -> list:
        return await self._request(data={"idOperacion": API_TANK_TEMPERATURES.op, "dir": API_TANK_TEMPERATURES.start, "num": API_TANK_TEMPERATURES.number})

    async def _t_basic(self) -> list:
        return await self._request(data={"idOperacion": API_BASIC_TEMPERATURES.op, "dir": API_BASIC_TEMPERATURES.start, "num": API_BASIC_TEMPERATURES.number})

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

    def parse_ecoforest_float(self, value):
        return self.parse_ecoforest_int(value) / 10
