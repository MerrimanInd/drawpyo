from enum import Enum


class PageSize(tuple, Enum):
    """
    Predefined page sizes expressed as (width, height) in Draw.io units.
    """

    USLETTERLANDSCAPE = (1100, 850)
    USLEGALLANDSCAPE = (1400, 850)
    USTABLOIDLANDSCAPE = (1700, 1100)
    USEXECUTIVELANDSCAPE = (1000, 700)
    USLETTERPORTRAIT = (850, 1100)
    USLEGALPORTRAIT = (850, 1400)
    USTABLOIDPORTRAIT = (1100, 1700)
    USEXECUTIVEPORTRAIT = (700, 1000)
    A0LANDSCAPE = (4681, 3300)
    A1LANDSCAPE = (3300, 2336)
    A2LANDSCAPE = (2336, 1654)
    A3LANDSCAPE = (1654, 1169)
    A4LANDSCAPE = (1169, 827)
    A5LANDSCAPE = (827, 583)
    A6LANDSCAPE = (583, 413)
    A7LANDSCAPE = (413, 291)
    A0PORTRAIT = (3300, 4681)
    A1PORTRAIT = (2336, 3300)
    A2PORTRAIT = (1654, 2336)
    A3PORTRAIT = (1169, 1654)
    A4PORTRAIT = (827, 1169)
    A5PORTRAIT = (583, 827)
    A6PORTRAIT = (413, 583)
    A7PORTRAIT = (291, 413)
    B4LANDSCAPE = (1390, 980)
    B5LANDSCAPE = (980, 690)
    B4PORTRAIT = (980, 1390)
    B5PORTRAIT = (690, 980)
    ASPECT16BY9 = (1600, 900)
    ASPECT16BY10 = (1920, 1200)
    ASPECT4BY3 = (1600, 1200)

    @property
    def width(self) -> int:
        return self[0]

    @property
    def height(self) -> int:
        return self[1]
