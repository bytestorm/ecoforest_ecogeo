import string, logging
from dataclasses import dataclass

import httpx
from pyecoforest.api import EcoforestApi

from custom_components.ecoforest_ecogeo.overrides.device import EcoGeoDevice

_LOGGER = logging.getLogger(__name__)

MODEL_ADDRESS = 5323
MODEL_LENGTH = 6

OP_TYPE_GET_SWITCH = 2001
OP_TYPE_SET_SWITCH = 2011
OP_TYPE_GET_REGISTER = 2002
OP_TYPE_SET_REGISTER = 2012

class DataTypes:
    Register = 1
    Coil = 2

class Operations:
    Get = {DataTypes.Coil: 2001, DataTypes.Register: 2002}
    Set = {DataTypes.Coil: 2011, DataTypes.Register: 2012}

REQUESTS = {
    DataTypes.Coil : [
        {"address": 1, "length": 41},
        {"address": 57, "length": 27},
        {"address": 105, "length": 3},
        {"address": 212, "length": 15},
    ],

    DataTypes.Register: [
        {"address": 1, "length": 31},
        {"address": 59, "length": 1},
        {"address": 194, "length": 8},
        {"address": 5066, "length": 18},
        {"address": 5185, "length": 1},

        {"address": MODEL_ADDRESS, "length": MODEL_LENGTH, "op": OP_TYPE_GET_REGISTER},
    ]
}

MAPPING = {
    "t_heating": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 200,
        "entity_type": "temperature"
    },
    "t_cooling": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 201,
        "entity_type": "temperature"
    },
    "t_dhw": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 8,
        "entity_type": "temperature"
    },
    "t_dg1_h": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 3,
        "entity_type": "temperature"
    },
    "t_dg1_c": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 197,
        "entity_type": "temperature"
    },
    "t_sg2": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 194,
        "entity_type": "temperature"
    },
    "t_sg3": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 195,
        "entity_type": "temperature"
    },
    "t_sg4": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 196,
        "entity_type": "temperature"
    },
    "t_outdoor": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 11,
        "entity_type": "temperature"
    },
    "power_heating": {
        "data_type": DataTypes.Register,
        "type": "int",
        "address": 5083,
        "entity_type": "power"
    },
    "power_cooling": {
        "data_type": DataTypes.Register,
        "type": "int",
        "address": 5185,
        "entity_type": "power"
    },
    "power_electric": {
        "data_type": DataTypes.Register,
        "type": "int",
        "address": 5082,
        "entity_type": "power"
    },
    "power_output": {
        "data_type": DataTypes.Register,
        "type": "custom",
        "entity_type": "power",
        "value_fn": lambda data, raw: data["power_cooling"] + data["power_heating"]
    },
    "t_brine_in": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 2,
        "entity_type": "temperature"
    },
    "t_brine_out": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 1,
        "entity_type": "temperature"
    },
    "p_brine": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 13,
        "entity_type": "pressure"
    },
    "p_output": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 14,
        "entity_type": "pressure"
    },
    "cop": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 30,
        "entity_type": "measurement"
    },
    "pf": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 31,
        "entity_type": "measurement"
    },
    "switch_heating": {
        "data_type": DataTypes.Coil,
        "type": "boolean",
        "address": 105,
        "entity_type": "switch"
    },
    "switch_cooling": {
        "data_type": DataTypes.Coil,
        "type": "boolean",
        "address": 107,
        "entity_type": "switch"
    },
    "switch_dhw": {
        "data_type": DataTypes.Coil,
        "type": "boolean",
        "address": 106,
        "entity_type": "switch"
    },
    "switch_dg1_output": {
        "data_type": DataTypes.Coil,
        "type": "boolean",
        "address": 60,
        "entity_type": "switch"
    },
    "switch_sg2_output": {
        "data_type": DataTypes.Coil,
        "type": "boolean",
        "address": 57,
        "entity_type": "switch"
    },
    "switch_pool_output": {
        "data_type": DataTypes.Coil,
        "type": "boolean",
        "address": 65,
        "entity_type": "switch"
    },
    "switch_pool_device_output": {
        "data_type": DataTypes.Coil,
        "type": "boolean",
        "address": 61,
        "entity_type": "switch"
    },
    "button_reset_alarms": {
        "data_type": DataTypes.Coil,
        "type": "boolean",
        "address": 83,
        "entity_type": "button"
    },
    "number_dhw_setpoint": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 17,
        "entity_type": "temperature",
        "is_number": True,
        "min": 0,
        "max": 65,
        "step": 0.1
    },
    "number_dhw_dt_start": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 15,
        "entity_type": "temperature",
        "is_number": True,
        "min": 2,
        "max": 25,
        "step": 0.1
    },
    "number_dhw_htr_set": {
        "data_type": DataTypes.Register,
        "type": "float",
        "address": 59,
        "entity_type": "temperature",
        "is_number": True,
        "min": 0,
        "max": 70,
        "step": 0.1
    },
    "alarm": {
        "data_type": DataTypes.Coil,
        "type": "custom",
        "entity_type": "enum",
        "value_fn": lambda data, raw_data: EcoGeoApi.get_alarm(raw_data)
    }
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
        state = {DataTypes.Coil: {}, DataTypes.Register: {}}

        for dt in [DataTypes.Coil, DataTypes.Register]:
            for request in REQUESTS[dt]:
                state[dt].update(await self._load_data(request["address"], request["length"], Operations.Get[dt]))

        device_info = {}
        for name, definition in MAPPING.items():
            match definition["type"]:
                case "int":
                    value = self.parse_ecoforest_int(state[definition["data_type"]][definition["address"]])
                case "float":
                    value = self.parse_ecoforest_float(state[definition["data_type"]][definition["address"]])
                case "boolean":
                    value = self.parse_ecoforest_bool(state[definition["data_type"]][definition["address"]])
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
            device_info[name] = definition["value_fn"](device_info, state)

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
            data={"idOperacion": OP_TYPE_SET_SWITCH, "dir": MAPPING[name]["address"], "num": 1, int(on): int(on)}
        )
        return await self.get()

    async def set_numeric_value(self, name, value: float) -> EcoGeoDevice:
        if name not in MAPPING.keys():
            raise Exception("unknown register")

        converted_value = self.convert_to_ecoforest_int(value)

        await self._request(
            data={"idOperacion": OP_TYPE_SET_REGISTER, "dir": MAPPING[name]["address"], "num": 1, converted_value: converted_value}
        )
        return await self.get()

    def _parse(self, response: str) -> list[str]:
        lines = response.split('\n')

        a, b = lines[0].split('=')
        if a not in ["error_geo_get_reg", "error_geo_get_bit", "error_geo_set_reg", "error_geo_set_bit"] or b != "0":
            raise Exception("bad response: {}".format(response))

        return lines[1].split('&')[2:]

    def parse_model_name(self, data):
        model_dictionary = ["--"] + [*string.digits] + [*string.ascii_uppercase]

        result = ''
        for address in range(MODEL_ADDRESS, MODEL_ADDRESS + MODEL_LENGTH):
            result += model_dictionary[self.parse_ecoforest_int(data[DataTypes.Register][address])]

        return result

    def convert_to_ecoforest_int(self, value):
        value = int(value * 10)

        if value < 0:
            value += 65536

        return ("0000" + hex(value)[2:])[-4:]

    def parse_ecoforest_int(self, value):
        result = int(value, 16)
        return result if result <= 32768 else result - 65536

    def parse_ecoforest_bool(self, value):
        return bool(int(value))

    def parse_ecoforest_float(self, value):
        return self.parse_ecoforest_int(value) / 10

    def get_alarm(data):
        alarm_registers = [
            1,	#Clock Board fault or not connected
            2,	#Extended memory fault
            3,	#Low outdoor temp. & Low ground temp.
            7,	#AI3 Probe failure. Compressor discharge pressure
            8,	#AI4 Probe failure. Brine outlet temperature
            9,	#AI5 Probe failure. Brine return temperature
            10,	#AI6 Probe failure. Brine circuit pressure
            11,	#AI7 Probe failure. Heating outlet temperature
            12,	#AI8 Probe failure. Heating inlet temperature
            13,	#AI9 Probe failure. Heating circuit pressure
            14,	#AI10 Probe failure. Tank temperature 1 (DHW)
            15,	#AI11 Probe failure. Outdoor temperature probe
            16,	#AI12 Probe fault
            17,	#Low brine inlet temperature
            18,	#High discharge pressure
            19,	#High discharge temperature
            20,	#Inverter temperature
            21,	#Low brine outlet temperature
            24,	#Ecogeo internal probes fault
            25,	#Low pressure brine circuit
            26,	#Low pressure Heating circuit
            33,	#Evaporation temperature
            34,	#Low suction pressure
            36,	#AI2 Probe failure Compressor suction Pressure
            37,	#AI1 Probe failure. Compressor suction temperature
            38,	#Low superheat (lowSH)
            39,	#Low evaporation temperature (LOP)
            40,	#High evaporation temperature (MOP)
            41,	#Low suction temperature
            212,	#Inverter comms fault
            213,	#High brine temperature
            214,	#pCOe number:AI13 Analog input probe on channel 1 disconnected or broken
            215,	#pCOe number:AI14 Analog input probe on channel 2 disconnected or broken
            216,	#pCOe number:AI15 Analog input probe on channel 3 disconnected or broken
            217,	#pCOe number:AI16 Analog input probe on channel 4 disconnected or broken
            218,	#pCOe number: pCOe offline
            219,	#th-T 1 Error (thermostat for DG1) **
            220,	#th-T 1 offline (thermostat for DG1) **
            221,	#th-T 2 Error (thermostat for SG2) **
            222,	#th-T 2 offline (thermostat for SG2) **
            223,	#th-T 3 Error (thermostat for SG3) **
            224,	#th-T 3 offline (thermostat for SG3) **
            225,	#th-T 4 Error (thermostat for SG4) **
            226,	#th-T 4 offline (thermostat for SG4) **
        ]

        for address in alarm_registers:
            if data[DataTypes.Coil][address] == "0":
                continue
            return address

        return 0
