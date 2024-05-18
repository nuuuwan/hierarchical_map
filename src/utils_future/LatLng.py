from dataclasses import dataclass


@dataclass
class LatLng:
    lat: float
    lng: float

    def to_tuple(self) -> tuple[float, float]:
        return self.lat, self.lng

    def distance_to(self, other) -> float:
        assert isinstance(other, LatLng)
        return (
            (self.lat - other.lat) ** 2 + (self.lng - other.lng) ** 2
        ) ** 0.5

    @staticmethod
    def from_tuple(t: tuple[float, float]) -> 'LatLng':
        return LatLng(t[0], t[1])
