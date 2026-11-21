# Fixed conversion rates for chapter sales
GEM_UNIT_PRICE_MMK = 10  # 1 gem = 10 MMK
COUPON_UNIT_PRICE_MMK = 10  # 1 coupon = 10 MMK


def gem_unit_price_mmk():
    """MMK value of one gem."""
    return GEM_UNIT_PRICE_MMK


def coupon_unit_price_mmk():
    """MMK value of one coupon."""
    return COUPON_UNIT_PRICE_MMK


def sale_value_mmk(gems, coupons):
    """Sale value in MMK: gem sold x gem rate + coupon used x coupon rate."""
    return int(gems or 0) * GEM_UNIT_PRICE_MMK + int(coupons or 0) * COUPON_UNIT_PRICE_MMK


def gems_to_mmk(gem_count):
    """Convert gem count to MMK."""
    return int(gem_count or 0) * GEM_UNIT_PRICE_MMK
