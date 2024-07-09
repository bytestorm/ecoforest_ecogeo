from dataclasses import dataclass

MODEL_NAME = "EcoGeo"


@dataclass
class EcoGeoDevice:
    # status information
#    on: bool
#    state: State
#    power: int
#    temperature: float
#    alarm: Alarm | None = None
#    alarm_code: str | None = None

    # sensors
#    environment_temperature: float | None = None
#    cpu_temperature: float | None = None
#    gas_temperature: float | None = None
#    ntc_temperature: float | None = None
#    depression: int | None = None
#    working_hours: int | None = None
#    working_state: int | None = None
#    working_level: int | None = None
#    ignitions: int | None = None
#    live_pulse: float | None = None
#    pulse_offset: float | None = None
#    extractor: float | None = None
#    convecto_air_flow: float | None = None
    is_supported: bool
    model_name: str
    serial_number: str
    firmware: str

    t_outdoor: float | None = None
    t_dhw: float | None = None
    t_cooling: float | None = None
    t_heating: float | None = None
    power_heating: int | None = None
    power_cooling: int | None = None
    power_electric: int | None = None

    @classmethod
    def build(cls, data: dict[str, dict[str, str]]):  # -> EcoGeoDevice:
        #DEADBEEF
        serial_number = "123"
        firmware = "321"
        stats = {
            "t_outdoor": "29.3",
            "t_dhw": "60.3",
            "t_cooling": "8",
            "t_heating": "12",
            "power_heating": "4321",
            "power_cooling": "6789",
            "power_electric": "1234",
        }

        return EcoGeoDevice(
            is_supported=True,
            model_name=MODEL_NAME,
            serial_number=serial_number,
            t_outdoor=float(stats["t_outdoor"]),
            t_dhw=float(stats["t_dhw"]),
            t_cooling=float(stats["t_cooling"]),
            t_heating=float(stats["t_heating"]),
            power_heating=int(stats["power_heating"]),
            power_cooling=int(stats["power_cooling"]),
            power_electric=int(stats["power_electric"]),
        )