from dataclasses import dataclass

MODEL_NAME = "EcoGeo"


@dataclass
class EcoGeoDevice:
    is_supported: bool
    model_name: str
    serial_number: str
    firmware: str

    state: dict[str, any] | None = None

    @classmethod
    def build(cls, serial_number: str, data: dict[str, any]):  # -> EcoGeoDevice:
        firmware = "321"

        return EcoGeoDevice(
            is_supported=True,
            model_name=MODEL_NAME,
            firmware=firmware,
            serial_number=serial_number,
            state=data
        )
