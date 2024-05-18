from utils import Log

from utils_future import LatLng

log = Log('Region')


class RegionCompress:
    MAX_EPOCHS = 1_000_000
    ALPHA = 0.01

    def transform(self, dLatLng: LatLng):
        new_centroid = None
        if self.centroid:
            new_centroid = self.centroid + dLatLng

        new_children = None
        if self.children:
            new_children = [
                child.transform(dLatLng) for child in self.children
            ]
        return self.__class__(
            id=self.id,
            name=self.name,
            color=self.color,
            children=new_children,
            centroid=new_centroid,
            size=self.size,
        )

    def decompress_children(self) -> list:
        new_children = [child.compress() for child in self.children]
        new_children = sorted(
            new_children,
            key=lambda child: child.bbox.mid.lat,
        )

        n = len(new_children)
        for g in range(self.MAX_EPOCHS):
            n_overlaps = 0
            for i1 in range(n):
                for i2 in range(i1 + 1, n):
                    child1 = new_children[i1]
                    child2 = new_children[i2]

                    if not child1.bbox.is_overlapping(child2.bbox):
                        continue
                    n_overlaps += 1

                    mid1 = child1.bbox.mid
                    mid2 = child2.bbox.mid
                    dlatlng = self.ALPHA * (mid2 - mid1)

                    new_children[i1] = child1.transform(-1 * dlatlng)
                    new_children[i2] = child2.transform(
                        dlatlng,
                    )

            if n_overlaps == 0:
                break
        return new_children

    def compress(self):
        if not self.children:
            return self

        new_children = self.decompress_children()

        region = self.__class__(
            id=self.id,
            name=self.name,
            color=self.color,
            children=new_children,
            centroid=None,
            size=self.size,
        )
        log.debug(f'[compress] ✅ {self.id}')
        return region
