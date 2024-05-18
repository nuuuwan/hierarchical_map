import os
from functools import cache

from utils import Log, _

log = Log('RenderRegion')


def shorted_text(x):
    x = ''.join([c for c in x if c not in 'aeiouy'])
    words = x.split()
    if len(words) == 1:
        return x[:3]
    return ''.join([word[0] for word in words])


class RenderRegion:
    DIR_RENDER = 'images'
    WIDTH, HEIGHT = (800, 800)
    PADDING = 40
    INNER_WIDTH, INNER_HEIGHT = WIDTH - 2 * PADDING, HEIGHT - 2 * PADDING

    def __init__(self, region):
        self.region = region

    @cache
    def get_t(self):
        bbox = self.region.bbox

        def t(latlng):
            lat, lng = latlng.to_tuple()
            min_lat, min_lng, max_lat, max_lng = bbox.to_tuple()
            # lat_span = max_lat - min_lat
            # lng_span = max_lng - min_lng
            # min_span = min(lat_span, lng_span)

            # actual_width = min_span / lat_span * self.INNER_WIDTH
            # actual_height = min_span / lng_span * self.INNER_HEIGHT
            # x_padding = (self.WIDTH - actual_width) / 2
            # y_padding = (self.HEIGHT - actual_height) / 2

            actual_width = self.INNER_WIDTH
            actual_height = self.INNER_HEIGHT
            x_padding = self.PADDING
            y_padding = self.PADDING

            plat = (lat - min_lat) / (max_lat - min_lat)
            plng = (lng - min_lng) / (max_lng - min_lng)

            x = int(plng * actual_width) + x_padding
            y = int((1 - plat) * actual_height) + y_padding
            return (x, y)

        return t

    @staticmethod
    def render_region_label(region, cx, cy, rx, ry):
        if region.children:
            return None
        font_size = min(rx, ry)
        text = shorted_text(region.name)
        return _(
            'text',
            text,
            dict(
                x=cx,
                y=cy,
                font_size=font_size,
                font_family='sans-serif',
                text_anchor='middle',
                alignment_baseline='middle',
                fill='#000',
            ),
        )

    @staticmethod
    def render_shape(region, cx, cy, rx, ry):
        return _(
            'ellipse',
            None,
            dict(
                cx=cx,
                cy=cy,
                rx=rx,
                ry=ry,
                fill=region.color if not region.children else '#eee',
                fill_opacity=0.5,
                stroke='#fff',
                stroke_width=2,
            ),
        )

    @staticmethod
    def render_region(t, region):
        bbox = region.bbox
        cx, cy = t(bbox.mid)
        cx2, cy2 = t(bbox.max_latlng)
        rx = cx2 - cx
        ry = cy - cy2

        inner = [
            RenderRegion.render_shape(region, cx, cy, rx, ry),
            RenderRegion.render_region_label(region, cx, cy, rx, ry),
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
            [
                RenderRegion.render_region(self.get_t(), self.region),
                _(
                    'rect',
                    None,
                    dict(
                        x=self.PADDING,
                        y=self.PADDING,
                        width=self.INNER_WIDTH,
                        height=self.INNER_HEIGHT,
                        fill='none',
                        stroke='#ccc',
                        stroke_width=1,
                    ),
                ),
            ],
            dict(
                width=self.WIDTH,
                height=self.HEIGHT,
            ),
        )
        svg.store(svg_path)
        log.info(f'Wrote SVG to {svg_path}')
        os.startfile(svg_path)
