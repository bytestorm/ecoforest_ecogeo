import string, logging
from dataclasses import dataclass

import httpx
from pyecoforest.api import EcoforestApi

from custom_components.ecoforest_ecogeo.overrides.device import EcoGeoDevice

_LOGGER = logging.getLogger(__name__)

MODEL_ADDRESS = 5323
MODEL_LENGTH = 6

OP_TYPE_GET_SWITCH = 2001
OP_TYPE_GET_REGISTER = 2002
OP_TYPE_SET = 2011

REQUESTS = [
    {"address": 3, "length": 9, "op": OP_TYPE_GET_REGISTER},
    {"address": 105, "length": 3, "op": OP_TYPE_GET_SWITCH},
    {"address": 194, "length": 8, "op": OP_TYPE_GET_REGISTER},
    {"address": 5066, "length": 18, "op": OP_TYPE_GET_REGISTER},
    {"address": 5185, "length": 1, "op": OP_TYPE_GET_REGISTER},
    {"address": MODEL_ADDRESS, "length": MODEL_LENGTH, "op": OP_TYPE_GET_REGISTER},
]

MAPPING = {
    "t_heating": {
        "type": "float",
        "address": 200,
        "entity_type": "temperature"
    },
    "t_cooling": {
        "type": "float",
        "address": 201,
        "entity_type": "temperature"
    },
    "t_dhw": {
        "type": "float",
        "address": 8,
        "entity_type": "temperature"
    },
    "t_dg1_h": {
        "type": "float",
        "address": 3,
        "entity_type": "temperature"
    },
    "t_dg1_c": {
        "type": "float",
        "address": 197,
        "entity_type": "temperature"
    },
    "t_sg2": {
        "type": "float",
        "address": 194,
        "entity_type": "temperature"
    },
    "t_sg3": {
        "type": "float",
        "address": 195,
        "entity_type": "temperature"
    },
    "t_sg4": {
        "type": "float",
        "address": 196,
        "entity_type": "temperature"
    },
    "t_outdoor": {
        "type": "float",
        "address": 11,
        "entity_type": "temperature"
    },
    "power_heating": {
        "type": "int",
        "address": 5083,
        "entity_type": "power"
    },
    "power_cooling": {
        "type": "int",
        "address": 5185,
        "entity_type": "power"
    },
    "power_electric": {
        "type": "int",
        "address": 5082,
        "entity_type": "power"
    },
    "power_output": {
        "type": "custom",
        "entity_type": "power",
        "value_fn": lambda data: data["power_cooling"] + data["power_heating"]
    },
    "switch_heating": {
        "type": "boolean",
        "address": 105,
        "entity_type": "switch"
    },
    "switch_cooling": {
        "type": "boolean",
        "address": 107,
        "entity_type": "switch"
    },
    "switch_dhw": {
        "type": "boolean",
        "address": 106,
        "entity_type": "switch"
    },
}


class EcoGeoApi(EcoforestApi):
    def __init__(
        self,
        host: str,
        user: str,
        password: str
    ) -> None:
        super().__init__(host, httpx.BasicAuth(user, password))

    async def get(self) -> EcoGeoDevice:
        state = {}
        for request in REQUESTS:
            state.update(await self._load_data(request["address"], request["length"], request["op"]))

        device_info = {}
        for name, definition in MAPPING.items():
            match definition["type"]:
                case "int":
                    value = self.parse_ecoforest_int(state[definition["address"]])
                case "float":
                    value = self.parse_ecoforest_float(state[definition["address"]])
                case "boolean":
                    value = self.parse_ecoforest_bool(state[definition["address"]])
                case "custom":
                    continue
                case _:
                    _LOGGER.error("unknown entity type for %s", name)
                    continue

            device_info[name] = value

        for name, definition in MAPPING.items():
            if definition["entity_type"] == "temperature":
                if device_info[name] == -999.9:
                    device_info[name] = None

            if definition["type"] != "custom":
                continue
            device_info[name] = definition["value_fn"](device_info)

        _LOGGER.debug(device_info)
        _LOGGER.debug(state)
        return EcoGeoDevice.build(self.parse_model_name(state), device_info)

    async def _load_data(self, address, length, op_type) -> dict[int, str]:
        response = await self._request(
            data={
                "idOperacion": op_type,
                "dir": address,
                "num": length
            }
        )

        result = {}
        index = 0
        for i in range(address, address+length):
            result[i] = response[index]
            index += 1

        return result

    async def turn_switch(self, name, on: bool | None = False) -> EcoGeoDevice:
        if name not in MAPPING.keys():
            raise Exception("unknown switch")

        await self._request(
            data={"idOperacion": OP_TYPE_SET, "dir": MAPPING[name]["address"], "num": 1, int(on): int(on)}
        )
        return await self.get()

    def _parse(self, response: str) -> list[str]:
        lines = response.split('\n')

        a, b = lines[0].split('=')
        if a not in ["error_geo_get_reg", "error_geo_get_bit", "error_geo_set_bit"] or b != "0":
            raise Exception("bad response: {}".format(response))

        return lines[1].split('&')[2:]

    def parse_model_name(self, data):
        model_dictionary = ["--"] + [*string.digits] + [*string.ascii_uppercase]

        result = ''
        for address in range(MODEL_ADDRESS, MODEL_ADDRESS + MODEL_LENGTH):
            result += model_dictionary[self.parse_ecoforest_int(data[address])]

        return result

    def parse_ecoforest_int(self, value):
        result = int(value, 16)
        return result if result <= 32768 else result - 65536

    def parse_ecoforest_bool(self, value):
        return bool(int(value))

    def parse_ecoforest_float(self, value):
        return self.parse_ecoforest_int(value) / 10
