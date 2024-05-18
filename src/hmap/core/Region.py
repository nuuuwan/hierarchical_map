from dataclasses import dataclass

from gig import Ent, EntType

from utils_future import BBox, LatLng




@dataclass
class Region:
    id: str
    name: str
    child_regions: list['Region']
    centroid: LatLng
    size: float

    @property
    def bbox(self):
        if self.child_regions is None:
            assert self.centroid is not None
            return BBox.from_centroid(self.centroid, self.size)

        return BBox.merge([region.bbox for region in self.child_regions])

    @staticmethod
    def build_lk():
        def get_district_regions(province_id):
            district_ents = Ent.list_from_type(
                EntType.DISTRICT,
            )
            district_ents = [
                district
                for district in district_ents
                if province_id in district.id
            ]
            return [
                Region(
                    id=district.id,
                    name=district.name,
                    child_regions=None,
                    centroid=LatLng.from_tuple(district.centroid),
                    size=district.population / 20_000_000,
                )
                for district in district_ents
            ]

        def get_province_regions():
            return [
                Region(
                    id=province.id,
                    name=province.name,
                    child_regions=get_district_regions(province.id),
                    centroid=None,
                    size=None,
                )
                for province in Ent.list_from_type(EntType.PROVINCE)
            ]

        root_region = Region(
            id='LK',
            name='Sri Lanka',
            child_regions=get_province_regions(),
            centroid=None,
            size=None,
        )

        return root_region
