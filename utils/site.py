from models.site_models import SiteModel


def site(request):
    site = SiteModel.get_settings()
    return {"site": site}
