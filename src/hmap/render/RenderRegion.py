import os
from functools import cache

from utils import Log, _

log = Log('RenderRegion')


class RenderRegion:
    DIR_RENDER = 'images'
    WIDTH, HEIGHT = 1000, 1000
    PADDING = 100
    INNER_WIDTH, INNER_HEIGHT = WIDTH - 2 * PADDING, HEIGHT - 2 * PADDING

    def __init__(self, region):
        self.region = region

    @cache
    def get_t(self):
        bbox = self.region.bbox

        def t(latlng):
            lat, lng = latlng.to_tuple()
            min_lat, min_lng, max_lat, max_lng = bbox.to_tuple()

            plat = (lat - min_lat) / (max_lat - min_lat)
            plng = (lng - min_lng) / (max_lng - min_lng)

            x = int(plng * self.INNER_WIDTH) + self.PADDING
            y = int((1 - plat) * self.INNER_HEIGHT) + self.PADDING
            return (x, y)

        return t

    @staticmethod
    def render_region(t, region):
        bbox = region.bbox
        x_west, y_south = t(bbox.south_east)
        x_east, y_north = t(bbox.north_west)

        inner = [
            _(
                'rect',
                None,
                {
                    'x': x_west,
                    'y': y_north,
                    'width': x_east - x_west,
                    'height': y_south - y_north,
                    'fill': '#808080',
                    'fill_opacity': '0.25',
                    'stroke': '#808080',
                    'stroke-width': 1,
                },
            )
        ]

        if region.child_regions:
            for child in region.child_regions:
                inner.append(RenderRegion.render_region(t, child))

        return _('g', inner)

    def write_svg(self):
        if not os.path.exists(self.DIR_RENDER):
            os.makedirs(self.DIR_RENDER)

        svg_path = os.path.join(self.DIR_RENDER, f'{self.region.id}.svg')

        svg = _(
            'svg', [RenderRegion.render_region(self.get_t(), self.region)]
        )
        svg.store(svg_path)
        log.info(f'Wrote SVG to {svg_path}')
        os.startfile(svg_path)
