from dataclasses import dataclass

from utils_future.LatLng import LatLng


@dataclass
class BBox:
    south_east: LatLng
    north_west: LatLng

    @property
    def dlat(self) -> float:
        return self.north_west.lat - self.south_east.lat

    @property
    def dlng(self) -> float:
        return self.north_west.lng - self.south_east.lng

    @property
    def mid(self) -> LatLng:
        return LatLng(
            (self.south_east.lat + self.north_west.lat) / 2,
            (self.south_east.lng + self.north_west.lng) / 2,
        )

    def is_overlapping(self, other: 'BBox') -> bool:
        return (
            self.south_east.lat <= other.north_west.lat
            and self.north_west.lat >= other.south_east.lat
            and self.south_east.lng <= other.north_west.lng
            and self.north_west.lng >= other.south_east.lng
        )

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (
            self.south_east.lat,
            self.south_east.lng,
            self.north_west.lat,
            self.north_west.lng,
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
            min_lat = min(min_lat, bbox.south_east.lat)
            min_lng = min(min_lng, bbox.south_east.lng)
            max_lat = max(max_lat, bbox.north_west.lat)
            max_lng = max(max_lng, bbox.north_west.lng)

        return BBox(
            LatLng(min_lat, min_lng),
            LatLng(max_lat, max_lng),
        )
