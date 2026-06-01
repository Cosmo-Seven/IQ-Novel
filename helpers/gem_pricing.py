from core.models import GemModel


def get_reference_gem_package():
    """Gem top-up package used to convert gems to MMK (popular first)."""
    return (
        GemModel.objects.filter(is_deleted=False, gem_amount__gt=0)
        .order_by("-is_popular", "-gem_amount")
        .first()
    )


def gem_unit_price_mmk():
    """MMK per one gem from the reference package."""
    package = get_reference_gem_package()
    if not package or not package.gem_amount:
        return 0
    return int(package.price / package.gem_amount)


def gems_to_mmk(gem_count):
    """Convert gem count to sale value in MMK."""
    if not gem_count:
        return 0
    return int(gem_count * gem_unit_price_mmk())
