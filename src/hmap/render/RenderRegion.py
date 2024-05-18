import os

from utils import Log

log = Log('RenderRegion')


class RenderRegion:
    DIR_RENDER = 'images'

    def __init__(self, region):
        self.region = region

    def write_svg(self):
        if not os.path.exists(self.DIR_RENDER):
            os.makedirs(self.DIR_RENDER)

        svg_path = os.path.join(self.DIR_RENDER, f'{self.region.id}.svg')
        log.info(f'Wrote SVG to {svg_path}')
