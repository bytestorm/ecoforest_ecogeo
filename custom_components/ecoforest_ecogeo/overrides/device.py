from dataclasses import dataclass

MODEL_NAME = "EcoGeo"


@dataclass
class EcoGeoDevice:
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

    switch_heating: bool | None = None
    switch_dhw: bool | None = None
    switch_cooling: bool | None = None

    @classmethod
    def build(cls, data: dict[str, dict[str, str]]):  # -> EcoGeoDevice:
        serial_number = data["serial"]["value"]
        firmware = "321"

        return EcoGeoDevice(
            is_supported=True,
            model_name=MODEL_NAME,
            firmware=firmware,
            serial_number=serial_number,
            t_outdoor=float(data["temperatures"]["t_outdoor"]),
            t_dhw=float(data["temperatures"]["t_dhw"]),
            t_cooling=float(data["temperatures"]["t_cooling"]),
            t_heating=float(data["temperatures"]["t_heating"]),
            power_heating=int(data["power"]["power_heating"]),
            power_cooling=int(data["power"]["power_cooling"]),
            power_electric=int(data["power"]["power_electric"]),
            switch_heating=bool(data["switches"]["switch_heating"]),
            switch_dhw=bool(data["switches"]["switch_dhw"]),
            switch_cooling=bool(data["switches"]["switch_cooling"]),
        )