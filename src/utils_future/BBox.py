from dataclasses import dataclass

from utils_future.LatLng import LatLng


@dataclass
class BBox:
    south_east: LatLng
    north_west: LatLng

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
