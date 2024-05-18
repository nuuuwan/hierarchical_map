import os
from functools import cache

from utils import Log, _

log = Log('RenderRegion')


def shorted_text(x):
    x = ''.join([c for c in x if c not in 'aeiou'])
    words = x.split()
    if len(words) == 1:
        return x[:2]
    return words[0][0] + words[1][0]


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
            lat_span = max_lat - min_lat
            lng_span = max_lng - min_lng
            min_span = min(lat_span, lng_span)

            actual_width = min_span / lat_span * self.INNER_WIDTH
            actual_height = min_span / lng_span * self.INNER_HEIGHT
            x_padding = (self.WIDTH - actual_width) / 2
            y_padding = (self.HEIGHT - actual_height) / 2

            plat = (lat - min_lat) / (max_lat - min_lat)
            plng = (lng - min_lng) / (max_lng - min_lng)

            x = int(plng * actual_width) + x_padding
            y = int((1 - plat) * actual_height) + y_padding
            return (x, y)

        return t

    @staticmethod
    def render_region(t, region):
        bbox = region.bbox
        x_west, y_south = t(bbox.south_east)
        x_east, y_north = t(bbox.north_west)
        width = x_east - x_west
        height = y_south - y_north
        font_size = min(width, height) * 0.6

        text = None if region.children else shorted_text(region.name)

        inner = [
            _(
                'rect',
                None,
                dict(
                    x=x_west,
                    y=y_north,
                    width=width,
                    height=height,
                    fill=region.color,
                    fill_opacity=0.25,
                    stroke='#fff',
                    stroke_width=1,
                ),
            ),
            _(
                'text',
                text,
                dict(
                    x=(x_west + x_east) / 2,
                    y=(y_south + y_north) / 2,
                    font_size=font_size,
                    font_family='sans-serif',
                    text_anchor='middle',
                    alignment_baseline='middle',
                    fill='#000',
                ),
            ),
        ]

        if region.children:
            for child in region.children:
                inner.append(RenderRegion.render_region(t, child))

        return _('g', inner)

    def write_svg(self):
        if not os.path.exists(self.DIR_RENDER):
            os.makedirs(self.DIR_RENDER)

        svg_path = os.path.join(self.DIR_RENDER, f'{self.region.id}.svg')

        svg = _(
            'svg',
            [RenderRegion.render_region(self.get_t(), self.region)],
            dict(
                width=self.WIDTH,
                height=self.HEIGHT,
            ),
        )
        svg.store(svg_path)
        log.info(f'Wrote SVG to {svg_path}')
        os.startfile(svg_path)
