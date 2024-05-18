import math
from dataclasses import dataclass

from utils import JSONFile, Log

from hmap.core.RegionBuilder import RegionBuilder
from hmap.core.RegionCompress import RegionCompress
from utils_future import BBox, LatLng

log = Log('Region')


@dataclass
class Region(RegionBuilder, RegionCompress):
    id: str
    name: str
    color: str
    children: list['Region']
    centroid: LatLng
    size: float

    @property
    def size_derived(self):
        if self.children is None:
            return self.size
        return math.sqrt(
            sum([child.size_derived**2 for child in self.children])
        )

    @property
    def bbox(self):
        if self.children is None:
            assert self.centroid is not None
            return BBox.from_centroid(self.centroid, self.size)
        return BBox.merge([region.bbox for region in self.children])

    # Serialize
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'children': [child.to_dict() for child in self.children]
            if self.children
            else None,
            'centroid': self.centroid.to_tuple() if self.centroid else None,
            'size': self.size,
        }

    @staticmethod
    def from_dict(d: dict) -> 'Region':
        return Region(
            id=d['id'],
            name=d['name'],
            color=d['color'],
            children=[Region.from_dict(child) for child in d['children']]
            if d['children']
            else None,
            centroid=LatLng.from_tuple(d['centroid'])
            if d['centroid']
            else None,
            size=d['size'],
        )

    def to_file(self, path: str):
        JSONFile(path).write(self.to_dict())

    @staticmethod
    def from_file(path: str) -> 'Region':
        return Region.from_dict(JSONFile(path).read())

    # Compression
