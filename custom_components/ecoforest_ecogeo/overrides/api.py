import string, logging
from dataclasses import dataclass

import httpx
from pyecoforest.api import EcoforestApi

from custom_components.ecoforest_ecogeo.overrides.device import EcoGeoDevice

_LOGGER = logging.getLogger(__name__)


@dataclass
class ApiRequest:
    op: str
    start: int
    number: int


API_SERIAL = ApiRequest("2002", 5323, 6)
API_TANK_TEMPERATURES = ApiRequest("2002", 200, 2)
API_BASIC_TEMPERATURES = ApiRequest("2002", 8, 4)
API_POWER = ApiRequest("2002", 5066, 18)
API_POWER_COOLING = ApiRequest("2002", 5185, 1)
API_SWITCHES = ApiRequest("2001", 105, 3)  # heating, dhw, cooling


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
        serial = await self._load_registers(API_SERIAL)
        temperatures_tanks = await self._load_registers(API_TANK_TEMPERATURES)
        temperatures_basic = await self._load_registers(API_BASIC_TEMPERATURES)
        power = await self._load_registers(API_POWER)
        power_cooling = await self._load_registers(API_POWER_COOLING)
        switches = await self._load_registers(API_SWITCHES)

        return EcoGeoDevice.build(
            {
                "serial": {
                    "value": self.parse_serial_number(serial)
                },
                "temperatures": {
                    "t_outdoor": self.parse_ecoforest_float(temperatures_basic[3]),
                    "t_heating": self.parse_ecoforest_float(temperatures_tanks[0]),
                    "t_cooling": self.parse_ecoforest_float(temperatures_tanks[1]),
                    "t_dhw": self.parse_ecoforest_float(temperatures_basic[0]),
                },
                "power": {
                    "power_heating": self.parse_ecoforest_int(power[17]),
                    "power_cooling": self.parse_ecoforest_int(power_cooling[0]),
                    "power_electric": self.parse_ecoforest_int(power[16]),
                },
                "switches": {
                    "switch_heating": self.parse_ecoforest_bool(switches[0]),
                    "switch_dhw": self.parse_ecoforest_bool(switches[1]),
                    "switch_cooling": self.parse_ecoforest_bool(switches[2])
                }
            }
        )

    async def _load_registers(self, request_description) -> list[str]:
        result = await self._request(
            data={
                "idOperacion": request_description.op,
                "dir": request_description.start,
                "num": request_description.number
            }
        )

        return result

    async def turn_switch(self, name, on: bool | None = False) -> EcoGeoDevice:
        match name:
            case "heating":
                register = 105
            case "dhw":
                register = 106
            case "cooling":
                register = 107
            case _:
                raise Exception("unknown switch")

        await self._request(
            data={"idOperacion": 2011, "dir": register, "num": 1, int(on): int(on)}
        )
        return await self.get()

    def _parse(self, response: str) -> list[str]:
        lines = response.split('\n')

        a, b = lines[0].split('=')
        if a not in ["error_geo_get_reg", "error_geo_get_bit", "error_geo_set_bit"] or b != "0":
            raise Exception("bad response: {}".format(response))

        return lines[1].split('&')[2:]

    def parse_serial_number(self, data):
        serial_dictionary = ["--"] + [*string.digits] + [*string.ascii_uppercase]
        return ''.join([serial_dictionary[self.parse_ecoforest_int(x)] for x in data])

    def parse_ecoforest_int(self, value):
        result = int(value, 16)
        return result if result <= 32768 else result - 65536

    def parse_ecoforest_bool(self, value):
        return bool(int(value))

    def parse_ecoforest_float(self, value):
        return self.parse_ecoforest_int(value) / 10
