from dataclasses import dataclass

from utils_future.LatLng import LatLng


@dataclass
class BBox:
    min_latlng: LatLng
    max_latlng: LatLng

    @property
    def dlat(self) -> float:
        return self.max_latlng.lat - self.min_latlng.lat

    @property
    def dlng(self) -> float:
        return self.max_latlng.lng - self.min_latlng.lng

    @property
    def mid(self) -> LatLng:
        return LatLng(
            (self.min_latlng.lat + self.max_latlng.lat) / 2,
            (self.min_latlng.lng + self.max_latlng.lng) / 2,
        )

    def is_overlapping(self, other: 'BBox') -> bool:
        return (
            self.min_latlng.lat <= other.max_latlng.lat
            and self.max_latlng.lat >= other.min_latlng.lat
            and self.min_latlng.lng <= other.max_latlng.lng
            and self.max_latlng.lng >= other.min_latlng.lng
        )

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (
            self.min_latlng.lat,
            self.min_latlng.lng,
            self.max_latlng.lat,
            self.max_latlng.lng,
        )

    @staticmethod
    def from_centroid(centroid: LatLng, radius: float) -> 'BBox':
        return BBox(
            LatLng(
                centroid.lat - radius,
                centroid.lng - radius,
            ),
            LatLng(
                centroid.lat + radius,
                centroid.lng + radius,
            ),
        )

    @staticmethod
    def merge(bbox_list: list['BBox']) -> 'BBox':
        min_lat, min_lng = 90, 180
        max_lat, max_lng = -90, -180

        for bbox in bbox_list:
            min_lat = min(min_lat, bbox.min_latlng.lat)
            min_lng = min(min_lng, bbox.min_latlng.lng)
            max_lat = max(max_lat, bbox.max_latlng.lat)
            max_lng = max(max_lng, bbox.max_latlng.lng)

        return BBox(
            LatLng(min_lat, min_lng),
            LatLng(max_lat, max_lng),
        )
