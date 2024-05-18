from hmap import Region, RenderRegion


def main():
    lk_region = Region.build_lk()
    lk_region = lk_region.compress()
    RenderRegion(lk_region).write_svg()


if __name__ == "__main__":
    main()
