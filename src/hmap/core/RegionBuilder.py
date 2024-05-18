import math

from gig import Ent, EntType, GIGTable
from utils import Log

from utils_future import LatLng

log = Log('RegionBuilder')


class RegionBuilder:
    K_POPULATION = 2500

    @staticmethod
    def get_child_ent_type(ent_type):
        if ent_type == EntType.PROVINCE:
            return EntType.ED

        if ent_type == EntType.ED:
            return EntType.PD
        return None

    @staticmethod
    def is_parent(ent, parent_id):
        if parent_id == 'LK':
            return True
        if parent_id in ent.id:
            return True
        if parent_id in ent.province_id:
            return True
        return False

    @classmethod
    def get_region(cls, ent, child_ent_type):
        gig_table = GIGTable(
            'government-elections-presidential', 'regions-ec', '2015'
        )
        gig = ent.gig(gig_table)
        valid = gig.valid

        v_blue = gig.UPFA
        v_green = gig.NDF
        v_win = max(v_blue, v_green)

        hue = 0 if v_blue > v_green else 140
        p_win = v_win / valid
        sat = 100
        pl = max(0, (p_win - 0.4)) / 0.6
        light = int(20 + (1 - pl) * 80)

        color = f'hsl({hue},{sat}%,{light}%)'

        return cls(
            id=ent.id,
            name=ent.name,
            color=color,
            children=cls.get_regions_from_type(
                child_ent_type,
                ent.id,
            )
            if child_ent_type
            else None,
            centroid=LatLng.from_tuple(ent.centroid),
            size=math.sqrt(valid) / RegionBuilder.K_POPULATION,
        )

    @classmethod
    def get_regions_from_type(
        cls,
        ent_type,
        parent_id,
    ):
        ents = Ent.list_from_type(
            ent_type,
        )
        ents = [
            ent for ent in ents if RegionBuilder.is_parent(ent, parent_id)
        ]
        child_ent_type = RegionBuilder.get_child_ent_type(ent_type)
        return [cls.get_region(ent, child_ent_type) for ent in ents]

    @classmethod
    def build_lk(cls):
        root_region = cls(
            id='LK',
            name='Sri Lanka',
            color="white",
            children=cls.get_regions_from_type(EntType.PROVINCE, 'LK'),
            centroid=None,
            size=None,
        )

        return root_region
