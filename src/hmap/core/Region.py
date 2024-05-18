import math
import random
from dataclasses import dataclass

from gig import Ent, EntType
from utils import JSONFile, Log

from utils_future import BBox, LatLng

log = Log('Region')


@dataclass
class Region:
    id: str
    name: str
    color: str
    children: list['Region']
    centroid: LatLng
    size: float

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
    def transform(self, dLatLng: LatLng) -> 'Region':
        # log.debug(f'[transform] {self.id} {str(dLatLng)}')
        new_centroid = None
        if self.centroid:
            new_centroid = LatLng(
                self.centroid.lat + dLatLng.lat,
                self.centroid.lng + dLatLng.lng,
            )
        new_children = None
        if self.children:
            new_children = [
                child.transform(dLatLng) for child in self.children
            ]
        return Region(
            id=self.id,
            name=self.name,
            color=self.color,
            children=new_children,
            centroid=new_centroid,
            size=self.size,
        )

    def decompress_children(self) -> list['Region']:
        new_children = [child.compress() for child in self.children]

        n = len(new_children)

        MAX_EPOCHS = 1_000_000
        ALPHA = 0.001
        for g in range(MAX_EPOCHS):
            n_overlaps = 0
            for i1 in range(n):
                child1 = new_children[i1]
                mid1 = child1.bbox.mid
                for i2 in range(i1 + 1, n):
                    child2 = new_children[i2]
                    mid2 = child2.bbox.mid
                    if child1.bbox.is_overlapping(child2.bbox):
                        n_overlaps += 1
                        dlat = ALPHA * (mid2.lat - mid1.lat)
                        dlng = ALPHA * (mid2.lng - mid1.lng)

                        new_children[i1] = child1.transform(
                            LatLng(-dlat, -dlng)
                        )
                        new_children[i2] = child2.transform(
                            LatLng(dlat, dlng)
                        )

            if n_overlaps == 0:
                break
        return new_children

    def compress(self) -> 'Region':
        if not self.children:
            return self

        new_children = self.decompress_children()

        region = Region(
            id=self.id,
            name=self.name,
            color=self.color,
            children=new_children,
            centroid=None,
            size=self.size,
        )
        log.debug(f'✅ [compress] {self.id}')
        return region

    # Build LK
    @staticmethod
    def build_lk():
        def get_child_ent_type(ent_type):
            if ent_type == EntType.PROVINCE:
                return EntType.ED

            if ent_type == EntType.ED:
                return EntType.PD
            return None

        def is_parent(ent, parent_id):
            if parent_id == 'LK':
                return True
            if parent_id in ent.id:
                return True
            if parent_id in ent.province_id:
                return True
            return False

        def get_region(ent, child_ent_type):
            return Region(
                id=ent.id,
                name=ent.name,
                color=random.choice(["#800", '#f80', '#080']),
                children=get_regions_from_type(
                    child_ent_type,
                    ent.id,
                )
                if child_ent_type
                else None,
                centroid=LatLng.from_tuple(ent.centroid),
                size=math.sqrt(ent.population) / 1_000,
            )

        def get_regions_from_type(
            ent_type,
            parent_id,
        ):
            ents = Ent.list_from_type(
                ent_type,
            )
            ents = [ent for ent in ents if is_parent(ent, parent_id)]
            child_ent_type = get_child_ent_type(ent_type)
            return [get_region(ent, child_ent_type) for ent in ents]

        root_region = Region(
            id='LK',
            name='Sri Lanka',
            color="white",
            children=get_regions_from_type(EntType.PROVINCE, 'LK'),
            centroid=None,
            size=None,
        )

        return root_region
