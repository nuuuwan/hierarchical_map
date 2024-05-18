from dataclasses import dataclass


@dataclass
class LatLng:
    lat: float
    lng: float

    @staticmethod
    def from_tuple(t: tuple[float, float]) -> 'LatLng':
        return LatLng(t[0], t[1])
