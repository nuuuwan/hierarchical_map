import os

from hmap import Region, RenderRegion


def main():
    compressed_data_path = os.path.join('data', 'LK.compressed.json')
    if os.path.exists(compressed_data_path):
        lk_region_compressed = Region.from_file(compressed_data_path)
    else:
        lk_region = Region.build_lk()
        lk_region_compressed = lk_region.compress()
        lk_region_compressed.to_file(compressed_data_path)

    RenderRegion(lk_region_compressed).write_svg()


if __name__ == "__main__":
    main()
